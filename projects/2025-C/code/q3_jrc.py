"""问题三：复杂裂隙轮廓和 JRC 采样敏感性。"""
from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


DATA_ROOT = Path(r"C:\Users\zyq\AppData\Local\Temp\huawei-c-test2\C题\附件3")
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
FIGURES = PROJECT / "figures" / "result"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


def jrc_from_points(points: np.ndarray, width: int, height: int) -> tuple[float, float]:
    points = points[np.argsort(points[:, 0])]
    unique_x = np.unique(points[:, 0])
    points = np.asarray([[x, np.median(points[points[:, 0] == x, 1])] for x in unique_x], dtype=float)
    x = points[:, 0] / max(width - 1, 1) * 94.25
    y = points[:, 1] / max(height - 1, 1) * 500.0
    slopes = np.diff(y) / np.maximum(np.diff(x), 1e-6)
    z2 = float(np.sqrt(np.mean(slopes * slopes))) if len(slopes) else 0.0
    jrc = float(51.85 * z2**0.6 - 10.37)
    return z2, jrc


def process(path: Path) -> list[dict[str, object]]:
    gray = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
    smooth = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(smooth, 30, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours = [c[:, 0, :] for c in contours if len(c) >= 30]
    if not contours:
        return []
    contour = max(contours, key=cv2.contourArea)
    rows = []
    for method, count in (("uniform", 32), ("uniform", 64), ("uniform", 128), ("curvature_adaptive", 64)):
        if method == "uniform":
            indices = np.linspace(0, len(contour) - 1, min(count, len(contour))).astype(int)
        else:
            step = max(1, len(contour) // count)
            base = list(range(0, len(contour), step))
            curvature = np.linalg.norm(np.diff(contour.astype(float), n=2, axis=0), axis=1)
            extra = np.argsort(curvature)[-min(count // 3, len(curvature)):]
            indices = np.unique(np.clip(np.r_[base, extra], 0, len(contour) - 1))
        z2, jrc = jrc_from_points(contour[indices], gray.shape[1], gray.shape[0])
        rows.append({"image": path.name, "method": method, "sample_count": len(indices), "contour_points": len(contour), "area_pixel": float(cv2.contourArea(contour)), "Z2": z2, "JRC": jrc})
    return rows


def main() -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(DATA_ROOT.glob("*.jpg")):
        rows.extend(process(path))
    if not rows:
        raise RuntimeError("no contour extracted")
    with (RESULTS / "q3_jrc_results.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS: extracted contours for {len({r['image'] for r in rows})} images; rows={len(rows)}")
    print("LIMITATION: JRC is image-derived and requires engineering calibration")


if __name__ == "__main__":
    main()
