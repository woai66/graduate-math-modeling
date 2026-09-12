#!/usr/bin/env python3
"""统计 DOCX 图片并粗略检查图片后是否有解释性文字。"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "a": A}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--min-figures", type=int, default=1)
    parser.add_argument("--min-explained", type=int, default=1)
    args = parser.parse_args()
    if not args.docx.is_file():
        print(f"FAIL: file not found: {args.docx}")
        return 2
    with zipfile.ZipFile(args.docx) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    paragraphs = root.findall(".//w:p", NS)
    figures = sum(1 for p in paragraphs if p.find(".//a:blip", NS) is not None)
    explained = 0
    for index, paragraph in enumerate(paragraphs):
        if paragraph.find(".//a:blip", NS) is None:
            continue
        following = paragraphs[index + 1:index + 3]
        following_text = "".join("".join(node.itertext()) for item in following for node in item.findall(".//w:t", NS))
        if "图" in following_text or "说明" in following_text or "结果" in following_text:
            explained += 1
    print(f"figures={figures}; explained={explained}")
    passed = figures >= args.min_figures and explained >= args.min_explained
    print(f"{'PASS' if passed else 'WARN'}: figure coverage")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
