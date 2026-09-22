# 归档区：不要读取，不要据此决策

本目录保存已经被现行规范取代的开发中间产物、历史版本和已知有缺陷的检查器。保留它们是为了审计和追溯，**不是**可用资源。

任何 agent 在竞赛过程中都不应把本目录的内容当作规则、模板或验收依据。如果搜索命中这里的文件，以 `SKILL.md` 和 `references/` 下的现行文件为准。

## 归档内容与原因

### references/

| 文件 | 归档原因 | 替代 |
| --- | --- | --- |
| `content-quota.yaml` | 固定字数/页数/图表数配额，与按论证负担分配篇幅的现行规范冲突 | `references/paper-writing.md` |
| `quality-gates.md` | 基于手工 `PASSED` 串行门禁和固定题型清单，与阶段合同冲突 | `references/stage-contracts.md`、`references/excellent-paper-rubric.md` |
| `paper-style.md`、`paper-outline.md`、`award-paper-profile.md` | 三份文件内容重叠，容易出现口径分歧 | 合并为 `references/paper-writing.md` |

### scripts/

| 文件 | 归档原因 |
| --- | --- |
| `verify_submission_readiness.py` | 读取手工 `PASSED` 状态和 CSV 文件大小，在 DOCX 压缩字节里找关键词，不能检验正文和科学结论 |
| `check_stage_gate.py` | 把研究过程压成 `PASSED` 串行链条，与可并行的阶段合同冲突 |
| `verify_docx_structure.py` | 假定固定四问，且把最后一问的统计延伸到文档末尾，附录会被计入正文 |
| `verify_docx_math.py` | 同时累加 `oMath` 与 `oMathPara`，存在重复计数 |
| `audit_paper_corpus.py` | 依赖外部 `pdfinfo`，功能已被 `scripts/extract_paper_text.py` 覆盖 |
| `excalidraw_paper_demo.js` | 早期 Excalidraw 示例，已被 `excalidraw_simple_flow.js` 与 `excalidraw_award_style_demo.js` 取代 |

### assets/

早期 Excalidraw 示例（`excalidraw-paper-flow.*`）、复杂示例的编辑前快照（`*.before-*.excalidraw`）、过程记录 JSON、Word 渲染检查输出，以及 Archify 交互示例的构建产物。这些是开发过程证据，不是当前推荐的流程图资产；现行资产见 `assets/excalidraw-simple-flow.*`、`assets/excalidraw-award-style-demo.*` 与 `assets/modeling-process.workflow.json`。
