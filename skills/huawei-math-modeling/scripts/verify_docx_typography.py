#!/usr/bin/env python3
"""对数学建模 Word 文档做轻量结构预检。"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    if not args.docx.is_file():
        print(f"FAIL: file not found: {args.docx}")
        return 2
    with zipfile.ZipFile(args.docx) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    text = "\n".join("".join(node.itertext()) for node in root.findall(".//w:p", NS))
    checks = {
        "has_text": bool(text.strip()),
        "has_abstract": "摘要" in text,
        "has_keywords": "关键词" in text,
        "has_references": "参考文献" in text,
        "has_appendix": "附录" in text,
    }
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'WARN'}: {name}")
    print(f"paragraphs={len(root.findall('.//w:p', NS))}")
    return 0 if checks["has_text"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
