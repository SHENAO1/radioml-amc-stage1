# Stage 1.6：真实 RadioML2016.10A 数据接入与 baseline 执行

## 1. 阶段定位

Stage 1.6 位于 Stage 1.5 和 Stage 2 之间，用于把真实 RadioML2016.10A 数据下载、接入、subset baseline 验证和服务器 full baseline 准备补齐。它仍然属于 baseline 阶段，不是 Stage 2。

本阶段的核心判断是：真实数据链路和 CNN1D/ResNet1D baseline 是否已经可以作为后续 STFT/CWT 与多视图融合实验的可靠对照。

## 2. 阶段目标

- 检查当前工程状态，确认 Stage 1 和 Stage 1.5 未被破坏。
- 检查真实 RadioML2016.10A 是否已经放入 `data/raw/` 或 `data/raw/radioml2016/`。
- 无真实数据时完善下载说明、服务器执行说明和过程文档。
- 有真实数据时执行 `check_dataset`、样本可视化、CNN1D/ResNet1D subset baseline 和 baseline 对比。
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
- 需要 RadioML2016.10A 数据文件。
- 需要本地或服务器 Python 环境。
- full baseline 建议使用具备足够磁盘空间和 GPU 的 Linux 服务器。

## 5. 当前数据状态

状态：Need Data。

2026-05-07 检查以下路径，均未检测到真实 RadioML2016.10A：

```text
data/raw/RML2016.10a_dict.pkl
data/raw/RML2016.10a_dict.pkl.bz2
data/raw/radioml2016/RML2016.10a_dict.pkl
data/raw/radioml2016/RML2016.10a_dict.pkl.bz2
```

`python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml` 已给出清晰缺失提示，不会因为缺少真实数据导致测试失败。

## 6. 执行命令

本次已执行：

```bash
pytest -q
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
```

真实数据放置后，本地 subset 验证命令：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/compare_runs.py --run_dirs runs/xxx_cnn1d runs/yyy_resnet1d --output runs/stage1_6_real_subset_comparison
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

当前真实数据缺失，真实 run 尚未生成。

- run_dir: Pending
- baseline comparison: Pending
- plots: Pending
- reports: Pending

真实 subset 完成后应记录：

- CNN1D run_dir
- ResNet1D run_dir
- `runs/stage1_6_real_subset_comparison/baseline_comparison.md`
- `runs/stage1_6_real_subset_comparison/baseline_comparison.csv`
- `confusion_matrix.png`
- `normalized_confusion_matrix.png`
- `accuracy_vs_snr.png`
- `per_class_accuracy.png`
- `stage1_5_report.md` 或 `stage1_6_report.md`

## 8. 实验摘要

当前真实数据缺失，真实实验摘要为 Pending。

- CNN1D overall accuracy: Pending
- ResNet1D overall accuracy: Pending
- Low SNR accuracy: Pending
- Mid SNR accuracy: Pending
- High SNR accuracy: Pending
- 每类准确率摘要: Pending
- 备注: subset/full 均未执行；已有 mock 结果仅为 smoke test。

## 9. 当前问题与风险

- 真实 RadioML2016.10A 尚未放置。
- 真实 subset baseline 尚未执行。
- 服务器 full baseline 尚未执行。
- 低 SNR 表现未知。
- Kaggle API token 和服务器磁盘/GPU 环境尚未验证。

## 10. 验收标准核对

| 验收项 | 状态 | 证据 |
|---|---|---|
| pytest 通过 | Done | `pytest -q` 输出 `.s......... [100%]` |
| 缺真实数据时 `check_dataset` 给出清晰提示 | Done | real subset check 打印四个候选路径和“不自动下载大数据集”说明 |
| README 数据下载说明完整 | Done | `README.md` 已补充 Kaggle token、Windows/Linux、subset/full 命令 |
| 下载脚本说明完整 | Done | `scripts/download_radioml_kaggle.sh` 已增强为说明型脚本 |
| Stage 1.6 过程文档已创建 | Done | `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md` |
| STAGE_INDEX 已更新 | Done | Stage 1.6 状态为 Need Data |
| PROGRESS_LOG 已追加 | Done | 2026-05-07 Stage 1.6 记录 |
| EXPERIMENT_LOG 已记录 pending | Done | `S16-PENDING-REAL` |
| NEXT_STAGE_PROMPTS 已更新 | Done | 已追加 Stage 1.6 -> Stage 2 |
| 没有删除既有 runs | Done | 本阶段未删除 `runs/` |
| 没有把数据或 checkpoint 加入 Git | Done | 未新增数据文件或 checkpoint |
| 真实 subset baseline 完成 | Pending | 等待 RadioML2016.10A |
| 服务器 full baseline 完成 | Pending | 等待服务器执行 |

## 11. 是否可以进入 Stage 2

当前不建议直接进入 Stage 2。

进入 Stage 2 的条件：

1. 至少完成真实 RadioML2016.10A subset baseline。
2. 最好完成真实 full baseline。
3. `baseline_comparison.md` 已生成。
4. `accuracy_vs_snr.png` 已生成。
5. `docs/EXPERIMENT_LOG.md` 已记录真实实验。
6. mock 结果不再作为主要依据。

如果只完成真实 subset baseline、full 尚未完成，可以进入 Stage 2 的工程开发，但论文实验仍需补齐 full baseline。

## 12. 下一阶段计划

Stage 2 将在真实 baseline 的基础上做 STFT/CWT on-the-fly 特征、时频 CNN 分支和 I/Q + 时频多视图融合。Stage 2 仍应保留 CNN1D/ResNet1D baseline，并继续更新 `docs/`。

## 13. 下一阶段提示词

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 训练工程师。

在进入 Stage 2 前，请先按 AGENTS.md 的 durable context 规则读取 docs/session_state.md、docs/progress.md 或 docs/PROGRESS_LOG.md，并读取 docs/stages/STAGE_016_REAL_DATA_EXECUTION.md、docs/EXPERIMENT_LOG.md 和真实 run_dir 中的 metrics.json/baseline_comparison.md。不要依赖聊天历史。

如果 Stage 1.6 仍为 Need Data，先不要实现 STFT/CWT、多视图融合、Transformer 或注意力机制；请先协助接入真实 RadioML2016.10A，并跑通 CNN1D/ResNet1D subset baseline。

如果 Stage 1.6 已完成真实 subset baseline，但 full baseline 未完成，可以进入 Stage 2 的工程开发，但论文实验仍需补齐服务器 full baseline。Stage 2 的所有对比必须基于真实 baseline 结果，不能用 mock smoke test 作为正式依据。

Stage 2 目标：
1. 新增 STFT/CWT on-the-fly 特征接口，不离线保存全量 STFT/CWT 图片。
2. 新增时频 CNN 分支。
3. 新增 I/Q + STFT、I/Q + CWT、I/Q + STFT + CWT 多视图融合模型。
4. 保留 CNN1D 和 ResNet1D baseline，不破坏 Stage 1.6 数据接入和 baseline 命令。
5. 新增 mock、real subset、real full 和 ablation 配置。
6. 新增消融脚本和对比报告，输出 overall、per-SNR、low/mid/high SNR、per-class、混淆矩阵、归一化混淆矩阵和复杂度统计。
7. 继续更新 docs/STAGE_INDEX.md、docs/PROGRESS_LOG.md、docs/EXPERIMENT_LOG.md、docs/NEXT_STAGE_PROMPTS.md 和新的 Stage 2 过程文档。
```
