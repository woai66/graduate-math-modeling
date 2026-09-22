#!/usr/bin/env python3
"""检查阶段状态是否允许进入下一阶段。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ORDER = ["problem_reading", "data_analysis", "modeling", "validation", "paper", "independent_review", "submission_package"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("status", type=Path)
    parser.add_argument("stage", choices=ORDER)
    args = parser.parse_args()
    try:
        states = json.loads(args.status.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BLOCKED: cannot read status: {exc}")
        return 2
    index = ORDER.index(args.stage)
    missing = [name for name in ORDER[:index] if states.get(name) != "PASSED"]
    if missing:
        print(f"BLOCKED: previous stages not PASSED: {', '.join(missing)}")
        return 1
    print(f"PASS: {args.stage} may start")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
