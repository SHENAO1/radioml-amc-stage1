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
