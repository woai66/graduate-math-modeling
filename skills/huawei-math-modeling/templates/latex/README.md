# LaTeX 论文模板使用说明

## 当前状态

`main.tex` 按“华为杯”第二十三届（2026）《论文格式规范》编写，条款对应关系见 `../../references/paper-formatting.md` 第 8 节。

**尚未编译验证**：本机没有安装 TeX 发行版（`xelatex`、`bibtex`、`biber` 均不可用），因此本模板只经过静态审查，没有实际编译通过。第一次使用前必须先装发行版并编译一次，把报错和实际生成的 PDF 反馈回来修正。

## 安装 TeX 发行版

Windows 推荐 TeX Live：

```powershell
winget install --id TeXLive.TeXLive -e
```

安装后重开终端，确认：

```powershell
xelatex --version
```

## 编译

```powershell
cd templates/latex
xelatex main.tex
xelatex main.tex
```

本文献用 `thebibliography` 手写，不需要 BibTeX。若改用 `.bib`，编译顺序为 `xelatex → bibtex → xelatex → xelatex`。

必须使用 **XeLaTeX**。`pdflatex` 无法正确加载中文字体，会出现字体缺失或静默回退。

## 官方格式对应关系

| 官方要求 | 模板实现 |
| --- | --- |
| 论文题目三号黑体居中 | `{\heiti\zihao{3} ...}` 置于 `center` 环境 |
| 一级标题四号黑体居中 | `\titleformat{\section}{\centering\heiti\zihao{4}}` |
| 其他汉字小四号宋体 | `\documentclass[zihao=-4]{ctexart}` + ctex 默认宋体 |
| 单倍行距 | `\singlespacing` |
| 页码从摘要页起、页脚居中 | `\fancyfoot[C]{\zihao{5}\thepage}`，摘要页为第一页 |
| 不得有页眉 | `\fancyhf{}` 且 `\headrulewidth=0pt` |
| 图题在图下、表题在表上 | `\captionsetup[figure]{position=below}`、`[table]{position=above}` |
| 图表公式按章编号 | `\numberwithin{...}{section}` |
| 参考文献三种表述方式 | `thebibliography` 中按官方格式手写条目 |

## 为什么用 `thebibliography` 而不是 GB/T 7714 宏包

官方给出的是简化格式（书籍、期刊、网上资源三种），与 GB/T 7714-2015 的字段要求不完全相同。参赛材料以官方格式为准，手写条目最不容易出错。若队伍更习惯 `gbt7714` 宏包，也可以使用，但要逐条核对输出结果是否符合官方三种表述方式。

## 常见坑

- **字体缺失**：XeLaTeX 找不到宋体/黑体时会静默回退，导出的 PDF 字体不对。核对 PDF 属性里的实际嵌入字体。
- **行距不等于 1.5**：官方要求单倍行距，中文排版里 `\singlespacing` 与 `\linespread{1.5}` 完全不同，不要混用。
- **浮动体跑位**：图和表可能被推到不合逻辑的页，定稿前逐页核对；必要时用 `\usepackage{float}` 加 `[H]`。
- **表格溢出**：宽表会超出页面，改用 `tabularx` 或缩小列间距。
- **页码起始**：摘要页必须是第 1 页。若前面加了封面或目录，需要用 `\pagenumbering` 重新起编。
- **匿名**：不要在 PDF 元数据、文件名或正文里留姓名、学校、队号以外的身份信息。

## 与 Word 路线的关系

官方提交格式是 PDF，且版式要求（宋体小四、黑体标题）用 Word 官方模板最容易精确满足。若队伍不熟悉 LaTeX，直接用官方模板 + 样式表更稳。两条路线只保留一份源稿，另一份只用于校验，避免出现两个版本的数值不一致。
