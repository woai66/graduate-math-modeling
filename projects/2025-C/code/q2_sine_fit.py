"""问题二：DBSCAN 聚类与 RANSAC 正弦拟合。"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import DBSCAN
from sklearn.linear_model import LinearRegression, RANSACRegressor


DATA_ROOT = Path(r"C:\Users\zyq\AppData\Local\Temp\huawei-c-test2\C题\附件2")
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
FIGURES = PROJECT / "figures" / "result"
RESULTS.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)


def fit_cluster(points: np.ndarray, width: int, height: int) -> dict[str, float]:
    x_px = points[:, 0].astype(float)
    y_px = points[:, 1].astype(float)
    x_mm = x_px / max(width - 1, 1) * 94.25
    y_mm = y_px / max(height - 1, 1) * 500.0
    omega = 2 * math.pi / 94.25
    design = np.column_stack((np.sin(omega * x_mm), np.cos(omega * x_mm), np.ones_like(x_mm)))
    model = RANSACRegressor(estimator=LinearRegression(), residual_threshold=18.0, random_state=0, min_samples=max(10, int(0.5 * len(points))))
    model.fit(design, y_mm)
    pred = model.predict(design)
    coef = model.estimator_.coef_
    intercept = float(model.estimator_.intercept_)
    amplitude = float(math.hypot(coef[0], coef[1]))
    beta = float(math.atan2(coef[1], coef[0]))
    residual = y_mm - pred
    ss_res = float(np.sum(residual * residual))
    ss_tot = float(np.sum((y_mm - y_mm.mean()) ** 2))
    return {
        "points": len(points),
        "inliers": int(np.sum(model.inlier_mask_)),
        "R_mm": amplitude,
        "P_mm": 94.25,
        "beta_rad": beta,
        "C_mm": intercept,
        "RMSE_mm": float(np.sqrt(np.mean(residual * residual))),
        "R2": 1 - ss_res / ss_tot if ss_tot else 0.0,
    }


def main() -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(DATA_ROOT.glob("*.jpg")):
        gray = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
        filtered = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(filtered, 35, 110)
        ys, xs = np.where(edges > 0)
        points = np.column_stack((xs, ys))[::6]
        if len(points) == 0:
            continue
        scaled = points.astype(float) / np.array([gray.shape[1], gray.shape[0]])
        labels = DBSCAN(eps=0.025, min_samples=18, n_jobs=-1).fit_predict(scaled)
        cluster_id = 0
        for label in sorted(set(labels)):
            if label < 0:
                continue
            cluster = points[labels == label]
            if len(cluster) < 30:
                continue
            try:
                fit = fit_cluster(cluster, gray.shape[1], gray.shape[0])
            except ValueError:
                continue
            fit.update({"image": path.name, "cluster": cluster_id})
            rows.append(fit)
            cluster_id += 1
    if not rows:
        raise RuntimeError("no clusters fitted")
    with (RESULTS / "q2_cluster_sine_results.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"PASS: fitted {len(rows)} clusters across {len({r['image'] for r in rows})} images")
    print(f"R2_mean={np.mean([float(r['R2']) for r in rows]):.4f}; RMSE_mean={np.mean([float(r['RMSE_mm']) for r in rows]):.4f} mm")


if __name__ == "__main__":
    main()
