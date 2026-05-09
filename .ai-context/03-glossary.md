# 03 · 术语表

<!-- 随项目推进增补。每条一行，定义精炼。 -->

## 通用
- **AMC**: Automatic Modulation Classification，无线电自动调制识别任务。
- **RadioML2016.10A**: 当前项目主证据数据集；full 实验和 Paper-Stage 5A/5B 均围绕它展开。
- **RadioML2018.01A**: 后续扩展目标；当前不能写成已完成验证。
- **I/Q**: In-phase / Quadrature 原始复基带信号表示，常作为 `[2, 128]` 输入。
- **SNR**: Signal-to-Noise Ratio，信噪比；本项目常按 low/mid/high SNR 分组分析。
- **STFT**: Short-Time Fourier Transform，短时傅里叶时频特征。
- **CWT**: Continuous Wavelet Transform，连续小波时频特征；当前 on-the-fly full 计算成本较高。
- **Fixed split**: 固定数据划分协议，保证不同模型和 seed 在同一 split 上可比。
- **Manifest**: 归档清单，记录文件路径、hash、sync policy 和 evidence label。
- **Baton**: 当前交接状态文件；新主入口是 `.ai-context/05-current-state.md` 和 `06-session-log.md`。

## Machine Learning
- **Epoch**: 一次遍历完整训练集的迭代单位。
- **Batch size**: 单次梯度更新所用的样本数；过大费显存，过小训练不稳。
- **Learning rate**: 梯度更新步长；最敏感的超参数之一，常配合 warmup 与 decay 调度。
- **Overfitting**: 训练损失持续下降但验证损失反弹；模型记住了训练集而非泛化。
- **Regularization**: 抑制过拟合的手段，如 L1/L2 权重衰减、Dropout、Early stopping。
- **Gradient clipping**: 把梯度范数截断到阈值，防止爆炸梯度。
- **Checkpoint**: 某一训练步的模型状态快照；本项目 `best_model.pt` 不默认同步到本地。
- **Inference**: 训练完成后用模型做预测的阶段；论文中需要区分 forward-only latency 与 preprocessing-inclusive latency。
- **Quantization**: 把 FP32/FP16 权重压到 INT8/INT4；当前不是主证据范围。

## 项目证据标签
- **PROJECT_SUPPORTED**: Stage 5A/5B full RadioML2016.10A fixed-split 证据，可用于有边界的主表和统计检验。
- **CONTROLLED_LATENCY**: 受控 CUDA forward-pass latency 证据；不支持 CPU latency、FLOPs/MACs 或 preprocessing-inclusive 部署结论。
- **SMOKE TEST**: 工程可运行性验证，只能说明链路通，不能作为性能结论。
- **DIAGNOSTIC**: 诊断或筛查输出，必须与主表隔离；若做 tiny subset，需要 same-subset controls。

## 项目特有术语
- **Stage 5A**: RadioML2016.10A full fixed-split 三种子训练矩阵，覆盖 9 个模型行。
- **Stage 5B**: 对 Stage 5A 结果的 artifact audit、aggregate table 和统计检验准备。
- **Stage 6B**: 后续 diagnostic/smoke screening queue；当前已有 smoke 不能纳入 Stage 5A/5B 主表。
- **MCLDNN negative evidence**: MCLDNN seeds `2025` 和 `3407` 的 chance-level 结果，保留为负证据而不是删除。
- **Prediction archive**: `paper_package/predictions_archive_20260508`，包含 27 个 prediction files，覆盖 9 models x 3 seeds。
- **Weight archive gap**: 27 个服务器 Stage 5A `best_model.pt` 仍未完整同步到本地。
