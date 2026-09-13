#!/usr/bin/env python3
"""检查证据矩阵是否非空且路径可追溯。"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

REQUIRED = {"claim_id", "question", "claim_text", "evidence_path", "code_path", "parameters", "validation", "status"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if not args.matrix.is_file():
        print(f"BLOCKED: missing matrix {args.matrix}")
        return 2
    with args.matrix.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        rows = list(reader)
    errors = []
    errors.extend(f"missing column: {name}" for name in REQUIRED - fields)
    ids = [row.get("claim_id", "") for row in rows]
    if not rows:
        errors.append("matrix has no claims")
    if len(ids) != len(set(ids)):
        errors.append("claim_id is not unique")
    for index, row in enumerate(rows, 2):
        for field in ("claim_text", "evidence_path", "code_path", "parameters", "validation", "status"):
            if not row.get(field, "").strip():
                errors.append(f"row {index}: empty {field}")
        for field in ("evidence_path", "code_path"):
            raw = row.get(field, "").strip()
            if raw and not (args.project_root / raw).exists():
                errors.append(f"row {index}: missing path {field}={raw}")
    if errors:
        print("BLOCKED: evidence matrix invalid")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: evidence matrix rows={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
