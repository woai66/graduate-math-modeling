# 论文证据链

建立 `reports/evidence_matrix.csv`，每行对应一个论文可核验主张：

```text
claim_id,question,claim_text,evidence_type,evidence_path,code_path,parameters,validation,status
```

## 绑定规则

- 数值结论绑定结果 CSV/JSON 和生成代码；记录运行命令、输入哈希和参数。
- 图表绑定源数据、绘图脚本和图像文件；正文段落必须解释图表作用。
- 模型假设绑定题面、领域文献或数据检验；不能只写“合理假设”。
- 创新绑定基线、改进模型和对比/消融结果；没有对比证据只能称为候选方案。
- 引用绑定正式论文、标准或官方页面；AI 输出不是引用来源。

## 写作顺序

先填证据矩阵，再写摘要和结论，最后补充连接段落。任何无法填入 `evidence_path` 的定量句子都必须删除或改成待验证说明。
