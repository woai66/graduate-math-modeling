"""2025 C 题纯 NumPy/Pillow 基线实验。

该脚本只用于验证 Skill 的可复现流程，不宣称达到竞赛最优结果。
"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\zyq\AppData\Local\Temp\huawei-c-test2\C题")
OUT = Path(__file__).resolve().parents[1] / "results"
FIG = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(parents=True, exist_ok=True)
for name in ("raw", "process", "result"):
    (FIG / name).mkdir(parents=True, exist_ok=True)


def natural_key(path: Path) -> tuple:
    return tuple(int(x) if x.isdigit() else x for x in re.split(r"(\d+)", path.name))


def gray_array(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32)


def edge_strength(gray: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(gray)
    return np.sqrt(gx * gx + gy * gy)


def save_mask(edge: np.ndarray, path: Path) -> tuple[float, int]:
    threshold = float(np.percentile(edge, 90))
    mask = edge >= threshold
    image = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8))
    image.save(path)
    small = mask[::8, ::8]
    seen = np.zeros_like(small, dtype=bool)
    components = 0
    height, width = small.shape
    for y in range(height):
        for x in range(width):
            if not small[y, x] or seen[y, x]:
                continue
            components += 1
            stack = [(y, x)]
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < height and 0 <= nx < width and small[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
    return float(mask.mean()), components


def enhanced_mask(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """用 CLAHE、双边滤波、自适应阈值和形态学得到较稳健的候选掩膜。"""
    image = np.clip(gray, 0, 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(image)
    filtered = cv2.bilateralFilter(enhanced, 5, 35, 35)
    edges = cv2.Canny(filtered, 35, 110)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask > 0, enhanced


def fit_sine(gray: np.ndarray) -> tuple[float, float, float, float]:
    height, width = gray.shape
    smoothed = cv2.GaussianBlur(np.clip(gray, 0, 255).astype(np.uint8), (5, 5), 0)
    edge = cv2.Canny(smoothed, 35, 110)
    y = np.empty(width, dtype=float)
    for x_index in range(width):
        candidates = np.where(edge[:, x_index] > 0)[0]
        y[x_index] = float(np.median(candidates)) if candidates.size else float(np.argmin(smoothed[:, x_index]))
    x = np.arange(width, dtype=float)
    omega = 2 * math.pi / width
    design = np.column_stack((np.sin(omega * x), np.cos(omega * x), np.ones(width)))
    coef, *_ = np.linalg.lstsq(design, y, rcond=None)
    pred = design @ coef
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    amplitude = float(math.hypot(coef[0], coef[1]))
    beta = float(math.atan2(coef[1], coef[0]))
    return amplitude, width, beta, float(coef[2]), r2


def roughness(gray: np.ndarray, sample_count: int) -> tuple[float, float]:
    smoothed = cv2.GaussianBlur(np.clip(gray, 0, 255).astype(np.uint8), (5, 5), 0).astype(np.float32)
    edge = edge_strength(smoothed)
    height, width = gray.shape
    x_pixels = np.linspace(0, width - 1, sample_count).astype(int)
    y_pixels = np.argmax(edge[:, x_pixels], axis=0).astype(float)
    x_mm = x_pixels / max(width - 1, 1) * 94.25
    y_mm = y_pixels / max(height - 1, 1) * 500.0
    slopes = np.diff(y_mm) / np.maximum(np.diff(x_mm), 1e-6)
    z2 = float(np.sqrt(np.mean(slopes * slopes)))
    jrc = float(51.85 * z2**0.6 - 10.37)
    return z2, jrc


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def question_one() -> None:
    rows = []
    for path in sorted((ROOT / "附件1").glob("*.jpg"), key=natural_key):
        gray = gray_array(path)
        edge = edge_strength(gray)
        mask, _ = enhanced_mask(gray)
        image = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8))
        image.save(FIG / "result" / f"q1_{path.stem}_mask.png")
        coverage, components = save_mask(edge, FIG / "process" / f"q1_{path.stem}_raw_edge.png")
        enhanced_coverage = float(mask.mean())
        rows.append({"image": path.name, "height": gray.shape[0], "width": gray.shape[1], "edge_threshold": round(float(np.percentile(edge, 90)), 4), "edge_coverage": round(enhanced_coverage, 6), "components_downsampled": components})
    write_csv(OUT / "q1_segmentation_summary.csv", rows)


def question_two() -> None:
    rows = []
    for path in sorted((ROOT / "附件2").glob("*.jpg"), key=natural_key):
        amplitude, period, beta, center, r2 = fit_sine(gray_array(path))
        rows.append({"image": path.name, "R_pixel": round(amplitude, 4), "P_pixel": round(period, 4), "beta_rad": round(beta, 6), "C_pixel": round(center, 4), "R2": round(r2, 6)})
    write_csv(OUT / "q2_sine_summary.csv", rows)


def question_three() -> None:
    rows = []
    path = sorted((ROOT / "附件3").glob("*.jpg"), key=natural_key)[0]
    gray = gray_array(path)
    for sample_count in (32, 64, 128, 256):
        z2, jrc = roughness(gray, sample_count)
        rows.append({"image": path.name, "sample_count": sample_count, "Z2": round(z2, 6), "JRC": round(jrc, 6)})
    write_csv(OUT / "q3_jrc_sensitivity.csv", rows)


def hole_info(path: Path) -> tuple[int, int]:
    match = re.search(r"(\d+)#孔", str(path))
    segment = re.search(r"(\d+)-\d+m", path.name)
    return int(match.group(1)), int(segment.group(1))


def question_four() -> None:
    rows = []
    hole_positions = {1: (500, 2000), 2: (1500, 2000), 3: (2500, 2000), 4: (500, 1000), 5: (1500, 1000), 6: (2500, 1000)}
    for path in sorted((ROOT / "附件4").rglob("*.jpg"), key=natural_key):
        hole, segment = hole_info(path)
        gray = gray_array(path)
        edge = edge_strength(gray)
        rows.append({"hole": hole, "segment_start_m": segment, "edge_density": float(np.mean(edge >= np.percentile(edge, 90))), "mean_intensity": float(gray.mean())})
    write_csv(OUT / "q4_hole_segment_features.csv", rows)
    lookup = {(int(r["hole"]), int(r["segment_start_m"])): r for r in rows}
    edges = []
    neighbor_pairs = [(1, 2), (2, 3), (4, 5), (5, 6), (1, 4), (2, 5), (3, 6)]
    for left, right in neighbor_pairs:
        for segment in range(7):
            a = lookup.get((left, segment))
            b = lookup.get((right, segment))
            if not a or not b:
                continue
            diff = abs(a["edge_density"] - b["edge_density"])
            probability = float(max(0.0, min(1.0, math.exp(-diff * 80))))
            edges.append({"hole_a": left, "hole_b": right, "segment_start_m": segment, "connectivity_score": round(probability, 6), "feature_difference": round(diff, 6)})
    write_csv(OUT / "q4_connectivity_scores.csv", edges)
    candidate_rows = []
    for edge in edges:
        score = 1 - abs(edge["connectivity_score"] - 0.5) * 2
        candidate_rows.append({"between_holes": f"{edge['hole_a']}-{edge['hole_b']}", "segment_start_m": edge["segment_start_m"], "uncertainty_score": round(score, 6)})
    candidate_rows.sort(key=lambda item: item["uncertainty_score"], reverse=True)
    write_csv(OUT / "q4_supplementary_drill_candidates.csv", candidate_rows[:3])
    draw_network(hole_positions, edges)


def draw_network(positions: dict[int, tuple[int, int]], edges: list[dict]) -> None:
    canvas = Image.new("RGB", (900, 620), "white")
    draw = ImageDraw.Draw(canvas)
    def project(x: float, y: float, z: float) -> tuple[int, int]:
        return int(100 + x * 0.22 + y * 0.10), int(540 - z * 0.055 - x * 0.04 + y * 0.03)
    for edge in edges:
        if edge["connectivity_score"] < 0.5:
            continue
        x1, y1 = positions[edge["hole_a"]]
        x2, y2 = positions[edge["hole_b"]]
        z = edge["segment_start_m"] * 1000 + 500
        draw.line((*project(x1, y1, z), *project(x2, y2, z)), fill=(60, 110, 180), width=2)
    for hole, (x, y) in positions.items():
        for z in (500, 2500, 4500, 6500):
            if hole == 4 and z > 4500:
                continue
            px, py = project(x, y, z)
            draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(210, 60, 60), outline=(80, 30, 30))
        px, py = project(x, y, 0)
        draw.text((px + 6, py - 10), f"{hole}#", fill=(0, 0, 0))
    draw.text((30, 20), "2025 C Connectivity Baseline Projection", fill=(0, 0, 0))
    canvas.save(FIG / "result" / "q4_connectivity_network.png")


if __name__ == "__main__":
    question_one()
    question_two()
    question_three()
    question_four()
    print(f"results written to {OUT}")
