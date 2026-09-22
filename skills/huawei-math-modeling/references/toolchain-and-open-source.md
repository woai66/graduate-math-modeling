# 工具链与开源参考

## 本地工具状态

以当前项目实际探测结果为准，运行前记录：Python、uv、Git、gh、Obsidian CLI、Word/WPS、Node.js 及关键 Python 包的版本。`uv.lock` 是 Python 依赖的来源；不要在系统 Python 中随意安装项目依赖。工具不存在时记录阻塞和替代方案，不把“命令能启动”当成数学或论文通过。

推荐检查命令：

```powershell
python --version
uv --version
git --version
gh --version
obsidian version
```

Git/gh 检查默认只读：远程地址、当前分支、登录状态和工作区变化。提交、推送、建 PR 或发布必须由用户明确授权；禁止使用 GitHub Contents API 上传文件。

## 外部项目的借鉴边界

- [woai66/math-modeling-skill](https://github.com/woai66/math-modeling-skill)：作为 Skill 组织、提示词分层和建模任务路由的参考。使用前记录具体提交、许可证、实际借鉴文件和本地验证结果。
- [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent)：作为多阶段任务拆解、代码/论文交接和智能体协作的参考。使用前记录具体提交、许可证、实际借鉴机制和本地验证结果。

仓库关注度或宣传语不构成科学证据。没有完成版本核对和行为测试时，只能写“参考设计”，不能写“已完整吸收”“已验证成熟”。不得复制外部项目的代码、提示词或资源到参赛论文而不保留许可证和来源。

## 绘图工具选择

论文数值图优先由 Matplotlib/Seaborn/NetworkX 等代码生成；论文流程图优先使用 Obsidian Excalidraw + ExcalidrawAutomate，保留可编辑源、SVG/PNG 和版心检查记录。Archify 适合交互式讨论和结构化流程展示。选择标准是可编辑、可复现、导出质量和 Word 兼容性，而不是工具数量。
