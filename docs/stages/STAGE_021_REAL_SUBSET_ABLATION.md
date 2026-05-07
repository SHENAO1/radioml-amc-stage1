# Stage 2.1：RadioML2016.10A 真实 subset 完整消融实验

## 1. 阶段定位

Stage 2.1 把 Stage 2 已完成的 STFT/CWT、多视图 Dataset、TF-CNN 和融合模型工程，推进到可比较、可复现、可写进结课报告的真实 RadioML2016.10A subset 消融结果。

本阶段仍然是 subset 实验，不是 full dataset 结果。服务器 full baseline/full ablation 需要进入 Stage 2.2。

## 2. 本阶段目标

- 固定 Stage 2 subset 消融配置。
- 在真实 RadioML2016.10A subset 上完成主要模型消融。
- 保证模型使用一致数据子集、split、seed、epoch、batch size 和评价指标。
- 生成统一 comparison 目录。
- 将 Stage 1.6 CNN1D/ResNet1D baseline 纳入对照。
- 更新阶段文档、实验日志和下一阶段提示词。

## 3. 本阶段不做什么

- 不删除已有 `runs/`。
- 不把 `data/raw/`、`runs/`、checkpoint 加入 Git。
- 不把 subset 结果写成 full dataset 结果。
- 不进入 RadioML2018.01A。
- 不引入 Transformer 或复杂注意力机制。
- 不离线保存全量 STFT/CWT 图片。

## 4. 实验配置

数据配置复用 Stage 1.6 真实 subset：

- 数据集：RadioML2016.10A
- subset：4 类、8 个 SNR、每个 modulation × SNR 200 条
- 类别：`BPSK`、`QPSK`、`8PSK`、`QAM16`
- SNR：`-2`、`0`、`2`、`4`、`6`、`8`、`10`、`12`
- 样本数：6400
- split：`stratified_by_mod_snr`
- train/val/test：0.7/0.1/0.2
- seed：42
- epochs：5
- batch size：128
- optimizer：AdamW
- learning rate：0.001
- weight decay：0.0001
- device：CPU

说明：当前 subset 不包含 `SNR <= -6`，因此 low SNR accuracy 为 N/A，不能据此分析低 SNR 鲁棒性。

## 5. 模型列表

| 模型 | 输入视图 | 状态 | 说明 |
|---|---|---|---|
| CNN1D | I/Q | Done | Stage 1.6 baseline，纳入对照 |
| ResNet1D | I/Q | Done | Stage 1.6 baseline，纳入对照 |
| tfcnn_stft | STFT | Done | 单时频分支 |
| tfcnn_cwt | CWT | Done | 单时频分支，CWT 使用 8 scales 控制 CPU 成本 |
| fusion_iq_stft | I/Q + STFT | Done | 双分支融合 |
| fusion_iq_amp_phase | I/Q + amplitude/phase | Done | 双分支融合，本阶段补齐轻量 on-the-fly amp/phase view |
| fusion_iq_stft_cwt | I/Q + STFT + CWT | Done | 三视图融合，CPU 耗时最高 |

## 6. 本阶段新增/复用文件

新增/修改：

- `configs/stage2_ablation_real_subset.yaml`：固定 Stage 2.1 消融模型、5 epochs、seed 42、batch 128。
- `scripts/make_stage2_1_comparison.py`：生成 Stage 2.1 专用 csv/md/json/notes。
- `src/radioml_amc/features/time_frequency.py`：新增 `compute_amplitude_phase_tensor`。
- `src/radioml_amc/data/dataset.py`：新增 `amp_phase` view。
- `src/radioml_amc/models/multiview.py`：融合模型支持 `amp_phase` 1D 分支。
- `src/radioml_amc/training/trainer.py`：新增模型别名和 `fusion_iq_amp_phase` 路由。
- `tests/test_stage2_features.py`
- `tests/test_stage2_models.py`

复用：

- `scripts/run_stage2_ablations.py`
- `scripts/compare_runs.py`
- `runs/20260507_153710_cnn1d/`
- `runs/20260507_153719_resnet1d/`

## 7. 执行命令

```bash
pytest -q
python -m compileall -q src scripts
python scripts/make_stage2_1_comparison.py --help
python scripts/run_stage2_ablations.py --config configs/stage2_ablation_real_subset.yaml
python scripts/make_stage2_1_comparison.py --run_dirs runs/20260507_153710_cnn1d runs/20260507_153719_resnet1d runs/20260507_164216_tfcnn_stft runs/20260507_164238_tfcnn_cwt runs/20260507_164433_fusion_iq_stft runs/20260507_164503_fusion_iq_amp_phase runs/20260507_164537_fusion_iq_stft_cwt --output runs/stage2_1_real_subset_ablation_comparison
```

## 8. run_dir 列表

| 模型 | run_dir |
|---|---|
| CNN1D | `runs/20260507_153710_cnn1d/` |
| ResNet1D | `runs/20260507_153719_resnet1d/` |
| tfcnn_stft | `runs/20260507_164216_tfcnn_stft/` |
| tfcnn_cwt | `runs/20260507_164238_tfcnn_cwt/` |
| fusion_iq_stft | `runs/20260507_164433_fusion_iq_stft/` |
| fusion_iq_amp_phase | `runs/20260507_164503_fusion_iq_amp_phase/` |
| fusion_iq_stft_cwt | `runs/20260507_164537_fusion_iq_stft_cwt/` |

## 9. 汇总输出

统一汇总目录：

```text
runs/stage2_1_real_subset_ablation_comparison/
```

包含：

- `stage2_1_ablation_comparison.csv`
- `stage2_1_ablation_comparison.md`
- `stage2_1_ablation_summary.json`
- `stage2_1_ablation_notes.md`

Stage 2-only 中间 comparison：

- `runs/stage2_1_real_subset_stage2_only/baseline_comparison.csv`
- `runs/stage2_1_real_subset_stage2_only/baseline_comparison.md`

## 10. 指标汇总

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | Train Time (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| CNN1D | I/Q | 0.8461 | N/A | 0.8300 | 0.8729 | 36228 | 2.5738 |
| ResNet1D | I/Q | 0.9070 | N/A | 0.8775 | 0.9563 | 110852 | 26.4653 |
| tfcnn_stft | STFT | 0.5961 | N/A | 0.6125 | 0.5687 | 23668 | 13.0773 |
| tfcnn_cwt | CWT | 0.6539 | N/A | 0.6850 | 0.6021 | 23668 | 103.8558 |
| fusion_iq_stft | I/Q + STFT | 0.8320 | N/A | 0.8200 | 0.8521 | 96948 | 22.7529 |
| fusion_iq_amp_phase | I/Q + amp/phase | 0.8086 | N/A | 0.7863 | 0.8458 | 138244 | 26.4587 |
| fusion_iq_stft_cwt | I/Q + STFT + CWT | 0.8328 | N/A | 0.8187 | 0.8562 | 149348 | 155.5534 |

每 SNR accuracy 摘要：

- CNN1D：`-2=0.7313`、`0=0.8250`、`2=0.8563`、`4=0.8500`、`6=0.8875`、`8=0.8875`、`10=0.8688`、`12=0.8625`
- ResNet1D：`-2=0.7125`、`0=0.7875`、`2=0.9438`、`4=0.9813`、`6=0.9625`、`8=0.9563`、`10=0.9688`、`12=0.9438`
- tfcnn_stft：`-2=0.5813`、`0=0.6000`、`2=0.6125`、`4=0.6313`、`6=0.6375`、`8=0.6188`、`10=0.5563`、`12=0.5313`
- tfcnn_cwt：`-2=0.6750`、`0=0.7313`、`2=0.7000`、`4=0.6375`、`6=0.6813`、`8=0.6500`、`10=0.6000`、`12=0.5563`
- fusion_iq_stft：`-2=0.7188`、`0=0.8000`、`2=0.8563`、`4=0.8250`、`6=0.9000`、`8=0.8563`、`10=0.8625`、`12=0.8375`
- fusion_iq_amp_phase：`-2=0.7000`、`0=0.7750`、`2=0.8000`、`4=0.8063`、`6=0.8500`、`8=0.8375`、`10=0.8688`、`12=0.8313`
- fusion_iq_stft_cwt：`-2=0.7188`、`0=0.8375`、`2=0.8438`、`4=0.8250`、`6=0.8688`、`8=0.8688`、`10=0.8625`、`12=0.8375`

## 11. 关键图表路径

每个 run 均包含：

- `plots/confusion_matrix.png`
- `plots/normalized_confusion_matrix.png`
- `plots/per_class_accuracy.png`
- `plots/accuracy_vs_snr.png`
- `plots/training_curve.png`

示例：

- `runs/20260507_164537_fusion_iq_stft_cwt/plots/accuracy_vs_snr.png`
- `runs/20260507_164537_fusion_iq_stft_cwt/plots/confusion_matrix.png`
- `runs/20260507_153719_resnet1d/plots/accuracy_vs_snr.png`
- `runs/20260507_153719_resnet1d/plots/confusion_matrix.png`

## 12. 当前结论

- 当前 subset 上最佳 overall accuracy 仍是 Stage 1.6 ResNet1D：0.9070。
- Stage 2.1 融合模型中最佳是 `fusion_iq_stft_cwt`：0.8328，略高于 `fusion_iq_stft` 的 0.8320，但显著增加 CPU 训练/推理耗时。
- 单时频分支明显弱于 I/Q baseline：`tfcnn_stft=0.5961`，`tfcnn_cwt=0.6539`。
- `fusion_iq_stft` 与 `fusion_iq_stft_cwt` 未超过 CNN1D baseline 0.8461，更未超过 ResNet1D baseline 0.9070。
- 当前结果可以写入结课报告的 subset 消融部分，但必须标注 single-seed、real subset 和 low SNR N/A。

## 13. 风险与限制

- 结果仍是 RadioML2016.10A subset，不是 full dataset。
- 当前是 single-seed 结果，没有多 seed 置信区间。
- subset 不含 `SNR <= -6`，不能支撑低 SNR 鲁棒性结论。
- CWT 和三视图融合 CPU 耗时较高，full dataset 建议在 GPU 服务器运行。
- 现有融合是简单 CNN branch concat，不含注意力；这符合本阶段限制，但表达能力有限。

## 14. 是否可以进入下一阶段

可以进入 Stage 2.2：服务器 RadioML2016.10A full baseline/full ablation。

不建议直接进入 RadioML2018.01A。正式报告和论文前应先补：

1. RadioML2016.10A full baseline；
2. full 上至少 `ResNet1D`、`fusion_iq_stft`、`fusion_iq_stft_cwt` 的对比；
3. 如果资源允许，对最佳 2 个模型做多 seed。

## 15. 下一阶段建议

- Stage 2.2：在 GPU 服务器上执行 full baseline/full ablation。
- Stage 3：完成 low SNR 鲁棒性分析与增强策略。
- RadioML2018.01A 留到 Stage 4。
