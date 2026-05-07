# Stage 2：STFT/CWT 时频分支与 I/Q 多视图融合

## 1. 阶段定位

Stage 2 在 Stage 1.6 真实 RadioML2016.10A subset baseline 之后，补充 STFT/CWT on-the-fly 特征、时频 CNN 分支和 I/Q 多视图融合模型。当前阶段是工程开发和最小真实闭环验证，不替代服务器 full baseline。

## 2. 阶段目标

- 新增 STFT/CWT on-the-fly 特征接口，不离线保存全量图片。
- 新增时频 CNN 分支，支持 STFT-only 和 CWT-only。
- 新增 I/Q + STFT、I/Q + CWT、I/Q + STFT + CWT 多视图融合模型。
- 保留 CNN1D 和 ResNet1D baseline，不破坏 Stage 1.6 命令。
- 新增 Stage 2 mock、real subset、real full 和 ablation 配置。
- 新增 `scripts/run_stage2_ablations.py` 批量运行消融实验。
- 输出 overall、per-SNR、low/mid/high SNR、per-class、confusion matrix、normalized_confusion_matrix、模型复杂度和训练耗时。

## 3. 本阶段不做什么

- 不自动下载大数据集。
- 不把 RadioML 数据、`runs/` 或 checkpoint 加入 Git。
- 不离线保存全量 STFT/CWT 图片。
- 不引入 Transformer 或复杂注意力机制。
- 不用 mock 结果冒充真实结果。

## 4. 输入条件

- Stage 1.6 真实 subset baseline 已完成。
- 本地存在 `data/raw/radioml2016/RML2016.10a_dict.pkl`。
- full baseline 尚未训练，论文正式实验前仍需补齐。
- 本地运行环境为 CPU；Stage 2 full 或完整消融建议在 GPU 服务器执行。

## 5. 已完成工作

| 任务 | 状态 | 说明 | 相关文件 |
|---|---|---|---|
| STFT on-the-fly | Done | `SignalDataset.__getitem__` 即时计算 STFT tensor `[1,F,T]` | `src/radioml_amc/features/time_frequency.py`, `src/radioml_amc/data/dataset.py` |
| CWT on-the-fly | Done | 使用轻量 Ricker CWT 即时计算 `[1,scales,L]` | `src/radioml_amc/features/time_frequency.py` |
| 多视图 dataset | Done | I/Q only 返回 tensor；多视图返回 dict，不预生成图片数据集 | `src/radioml_amc/data/dataset.py` |
| 时频 CNN | Done | 支持 `tfcnn_stft`、`tfcnn_cwt` | `src/radioml_amc/models/multiview.py` |
| 多视图融合 | Done | 支持 `fusion_iq_stft`、`fusion_iq_cwt`、`fusion_iq_stft_cwt` | `src/radioml_amc/models/multiview.py` |
| 训练器兼容 | Done | batch 可为 tensor 或 view dict；metrics 增加 feature/model_complexity | `src/radioml_amc/training/trainer.py` |
| Stage 2 配置 | Done | 新增 mock、real subset、real full、ablation 配置 | `configs/stage2_*.yaml` |
| Stage 2 消融脚本 | Done | 可按模型列表批量训练并生成 comparison | `scripts/run_stage2_ablations.py` |
| mock smoke | Done | `fusion_iq_stft_cwt` 一轮跑通 | `runs/20260507_161030_fusion_iq_stft_cwt/` |
| real subset 最小闭环 | Done | `tfcnn_stft` 一轮跑通 | `runs/20260507_161048_tfcnn_stft/` |

## 6. 修改/新增文件

- `src/radioml_amc/features/time_frequency.py`：新增 torch STFT/CWT tensor 接口。
- `src/radioml_amc/data/dataset.py`：新增多视图 on-the-fly dataset 逻辑。
- `src/radioml_amc/models/multiview.py`：新增时频 CNN 和融合模型。
- `src/radioml_amc/models/__init__.py`、`src/radioml_amc/features/__init__.py`：导出 Stage 2 接口。
- `src/radioml_amc/training/trainer.py`：支持多视图 batch、Stage 2 模型构建和复杂度记录。
- `configs/stage2_local_mock.yaml`
- `configs/stage2_rml2016a_real_subset.yaml`
- `configs/stage2_rml2016a_real_full.yaml`
- `configs/stage2_ablation_mock.yaml`
- `configs/stage2_ablation_real_subset.yaml`
- `scripts/run_stage2_ablations.py`
- `tests/test_stage2_features.py`
- `tests/test_stage2_models.py`

## 7. 执行命令

```bash
pytest -q
python scripts/run_stage2_ablations.py --config configs/stage2_ablation_mock.yaml --models fusion_iq_stft_cwt --output runs/stage2_mock_smoke_ablation
python scripts/run_stage2_ablations.py --config configs/stage2_ablation_real_subset.yaml
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/compare_runs.py --run_dirs runs/20260507_153710_cnn1d runs/20260507_153719_resnet1d --output runs/stage2_stage1_6_regression_comparison
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

## 8. 输出结果

- mock Stage 2 run: `runs/20260507_161030_fusion_iq_stft_cwt/`
- mock comparison: `runs/stage2_mock_smoke_ablation/baseline_comparison.md`
- real Stage 2 run: `runs/20260507_161048_tfcnn_stft/`
- real comparison: `runs/stage2_real_subset_ablation/baseline_comparison.md`
- Stage 1.6 regression visualization: `runs/20260507_161117_visualize_examples/`
- Stage 1.6 regression comparison: `runs/stage2_stage1_6_regression_comparison/baseline_comparison.md`
- Stage 1.6 regression baseline rerun:
  - `runs/20260507_161134_cnn1d/`
  - `runs/20260507_161144_resnet1d/`
  - `runs/20260507_161154_stage1_5_comparison/`

## 9. 实验摘要

Stage 1.6 真实 subset baseline 保持一致：

| 模型 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | 备注 |
|---|---:|---:|---:|---:|---:|---|
| CNN1D | 0.8461 | N/A | 0.8300 | 0.8729 | 36228 | Stage 1.6 baseline；5 epochs |
| ResNet1D | 0.9070 | N/A | 0.8775 | 0.9563 | 110852 | Stage 1.6 baseline；5 epochs |

Stage 2 新增结果：

| 模型 | 数据 | Views | Epochs | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | 备注 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| fusion_iq_stft_cwt | mock | I/Q + STFT + CWT | 1 | 0.2308 | 0.1250 | 0.2000 | 0.3750 | 149348 | mock smoke test，不能作为正式实验结论 |
| tfcnn_stft | real subset | STFT | 1 | 0.4047 | N/A | 0.4788 | 0.2812 | 23668 | 真实数据工程闭环；仅 1 epoch，不能和 5-epoch baseline 做正式优劣结论 |

`tfcnn_stft` 每 SNR 准确率：

- `-2=0.3563`、`0=0.6000`、`2=0.6500`、`4=0.4875`、`6=0.3000`、`8=0.3063`、`10=0.2750`、`12=0.2625`

`tfcnn_stft` 每类准确率：

- `8PSK=0.3031`、`BPSK=0.4125`、`QAM16=0.8719`、`QPSK=0.0313`

## 10. 当前问题与风险

- full baseline 尚未训练，论文正式实验前仍需补齐。
- 当前 Stage 2 真实结果只跑了 `tfcnn_stft` 一轮，是工程闭环证据，不是正式消融结论。
- CWT 和多视图融合已实现并通过 mock smoke，但真实 subset/full 完整消融尚未执行。
- 本地 CPU 环境运行可行，但 full 数据和完整 ablation 建议迁移到 GPU 服务器。
- 当前 subset 不包含 `SNR <= -6`，low SNR accuracy 仍为 N/A。
- NumPy 2.4 对 pickle load 触发 `VisibleDeprecationWarning`，不影响当前读取结果，但后续可单独清理 warning。

## 11. 验收标准核对

| 验收项 | 状态 | 证据 |
|---|---|---|
| Stage 1.6 `check_dataset` 可运行 | Done | 输出 6400 samples、4 类、8 个 SNR、无 NaN/Inf |
| Stage 1.6 `visualize_examples` 可运行 | Done | `runs/20260507_161117_visualize_examples/` |
| Stage 1.6 `run_stage1_5_baselines` 可运行 | Done | `runs/20260507_161134_cnn1d/`、`runs/20260507_161144_resnet1d/` |
| Stage 1.6 `compare_runs` 可运行 | Done | `runs/stage2_stage1_6_regression_comparison/` |
| STFT/CWT on-the-fly | Done | dataset 在 `__getitem__` 计算，未生成全量图片数据集 |
| mock smoke test | Done | `fusion_iq_stft_cwt` run 已生成 |
| real subset Stage 2 闭环 | Done | `tfcnn_stft` run 已生成 |
| 指标输出完整 | Done | `metrics.json` 含 overall、per-SNR、SNR groups、per-class、confusion、normalized_confusion、params、耗时 |
| docs 更新 | Done | 本文档、阶段索引、进展日志、实验日志、下一阶段提示词 |
| 不引入 Transformer/注意力 | Done | 当前模型为 CNN 分支和 concat late fusion |

## 12. 下一阶段计划

- 在服务器补齐 Stage 1.6 full baseline。
- 在真实 subset 上执行完整 Stage 2 消融：`tfcnn_stft`、`tfcnn_cwt`、`fusion_iq_stft`、`fusion_iq_cwt`、`fusion_iq_stft_cwt`。
- 完成后再迁移到 full 数据，生成正式论文表格。
- Stage 3 再围绕低 SNR 做鲁棒性和增强实验。

## 13. 下一阶段提示词

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 训练工程师。

请按 durable context 规则先读取 docs/PROGRESS_LOG.md、docs/STAGE_INDEX.md、docs/stages/STAGE_02_TIME_FREQUENCY_MULTIVIEW.md、docs/EXPERIMENT_LOG.md，并读取 Stage 2 run evidence：
- runs/20260507_161048_tfcnn_stft/metrics.json
- runs/stage2_real_subset_ablation/baseline_comparison.md
- runs/20260507_161030_fusion_iq_stft_cwt/metrics.json

当前状态：
- Stage 1.6 真实 subset baseline 已完成：CNN1D Acc 0.8461，ResNet1D Acc 0.9070。
- full baseline 尚未训练，论文正式实验前仍需补齐。
- Stage 2 工程已完成：on-the-fly STFT/CWT、多视图 dataset、时频 CNN、I/Q+STFT、I/Q+CWT、I/Q+STFT+CWT 融合模型、configs/stage2_* 和 scripts/run_stage2_ablations.py。
- mock smoke 已跑通：fusion_iq_stft_cwt Acc 0.2308，仅工程验证。
- real subset 最小闭环已跑通：tfcnn_stft 1 epoch Acc 0.4047，仅工程闭环，不是正式消融结论。

下一步请做 Stage 2 正式消融准备：
1. 先不要改动 Stage 1.6 baseline 命令。
2. 在真实 subset 上运行完整 Stage 2 消融模型列表：tfcnn_stft、tfcnn_cwt、fusion_iq_stft、fusion_iq_cwt、fusion_iq_stft_cwt。
3. 对齐训练 epoch、batch、seed 和 split，生成 comparison。
4. 记录 EXPERIMENT_LOG，明确 mock、1-epoch smoke 和正式 subset 消融的区别。
5. full baseline 和 full Stage 2 消融建议迁移到 GPU 服务器。
```
