#!/usr/bin/env python3
"""生成可直接填写的研赛论文 DOCX 骨架。

样式依据“华为杯”第二十三届（2026）《论文格式规范》与附件3 模板实测版式：
  - 题目三号黑体居中；一级标题四号黑体居中；其余汉字小四宋体；单倍行距
  - 页边距 上30.0 下17.5 左右22.5 mm；页眉距15.0；页脚距17.5
  - 封面不显示页码；页码从摘要页开始、页脚居中、阿拉伯数字连续
  - 不得有页眉
章节结构参考优秀论文范式（见 references/paper-writing.md）。

用法：
    python build_paper_skeleton.py <输出.docx> [--questions 4] [--title 文本]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Mm, Pt, RGBColor
except ImportError:  # pragma: no cover
    print("BLOCKED: 缺少 python-docx，请先执行 uv add python-docx")
    raise SystemExit(2)


SONG = "宋体"
HEI = "黑体"
WEST = "Times New Roman"
MONO = "Consolas"

PT_TITLE = 16.0      # 三号
PT_HEAD1 = 14.0      # 四号
PT_BODY = 12.0       # 小四
PT_CAPTION = 10.5    # 五号

BLACK = RGBColor(0x1A, 0x1A, 0x1A)


def set_rpr_fonts(rpr, east_asian: str, ascii_font: str) -> None:
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), east_asian)
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)


def set_run_fonts(run_element, east_asian: str, ascii_font: str) -> None:
    set_rpr_fonts(run_element.get_or_add_rPr(), east_asian, ascii_font)


def style_fonts(style, east_asian: str, ascii_font: str, size_pt: float) -> None:
    style.font.name = ascii_font
    style.font.size = Pt(size_pt)
    style.font.color.rgb = BLACK
    set_rpr_fonts(style.element.get_or_add_rPr(), east_asian, ascii_font)


def set_first_line_indent_chars(style, chars: int = 2) -> None:
    """用“字符”为单位设置首行缩进，符合中文排版习惯。"""
    ppr = style.element.get_or_add_pPr()
    ind = ppr.find(qn("w:ind"))
    if ind is None:
        ind = OxmlElement("w:ind")
        ppr.append(ind)
    ind.set(qn("w:firstLineChars"), str(chars * 100))
    ind.set(qn("w:firstLine"), "240")


def clear_spacing(style) -> None:
    pf = style.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE


def add_page_number_field(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)
    set_run_fonts(run._r, SONG, WEST)
    run.font.size = Pt(PT_CAPTION)


def restart_page_number(section, start: int = 1) -> None:
    sect_pr = section._sectPr
    pg = sect_pr.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType")
        sect_pr.append(pg)
    pg.set(qn("w:start"), str(start))


def three_line_borders(table) -> None:
    """把表格设置为三线表：顶线、表头下线、底线。"""
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "8")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    for edge in ("left", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        borders.append(el)
    tbl_pr.append(borders)
    header_cells = table.rows[0].cells
    for cell in header_cells:
        tc_pr = cell._tc.get_or_add_tcPr()
        tc_borders = OxmlElement("w:tcBorders")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:color"), "000000")
        tc_borders.append(bottom)
        tc_pr.append(tc_borders)


def build_styles(doc) -> None:
    normal = doc.styles["Normal"]
    style_fonts(normal, SONG, WEST, PT_BODY)
    clear_spacing(normal)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    set_first_line_indent_chars(normal, 2)

    h1 = doc.styles["Heading 1"]
    style_fonts(h1, HEI, WEST, PT_HEAD1)
    clear_spacing(h1)
    h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    h2 = doc.styles["Heading 2"]
    style_fonts(h2, HEI, WEST, PT_BODY)
    clear_spacing(h2)
    h2.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    h3 = doc.styles["Heading 3"]
    style_fonts(h3, HEI, WEST, PT_BODY)
    clear_spacing(h3)
    h3.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

    caption = doc.styles["Caption"]
    style_fonts(caption, SONG, WEST, PT_CAPTION)
    clear_spacing(caption)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 自定义样式：论文题目、封面文字、参考文献条目、代码
    title = doc.styles.add_style("论文题目", 1)  # 1 = paragraph
    title.base_style = doc.styles["Normal"]
    style_fonts(title, HEI, WEST, PT_TITLE)
    clear_spacing(title)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_first_line_indent_chars(title, 0)

    cover = doc.styles.add_style("封面标题", 1)
    cover.base_style = doc.styles["Normal"]
    style_fonts(cover, HEI, WEST, 18.0)
    clear_spacing(cover)
    cover.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_first_line_indent_chars(cover, 0)

    ref = doc.styles.add_style("参考文献条目", 1)
    ref.base_style = doc.styles["Normal"]
    style_fonts(ref, SONG, WEST, PT_CAPTION)
    clear_spacing(ref)
    ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    ref.paragraph_format.left_indent = Pt(21)
    ref.paragraph_format.first_line_indent = Pt(-21)

    code = doc.styles.add_style("代码", 1)
    code.base_style = doc.styles["Normal"]
    style_fonts(code, SONG, MONO, PT_CAPTION)
    clear_spacing(code)
    code.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_first_line_indent_chars(code, 0)

    # 填写提示：灰色五号，明显区别于正文，定稿前应全部删除
    note = doc.styles.add_style("提示", 1)
    note.base_style = doc.styles["Normal"]
    style_fonts(note, SONG, WEST, PT_CAPTION)
    note.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    clear_spacing(note)
    note.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_first_line_indent_chars(note, 0)


def setup_section(section) -> None:
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(1.75)
    section.left_margin = Cm(2.25)
    section.right_margin = Cm(2.25)
    section.header_distance = Cm(1.5)
    section.footer_distance = Cm(1.75)


def h(doc, text: str, level: int):
    return doc.add_heading(text, level=level)


def p(doc, text: str, style: str | None = None):
    if style is None and text.startswith("【"):
        style = "提示"
    return doc.add_paragraph(text, style=style)


def caption(doc, text: str):
    return doc.add_paragraph(text, style="Caption")


def build_question(doc, index: int, total: int) -> None:
    ordinal = ["一", "二", "三", "四", "五"][index - 1]
    h(doc, f"{4 + index} 问题{ordinal}：模型建立与求解", 1)
    p(doc, "【本问要回答的任务、题面编号与输出要求】")
    sections = [
        ("问题分析", "【本问与前后问的联系、难点、可计算定义与反例、选模理由】"),
        ("数据与特征", "【使用的数据、字段、单位、缺失与异常处理、特征构造依据】"),
        ("模型建立", "【变量、假设、目标函数或统计模型、公式推导与符号说明】"),
        ("参数估计与求解算法", "【参数来源、初值与搜索范围、停止条件、复杂度、求解器版本】"),
        ("结果与分析", "【真实运行结果、图表编号与解释、与基线的比较】"),
        ("验证与敏感性分析", "【独立验证方式、关键参数扰动、失败样本与适用范围】"),
        ("小结", "【本问结论、单位、不确定性与对下一问的接口】"),
    ]
    for order, (sub_title, hint) in enumerate(sections, start=1):
        h(doc, f"{4 + index}.{order} {sub_title}", 2)
        p(doc, hint)
        if sub_title == "结果与分析":
            caption(doc, f"图 {4 + index}-1 【图题：说明对象、条件与单位】")
            caption(doc, f"表 {4 + index}-1 【表题：说明对象、条件与单位】")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--questions", type=int, default=4, help="题面的问题数量，默认 4")
    parser.add_argument("--title", default="【在此填写论文题目】")
    args = parser.parse_args()
    if not 1 <= args.questions <= 5:
        print("BLOCKED: --questions 需在 1—5 之间")
        return 2

    doc = Document()
    build_styles(doc)
    setup_section(doc.sections[0])

    # ---------- 封面（不显示页码） ----------
    p(doc, "中国研究生创新实践系列大赛", style="封面标题")
    p(doc, "“华为杯”第二十三届中国研究生数学建模竞赛", style="封面标题")
    doc.add_paragraph()
    doc.add_paragraph()
    p(doc, args.title, style="论文题目")
    p(doc, "【按当届开赛公告确认是否需要填写队伍编号；附件2 禁止出现学校、姓名等身份信息】")
    doc.add_section(WD_SECTION.NEW_PAGE)
    setup_section(doc.sections[1])
    restart_page_number(doc.sections[1], 1)

    # 封面不显示页码；摘要页起显示居中页码
    doc.sections[0].footer.is_linked_to_previous = False
    for para in doc.sections[0].footer.paragraphs:
        para.text = ""
    doc.sections[0].header.is_linked_to_previous = False
    for para in doc.sections[0].header.paragraphs:
        para.text = ""

    footer = doc.sections[1].footer
    footer.is_linked_to_previous = False
    foot_para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    foot_para.text = ""
    foot_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number_field(foot_para)
    for para in doc.sections[1].header.paragraphs:
        para.text = ""

    # ---------- 摘要页 ----------
    p(doc, args.title, style="论文题目")
    h(doc, "摘 要", 1)
    p(
        doc,
        "【摘要需写清：针对问题一……；针对问题二……；最后是总体结论与创新点。"
        "每个定量结论都要有真实运行结果支撑，一般不超过两页，无需英文。】",
    )
    p(doc, "【创新点：说明新在哪里、为什么旧方法不够、如何验证、适用边界。】")
    para = p(doc, "关键词：【关键词一；关键词二；关键词三；关键词四】")
    para.paragraph_format.first_line_indent = Pt(0)
    doc.add_page_break()

    # ---------- 正文 ----------
    h(doc, "1 问题重述", 1)
    h(doc, "1.1 问题背景", 2)
    p(doc, "【只写与本题相关的背景，避免大段科普。】")
    h(doc, "1.2 问题提出", 2)
    p(doc, "【逐问复述任务动词、对象、输入、输出、约束和评价口径。】")

    h(doc, "2 问题分析与技术路线", 1)
    h(doc, "2.1 总体思路", 2)
    p(doc, "【说明各问之间的依赖关系、跨问接口和不确定性传递。】")
    h(doc, "2.2 各问难点与建模思路", 2)
    p(doc, "【逐问说明难点、候选路线、选择理由和验证方式。】")
    h(doc, "2.3 技术路线图", 2)
    caption(doc, "图 2-1 【技术路线图：与正文各问一一对应】")

    h(doc, "3 模型假设与符号说明", 1)
    h(doc, "3.1 模型假设", 2)
    p(doc, "【假设 1：……（写清工程或数据依据，并说明可检验方式）。】")
    h(doc, "3.2 符号说明", 2)
    table = doc.add_table(rows=3, cols=3)
    data = [
        ("符号", "含义", "单位"),
        ("x", "决策变量", "—"),
        ("ρ", "空气密度", "kg/m³"),
    ]
    for r, row in enumerate(data):
        for c, text in enumerate(row):
            table.cell(r, c).text = text
    three_line_borders(table)
    caption(doc, "表 3-1 符号说明")

    h(doc, "4 数据来源与预处理", 1)
    h(doc, "4.1 数据来源与字段说明", 2)
    p(doc, "【来源、文件清单与哈希、字段、单位、坐标系、时间范围与业务键。】")
    h(doc, "4.2 数据初检", 2)
    p(doc, "【样本量、缺失、异常、重复、标签分布、覆盖范围。】")
    h(doc, "4.3 数据预处理", 2)
    p(doc, "【清洗规则、处理前后行数、防泄漏的划分方式与其依据。】")

    for i in range(1, args.questions + 1):
        build_question(doc, i, args.questions)

    h(doc, f"{4 + args.questions} 模型评价与推广", 1)
    h(doc, f"{4 + args.questions}.1 模型优点", 2)
    p(doc, "【逐问说明优点，不要只写统一的一段。】")
    h(doc, f"{4 + args.questions}.2 模型不足", 2)
    p(doc, "【写清失效条件、未覆盖样本与证据边界。】")
    h(doc, f"{4 + args.questions}.3 改进方向与推广", 2)
    p(doc, "【说明进一步可做的实验与适用范围。】")

    h(doc, f"{5 + args.questions} 参考文献", 1)
    for sample in [
        "[1] 作者，书名，出版地：出版社，起止页码，出版年。",
        "[2] 作者，论文名，杂志名，卷期号：起止页码，出版年。",
        "[3] 作者，资源标题，网址，访问时间（年月日）。",
    ]:
        p(doc, sample, style="参考文献条目")
    p(doc, "【正文引用处用方括号标注编号，如 [1][3]；引用书籍必须指出页码；每条文献都要被正文引用。】")

    h(doc, f"{6 + args.questions} 附录", 1)
    h(doc, f"{6 + args.questions}.1 程序代码索引", 2)
    p(doc, "【列出代码文件名、用途与运行入口；源代码按题目要求另行提交竞赛系统。】")
    h(doc, f"{6 + args.questions}.2 复现环境与运行说明", 2)
    p(doc, "【Python 版本、依赖锁、随机种子、运行命令、输入哈希。】", style="代码")
    h(doc, f"{6 + args.questions}.3 人工智能工具使用说明", 2)
    p(
        doc,
        "【按附件4 要求列明：工具名称、版本/型号、开发机构/公司、版本发布日期，"
        "以及本队在哪些环节使用、做了哪些核对与修改。】",
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(args.output)
    print(f"PASS: 已生成 {args.output}（{args.questions} 个问题章节）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
