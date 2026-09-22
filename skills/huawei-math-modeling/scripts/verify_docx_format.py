#!/usr/bin/env python3
"""核对 DOCX 是否符合研赛论文格式规范（字体、字号、行距、页码、页眉、纸张）。

依据“华为杯”第二十三届（2026）《论文格式规范》：
  - 论文题目：三号黑体，居中
  - 一级标题：四号黑体，居中
  - 其他汉字：小四号宋体
  - 行距：单倍
  - 页码：从摘要页起，位于页脚中部，阿拉伯数字连续编号
  - 不得有页眉

本脚本只报告它真正读到的样式与页面设置。它无法判断公式是否可编辑、分页是否合理、
图表位置是否美观、参考文献是否真实，这些必须导出 PDF 后人工逐页查看。

用法：
    python verify_docx_format.py <论文.docx> [--max-report 20]
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Emu, Pt
except ImportError:  # pragma: no cover
    print("BLOCKED: 缺少 python-docx，请先执行 uv add python-docx")
    raise SystemExit(2)


# 官方字号（磅）
SIZE_TITLE = 16.0   # 三号
SIZE_HEADING1 = 14.0  # 四号
SIZE_BODY = 12.0    # 小四
SIZE_CAPTION = 10.5  # 五号

FONT_SONG = {"宋体", "SimSun", "NSimSun"}
FONT_HEI = {"黑体", "SimHei"}
FONT_WEST = {"Times New Roman"}

FIELD_PAGE = ("PAGE",)

# 官方附件3 论文模板实测页边距（mm），容差 ±2 mm
TEMPLATE_MARGINS_MM = {"top": 30.0, "bottom": 17.5, "left": 22.5, "right": 22.5}
MARGIN_TOLERANCE_MM = 2.0


def iter_runs(paragraph):
    for run in paragraph.runs:
        if run.text.strip():
            yield run


def run_east_asian_font(run) -> str | None:
    rpr = run._element.rPr
    if rpr is None or rpr.rFonts is None:
        return None
    return rpr.rFonts.get(qn("w:eastAsia"))


def run_ascii_font(run) -> str | None:
    rpr = run._element.rPr
    if rpr is None or rpr.rFonts is None:
        return None
    return rpr.rFonts.get(qn("w:ascii"))


def style_chain(paragraph):
    """返回段落样式链上的 (east_asian, ascii, size) 首个非空取值。"""
    ea = ascii_ = size = None
    styles = []
    style = paragraph.style
    while style is not None:
        styles.append(style)
        style = style.base_style
        if len(styles) > 8:
            break
    for st in styles:
        font = st.font
        if ea is None:
            rpr = st.element.rPr
            if rpr is not None and rpr.rFonts is not None:
                ea = rpr.rFonts.get(qn("w:eastAsia"))
                ascii_ = rpr.rFonts.get(qn("w:ascii"))
        if size is None and font.size is not None:
            size = font.size.pt
    return ea, ascii_, size


def effective_format(paragraph):
    """取段落首个有效文字 run 的字体字号，缺失时回退到样式链。"""
    ea = ascii_ = size = None
    for run in iter_runs(paragraph):
        ea = run_east_asian_font(run) or ea
        ascii_ = run_ascii_font(run) or ascii_
        if run.font.size is not None:
            size = run.font.size.pt
        if ea and size:
            break
    if ea is None or size is None:
        s_ea, s_ascii, s_size = style_chain(paragraph)
        ea = ea or s_ea
        ascii_ = ascii_ or s_ascii
        size = size if size is not None else s_size
    return ea, ascii_, size


def line_spacing(paragraph) -> float | None:
    pf = paragraph.paragraph_format
    ls = pf.line_spacing
    if ls is None:
        # 回退到样式链
        style = paragraph.style
        while style is not None:
            if style.paragraph_format.line_spacing is not None:
                return style.paragraph_format.line_spacing
            style = style.base_style
        return None
    return ls


def style_name(paragraph) -> str:
    style = paragraph.style
    if style is None or style.name is None:
        return ""
    return style.name


def has_page_field(container_part) -> bool:
    """检查页眉/页脚 XML 中是否存在 PAGE 域。"""
    if container_part is None:
        return False
    xml = container_part._element.xml
    return any(token in xml for token in FIELD_PAGE)


def header_has_text(section) -> bool:
    """页眉是否含可见文字（不含页码域）。"""
    header = section.header
    if header is None:
        return False
    return any(p.text.strip() for p in header.paragraphs)


import re


HEADING_PATTERNS = [
    re.compile(r"^第\s*[一二三四五六七八九十]+\s*[章节部分]"),
    re.compile(r"^[一二三四五六七八九十]+\s*[、.．]"),
    re.compile(r"^\d+(?:\.\d+){0,3}\s*[、.．]?\s*\S"),
    re.compile(r"^（[一二三四五六七八九十]+）"),
]

SPECIAL_HEADINGS = {"摘要", "关键词", "参考文献", "附录", "目录", "问题重述", "模型假设", "符号说明"}

HEADING_STYLE_RE = re.compile(r"^(heading|标题)\s*([1-9])$", re.IGNORECASE)
TITLE_STYLE_NAMES = {"论文题目", "论文标题", "题目"}
COVER_STYLE_NAMES = {"封面标题", "封面副标题"}
REFERENCE_STYLE_NAMES = {"参考文献条目", "参考文献"}
NOTE_STYLE_NAMES = {"提示", "填写提示", "批注"}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
CODE_HINT_RE = re.compile(r"[{};=<>\[\]]|^\s{2,}\S")


def looks_like_code(text: str) -> bool:
    """附录代码通常无中文、含缩进或典型符号，单独归类避免误判正文字号。"""
    if CJK_RE.search(text):
        return False
    if len(text) < 6:
        return False
    return bool(CODE_HINT_RE.search(text))


def classify(paragraph) -> str:
    """粗略分类段落用途，用于套用不同字号要求。"""
    text = paragraph.text.strip()
    name = style_name(paragraph)
    lower = name.lower()
    if not text:
        return "empty"
    if name in TITLE_STYLE_NAMES:
        return "title"
    if name in COVER_STYLE_NAMES:
        return "cover"
    if name in REFERENCE_STYLE_NAMES:
        return "reference"
    if name in NOTE_STYLE_NAMES:
        return "note"
    if "caption" in lower or "题注" in name:
        return "caption"
    if "代码" in name or "code" in lower or "preformatted" in lower:
        return "code"
    # 只有规范命名的标题样式才算标题；封面标题、论文题目等自定义样式按各自规则处理
    heading_match = HEADING_STYLE_RE.match(name.strip())
    if heading_match:
        return f"heading{int(heading_match.group(2))}"
    if len(text) <= 30 and (text.startswith("图") or text.startswith("表")):
        return "caption"
    # 未使用标题样式但结构上属于标题的段落
    compact = re.sub(r"\s+", "", text)
    if len(compact) <= 40 and any(p.match(text.strip()) for p in HEADING_PATTERNS):
        return "heading1"
    if compact in SPECIAL_HEADINGS:
        return "heading1"
    if looks_like_code(text):
        return "code"
    return "body"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("--max-report", type=int, default=20)
    args = parser.parse_args()
    if not args.docx.is_file():
        print(f"BLOCKED: 文件不存在: {args.docx}")
        return 2

    doc = Document(args.docx)
    problems: list[str] = []
    notes: list[str] = []

    # 页面设置
    page_field_sections = [i for i, s in enumerate(doc.sections, 1) if has_page_field(s.footer)]
    for index, section in enumerate(doc.sections, 1):
        width_mm = section.page_width.mm if section.page_width else 0
        height_mm = section.page_height.mm if section.page_height else 0
        if not (205 <= width_mm <= 215 and 292 <= height_mm <= 302):
            problems.append(f"第 {index} 节纸张 {width_mm:.1f}×{height_mm:.1f} mm，不是 A4")
        notes.append(
            "第 {i} 节 A4={ok} 页边距(上下左右 mm)：{t:.1f}/{b:.1f}/{l:.1f}/{r:.1f}".format(
                i=index,
                ok="是" if (205 <= width_mm <= 215) else "否",
                t=section.top_margin.mm if section.top_margin else 0,
                b=section.bottom_margin.mm if section.bottom_margin else 0,
                l=section.left_margin.mm if section.left_margin else 0,
                r=section.right_margin.mm if section.right_margin else 0,
            )
        )
        actual = {
            "top": section.top_margin.mm if section.top_margin else 0,
            "bottom": section.bottom_margin.mm if section.bottom_margin else 0,
            "left": section.left_margin.mm if section.left_margin else 0,
            "right": section.right_margin.mm if section.right_margin else 0,
        }
        deviating = [
            "%s %.1f→%.1f" % (side, actual[side], expect)
            for side, expect in TEMPLATE_MARGINS_MM.items()
            if abs(actual[side] - expect) > MARGIN_TOLERANCE_MM
        ]
        if deviating:
            notes.append(
                "第 %d 节页边距与官方模板偏差（实际→模板 mm）：%s" % (index, "，".join(deviating))
            )
        if header_has_text(section):
            problems.append(f"第 {index} 节页眉有内容；官方要求不得有页眉")
        footer = section.footer
        if not has_page_field(footer):
            if index == 1 and len(doc.sections) > 1 and page_field_sections:
                notes.append(f"第 {index} 节页脚无页码域（封面不编号，符合规范）")
            else:
                problems.append(f"第 {index} 节页脚未检测到 PAGE 页码域；官方要求页脚中部自动页码")

    # 段落格式
    body_total = 0
    body_bad_font = 0
    body_bad_size = 0
    body_bad_spacing = 0
    body_fonts: collections.Counter = collections.Counter()
    body_sizes: collections.Counter = collections.Counter()
    body_spacings: collections.Counter = collections.Counter()
    skipped_styles: collections.Counter = collections.Counter()
    samples: list[str] = []
    for paragraph in doc.paragraphs:
        kind = classify(paragraph)
        if kind == "empty":
            continue
        if kind in ("cover", "reference", "caption", "code", "note"):
            skipped_styles[kind] += 1
            continue
        ea, ascii_, size = effective_format(paragraph)
        ls = line_spacing(paragraph)
        text = paragraph.text.strip()
        snippet = text[:36] + ("…" if len(text) > 36 else "")

        if kind == "body":
            body_total += 1
            body_fonts[ea or "(未设置)"] += 1
            body_sizes[("%.1f" % size) if size is not None else "(未设置)"] += 1
            body_spacings[str(ls) if ls is not None else "(继承)"] += 1
            if ea not in FONT_SONG:
                body_bad_font += 1
                if len(samples) < args.max_report:
                    samples.append(f"[正文字体] 期望宋体，实际 {ea or '未显式设置'}：{snippet}")
            if size is None or abs(size - SIZE_BODY) > 0.2:
                body_bad_size += 1
                if len(samples) < args.max_report:
                    samples.append(
                        f"[正文字号] 期望小四 12 pt，实际 {size if size else '未设置'}：{snippet}"
                    )
            if ls not in (None, 1.0):
                body_bad_spacing += 1
                if len(samples) < args.max_report:
                    samples.append(f"[正文行距] 期望单倍，实际 {ls}：{snippet}")
            if ascii_ and ascii_ not in FONT_WEST:
                if len(samples) < args.max_report:
                    samples.append(f"[西文字体] 期望 Times New Roman，实际 {ascii_}：{snippet}")
        elif kind == "heading1":
            if ea not in FONT_HEI:
                if len(samples) < args.max_report:
                    samples.append(f"[一级标题字体] 期望黑体，实际 {ea or '未显式设置'}：{snippet}")
            if size is None or abs(size - SIZE_HEADING1) > 0.2:
                if len(samples) < args.max_report:
                    samples.append(
                        f"[一级标题字号] 期望四号 14 pt，实际 {size if size else '未设置'}：{snippet}"
                    )
        elif kind == "title":
            if ea not in FONT_HEI:
                problems.append(f"论文题目期望黑体三号，实际字体 {ea or '未显式设置'}")
            if size is None or abs(size - SIZE_TITLE) > 0.2:
                problems.append(f"论文题目期望三号 16 pt，实际 {size if size else '未设置'}")

    # 没有“论文题目”样式时，退回到首个非空段落
    if not any(p.text.strip() and style_name(p) in TITLE_STYLE_NAMES for p in doc.paragraphs):
        first_text = next((p for p in doc.paragraphs if p.text.strip()), None)
        if first_text is not None:
            ea, _, size = effective_format(first_text)
            if ea not in FONT_HEI:
                problems.append(f"首个非空段落（题目）期望黑体三号，实际字体 {ea or '未显式设置'}")
            if size is None or abs(size - SIZE_TITLE) > 0.2:
                problems.append(f"首个非空段落（题目）期望三号 16 pt，实际 {size if size else '未设置'}")

    print(f"文件: {args.docx.name}")
    for note in notes:
        print("  " + note)

    # 正文段落为空时（例如空白骨架），退回到检查 Normal 样式定义
    if body_total == 0:
        normal = doc.styles["Normal"]
        ea, ascii_, size = None, None, None
        rpr = normal.element.rPr
        if rpr is not None and rpr.rFonts is not None:
            ea = rpr.rFonts.get(qn("w:eastAsia"))
            ascii_ = rpr.rFonts.get(qn("w:ascii"))
        if normal.font.size is not None:
            size = normal.font.size.pt
        print("  未发现正文段落，改为检查 Normal 样式定义")
        if ea not in FONT_SONG:
            problems.append(f"Normal 样式期望宋体，实际 {ea or '未设置'}")
        if size is None or abs(size - SIZE_BODY) > 0.2:
            problems.append(f"Normal 样式期望小四 12 pt，实际 {size if size else '未设置'}")
        if ascii_ and ascii_ not in FONT_WEST:
            problems.append(f"Normal 样式西文期望 Times New Roman，实际 {ascii_}")

    print(
        "正文段落统计: 检查 {n} 段；字体不符 {f}；字号不符 {s}；行距不符 {sp}".format(
            n=body_total, f=body_bad_font, s=body_bad_size, sp=body_bad_spacing
        )
    )
    if body_total:
        print("  正文中文字体分布: " + "，".join(f"{k}×{v}" for k, v in body_fonts.most_common(5)))
        print("  正文字号分布(pt): " + "，".join(f"{k}×{v}" for k, v in body_sizes.most_common(5)))
        print("  正文行距分布: " + "，".join(f"{k}×{v}" for k, v in body_spacings.most_common(5)))
    if skipped_styles:
        print(
            "  按专用规则跳过: "
            + "，".join(f"{k}×{v}" for k, v in skipped_styles.most_common())
            + "（封面、参考文献、图表题注、代码各有自己的字号要求）"
        )
    for item in samples:
        print("  - " + item)
    if problems:
        print("BLOCKED: 格式规范未满足")
        for item in problems:
            print("  - " + item)
        return 1
    if body_bad_font or body_bad_size or body_bad_spacing:
        print("WARN: 正文存在与原规范不一致的段落，见上表")
        return 1
    print("PASS: 已检查项符合官方字体、字号、行距、页码与页眉要求")
    print("注意：公式可编辑性、分页、图表位置、参考文献真实性仍需人工逐页核查")
    return 0


if __name__ == "__main__":
    sys.exit(main())
