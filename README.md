# radioml-amc-stage1

## 1. 项目简介

本项目是机器学习结课作业第一阶段工程：基于 RadioML2016.10A 的无线电自动调制识别 AMC 最小可运行闭环。当前目标是先把本地工程、mock smoke test、训练评估、可视化、报告和服务器衔接流程跑通，后续再扩展到论文级实验。

研究主题：

《基于时频特征与深度神经网络融合的无线电调制识别方法研究——以 RadioML2016.10A 与 RadioML2018.01A 数据集为例》

## 2. 第一阶段目标

- 支持 RadioML2016.10A 数据读取接口；
- 支持无真实数据集时的 mock/synthetic smoke test；
- 提供数据统计、示例可视化、CNN1D 和 ResNet1D baseline；
- 保存训练日志、指标、混淆矩阵、SNR 准确率曲线和阶段报告；
- 保证代码可以后续上传 GitHub，并在服务器上下载数据后继续训练。

## 3. 当前阶段范围限制

本阶段不实现 Transformer、多视图融合、复杂注意力机制或论文创新模型；不完整处理 RadioML2018.01A；不自动下载大数据集；不把数据集或训练输出加入 Git；不把所有样本离线转成时频图图片。

## 4. 环境配置

建议在项目根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 5. 本地无数据集 smoke test 流程

当前没有真实数据集也可以完整跑通工程闭环：

```bash
python scripts/check_dataset.py --config configs/stage1_local_mock.yaml
python scripts/visualize_examples.py --config configs/stage1_local_mock.yaml
python scripts/train_cnn1d.py --config configs/stage1_local_mock.yaml
python scripts/train_resnet1d.py --config configs/stage1_local_mock.yaml
python scripts/make_report.py --run_dir runs/某次运行目录
pytest -q
```

mock 数据只用于检查工程是否可运行，不能作为正式实验结果或论文结论。

## 6. RadioML2016.10A 数据集下载与放置

Stage 1.6 需要真实 RadioML2016.10A 数据后才能执行正式 subset/full baseline。当前项目不会自动下载大数据集，也不会把数据集加入 Git。

请先配置 Kaggle API token：

```bash
pip install kaggle
mkdir -p ~/.kaggle
# 将 kaggle.json 放到 ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

Windows PowerShell：

```powershell
pip install kaggle
New-Item -ItemType Directory -Force $env:USERPROFILE\.kaggle
# 将 kaggle.json 放到 $env:USERPROFILE\.kaggle\kaggle.json
```

不要把 `kaggle.json` 提交到 GitHub。`scripts/download_radioml_kaggle.sh` 会创建约定目录并打印 Kaggle 下载示例，但不会强制下载。

RadioML2016.10A 下载示例：

```bash
bash scripts/download_radioml_kaggle.sh
kaggle datasets download -d nolasthitnotomorrow/radioml2016-deepsigcom -p data/raw/radioml2016 --unzip
```

如果 Kaggle 页面上的 dataset slug 与示例不同，请以 Kaggle 页面实际 slug 为准。Stage 1.6 不需要 RadioML2018.01A；脚本中的 2018 命令只为后续阶段预留。

下载后请检查文件名，并放到以下任一位置：

```text
data/raw/RML2016.10a_dict.pkl
data/raw/RML2016.10a_dict.pkl.bz2
data/raw/radioml2016/RML2016.10a_dict.pkl
data/raw/radioml2016/RML2016.10a_dict.pkl.bz2
```

Linux 服务器可使用软链接：

```bash
ln -s "$(pwd)/data/raw/radioml2016/RML2016.10a_dict.pkl" data/raw/RML2016.10a_dict.pkl
```

Windows PowerShell 可直接移动：

```powershell
Move-Item .\RML2016.10a_dict.pkl .\data\raw\radioml2016\RML2016.10a_dict.pkl
```

真实数据检查和本地 subset baseline：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/compare_runs.py --run_dirs runs/xxx_cnn1d runs/yyy_resnet1d --output runs/stage1_6_real_subset_comparison
```

subset 只用于本地验证真实数据链路，不能替代服务器 full baseline。如果数据文件不存在，脚本会给出清晰提示，不会打印难以阅读的 traceback。

## 7. 输出目录说明

每次训练会创建：

```text
runs/YYYYMMDD_HHMMSS_modelname/
├── config.yaml
├── logs.txt
├── metrics.json
├── metrics.csv
├── label_mapping.json
├── best_model.pt
├── plots/
│   ├── training_curve.png
│   ├── confusion_matrix.png
│   ├── accuracy_vs_snr.png
│   ├── iq_examples.png
│   ├── constellation_examples.png
│   ├── amplitude_phase_examples.png
│   └── stft_examples.png
└── stage1_report.md
```

`runs/` 不上传 GitHub。

## 8. CNN1D 和 ResNet1D 方法说明

CNN1D 是轻量一维卷积 baseline，输入 `[batch, 2, 128]`，经过 Conv1d、BatchNorm1d、ReLU、MaxPool1d、AdaptiveAvgPool1d 和 Linear 分类器输出类别 logits。

ResNet1D 使用 2 到 3 个轻量残差块，仍然直接处理 I/Q 序列。它用于验证残差结构在该任务上的基础表现，不包含复杂注意力或多分支融合。

## 9. 可视化说明

`scripts/visualize_examples.py` 会随机抽样并保存：

- I/Q 时域波形；
- 星座图；
- 幅度和相位曲线；
- STFT 时频图。

STFT 在第一阶段只用于示例可视化，不会把全量样本离线转换成图片数据集。

## 10. 服务器 full baseline 训练与数据集下载说明

本地推荐流程：

1. 创建虚拟环境；
2. `pip install -r requirements.txt`；
3. 用 mock 配置跑 smoke test；
4. 确认脚本和 pytest 无误；
5. git push 到 GitHub。

服务器推荐使用 `tmux` 或等价的会话管理工具，建议直接在服务器下载数据集，不建议从本地上传大数据。先检查数据盘空间和 GPU：

```bash
df -h
nvidia-smi
python - <<'PY'
import torch
print("cuda_available:", torch.cuda.is_available())
print("device_count:", torch.cuda.device_count())
PY
```

服务器推荐流程：

```bash
git clone <your-repo-url>
cd radioml-amc-stage1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/check_storage.sh
bash scripts/download_radioml_kaggle.sh
# 按脚本提示配置 Kaggle token 并手动运行 RadioML2016.10A 下载命令
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml
```

full baseline 耗时需要根据服务器 GPU、CPU、磁盘和 batch size 确定。full baseline 完成后至少保存并记录：

- `metrics.json`
- `baseline_comparison.md`
- `baseline_comparison.csv`
- `confusion_matrix.png`
- `normalized_confusion_matrix.png`
- `accuracy_vs_snr.png`
- `per_class_accuracy.png`
- `stage1_5_report.md` 或 `stage1_6_report.md`

`scripts/download_radioml_kaggle.sh` 是示例脚本，不会自动下载。不要把 `kaggle.json` 上传到 GitHub。

## 11. GitHub 上传注意事项

GitHub 只上传代码、配置、说明和测试文件。以下内容不上传：

- `data/raw/` 中的数据集；
- `data/processed/` 中的大文件；
- `runs/` 中的训练输出；
- Kaggle token；
- `.pt`、`.pth`、`.pkl`、`.bz2` 等大文件或模型文件。

## 12. 常见问题

**没有数据集能不能运行？**  
可以，使用 `configs/stage1_local_mock.yaml`。

**mock 结果能不能写进论文？**  
不能。mock 结果只说明工程链路可运行。

**为什么默认真实配置开启 subset_mode？**  
为了本地先用少量类别、少量 SNR 和每组有限样本做调试。服务器正式训练时可以关闭 `subset_mode`。

**RadioML2018.01A 是否已完整支持？**  
没有。本阶段只预留说明和服务器检查项，完整处理留到第二阶段。

## 13. 第二阶段计划

第二阶段建议加入 STFT/CWT 时频分支、多视图融合、低 SNR 鲁棒训练、消融实验和正式论文表格。进入第二阶段前至少应完成真实 RadioML2016.10A subset baseline，并生成 `baseline_comparison.md`、`baseline_comparison.csv` 和 `accuracy_vs_snr.png`；更稳妥的论文实验入口是服务器 full baseline 也完成。mock 结果不能作为进入 Stage 2 的主要依据。

## 14. 阶段 1.5：真实数据 baseline

阶段 1.5 的目标是把第一阶段从 mock 工程闭环推进到真实 RadioML2016.10A baseline 实验闭环。当前阶段仍然不实现 STFT/CWT 训练分支、多视图融合、Transformer 或复杂注意力机制。

先做真实 baseline 的原因是：后续融合模型必须有可靠对照组。只有 CNN1D 和 ResNet1D 在真实数据 subset/full 上的协议、指标和输出稳定后，第二阶段的时频分支收益才有可解释性。

### 14.1 RadioML2016.10A 文件放置路径

请手动下载 RadioML2016.10A，并放到以下任一路径：

```text
data/raw/RML2016.10a_dict.pkl
data/raw/RML2016.10a_dict.pkl.bz2
data/raw/radioml2016/RML2016.10a_dict.pkl
data/raw/radioml2016/RML2016.10a_dict.pkl.bz2
```

新配置默认使用：

```yaml
data:
  raw_path: auto
```

也可以在 config 中显式设置 `data.raw_path`。项目不会自动联网下载数据集。

### 14.2 本地真实 subset 测试

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

subset 配置只用于本地小规模真实数据验证，默认选择 `BPSK/QPSK/8PSK/QAM16`、多个中高 SNR 和每组最多 200 条样本。

### 14.3 服务器真实 full 训练

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml
```

full 配置默认关闭 subset，建议在服务器或高性能 GPU 环境运行。

### 14.4 CNN1D / ResNet1D baseline 协议

- Baseline A：CNN1D。
- Baseline B：ResNet1D。
- 输入统一为 `[batch, 2, 128]` I/Q 序列。
- 不加入时频分支、多视图融合、Transformer 或注意力机制。
- 输出指标包括 overall accuracy、per-SNR accuracy、per-class accuracy、confusion matrix、normalized confusion matrix、low/mid/high SNR accuracy、参数量、训练时间、推理时间和 best epoch。
- SNR 分组：
  - low SNR：`SNR <= -6`
  - mid SNR：`-4 <= SNR <= 6`
  - high SNR：`SNR >= 8`

### 14.5 run 输出说明

新的训练 run 会尽量保存：

```text
runs/YYYYMMDD_HHMMSS_modelname/
├── config.yaml
├── logs.txt
├── dataset_summary.json
├── split_summary.json
├── label_mapping.json
├── metrics.json
├── metrics.csv
├── best_model.pt
├── plots/
│   ├── training_curve.png
│   ├── confusion_matrix.png
│   ├── normalized_confusion_matrix.png
│   ├── accuracy_vs_snr.png
│   ├── per_class_accuracy.png
│   ├── iq_examples.png
│   ├── constellation_examples.png
│   └── stft_examples.png
├── stage1_report.md
└── stage1_5_report.md
```

`dataset_summary.json` 记录样本数、shape、dtype、类别/SNR 分布、modulation × SNR 分布、NaN/Inf 检查和真实数据文件路径。`split_summary.json` 记录 train/val/test 样本数、比例和分层统计。

### 14.6 baseline 对比

批量 baseline：

```bash
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

对比已有 runs：

```bash
python scripts/compare_runs.py --run_dirs runs/xxx_cnn1d runs/yyy_resnet1d --output runs/stage1_5_comparison
```

输出：

- `baseline_comparison.csv`
- `baseline_comparison.md`

### 14.7 docs/ 过程文档体系

`docs/` 用于阶段过程管理，进入 Git。核心文件：

- `docs/README.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`
- `docs/stages/`

`reports/` 偏正式报告模板或报告结构；`runs/` 是每次运行产物，不进入 Git。

### 14.8 常见错误

**找不到数据文件**  
确认文件位于 `data/raw/` 或 `data/raw/radioml2016/` 下，文件名必须匹配 `RML2016.10a_dict.pkl` 或 `RML2016.10a_dict.pkl.bz2`。也可以在 config 中显式设置 `data.raw_path`。

**pickle encoding 问题**  
loader 使用 `pickle.load(..., encoding="latin1")` 兼容 Python 3 读取旧版 pickle。

**内存不足**  
先使用 `configs/stage1_rml2016a_real_subset.yaml`，降低 `max_samples_per_group` 或 `batch_size`。全量训练建议放到服务器。

**GPU 不可见**  
检查 PyTorch CUDA 安装和 `torch.cuda.is_available()`。`device: auto` 会在 CUDA 不可用时回退 CPU。

**matplotlib 中文乱码**  
当前图表标题主要使用英文，避免依赖本地中文字体。若自行添加中文图题，需要配置可用中文字体。

**sklearn 分层划分报错**  
如果某些 modulation × SNR 组合样本太少，降低过滤范围或增加样本数。代码会尽量使用固定 seed 和分层划分，必要时回退到非分层切分。

### 14.9 Git 与大文件约定

- mock 结果不能作为正式实验结论。
- 数据集不进入 Git。
- `runs/` 不进入 Git。
- checkpoint 不进入 Git。
- `docs/` 和 `configs/` 需要进入 Git。
- `reports/` 模板需要进入 Git。
- 真实数据建议先 subset，再 full。
- 大数据集建议在服务器直接下载。

### 14.10 第二阶段入口

第二阶段主题是 STFT/CWT 时频分支与 I/Q 多视图融合。进入第二阶段前，应优先完成真实 RadioML2016.10A subset baseline，并把结果写入 `docs/EXPERIMENT_LOG.md` 和对应阶段文档。

## 15. 阶段 1.6：真实 subset baseline 当前结果

2026-05-07 已通过 Kaggle 下载并接入真实 RadioML2016.10A：

```text
data/raw/radioml2016/RML2016.10a_dict.pkl
```

真实 subset 配置 `configs/stage1_rml2016a_real_subset.yaml` 已跑通：

- 样本数：6400
- shape：`[6400, 2, 128]`
- 类别：`8PSK`、`BPSK`、`QAM16`、`QPSK`
- SNR：`-2`、`0`、`2`、`4`、`6`、`8`、`10`、`12`
- 每个 modulation × SNR：200 条
- NaN/Inf：无

真实 subset baseline：

| 模型 | run_dir | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---|---:|---:|---:|---:|
| CNN1D | `runs/20260507_153710_cnn1d/` | 0.8461 | N/A | 0.8300 | 0.8729 |
| ResNet1D | `runs/20260507_153719_resnet1d/` | 0.9070 | N/A | 0.8775 | 0.9563 |

comparison 输出：

```text
runs/stage1_6_real_subset_comparison/baseline_comparison.md
runs/stage1_6_real_subset_comparison/baseline_comparison.csv
```

说明：当前 subset 不包含 `SNR <= -6`，因此 low SNR accuracy 为 N/A。可以进入 Stage 2 的工程开发，但论文实验仍需在服务器补齐 full baseline。

## 16. 阶段 2.1：真实 subset 消融当前结果

Stage 2 已完成 STFT/CWT on-the-fly 特征、多视图 Dataset、TF-CNN 和 I/Q + 时频融合模型。Stage 2.1 在真实 RadioML2016.10A subset 上完成 single-seed 消融，并将 Stage 1.6 baseline 纳入统一对比。

统一汇总目录：

```text
runs/stage2_1_real_subset_ablation_comparison/
```

主要结果：

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---|---:|---:|---:|---:|
| CNN1D | I/Q | 0.8461 | N/A | 0.8300 | 0.8729 |
| ResNet1D | I/Q | 0.9070 | N/A | 0.8775 | 0.9563 |
| tfcnn_stft | STFT | 0.5961 | N/A | 0.6125 | 0.5687 |
| tfcnn_cwt | CWT | 0.6539 | N/A | 0.6850 | 0.6021 |
| fusion_iq_stft | I/Q + STFT | 0.8320 | N/A | 0.8200 | 0.8521 |
| fusion_iq_amp_phase | I/Q + amp/phase | 0.8086 | N/A | 0.7863 | 0.8458 |
| fusion_iq_stft_cwt | I/Q + STFT + CWT | 0.8328 | N/A | 0.8187 | 0.8562 |

当前 subset 最佳模型仍是 ResNet1D。结果可以写入结课报告的 subset 消融章节，但必须标注：single-seed、real subset、非 full dataset、low SNR N/A。下一步优先在服务器执行 RadioML2016.10A full baseline/full ablation。

## 17. 阶段 2.2：RadioML2016.10A full 当前结果

Stage 2.2 已在 GPU 服务器上完成 RadioML2016.10A full 数据检查、CNN1D/ResNet1D full baseline 和 `fusion_iq_stft` full 消融。

统一汇总目录：

```text
runs/stage2_2_full_ablation_comparison/
```

主要结果：

| 模型 | 输入视图 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---|---:|---:|---:|---:|
| CNN1D | I/Q | 0.5855 | 0.2032 | 0.8017 | 0.8790 |
| ResNet1D | I/Q | 0.5968 | 0.2091 | 0.8155 | 0.8950 |
| fusion_iq_stft | I/Q + STFT | 0.5782 | 0.2222 | 0.7856 | 0.8455 |

当前 full 最佳模型是 ResNet1D。`fusion_iq_stft` 在 low SNR 分组略高于 baseline，但 overall、mid SNR 和 high SNR 未超过 ResNet1D。

`fusion_iq_stft_cwt` 在 RTX 4070 12GB 上被记录为 optional skipped：on-the-fly CWT 触发大量 NNPACK warning，训练在 epoch 1 前明显 CPU-bound，GPU 利用率接近 0%。后续如需 full 三视图，应先优化 CWT 成本或换更强服务器。
