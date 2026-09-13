from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
OUT = PROJECT / "figures" / "result"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams["axes.unicode_minus"] = False


def rows(name: str):
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


q1 = rows("q1_candidate_summary.csv")
plt.figure(figsize=(9, 4.5))
plt.bar([r["image"].replace("图", "") for r in q1], [float(r["mask_coverage"]) for r in q1], color="#4169A1")
plt.ylabel("candidate mask coverage")
plt.xlabel("image")
plt.title("Q1 candidate mask coverage")
plt.tight_layout()
plt.savefig(OUT / "q1_coverage.png", dpi=180)
plt.close()

q2 = rows("q2_cluster_sine_results.csv")
grouped = {}
for r in q2:
    grouped.setdefault(r["image"], []).append(float(r["R2"]))
plt.figure(figsize=(9, 4.5))
labels = list(grouped)
plt.boxplot([grouped[k] for k in labels], tick_labels=[x.replace("图", "") for x in labels], showmeans=True)
plt.ylabel("R²")
plt.xlabel("image")
plt.title("Q2 RANSAC sine fit R² by image")
plt.tight_layout()
plt.savefig(OUT / "q2_r2_boxplot.png", dpi=180)
plt.close()

q3 = rows("q3_jrc_results.csv")
first = [r for r in q3 if r["image"] == "图3-1.jpg"]
plt.figure(figsize=(7, 4.5))
plt.bar([f'{r["method"]}-{r["sample_count"]}' for r in first], [float(r["JRC"]) for r in first], color="#5B8E7D")
plt.ylabel("JRC")
plt.xlabel("sampling method and count")
plt.title("Q3 JRC sampling sensitivity for image 3-1")
plt.xticks(rotation=25, ha="right")
plt.tight_layout()
plt.savefig(OUT / "q3_jrc_sensitivity.png", dpi=180)
plt.close()

q4 = rows("q4_connectivity_results.csv")
positions = {1: (500, 2000), 2: (1500, 2000), 3: (2500, 2000), 4: (500, 1000), 5: (1500, 1000), 6: (2500, 1000)}
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
for hole, (x, y) in positions.items():
    z = np.arange(0, 7000, 1000) if hole != 4 else np.arange(0, 5000, 1000)
    ax.plot([x] * len(z), [y] * len(z), z, color="#C84C4C", marker="o", markersize=3)
for r in q4:
    if float(r["relative_score"]) < 0.65:
        continue
    x1, y1 = positions[int(r["hole_a"])]
    x2, y2 = positions[int(r["hole_b"])]
    z = int(r["segment_start_m"]) * 1000 + 500
    ax.plot([x1, x2], [y1, y2], [z, z], color="#4169A1", linewidth=1.4, alpha=0.8)
ax.set_xlabel("x mm")
ax.set_ylabel("y mm")
ax.set_zlabel("depth mm")
ax.set_title("Q4 relative connectivity network")
plt.tight_layout()
plt.savefig(OUT / "q4_connectivity_3d.png", dpi=180)
plt.close()

print("PASS: project figures written")
