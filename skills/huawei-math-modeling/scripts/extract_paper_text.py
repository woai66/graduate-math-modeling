#!/usr/bin/env python3
"""把优秀论文 PDF 抽取成带页码标记的文本，便于逐节研读和定位引用。

用途：解剖参考论文的章节结构、建模链条和验证方式，或核对某个结论所在的页码。
抽取结果是研究笔记的原料，不是论文正文，不得直接复制进参赛论文。

依赖：pdfplumber。若缺失，先 ``uv add pdfplumber``。

示例：
    python extract_paper_text.py <pdf目录> <输出目录>
    python extract_paper_text.py <pdf目录> <输出目录> --headings-only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:  # pragma: no cover - 依赖缺失时给出明确指引
    print("BLOCKED: 缺少 pdfplumber，请先执行 uv add pdfplumber")
    raise SystemExit(2)


# 中文论文常见的章节写法，例如“3.2 模型建立”“四、结果分析”
HEADING_PATTERNS = [
    re.compile(r"^\s*第\s*[一二三四五六七八九十]+\s*[章节部分]"),
    re.compile(r"^\s*[一二三四五六七八九十]+\s*[、.．]\s*\S"),
    re.compile(r"^\s*\d+(?:\.\d+){0,3}\s*[、.．]?\s+\S"),
    re.compile(r"^\s*(摘\s*要|关\s*键\s*词|参考文献|附\s*录|目\s*录|引\s*言)\s*$"),
]


def is_heading(line: str) -> bool:
    text = line.strip()
    if not text or len(text) > 40:
        return False
    return any(pattern.match(text) for pattern in HEADING_PATTERNS)


def extract(path: Path) -> dict:
    pages: list[str] = []
    headings: list[dict] = []
    with pdfplumber.open(path) as pdf:
        page_count = len(pdf.pages)
        for index, page in enumerate(pdf.pages, start=1):
            raw = page.extract_text() or ""
            pages.append(f"\n\n===== 第 {index} 页 =====\n{raw}")
            for line in raw.splitlines():
                if is_heading(line):
                    headings.append({"page": index, "text": line.strip()})
    return {
        "file": path.name,
        "pages": page_count,
        "bytes": path.stat().st_size,
        "headings": headings,
        "text": "".join(pages),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="PDF 文件或包含 PDF 的目录")
    parser.add_argument("output", type=Path, help="文本输出目录")
    parser.add_argument("--headings-only", action="store_true", help="只输出章节大纲")
    args = parser.parse_args()

    targets = sorted(args.source.rglob("*.pdf")) if args.source.is_dir() else [args.source]
    if not targets:
        print("BLOCKED: 未找到 PDF")
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    index: list[dict] = []
    for path in targets:
        record = extract(path)
        stem = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", path.stem)[:80]
        if not args.headings_only:
            (args.output / f"{stem}.txt").write_text(record["text"], encoding="utf-8")
        index.append(
            {
                "file": record["file"],
                "pages": record["pages"],
                "bytes": record["bytes"],
                "headings": record["headings"],
            }
        )
        print(f"OK  {record['pages']:>4} 页  {record['file']}")

    (args.output / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    outline = []
    for record in index:
        outline.append(f"\n## {record['file']}（{record['pages']} 页）\n")
        if not record["headings"]:
            outline.append("- 未识别到章节标题，需人工查看目录页\n")
            continue
        for heading in record["headings"]:
            outline.append(f"- p{heading['page']:>3}  {heading['text']}\n")
    (args.output / "_outlines.md").write_text("".join(outline), encoding="utf-8")
    print(f"PASS: papers={len(index)}; output={args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
