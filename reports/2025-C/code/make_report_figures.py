from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG = ROOT / "figures" / "result"
FIG.mkdir(parents=True, exist_ok=True)


def read_rows(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def bars(rows, value_key, labels, title, output, scale=1.0):
    width, height = 1200, 620
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    values = [float(row[value_key]) * scale for row in rows]
    max_value = max(values) or 1.0
    draw.text((40, 30), title, fill="black")
    left, bottom, top = 80, 540, 100
    bar_width = max(12, int((width - 150) / max(len(values), 1) * 0.65))
    gap = (width - 150) / max(len(values), 1)
    for i, value in enumerate(values):
        x = int(left + i * gap)
        y = int(bottom - (bottom - top) * value / max_value)
        draw.rectangle((x, y, x + bar_width, bottom), fill=(65, 105, 170), outline=(30, 50, 90))
        draw.text((x, bottom + 8), labels[i], fill="black")
        draw.text((x, max(60, y - 22)), f"{value:.3f}", fill="black")
    draw.line((left, bottom, width - 40, bottom), fill="black", width=2)
    image.save(output)


q1 = read_rows("q1_segmentation_summary.csv")
bars(q1, "edge_coverage", [r["image"].replace("图", "") for r in q1], "Q1 edge-mask coverage", FIG / "q1_edge_coverage.png", 1)
mask = Image.open(FIG / "q1_图1-1_mask.png").convert("RGB")
strip_height = mask.height // 3
preview = Image.new("RGB", (900, 680), "white")
for i in range(3):
    strip = mask.crop((0, i * strip_height, mask.width, (i + 1) * strip_height))
    strip.thumbnail((280, 600))
    x = 30 + i * 300
    preview.paste(strip, (x, 50))
    ImageDraw.Draw(preview).text((x, 20), f"segment {i + 1}", fill="black")
preview.save(FIG / "q1_mask_preview.png")
q2 = read_rows("q2_sine_summary.csv")
bars(q2, "R2", [r["image"].replace("图", "") for r in q2], "Q2 sine baseline R2", FIG / "q2_r2.png", 1)
q3 = read_rows("q3_jrc_sensitivity.csv")
bars(q3, "JRC", [r["sample_count"] for r in q3], "Q3 JRC sensitivity to sample count", FIG / "q3_jrc_sensitivity.png", 1)
