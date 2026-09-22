# 流程图工具接入与验收

适用范围：数模选题讨论、技术路线、逐问求解流程和数据依赖图。使用前先读仓库版 SKILL.md。这里只维护流程图能力；数值结果图仍由真实数据与科学绘图代码生成。

## 1. 按图的目的选择工具

| 用途 | 默认方式 | 交付和边界 |
| --- | --- | --- |
| 与队伍讨论步骤、分支、依赖 | Mermaid 文本草图 | 可快速修改；当前没有单独安装 mmdc，不能承诺命令行导出已可用 |
| 复杂技术路线、数据流、交接、互动讲解 | 已安装的 Archify Skill | 可编辑 JSON 规格、独立 HTML、SVG/PNG；需要结构校验和实际截图检查 |
| 放入论文的可编辑方法流程图 | 优先 Obsidian Excalidraw + ExcalidrawAutomate；保留原生源图，导出 SVG/PNG | 本地复杂样图已验证编辑、导出和 WPS DOCX 单页呈现；Microsoft Word 与异机字体仍需实测。按最终版心检查，不以像素数代替物理字号 |
| 分布、回归、拟合、误差、几何/空间结果 | Matplotlib、Seaborn、NetworkX 等 | 不调用流程图工具伪造结果；保留数据、脚本、单位和运行来源 |

本机 Archify 已安装，无需新增 MCP。只有需要某个绘图应用的协作、编辑或专属格式能力时才发现并引入相应连接器；外部账户、上传和发布另按用户范围处理。本次未修改安装副本或引入外部服务。

## 1.1 Excalidraw 论文插图路线

2026-09-20 按用户提供的优秀论文截图制作了三层、三列、嵌套框、空心箭头与跨栏反馈样图。源图 `assets/excalidraw-award-style-demo.excalidraw.md` 可在 Obsidian 编辑；同名 `.excalidraw` 是本次导出时的固定交换快照，`.svg`/`.png` 为插件实际导出。此图只演示表达方式，不证明园林模型已经实施。

本地链路采用 Obsidian 1.13.7 + Excalidraw 2.26.4。CLI 已开启；先通过 CLI `help eval` 和只读查询核对知识库，再调用该知识库内的 EA。不要依赖另一台电脑的可执行文件位置。`scripts/excalidraw_award_style_demo.js` 是可复用绘图示例，按次注入 `ea`、`app`、`mode` 执行，支持 `create`、`inspect`、`edit`、`polish`、`recolor`、`check-saved`、`export`。`create` 遇到同名源图会拒绝覆盖；`edit`/`polish` 仅用于这个测试件，真实论文按实际元素和语义改写。

操作时保留以下要点：

- 论文风格使用白底、低饱和分区、`roughness: 0`，统一字体与间距。先确定分区和连线路径，再放节点；跨栏反馈走预留通道。
- 中文先 `measureText`，还要给绑定容器留出内边距。测量能放下不代表插件恢复场景后不会换行，必须看实际导出。
- 图形与文字使用 `containerId`、`boundElements` 双向绑定；关系箭头设置端点绑定。空心大箭头可用原生闭合折线组合。移动它们后仍检查端点和走线。
- 编辑现有图时先 `copyViewElementsToEAforEditing`，只改工作副本，再 `await addElementsToView`。保留元素 ID 和 `customData`，不能以删除重建代替编辑验证。
- 保存可能滞后于 `addElementsToView` 返回。导出前用 `getSceneFromFile` 对照画布的文字与几何；示例的 `check-saved` 最多等待 4 秒，不一致就停止。导出期间源文件改变也停止，不把旧图标为最新。
- 2.26.4 本机没有 `createViewPNG`。使用已经验证的 `createSVG(savedPath, true, settings, ...)` 与 `createPNG(savedPath, scale, settings, ...)`；先 `ea.clear()`，避免工作台残留元素参与导出。不能照抄更新版本接口假设本机可用。
- 活动源图可继续手工编辑；定稿 PNG、Word 与导出时快照绑定，记录指纹。之后源图改变则重新导出和检查，不能覆盖队员的编辑来强配旧图。
- 通过 EA 改完场景后要显式保存。实测 2.26.4 中 `addElementsToView(save=true)` 之后自动保存未必在检查窗口内落盘，只调 `check-saved` 会一直判定“画布与源文件不一致”；正确顺序是 `setDirty()` 再 `await view.save()`，然后比对。示例脚本的 `flushSave` 已固化这一步，缺少它时导出的是旧图。

### 论文插图配色（Nature / NPG）

正式论文插图用低饱和科研配色，不用高饱和渐变、阴影和荧光色。本仓库采用科研绘图常用的 NPG（Nature Publishing Group）方案，按“深色细描边、极浅色底、近黑正文”处理：

| 角色 | 色值 | 用途 |
| --- | --- | --- |
| 正文与关键文字 | `#1A1A1A` | 近黑，避免纯黑在屏幕上过硬 |
| 结构主线 | `#3C5488` | 流程骨架与问题一面板 |
| 数据与预处理 | `#4DBBD5` | 专用于数据流，不与问题色混用 |
| 强调与反馈 | `#B5534A` | 需要回看的分支与反馈箭头 |
| 验证与迁移 | `#00A087` | 对照实验与泛化验证 |
| 结论带 | `#B09C85` | 最终结论的收束区 |
| 辅助标注 | `#8491B4` | 次要连线与注释 |
| 面板底色 | `#EDF1F7` / `#FBEDEA` / `#E7F4F1` | 三块并列面板的浅色底 |

约束：一张图主色不超过四种；同一含义始终同色；浅色只铺底、深色只描边；灰度打印后仍要能靠明暗区分层级。示例脚本的 `recolor` 模式在保留元素 ID、文字与端点绑定的前提下换色，实测 106 个元素全部换色且 ID 不变。

本次样图有 106 个原生元素，已实际修改中文标签并移动节点，随后整体换用上述 NPG 配色并保留全部元素 ID。导出为 SVG 1128×1360、PNG 3384×4080；按 16 cm 宽插入 A4 DOCX，有效分辨率约 537 dpi，最小标签约 9.65 pt。实际使用 WPS Writer 12.1.0.28488 导出 PDF，再以随包 Poppler 渲染 1/1 页并查看；中文、分支、反馈、配色和分页通过本地检查。`render_docx.py` 因本机缺少 `soffice.exe` 无法执行渲染，因此不能声称 LibreOffice 或 Microsoft Word 已验证。验收记录见 `assets/excalidraw-award-style-demo.review.json`；换色过程记录已归档到 `_archive/assets/excalidraw-award-style-demo.recolor-check.json`。

`-word.docx` 用于检查排版；图形在 Word 内是整张 PNG，在 Excalidraw 源文件中逐项编辑。SVG 的中文跨机器字体仍待验证。Archify 保留用于讨论和互动讲解；本测试不要求新增 MCP 或上传绘图服务。

### 最小示例：中文加分支加反馈箭头

`scripts/excalidraw_simple_flow.js` 是入门练习用的最小图，27 个原生元素（7 矩形、1 菱形、10 文字、9 箭头），主线为题意解析 → 数据核对 → 方案讨论，分叉到基线模型与创新模型，汇总到小样本核验，再由菱形判断分流：达标走全量实验，不达标沿右侧专用通道虚线回到方案讨论。两条命令即可复现：

```powershell
obsidian eval 'code=(async()=>{const s=await app.vault.adapter.read("20_学习/研究生数模竞赛/skills/huawei-math-modeling/scripts/excalidraw_simple_flow.js");const F=Object.getPrototypeOf(async function(){}).constructor;return JSON.stringify(await new F("ea","app","mode",s)(ExcalidrawAutomate,app,"create"));})()'
obsidian eval 'code=(async()=>{const s=await app.vault.adapter.read("20_学习/研究生数模竞赛/skills/huawei-math-modeling/scripts/excalidraw_simple_flow.js");const F=Object.getPrototypeOf(async function(){}).constructor;return JSON.stringify(await new F("ea","app","mode",s)(ExcalidrawAutomate,app,"export"));})()'
```

创建时会校验每个中文标签是否放得下，放不下直接报错而不是让插件自动换行；导出前先 `flushSave` 再比对画布与源文件，不一致就停止。实测结果：SVG 968×932、PNG 2904×2796、9 条箭头全部带端点绑定，产物见 `assets/excalidraw-simple-flow.*`。

## 2. 图在研究流程中的位置

- 选题及题意讨论：画输入、任务与开放概念之间的关系，标清待决定分歧；不能把候选方法画成已实施。
- 方案确定：绘制推导、预处理、求解和验证的技术路线，标出每问输入/输出及反馈；这时可产生正式图规格。
- 编程与实验：随实现更新图，明确实际使用的数据、模型和验证分支。算法改变时同步图规格，不能保留未实现模块装饰方法链。
- 跨问核对：重点画数据依赖，带对象 ID、单位、版本和质量标志的接口；结构图本身不能代替真实结果索引。
- 论文定稿：图与最终代码/公式/实验版本逐项对应，按论文尺寸静态导出，放进 Word 后再渲染检查。

已有共同决定的流程不重复请求确认。图揭示了新的模型分歧或改变研究主线时再讨论。建模创新由人和 AI 共同论证，制图工具负责准确表达已经成立的关系。

## 3. 生成前的最小信息

在现有图规格或项目记录中明确：图的用途与章节、要解释的问题、节点及含义、箭头的实际关系、必要分支/返回条件、哪些内容已实现、事实来源、目标尺寸。避免为每张图新建一套状态表。

本仓库示例是**备赛协作流程说明**，不是某道赛题的技术路线，也不是任何题目已经完成的证明。主线为选题与题意 → 数据初核 → 共同定方案 → 分步实验 → 贯通结果 → 论文审阅与交付；核心方案改变时回到共同讨论。

## 4. Archify 操作步骤（讨论展示用途）

首次使用按本机可用路径读取 Archify 的 SKILL.md。目前位置为 `C:/Users/zyq/.codex/skills/archify/SKILL.md`；其他电脑重新定位，不把该用户路径写入题目代码。工具本轮核验版本为 2.16，Node.js 为 v24.19.0，版本变化后重跑示例。

1. 按内容选 workflow、dataflow 等类型，只读取对应 schema、common schema 和一个示例。
2. 根据真实语义写 JSON 规格，先用自动布局/路由；使用 `meta.locale: zh-CN`、`meta.quality_profile: showcase`。
3. 运行 validate，按具体诊断修改节点和连线；保留有意义的箭头和标签，不能删掉反馈来凑通过。
4. 通过后用 deliver 生成 HTML，保存同名 `.delivery.json` 凭据。结构通过需要 9/9、零错误、零警告。
5. 用 visual-check 检查 1440×900、1600×1000、1920×1080、2048×1320，并查看浅/深色截图；自动回执中的 `visualReview: pending` 不要手改成通过，视觉审阅另记录。
6. 从已校验 HTML 的自带导出菜单导出 SVG/PNG。可用本 Skill 的 `scripts/export_flowchart.mjs` 执行此操作，它校验 HTML 与图规格指纹，使用隐藏浏览器、阻止外网请求，不修改图几何。
7. 检查实际静态图，核对文字、箭头、图例和反馈；再做目标 Word 版心检查。

PowerShell 命令模板（先将变量赋为依赖加载器与本机工具实际返回的路径）：

```powershell
& $nodeExe $archifyCli doctor
& $nodeExe $archifyCli validate workflow $specPath --quality showcase --json
if ($LASTEXITCODE -ne 0) { throw '流程图结构校验失败' }
$delivery = & $nodeExe $archifyCli deliver workflow $specPath $htmlPath --quality showcase --json
if ($LASTEXITCODE -ne 0) { throw '流程图生成失败' }
$delivery | Set-Content -LiteralPath $deliveryPath -Encoding utf8
& $nodeExe $archifyCli visual-check $htmlPath --json
if ($LASTEXITCODE -ne 0) { throw '页面检查失败，读取诊断后修复' }
& $nodeExe $exportScript $htmlPath --playwright-dir $playwrightDir --browser $chromeExe
if ($LASTEXITCODE -ne 0) { throw '静态导出失败' }
```

`$deliveryPath` 为 HTML 去掉 `.html` 后加 `.delivery.json`；导出脚本要求图规格与 HTML 放同一目录、规格文件名与凭据一致。脚本读取凭据，不重新决定模型，也不提供科学有效性判定。输出有同名 `.svg`、`.png` 和 `.export.json`。

在当前沙箱内，Archify 渲染曾因解析用户目录报 `EPERM realpath`；按环境审批要求运行本地命令后可正常执行。遇到这种权限错误走审批机制，不复制工具绕过限制，也不把它当成布局错误。

## 5. 结构、视觉和论文插图分别验收

| 层次 | 实际检查内容 | 通过不能替代什么 |
| --- | --- | --- |
| 语义 | 节点、分支、箭头与已确定方案/实际实现一致 | 不证明模型有效 |
| 结构 | 规格合法、节点不重叠、连线不穿无关节点、反馈方向清楚 | 不证明页面尺寸合适 |
| 桌面视觉 | 四种窗口、浅深主题、文字/线条清楚、无裁切和页面溢出 | 不证明放进 Word 后可读 |
| 静态导出 | SVG/PNG 有效，无工具栏、临时焦点和交互遮罩；与输入哈希绑定 | 不证明目标 Word 能正确渲染 SVG |
| 论文尺寸 | 在实际版心下文字清晰，线宽和灰度对比合适；插入 Word 后全页检查 | 不证明论文内容或引用正确 |

练习稿以正文 16 cm 左右版心为参考时，先把图按这个宽度显示。图内关键文字通常以 9 pt 或更大作为初始设计目标，并按官方模板、信息密度和实际可读性调整。这是字号设计参考，不是固定质量评分。PNG 的像素/有效 dpi 只解决清晰度，不解决文字物理尺寸太小。

Archify 自带 SVG 为双主题矢量输出；导出的 PNG 采用当时主题。论文优先用已经核查的浅色 PNG，或对 SVG 在目标 Word/PDF 渲染器中做实际兼容性测试。SVG 导出包含可编辑图形文本，不代表 Word 中每个元素都是原生流程图形状。

任何布局调整都修改源规格并重新 validate/deliver；不能只改 HTML 后沿用旧回执。实际改动输入后，导出脚本应拒绝使用旧的通过凭据。

## 6. 本次可复现示例与已知边界

Archify 讨论示例的源规格保留在 `assets/modeling-process.workflow.json`；其余构建产物（`html`、`delivery.json`、`validation.json`、`visual-check.*`、`svg`、`png`、`export.json`、`review.json`）已归档到 `_archive/assets/`，需要时按规格重新生成。

2026-09-20 的实际结果（归档记录）：结构 9/9，零错误、零警告；四种桌面尺寸检查通过，四张浅/深截图已查看；PNG 2880×1600、SVG 成功导出。截图和静态 PNG 中的中文、箭头、图例均可辨，无节点遮挡。此图可用于讨论和备赛说明。

发现并修复的问题：最初宽节点超出 Archify workflow 固定列间距；随后纵向多层图在桌面视口高度溢出。最终采用两阶段布局，保留核心方案调整反馈。示例采用折返阅读，因此没有声明单调递增列的 `mainPath`；不能伪造 mainPath 来通过布局限制。

**旧 Archify 示例的论文版面仍待验证：**当前示例包含较小的副标题与图例，缩至 16 cm 宽后不能直接按正式论文插图验收；进入论文前需重新布局、精简非必要副标题或拆图，保留所有关键语义并检查实际字号。该 Archify 图未生成 Word 插图验证件；不得混用 Excalidraw 样例的验收结论。

## 7. 重建进度

流程图模块已完成首次本地生成、检查和导出试运行；数模 Skill 的科学模型、数据证据、完整论文等其他模块仍待重写和实战验收。后续优先完成：科学绘图统一样式与真实数据示例、跨问题输入输出/结果索引、Word 公式与图表排版验证。它们按实际需要逐项接入，不能因流程图可用而把整套 Skill 标为成熟。
