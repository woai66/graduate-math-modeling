#!/usr/bin/env python3
"""检查论文候选稿是否具备最小提交证据。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_STAGES = ["problem_reading", "data_analysis", "modeling", "validation", "paper", "independent_review"]
FORBIDDEN = ["TODO", "待补充", "示意图", "仅供参考", "example.com"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--paper", type=Path)
    args = parser.parse_args()
    project = args.project
    errors: list[str] = []
    status_path = project / "stage_status.json"
    if not status_path.is_file():
        errors.append("missing stage_status.json")
    else:
        try:
            states = json.loads(status_path.read_text(encoding="utf-8"))
            errors.extend(f"stage {stage} is not PASSED" for stage in REQUIRED_STAGES if states.get(stage) != "PASSED")
        except json.JSONDecodeError:
            errors.append("invalid stage_status.json")
    matrix = project / "reports" / "evidence_matrix.csv"
    if not matrix.is_file() or matrix.stat().st_size <= 100:
        errors.append("evidence matrix missing or empty")
    paper = args.paper or project / "完整论文.docx"
    if paper.is_file():
        raw = paper.read_bytes()
        for marker in FORBIDDEN:
            if marker.encode("utf-8") in raw:
                errors.append(f"forbidden placeholder/claim marker: {marker}")
    else:
        errors.append(f"missing paper: {paper}")
    if errors:
        print("BLOCKED: submission readiness failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: minimum submission evidence present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
