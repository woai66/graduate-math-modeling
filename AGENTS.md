# 本仓库的数模工作规范

处理本仓库的华为杯赛题、代码或论文时，显式读取仓库版
`skills/huawei-math-modeling/SKILL.md`，再按任务读取
`skills/huawei-math-modeling/references/rebuild-spec.md` 的相关章节。

仓库版目前是 `0.5.0-draft`，尚未经完整赛题验证。已安装的旧
`huawei-math-modeling` 副本保留，但不作为本仓库的当前规范；其中固定篇幅配额、
85/90 分评级、固定四问及手工 PASSED 门禁不继续沿用。

文件只在 `SKILL.md` 与 `references/README.md` 指定的路由中读取：

- 论文写作以 `references/paper-writing.md` 为准；
- 论文排版以 `references/paper-formatting.md` 为准，字体（题目三号黑体居中、一级标题
  四号黑体居中、其余汉字小四宋体）、单倍行距、页脚居中页码、无页眉、可编辑公式都是
  官方硬性要求，排版不达标不能进入评阅比较；
- AI 使用以 `references/ai-compliance.md` 为准：允许辅助，不得替代独立思考与核心创新；
  论文文字必须由队员用自己的语言表述；程序与数据分析按官方四要素标注工具信息；
- 创新与自我质疑以 `references/novelty-and-dialectics.md` 为准；
- 参考别人怎么建模时读 `references/excellent-paper-deconstruction.md`；
- 论文流程图以 Obsidian Excalidraw 路线为准，见 `references/diagram-workflow.md`；
  桌面图通过不能代替论文版心与 Word 插图验收。

`skills/huawei-math-modeling/_archive/` 是历史归档，只用于追溯，不作为规则、模板或
验收依据；搜索命中那里的文件时，以现行文件为准。

按用户要求，新题先由人与 AI 充分讨论选题、题意、创新定义及模型与实验方案，
再按共同确定的范围分步实施。已明确的决定不反复确认；核心路线改变时重新讨论。
人和 AI 都要提出新方案并对自己的方案给出最强反对意见；创新点须回答
“新在哪、为什么旧方法不够、怎么证明、边界在哪”，答不上就降级或删除。
数值结果图优先由真实数据与代码生成，跨问题结果必须保留版本、单位及依赖来源。
未标定的量只能叫评分或指数，无独立标签不得报准确率。

接续 C/D 项目先核对当前代码、结果与审阅记录，保留已有未提交成果。
遵守用户当前任务范围及 Git 授权；本文件不授权提交、推送或改写历史。
