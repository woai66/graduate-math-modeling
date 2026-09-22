# 参考资料索引

本目录的每个文件都有唯一职责。按任务读对应的文件，不要一次全部加载，也不要读取上一层 `_archive/`。

## 按任务选择

| 当前在做什么 | 读这些 |
| --- | --- |
| 开始一道新题、选题、与队伍讨论题意 | `../SKILL.md` → `rebuild-spec.md` 第 0 节 → `simulation-training.md` |
| 判断当前阶段该产出什么、什么算完成 | `stage-contracts.md` |
| 拆题、确定每问任务与主分类 | `problem-routing.md` |
| 数据审计、清洗、划分、防泄漏 | `data-analysis.md` |
| 选模型、找基线和备选方法 | `algorithm-catalog.md` |
| 构思创新点、准备反方审阅 | `novelty-and-dialectics.md` |
| 参考别人怎么建模、哪些坑不要踩 | `excellent-paper-deconstruction.md` |
| 写正文、定大纲、控篇幅 | `paper-writing.md` |
| **排版定稿：字体、字号、行距、页码、公式、图表、参考文献格式** | `paper-formatting.md` |
| **AI 使用与标注合规（必读）** | `ai-compliance.md` |
| 把结论绑定到结果、代码和图表 | `evidence-chain.md` |
| 定稿前质量审阅 | `excellent-paper-rubric.md` |
| 做论文流程图、数值图、配色 | `diagram-workflow.md` |
| 检查 Word 结构、公式、图表、字体 | `docx-checks.md` |
| 核对环境、Git/gh、外部工具借鉴边界 | `toolchain-and-open-source.md` |
| 正式参赛前核对当届规则、模板、附件、AI 规范 | `official-rules-checklist.md` |
| 查询完整工作规范的其他章节 | `rebuild-spec.md` |
| 追查历史版本 | 上一层 `_archive/README.md`，只用于追溯，不作为依据 |

## 文件职责速查

- `rebuild-spec.md`：完整工作规范，含讨论机制、数据/模型/实验要求、论文与交付要求、回归验收设计。
- `simulation-training.md`：赛前仿真训练的端到端流程与今日最小目标。
- `stage-contracts.md`：D0/M1/P1/P2/W1/W2 各阶段的输入、输出、完成条件与交付级别。
- `novelty-and-dialectics.md`：创新四问、反方审阅、反例优先、诚实命名、人机分工。
- `excellent-paper-deconstruction.md`：七篇参考论文的逐篇解剖、可迁移范式与需警惕模式。
- `excellent-paper-rubric.md`：定稿前的十维审阅表和红线项。
- `paper-writing.md`：论文大纲、每问闭环写法、格式编号、篇幅预算原则。
- `paper-formatting.md`：官方排版硬性要求、中文字号对照、样式体系、公式与图表规范、参考文献三种表述、LaTeX/Word 两条路线、定稿验收清单。
- `ai-compliance.md`：官方 AI 使用规定、标注模板、项目日志要求、定稿检查与红线。
- `evidence-chain.md`：主张、结果、图表、代码、参数和引用的绑定格式。
- `problem-routing.md`、`data-analysis.md`、`algorithm-catalog.md`：题型路由、数据检查和方法候选。
- `diagram-workflow.md`：Excalidraw 论文插图路线、NPG 配色、导出与验收。
- `docx-checks.md`：Word 可用的结构预检脚本与人工检查要求。
- `official-rules-checklist.md`：第二十三届官方附件1—4 的核验结果、文件哈希、提交链路与未核验项。
- `toolchain-and-open-source.md`：本地工具状态、Git/gh 边界、外部开源项目借鉴范围。

## 项目资料路由

- 仓库根 `README.md`：竞赛简介、题型分类、2023—2025 赛题统计和备赛策略。
- `projects/<year>-<topic>/`：具体题目的题目卡、数据字典、代码、结果、图表和论文。
- `templates/`：项目计划、阶段状态、结果契约、证据矩阵、仿真运行记录模板。
- `assets/`：流程图现行示例；其中图片不作为模型结果证据。
- 外部资料目录：历年题面、优秀论文和代码资料；引用时保留文件来源、页码或哈希。

## 归档政策

`_archive/` 中的文件已经被取代或已知有缺陷，不参与任何通过判定，也不应作为写作或建模依据。历史脚本只有在完成真实正例与负例测试后才能重新接入；文件存在、脚本运行成功或手工写入 `PASSED` 都不构成验收证据。

