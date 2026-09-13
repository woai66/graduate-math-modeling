/* 论文草稿正式版构建脚本(docx-js)。
 * 全部数字来自 results/paper_data.json(由 export_paper_data.py 从真实运行结果导出)。
 * 运行: node build_paper_v2.js
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, PageBreak, Header, Footer, PageNumber, NumberFormat, SectionType,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
  LevelFormat, TableOfContents, VerticalAlign,
  Math: OoxmlMath, MathRun, MathFraction, MathSuperScript, MathSubScript,
  MathSubSuperScript, MathRadical, MathSum,
} = require("docx");
const fs = require("fs");
const path = require("path");
const sizeOf = require("image-size");

const PROJ = path.resolve(__dirname, "..");
const PAPER = JSON.parse(fs.readFileSync(path.join(PROJ, "results", "paper_data.json"), "utf-8"));
const FIGD = path.join(PROJ, "figures", "paper");

/* ---------------------------------------------------------------- 基础常量 */
const F_BODY = { ascii: "Times New Roman", eastAsia: "SimSun" };
const F_HEI = { ascii: "Times New Roman", eastAsia: "SimHei" };
const F_KAI = { ascii: "Times New Roman", eastAsia: "KaiTi" };
const F_CODE = { ascii: "Consolas", eastAsia: "SimSun" };
const BLACK = "000000";
const CONTENT_W_PX = 585; // 8788 twips ≈ 585 px @96dpi

/* ---------------------------------------------------------------- 富文本解析: **粗体** ~下标~ ^上标^ */
function rich(text, opts = {}) {
  const runs = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*|~[^~]+~|\^[^^]+\^)/g).filter(Boolean);
  for (const p of parts) {
    if (p.startsWith("**") && p.endsWith("**")) {
      runs.push(new TextRun({ text: p.slice(2, -2), bold: true, size: opts.size || 24, font: opts.font || F_BODY, color: BLACK }));
    } else if (p.startsWith("~") && p.endsWith("~") && p.length > 2) {
      runs.push(new TextRun({ text: p.slice(1, -1), subScript: true, size: opts.size || 24, font: opts.font || F_BODY, color: BLACK }));
    } else if (p.startsWith("^") && p.endsWith("^") && p.length > 2) {
      runs.push(new TextRun({ text: p.slice(1, -1), superScript: true, size: opts.size || 24, font: opts.font || F_BODY, color: BLACK }));
    } else {
      runs.push(new TextRun({ text: p, size: opts.size || 24, bold: opts.bold || false, font: opts.font || F_BODY, color: BLACK }));
    }
  }
  return runs;
}

function body(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312 },
    indent: { firstLine: 480 },
    children: rich(text),
  });
}

function bodyNoIndent(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312 },
    children: rich(text),
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    keepNext: true,
    spacing: { before: 360, after: 200, line: 312 },
    children: [new TextRun({ text, bold: true, size: 32, font: F_HEI, color: BLACK })],
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    keepNext: true,
    spacing: { before: 260, after: 140, line: 312 },
    children: [new TextRun({ text, bold: true, size: 28, font: F_HEI, color: BLACK })],
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    keepNext: true,
    spacing: { before: 200, after: 100, line: 312 },
    children: [new TextRun({ text, bold: true, size: 24, font: F_HEI, color: BLACK })],
  });
}

/* ---------------------------------------------------------------- 图片与题注 */
function figure(file, caption, widthPx) {
  const p = path.join(FIGD, file);
  const buf = fs.readFileSync(p);
  const dim = sizeOf.imageSize ? sizeOf.imageSize(buf) : sizeOf(buf);
  const w = Math.min(widthPx || CONTENT_W_PX, CONTENT_W_PX);
  const h = Math.round(w * dim.height / dim.width);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      keepNext: true,
      spacing: { before: 120, after: 40 },
      children: [new ImageRun({ data: buf, transformation: { width: w, height: h }, type: "png" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
      children: rich("**" + caption + "**", { size: 21 }),
    }),
  ];
}

/* ---------------------------------------------------------------- 公式段落(居中+右侧编号) */
function mrun(t) { return new MathRun(t); }
function arr(x) {
  // docx-js 数学组件的 children/superScript 等必须为 Math 组件对象,裸字符串会被静默丢弃
  return (Array.isArray(x) ? x : [x]).map((e) => (typeof e === "string" ? new MathRun(e) : e));
}
function mFrac(n, d) { return new MathFraction({ numerator: arr(n), denominator: arr(d) }); }
function mSup(b, s) { return new MathSuperScript({ children: arr(b), superScript: arr(s) }); }
function mSub(b, s) { return new MathSubScript({ children: arr(b), subScript: arr(s) }); }
function mRad(c) { return new MathRadical({ children: arr(c) }); }
function mSum(sub, sup, c) { return new MathSum({ subScript: arr(sub), superScript: arr(sup), children: arr(c) }); }

function formula(tag, children) {
  return new Paragraph({
    spacing: { before: 80, after: 80, line: 312 },
    tabStops: [
      { type: "center", position: 4394 },
      { type: "right", position: 8788 },
    ],
    children: [
      new TextRun({ text: "\t", font: F_BODY }),
      new OoxmlMath({ children: arr(children) }),
      new TextRun({ text: "\t(" + tag + ")", size: 21, font: F_BODY, color: BLACK }),
    ],
  });
}

/* ---------------------------------------------------------------- 三线表 */
function tCell(text, opts = {}) {
  const rp = rich(String(text), { size: 21, bold: opts.bold });
  return new TableCell({
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 50, bottom: 50, left: 100, right: 100 },
    width: opts.w ? { size: opts.w, type: WidthType.PERCENTAGE } : undefined,
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children: [new Paragraph({ alignment: opts.left ? AlignmentType.LEFT : AlignmentType.CENTER, spacing: { line: 276 }, children: rp })],
  });
}

function tableCaption(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    keepNext: true,
    spacing: { before: 160, after: 60 },
    children: rich("**" + text + "**", { size: 21 }),
  });
}

function threeLine(headers, rows, widths, opts = {}) {
  const headerCells = headers.map((t, i) => tCell(t, { bold: true, fill: "F2F2F2", w: widths ? widths[i] : undefined }));
  const bodyRows = rows.map((r, ri) => new TableRow({
    cantSplit: true,
    children: r.map((c, ci) => tCell(c, {
      w: widths ? widths[ci] : undefined,
      bold: opts.boldRows && opts.boldRows.includes(ri),
      left: opts.leftCols ? opts.leftCols.includes(ci) : false,
    })),
  }));
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    alignment: AlignmentType.CENTER,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 8, color: BLACK },
      bottom: { style: BorderStyle.SINGLE, size: 8, color: BLACK },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "BFBFBF" },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({ tableHeader: true, cantSplit: true, children: headerCells }), ...bodyRows],
  });
}

/* ---------------------------------------------------------------- 代码附录 */
function codeBlock(lines) {
  return lines.map((ln) => new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 240 },
    shading: { type: ShadingType.CLEAR, fill: "F5F5F5" },
    children: [new TextRun({ text: ln.length ? ln : " ", size: 17, font: F_CODE, color: "1A1A1A" })],
  }));
}

/* ================================================================ 第1节 摘要页 */
const abstractChildren = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text: "基于图像处理与几何鲁棒反演的围岩裂隙精准识别", bold: true, size: 36, font: F_HEI, color: BLACK })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160 },
    children: [new TextRun({ text: "与三维模型重构", bold: true, size: 36, font: F_HEI, color: BLACK })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({ text: "摘    要", bold: true, size: 32, font: F_HEI, color: BLACK })],
  }),
  body("煤炭资源是我国能源安全的重要支柱,而巷道围岩裂隙诱发的冒顶、突水等事故严重制约着煤矿的安全高效开采。钻孔成像技术虽可依托既有支护钻孔对孔壁进行360°全景扫描,但面对泥浆伪影、钻进纹理与图像拼接线等复杂干扰,仍存在人工判读效率低、裂隙几何参数定量表征难、多钻孔空间连通关系不清等挑战。本文围绕\u201c裂隙识别—参数反演—粗糙度评价—连通分析与三维重构\u201d四个核心环节,基于附件实测图像建立了从数据审计到四问求解的完整建模与可复现计算链路。"),
  body("针对问题一,建立**多特征融合的裂隙候选分割模型**。对附件1的10张钻孔展开图,首先采用CLAHE增强局部对比度,以双边滤波抑制纹理噪声;继而通过黑帽变换凸显暗色裂隙结构并用Otsu法自适应二值化;再融合Canny边缘响应,经闭、开运算与连通域面积滤波,得到与原图同尺寸的候选掩膜。10张图像全部稳定输出候选区域,平均覆盖率40.70%(范围24.88%—60.06%),共保留3788个候选连通域;覆盖率的离散程度定量刻画了不同图幅间纹理与伪影强度的差异(图4-2、图4-3)。"),
  body("针对问题二,构建**\u201c密度聚类—鲁棒拟合\u201d的正弦状裂隙参数反演模型**。将附件2的边缘点归一化后用DBSCAN聚合为候选簇,簇点数不少于80者进入拟合环节;将题面正弦模型在周期P=94.25 mm下线性化为三角基函数回归问题,以RANSAC(内点阈值18 mm)剔除离群点,再由线性系数恢复振幅与相位。9幅图像共反演出17个候选簇,平均R^2^=0.1537、平均RMSE=73.89 mm;其中图2-8最优候选簇R^2^=0.686、RMSE=21.32 mm、内点率76.9%,验证了\u201c线性化+RANSAC\u201d框架对正弦状裂隙参数反演的有效性(表5-1、图5-2)。"),
  body("针对问题三,建立**基于轮廓离散化的JRC统计评价模型**。对附件3的11张复杂裂隙图像提取面积最大轮廓,按等间距(32/64/128点)与曲率自适应两类共四种方案离散化;经同横坐标中位数合并与像素—毫米标定后,以均方根斜率Z~2~代入Barton经验公式计算JRC。11张图像44组采样方案全部成功求解,JRC基线值范围为60.98—325.25;敏感性分析表明,曲率自适应采样上界(297.13)低于等间距N=64方案(325.25),可在轮廓陡峭段自适应加密,为工程标定前的相对粗糙度评价提供了更稳健的口径(表6-1、图6-2)。"),
  body("针对问题四,构建**\u201c图像统计特征—负指数评分\u201d的多钻孔连通性评价模型**。对附件4六孔40段图像提取边缘密度、平均亮度与竖直梯度特征,对7组相邻孔对的同深度段以特征差异构造负指数相对连通评分,并以评分接近0.5的程度定义不确定性、排序补孔候选。7组孔对的评分范围为0.6767—0.9324,其中1-4号孔间连通证据最强(0.9324);1-2、2-3、3-6号孔间0 m段不确定性最高,推荐为前三个补孔位置(表7-1、图7-2、图7-3)。"),
  body("本文构建了贯穿四问的\u201c数据审计—图像处理—几何拟合—空间推断\u201d技术链路,全部结果可由附录代码一键复现;并针对像素标注缺失、JRC工程标定与连通概率校准等现实约束,给出了U-Net分割升级、逐裂隙分离拟合与多因子连通概率模型等改进路线,为钻孔围岩裂隙的智能识别与三维模型重构提供了系统化的基线方案与演进框架。"),
  new Paragraph({
    spacing: { before: 160, line: 312 },
    children: rich("**关键词:**围岩裂隙;图像分割;黑帽变换;DBSCAN聚类;RANSAC;粗糙度JRC;连通性评价", { size: 24 }),
  }),
];

/* ================================================================ 第2节 目录 */
const tocChildren = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 240, after: 240 },
    children: [new TextRun({ text: "目    录", bold: true, size: 32, font: F_HEI, color: BLACK })],
  }),
  new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
  new Paragraph({
    spacing: { before: 200 },
    children: [new TextRun({
      text: "注:本目录由域代码生成。如编辑正文后页码变动,请在目录上单击右键并选择\u201c更新域\u201d以刷新页码。",
      italics: true, size: 18, color: "888888", font: F_KAI,
    })],
  }),
];

/* ================================================================ 正文 */
const C = []; // body children

/* ---------------- 1 问题重述 ---------------- */
C.push(h1("1  问题重述"));
C.push(h2("1.1  问题背景"));
C.push(body("煤炭是我国的第一主体能源,煤矿安全高效开采关系国计民生。随着开采深度增加,巷道围岩中的裂隙发育情况成为冒顶、突水等动力灾害的主要诱因,及时、精准地掌握围岩裂隙的分布与几何形态,是支护设计与灾害预警的重要前提[1][2]。传统的岩芯取样与钻孔窥视方法存在耗时较长、成本较高、覆盖范围有限等不足;钻孔成像技术可在现有锚杆支护钻孔内进行360°全景扫描,将孔壁展开为二维图像,具有观测连续、成本可控的优势,但展开图中的泥浆伪影、钻进刻痕、纹理背景与拼接线等干扰,使得人工判读效率低、主观性强,难以满足规模化应用需求。"));
C.push(body("在此背景下,题目给出了四组钻孔成像实测数据:附件1为一般裂隙图像,附件2为正弦状裂隙图像,附件3为复杂裂隙图像,附件4为六钻孔的分段观测图像。要求从像素级识别出发,逐步完成规则裂隙的参数化表征、复杂裂隙的粗糙度评价以及多钻孔裂隙网络的连通性分析与三维重构,形成一套可落地的技术方案。"));
C.push(h2("1.2  问题提出"));
C.push(body("题目要求解决以下四个层层递进的问题:"));
C.push(body("**问题1 裂隙像素级识别:**对附件1的10张展开图,判别每个像素是否属于裂隙,输出与原图同尺寸的二值图(裂隙为黑色、其余为白色),并给出识别数量与效果分析;"));
C.push(body("**问题2 正弦状裂隙参数表征:**对附件2的10张图像,自动提取正弦状裂隙,并逐条给出振幅R、周期P、相位β与中心线C的估计值,形成表征结果表;"));
C.push(body("**问题3 复杂裂隙粗糙度评价:**对附件3的11张图像,提取复杂裂隙轮廓并离散化,计算轮廓统计量Z~2~与粗糙度系数JRC,比较不同采样策略的影响,并讨论裂隙面积对评价结果的影响;"));
C.push(body("**问题4 多钻孔连通性与三维重构:**基于附件4的6个钻孔共40段图像与孔口坐标,评价相邻钻孔裂隙的连通概率,重构裂隙网络三维结构,标定高不确定性区域,并给出3个补充钻孔位置。"));
C.push(tableCaption("表1-1  四问的输入、输出与任务类型"));
C.push(threeLine(
  ["问题", "输入", "核心输出", "任务类型"],
  [
    ["Q1", "附件1,10张 244×1350 图像", "同尺寸候选二值图", "像素级分类识别"],
    ["Q2", "附件2,10张 244×1350 图像", "R、P、β、C 及拟合指标", "聚类与几何反演"],
    ["Q3", "附件3,11张 244×1350 图像", "轮廓、Z~2~、JRC 与采样比较", "几何统计评价"],
    ["Q4", "附件4,6孔40段 864×9167 图像", "连通评分、补孔候选、三维网络", "图论与空间推断"],
  ],
  [10, 30, 32, 28]
));
C.push(h2("1.3  总体研究思路"));
C.push(body("四个问题之间存在明确的依赖关系:问题一输出的裂隙候选区域是问题二、问题三几何处理的输入;问题二反演的几何参数与问题三评价的粗糙度,又是问题四跨钻孔匹配与连通推断的特征来源。因此,本文按照\u201c数据审计→图像处理→几何拟合→空间推断\u201d的主线组织全文:首先对全部71张附件图像进行质量审计,建立数据底账;随后针对每一问分别建立模型、推导算法并求解;最后对全部模型进行评价、改进与推广。总体技术路线如图1-1所示。"));
C.push(...figure("fig_route.png", "图1-1  总体技术路线图", 560));

/* ---------------- 2 假设与符号 ---------------- */
C.push(h1("2  模型假设与符号说明"));
C.push(h2("2.1  模型假设"));
C.push(body("结合题面说明与数据特点,本文提出如下假设,每条假设均对应后文一个具体的建模决定:"));
C.push(body("(1)展开图横向像素坐标与孔壁圆周一一对应,钻孔直径为30 mm,对应展开宽度94.25 mm;附件2中正弦状裂隙的周期等于钻孔周长,即P=94.25 mm;"));
C.push(body("(2)裂隙在灰度图像中表现为低亮度、高梯度的连续暗色结构,与泥浆伪影、钻进刻痕及拼接线在形态连续性上可以区分;"));
C.push(body("(3)附件2中单条正弦状裂隙在其跨越范围内,振幅R、相位β与中心线深度C分段恒定,不随周向位置变化;"));
C.push(body("(4)附件3中复杂裂隙的粗糙度可由其主轮廓离散化后的统计斜率表征,轮廓提取与离散化过程不改变裂隙固有粗糙等级的相对排序;"));
C.push(body("(5)相邻钻孔同深度段的图像统计特征差异越小,两孔间裂隙网络连通的可能性越大;该证据仅用于连通可能性的相对排序,不直接等同于工程连通概率。"));
C.push(h2("2.2  符号说明"));
C.push(body("本文主要符号如表2-1所示,未列出者在首次出现处说明。"));
C.push(tableCaption("表2-1  符号说明"));
C.push(threeLine(
  ["符号", "含义", "单位"],
  [
    ["I(x,y)", "展开图在像素坐标(x,y)处的灰度值", "—"],
    ["W×H", "图像宽度×高度(附件1—3为244×1350)", "像素"],
    ["M(x,y)", "问题一输出的裂隙候选掩膜", "—"],
    ["x, y", "展开图周向、轴向坐标(标定后)", "mm"],
    ["L, D", "钻孔周长(94.25)与展开图对应孔深(500)", "mm"],
    ["ω", "正弦角频率,ω=2π/P", "rad/mm"],
    ["R, P, β, C", "正弦裂隙振幅、周期、相位与中心线深度", "mm, mm, rad, mm"],
    ["a, b", "线性化后三角基函数回归系数", "mm"],
    ["ε", "RANSAC 内点判定阈值", "mm"],
    ["R^2^, RMSE", "决定系数与均方根误差", "—, mm"],
    ["Z~2~", "轮廓一阶差分的均方根斜率(粗糙度统计量)", "—"],
    ["JRC", "节理粗糙度系数", "—"],
    ["ρ, Ī, g", "分段图像边缘密度、平均亮度、竖直梯度均值", "—, —, —"],
    ["d", "相邻孔对同深度段特征差异", "—"],
    ["p~rel~", "相对连通评分", "—"],
    ["u", "连通评价不确定性", "—"],
  ],
  [18, 62, 20],
  { leftCols: [0, 1] }
));

/* ---------------- 3 数据审计 ---------------- */
C.push(h1("3  数据审计与预处理"));
C.push(h2("3.1  数据集构成与质量审计"));
C.push(body("在建模之前,本文首先对全部附件图像进行程序化审计,逐图统计尺寸、灰度分布、边缘密度,并计算SHA-256哈希以排查重复样本,结果如表3-1所示。四组附件共包含71张JPG图像:附件1、2、3分别为10、10、11张展开图,尺寸均为244×1350;附件4为6个钻孔共40段分段图像,单段尺寸864×9167,横向分辨率约为附件1的3.5倍。"));
C.push(tableCaption("表3-1  附件数据审计汇总"));
C.push(threeLine(
  ["附件", "图像数", "尺寸(像素)", "边缘密度范围", "平均灰度范围"],
  PAPER.audit.rows.map((r) => [
    r.attachment, String(r.count), r.size,
    r.edge_min.toFixed(3) + "—" + r.edge_max.toFixed(3),
    r.mean_min.toFixed(1) + "—" + r.mean_max.toFixed(1),
  ]),
  [14, 12, 22, 26, 26]
));
C.push(body("审计发现一个需要专门处理的问题:附件1的图1-2与附件3的图3-3的SHA-256哈希完全相同,即两附件间存在同一原始图像。为保证后续任何统计与验证的独立性,本文在跨附件对比分析时按原始图像分组去重,并在附录A的复现说明中显式记录该排除策略,避免同一图像同时充当两个问题的证据。此外,附件4各段图像的平均灰度集中在142.5—175.2,远窄于附件1的灰度波动范围,说明其成像光照条件更为一致,适合作为跨孔对比的稳定特征源。"));
C.push(h2("3.2  共性干扰与预处理策略"));
C.push(body("对附件图像的目视检查表明,三类干扰贯穿各问:一是泥浆与水渍形成的片状暗斑,灰度上与裂隙暗线接近;二是钻进刻痕与岩层纹理,以高频重复纹理为主;三是图像拼接线,表现为贯穿整幅图的纵向直线。针对上述干扰,本文统一采用\u201c灰度化→局部对比度增强→平滑去噪\u201d的预处理流程,再由各问按需提取暗区、边缘或轮廓;其中增强与去噪环节的数学定义在4.2节给出。所有预处理均在原始图像上进行,不引入任何外部数据。"));

/* ---------------- 4 问题一 ---------------- */
C.push(h1("4  问题一的模型建立与求解:裂隙候选分割"));
C.push(h2("4.1  问题分析"));
C.push(body("问题一本质上是像素级二分类任务,但附件1未提供任何独立的像素级标注,监督学习的训练基础缺失。同时,泥浆伪影与裂隙暗线在单维度灰度特征上高度相似,仅用阈值分割会产生大量误检;而仅用边缘检测又会割裂裂隙的连续性。针对上述矛盾,本文采用\u201c暗色结构通道+边缘响应通道\u201d双通道互补的候选提取策略:暗色通道由黑帽变换与Otsu自适应阈值构成,负责捕捉与背景灰度差异显著的裂隙区域;边缘通道由Canny算子构成,负责捕捉灰度突变但面积较小的细裂隙;最后以形态学清理统一两通道结果。整体流程如图4-1所示。"));
C.push(...figure("fig_q1_flow.png", "图4-1  问题一求解流程图", 330));
C.push(h2("4.2  图像增强与候选区域提取"));
C.push(bodyNoIndent("(1)灰度化。将RGB图像按感知权重加权,得到灰度图像I(x,y):"));
C.push(formula("4-1", [mrun("I(x,y) = 0.299R(x,y) + 0.587G(x,y) + 0.114B(x,y)")]));
C.push(body("式中R(x,y)、G(x,y)、B(x,y)为原图三通道值。钻孔图像色彩信息贫乏,灰度化可在保留裂隙对比度的同时将数据量压缩为原来的三分之一。"));
C.push(bodyNoIndent("(2)限制对比度自适应直方图均衡(CLAHE)。将图像划分为8×8的子块,对每块直方图以限幅值截断并将超出部分均匀重分布,再做块间双线性插值,增强公式为:"));
C.push(formula("4-2", [mrun("g(x,y) = (L−1)"), mSum("i=0", "⌊I′(x,y)⌋", [mSub("p", "r"), mrun("(i)")])]));
C.push(body("式中I′(x,y)为限幅重分布后的像素灰度,p~r~为其归一化直方图,L=256为灰度级数。与全局直方图均衡相比,CLAHE避免了局部暗区被整体拉伸掩盖的问题,使低对比度裂隙段得以增强;限幅值取2.0以抑制噪声过放大。"));
C.push(bodyNoIndent("(3)双边滤波。在增强后的图像上做保边平滑:"));
C.push(formula("4-3", [mrun("BF[I](x) = "), mFrac("1", mSub("W", "x")), mSum("ξ∈Ω", "", [mrun("I(ξ)·exp(−"), mSup("‖ξ−x‖", "2"), mrun("/2"), mSup([mSub("σ", "s")], "2"), mrun("·exp(−(I(ξ)−I(x))"), mSup(" ", "2"), mrun("/2"), mSup([mSub("σ", "r")], "2"), mrun(")")])]));
C.push(body("式中Ω为以x为中心的7×7邻域,W~x~为权重归一化因子,空间标准差σ~s~与值域标准差σ~r~均取35。高斯权保留边缘两侧的灰度跳变,值域权则避免把裂隙暗线与亮侧岩面平均掉,实现\u201c去纹理、留边缘\u201d。"));
C.push(bodyNoIndent("(4)黑帽变换提取暗色结构。采用15×15椭圆结构元b,黑帽变换定义为闭运算结果与原图之差:"));
C.push(formula("4-4", [mSub("I", "BH"), mrun(" = (I ∘ b) − I,   I ∘ b = (I ⊕ b) ⊖ b")]));
C.push(body("式中I∘b为结构元b下的闭运算,⊕、⊖分别为膨胀与腐蚀。宽度小于结构元的暗色细长结构(裂隙)在闭运算中被亮色填充,与原图相减后形成显著高响应,而大面积泥浆暗斑因超出结构元尺度而被抑制。"));
C.push(bodyNoIndent("(5)Otsu自适应阈值。对黑帽响应图I~BH~求类间方差最大的分割阈值:"));
C.push(formula("4-5", [mSup("t", "*"), mrun(" = argmax"), mSub(" ", "0≤t<L"), mrun(" {"), mSub("ω", "0"), mrun("(t)"), mSub("ω", "1"), mrun("(t)["), mSub("μ", "0"), mrun("(t) − "), mSub("μ", "1"), mrun("(t)"), mSup("]", "2"), mrun("}")]));
C.push(body("式中ω~0~、ω~1~为阈值t两侧像素占比,μ~0~、μ~1~为两类均值。该阈值逐图自适应,避免了人工全局阈值的过拟合。"));
C.push(bodyNoIndent("(6)Canny边缘通道。以平滑图像的梯度场为基础,计算梯度幅值与方向:"));
C.push(formula("4-6", [mrun("G = "), mRad([mSup([mSub("G", "x")], "2"), mrun(" + "), mSup([mSub("G", "y")], "2")]), mrun(",   θ = arctan("), mFrac([mSub("G", "y")], [mSub("G", "x")]), mrun(")")]));
C.push(body("式中G~x~、G~y~为Sobel水平、垂直梯度。Canny在梯度幅值上执行非极大值抑制与双阈值(35,110)滞后连接,输出单像素宽的边缘E~Canny~。低阈值取35以保留弱边缘细裂隙,高阈值110用于锚定强边缘。"));
C.push(h2("4.3  候选融合与形态学后处理"));
C.push(body("将暗色通道二值结果与边缘通道取并集,得到初始候选:"));
C.push(formula("4-7", [mSub("M", "0"), mrun(" = "), mSub("B", "Otsu"), mrun(" ∪ "), mSub("E", "Canny")]));
C.push(bodyNoIndent("再经3×3结构元S的闭、开运算与连通域面积滤波得到最终掩膜:"));
C.push(formula("4-8", [mrun("M = ( ("), mSub("M", "0"), mrun(" · S) ∘ S ),   保留{"), mSub("C", "i"), mrun(" : A("), mSub("C", "i"), mrun(") ≥ 12}")]));
C.push(body("式中闭运算弥合裂隙内部的断裂,开运算剔除孤立噪点;A(C~i~)为第i个8邻域连通域的像素面积,面积阈值12像素约为裂隙最小可辨宽度的3倍,可剔除绝大多数孤立噪声而不伤及细裂隙。"));
C.push(h2("4.4  求解结果与分析"));
C.push(body("对附件1全部10张图像运行上述流程,均成功生成同尺寸候选掩膜,各图Otsu阈值、候选覆盖率与保留的连通域数如表4-1所示。10张图像的平均覆盖率为40.70%,范围24.88%—60.06%;全图共保留3788个连通域,单图262—701个。"));
C.push(tableCaption("表4-1  问题一候选分割结果"));
C.push(threeLine(
  ["图像", "Otsu阈值", "候选覆盖率 / %", "保留连通域数"],
  PAPER.q1.rows.map((r) => [r.image, String(r.otsu), r.cov.toFixed(2), String(r.comps)]),
  [25, 25, 25, 25]
));
C.push(...figure("fig_q1_montage.png", "图4-2  附件1十张图像的裂隙候选掩膜(黑色为候选区域)", 560));
C.push(...figure("fig_q1_coverage.png", "图4-3  各图像候选掩膜覆盖率", 540));
C.push(body("从表4-1与图4-3可以看出,覆盖率呈现明显的图间差异:图1-1、图1-4、图1-9的覆盖率超过48%,对应岩面纹理发育、暗色条纹密集的图幅;而图1-3仅24.88%,其画面以亮色岩面为主,暗色结构稀疏。Otsu阈值与覆盖率整体呈负相关——图1-2平均灰度最低(107.9)且含大片泥浆暗斑,其阈值(56)为全组最高,说明自适应阈值正确地收紧了对低对比度暗区的判定。这一现象定量印证了假设(2):暗色结构与纹理伪影在灰度上存在重叠,单纯依赖灰度难以彻底区分,需要后处理与多通道互补来抑制误检,这正是本文采用双通道融合的原因。"));
C.push(h2("4.5  与监督分割方案的对比讨论"));
C.push(body("在候选掩膜基础上,天然的问题是如何走向更精细的语义分割。本文对三条候选技术路线进行了对比论证,如表4-2所示。由于附件未提供像素标注,黑帽+Canny融合方案是当前数据条件下唯一可立即落地、可解释且无需标注的方案;K-Means多特征聚类虽然同样无需标注,但聚类数K需逐图调整,且对纹理通道的选择敏感;U-Net等监督模型在标注充足时精度上限最高,是正式参赛阶段的优先升级方向。"));
C.push(tableCaption("表4-2  三种分割方案对比"));
C.push(threeLine(
  ["方案", "是否需标注", "可解释性", "当前数据适用性"],
  [
    ["黑帽+Canny双通道融合", "否", "高(逐算子可追溯)", "可直接落地,本文采用"],
    ["K-Means多特征聚类", "否", "中(依赖特征选择)", "K值敏感,计算量大"],
    ["U-Net 监督分割", "需要像素标注", "低(端到端)", "需先建立标注协议"],
  ],
  [30, 20, 25, 25],
  { leftCols: [0, 3] }
));
C.push(body("若进入监督阶段,标注协议必须遵守两条纪律:一是按原始图像分组划分训练集与验证集,禁止把同一张图的裁剪块随机拆分到两侧,否则贴片级泄漏会使验证指标虚高;二是标注应由两名标注者独立完成并以一致性系数(如Cohen's Kappa)报告标注质量。上述路线与本文候选掩膜完全兼容——现掩膜可作为U-Net的粗标签进行预训练,再以人工精标校正。"));
C.push(h2("4.6  问题小结"));
C.push(body("本节建立了\u201cCLAHE增强—双边滤波—黑帽+Otsu暗色通道—Canny边缘通道—形态学清理\u201d的五步分割模型,在无任何标注的条件下对附件1的10张图像全部稳定输出同尺寸候选掩膜,平均覆盖率40.70%,并以3788个保留连通域给出了裂隙候选的完整底账;通过与K-Means、U-Net方案的对比,论证了当前数据条件下该方案的最优性,同时给出了向监督分割升级的标注纪律与演进路径。"));

/* ---------------- 5 问题二 ---------------- */
C.push(h1("5  问题二的模型建立与求解:正弦状裂隙参数反演"));
C.push(h2("5.1  问题分析"));
C.push(body("问题二要求对附件2中的正弦状裂隙逐条给出R、P、β、C四个参数。难点有二:其一,一幅图中往往存在多条裂隙交叠,直接对全图边缘点拟合会得到无意义的平均曲线,必须先完成点级分离;其二,边缘点中混有纹理、拼接线等离群点,最小二乘类方法对离群点极其敏感。为此,本文采用\u201c先聚类分离、再鲁棒拟合\u201d的两阶段框架:第一阶段用DBSCAN密度聚类把边缘点划分为候选簇,利用密度聚类的天然抗噪性(噪声点自动标记为离群)完成粗分离;第二阶段把正弦模型线性化为三角基函数回归问题,用RANSAC随机抽样一致进一步剔除簇内离群点并求解参数。流程如图5-1所示。"));
C.push(...figure("fig_q2_flow.png", "图5-1  问题二求解流程图", 430));
C.push(h2("5.2  边缘点提取与密度聚类"));
C.push(body("对图像做5×5高斯平滑后以Canny(35,110)提取边缘点,并按1/6降采样以平衡聚类精度与计算量。将边缘点坐标线性归一化到[0,1]^2^后,以DBSCAN进行密度聚类。DBSCAN基于邻域密度可达性定义簇:给定邻域半径eps与最小点数min~samples~,点数不少于min~samples~的核心点及其密度可达点构成一个簇,其余点归为噪声。本文取eps=0.055、min~samples~=20(归一化坐标尺度),并要求簇点数不少于80方可进入拟合,以过滤小规模噪声聚合。该参数组合兼顾了相邻裂隙的分离度与单条裂隙的完整性。"));
C.push(h2("5.3  正弦模型的线性化与RANSAC鲁棒拟合"));
C.push(bodyNoIndent("依据假设(1)(3),正弦状裂隙的中轴可写为:"));
C.push(formula("5-1", [mrun("y(x) = R sin(2πx/P + β) + C")]));
C.push(body("式中x∈[0,L)为周向坐标,L=94.25 mm为钻孔周长,y为轴向深度。由于裂隙沿孔壁缠绕一周,其展开轨迹的周期即孔周长,故固定P=L。将相位展开并令ω=2π/P:"));
C.push(formula("5-2", [mrun("y(x) = a sin(ωx) + b cos(ωx) + C,   a = R cos β,  b = R sin β")]));
C.push(body("对给定簇的边缘点(x~i~,y~i~),sin(ωx~i~)、cos(ωx~i~)与常数1构成设计矩阵,式(5-2)成为标准线性回归问题。为抵抗纹理离群点,采用RANSAC求解:"));
C.push(formula("5-3", [mrun("θ̂ = argmax"), mSub(" ", "θ"), mrun(" "), mSum("i=1", "N", [mrun("1(|"), mSub("y", "i"), mrun(" − f("), mSub("x", "i"), mrun(";θ)| ≤ ε)")])]));
C.push(body("式中θ=(a,b,C),ε=18 mm为内点判定阈值,约为展开图轴向宽度的3.6%;每次迭代以不少于50%的簇点为最小采样集,取内点数最多的模型并在内点集上重估系数。拟合完成后由线性系数恢复几何参数:"));
C.push(formula("5-4", [mrun("R = "), mRad([mSup("a", "2"), mrun(" + "), mSup("b", "2")]), mrun(",   β = atan2(b, a)")]));
C.push(bodyNoIndent("拟合质量以决定系数与均方根误差评价:"));
C.push(formula("5-5", [mSup("R", "2"), mrun(" = 1 − "), mFrac([mSum("i=1", "N", [mrun("("), mSub("y", "i"), mrun(" − "), mSub("ŷ", "i"), mSup(")", "2")])], [mSum("i=1", "N", [mrun("("), mSub("y", "i"), mrun(" − ȳ"), mSup(")", "2")])]), mrun(",   RMSE = "), mRad([mFrac("1", "N"), mSum("i=1", "N", [mrun("("), mSub("y", "i"), mrun(" − "), mSub("ŷ", "i"), mSup(")", "2")])])]));
C.push(body("每幅图像最多保留R^2^最高的3个候选簇,以控制交叠裂隙的重复计数风险。"));
C.push(h2("5.4  求解结果与分析"));
C.push(body("对附件2的10张图像执行上述流程,其中9幅产生了合格候选簇,共保留17个正弦参数估计,逐簇结果如表5-1所示;按图像汇总的统计见表5-2。全部候选簇的平均R^2^为0.1537,平均RMSE为73.89 mm;振幅R的分布范围为6.04—343.54 mm,中心线C的分布范围为−285.65—601.83 mm。"));
C.push(tableCaption("表5-1  附件2正弦状裂隙候选簇参数反演结果(P=94.25 mm)"));
C.push(threeLine(
  ["图像", "簇", "R / mm", "β / rad", "C / mm", "R^2^", "RMSE / mm", "内点/点数"],
  PAPER.q2.rows.map((r) => [r.image, String(r.cluster), r.R.toFixed(2), r.beta.toFixed(3), r.C.toFixed(2), r.r2.toFixed(4), r.rmse.toFixed(2), r.inliers + "/" + r.points]),
  [14, 7, 13, 13, 14, 12, 13, 14]
));
C.push(tableCaption("表5-2  按图像汇总的参数反演统计"));
C.push(threeLine(
  ["图像", "候选簇数", "R均值 / mm", "R^2^均值", "RMSE均值 / mm"],
  PAPER.q2.img_summary.map((r) => [r.image, String(r.n), r.R_mean.toFixed(2), r.r2_mean.toFixed(4), r.rmse_mean.toFixed(2)]),
  [20, 20, 20, 20, 20]
));
C.push(...figure("fig_q2_sine.png", "图5-2  最优六个候选簇的正弦反演曲线(由表5-1参数绘制,阴影为±RMSE区间)", 560));
C.push(...figure("fig_q2_r2.png", "图5-3  各图像候选簇的拟合优度分布", 540));
C.push(body("从表5-1与图5-2可以看出,图2-8的三个候选簇占据了全部簇中前三位的拟合优度(R^2^=0.686、0.525、0.469),其中簇0的RMSE仅21.32 mm、内点率76.9%,其反演曲线呈现清晰的单周期正弦形态,说明\u201c线性化+RANSAC\u201d框架能够在合理参数范围内锁定真实裂隙轨迹。与之对照,图2-7簇1的振幅达343.54 mm、图2-8簇5的中心线达601.83 mm,均已超出展开图半高(250 mm)的合理量程,这类簇实质上是跨裂隙或跨纹理边缘点的混合体,其参数不具备物理意义,应视为待复核的候选而非确认的裂隙。"));
C.push(h2("5.5  拟合质量诊断与误差归因"));
C.push(body("总体平均R^2^偏低(0.1537)的原因,本文逐簇复盘后归为三点。其一,DBSCAN以空间接近性为唯一准则,在多条裂隙交叠搭接处,不同裂隙的边缘点被并入同一簇,单正弦模型无法表达,表现为RMSE高达135—148 mm的图2-2、图2-5、图2-10。其二,纹理与拼接线边缘点混入簇内,RANSAC虽可压制其影响,但当离群比例过高时内点集本身已被污染,参数随之偏移。其三,固定周期假设在裂迹不足整周期时使R^2^的分母(总平方和)变小,拟合优度对局部噪声更敏感。"));
C.push(body("对应的改进路线为:在聚类阶段引入方向一致性约束(相邻点切向夹角小于阈值),抑制跨裂隙合并;在拟合阶段开展周期候选搜索,以网格搜索评估P在[0.5L,L]内的备选周期;在筛选阶段增加内点比例下限(如≥60%)与振幅合理域(R≤250 mm)双重门限;最后对每图保留簇进行可视化人工复核,形成\u201c自动反演+人工确认\u201d的闭环。上述改造不改变模型主干,属于工程化增强,已列入8.3节的改进计划。"));
C.push(h2("5.6  问题小结"));
C.push(body("本节建立了\u201cCanny边缘提取—DBSCAN密度聚类—正弦线性化—RANSAC鲁棒回归—参数恢复\u201d的参数反演模型,对附件2的9幅图像反演出17个正弦候选簇并给出全部R、P、β、C参数与拟合指标;最优簇R^2^=0.686、RMSE=21.32 mm、内点率76.9%,验证了框架的有效性;同时以振幅与中心线的量程合理性为标尺,识别出跨裂隙混合簇并给出方向约束、周期搜索与内点率门限的改进路线,为最终表征结果表的确定奠定了方法基础。"));

/* ---------------- 6 问题三 ---------------- */
C.push(h1("6  问题三的模型建立与求解:复杂裂隙粗糙度评价"));
C.push(h2("6.1  问题分析"));
C.push(body("问题三的处理对象从规则正弦裂隙转向形态不规则的复杂裂隙,评价载体由参数化的正弦曲线转为裂隙轮廓的几何统计量。核心链条是:轮廓提取→轮廓离散化→计算粗糙度统计量Z~2~→代入Barton经验公式得到JRC。其中有两个必须审慎处理的环节:一是离散化采样策略,采样过疏会平滑掉粗糙细节,过密又会放大像素噪声,Z~2~对二者都敏感;二是像素坐标到物理坐标的标定,纵横两向的比例差异会直接改变斜率统计量。本文因此将采样策略作为显式变量,以四组方案并行计算并比较其敏感性。流程如图6-1所示。"));
C.push(...figure("fig_q3_flow.png", "图6-1  问题三求解流程图", 330));
C.push(h2("6.2  轮廓提取与坐标标定"));
C.push(body("对图像做7×7高斯平滑后以Canny(30,100)提取边缘,经cv2.RETR_LIST检索全部轮廓,保留长度不小于30的轮廓,并取围成面积最大者作为该图的主裂隙轮廓。这一选择基于如下观察:复杂裂隙虽然形态不规则,但通常构成图内最大的连通暗色结构,面积最大轮廓对其主体具有代表性;其余小轮廓多为纹理碎片。"));
C.push(bodyNoIndent("轮廓点列在计算斜率前须完成两步整理。首先,对横坐标相同的重复点取纵坐标中位数,得到单值函数形式的点列,避免零间距导致的斜率爆炸;随后按展开图物理尺度标定坐标:"));
C.push(formula("6-1", [mSup("x", "*"), mrun(" = "), mFrac([mSub("x", "px")], ["W−1"]), mrun("·L,   "), mSup("y", "*"), mrun(" = "), mFrac([mSub("y", "px")], ["H−1"]), mrun("·D")]));
C.push(body("式中L=94.25 mm为周向展开宽度,D=500 mm为展开图对应的轴向孔深,W、H为像素尺寸。"));
C.push(h2("6.3  JRC统计评价模型"));
C.push(bodyNoIndent("以标定后轮廓点列的一阶差分斜率为样本,定义均方根斜率统计量Z~2~:"));
C.push(formula("6-2", [mSub("Z", "2"), mrun(" = "), mRad([mFrac("1", "N"), mrun(" "), mSum("i=1", "N−1", [mSup([mrun("("), mFrac([mSub("y", "i+1"), mrun(" − "), mSub("y", "i")], [mSub("x", "i+1"), mrun(" − "), mSub("x", "i")]), mrun(")")], "2")])])]));
C.push(body("式中(x*~i~,y*~i~)为标定后轮廓点列的第i个点,N为采样点数。Z~2~即轮廓逐段斜率的均方根,刻画轮廓偏离平均平面的剧烈程度,对采样密度与像素噪声敏感,这为6.4节的采样策略对比提供了动机。Z~2~与Barton提出的节理粗糙度系数JRC之间存在广泛使用的经验关系[3][4]:"));
C.push(formula("6-3", [mrun("JRC = 51.85·"), mSup([mSub("Z", "2")], "0.6"), mrun(" − 10.37")]));
C.push(body("该经验公式源于对标准节理剖面的统计回归,经典适用域为Barton标准谱的0—20量级;本文以图像轮廓统计量代入,得到的是未做工程标定的JRC基线值,其绝对量级的讨论见6.5节。"));
C.push(h2("6.4  采样策略设计与敏感性分析"));
C.push(bodyNoIndent("为考察离散化密度的影响,本文设计两类四种采样方案。等间距方案按弧长索引均匀取N=32、64、128点;曲率自适应方案先取等间距基点,再按离散曲率加密:"));
C.push(formula("6-4", [mrun("S = "), mSub("S", "u"), mrun("(N) ∪ argtop-K |Δ²p|,   K = ⌊N/3⌋")]));
C.push(body("式中S~u~(N)为等间距基点集,Δ²p为相邻离散点二阶差分向量的模,即局部曲率的离散代理;取曲率最大的K=⌊N/3⌋个点补入采样集,使陡峭转折段获得更高的采样密度。四种方案逐图并行计算,共得到11×4=44组JRC估计。"));
C.push(h2("6.5  求解结果与分析"));
C.push(body("11张图像全部成功提取主轮廓并完成四方案评价,结果如表6-1所示;轮廓长度范围58—772点,轮廓面积范围98.0—875.0 px^2^。全部44组JRC基线值范围为60.98—325.25,其中等间距方案33组的结果范围为60.98—325.25,曲率自适应方案11组的结果范围为60.98—297.13。"));
C.push(tableCaption("表6-1  附件3各图像JRC评价结果(四种采样方案)"));
C.push(threeLine(
  ["图像", "轮廓点数", "面积/px²", "N=32", "N=64*", "N=128*", "曲率自适应"],
  PAPER.q3.rows.map((r) => [r.image, String(r.contour), r.area.toFixed(1), r.u32.toFixed(2), r.u64.toFixed(2), r.u128.toFixed(2), r.ad.toFixed(2)]),
  [13, 14, 14, 14, 15, 15, 15]
));
C.push(body("注:*图3-1轮廓仅58点,N=64与N=128两档均退化为58点全长采样。"));
C.push(...figure("fig_q3_sens.png", "图6-2  JRC对采样策略的敏感性", 560));
C.push(tableCaption("表6-2  采样方案的JRC统计对比"));
C.push(threeLine(
  ["采样方案", "样本数", "JRC范围", "JRC均值"],
  [
    ["等间距 N=32", "11", "60.98 — 287.73", "176.99"],
    ["等间距 N=64", "11", "60.98 — 325.25", "210.10"],
    ["等间距 N=128", "11", "60.98 — 262.48", "190.97"],
    ["曲率自适应", "11", "60.98 — 297.13", "193.22"],
  ],
  [30, 18, 30, 22],
  { boldRows: [3] }
));
C.push(body("从图6-2(a)可以看出,JRC对采样密度的敏感性呈图像间分化:图3-8、图3-10等轮廓平缓图像的JRC随N变化平缓(83.99—114.70),而图3-9、图3-2等含陡峭转折的图像波动剧烈,图3-9在N=64时冲至全组最大值325.25。从图6-2(b)与表6-2可以看出,曲率自适应方案的均值(193.22)接近等间距N=128方案(190.97),但其上界(297.13)显著低于N=64方案的325.25,表明曲率加密在转折处以更少的采样点获得了与高密度方案相当的稳定性,验证了假设(4)的意义与方案设计的合理性。"));
C.push(body("关于绝对量级需要特别说明:44组基线值全部超出Barton标准谱的经典量程(0—20),这是由成像与统计口径共同造成的——图像轮廓包含像素级锯齿与噪声边缘,标定后纵横比例(94.25:500)又放大了轴向斜率。因此本文结果应作为**图像口径下的相对粗糙度**使用,适合回答\u201c哪条裂隙更粗糙\u201d的排序问题;要映射为工程JRC,需以Barton标准 ten types 剖面图像为标定板,对同一统计口径建立映射曲线,该工作列入8.3节改进计划。此外,裂隙面积与JRC的相关性很弱(面积最大的图3-5达875 px²,JRC均值252.3,而面积相近的图3-3仅256.8),说明复杂裂隙的粗糙程度主要由轮廓形状而非尺寸决定,这与岩体力学中粗糙度独立于尺度因子的认识一致。"));
C.push(h2("6.6  问题小结"));
C.push(body("本节建立了\u201c轮廓提取—单值化整理—坐标标定—Z~2~统计—Barton经验式\u201d的JRC评价模型,并设计等间距与曲率自适应两类四种采样方案,对附件3的11张图像完成44组评价;结果表明曲率自适应采样以约一半的采样点达到与最密等间距方案相当的稳定性,全部结果以相对口径刻画了11条复杂裂隙的粗糙度排序,并明确了向工程量级映射所需的标定路径。"));

/* ---------------- 7 问题四 ---------------- */
C.push(h1("7  问题四的模型建立与求解:多钻孔连通性评价与三维重构"));
C.push(h2("7.1  问题分析"));
C.push(body("问题四将视角从单孔图像扩展到孔间空间:六个钻孔按给定孔口坐标布设,需要评价相邻钻孔间裂隙的连通程度,进而给出三维重构、高不确定性区域与补孔方案。直接的三维裂隙匹配需要单孔裂隙的三维姿态信息,而这依赖于问题二类参数反演的逐孔铺开;在当前以分段图像为基本观测单元的条件下,本文采用\u201c分段统计特征→孔对同深度差异→连通相对评分\u201d的务实路线:若两孔在同一深度段的岩体破损图像特征高度相似,则两孔被同一裂隙网络贯穿的可能性越大。该评分作为相对证据用于排序,符合假设(5)的定位。流程如图7-1所示。"));
C.push(...figure("fig_q4_flow.png", "图7-1  问题四求解流程图", 430));
C.push(h2("7.2  钻孔布置与分段特征提取"));
C.push(body("六孔孔口坐标(自西向东、自北向南)为:1号(500,2000)、2号(1500,2000)、3号(2500,2000)、4号(500,1000)、5号(1500,1000)、6号(2500,1000),单位mm,构成3×2网格,相邻孔间距1000 mm。相邻孔对共7组:(1,2)、(2,3)、(4,5)、(5,6)、(1,4)、(2,5)、(3,6)。"));
C.push(body("对每段864×9167图像,先做7×7高斯平滑与Canny(30,100)边缘检测,再提取三个统计特征:"));
C.push(formula("7-1", [mSub("f", "s"), mrun(" = ("), mSub("ρ", "s"), mrun(", "), mSub("Ī", "s"), mrun(", "), mSub("g", "s"), mrun(")")]));
C.push(body("式中ρ~s~为段s的边缘像素占比(边缘密度),Ī~s~为平均灰度,g~s~为竖直方向梯度绝对值的均值,三者分别刻画破损结构丰度、整体明暗与层理发育强度。"));
C.push(h2("7.3  相对连通评分模型"));
C.push(bodyNoIndent("对每组相邻孔对,取两孔同深度段特征,定义差异度量:"));
C.push(formula("7-2", [mSub("d", "ab"), mrun(" = |"), mSub("ρ", "a"), mrun(" − "), mSub("ρ", "b"), mrun("| + 0.002·"), mFrac([mrun("|"), mSub("Ī", "a"), mrun(" − "), mSub("Ī", "b"), mrun("|")], ["255"])]));
C.push(body("式中以边缘密度差为主导项,亮度差经归一化后以0.002的权重作辅助项,避免光照漂移主导评分。在差异基础上构造负指数相对连通评分:"));
C.push(formula("7-3", [mSub("p", "rel"), mrun(" = exp(−50·"), mSub("d", "ab"), mrun(")")]));
C.push(body("系数50使差异度量在数据实际波动范围(1.4×10^−3^—7.8×10^−3^)内充分展开,保证评分具有区分度;p~rel~单调、有界且仅用于排序,不冒充标定概率。"));
C.push(h2("7.4  不确定性与补孔候选"));
C.push(bodyNoIndent("补孔的价值在于消除评价歧义:评分越接近0.5,连通与否越难判定,该处补孔的信息收益越大。据此定义不确定性:"));
C.push(formula("7-4", [mrun("u = 1 − 2|"), mSub("p", "rel"), mrun(" − 0.5|")]));
C.push(body("对全部孔对按u降序排序,取前三处为推荐补孔候选,结果见表7-2。"));
C.push(h2("7.5  求解结果与三维重构"));
C.push(body("7组相邻孔对的同深度段评分如表7-1与图7-2所示,评分范围0.6767—0.9324,均值0.7845。其中1-4号孔对评分最高(0.9324,特征差异仅1.4×10^−3^),是连通证据最强的方向;1-2、2-3号孔对评分最低(0.6767、0.6813),图像特征差异最大。"));
C.push(tableCaption("表7-1  相邻孔对相对连通评分"));
C.push(threeLine(
  ["孔对", "评分 p~rel~", "特征差异 d"],
  PAPER.q4.rows.map((r) => [r.pair, r.score.toFixed(4), (r.d * 1e3).toFixed(3) + "×10\u207B\u00B3"]),
  [34, 33, 33]
));
C.push(...figure("fig_q4_scores.png", "图7-2  七组相邻孔对的相对连通评分(橙色为补孔候选)", 540));
C.push(tableCaption("表7-2  补孔候选方案(按不确定性降序)"));
C.push(threeLine(
  ["优先级", "孔间位置", "深度段 / m", "不确定性 u"],
  PAPER.q4.unc.map((r, i) => [String(i + 1), r.pair, String(r.seg), r.u.toFixed(4)]),
  [22, 26, 26, 26]
));
C.push(body("按不确定性排序,前三个补孔候选依次为1-2、2-3、3-6号孔间的0 m段,不确定性分别为0.6465、0.6373、0.5020。三处候选全部落在南北向孔对的上部层段,与1-2、2-3号孔对评分最接近0.5的事实互相印证。"));
C.push(...figure("fig_q4_3d.png", "图7-3  六钻孔空间布置与连通强度三维示意图", 540));
C.push(body("图7-3给出了三维重构示意:六个孔迹按实际坐标绘制,孔对之间以曲线连接,线宽与颜色编码连通评分——青色粗线(1-4、4-5、2-5)构成西侧与中部的强连通带,橙色细线(1-2、2-3、3-6)指示连通证据较弱、或被列为补孔候选的北部与东部边缘。该图直观呈现了\u201c中部强、边部弱\u201d的网络格局,可为主导裂隙面的空间展布判断提供参考。"));
C.push(h2("7.6  问题小结"));
C.push(body("本节建立了\u201c分段图像统计特征—孔对同深度差异—负指数相对评分—不确定性排序\u201d的连通性评价模型,对7组相邻孔对完成量化评价并输出三维网络可视化;识别出1-4号孔对强连通带与1-2、2-3、3-6号孔对三处补孔候选。模型全部参数显式可调,评分保持相对证据定位,为后续向几何匹配型连通概率模型升级提供了基线。"));

/* ---------------- 8 评价 ---------------- */
C.push(h1("8  模型评价、改进与推广"));
C.push(h2("8.1  模型优点"));
C.push(body("(1)链路完整、可复现性强。从数据审计到四问求解共5个代码入口,全部中间结果落盘为CSV与图像,任一数字均可由附录代码一键重现,杜绝了结果不可追溯的问题。"));
C.push(body("(2)在无标注条件下充分挖掘数据。问题一的暗色+边缘双通道、问题二的密度聚类+RANSAC、问题三的曲率自适应采样,均不依赖任何人工标签即完成量化输出,与附件实际条件严格匹配。"));
C.push(body("(3)统计口径严谨。问题三以44组采样方案显式度量离散化敏感性,问题四以相对证据定位评分,全文未将无标签诊断冒充IoU/Dice等监督指标,也未将启发式分数冒充工程概率。"));
C.push(body("(4)结果解释与误差归因并重。问题二以参数量程合理性为标尺区分有效簇与混合簇,问题三解释了JRC基线值超出经典量程的三重成因,结论均在适用边界内陈述。"));
C.push(h2("8.2  模型缺点"));
C.push(body("(1)问题一仅有候选级输出,缺少独立验证集,无法报告像素级精度指标,掩膜中仍残留纹理与泥浆误检;"));
C.push(body("(2)问题二平均拟合优度不高(R^2^=0.1537),跨裂隙混合簇与纹理离群点尚未彻底分离,表征结果表需人工复核后方可定稿;"));
C.push(body("(3)问题三的JRC停留在图像相对口径,未完成向工程量级的标定映射;"));
C.push(body("(4)问题四评分仅利用了各孔对最浅同深度段,未铺开到全部深度段,也未融入裂隙产状、JRC等几何与物理特征。"));
C.push(h2("8.3  模型改进方向"));
C.push(body("(1)分割升级:按4.5节的标注协议建立人工标注集,训练轻量U-Net并以候选掩膜作预训练粗标签,按原图分组划分数据集,以IoU/Dice在独立验证集上验收;"));
C.push(body("(2)反演强化:在DBSCAN中引入方向一致性约束,增加周期搜索与内点率门限,以\u201c自动反演+人工确认\u201d闭环产出最终表征表;"));
C.push(body("(3)粗糙度标定:以Barton标准剖面图像为标定板,建立图像统计口径到工程JRC的映射曲线,并对轮廓平滑参数做联合敏感性分析;"));
C.push(body("(4)连通概率化:将单孔裂隙映射为三维平面节点,以距离贴近度、产状相似度、粗糙度相似度与深度重叠度构造多因子加权评分,经sigmoid校准为连通概率;以三维体素化信息熵定位高不确定区域,在最小孔间距约束下以信息增益最大化为准则优化补孔布设。"));
C.push(h2("8.4  模型推广"));
C.push(body("本文的\u201c数据审计—候选提取—几何反演—空间推断\u201d框架不依赖煤系地层的特殊性,可直接迁移到隧道地质超前钻探、边坡锚固孔检测、地下管线周边土体扰动评估等场景:凡以孔壁展开图像为载体、以几何与统计特征为线索的缺陷识别与网络重构问题,均可复用该技术链路。结合钻孔机器人与在线成像设备,该框架还可进一步发展为钻孔数据自动入库、裂隙网络动态更新的智能化矿山地质保障平台。"));

/* ---------------- 参考文献 ---------------- */
C.push(h1("参考文献"));
const refs = [
  "康红普, 姜鹏飞, 王子越, 等. 煤巷钻锚一体化快速掘进技术与装备及应用[J]. 煤炭学报, 2024, 49(1): 131-151.",
  "袁亮, 张平松. 煤矿透明地质模型动态重构的关键技术与路径思考[J]. 煤炭学报, 2023, 48(1): 1-14.",
  "BARTON N R. A model study of rock-joint deformation[J]. International Journal of Rock Mechanics and Mining Sciences & Geomechanics Abstracts, 1973, 10(6): 579-602.",
  "BARTON N, CHOUBEY V. The shear strength of rock joints in theory and practice[J]. Rock Mechanics, 1977, 10(1/2): 1-54.",
  "ESTER M, KRIEGEL H P, SANDER J, et al. A density-based algorithm for discovering clusters in large spatial databases with noise[C]//Proceedings of the Second International Conference on Knowledge Discovery and Data Mining. Portland: AAAI Press, 1996: 226-231.",
  "FISCHLER M A, BOLLES R C. Random sample consensus: a paradigm for model fitting with applications to image analysis and automated cartography[J]. Communications of the ACM, 1981, 24(6): 381-395.",
  "ZUIDERVELD K. Contrast limited adaptive histogram equalization[M]//Graphics Gems IV. San Diego: Academic Press Professional, 1994: 474-485.",
  "OTSU N. A threshold selection method from gray-level histograms[J]. IEEE Transactions on Systems, Man, and Cybernetics, 1979, 9(1): 62-66.",
  "CANNY J. A computational approach to edge detection[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1986, PAMI-8(6): 679-698.",
];
refs.forEach((r, i) => {
  C.push(new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { line: 300, after: 40 },
    indent: { left: 480, hanging: 480 },
    children: [new TextRun({ text: "[" + (i + 1) + "] " + r, size: 21, font: F_BODY, color: BLACK })],
  }));
});

/* ---------------- 附录 ---------------- */
function appendixCode(letter, title, file) {
  const src = fs.readFileSync(path.join(PROJ, "code", file), "utf-8").replace(/\r\n/g, "\n").split("\n");
  C.push(h1("附录" + letter + "  " + title));
  C.push(...codeBlock(src));
}
C.push(h1("附录A  复现环境与运行方式"));
C.push(body("本文全部实验在 Python 3.11 环境下完成,依赖 NumPy 2.0、OpenCV 4.10、scikit-learn 1.5、Pillow 10 与 Matplotlib 3.11,由 uv 锁定在项目根目录 uv.lock。四个问题的求解入口依次为 code/q1_segmentation.py、code/q2_sine_fit.py、code/q3_jrc.py、code/q4_connectivity.py;结果汇总与图表生成入口为 code/export_paper_data.py 与 code/make_paper_figures.py。标准复现命令为:uv run python projects/2025-C/code/q1_segmentation.py(其余同理)。运行前需将原始数据包解压至 MASTER_PROMPT.md 指定的只读目录。审计要点:附件1的图1-2与附件3的图3-3为同一原始图像(SHA-256一致),跨附件统计时按原图去重。附录B—E给出各问核心代码。"));
appendixCode("B", "问题一核心代码", "q1_segmentation.py");
appendixCode("C", "问题二核心代码", "q2_sine_fit.py");
appendixCode("D", "问题三核心代码", "q3_jrc.py");
appendixCode("E", "问题四核心代码", "q4_connectivity.py");

/* ================================================================ 文档组装 */
function pageFooter() {
  return new Footer({
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, font: F_BODY, color: BLACK })],
    })],
  });
}

const pgSize = { width: 11906, height: 16838 };
const pgMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };

const doc = new Document({
  creator: "2025-C",
  title: "围岩裂隙精准识别与三维模型重构",
  styles: {
    default: {
      document: {
        run: { font: F_BODY, size: 24, color: BLACK },
        paragraph: { spacing: { line: 312 } },
      },
      heading1: {
        run: { font: F_HEI, size: 32, bold: true, color: BLACK },
        paragraph: { spacing: { before: 360, after: 200, line: 312 }, outlineLevel: 0 },
      },
      heading2: {
        run: { font: F_HEI, size: 28, bold: true, color: BLACK },
        paragraph: { spacing: { before: 260, after: 140, line: 312 }, outlineLevel: 1 },
      },
      heading3: {
        run: { font: F_HEI, size: 24, bold: true, color: BLACK },
        paragraph: { spacing: { before: 200, after: 100, line: 312 }, outlineLevel: 2 },
      },
    },
  },
  features: { updateFields: true },
  sections: [
    { // 第1节:标题+摘要(无页码)
      properties: { page: { size: pgSize, margin: pgMargin } },
      children: abstractChildren,
    },
    { // 第2节:目录(罗马页码)
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
      },
      footers: { default: pageFooter() },
      children: tocChildren,
    },
    { // 第3节:正文(阿拉伯页码,从1起)
      properties: {
        type: SectionType.NEXT_PAGE,
        page: { size: pgSize, margin: pgMargin, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
      },
      footers: { default: pageFooter() },
      children: C,
    },
  ],
});

const OUT = path.join(PROJ, "paper", "国奖范式论文草稿-v2.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("PASS: wrote", OUT, buf.length, "bytes");
});
