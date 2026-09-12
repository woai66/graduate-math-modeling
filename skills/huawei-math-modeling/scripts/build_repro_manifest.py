#!/usr/bin/env python3
"""生成输入文件哈希和运行参数清单，避免结果无法复现。"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--command", default="")
    args = parser.parse_args()
    inputs = []
    for item in args.input:
        path = Path(item)
        if not path.is_file():
            print(f"FAIL: input not found: {path}")
            return 2
        inputs.append({"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "seed": args.seed,
        "command": args.command,
        "inputs": inputs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"PASS: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
