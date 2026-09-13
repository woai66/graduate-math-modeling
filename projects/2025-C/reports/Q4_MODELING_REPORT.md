# Q4 建模阶段回执

状态：PARTIAL

已对附件 4 的六孔分段图像计算平滑 Canny 边缘密度、亮度和梯度特征，并在七组相邻钻孔对之间构造同深度段相对连通评分。结果写入 `results/q4_connectivity_results.csv`，不确定性候选写入 `results/q4_uncertainty_candidates.csv`。

当前评分是未标定的相对证据，尚未整合单孔裂隙几何、方向、JRC 和真实连通标注；补孔位置只能作为候选，不能写成工程决策结论。
