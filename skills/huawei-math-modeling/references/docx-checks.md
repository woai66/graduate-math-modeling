# DOCX 检查入口

生成 Word 论文后，若 Python 和 `python-docx` 可用，运行：

```powershell
python scripts/verify_docx_typography.py 完整论文.docx
python scripts/verify_docx_math.py 完整论文.docx --min-equations 1
python scripts/verify_docx_figures.py 完整论文.docx --min-figures 1 --min-explained 1
```

这些脚本只做结构性预检，不能替代人工阅读、Word 打开检查和页面渲染。若依赖缺失，报告 `BLOCKED`，不要把未检查的文档称为已通过。
