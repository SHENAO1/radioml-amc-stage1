# Stage 3：低 SNR 鲁棒性分析、结果解释与轻量改进准备

## 1. 本阶段目标

Stage 3 不继续盲目增加模型，而是把 Stage 2.2 的 RadioML2016.10A full 实验结果转化为结课报告可用的分析结论，并判断是否需要后续低 SNR 改进实验。

核心问题：

- ResNet1D 是否仍是 full dataset 的整体最优模型；
- `fusion_iq_stft` 是否在低 SNR 区间有补充价值；
- 这种补充价值是否足以支持强结论；
- CWT full 实验是否适合纳入主表；
- 下一步应优先改训练策略、数据采样，还是模型结构。

## 2. 输入结果来源

Stage 3 分析使用 Stage 2.2 已同步到本地的 full run：

| 模型 | run_dir |
|---|---|
| CNN1D | `runs/20260507_192755_cnn1d/` |
| ResNet1D | `runs/20260507_193019_resnet1d/` |
| fusion_iq_stft | `runs/20260507_193548_fusion_iq_stft/` |

统一 comparison：

```text
runs/stage2_2_full_ablation_comparison/stage2_2_full_comparison.md
runs/stage2_2_full_ablation_comparison/stage2_2_full_comparison.csv
```

Stage 3 分析输出：

```text
runs/stage3_low_snr_analysis/
```

包含：

- `stage3_low_snr_summary.csv`
- `stage3_low_snr_summary.md`
- `stage3_low_snr_summary.json`
- `per_snr_accuracy_comparison.png`
- `low_mid_high_accuracy_bar.png`
- `overall_vs_low_snr_tradeoff.png`
- `per_class_accuracy_comparison.png`
- `stage3_low_snr_findings.md`

## 3. Stage 2.2 full 结果复述

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---|---:|---:|---:|---:|
| CNN1D | I/Q | 0.5855 | 0.2032 | 0.8017 | 0.8790 |
| ResNet1D | I/Q | 0.5968 | 0.2091 | 0.8155 | 0.8950 |
| fusion_iq_stft | I/Q + STFT | 0.5782 | 0.2222 | 0.7856 | 0.8455 |

结论：

- Overall 最佳：ResNet1D，0.5968。
- Low SNR 最佳：`fusion_iq_stft`，0.2222。
- `fusion_iq_stft` 相比 ResNet1D 的 low SNR 提升：+0.0131，即 +1.31 percentage points。
- `fusion_iq_stft` 相比 ResNet1D 的 overall 下降：-0.0186，即 -1.86 percentage points。

## 4. Low SNR 分析

当前 full 数据包含 `SNR <= -6`，因此 low SNR accuracy 可以正式用于分析。

`fusion_iq_stft` 在 low SNR 上高于两个 I/Q baseline：

- 相比 CNN1D：+0.0190，即 +1.90 pp；
- 相比 ResNet1D：+0.0131，即 +1.31 pp。

这说明 STFT 分支在噪声较强时可能提供了 I/Q 序列以外的补充结构信息。但该提升幅度较小，并且只有 single-seed，因此只能作为弱证据，不能作为“融合模型全面更强”的结论。

## 5. Per-SNR 曲线分析

`fusion_iq_stft` 相比 ResNet1D 的主要增益集中在低 SNR 到过渡 SNR 区间：

| SNR | fusion_iq_stft - ResNet1D |
|---:|---:|
| -10 | +0.0305 |
| -4 | +0.0273 |
| -6 | +0.0218 |
| -12 | +0.0173 |
| -8 | +0.0168 |

在 0 dB 及更高 SNR 上，ResNet1D 明显更稳。`fusion_iq_stft` 的 mid-SNR delta 为 -0.0298，high-SNR delta 为 -0.0495。这表明当前融合模型更像是牺牲中高 SNR 表现换取低 SNR 小幅收益，而不是整体提升。

关键图：

- `runs/stage3_low_snr_analysis/per_snr_accuracy_comparison.png`
- `runs/stage3_low_snr_analysis/low_mid_high_accuracy_bar.png`
- `runs/stage3_low_snr_analysis/overall_vs_low_snr_tradeoff.png`

## 6. Per-class / confusion 分析

已有 `metrics.json` 包含 full-test-set 的 per-class accuracy 和 full-test confusion matrix，但没有保存 sample-level predictions。因此：

- 可以分析 overall per-class 差异；
- 可以使用已有 overall confusion matrix 作为全测试集参考；
- 不能直接生成 low-SNR-only confusion matrix；
- 低 SNR confusion matrix 需要重新 evaluate checkpoint 并保存 predictions 后生成。

`fusion_iq_stft` 相比 ResNet1D 的 per-class overall 差异：

| Class | fusion_iq_stft | ResNet1D | Delta |
|---|---:|---:|---:|
| WBFM | 0.2555 | 0.1815 | +0.0740 |
| QPSK | 0.5933 | 0.5280 | +0.0653 |
| GFSK | 0.6522 | 0.6230 | +0.0292 |
| PAM4 | 0.7040 | 0.6825 | +0.0215 |
| AM-SSB | 0.8778 | 0.8722 | +0.0055 |
| 8PSK | 0.5423 | 0.5387 | +0.0035 |
| CPFSK | 0.6228 | 0.6295 | -0.0067 |
| AM-DSB | 0.7075 | 0.7218 | -0.0142 |
| QAM64 | 0.6312 | 0.6552 | -0.0240 |
| BPSK | 0.6052 | 0.6302 | -0.0250 |
| QAM16 | 0.1685 | 0.5020 | -0.3335 |

时频融合对 `WBFM`、`QPSK`、`GFSK`、`PAM4` 更友好，但对 `QAM16` 伤害非常明显。低 SNR 下的具体混淆类别仍需 prediction-level 文件支持。

## 7. Complexity / accuracy trade-off

| 模型 | Params | Train Time (s) | Inference Time (s) | Overall Acc | Low SNR Acc |
|---|---:|---:|---:|---:|---:|
| CNN1D | 37131 | 133.9510 | 0.5953 | 0.5855 | 0.2032 |
| ResNet1D | 111755 | 198.1280 | 0.8730 | 0.5968 | 0.2091 |
| fusion_iq_stft | 98299 | 326.8360 | 4.0987 | 0.5782 | 0.2222 |

`fusion_iq_stft` 参数量低于 ResNet1D，但训练和推理时间更高，主要因为 STFT 是 on-the-fly 计算。当前版本在低 SNR 上有小幅收益，但整体性价比不如 ResNet1D 稳定。

## 8. CWT skipped 的合理性说明

`fusion_iq_stft_cwt` 在 RTX 4070 12GB 上尝试后停止，原因：

- full on-the-fly CWT 明显 CPU-bound；
- 约 5 分钟未完成第 1 个 epoch；
- `NNPACK unsupported hardware` warning 大量刷屏；
- 日志增长到约 480MB；
- GPU 利用率接近 0%。

因此 CWT full 不适合纳入当前 full 主表。把它记录为 optional skipped 比报告一个不完整或不稳定结果更严谨。

## 9. 可以写入结课报告的结论

可以写：

- RadioML2016.10A full 上，ResNet1D 是当前 overall 最优 baseline。
- I/Q + STFT 融合没有提升 overall accuracy。
- I/Q + STFT 融合在 low SNR 分组上比 I/Q baseline 略高，提示时频特征可能对低 SNR 样本有补充价值。
- 当前结果支持“低 SNR 方向值得继续研究”的弱结论。
- CWT full 因计算成本过高，暂不纳入主表。

## 10. 当前不能写入结课报告的过强结论

不能写：

- 融合模型全面优于 baseline。
- CWT 模型已完成 full 消融。
- 本项目已验证 RadioML2018.01A。
- 方法达到 SOTA。
- 时频融合在所有 SNR、所有类别上都有效。
- single-seed 结果具有稳定统计显著性。

## 11. 后续 Stage 3.1 / Stage 3.2 建议

优先级建议：

1. Stage 3.1：low-SNR weighted loss 或 SNR-balanced sampler 小规模改进实验。
2. 重新 evaluate 已有 checkpoint 并保存 predictions，生成 low-SNR-only confusion matrix。
3. 对 `QAM16` 退化进行误差分析，判断是否是 STFT branch、融合策略或训练协议导致。
4. 如需重试 CWT，先降低 CWT scales 或增加缓存/警告抑制，不要直接强跑 full 三视图。

优先优化方向：先做数据采样/训练策略，再考虑模型结构。当前模型结构已经能暴露低 SNR 现象，继续堆复杂模型的证据不足。

## 12. 是否建议进入报告写作阶段

建议可以进入 Stage 5.0 结课报告初稿，因为已有：

- mock 工程闭环；
- real subset baseline；
- real subset Stage 2 消融；
- real full baseline；
- real full STFT 融合；
- low SNR 分析；
- CWT skipped 的合理解释。

如果希望报告中的“低 SNR 改进”更有说服力，可以先做 Stage 3.1 的小规模 weighted loss / SNR-balanced sampler 实验。
