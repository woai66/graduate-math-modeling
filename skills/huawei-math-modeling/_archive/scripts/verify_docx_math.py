#!/usr/bin/env python3
"""统计 DOCX 中的 Office Math ML 公式。"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--min-equations", type=int, default=1)
    args = parser.parse_args()
    if not args.docx.is_file():
        print(f"FAIL: file not found: {args.docx}")
        return 2
    with zipfile.ZipFile(args.docx) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    count = len(root.findall(f".//{{{M}}}oMath")) + len(root.findall(f".//{{{M}}}oMathPara"))
    print(f"equations={count}; required={args.min_equations}")
    if count < args.min_equations:
        print("WARN: equation count below requested minimum")
        return 1
    print("PASS: equation count")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
