"""问题四：基于几何邻接和图像统计的连通性相对评分。"""
from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


DATA_ROOT = Path(r"C:\Users\zyq\AppData\Local\Temp\huawei-c-test2\C题\附件4")
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
FIGURES = PROJECT / "figures" / "result"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)
POSITIONS = {1: (500, 2000), 2: (1500, 2000), 3: (2500, 2000), 4: (500, 1000), 5: (1500, 1000), 6: (2500, 1000)}
NEIGHBORS = [(1, 2), (2, 3), (4, 5), (5, 6), (1, 4), (2, 5), (3, 6)]


def key(path: Path) -> tuple[int, int]:
    hole = int(re.search(r"(\d+)#孔", str(path)).group(1))
    segment = int(re.search(r"(\d+)-\d+m", path.name).group(1))
    return hole, segment


def feature(path: Path) -> dict[str, float | int]:
    gray = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (7, 7), 0), 30, 100)
    return {"edge_density": float(np.mean(edges > 0)), "mean_intensity": float(gray.mean()), "orientation": float(np.mean(np.abs(np.gradient(gray.astype(float), axis=0))))}


def main() -> None:
    features = {}
    for path in DATA_ROOT.rglob("*.jpg"):
        features[key(path)] = feature(path)
    rows = []
    for left, right in NEIGHBORS:
        max_segment = min([s for h, s in features if h == left] + [s for h, s in features if h == right])
        for segment in range(max_segment + 1):
            a, b = features.get((left, segment)), features.get((right, segment))
            if a is None or b is None:
                continue
            diff = abs(a["edge_density"] - b["edge_density"]) + 0.002 * abs(a["mean_intensity"] - b["mean_intensity"]) / 255
            score = max(0.0, min(1.0, math.exp(-50 * diff)))
            rows.append({"hole_a": left, "hole_b": right, "segment_start_m": segment, "relative_score": score, "feature_difference": diff})
    with (RESULTS / "q4_connectivity_results.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    candidates = sorted(rows, key=lambda row: abs(float(row["relative_score"]) - 0.5))[:3]
    with (RESULTS / "q4_uncertainty_candidates.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["between_holes", "segment_start_m", "uncertainty_score"])
        writer.writeheader()
        for row in candidates:
            writer.writerow({"between_holes": f"{row['hole_a']}-{row['hole_b']}", "segment_start_m": row["segment_start_m"], "uncertainty_score": 1 - abs(float(row["relative_score"]) - 0.5) * 2})
    print(f"PASS: generated {len(rows)} adjacent-hole relative scores")
    print("LIMITATION: scores are uncalibrated relative evidence, not field probabilities")


if __name__ == "__main__":
    main()
