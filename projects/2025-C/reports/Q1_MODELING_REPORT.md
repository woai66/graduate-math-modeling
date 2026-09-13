# Q1 建模阶段回执

状态：PARTIAL

已运行 `code/q1_segmentation.py`，使用 CLAHE、双边滤波、黑帽变换、Otsu 阈值、Canny 边缘和形态学清理生成附件 1 的 10 张同尺寸候选掩膜，结果保存在 `figures/result/`，统计保存在 `results/q1_candidate_summary.csv`。

当前只能将输出称为“裂隙候选掩膜”。附件中未发现独立像素标签，因此不能报告 IoU、Dice、Precision、Recall 或 Accuracy，也不能把候选掩膜称为已验证的智能识别结果。

进入正式模型前必须完成：

1. 明确题面是否允许无监督输出，或建立由队伍人工复核的独立标注集并保存标注规则。
2. 按原图分组划分训练/验证，避免裁剪块泄漏。
3. 以候选掩膜为基线，比较 U-Net/轻量 U-Net 或其他分割模型，并给出独立验证和失败样本。
4. 更新 `results/result_contract_Q1.json`，填写样本覆盖、代码入口、输出附件、指标和运行 ID。
