# Stage 2.2：RadioML2016.10A full baseline/full ablation

## 1. 阶段定位

Stage 2.2 将 Stage 1.6/2.1 的真实 subset 结果推进到 RadioML2016.10A full 数据集。目标是补齐结课报告中必须区分于 subset 的正式 full baseline，并验证主要 I/Q + STFT 融合模型在 full 数据上的表现。

本阶段仍然不进入 RadioML2018.01A，不引入 Transformer 或复杂注意力机制。

## 2. 实验环境

- 服务器：GPUShare Linux 实例
- GPU：NVIDIA GeForce RTX 4070 12GB
- Python：3.11.12
- PyTorch：2.9.1+cu128
- CUDA available：True
- 数据目录：`/hy-tmp/radioml-amc-stage1/data/raw/radioml2016/RML2016.10a_dict.pkl`

## 3. 数据检查

执行命令：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
```

检查结果：

- 样本数：220000
- shape：`[220000, 2, 128]`
- 类别数：11
- SNR 数：20
- SNR 范围：`-20` 到 `18`
- 每个 modulation × SNR：1000 条
- NaN/Inf：无

## 4. 实验配置

统一设置：

- 数据集：RadioML2016.10A full
- split：`stratified_by_mod_snr`
- train/val/test：154000 / 22000 / 44000
- seed：42
- batch size：256
- optimizer：AdamW
- learning rate：0.001
- weight decay：0.0001
- device：cuda

baseline 配置：

- `configs/stage1_rml2016a_real_full.yaml`
- epochs：30
- early stopping patience：8

Stage 2 配置：

- `configs/stage2_rml2016a_real_full.yaml`
- epochs：20
- early stopping patience：6
- STFT：`nperseg=32`、`noverlap=16`
- CWT：on-the-fly，full 三视图在本服务器上被标记为 optional skipped

## 5. 执行命令

```bash
pytest -q
python -m compileall -q src scripts
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml

python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml

python scripts/run_stage2_ablations.py \
  --config configs/stage2_rml2016a_real_full.yaml \
  --models fusion_iq_stft \
  --output runs/stage2_2_full_fusion_iq_stft

python scripts/compare_runs.py \
  --run_dirs runs/20260507_192755_cnn1d runs/20260507_193019_resnet1d runs/20260507_193548_fusion_iq_stft \
  --output runs/stage2_2_full_ablation_comparison
```

## 6. run_dir 列表

| 模型 | 输入视图 | run_dir |
|---|---|---|
| CNN1D | I/Q | `runs/20260507_192755_cnn1d/` |
| ResNet1D | I/Q | `runs/20260507_193019_resnet1d/` |
| fusion_iq_stft | I/Q + STFT | `runs/20260507_193548_fusion_iq_stft/` |
| fusion_iq_stft_cwt | I/Q + STFT + CWT | optional skipped |

## 7. 汇总输出

统一汇总目录：

```text
runs/stage2_2_full_ablation_comparison/
```

包含：

- `stage2_2_full_comparison.csv`
- `stage2_2_full_comparison.md`
- `stage2_2_full_summary.json`
- `stage2_2_full_notes.md`

## 8. 指标汇总

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | Train Time (s) | Inference Time (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| CNN1D | I/Q | 0.5855 | 0.2032 | 0.8017 | 0.8790 | 37131 | 133.9510 | 0.5953 |
| ResNet1D | I/Q | 0.5968 | 0.2091 | 0.8155 | 0.8950 | 111755 | 198.1280 | 0.8730 |
| fusion_iq_stft | I/Q + STFT | 0.5782 | 0.2222 | 0.7856 | 0.8455 | 98299 | 326.8360 | 4.0987 |

## 9. 每 SNR accuracy 摘要

CNN1D：

```text
-20=0.0909, -18=0.0982, -16=0.0964, -14=0.1141, -12=0.1309,
-10=0.2214, -8=0.3582, -6=0.5155, -4=0.6282, -2=0.7564,
0=0.8182, 2=0.8627, 4=0.8695, 6=0.8750, 8=0.8814,
10=0.8823, 12=0.8809, 14=0.8705, 16=0.8827, 18=0.8764
```

ResNet1D：

```text
-20=0.0950, -18=0.0945, -16=0.0982, -14=0.1314, -12=0.1618,
-10=0.2355, -8=0.3577, -6=0.4991, -4=0.6277, -2=0.7591,
0=0.8518, 2=0.8732, 4=0.8873, 6=0.8936, 8=0.8927,
10=0.8995, 12=0.8964, 14=0.8873, 16=0.9000, 18=0.8941
```

fusion_iq_stft：

```text
-20=0.0995, -18=0.1005, -16=0.0991, -14=0.1382, -12=0.1791,
-10=0.2659, -8=0.3745, -6=0.5209, -4=0.6550, -2=0.7455,
0=0.8086, 2=0.8282, 4=0.8314, 6=0.8450, 8=0.8450,
10=0.8464, 12=0.8473, 14=0.8450, 16=0.8391, 18=0.8500
```

## 10. 关键图表路径

每个完成 run 均包含：

- `plots/confusion_matrix.png`
- `plots/normalized_confusion_matrix.png`
- `plots/per_class_accuracy.png`
- `plots/accuracy_vs_snr.png`
- `plots/training_curve.png`

示例：

- `runs/20260507_193019_resnet1d/plots/accuracy_vs_snr.png`
- `runs/20260507_193019_resnet1d/plots/confusion_matrix.png`
- `runs/20260507_193548_fusion_iq_stft/plots/accuracy_vs_snr.png`
- `runs/20260507_193548_fusion_iq_stft/plots/confusion_matrix.png`

## 11. 当前结论

- Full 数据上当前最佳 overall accuracy 是 ResNet1D：0.5968。
- `fusion_iq_stft` 的 overall accuracy 为 0.5782，未超过 CNN1D/ResNet1D baseline。
- `fusion_iq_stft` 在 low SNR 分组上为 0.2222，高于 CNN1D 0.2032 和 ResNet1D 0.2091，但 mid/high SNR 明显低于 ResNet1D。
- full 数据的整体准确率显著低于 4 类 subset，原因是 full 任务包含 11 类和更完整低 SNR 范围。
- 低 SNR 结论现在可以基于 full 数据讨论，但应说明当前仅 single-seed。

## 12. CWT optional skipped 说明

`fusion_iq_stft_cwt` 已在 RTX 4070 12GB 上尝试，但在 epoch 1 完成前停止。原因：

- on-the-fly CWT 触发大量 `NNPACK unsupported hardware` 警告；
- 日志在约 5 分钟内膨胀到约 480MB；
- GPU 利用率接近 0%，瓶颈明显在 CPU/CWT 特征计算；
- 继续运行不具备性价比。

该项记录为 optional skipped，不作为失败模型结果。后续如需 full CWT/三视图，应先降低 CWT 计算成本、抑制 warning flood、降低 batch/features，或迁移到更强 CPU/GPU 服务器。

## 13. 风险与限制

- 当前 full 结果为 single-seed，没有多 seed 置信区间。
- RTX 4070 12GB 可以完成 baseline 和 STFT 融合，但不适合当前实现下的 full CWT 三视图。
- 融合模型尚未超过 I/Q ResNet baseline，后续需要改进融合策略或训练协议后再讨论方法收益。
- 当前没有 RadioML2018.01A 结果。

## 14. 是否可以进入下一阶段

可以进入 Stage 3：低 SNR 鲁棒性与消融分析。

建议 Stage 3 先围绕 RadioML2016.10A full 数据完成：

1. 低 SNR 分段报告和图表；
2. 针对 low SNR 的训练采样/加权策略；
3. 对 ResNet1D 与 `fusion_iq_stft` 的 error analysis；
4. 视资源决定是否重试优化后的 CWT。
