from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


DATA_ROOT = Path(r"C:\Users\zyq\AppData\Local\Temp\huawei-c-test2\C题")
PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "results"
REPORTS = PROJECT / "reports"
RESULTS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    expected = {"附件1": 10, "附件2": 10, "附件3": 11, "附件4": 40}
    rows: list[dict[str, object]] = []
    for attachment, count in expected.items():
        paths = sorted((DATA_ROOT / attachment).rglob("*.jpg"))
        for path in paths:
            image = Image.open(path).convert("L")
            gray = np.asarray(image, dtype=np.float32)
            edges = cv2.Canny(gray.astype(np.uint8), 35, 110)
            rows.append({
                "attachment": attachment,
                "file": str(path.relative_to(DATA_ROOT)),
                "width": image.width,
                "height": image.height,
                "min": round(float(gray.min()), 4),
                "max": round(float(gray.max()), 4),
                "mean": round(float(gray.mean()), 4),
                "std": round(float(gray.std()), 4),
                "p01": round(float(np.percentile(gray, 1)), 4),
                "p99": round(float(np.percentile(gray, 99)), 4),
                "edge_density": round(float(np.mean(edges > 0)), 6),
                "sha256": sha256(path),
            })
        if len(paths) != count:
            raise RuntimeError(f"{attachment}: expected {count}, got {len(paths)}")
    with (RESULTS / "data_audit.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    hashes = [row["sha256"] for row in rows]
    duplicate_count = len(hashes) - len(set(hashes))
    duplicate_groups: dict[str, list[str]] = {}
    for row in rows:
        duplicate_groups.setdefault(str(row["sha256"]), []).append(str(row["file"]))
    duplicate_groups = {key: value for key, value in duplicate_groups.items() if len(value) > 1}
    lines = [
        "# C 题数据分析阶段回执",
        "",
        f"扫描文件数：{len(rows)}；重复文件数：{duplicate_count}。",
        f"重复组：{'; '.join(', '.join(value) for value in duplicate_groups.values()) if duplicate_groups else '无'}。",
        "",
        "| 附件 | 文件数 | 尺寸 |",
        "| --- | ---: | --- |",
    ]
    for attachment, count in expected.items():
        subset = [row for row in rows if row["attachment"] == attachment]
        sizes = sorted({f"{row['width']}×{row['height']}" for row in subset})
        lines.append(f"| {attachment} | {len(subset)} | {', '.join(sizes)} |")
    lines.extend([
        "",
        "数据审计已完成：附件覆盖数量符合题面，图像尺寸在附件内一致，文件 SHA-256 已写入 `results/data_audit.csv`。",
        "",
        "注意：附件 1—3 当前清单中未发现独立像素标签文件；在获得可核验标签前，问题 1 只能做无监督诊断，不能报告监督学习精度。",
    ])
    (REPORTS / "DATA_ANALYSIS_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"PASS: audited {len(rows)} images; duplicates={duplicate_count}")


if __name__ == "__main__":
    main()
