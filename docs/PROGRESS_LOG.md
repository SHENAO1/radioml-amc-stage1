# 项目进展日志

## 2026-05-09 Paper-Stage 6 A 方案 — fusion_cldnn_stft + 增强 + label smoothing **(POSITIVE)**

### 本次目标

承接 P2.5 负结果，先做 Stage 2 文献校准（[`docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md`](paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md)），确认 RML2016.10A avg-across-SNR 真实 SOTA ~0.63–0.65（LENet-M 0.6463、SigFormer 0.6371），我们 CLDNN 0.6129 还有 2–3 pp 空间可冲。然后选定 A 方案：在一次训练中叠加三项独立干预——

1. **架构升级**：fusion 的 I/Q 分支从 CNN1D-style (`IQBranch1D`) 换成 CLDNN-style (`CLDNNIQBranch`，CNN+LSTM)；
2. **信号域增强**（仅 train）：phase rotation θ~U(-π,π) prob 0.5 + cyclic time shift k~U(-8,+8) prob 0.5；
3. **label smoothing 0.1**。

evidence label `FUSION_CLDNN_STFT_AUG_LS_3090`，独立输出根；Stage 5A/5B 与之前所有 Stage 6 子证据均不动。

### 本次完成

- 文献调研落档；`.ai-context/04-decisions.md` 加 ADR；`05-current-state.md` 同步 Stage 2 文献校准要点。
- 代码：`CLDNNIQBranch` + `FusionCldnnStftNet`（`src/radioml_amc/models/multiview.py`）；`SignalAugmenter` + `build_augmenter`（`src/radioml_amc/data/augmentation.py`）；`SignalDataset` 加可选 `augmenter` 参数；trainer 的 `_make_loaders` 加可选 `augment_config`，**只对 train loader 创建带 augmenter 的 dataset**；loss factory 支持 `label_smoothing`。所有改动**默认 None / disabled**，对 Stage 5A 完全向后兼容。
- 新增 `configs/paper/rml2016a_fusion_cldnn_stft_aug_ls_3090.yaml` + orchestrator `scripts/paper/run_fusion_cldnn_stft_aug_ls_training.py`。
- 服务器 smoke check 通过：fusion_cldnn_stft 286k 参数，CUDA forward + augmenter + LS CE 全部 OK。
- tmux session `pa` 跑完 3 cells × epoch 50，27.4 分钟，0 失败。

### Headline 结果（mean across 3 seeds）

| Metric | A 方案 fusion_cldnn_stft + aug + LS | Stage 5A CLDNN | Δ |
|---|---:|---:|---:|
| Overall | **0.6264** (σ=0.0005) | 0.6129 | **+0.0135** ✅ |
| Low-SNR | **0.2258** (σ=0.0008) | 0.2224 | +0.0034 ✅ |
| Mid-SNR | **0.8606** (σ=0.0009) | 0.8396 | +0.0210 ✅ |
| High-SNR | **0.9264** (σ=0.0003) | 0.9070 | +0.0194 ✅ |

**4 个指标全部正向；fusion 首次超过 CLDNN baseline。** Best-epoch 31/42/31 均在预算内，结果不是 budget 截断驱动；3-seed std 0.0005 远小于 +0.0135 增量，结果稳健。

vs Stage 5A `fusion_iq_stft` 0.5771 → +0.0493 overall；vs P1.1 `fusion_iq_stft` 0.5851（同 schedule）→ +0.0413 overall。证实是 **架构 + 增强 + LS 的组合贡献**，不是 budget 或单一干预效应。

vs 2024 公开 SOTA（同口径）：贴近 CC-MSNet 0.6286 / CCTL-Net 0.6297；距 LENet-M 0.6463 / SigFormer 0.6371 仍 1–2 pp。深低 SNR (-20 至 -16 dB) 仍 ~chance level，是信息论下限不是模型容量问题（与 P1.3 collapse-to-AM-SSB 分析一致）。

### 修改/新增文件

- 新增 `src/radioml_amc/models/multiview.py` 中 `CLDNNIQBranch` + `FusionCldnnStftNet`
- 新增 `src/radioml_amc/data/augmentation.py`（`SignalAugmenter`, `build_augmenter`）
- 修改 `src/radioml_amc/data/dataset.py`（`SignalDataset` 加可选 `augmenter`）
- 修改 `src/radioml_amc/training/trainer.py`（`_make_loaders` 加 `augment_config`，build_model 注册 fusion_cldnn_stft；调用点一处加 `augment_config=train_cfg.get("augmentation")`）
- 修改 `src/radioml_amc/training/losses.py`（CE 路径支持 `label_smoothing`）
- 修改 `src/radioml_amc/models/__init__.py`（导出 `FusionCldnnStftNet`）
- 新增 `configs/paper/rml2016a_fusion_cldnn_stft_aug_ls_3090.yaml`
- 新增 `scripts/paper/run_fusion_cldnn_stft_aug_ls_training.py`
- 新增 `docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md`
- 新增 `docs/paper/PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_ANALYSIS.md`
- 新增 `docs/paper/PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_3090_REPORT.md`（auto-generated）
- 新增 manuscript `docs/paper/manuscript/section5_6_proposed_fusion_cldnn_stft.md`（**Section 5.6 正面贡献**）
- 修改 `docs/paper/PAPER_STAGE_INDEX.md`（加 Stage 2 lit + A 方案两行 + `FUSION_CLDNN_STFT_AUG_LS_3090` evidence label policy）
- 修改 `.ai-context/04-decisions.md`、`05-current-state.md`、`06-session-log.md`

### 服务器侧产物（未本地归档）

- `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_<train_seed>/` 共 3 个 cell × 11 个 required artifact + `best_model.pt` + `plots/`。
- 至此服务器累计未归档权重：Stage 5A 27 + P1.1 12 + P2.5 6 + A 3 = **48 个 best_model.pt**。

### 限制

- A 方案是三干预 stacked 单次实验，**未做 per-intervention 消融**，无法说哪一项贡献多少。manuscript 5.6 末段已注明，作为 future work 候选。
- A 方案 GPU = RTX 3090 ≠ Stage 5A 的 RTX 4070；prediction-level paired bootstrap/McNemar 不能跨硬件直接做，3-seed-mean 是唯一支持的对比层级。
- A 方案仅在 RadioML2016.10A 测试，2018.01A 未跑。

## 2026-05-09 Paper-Stage 6 串行三连：低 SNR 混淆 + 复杂度/CPU 延迟 + SNR 加权 CE

### 本次目标

承接 P1.1 结论，按 A → B → C 顺序补齐 manuscript 三个空缺：
- A: 低 SNR-only 混淆矩阵（Section 5.2 失踪 figures）；
- B: MACs / FLOPs / CPU 延迟（Section 5.4 失踪 cells）；
- C: SNR 加权 CE 干预实验（验证 P1.3 揭示的 collapse-to-AM-SSB 是否能用最简单的 loss 重写解决）。

每一项走独立 evidence label + 独立输出根，**Stage 5A/5B 主表与 P1.1 数据不动**。

### 本次完成

**A — P1.3 低 SNR 混淆矩阵**：纯后处理 27 份 Stage 5A `predictions_test.csv`。本地 CPU 运行，~1 分钟。输出 27 张 PNG（9 模型 × {raw / normalized / per-seed} 视角）+ summary CSV/MD 到 `results/paper_stage6/low_snr_confusion_extended/`。**关键发现**：7/9 稳定模型在 SNR≤−6 dB 时把数字调制类（8PSK/BPSK/QPSK/CPFSK/GFSK）误判成 AM-SSB 的比例 0.63–0.81；AM-SSB 自身 low-SNR acc 0.87–0.95。

**B — P1.2 扩展 complexity / latency**：新增 `scripts/paper/measure_extended_complexity_latency.py`，在服务器（EPYC 7B12, num_threads=1, torch 2.9.1+cu128）跑 `thop` + `torch.utils.benchmark`。286 秒完成，输出 `results/paper_stage6/extended_complexity_latency/`。**关键发现**：MCLDNN 49 M MACs / 573 ms CPU bs=256 最重；CLDNN 8.7 M / 183 ms 居中；fusion_iq_stft 2.0 M MACs **比 ResNet1D 4.9 M 还少** → fusion 不是因为算力少才输；lwamcnet 参数最少（20k）但 CPU bs=1 第二慢（depthwise/grouped conv 在单线程 CPU 不划算）。

**C — P2.5 SNR 加权 CE**：新增 `src/radioml_amc/training/losses.py`（`SnrWeightedCrossEntropy` + `build_criterion` + `compute_loss`）。Trainer 接入 `train.loss` 配置，向后兼容（无 cfg = plain CE）。新 config + orchestrator + tmux session `p25` 跑 6 cells（cldnn + fusion_iq_stft × 3 seed），22.8 分钟，0 失败。**关键结果**（mean across 3 seeds）：

| 模型 | Overall | Δ vs Stage 5A | Low-SNR | Δ vs Stage 5A | Mid-SNR | High-SNR |
|---|---:|---:|---:|---:|---:|---:|
| cldnn (P2.5) | 0.5896 | **−0.0233** | 0.2281 | **+0.0058** | 0.7958 | 0.8652 |
| fusion_iq_stft (P2.5) | 0.5704 | −0.0067 | 0.2255 | +0.0042 | 0.7679 | 0.8331 |

低 SNR 涨幅集中在 −8 至 −4 dB 转折区；−20 至 −16 dB 仍 ~chance level (0.09–0.11)。**简单 2× 加权改不动深度低 SNR 的 collapse**；mid/high SNR 的代价大于 low SNR 的收益 → manuscript 写为**负结果**，强化 limitations。

### 修改/新增文件

- 新增 `src/radioml_amc/training/losses.py`（loss factory）
- 修改 `src/radioml_amc/training/trainer.py`（接入 `train.loss` 钩子，向后兼容）
- 新增 `configs/paper/rml2016a_low_snr_weighted_ce_3090.yaml`
- 新增 `scripts/paper/build_low_snr_confusion_matrices.py`
- 新增 `scripts/paper/measure_extended_complexity_latency.py`
- 新增 `scripts/paper/run_low_snr_weighted_ce_training.py`
- 新增分析 `docs/paper/PAPER_STAGE6_LOW_SNR_CONFUSION_ANALYSIS.md`
- 新增分析 `docs/paper/PAPER_STAGE6_EXTENDED_COMPLEXITY_ANALYSIS.md`
- 新增分析 `docs/paper/PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_ANALYSIS.md`
- 新增报告 `docs/paper/PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md`（auto-generated）
- 新增 manuscript `docs/paper/manuscript/section5_2_addendum_low_snr_per_class.md`
- 新增 manuscript `docs/paper/manuscript/section5_4_addendum_complexity_latency_filled.md`
- 新增 manuscript `docs/paper/manuscript/section7_8_low_snr_weighted_ce_outcome.md`
- 修改 `docs/paper/PAPER_STAGE_INDEX.md`：新增 3 行 stage 状态 + 3 个 evidence label policy
- 修改 `.ai-context/04-decisions.md`、`.ai-context/05-current-state.md`、`.ai-context/06-session-log.md`

### 服务器侧产物（未本地归档）

- `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/<model>/seed_<train_seed>/` 共 6 个 cell × 11 个 required artifact + `best_model.pt` + `plots/`。
- 算上 P1.1 的 12 个，共 18 个 best_model.pt 在服务器，未本地归档。

### 限制

- P2.5 vs Stage 5A 同时存在硬件（4070→3090）和 loss（plain→weighted）两个变更；不能直接做 paired bootstrap/McNemar。
- 干预实验仅覆盖 cldnn 和 fusion_iq_stft；其余 7 个 Stage 5A 模型的 manuscript 主表解释**继续来自 Stage 5A 原结果**。
- Group 加权方案 (low=2.0, mid=1.0, high=0.7) 是单一选择；focal loss、连续 SNR 加权、SNR-balanced sampler、per-(class, SNR) 加权 都未测试。

## 2026-05-09 Paper-Stage 6 Extended Budget：RTX 3090 robustness check 完成

### 本次目标

- 验证 Stage 5A 的 epoch=20 budget 是否欠训练。
- 在新租 gpushare RTX 3090 实例上对 4 个核心模型重训：epoch 50 + 5-epoch 线性 warmup + cosine LR + early-stop patience 15。
- 输出走独立 evidence label `EXTENDED_BUDGET_3090` 和独立输出根，**不**修改 Stage 5A/5B 主表。

### 本次完成

- 部署：`paper-sci-track` 分支推到 GitHub；本地未提交的 59 个文件 SFTP 同步到服务器；上传数据集 612 MB（MD5 `61bf35ac7f0b7d8843613453447ea290`）；安装 scipy/sklearn/matplotlib/pandas/pywavelets/thop/pytest/tqdm；mock smoke 与 GPU forward+backward 验证通过。
- Trainer 新增可选 `train.scheduler` 配置（cosine + warmup），默认 `None`，与 Stage 5A 完全向后兼容。
- 12/12 cells 完成，0 失败，54.4 分钟。模型 × seed：`cldnn`、`resnet1d`、`iq_param_matched`、`fusion_iq_stft` × `42`、`2025`、`3407`。
- 关键发现：ΔOverall 全部在 ±1 pp 内（ranking 不变，`cldnn` 仍最强 0.6145）；ΔLow-SNR 全部为负，`fusion_iq_stft` 跌幅最大 −0.89 pp；best_epoch 显示 `resnet1d` 完全没欠训练（15–20），`fusion_iq_stft` 欠训练最严重（34–42）但收益仅 +0.80 pp，仍输给 cldnn 3 pp。
- 结论：**Stage 5A 没有被显著欠训练**；延长 budget 无法救低 SNR，反而轻微伤害；融合架构与 cldnn 的差距不是 budget 问题。

### 修改/新增文件

- 新增 `configs/paper/rml2016a_extended_budget_3090.yaml`
- 新增 `scripts/paper/run_extended_budget_training.py`
- 新增 `docs/paper/PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md`（自动生成）
- 新增 `docs/paper/PAPER_STAGE6_EXTENDED_BUDGET_ANALYSIS.md`（分析附录）
- 新增 `docs/paper/manuscript/section7_7_training_budget_sensitivity.md`
- 修改 `src/radioml_amc/training/trainer.py`：增加可选 cosine LR scheduler
- 修改 `docs/paper/PAPER_STAGE_INDEX.md`：登记 Stage 6 Extended Budget 行 + `EXTENDED_BUDGET_3090` evidence label policy
- 修改 `.ai-context/04-decisions.md`、`.ai-context/05-current-state.md`、`.ai-context/06-session-log.md`

### 服务器侧产物（未本地归档）

- `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/<model>/seed_<train_seed>/` 共 12 个 cell，每个 cell 含 11 个 required artifact + `best_model.pt` + `plots/`。
- `run.log`、`status.json` 同目录可读；如需要本地归档权重，沿用 Stage 5A 策略：单独 archive 路径并 hash-check，不要覆盖 `results/`。

### 限制

- 新 GPU 是 RTX 3090（Ampere sm_86），与 Stage 5A 的 RTX 4070（Ada sm_89）架构不同。即使 seed 相同，cuDNN kernel 选择可能不同，**与 Stage 5A 不能跨硬件做 paired bootstrap/McNemar**。
- 本轮只跑了 4 个模型（核心强基线 + 融合控制 + 静态融合），其余 5 个 Stage 5A 模型（`cnn1d`、`tfcnn_stft`、`mcldnn`、`lwamcnet`、`gated_fusion_iq_stft`）的论文主表解释**继续来自 Stage 5A 原结果**。

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

## 2026-05-07 Stage 3：低 SNR 鲁棒性分析、结果解释与轻量改进准备

### 本次目标

- 基于 Stage 2.2 full 结果生成低 SNR 分析表格和图表。
- 判断 `fusion_iq_stft` 的 low SNR 提升是否足以支持报告结论。
- 明确当前不能生成 low-SNR-only confusion matrix 的原因。
- 形成 Stage 3 文档和后续 Stage 3.1 / Stage 5.0 提示词。

### 本次完成

- 新增 `scripts/analyze_stage3_low_snr.py`。
- 新增 `tests/test_stage3_analysis.py`，使用临时 metrics 验证分析脚本输出。
- 生成 Stage 3 分析目录：`runs/stage3_low_snr_analysis/`。
- 生成 per-SNR、low/mid/high、overall-vs-low 和 per-class 对比图。
- 确认 Stage 2.2 run 未保存 prediction-level 文件，因此 low-SNR-only confusion matrix 暂记为 pending。
- 新增阶段文档：`docs/stages/STAGE_03_LOW_SNR_ANALYSIS.md`。

### 执行命令

```bash
python scripts/analyze_stage3_low_snr.py --help
python scripts/analyze_stage3_low_snr.py --comparison-dir runs/stage2_2_full_ablation_comparison --cnn1d-run-dir runs/20260507_192755_cnn1d --resnet1d-run-dir runs/20260507_193019_resnet1d --fusion-run-dir runs/20260507_193548_fusion_iq_stft --output runs/stage3_low_snr_analysis
pytest -q
python -m compileall -q src scripts
git diff --check
```

### 输出结果

- `runs/stage3_low_snr_analysis/stage3_low_snr_summary.csv`
- `runs/stage3_low_snr_analysis/stage3_low_snr_summary.md`
- `runs/stage3_low_snr_analysis/stage3_low_snr_summary.json`
- `runs/stage3_low_snr_analysis/stage3_low_snr_findings.md`
- `runs/stage3_low_snr_analysis/per_snr_accuracy_comparison.png`
- `runs/stage3_low_snr_analysis/low_mid_high_accuracy_bar.png`
- `runs/stage3_low_snr_analysis/overall_vs_low_snr_tradeoff.png`
- `runs/stage3_low_snr_analysis/per_class_accuracy_comparison.png`

### 实验摘要

| 模型 | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc |
|---|---:|---:|---:|---:|
| CNN1D | 0.5855 | 0.2032 | 0.8017 | 0.8790 |
| ResNet1D | 0.5968 | 0.2091 | 0.8155 | 0.8950 |
| fusion_iq_stft | 0.5782 | 0.2222 | 0.7856 | 0.8455 |

`fusion_iq_stft` 相比 ResNet1D：low SNR +0.0131，overall -0.0186，mid SNR -0.0298，high SNR -0.0495。

### 当前结论

- ResNet1D 是 full overall 最优模型。
- `fusion_iq_stft` 是当前 low SNR 最优模型，但提升幅度较小。
- 当前证据支持“STFT 对低 SNR 可能有补充价值”的弱结论。
- 当前证据不支持“融合模型全面优于 baseline”的强结论。

### 下一步计划

- 如果目标是强化低 SNR 证据，进入 Stage 3.1：low-SNR weighted loss / SNR-balanced sampler。
- 如果目标是尽快完成课程报告，可以进入 Stage 5.0：结课报告初稿生成。

## 2026-05-07 Stage 3.5：文献调研、工作量表达与创新点规划

### 本次目标

- 将 AMC 相关 arXiv 论文和 GitHub 仓库调研结果整理成可引用的项目文档。
- 明确结课报告中如何体现工程工作量、实验工作量和分析工作量。
- 基于 Stage 3 full 结果选择后续最合适的创新点，不盲目增加复杂模型。

### 本次完成

- 新增 Stage 3.5 文档，整理 30 篇 arXiv 相关论文和 12 个相关 GitHub 仓库。
- 将相关工作归纳为 I/Q baseline、时频/多视图、低 SNR 鲁棒性、轻量化/可复现工程 4 条主线。
- 固定后续最推荐创新点：low-SNR weighted loss / SNR-balanced sampler、prediction-level 误差分析、成本感知时频特征分析、subset-to-full generalization gap 和多视图输入体系。
- 更新 README 的 Workload and Innovation Plan 摘要。
- 更新阶段索引和下一阶段提示词。

### 修改/新增文件

- `docs/stages/STAGE_035_WORKLOAD_INNOVATION_PLAN.md`
- `README.md`
- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`

### 当前结论

- 当前最适合体现新增工作量的方向是 Stage 3.1：low-SNR weighted loss 或 SNR-balanced sampler。
- 若课程时间有限，当前材料已经足够进入 Stage 5.0 结课报告初稿。
- 暂不建议进入 RadioML2018.01A，也不建议引入 Transformer 或强跑 full CWT。
