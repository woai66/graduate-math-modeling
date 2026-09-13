#!/usr/bin/env python3
"""批量统计优秀论文 PDF 页数，生成可追溯的样本画像。"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


def pages(path: Path) -> int | None:
    try:
        result = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = []
    for path in sorted(args.root.rglob("*.pdf")):
        records.append({"path": str(path), "pages": pages(path), "bytes": path.stat().st_size})
    if not records:
        print("BLOCKED: no PDF files found")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    valid = [r["pages"] for r in records if r["pages"] is not None]
    print(f"PASS: papers={len(records)}; pages_min={min(valid)}; pages_max={max(valid)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
