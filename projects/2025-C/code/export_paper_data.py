"""从 results/ 汇总论文正文所需全部数字,输出 paper_data.json 供 docx 构建脚本读取。"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open("r", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def img_key(name: str) -> int:
    return int(name.split("-")[1].split(".")[0])


data: dict[str, object] = {}

# ---- 数据审计 ----
audit = read_csv("data_audit.csv")
groups: dict[str, list[dict[str, str]]] = defaultdict(list)
for r in audit:
    groups[r["attachment"]].append(r)
audit_rows = []
for att in sorted(groups):
    rows = groups[att]
    w = {r["width"] for r in rows}
    h = {r["height"] for r in rows}
    audit_rows.append({
        "attachment": att,
        "count": len(rows),
        "size": f"{next(iter(w))}×{next(iter(h))}",
        "edge_min": min(float(r["edge_density"]) for r in rows),
        "edge_max": max(float(r["edge_density"]) for r in rows),
        "mean_min": min(float(r["mean"]) for r in rows),
        "mean_max": max(float(r["mean"]) for r in rows),
    })
data["audit"] = {
    "total": len(audit),
    "rows": audit_rows,
}
# SHA 重复
import hashlib
seen: dict[str, str] = {}
dups = []
for r in audit:
    if r["sha256"] in seen:
        dups.append((seen[r["sha256"]], r["file"]))
    else:
        seen[r["sha256"]] = r["file"]
data["audit"]["dups"] = [f"{a} 与 {b} 完全相同" for a, b in dups]

# ---- Q1 ----
q1 = read_csv("q1_candidate_summary.csv")
q1_rows = [{
    "image": r["image"].replace(".jpg", ""),
    "otsu": int(float(r["otsu_threshold"])),
    "cov": round(float(r["mask_coverage"]) * 100, 2),
    "comps": int(float(r["components"])),
} for r in sorted(q1, key=lambda r: img_key(r["image"]))]
data["q1"] = {
    "rows": q1_rows,
    "mean_cov": round(sum(r["cov"] for r in q1_rows) / len(q1_rows), 2),
    "total_comps": sum(r["comps"] for r in q1_rows),
    "cov_min": min(r["cov"] for r in q1_rows),
    "cov_max": max(r["cov"] for r in q1_rows),
}

# ---- Q2 ----
q2 = read_csv("q2_cluster_sine_results.csv")
q2_rows = [{
    "image": r["image"].replace(".jpg", ""),
    "cluster": int(r["cluster"]),
    "R": round(float(r["R_mm"]), 2),
    "P": round(float(r["P_mm"]), 2),
    "beta": round(float(r["beta_rad"]), 3),
    "C": round(float(r["C_mm"]), 2),
    "rmse": round(float(r["RMSE_mm"]), 2),
    "r2": round(float(r["R2"]), 4),
    "points": int(float(r["points"])),
    "inliers": int(float(r["inliers"])),
} for r in sorted(q2, key=lambda r: (img_key(r["image"]), int(r["cluster"])))]
best = max(q2_rows, key=lambda r: r["r2"])
per_img_stats = defaultdict(list)
for r in q2_rows:
    per_img_stats[r["image"]].append(r)
img_summary = []
for img in sorted(per_img_stats, key=img_key):
    rows = per_img_stats[img]
    img_summary.append({
        "image": img,
        "n": len(rows),
        "R_mean": round(sum(r["R"] for r in rows) / len(rows), 2),
        "r2_mean": round(sum(r["r2"] for r in rows) / len(rows), 4),
        "rmse_mean": round(sum(r["rmse"] for r in rows) / len(rows), 2),
    })
data["q2"] = {
    "rows": q2_rows,
    "n_clusters": len(q2_rows),
    "n_images": len(per_img_stats),
    "mean_r2": round(sum(r["r2"] for r in q2_rows) / len(q2_rows), 4),
    "mean_rmse": round(sum(r["rmse"] for r in q2_rows) / len(q2_rows), 2),
    "best": best,
    "img_summary": img_summary,
    "R_min": min(r["R"] for r in q2_rows),
    "R_max": max(r["R"] for r in q2_rows),
    "C_min": min(r["C"] for r in q2_rows),
    "C_max": max(r["C"] for r in q2_rows),
}

# ---- Q3 ----
q3 = read_csv("q3_jrc_results.csv")
per_img3: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
meta3: dict[str, dict[str, float]] = {}
for r in q3:
    img = r["image"].replace(".jpg", "")
    per_img3[img][r["method"]].append(float(r["JRC"]))
    meta3[img] = {"contour": int(float(r["contour_points"])), "area": float(r["area_pixel"])}


def pick(vals: list[float]) -> float:
    return round(vals[0], 2)


q3_rows = []
for img in sorted(per_img3, key=img_key):
    uni = sorted(per_img3[img]["uniform"])
    u64 = round(uni[1], 2) if len(uni) > 1 else None
    u128 = round(uni[2], 2) if len(uni) > 2 else None
    ad = round(per_img3[img]["curvature_adaptive"][0], 2)
    q3_rows.append({
        "image": img,
        "contour": int(meta3[img]["contour"]),
        "area": round(meta3[img]["area"], 1),
        "u32": round(uni[0], 2), "u64": u64, "u128": u128, "ad": ad,
    })
all_jrc = [float(r["JRC"]) for r in q3]
uni_jrc = [float(r["JRC"]) for r in q3 if r["method"] == "uniform"]
ad_jrc = [float(r["JRC"]) for r in q3 if r["method"] == "curvature_adaptive"]
data["q3"] = {
    "rows": q3_rows,
    "n_images": len(q3_rows),
    "n_schemes": len(q3),
    "range_all": [round(min(all_jrc), 2), round(max(all_jrc), 2)],
    "range_uniform": [round(min(uni_jrc), 2), round(max(uni_jrc), 2)],
    "range_adaptive": [round(min(ad_jrc), 2), round(max(ad_jrc), 2)],
    "mean_all": round(sum(all_jrc) / len(all_jrc), 2),
    "mean_uniform": round(sum(uni_jrc) / len(uni_jrc), 2),
    "mean_adaptive": round(sum(ad_jrc) / len(ad_jrc), 2),
}

# ---- Q4 ----
q4 = read_csv("q4_connectivity_results.csv")
q4_rows = [{
    "pair": f"{r['hole_a']}-{r['hole_b']}",
    "seg": int(float(r["segment_start_m"])),
    "d": float(r["feature_difference"]),
    "score": round(float(r["relative_score"]), 4),
} for r in q4]
unc = read_csv("q4_uncertainty_candidates.csv")
data["q4"] = {
    "rows": q4_rows,
    "mean_score": round(sum(r["score"] for r in q4_rows) / len(q4_rows), 4),
    "range": [min(r["score"] for r in q4_rows), max(r["score"] for r in q4_rows)],
    "unc": [{
        "pair": r["between_holes"],
        "seg": int(float(r["segment_start_m"])),
        "u": round(float(r["uncertainty_score"]), 4),
    } for r in sorted(unc, key=lambda r: -float(r["uncertainty_score"]))],
}

with (PROJECT / "results" / "paper_data.json").open("w", encoding="utf-8") as handle:
    json.dump(data, handle, ensure_ascii=False, indent=1)
print("PASS: paper_data.json")
print(json.dumps({k: (v if not isinstance(v, dict) else {kk: '...' for kk in v}) for k, v in data.items()}, ensure_ascii=False)[:400])
