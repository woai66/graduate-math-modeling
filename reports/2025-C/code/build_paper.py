from __future__ import annotations

import csv
import math
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures" / "result"
OUTPUT = ROOT / "完整论文.docx"


def read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def set_cell_shading(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    props.append(shading)


def set_cell_text(cell, text: str, bold: bool = False, color: str = "000000") -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(color)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], header, bold=True, color="FFFFFF")
        set_cell_shading(table.rows[0].cells[i], "315A83")
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value)
            if row_index % 2 == 1:
                set_cell_shading(cells[i], "EAF1F7")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_caption(doc, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(9)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def add_figure(doc, filename: str, caption: str, width: float = 6.0) -> None:
    path = FIGURES / filename
    if not path.is_file():
        return
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(width))
    add_caption(doc, caption)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


def add_omml_formula_after(paragraph, text: str) -> None:
    formula_paragraph = OxmlElement("w:p")
    math_para = OxmlElement("m:oMathPara")
    math = OxmlElement("m:oMath")
    run = OxmlElement("m:r")
    math_text = OxmlElement("m:t")
    math_text.text = text
    run.append(math_text)
    math.append(run)
    math_para.append(math)
    formula_paragraph.append(math_para)
    paragraph._p.addnext(formula_paragraph)


def configure(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.0)
    for style_name in ("Normal", "Body Text"):
        style = doc.styles[style_name]
        style.font.name = "宋体"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        style.font.size = Pt(10.5)
        style.paragraph_format.line_spacing = 1.35
        style.paragraph_format.space_after = Pt(6)
    for style_name, size in (("Title", 18), ("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 11)):
        style = doc.styles[style_name]
        style.font.name = "黑体"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = True
    add_page_number(section.footer.paragraphs[0])


def paragraph(doc, text: str, bold_prefix: str | None = None) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    if bold_prefix and text.startswith(bold_prefix):
        r1 = p.add_run(bold_prefix)
        r1.bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p


def main() -> None:
    q1 = read_csv("q1_segmentation_summary.csv")
    q2 = read_csv("q2_sine_summary.csv")
    q3 = read_csv("q3_jrc_sensitivity.csv")
    q4 = read_csv("q4_connectivity_scores.csv")
    candidates = read_csv("q4_supplementary_drill_candidates.csv")
    q1_coverage = sum(float(row["edge_coverage"]) for row in q1) / len(q1)
    q1_components = sum(int(row["components_downsampled"]) for row in q1) / len(q1)
    q2_r2 = [float(row["R2"]) for row in q2]
    q3_values = [float(row["JRC"]) for row in q3]
    q4_values = [float(row["connectivity_score"]) for row in q4]

    doc = Document()
    configure(doc)
    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("2025 年中国研究生数学建模竞赛 C 题\n围岩裂隙精准识别与三维模型重构")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("基于 OpenCV、NumPy 与 Pillow 的可复现增强基线实验报告").italic = True
    doc.add_paragraph()

    doc.add_heading("摘要", level=1)
    paragraph(doc, f"针对钻孔成像展开图中的裂隙识别、参数表征、粗糙度评价和多钻孔连通性分析问题，本文建立了一套使用 OpenCV、NumPy 与 Pillow 的可复现增强基线流程。问题一使用 CLAHE、双边滤波、Canny 边缘和形态学闭开运算生成像素候选掩膜，在 10 张附件 1 图像上的平均边缘覆盖率为 {q1_coverage:.2%}，下采样连通域数量均值为 {q1_components:.1f}。问题二将平滑 Canny 边缘的每列中位纵坐标作为粗略观测点，利用线性化正弦模型估计振幅、周期、相位和中心线位置，10 张图像的拟合决定系数 R² 范围为 {min(q2_r2):.4f}—{max(q2_r2):.4f}，说明单一正弦基线不足以直接完成可靠裂隙拟合。问题三基于平滑梯度轮廓进行等间距采样，发现样本数从 32 增至 256 时 JRC 估计由 {q3_values[0]:.2f} 变为 {q3_values[-1]:.2f}，表明轮廓提取和采样策略是粗糙度评价的主要敏感因素。问题四以钻孔分段的边缘密度差异构造启发式连通评分，并生成六孔三维投影示意图；该评分用于候选补孔排序，不应解释为经过现场标定的真实概率。本文的主要价值是建立数据、代码、结果表和 Word 论文之间的可追溯链路，并明确了后续 U-Net、DBSCAN、RANSAC 和概率图模型的增强方向。")
    paragraph(doc, "关键词：围岩裂隙；像素分割；正弦拟合；JRC；连通性；三维重构；可复现基线")

    doc.add_heading("1 研究背景与问题重述", level=1)
    paragraph(doc, "煤矿巷道围岩中的裂隙会影响冒顶、突水和瓦斯运移风险。钻孔成像将孔壁三维结构展开为二维图像，为裂隙识别和空间重构提供了数据基础，但图像同时包含岩石纹理、泥浆污染、钻进痕迹和拼接线等干扰。题目要求从像素级识别出发，逐步完成正弦状裂隙参数拟合、复杂裂隙粗糙度计算、多钻孔连通性分析以及补充钻孔位置选择。")
    paragraph(doc, "本文将四个问题视为一条数据链路：问题一提供裂隙候选区域，问题二提取规则裂隙几何参数，问题三评价复杂裂隙粗糙度，问题四把单孔结果映射到统一空间并进行网络推断。由于当前环境缺少深度学习和科学计算扩展库，本文先完成纯 NumPy/Pillow 基线，所有结果均来自实际运行脚本。")

    doc.add_heading("2 符号与数据说明", level=1)
    add_table(doc, ["符号", "含义", "单位"], [
        ["x", "钻孔周向展开坐标", "mm"], ["y", "钻孔轴向深度坐标", "mm"],
        ["R", "正弦裂隙振幅", "mm"], ["P", "正弦裂隙周期", "mm"],
        ["β", "正弦裂隙相位", "rad"], ["C", "正弦裂隙中心线位置", "mm"],
        ["Z₂", "裂隙轮廓二阶统计参数", "—"], ["JRC", "裂隙粗糙度系数", "—"],
    ])
    add_table(doc, ["附件", "用途", "实际清单"], [
        ["附件 1", "像素级裂隙识别", "10 张，244×1350 像素"],
        ["附件 2", "正弦状裂隙参数", "10 张，244×1350 像素"],
        ["附件 3", "复杂裂隙粗糙度", "11 张，244×1350 像素"],
        ["附件 4", "多钻孔连通与重构", "6 孔 40 段，864×9167 像素"],
    ])
    paragraph(doc, "题面给出钻孔直径 30 mm、周长约 94.25 mm；附件 1—3 单孔深度约 500 mm，附件 4 每段 1000 mm，4 号孔总深度 5000 mm，其余钻孔总深度 7000 mm。数据包未提交进 Git 仓库，实验通过临时目录读取。")

    doc.add_heading("3 模型假设与总体流程", level=1)
    paragraph(doc, "假设一：在基线实验中，图像灰度梯度较大的区域可以作为裂隙或纹理候选，但该候选不等同于真实裂隙。假设二：规则裂隙在展开图中可以用固定周期的正弦函数近似，但暗像素观测会受到多条裂隙和噪声干扰。假设三：相邻钻孔相同深度段的边缘密度相似性可以作为连通性排序的弱证据，不能替代现场标定。")
    paragraph(doc, "总体流程为：读取图像并保留原始数据；计算二维灰度梯度；生成分位数边缘掩膜；输出像素覆盖率和连通域统计；再分别进入正弦拟合、采样敏感性和跨孔评分模块。所有随机性均未引入，脚本和输出 CSV 保存在 reports/2025-C 下。")

    doc.add_heading("4 问题一 裂隙像素识别", level=1)
    paragraph(doc, "设灰度图像为 I(x,y)，先用 CLAHE 增强局部对比度，再用双边滤波抑制纹理噪声。对平滑图像使用 Canny 算子得到边缘候选，并用 3×3 形态学闭运算连接断裂边缘、开运算去除孤立噪声，得到二值掩膜 M(x,y)。该策略不需要标签，适合验证数据链路，但仍会保留部分岩石纹理和钻进痕迹。")
    paragraph(doc, f"10 张图像的平均边缘覆盖率为 {q1_coverage:.2%}，范围为 18.84%—48.40%，下采样后连通域均值为 {q1_components:.1f}。覆盖率受 Canny 阈值、纹理强度和形态学操作影响，不能解释为真实裂隙面积比例；因此该结果只用于检查输入、输出尺寸和后续流程。")
    add_figure(doc, "q1_mask_preview.png", "图 4-1 附件 1 图 1-1 基线掩膜的三段预览")
    add_figure(doc, "q1_edge_coverage.png", "图 4-2 十张附件 1 图像的边缘覆盖率")
    paragraph(doc, "改进方向是使用带标注的 U-Net 或轻量 U-Net，并按钻孔或原图分组划分训练集和验证集；同时使用 Dice/Focal 类损失处理裂隙像素稀疏问题。当前数据未提供可直接读取的像素标签，因此本文不计算 Accuracy、IoU 或 F1，以免制造虚假精度。")

    doc.add_heading("5 问题二 正弦状裂隙参数初估", level=1)
    q2_explanation = paragraph(doc, "题目给出的正弦模型为 y = R sin(2πx/P + β) + C。增强基线先对图像进行高斯平滑和 Canny 边缘检测，再将每一列边缘像素的中位纵坐标作为观测点，并将周期 P 固定为图像宽度 244 像素。利用 sin(a+b) 展开后，模型可以写成 y = a sin(2πx/P) + b cos(2πx/P) + C，再使用最小二乘求解 a、b、C，最后得到 R = sqrt(a²+b²) 和 β = atan2(b,a)。")
    add_omml_formula_after(q2_explanation, "y = R sin(2πx/P + β) + C")
    paragraph(doc, f"10 张图像的 R² 范围为 {min(q2_r2):.4f}—{max(q2_r2):.4f}，最大值仍低于 0.20。说明“每列最暗像素 + 单一正弦”不能有效分离多条裂隙、纹理和泥浆干扰。该负结果具有诊断价值：后续应先做语义分割和连通域/DBSCAN 聚类，再对每条裂隙使用 RANSAC 或鲁棒非线性拟合。")
    add_figure(doc, "q2_r2.png", "图 5-1 十张附件 2 图像的正弦基线拟合 R²")
    add_table(doc, ["图像", "R 像素", "P 像素", "β rad", "C 像素", "R²"], [[r["image"], r["R_pixel"], r["P_pixel"], r["beta_rad"], r["C_pixel"], r["R2"]] for r in q2[:5]])

    doc.add_heading("6 问题三 复杂裂隙粗糙度与采样敏感性", level=1)
    q3_explanation = paragraph(doc, "对附件 3 图 3-1，基线在每个横坐标采样点上选取梯度最大的纵坐标，随后将像素坐标换算到题面给定的 94.25 mm 周长和 500 mm 深度范围。根据相邻离散点斜率计算 Z₂，再使用题给经验式 JRC = 51.85 Z₂^0.6 − 10.37。")
    add_omml_formula_after(q3_explanation, "JRC = 51.85 Z₂^0.6 − 10.37")
    paragraph(doc, f"当采样点数从 32 增至 256 时，JRC 从 {q3_values[0]:.2f} 增至 {q3_values[-1]:.2f}。结果随采样密度大幅上升，说明梯度峰值中包含大量纹理和噪声，且简单等间距采样会放大局部尖峰。该结果不能作为工程 JRC 定值，只能作为采样敏感性诊断。")
    add_figure(doc, "q3_jrc_sensitivity.png", "图 6-1 JRC 基线结果对采样点数的敏感性")
    add_table(doc, ["采样点数", "Z₂", "JRC"], [[r["sample_count"], r["Z2"], r["JRC"]] for r in q3])
    paragraph(doc, "后续应先提取连续裂隙轮廓，再比较等间距、曲率加权和自适应拐点采样；还应对图像分辨率、轮廓平滑和裂隙面积做联合敏感性分析。")

    doc.add_heading("7 问题四 多钻孔连通性基线", level=1)
    paragraph(doc, "附件 4 包含 6 个钻孔和 40 个分段图像。基线先计算每个分段的 90% 梯度边缘密度，再对相邻钻孔的同深度段构造差异 d。连通评分定义为 p = exp(−80d)，用于排序而非概率校准。该评分只利用图像统计相似性，没有使用裂隙方向、JRC 和三维几何匹配，因此属于弱基线。")
    paragraph(doc, f"在当前启发式评分中，候选连通评分范围为 {min(q4_values):.4f}—{max(q4_values):.4f}。按最接近 0.5 的不确定性排序，优先补孔候选为：{', '.join(f'{r["between_holes"]} 段 {r["segment_start_m"]}m' for r in candidates)}。这些位置只是基于边缘密度差异的基线建议，正式结论需要加入裂隙几何、方向和现场空间约束。")
    add_figure(doc, "q4_connectivity_network.png", "图 7-1 六孔分段连通性基线的三维投影示意")
    add_table(doc, ["候选孔间位置", "分段起点 m", "不确定性评分"], [[r["between_holes"], r["segment_start_m"], r["uncertainty_score"]] for r in candidates])

    doc.add_heading("8 模型评价与改进方向", level=1)
    paragraph(doc, "优点方面，本文增强基线主动使用 OpenCV、NumPy 和 Pillow，能够在不依赖深度学习框架的情况下完成数据读取、四问串联、结果表生成和图表输出；每个结果都由脚本生成，便于复现。问题一验证了二值输出尺寸和边缘覆盖统计，问题二和问题三的低质量/高敏感性结果及时暴露了简单模型的不足，避免把错误结果包装成最终结论。")
    paragraph(doc, "局限方面，梯度阈值没有语义标签，正弦拟合没有逐裂隙聚类，JRC 轮廓没有经过工程校准，连通评分也没有真实连通标注。因此本文不能替代竞赛最终方案，也不能直接作为工程安全决策依据。")
    paragraph(doc, "改进方面，问题一应使用 U-Net 类分割并以人工标注做 IoU/F1 验证；问题二应加入 DBSCAN/连通域分离、FFT 初值和 RANSAC 鲁棒拟合；问题三应做轮廓平滑、曲率加权采样和面积分层；问题四应建立裂隙几何匹配、JRC 修正和不确定性驱动的图模型，并通过多次扰动验证补孔位置稳定性。")

    doc.add_heading("9 结论", level=1)
    paragraph(doc, "本文完成了 2025 年研赛 C 题从原始图像到 Word 论文的第一版可复现实验链路。基线结果表明，梯度边缘可以快速建立输入输出和图表流程，但单一图像统计不足以完成高可信裂隙识别；正弦拟合的低 R² 和 JRC 对采样密度的强敏感性，明确指出了需要引入分割、聚类、鲁棒拟合和轮廓校准的位置。下一阶段应围绕问题一的标注/分割质量和问题二的逐裂隙拟合展开，而不是继续堆叠未经验证的复杂模型。")

    doc.add_heading("参考文献", level=1)
    paragraph(doc, "[1] 康红普，姜鹏飞，王子越，等. 煤巷钻锚一体化快速掘进技术与装备及应用[J]. 煤炭学报，2024，49(1):131-151.")
    paragraph(doc, "[2] 袁亮，张平松. 煤矿透明地质模型动态重构的关键技术与路径思考[J]. 煤炭学报，2023，48(1):1-14.")
    paragraph(doc, "[3] 2025 年中国研究生数学建模竞赛 C 题题面及附件说明，竞赛资料目录提供的原始文件。")

    doc.add_heading("附录 代码与复现命令", level=1)
    paragraph(doc, "核心脚本：reports/2025-C/code/run_baseline.py；图表脚本：reports/2025-C/code/make_report_figures.py。运行前将 C 题数据包解压到临时目录，并在 run_baseline.py 中更新 ROOT。")
    paragraph(doc, "运行命令：python reports/2025-C/code/run_baseline.py；python reports/2025-C/code/make_report_figures.py。结果 CSV 位于 reports/2025-C/results，图表位于 reports/2025-C/figures/result。")
    paragraph(doc, "本论文对应的输入哈希、Python 环境、随机种子和运行命令已记录在 reports/2025-C/results/复现清单.json；当前文档是基线实验稿，提交前必须按当届官方模板、附件命名和 AI 使用规范复核。")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
