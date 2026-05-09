# Stage 3.5：文献调研、工作量表达与创新点规划

## 1. 本阶段目标

Stage 3.5 的目标不是继续增加复杂模型，而是把当前已经完成的 RadioML2016.10A 工程、实验和分析整理成结课报告中可说明“工作量”和“创新点”的材料。

本阶段输出主要服务于两件事：

- 在报告中形成清晰的相关工作脉络；
- 为后续 Stage 3.1 低 SNR 轻量改进实验或 Stage 5.0 结课报告初稿提供依据。

当前项目已经具备的事实基础：

- Stage 1 到 Stage 3 已完成 mock、subset、full、时频融合和低 SNR 分析闭环；
- RadioML2016.10A full 上 ResNet1D 是 overall 最佳模型；
- `fusion_iq_stft` 没有超过 ResNet1D overall，但 low SNR 略高；
- CWT full on-the-fly 训练在 RTX 4070 12GB 上成本过高，已记录为 optional skipped；
- 当前不能宣称融合模型全面优于 baseline，也不能宣称完成 RadioML2018.01A。

## 2. 相关工作主线

建议将相关工作和项目贡献整理为 4 条主线：

| 主线 | 说明 | 与本项目对应 |
|---|---|---|
| I/Q baseline | 直接使用 I/Q 时域序列的 CNN、ResNet、CLDNN 等方法 | CNN1D、ResNet1D、subset/full baseline |
| 时频/多视图 | STFT、CWT、幅相、星座图等多表示融合 | STFT/CWT on-the-fly、多视图 Dataset、TF-CNN、fusion 模型 |
| 低 SNR 鲁棒性 | 噪声条件下的分类稳定性、采样策略和损失设计 | Stage 3 low SNR analysis、Stage 3.1 weighted loss / sampler |
| 轻量化与可复现工程 | 参数量、训练耗时、推理耗时、配置化实验和可复现文档 | configs、scripts、runs comparison、docs 阶段体系 |

## 3. 30 篇 arXiv 论文与可借鉴点

这些论文用于构建结课报告的相关工作和方法依据，不表示本项目已经逐篇复现。

| # | 论文 | 可借鉴点 |
|---:|---|---|
| 1 | [Convolutional Radio Modulation Recognition Networks](https://arxiv.org/abs/1602.04105) | RadioML 与 CNN baseline 起点 |
| 2 | [Deep Neural Network Architectures for Modulation Classification](https://arxiv.org/abs/1712.00443) | CNN、LSTM、CLDNN baseline 体系 |
| 3 | [Fast Deep Learning for Automatic Modulation Classification](https://arxiv.org/abs/1901.05850) | 快速模型、采样长度和效率分析 |
| 4 | [Sequential Convolutional Recurrent Neural Networks for Fast AMC](https://arxiv.org/abs/1909.03050) | CNN + RNN 对照思路 |
| 5 | [Automatic Modulation Classification with Deep Neural Networks](https://arxiv.org/abs/2301.11773) | 系统消融和实验报告范式 |
| 6 | [A Novel Automatic Modulation Classification Scheme Based on Multi-Scale Networks](https://arxiv.org/abs/2105.15037) | 多尺度 CNN |
| 7 | [Deep Multi-Scale Representation Learning with Attention for AMC](https://arxiv.org/abs/2209.03764) | 多尺度和通道重标定思路 |
| 8 | [AMC-Net](https://arxiv.org/abs/2304.00445) | 专用 AMC 网络结构 |
| 9 | [Automatic Modulation Classification Using Involution Enabled Residual Networks](https://arxiv.org/abs/2108.10001) | ResNet 类结构改进 |
| 10 | [Ultra Lite CNN for Fast AMC](https://arxiv.org/abs/2208.04659) | 轻量 CNN 与效率权衡 |
| 11 | [MAMCA](https://arxiv.org/abs/2405.11263) | accuracy / efficiency 权衡 |
| 12 | [Automatic Modulation Classification via Green Machine Learning](https://arxiv.org/abs/2604.10317) | 绿色学习与可解释约束 |
| 13 | [G-AMC](https://arxiv.org/abs/2604.06402) | 轻量绿色 AMC |
| 14 | [Polar Feature Based Deep Architectures for AMC](https://arxiv.org/abs/1810.02027) | 极坐标、幅度和相位特征 |
| 15 | [High-Capacity Complex CNNs for I/Q](https://arxiv.org/abs/2010.10717) | 复值网络和 I/Q 表示 |
| 16 | [Learning Constellation Map with Deep CNN for AMC](https://arxiv.org/abs/2009.02026) | 星座图表示 |
| 17 | [Fully Dense Neural Network for Automatic Modulation Recognition](https://arxiv.org/abs/1912.03449) | 非 CNN 对照 |
| 18 | [Efficient AMR Based on Parameter Estimation and Transformation](https://arxiv.org/abs/2110.04980) | 参数估计结合深度学习 |
| 19 | [Learning Time-Frequency Attention Mechanism for AMR](https://arxiv.org/abs/2111.03258) | 时频特征用于 AMR 的依据 |
| 20 | [Time-Frequency Analysis Based Blind Modulation Classification](https://arxiv.org/abs/2004.00378) | 时频分析依据 |
| 21 | [Augmenting Radio Signals with Wavelet Transform](https://arxiv.org/abs/2311.03761) | 小波增强和 CWT 方向 |
| 22 | [Adaptive Fusion Network for Automatic Modulation Recognition](https://arxiv.org/abs/2203.03140) | 多特征融合 |
| 23 | [Data-and-Knowledge Dual-Driven AMR](https://arxiv.org/abs/2206.15035) | 数据驱动与专家知识结合 |
| 24 | [Transfer Learning Guided Noise Reduction for Radio Modulation Classification](https://arxiv.org/abs/2411.08376) | 低 SNR 去噪方向 |
| 25 | [Deep Domain-Adversarial Adaptation for AMC under Channel Variability](https://arxiv.org/abs/2508.06829) | 信道泛化 |
| 26 | [Uncertainty Quantification for Deep Learning Based AMC](https://arxiv.org/abs/2503.04142) | 置信度和可靠性分析 |
| 27 | [Open Set Modulation Recognition](https://arxiv.org/abs/2002.12037) | 开集识别 |
| 28 | [Open Set Wireless Signal Classification](https://arxiv.org/abs/2302.03749) | 专家特征和 open-set 设置 |
| 29 | [Deep Transfer Clustering of Radio Signals](https://arxiv.org/abs/2107.12237) | 少标签和迁移学习 |
| 30 | [Data Augmentation for Deep Learning Based Radio Modulation Classification](https://arxiv.org/abs/1912.03026) | 数据增强 |

## 4. 相关 GitHub 仓库

这些仓库用于对照工程组织、baseline 选择和报告相关工作，不应直接复制其代码到本项目。

| 仓库 | 可借鉴点 |
|---|---|
| [caharper/Automatic-Modulation-Classification-with-Deep-Neural-Networks](https://github.com/caharper/Automatic-Modulation-Classification-with-Deep-Neural-Networks) | 系统消融和 RadioML2018 实验组织 |
| [radioML/examples](https://github.com/radioML/examples) | 官方示例、VTCNN2 风格 baseline |
| [radioML/dataset](https://github.com/radioML/dataset) | GNU Radio 数据生成思路 |
| [brysef/rfml](https://github.com/brysef/rfml) | PyTorch RFML 工具链 |
| [Richardzhangxx/AMR-Benchmark](https://github.com/Richardzhangxx/AMR-Benchmark) | AMR baseline benchmark |
| [wzjialang/MCLDNN](https://github.com/wzjialang/MCLDNN) | 多通道时序融合 |
| [Patrick-Nick/CDSCNN](https://github.com/Patrick-Nick/CDSCNN) | 复值轻量 CNN |
| [BeechburgPieStar/ULCNN](https://github.com/BeechburgPieStar/ULCNN) | ultra-lite CNN |
| [kwyoke/RF_modulation_classification](https://github.com/kwyoke/RF_modulation_classification) | I/Q、幅相和星座图实验 |
| [KristynaPijackova/Radio-Modulation-Recognition-Networks](https://github.com/KristynaPijackova/Radio-Modulation-Recognition-Networks) | CNN、CLDNN、Transformer 对比 |
| [Singingkettle/ChangShuoRadioData](https://github.com/Singingkettle/ChangShuoRadioData) | joint detection + AMC 任务 |
| [cheeseBG/meta-transformer-amc](https://github.com/cheeseBG/meta-transformer-amc) | 少样本和可扩展 AMC，当前只作相关工作引用 |

## 5. 推荐创新点

### 5.1 低 SNR 专项训练策略

这是当前最推荐的新增工作量。Stage 3 已经发现：

- `fusion_iq_stft` 相比 ResNet1D：low SNR +0.0131；
- `fusion_iq_stft` 相比 ResNet1D：overall -0.0186。

后续可做：

- low-SNR weighted loss；
- SNR-balanced sampler；
- 在 ResNet1D 和 `fusion_iq_stft` 上做最小对照；
- 指标关注 low SNR 是否提升，以及 overall 是否严重下降。

该方向与当前证据链最贴合，适合作为 Stage 3.1。

### 5.2 Prediction-level 误差分析

Stage 3 已明确当前 run 未保存 sample-level predictions，因此无法直接生成 low-SNR-only confusion matrix。建议新增轻量 evaluate / save_predictions 能力，输出：

- low-SNR-only confusion matrix；
- low-SNR per-class accuracy；
- low SNR 下的主要混淆类别；
- `QAM16` 在 `fusion_iq_stft` 中退化的具体来源。

这比继续加模型更适合结课报告，因为它解释了结果，而不只是堆实验。

### 5.3 成本感知的时频特征分析

项目已经有清晰工程证据：

- STFT 可以 full 训练；
- CWT full on-the-fly 在 RTX 4070 12GB 上 CPU-bound；
- `fusion_iq_stft` 参数量低于 ResNet1D，但训练和推理更慢；
- CWT 暂不纳入 full 主表是合理取舍。

报告中应把这部分写成“工程约束下的可行性研究”，体现训练工程能力。

### 5.4 Subset-to-full generalization gap

已有 subset 和 full 的强对照：

| 模型 | subset overall | full overall | gap |
|---|---:|---:|---:|
| ResNet1D | 0.9070 | 0.5968 | -0.3102 |
| fusion_iq_stft | 0.8320 | 0.5782 | -0.2538 |

这可以支撑报告中的重要论点：subset 结果不能替代 full dataset 结论，尤其不能支撑低 SNR 鲁棒性结论。

### 5.5 多视图输入体系

本项目不仅实现了一个模型，而是形成了可配置多视图实验框架：

- I/Q；
- STFT；
- CWT；
- amplitude / phase；
- I/Q + STFT；
- I/Q + amplitude / phase；
- I/Q + STFT + CWT。

报告中应强调这是“实验框架”和“消融体系”，不是单个模型的孤立实现。

## 6. 不建议现在做的方向

| 方向 | 原因 |
|---|---|
| Transformer / 大模型 | 与当前阶段限制冲突，课程项目成本高，且不能直接解释已有 Stage 3 现象 |
| RF-GPT 类方法 | 偏离当前 RadioML2016.10A 消融闭环 |
| 强跑 full CWT | 已有证据显示当前服务器成本不划算 |
| 立即进入 RadioML2018.01A | 会稀释当前 RadioML2016.10A 的完整叙事 |
| 宣称融合全面优于 baseline | Stage 2.2 full 结果不支持 |

## 7. 结课报告中的工作量表达

建议把工作量写成 6 块：

1. 工程复现闭环：mock、subset、full、GitHub、docs、configs、runs。
2. Baseline 复现：CNN1D、ResNet1D，subset + full。
3. 时频特征工程：STFT/CWT on-the-fly，不离线保存全量图片。
4. 多视图融合实验：I/Q、STFT、CWT、amp/phase 与融合。
5. Full dataset 实验：RadioML2016.10A，220000 samples、11 类、20 SNR。
6. 低 SNR 专项分析：融合不是 overall 最优，但 STFT 对 low SNR 有补充价值。

报告中可以使用的谨慎表述：

- “本文构建了一个可配置的 RadioML2016.10A AMC 实验框架，覆盖 I/Q baseline、时频特征、多视图融合和低 SNR 分析。”
- “在 RadioML2016.10A full 数据上，ResNet1D 获得当前最高 overall accuracy。”
- “I/Q + STFT 融合模型在 low SNR 分组上略优于 I/Q baseline，提示时频特征可能具有低 SNR 补充价值。”
- “CWT on-the-fly full 训练受计算成本限制，本文将其作为可行性分析而非主表结论。”

不应写：

- “融合模型全面优于 baseline。”
- “本文已完成 RadioML2018.01A 验证。”
- “本文方法达到 SOTA。”
- “CWT full 消融已完成。”

## 8. 下一步建议

优先路线：

1. Stage 3.1：实现 low-SNR weighted loss 或 SNR-balanced sampler。
2. Stage 3.1 同步补充 evaluate/save_predictions，用于 low-SNR-only confusion matrix。
3. 如果课程时间紧，直接进入 Stage 5.0 结课报告初稿，把 Stage 3.1 写成可选增强实验。

当前不建议进入 Stage 4 RadioML2018.01A，除非 RadioML2016.10A 报告主线已经完整。

