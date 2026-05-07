# Stage 1.5：RadioML2016.10A 真实数据 baseline

## 1. 阶段定位

Stage 1.5 位于 mock 工程闭环和论文创新模型之间。本阶段不追求新模型，而是把工程推进到真实 RadioML2016.10A baseline 实验闭环，为 Stage 2 的时频分支与多视图融合提供可靠对照组。

## 2. 阶段目标

- 审计 Stage 1 工程并确认 mock 流程仍可运行。
- 新增 `docs/` 过程文档体系。
- 强化 RadioML2016.10A loader，支持 `raw_path: auto`、`.pkl`、`.pkl.bz2` 和 Python 3 `latin1` pickle 读取。
- 新增真实 subset 配置和 full 配置。
- 固定 CNN1D 与 ResNet1D baseline 协议。
- 保存 `dataset_summary.json`、`split_summary.json`、`label_mapping.json`、metrics、plots 和 `stage1_5_report.md`。
- 新增 baseline 批量运行脚本和 run 对比脚本。
- 为 Stage 2 的 STFT/CWT 和多视图融合准备干净接口。

## 3. 本阶段不做什么

- 不实现 STFT/CWT 训练分支。
- 不实现 I/Q 与时频多视图融合网络。
- 不实现 Transformer、注意力机制或复杂论文创新模型。
- 不完整训练 RadioML2018.01A。
- 不自动下载大数据集。
- 不将全量样本离线转换为 STFT 图片。
- 不把 mock 结果作为真实实验结论。

## 4. 输入条件

- Stage 1 已完成的工程代码。
- `configs/stage1_local_mock.yaml`。
- 新增的 `configs/stage1_rml2016a_real_subset.yaml` 和 `configs/stage1_rml2016a_real_full.yaml`。
- 真实数据可放置在以下任一路径：
  - `data/raw/RML2016.10a_dict.pkl`
  - `data/raw/RML2016.10a_dict.pkl.bz2`
  - `data/raw/radioml2016/RML2016.10a_dict.pkl`
  - `data/raw/radioml2016/RML2016.10a_dict.pkl.bz2`

## 5. 真实数据检测状态

当前未检测到真实 RadioML2016.10A 数据文件。

> **当前尚未接入真实 RadioML2016.10A 数据，本阶段真实 baseline 训练尚未完成，不能作为正式实验结论。**

## 6. 已完成工作

| 任务 | 状态 | 说明 | 相关文件 |
|---|---|---|---|
| Stage 1 审计 | Done | README、configs、loader、trainer、scripts、tests 已检查 | `README.md`, `src/`, `scripts/`, `tests/` |
| 修改前 mock pytest | Done | `.s... [100%]` | `tests/` |
| 修改前 mock check_dataset | Done | 输出 `[512, 2, 128]`、4 类、4 个 SNR | `configs/stage1_local_mock.yaml` |
| 修改前 mock train_cnn1d | Done | 新增验证 run | `runs/20260507_122235_cnn1d/` |
| 修改后 mock pytest | Done | `.s......... [100%]` | `tests/` |
| 修改后 mock CNN1D/ResNet1D | Done | 新输出结构 smoke test | `runs/20260507_123742_cnn1d/`, `runs/20260507_123758_resnet1d/` |
| docs 过程体系 | Done | 新增顶层文档和阶段文档 | `docs/` |
| loader 自动路径检测 | Done | 支持四个约定路径和 `raw_path: auto` | `src/radioml_amc/data/rml2016a_loader.py` |
| subset 配置 | Done | 本地真实小规模测试配置 | `configs/stage1_rml2016a_real_subset.yaml` |
| full 配置 | Done | 服务器全量训练配置 | `configs/stage1_rml2016a_real_full.yaml` |
| split summary | Done | 保存 train/val/test 样本、比例和分组统计 | `src/radioml_amc/data/split.py` |
| metrics 增强 | Done | 增加 low/mid/high SNR、normalized confusion matrix、时间统计 | `src/radioml_amc/training/metrics.py`, `trainer.py` |
| baseline 批量脚本 | Done | 依次训练 CNN1D 和 ResNet1D 并汇总 | `scripts/run_stage1_5_baselines.py` |
| run 对比脚本 | Done | 多 run metrics 对比输出 CSV/Markdown | `scripts/compare_runs.py` |
| Stage 1.5 报告 | Done | 每个新训练 run 生成 `stage1_5_report.md` | `src/radioml_amc/reporting/make_stage1_report.py` |

## 7. Baseline 设置

Baseline A：CNN1D。

- 输入：`[batch, 2, 128]`。
- 输出：调制类别 logits。
- 不包含时频分支、注意力或融合结构。

Baseline B：ResNet1D。

- 输入：`[batch, 2, 128]`。
- 使用轻量一维残差块。
- 不包含时频分支、注意力或融合结构。

共同输出：

- overall accuracy。
- low SNR accuracy：`SNR <= -6`。
- mid SNR accuracy：`-4 <= SNR <= 6`。
- high SNR accuracy：`SNR >= 8`。
- per-SNR accuracy。
- per-class accuracy。
- confusion matrix。
- normalized confusion matrix。
- 参数量、训练时间、推理时间和 best epoch。

## 8. subset 配置

- 文件：`configs/stage1_rml2016a_real_subset.yaml`
- 数据：RadioML2016.10A
- `raw_path: auto`
- `subset_mode: true`
- `subset_mods`: `BPSK`, `QPSK`, `8PSK`, `QAM16`
- `subset_snrs`: `-2, 0, 2, 4, 6, 8, 10, 12`
- `max_samples_per_group: 200`
- 训练：5 epochs, batch size 128, early stopping patience 3

## 9. full 配置

- 文件：`configs/stage1_rml2016a_real_full.yaml`
- 数据：RadioML2016.10A
- `raw_path: auto`
- `subset_mode: false`
- 训练：30 epochs, batch size 256, early stopping patience 8
- 预期用途：服务器或高性能 GPU 环境全量训练

## 10. 执行命令

无真实数据时已验证：

```bash
pytest -q
python scripts/check_dataset.py --config configs/stage1_local_mock.yaml
python scripts/train_cnn1d.py --config configs/stage1_local_mock.yaml
python scripts/train_resnet1d.py --config configs/stage1_local_mock.yaml
python scripts/compare_runs.py --run_dirs runs/20260507_123742_cnn1d runs/20260507_123758_resnet1d --output runs/stage1_5_mock_comparison
```

放置真实数据后本地 subset：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/visualize_examples.py --config configs/stage1_rml2016a_real_subset.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

服务器 full：

```bash
python scripts/check_dataset.py --config configs/stage1_rml2016a_real_full.yaml
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_full.yaml
```

对比已有 runs：

```bash
python scripts/compare_runs.py --run_dirs runs/xxx_cnn1d runs/yyy_resnet1d --output runs/stage1_5_comparison
```

## 11. 输出结果

新训练 run 目录应包含：

- `config.yaml`
- `logs.txt`
- `dataset_summary.json`
- `split_summary.json`
- `label_mapping.json`
- `metrics.json`
- `metrics.csv`
- `best_model.pt`
- `plots/training_curve.png`
- `plots/confusion_matrix.png`
- `plots/normalized_confusion_matrix.png`
- `plots/accuracy_vs_snr.png`
- `plots/per_class_accuracy.png`
- `stage1_report.md`
- `stage1_5_report.md`

已完成的 mock 输出结构 smoke test：

- `runs/20260507_123742_cnn1d/`
- `runs/20260507_123758_resnet1d/`
- `runs/stage1_5_mock_comparison/baseline_comparison.csv`
- `runs/stage1_5_mock_comparison/baseline_comparison.md`

以上 mock 对比只验证脚本和输出结构，不能作为正式实验结果。

## 12. Baseline 对比结果

真实数据 baseline 对比当前 pending。真实数据放置后运行：

```bash
python scripts/run_stage1_5_baselines.py --config configs/stage1_rml2016a_real_subset.yaml
```

脚本会在 `runs/YYYYMMDD_HHMMSS_stage1_5_comparison/` 下生成：

- `baseline_comparison.csv`
- `baseline_comparison.md`

## 13. 当前问题

- 当前未检测到真实 RadioML2016.10A 数据。
- 真实 subset/full baseline 尚未运行。
- QAM16/QAM64、AM-DSB/WBFM 等真实混淆关系尚无证据。
- Stage 2 前必须先补齐真实 baseline，否则融合模型缺少可信对照。

## 14. 第二阶段计划

Stage 2 将在稳定 baseline 基础上实现 STFT/CWT on-the-fly 特征、时频 CNN 分支、I/Q + 时频多视图融合模型，并做 I/Q only、STFT only、CWT only、I/Q + STFT、I/Q + CWT、I/Q + STFT + CWT 消融实验。

## 15. 验收标准核对

| 验收项 | 状态 | 证据 |
|---|---|---|
| Stage 1 mock pytest 修改前通过 | Done | `.s... [100%]` |
| mock check_dataset 修改前通过 | Done | 输出 `[512, 2, 128]` |
| mock train_cnn1d 修改前通过 | Done | `runs/20260507_122235_cnn1d/` |
| Stage 1.5 pytest 修改后通过 | Done | `.s......... [100%]` |
| Stage 1.5 mock train_cnn1d 修改后通过 | Done | `runs/20260507_123742_cnn1d/` |
| Stage 1.5 mock train_resnet1d 修改后通过 | Done | `runs/20260507_123758_resnet1d/` |
| Stage 1.5 compare_runs smoke test | Done | `runs/stage1_5_mock_comparison/baseline_comparison.md` |
| docs 过程文档体系创建 | Done | `docs/` |
| loader 支持四个自动路径 | Done | `DEFAULT_RML2016A_CANDIDATES` |
| loader 支持 `.pkl/.pkl.bz2` | Done | `rml2016a_loader.py` |
| subset/full 配置创建 | Done | `configs/stage1_rml2016a_real_subset.yaml`, `configs/stage1_rml2016a_real_full.yaml` |
| split summary 输出 | Done | `split_summary.json` 生成逻辑 |
| baseline 批量脚本 | Done | `scripts/run_stage1_5_baselines.py` |
| compare_runs 脚本 | Done | `scripts/compare_runs.py` |
| 真实 subset baseline | Need Data | 当前未检测到真实数据 |
| 真实 full baseline | Need Data | 当前未检测到真实数据 |

## 16. 第二阶段提示词

完整提示词已归档到 `docs/NEXT_STAGE_PROMPTS.md` 的 `Stage 1.5 → Stage 2` 小节。
