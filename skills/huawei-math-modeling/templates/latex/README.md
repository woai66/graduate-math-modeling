# LaTeX 论文模板使用说明

## 当前状态

`main.tex` 按“华为杯”第二十三届（2026）《论文格式规范》编写，条款对应关系见 `../../references/paper-formatting.md` 第 8 节。

**已编译验证**（2026-09-22，TeX Live 2026 + XeLaTeX）：连续两次 `xelatex` 成功生成 3 页 PDF，无错误。实测结果：

| 检查项 | 实测 |
| --- | --- |
| 题目 | 黑体 16.00 pt（三号）+ 西文 Times New Roman 16 pt |
| 一级标题 | 黑体 14.00 pt（四号） |
| 正文 | 宋体 12.00 pt（小四） |
| 图表标题 | 宋体 10.50 pt（五号） |
| 页脚页码 | Times New Roman 10.50 pt |
| 纸张 | 595.3 × 841.9 pt（A4） |
| 嵌入字体 | SimSun、SimHei、TimesNewRomanPSMT 均正确嵌入，无静默回退 |
| 分页 | 摘要页为第 1 页，正文从第 2 页开始 |

页边距取自官方附件3 模板实测值（上 30.0、下 17.5、左右 22.5 mm）。`footskip=0.9cm` 是让页脚落在下边距内的近似值，与 Word 版式可能有毫米级差异，定稿前请与官方模板并排目视比对。

## TeX 发行版安装情况

本机已安装 TeX Live 2026 到 `C:\Users\zyq\texlive\2026`，采用 `scheme-basic` + `collection-langchinese`，再按需补装 xetex 与排版宏包（不含文档，约 700 MB 量级）。可执行文件目录：

```text
C:\Users\zyq\texlive\2026\bin\windows
```

若在新机器安装，官方未提供 winget 包，需要下载 CTAN 的 `install-tl.zip` 后用自带 Perl 非交互安装。也可以选择 MiKTeX（`winget install MiKTeX.MiKTeX`），它会按需自动补包。

## 若需补装宏包

```powershell
C:\Users\zyq\texlive\2026\bin\windows\tlmgr.bat install <包名>
```

## 依赖版本

- XeTeX 3.141592653-2.6-0.999998（TeX Live 2026）
- kpathsea 6.4.2

## 编译

```powershell
$bin = 'C:\Users\zyq\texlive\2026\bin\windows'
& "$bin\xelatex.exe" -interaction=nonstopmode main.tex
& "$bin\xelatex.exe" -interaction=nonstopmode main.tex
```

本文献用 `thebibliography` 手写，不需要 BibTeX。若改用 `.bib`，编译顺序为 `xelatex → bibtex → xelatex → xelatex`。

必须使用 **XeLaTeX**。`pdflatex` 无法正确加载中文字体，会出现字体缺失或静默回退。

模板中的 `\includegraphics{figures/demo.pdf}` 需要先在 `figures/` 放入图片，否则编译会报找不到文件。

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
