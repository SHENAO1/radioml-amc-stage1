# 实验记录表

| 实验ID | 日期 | 阶段 | 数据模式 | 数据集 | 配置文件 | 模型 | run_dir | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | 备注 |
|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---|
| EXP-S1-MOCK-CNN1D-001 | 2026-05-07 | Stage 1 | mock | mock_radioml | `configs/stage1_local_mock.yaml` | CNN1D | `runs/20260507_120214_cnn1d/` | 0.2427 | N/A | N/A | N/A | mock smoke test，不能作为正式结果 |
| EXP-S1-MOCK-RESNET1D-001 | 2026-05-07 | Stage 1 | mock | mock_radioml | `configs/stage1_local_mock.yaml` | ResNet1D | `runs/20260507_120227_resnet1d/` | 0.2621 | N/A | N/A | N/A | mock smoke test，不能作为正式结果 |
| EXP-S1-MOCK-EVAL-CNN1D-001 | 2026-05-07 | Stage 1 | mock | mock_radioml | `configs/stage1_local_mock.yaml` | CNN1D eval | `runs/20260507_120242_eval_cnn1d/` | 0.2427 | N/A | N/A | N/A | mock checkpoint evaluation smoke test，不能作为正式结果 |
| EXP-S15-MOCK-CNN1D-SMOKE-001 | 2026-05-07 | Stage 1.5 | mock | mock_radioml | `configs/stage1_local_mock.yaml` | CNN1D | `runs/20260507_123742_cnn1d/` | 0.2427 | 0.2069 | 0.2708 | 0.2308 | Stage 1.5 输出结构 smoke test，不能作为正式结果 |
| EXP-S15-MOCK-RESNET1D-SMOKE-001 | 2026-05-07 | Stage 1.5 | mock | mock_radioml | `configs/stage1_local_mock.yaml` | ResNet1D | `runs/20260507_123758_resnet1d/` | 0.2621 | 0.2414 | 0.2917 | 0.2308 | Stage 1.5 输出结构 smoke test，不能作为正式结果 |
| EXP-S15-REAL-PENDING-001 | 2026-05-07 | Stage 1.5 | real | RadioML2016.10A | `configs/stage1_rml2016a_real_subset.yaml` | CNN1D/ResNet1D | N/A | N/A | N/A | N/A | N/A | pending：未检测到真实数据，等待放置数据后运行 subset baseline |
| S16-PENDING-REAL | 2026-05-07 | Stage 1.6 | real | RadioML2016.10A | `configs/stage1_rml2016a_real_subset.yaml` | CNN1D/ResNet1D | N/A | N/A | N/A | N/A | N/A | 历史 pending 记录；已由 S16-REAL-SUBSET-CNN1D-001 和 S16-REAL-SUBSET-RESNET1D-001 补充真实结果 |
| S16-REAL-SUBSET-CNN1D-001 | 2026-05-07 | Stage 1.6 | real subset | RadioML2016.10A | `configs/stage1_rml2016a_real_subset.yaml` | CNN1D | `runs/20260507_153710_cnn1d/` | 0.8461 | N/A | 0.8300 | 0.8729 | subset：4 类、8 个 SNR、每组 200 条；low SNR N/A，因为 subset 不含 `SNR <= -6` |
| S16-REAL-SUBSET-RESNET1D-001 | 2026-05-07 | Stage 1.6 | real subset | RadioML2016.10A | `configs/stage1_rml2016a_real_subset.yaml` | ResNet1D | `runs/20260507_153719_resnet1d/` | 0.9070 | N/A | 0.8775 | 0.9563 | subset：4 类、8 个 SNR、每组 200 条；full baseline pending |
| S2-MOCK-FUSION-IQ-STFT-CWT-SMOKE-001 | 2026-05-07 | Stage 2 | mock | mock_radioml | `configs/stage2_ablation_mock.yaml` | fusion_iq_stft_cwt | `runs/20260507_161030_fusion_iq_stft_cwt/` | 0.2308 | 0.1250 | 0.2000 | 0.3750 | mock smoke test，验证 I/Q+STFT+CWT 多视图链路，不能作为正式结果 |
| S2-REAL-SUBSET-TFCNN-STFT-001 | 2026-05-07 | Stage 2 | real subset | RadioML2016.10A | `configs/stage2_ablation_real_subset.yaml` | tfcnn_stft | `runs/20260507_161048_tfcnn_stft/` | 0.4047 | N/A | 0.4788 | 0.2812 | 真实 subset 1 epoch 工程闭环；不能和 5-epoch Stage 1.6 baseline 做正式优劣结论 |

说明：mock 实验只用于验证工程链路，不代表真实 RadioML2016.10A 性能。真实 subset/full 实验完成后，应新增记录并填写 low/mid/high SNR accuracy、run_dir 和备注。
