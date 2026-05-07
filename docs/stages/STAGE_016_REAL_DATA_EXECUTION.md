# Stage 1.6：真实 RadioML2016.10A 数据接入与 baseline 执行

## 1. 阶段定位

Stage 1.6 位于 Stage 1.5 和 Stage 2 之间，用于把真实 RadioML2016.10A 数据下载、接入、subset baseline 验证和服务器 full baseline 准备补齐。它仍然属于 baseline 阶段，不是 Stage 2。

本阶段的核心判断是：真实数据链路和 CNN1D/ResNet1D baseline 是否已经可以作为后续 STFT/CWT 与多视图融合实验的可靠对照。

## 2. 阶段目标

- 检查当前工程状态，确认 Stage 1 和 Stage 1.5 未被破坏。
- 检查真实 RadioML2016.10A 是否已经放入 `data/raw/` 或 `data/raw/radioml2016/`。
- 完成真实 RadioML2016.10A subset 数据检查、样本可视化、CNN1D/ResNet1D baseline 和 comparison。
- 明确服务器 full baseline 的执行步骤、输出文件和进入 Stage 2 的前置条件。

## 3. 本阶段不做什么

- 不实现 STFT/CWT 训练分支。
- 不实现 I/Q + 时频多视图融合模型。
- 不实现 Transformer。
- 不实现注意力机制。
- 不完整处理 RadioML2018.01A。
- 不自动把所有样本转成 STFT 图片。
- 不把数据集、checkpoint 或 `runs/` 加入 Git。
- 不用 mock 数据结果冒充真实结果。

## 4. 输入条件

- 已完成 Stage 1：本地 mock 工程闭环。
- 已完成 Stage 1.5：真实数据 baseline 工程接口与 docs 文档体系。
- 已下载 RadioML2016.10A 数据文件。
- 需要本地或服务器 Python 环境。
- full baseline 建议使用具备足够磁盘空间和 GPU 的 Linux 服务器。

## 5. 当前数据状态

状态：Subset Done, Full Pending。

2026-05-07 已检测到真实 RadioML2016.10A：

```text
data/raw/radioml2016/RML2016.10a_dict.pkl
```

subset 配置数据摘要：

- 数据模式：real
- 数据集：RadioML2016.10A
- 样本数：6400
- X shape：`[6400, 2, 128]`
- dtype：`float32`
- NaN：false
- Inf：false
- modulation 类别：`8PSK`、`BPSK`、`QAM16`、`QPSK`
- SNR：`-2`、`0`、`2`、`4`、`6`、`8`、`10`、`12`
- 每类样本数：1600
- 每个 SNR 样本数：800
- 每个 modulation × SNR 样本数：200

说明：当前 subset 不包含 `SNR <= -6` 的样本，因此 low SNR accuracy 为 N/A。后续 full baseline 会覆盖完整 SNR 范围。

## 6. 执行命令

本次已执行：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/compare_runs.py --run_dirs runs/20260507_153710_cnn1d runs/20260507_153719_resnet1d --output runs/stage1_6_real_subset_comparison
pytest -q
```

服务器 full baseline 推荐命令：

```bash
git clone <your-repo-url>
cd radioml-amc-stage1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/check_storage.sh
bash scripts/download_radioml_kaggle.sh
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml
```

服务器建议使用 `tmux`，数据集建议直接在服务器下载，不建议从本地上传大数据。运行前检查：

```bash
df -h
nvidia-smi
python - <<'PY'
import torch
print("cuda_available:", torch.cuda.is_available())
print("device_count:", torch.cuda.device_count())
PY
```

## 7. 输出结果

- visualization run: `runs/20260507_153454_visualize_examples/`
- CNN1D run_dir: `runs/20260507_153710_cnn1d/`
- ResNet1D run_dir: `runs/20260507_153719_resnet1d/`
- baseline comparison: `runs/stage1_6_real_subset_comparison/baseline_comparison.md`
- baseline comparison CSV: `runs/stage1_6_real_subset_comparison/baseline_comparison.csv`

两个训练 run 均生成：

- `metrics.json`
- `metrics.csv`
- `dataset_summary.json`
- `split_summary.json`
- `best_model.pt`
- `stage1_5_report.md`
- `plots/confusion_matrix.png`
- `plots/normalized_confusion_matrix.png`
- `plots/accuracy_vs_snr.png`
- `plots/per_class_accuracy.png`
- `plots/training_curve.png`

## 8. 实验摘要

| 模型 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | 备注 |
|---|---:|---:|---:|---:|---:|---|
| CNN1D | 0.8461 | N/A | 0.8300 | 0.8729 | 36228 | real subset；low SNR N/A，因为 subset 不含 `SNR <= -6` |
| ResNet1D | 0.9070 | N/A | 0.8775 | 0.9563 | 110852 | real subset；low SNR N/A，因为 subset 不含 `SNR <= -6` |

每类准确率摘要：

- CNN1D：`8PSK=0.8406`、`BPSK=0.9750`、`QAM16=0.9313`、`QPSK=0.6375`
- ResNet1D：`8PSK=0.8094`、`BPSK=0.9969`、`QAM16=0.9594`、`QPSK=0.8625`

每 SNR 准确率摘要：

- CNN1D：`-2=0.7313`、`0=0.8250`、`2=0.8563`、`4=0.8500`、`6=0.8875`、`8=0.8875`、`10=0.8688`、`12=0.8625`
- ResNet1D：`-2=0.7125`、`0=0.7875`、`2=0.9438`、`4=0.9813`、`6=0.9625`、`8=0.9563`、`10=0.9688`、`12=0.9438`

## 9. 当前问题与风险

- 当前只完成真实 subset baseline，服务器 full baseline 尚未执行。
- 本地环境未检测到 CUDA，subset baseline 使用 CPU 运行。
- subset 不包含 `SNR <= -6`，低 SNR 表现仍需 full baseline 或扩展 subset 验证。
- full baseline 耗时和显存需求需要在服务器上确认。
- 当前真实 subset 指标可以作为工程进入 Stage 2 的依据，但论文正式对比仍应补齐 full baseline。

## 10. 验收标准核对

| 验收项 | 状态 | 证据 |
|---|---|---|
| pytest 通过 | Done | `pytest -q` 输出 `.s......... [100%]` |
| 真实 subset `check_dataset` 通过 | Done | `num_samples=6400`、`shape=[6400,2,128]`、无 NaN/Inf |
| 真实 subset 可视化通过 | Done | `runs/20260507_153454_visualize_examples/plots/` |
| CNN1D 真实 subset 训练完成 | Done | `runs/20260507_153710_cnn1d/` |
| ResNet1D 真实 subset 训练完成 | Done | `runs/20260507_153719_resnet1d/` |
| baseline_comparison.md 已生成 | Done | `runs/stage1_6_real_subset_comparison/baseline_comparison.md` |
| baseline_comparison.csv 已生成 | Done | `runs/stage1_6_real_subset_comparison/baseline_comparison.csv` |
| accuracy_vs_snr.png 已生成 | Done | 两个训练 run 的 `plots/accuracy_vs_snr.png` |
| confusion_matrix.png 已生成 | Done | 两个训练 run 的 `plots/confusion_matrix.png` |
| normalized_confusion_matrix.png 已生成 | Done | 两个训练 run 的 `plots/normalized_confusion_matrix.png` |
| per_class_accuracy.png 已生成 | Done | 两个训练 run 的 `plots/per_class_accuracy.png` |
| README 数据下载说明完整 | Done | `README.md` 已补充 Kaggle token、Windows/Linux、subset/full 命令 |
| 下载脚本说明完整 | Done | `scripts/download_radioml_kaggle.sh` 已增强为说明型脚本 |
| STAGE_INDEX 已更新 | Done | Stage 1.6 状态为 Partial Done |
| PROGRESS_LOG 已追加 | Done | 2026-05-07 Stage 1.6 subset 完成记录 |
| EXPERIMENT_LOG 已记录真实 subset | Done | 已记录 CNN1D 和 ResNet1D 两条真实 subset 实验 |
| NEXT_STAGE_PROMPTS 已更新 | Done | 已说明 subset done、full pending 时的 Stage 2 条件 |
| 没有删除既有 runs | Done | 本阶段未删除 `runs/` |
| 没有把数据或 checkpoint 加入 Git | Done | `data/raw/` 和 `runs/` 仍被 `.gitignore` 忽略 |
| 服务器 full baseline 完成 | Pending | 等待服务器执行 |

## 11. 是否可以进入 Stage 2

可以进入 Stage 2 的工程开发，但论文实验仍需补齐服务器 full baseline。

当前已满足：

1. 已完成真实 RadioML2016.10A subset baseline。
2. `baseline_comparison.md` 已生成。
3. `baseline_comparison.csv` 已生成。
4. `accuracy_vs_snr.png` 已生成。
5. `docs/EXPERIMENT_LOG.md` 已记录真实 subset 实验。
6. mock 结果不再作为主要依据。

尚未满足：

- 真实 full baseline 尚未完成。
- 完整低 SNR 结果尚未形成。

## 12. 下一阶段计划

Stage 2 将在真实 subset baseline 的基础上做 STFT/CWT on-the-fly 特征、时频 CNN 分支和 I/Q + 时频多视图融合。Stage 2 仍应保留 CNN1D/ResNet1D baseline，并继续更新 `docs/`。

论文实验主线仍需在服务器补跑 full baseline，再做正式消融和论文表格。

## 13. 下一阶段提示词

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 训练工程师。

在进入 Stage 2 前，请先按 AGENTS.md 的 durable context 规则读取 docs/session_state.md、docs/progress.md 或 docs/PROGRESS_LOG.md，并读取 docs/stages/STAGE_016_REAL_DATA_EXECUTION.md、docs/EXPERIMENT_LOG.md 和真实 run_dir 中的 metrics.json/baseline_comparison.md。不要依赖聊天历史。

当前 Stage 1.6 已完成真实 RadioML2016.10A subset baseline：
- CNN1D run_dir: runs/20260507_153710_cnn1d/
- ResNet1D run_dir: runs/20260507_153719_resnet1d/
- comparison: runs/stage1_6_real_subset_comparison/
- CNN1D overall accuracy: 0.8461
- ResNet1D overall accuracy: 0.9070
- low SNR accuracy: N/A，因为 subset 不含 SNR <= -6

可以进入 Stage 2 的工程开发，但论文实验仍需补齐服务器 full baseline。Stage 2 的所有对比必须基于真实 baseline 结果，不能用 mock smoke test 作为正式依据。

Stage 2 目标：
1. 新增 STFT/CWT on-the-fly 特征接口，不离线保存全量 STFT/CWT 图片。
2. 新增时频 CNN 分支。
3. 新增 I/Q + STFT、I/Q + CWT、I/Q + STFT + CWT 多视图融合模型。
4. 保留 CNN1D 和 ResNet1D baseline，不破坏 Stage 1.6 数据接入和 baseline 命令。
5. 新增 mock、real subset、real full 和 ablation 配置。
6. 新增消融脚本和对比报告，输出 overall、per-SNR、low/mid/high SNR、per-class、混淆矩阵、归一化混淆矩阵和复杂度统计。
7. 继续更新 docs/STAGE_INDEX.md、docs/PROGRESS_LOG.md、docs/EXPERIMENT_LOG.md、docs/NEXT_STAGE_PROMPTS.md 和新的 Stage 2 过程文档。
```
