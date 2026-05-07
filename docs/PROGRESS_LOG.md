# 项目进展日志

## 2026-05-07 Stage 1：本地 mock 工程闭环

### 本次目标

- 完成无真实数据条件下的 RadioML AMC 工程 smoke test。
- 跑通 mock 数据检查、示例可视化、CNN1D/ResNet1D 训练、评估和报告。
- 保证 pytest smoke tests 可运行。

### 本次完成

- mock 数据生成、数据统计、训练、评估、可视化和报告生成闭环已完成。
- CNN1D 和 ResNet1D baseline 均可在 `[N, 2, 128]` I/Q 输入上训练。
- `pytest -q` 输出 `.s... [100%]`，其中 `s` 是真实 RadioML2016.10A 文件不存在时按预期 skip。

### 修改/新增文件

- `src/radioml_amc/data/`
- `src/radioml_amc/models/`
- `src/radioml_amc/training/`
- `src/radioml_amc/visualization/`
- `scripts/`
- `configs/stage1_local_mock.yaml`
- `configs/stage1_rml2016a.yaml`
- `reports/stage1_report_template.md`
- `tests/`

### 执行命令

```bash
python scripts/check_dataset.py --config configs/stage1_local_mock.yaml
python scripts/visualize_examples.py --config configs/stage1_local_mock.yaml
python scripts/train_cnn1d.py --config configs/stage1_local_mock.yaml
python scripts/train_resnet1d.py --config configs/stage1_local_mock.yaml
python scripts/evaluate_model.py --config configs/stage1_local_mock.yaml --checkpoint runs/20260507_120214_cnn1d/best_model.pt
python scripts/make_report.py --run_dir runs/20260507_120214_cnn1d
pytest -q
```

### 输出结果

- run_dir: `runs/20260507_120214_cnn1d/`
- run_dir: `runs/20260507_120227_resnet1d/`
- run_dir: `runs/20260507_120242_eval_cnn1d/`
- run_dir: `runs/20260507_120315_visualize_examples/`
- metrics: mock smoke test 指标已写入对应 `metrics.json`
- plots: 对应 run 的 `plots/`
- report: 对应 run 的 `stage1_report.md`

### 当前问题

- 当前结果全部来自 mock/synthetic 数据，仅用于工程 smoke test。
- 真实 RadioML2016.10A 尚未下载，不能形成正式实验结论。

### 下一步计划

- 进入 Stage 1.5，接入真实 RadioML2016.10A subset/full 配置，固定 CNN1D/ResNet1D baseline 协议。

## 2026-05-07 Stage 1.5：RadioML2016.10A 真实数据 baseline

### 本次目标

- 审计 Stage 1 工程，确认 mock 流程未破坏。
- 新增 docs 过程文档体系。
- 强化 RadioML2016.10A loader 的自动路径检测和 `.pkl/.pkl.bz2` 读取能力。
- 新增真实 subset/full 配置、baseline 批量脚本、run 对比脚本和阶段 1.5 报告。

### 本次完成

- 修改前验证：`pytest -q` 为 `.s... [100%]`。
- 修改前验证：mock `check_dataset` 正常输出 `[512, 2, 128]`、4 类、4 个 SNR。
- 修改前验证：mock `train_cnn1d` 跑通，run_dir 为 `runs/20260507_122235_cnn1d/`。
- 修改后验证：`pytest -q` 为 `.s......... [100%]`。
- 修改后验证：mock `check_dataset` 正常输出 `has_nan=false`、`has_inf=false`、modulation × SNR 统计。
- 修改后验证：mock `train_cnn1d` 跑通，run_dir 为 `runs/20260507_123742_cnn1d/`。
- 修改后验证：mock `train_resnet1d` 跑通，run_dir 为 `runs/20260507_123758_resnet1d/`。
- 修改后验证：`compare_runs.py` 跑通，输出 `runs/stage1_5_mock_comparison/baseline_comparison.md`。
- 未检测到真实 RadioML2016.10A 四个约定路径，真实 baseline 训练当前 pending。

### 修改/新增文件

- `docs/`
- `configs/stage1_rml2016a_real_subset.yaml`
- `configs/stage1_rml2016a_real_full.yaml`
- `scripts/run_stage1_5_baselines.py`
- `scripts/compare_runs.py`
- `src/radioml_amc/data/rml2016a_loader.py`
- `src/radioml_amc/data/split.py`
- `src/radioml_amc/training/metrics.py`
- `src/radioml_amc/training/trainer.py`
- `src/radioml_amc/reporting/`
- `src/radioml_amc/visualization/`
- `README.md`
- `.gitignore`
- `tests/`

### 执行命令

```bash
pytest -q
python scripts/check_dataset.py --config configs/stage1_local_mock.yaml
python scripts/train_cnn1d.py --config configs/stage1_local_mock.yaml
python scripts/train_resnet1d.py --config configs/stage1_local_mock.yaml
python scripts/compare_runs.py --run_dirs runs/20260507_123742_cnn1d runs/20260507_123758_resnet1d --output runs/stage1_5_mock_comparison
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

### 输出结果

- run_dir: `runs/20260507_123742_cnn1d/`
- run_dir: `runs/20260507_123758_resnet1d/`
- comparison: `runs/stage1_5_mock_comparison/baseline_comparison.md`
- metrics: mock smoke test，不能作为正式结果。
- plots: `runs/20260507_123742_cnn1d/plots/`
- report: `runs/20260507_123742_cnn1d/stage1_5_report.md`
- real subset status: 数据缺失，baseline 批量训练未执行。

### 当前问题

- 当前尚未接入真实 RadioML2016.10A 数据，本阶段真实 baseline 训练尚未完成，不能作为正式实验结论。

### 下一步计划

- 放置真实数据到 `data/raw/` 或 `data/raw/radioml2016/` 后，先运行 subset 检查与训练，再在服务器运行 full baseline。

## 2026-05-07 Stage 1.6：真实 RadioML2016.10A 数据接入与 baseline 执行

### 本次目标

- 检查当前工程状态，确认 Stage 1 和 Stage 1.5 未被破坏。
- 检查真实 RadioML2016.10A 是否已经放入约定路径。
- 无真实数据时补齐下载说明、服务器 full baseline 步骤和 Stage 1.6 过程文档。
- 明确进入 Stage 2 的前置条件。

### 本次完成

- 确认当前是 Git 仓库，初始 `git status --short` 无输出。
- 确认 `README.md`、`docs/`、`configs/`、`scripts/`、`runs/` 结构完整。
- 确认四个约定路径均未检测到真实 RadioML2016.10A。
- 执行 `pytest -q`，结果为 `.s......... [100%]`。
- 执行真实 subset `check_dataset`，脚本给出清晰缺失提示并正常返回。
- 增强 `scripts/download_radioml_kaggle.sh` 的 Kaggle token、Windows/Linux、2016/2018 示例和 `check_dataset` 说明。
- 更新 README 的数据下载、放置、本地 subset 和服务器 full baseline 命令。
- 新增 Stage 1.6 过程文档，并更新阶段索引、实验记录和下一阶段提示词。

### 修改/新增文件

- `README.md`
- `scripts/download_radioml_kaggle.sh`
- `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md`
- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`

### 执行命令

```bash
pytest -q
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
```

### 输出结果

- data status: Need Data；真实 RadioML2016.10A 尚未放置。
- run_dir: N/A。
- baseline comparison: N/A。
- report: `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md`。
- docs: `docs/STAGE_INDEX.md`、`docs/PROGRESS_LOG.md`、`docs/EXPERIMENT_LOG.md`、`docs/NEXT_STAGE_PROMPTS.md` 已更新。

### 当前问题

- 真实 RadioML2016.10A 尚未放置，真实 subset/full baseline 尚未执行。
- 服务器 Kaggle token、磁盘空间和 GPU 环境尚未验证。
- 当前 baseline comparison 仍只有 mock smoke test，不是正式实验结果。

### 下一步计划

- 下载 RadioML2016.10A 并放到 `data/raw/` 或 `data/raw/radioml2016/` 的约定路径。
- 先运行 `python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml`。
- 再运行真实 subset 可视化、CNN1D/ResNet1D baseline 和 comparison。
- subset 验证通过后，在服务器执行 full baseline。

## 2026-05-07 Stage 1.6：真实 subset baseline 完成

### 本次目标

- 在真实 RadioML2016.10A 数据已下载后，完成 Stage 1.6 subset baseline 闭环。
- 跑通真实 subset `check_dataset`、可视化、CNN1D/ResNet1D 训练和 baseline comparison。
- 更新 docs 记录真实 subset 结果，并明确 full baseline 仍待服务器执行。

### 本次完成

- 检测到真实数据：`data/raw/radioml2016/RML2016.10a_dict.pkl`。
- 真实 subset 数据检查通过：6400 条样本，4 类，8 个 SNR，每个 modulation × SNR 200 条，shape `[6400, 2, 128]`，dtype `float32`，无 NaN/Inf。
- 真实 subset 可视化生成：`runs/20260507_153454_visualize_examples/`。
- CNN1D 真实 subset 训练完成：`runs/20260507_153710_cnn1d/`。
- ResNet1D 真实 subset 训练完成：`runs/20260507_153719_resnet1d/`。
- 固定名称 comparison 已生成：`runs/stage1_6_real_subset_comparison/`。
- 已更新 Stage 1.6 文档、阶段索引、实验记录和下一阶段提示词。

### 修改/新增文件

- `README.md`
- `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md`
- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`

### 执行命令

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/compare_runs.py --run_dirs runs/20260507_153710_cnn1d runs/20260507_153719_resnet1d --output runs/stage1_6_real_subset_comparison
pytest -q
```

### 输出结果

- data status: real subset done；full pending。
- CNN1D run_dir: `runs/20260507_153710_cnn1d/`
- ResNet1D run_dir: `runs/20260507_153719_resnet1d/`
- baseline comparison: `runs/stage1_6_real_subset_comparison/baseline_comparison.md`
- baseline comparison CSV: `runs/stage1_6_real_subset_comparison/baseline_comparison.csv`
- report: 两个训练 run 均生成 `stage1_5_report.md`
- docs: `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md` 已更新真实 subset 结果

### 实验摘要

- CNN1D overall accuracy: 0.8461
- CNN1D mid/high SNR accuracy: 0.8300 / 0.8729
- ResNet1D overall accuracy: 0.9070
- ResNet1D mid/high SNR accuracy: 0.8775 / 0.9563
- Low SNR accuracy: N/A，因为当前 subset 不含 `SNR <= -6`

### 当前问题

- 本地 PyTorch 未检测到 CUDA，subset baseline 使用 CPU 运行。
- 服务器 full baseline 尚未执行。
- 完整低 SNR 表现仍需 full baseline 或扩展 subset 验证。

### 下一步计划

- 可进入 Stage 2 的工程开发：STFT/CWT on-the-fly 特征和多视图融合。
- 论文实验前仍需在服务器执行 `configs/stage1_rml2016a_real_full.yaml` full baseline。

## 2026-05-07 Stage 2：STFT/CWT 时频分支与多视图融合工程开发

### 本次目标

- 新增 STFT/CWT on-the-fly 特征接口，不离线保存全量图片。
- 新增时频 CNN 分支和 I/Q + STFT、I/Q + CWT、I/Q + STFT + CWT 多视图融合模型。
- 新增 `configs/stage2_*` 配置和 `scripts/run_stage2_ablations.py`。
- 保留 CNN1D/ResNet1D baseline，不破坏 Stage 1.6 命令。
- 跑通 mock smoke 和至少一个真实 subset Stage 2 闭环。

### 本次完成

- `SignalDataset` 已支持按配置返回 I/Q tensor 或多视图 dict。
- STFT/CWT 在 `__getitem__` 中即时计算，没有离线保存全量图片数据集。
- 新增 `tfcnn_stft`、`tfcnn_cwt`、`fusion_iq_stft`、`fusion_iq_cwt`、`fusion_iq_stft_cwt`。
- 训练器已支持 tensor/dict batch，并在 `metrics.json` 记录 `feature_views`、`feature_config` 和 `model_complexity`。
- 新增 Stage 2 mock、real subset、real full 和 ablation 配置。
- 新增 Stage 2 消融批处理脚本。
- `pytest -q` 通过：`.s.............. [100%]`。
- mock smoke 跑通：`fusion_iq_stft_cwt`，run_dir 为 `runs/20260507_161030_fusion_iq_stft_cwt/`。
- real subset 最小闭环跑通：`tfcnn_stft`，run_dir 为 `runs/20260507_161048_tfcnn_stft/`。
- Stage 1.6 回归验证通过：`check_dataset`、`visualize_examples`、`compare_runs`、`run_stage1_5_baselines` 均可运行。

### 修改/新增文件

- `src/radioml_amc/features/time_frequency.py`
- `src/radioml_amc/features/__init__.py`
- `src/radioml_amc/data/dataset.py`
- `src/radioml_amc/models/multiview.py`
- `src/radioml_amc/models/__init__.py`
- `src/radioml_amc/training/trainer.py`
- `configs/stage2_local_mock.yaml`
- `configs/stage2_rml2016a_real_subset.yaml`
- `configs/stage2_rml2016a_real_full.yaml`
- `configs/stage2_ablation_mock.yaml`
- `configs/stage2_ablation_real_subset.yaml`
- `scripts/run_stage2_ablations.py`
- `tests/test_stage2_features.py`
- `tests/test_stage2_models.py`
- `docs/stages/STAGE_02_TIME_FREQUENCY_MULTIVIEW.md`
- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`

### 执行命令

```bash
pytest -q
python scripts/run_stage2_ablations.py --config configs/stage2_ablation_mock.yaml --models fusion_iq_stft_cwt --output runs/stage2_mock_smoke_ablation
python scripts/run_stage2_ablations.py --config configs/stage2_ablation_real_subset.yaml
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/compare_runs.py --run_dirs runs/20260507_153710_cnn1d runs/20260507_153719_resnet1d --output runs/stage2_stage1_6_regression_comparison
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

### 输出结果

- mock Stage 2 run: `runs/20260507_161030_fusion_iq_stft_cwt/`
- mock comparison: `runs/stage2_mock_smoke_ablation/baseline_comparison.md`
- real Stage 2 run: `runs/20260507_161048_tfcnn_stft/`
- real comparison: `runs/stage2_real_subset_ablation/baseline_comparison.md`
- Stage 1.6 regression visualization: `runs/20260507_161117_visualize_examples/`
- Stage 1.6 regression comparison: `runs/stage2_stage1_6_regression_comparison/`
- Stage 1.6 regression baseline rerun: `runs/20260507_161134_cnn1d/`、`runs/20260507_161144_resnet1d/`

### 实验摘要

- mock `fusion_iq_stft_cwt` overall accuracy: 0.2308，仅工程 smoke test，不能作为正式结论。
- real subset `tfcnn_stft` overall accuracy: 0.4047，1 epoch 工程闭环，不能和 5-epoch baseline 做正式优劣结论。
- real subset `tfcnn_stft` mid/high SNR accuracy: 0.4788 / 0.2812。
- real subset `tfcnn_stft` low SNR accuracy: N/A，因为当前 subset 不含 `SNR <= -6`。

### 当前问题

- full baseline 仍未训练。
- Stage 2 完整真实 subset 消融尚未执行。
- CWT 和融合模型真实 subset/full 结果尚未形成。
- full 数据和正式消融建议在 GPU 服务器运行。

### 下一步计划

- 在真实 subset 上运行完整 Stage 2 消融：`tfcnn_stft`、`tfcnn_cwt`、`fusion_iq_stft`、`fusion_iq_cwt`、`fusion_iq_stft_cwt`。
- 补齐服务器 full baseline 后，再执行 full Stage 2 消融。
- 完整低 SNR 结论等待 full 数据或扩展 subset。

## 2026-05-07 Stage 2.1：RadioML2016.10A 真实 subset 完整消融

### 本次目标

- 固定 Stage 2 subset ablation 配置，不再使用 1 epoch 作为正式 subset 结果。
- 在真实 RadioML2016.10A subset 上完成主要时频和多视图模型消融。
- 将 Stage 1.6 CNN1D/ResNet1D baseline 纳入统一对比。
- 生成可复现实验报告所需的 csv、md、json 和 notes。
- 更新 Stage 2.1 文档、阶段索引、进展日志、实验日志和下一阶段提示词。

### 本次完成

- 审查确认现有 `scripts/run_stage2_ablations.py` 可批量训练，但原 `configs/stage2_ablation_real_subset.yaml` 只跑 `tfcnn_stft` 且 1 epoch，不适合作正式消融。
- 新增 `amp_phase` on-the-fly view，并补齐 `fusion_iq_amp_phase` 路由。
- 将 Stage 2.1 消融配置固定为 seed 42、5 epochs、batch size 128、同一真实 subset 和同一分层 split。
- CWT 使用 8 scales，避免 CPU 上成本过高。
- 新增 `scripts/make_stage2_1_comparison.py`，生成 Stage 2.1 专用汇总文件。
- `pytest -q` 通过：`.s................. [100%]`。
- `python -m compileall -q src scripts` 通过。
- 真实 subset Stage 2.1 五个模型均跑通。
- 统一汇总目录已生成：`runs/stage2_1_real_subset_ablation_comparison/`。

### 修改/新增文件

- `configs/stage2_ablation_real_subset.yaml`
- `scripts/make_stage2_1_comparison.py`
- `src/radioml_amc/features/time_frequency.py`
- `src/radioml_amc/features/__init__.py`
- `src/radioml_amc/data/dataset.py`
- `src/radioml_amc/models/multiview.py`
- `src/radioml_amc/training/trainer.py`
- `tests/test_stage2_features.py`
- `tests/test_stage2_models.py`
- `docs/stages/STAGE_021_REAL_SUBSET_ABLATION.md`
- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`

### 执行命令

```bash
pytest -q
python -m compileall -q src scripts
python scripts/make_stage2_1_comparison.py --help
python scripts/run_stage2_ablations.py --config configs/stage2_ablation_real_subset.yaml
python scripts/make_stage2_1_comparison.py --run_dirs runs/20260507_153710_cnn1d runs/20260507_153719_resnet1d runs/20260507_164216_tfcnn_stft runs/20260507_164238_tfcnn_cwt runs/20260507_164433_fusion_iq_stft runs/20260507_164503_fusion_iq_amp_phase runs/20260507_164537_fusion_iq_stft_cwt --output runs/stage2_1_real_subset_ablation_comparison
```

### 输出结果

- `runs/20260507_164216_tfcnn_stft/`
- `runs/20260507_164238_tfcnn_cwt/`
- `runs/20260507_164433_fusion_iq_stft/`
- `runs/20260507_164503_fusion_iq_amp_phase/`
- `runs/20260507_164537_fusion_iq_stft_cwt/`
- `runs/stage2_1_real_subset_stage2_only/baseline_comparison.md`
- `runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_comparison.csv`
- `runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_comparison.md`
- `runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_summary.json`
- `runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_notes.md`

### 实验摘要

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---|---:|---:|---:|---:|
| CNN1D | I/Q | 0.8461 | N/A | 0.8300 | 0.8729 |
| ResNet1D | I/Q | 0.9070 | N/A | 0.8775 | 0.9563 |
| tfcnn_stft | STFT | 0.5961 | N/A | 0.6125 | 0.5687 |
| tfcnn_cwt | CWT | 0.6539 | N/A | 0.6850 | 0.6021 |
| fusion_iq_stft | I/Q + STFT | 0.8320 | N/A | 0.8200 | 0.8521 |
| fusion_iq_amp_phase | I/Q + amp/phase | 0.8086 | N/A | 0.7863 | 0.8458 |
| fusion_iq_stft_cwt | I/Q + STFT + CWT | 0.8328 | N/A | 0.8187 | 0.8562 |

当前 subset 上最佳 overall accuracy 仍是 Stage 1.6 ResNet1D：0.9070。Stage 2.1 中最佳融合模型为 `fusion_iq_stft_cwt`：0.8328。

### 当前问题

- 当前结果是 single-seed real subset，不是 full dataset。
- subset 不含 `SNR <= -6`，low SNR accuracy 为 N/A，不能支撑低 SNR 鲁棒性结论。
- CWT 和三视图融合在 CPU 上训练耗时明显高于 STFT/IQ 融合。
- 融合模型未超过 ResNet1D baseline，后续 full dataset 上需重新验证。

### 下一步计划

- 进入 Stage 2.2：服务器 RadioML2016.10A full baseline/full ablation。
- 优先 full baseline：CNN1D、ResNet1D。
- full ablation 建议优先跑：`fusion_iq_stft`、`fusion_iq_stft_cwt`；资源足够再补 `tfcnn_cwt`。
- Stage 3 再做低 SNR 鲁棒性分析。

## 2026-05-07 Stage 2.2：RadioML2016.10A full baseline/full ablation

### 本次目标

- 在 GPU 服务器上完成 RadioML2016.10A full 数据检查。
- 补齐 full CNN1D/ResNet1D baseline。
- 跑通主要 Stage 2 full 融合模型 `fusion_iq_stft`。
- 生成 full comparison，并同步结果回本地 `runs/`。
- 记录 CWT 三视图在当前服务器上的 optional skipped 原因。

### 本次完成

- 服务器环境验证通过：NVIDIA GeForce RTX 4070、Python 3.11.12、PyTorch 2.9.1+cu128、CUDA available。
- full 数据检查通过：220000 samples、11 类、20 个 SNR、无 NaN/Inf。
- `pytest -q` 通过：`.s................. [100%]`。
- `python -m compileall -q src scripts` 通过。
- full CNN1D baseline 完成。
- full ResNet1D baseline 完成。
- full `fusion_iq_stft` 完成。
- 统一汇总目录已生成并同步回本地：`runs/stage2_2_full_ablation_comparison/`。
- `fusion_iq_stft_cwt` 在 RTX 4070 12GB 上尝试后停止，记录为 optional skipped。

### 执行命令

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml
python scripts/run_stage2_ablations.py --config configs/stage2_rml2016a_real_full.yaml --models fusion_iq_stft --output runs/stage2_2_full_fusion_iq_stft
python scripts/compare_runs.py --run_dirs runs/20260507_192755_cnn1d runs/20260507_193019_resnet1d runs/20260507_193548_fusion_iq_stft --output runs/stage2_2_full_ablation_comparison
```

### 输出结果

- `runs/20260507_192755_cnn1d/`
- `runs/20260507_193019_resnet1d/`
- `runs/20260507_193548_fusion_iq_stft/`
- `runs/stage2_2_full_ablation_comparison/stage2_2_full_comparison.csv`
- `runs/stage2_2_full_ablation_comparison/stage2_2_full_comparison.md`
- `runs/stage2_2_full_ablation_comparison/stage2_2_full_summary.json`
- `runs/stage2_2_full_ablation_comparison/stage2_2_full_notes.md`

### 实验摘要

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---|---:|---:|---:|---:|
| CNN1D | I/Q | 0.5855 | 0.2032 | 0.8017 | 0.8790 |
| ResNet1D | I/Q | 0.5968 | 0.2091 | 0.8155 | 0.8950 |
| fusion_iq_stft | I/Q + STFT | 0.5782 | 0.2222 | 0.7856 | 0.8455 |

当前 full 上最佳 overall accuracy 是 ResNet1D：0.5968。`fusion_iq_stft` 未超过 baseline，但 low SNR 分组略高于 CNN1D/ResNet1D。

### 当前问题

- 当前 full 结果仍是 single-seed。
- full CWT 三视图在 RTX 4070 12GB 上因 CPU-bound CWT 和 NNPACK warning flood 被标记为 optional skipped。
- Stage 2 融合模型未在 overall/mid/high SNR 上超过 ResNet1D。

### 下一步计划

- 进入 Stage 3：基于 full 数据做低 SNR 鲁棒性与误差分析。
- 优先分析 low SNR 下 `fusion_iq_stft` 相对 baseline 的收益和类别混淆。
- 后续如重试 CWT，应先优化 CWT on-the-fly 成本或使用更强服务器。
