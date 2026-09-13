"""问题一裂隙候选分割。

当前附件未提供独立像素标签，因此本脚本只输出可审计的候选掩膜和无监督诊断，
不计算监督学习精度。
"""
from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


DATA_ROOT = Path(r"C:\Users\zyq\AppData\Local\Temp\huawei-c-test2\C题\附件1")
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
FIGURES = PROJECT / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
(FIGURES / "process").mkdir(parents=True, exist_ok=True)
(FIGURES / "result").mkdir(parents=True, exist_ok=True)


def segment(gray: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    filtered = cv2.bilateralFilter(enhanced, 7, 35, 35)
    blackhat_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    blackhat = cv2.morphologyEx(filtered, cv2.MORPH_BLACKHAT, blackhat_kernel)
    _, dark_mask = cv2.threshold(blackhat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    canny = cv2.Canny(filtered, 35, 110)
    combined = cv2.bitwise_or(dark_mask, canny)
    small_kernel = np.ones((3, 3), np.uint8)
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, small_kernel, iterations=1)
    combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN, small_kernel, iterations=1)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(combined, connectivity=8)
    cleaned = np.zeros_like(combined)
    kept = 0
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area >= 12:
            cleaned[labels == label] = 255
            kept += 1
    diagnostics = {
        "otsu_threshold": float(cv2.threshold(blackhat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[0]),
        "mask_coverage": float(np.mean(cleaned > 0)),
        "components": float(kept),
    }
    return cleaned, diagnostics


def main() -> None:
    rows = []
    for path in sorted(DATA_ROOT.glob("*.jpg")):
        gray = np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
        mask, diagnostics = segment(gray)
        output = FIGURES / "result" / f"q1_{path.stem}_candidate.png"
        Image.fromarray(255 - mask).save(output)
        rows.append({"image": path.name, "width": gray.shape[1], "height": gray.shape[0], **{k: round(v, 6) for k, v in diagnostics.items()}})
    with (RESULTS / "q1_candidate_summary.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    mean_coverage = sum(float(row["mask_coverage"]) for row in rows) / len(rows)
    print(f"PASS: Q1 generated {len(rows)} candidate masks; mean_coverage={mean_coverage:.4f}")
    print("LIMITATION: no independent pixel labels; supervised metrics are unavailable")


if __name__ == "__main__":
    main()
