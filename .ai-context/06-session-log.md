# 06 · 会话日志

<!-- 动态文档。每次会话结束在最上方追加一条。**新的在上**。 -->

> **条目格式 / Entry format**:
>
> ```
> ## YYYY-MM-DD · <助手名 / Assistant name>
> **完成 / Done**: ...
> **进行中 / In progress**: ...
> **下一步建议 / Next**: ...
> **注意 / Watch out**: ...
> ```
>
> **归档规则**: 当本文件条目超过 20 条时，把较早的一半移动到 `06-session-log-archive.md`
>（或按月切片到 `archive/YYYY-MM.md`）。这是为了避免文件超过 Claude Code 单文件 40,000
> 字符上限，同时降低 Codex 的 `project_doc_max_bytes` 截断风险。

---

## 2026-05-09 · Claude Code (A 方案完成：fusion_cldnn_stft + aug + LS — **POSITIVE**)
**完成 / Done**:
- 实现 `CLDNNIQBranch`（CLDNN encoder 去掉分类头，输出 128-D embedding）和 `FusionCldnnStftNet`（CLDNN-style I/Q + 2D-CNN STFT + fused MLP，286k 参数）。
- 新增 `src/radioml_amc/data/augmentation.py`：信号域 `SignalAugmenter`（phase rotation θ~U(-π,π) prob 0.5；cyclic time shift k~U(-8,+8) prob 0.5）+ `build_augmenter` factory。
- `SignalDataset` 加可选 `augmenter` 参数；trainer 的 `_make_loaders` 加可选 `augment_config` 参数，**只对 train loader 创建带 augmenter 的 dataset**，val/test loader 共享原 dataset；默认行为不变。
- Loss factory `build_criterion` 支持 `label_smoothing` 字段：`{"name":"ce","label_smoothing":0.1}` → `nn.CrossEntropyLoss(label_smoothing=0.1)`。
- 新增 config `configs/paper/rml2016a_fusion_cldnn_stft_aug_ls_3090.yaml`、orchestrator `scripts/paper/run_fusion_cldnn_stft_aug_ls_training.py`。Evidence label `FUSION_CLDNN_STFT_AUG_LS_3090`，独立输出根。
- Smoke check 通过：`fusion_cldnn_stft(2,2,128)` → `[2,11]`，286k 参数，CUDA forward + augmenter + LS CE 全部 OK。
- Tmux session `pa` 跑完 3 cells × 50 epoch，27.4 分钟，0 失败。

**Headline 结果**（mean across 3 seeds）:
| Metric | A 方案 | Stage 5A CLDNN | Δ |
|---|---:|---:|---:|
| Overall | **0.6264** (σ=0.0005) | 0.6129 | **+0.0135** |
| Low-SNR | **0.2258** (σ=0.0008) | 0.2224 | +0.0034 |
| Mid-SNR | **0.8606** (σ=0.0009) | 0.8396 | +0.0210 |
| High-SNR | **0.9264** (σ=0.0003) | 0.9070 | +0.0194 |

- **All four metrics positive**；27× seed std 远大于 +0.0135 增量，结果稳健。
- 与 P1.1 同 schedule fusion_iq_stft 比 +4.13 pp overall，证实是 backbone + 增强 + LS 的组合贡献。
- 与 2024 论文 SOTA 对比：贴近 CC-MSNet (0.6286)、CCTL-Net (0.6297)，距 LENet-M (0.6463) / SigFormer (0.6371) 仍 1-2 pp。
- 深低 SNR (-20 至 -16 dB) 仍 chance level → 信息论下限，非模型容量问题（P1.3 已证）。

- 新增分析 `PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_ANALYSIS.md`、manuscript **Section 5.6** `section5_6_proposed_fusion_cldnn_stft.md`（项目正面贡献章节）。
- `PAPER_STAGE_INDEX.md` 加 A 方案行 + `FUSION_CLDNN_STFT_AUG_LS_3090` evidence label policy。

**进行中 / In progress**: A 方案是 3 干预 stacked 单次实验，**未做 per-intervention 消融**，作为已知 limitation 在 manuscript 5.6 末段注明。

**下一步建议 / Next**:
- 可选下一项：3-run 消融（architecture-only / +aug / +LS）拆 +0.0135 各自贡献，每个 ~30 分钟训练。
- 可选定稿：拼合 manuscript（Section 4 + 5.1-5.5 + 5.2.A + 5.4.A + 5.6 + 6 + 7.1-7.6 + 7.7 + 7.8）+ figures/tables inventory + 冻结 evidence package。
- 不再做实验也是合理选项，因为 A 方案已经把 fusion 叙事翻到正面，结课报告/论文核心结论站得住。

**注意 / Watch out**:
- A 方案 GPU = RTX 3090 ≠ Stage 5A 的 RTX 4070；prediction-level paired bootstrap/McNemar 不能跨硬件直接做。3-seed-mean 比较是 manuscript 唯一支持的对比层级。
- 3 个新 best_model.pt 留在服务器，未本地归档；同 Stage 5A / P1.1 / P2.5 策略，需要时单独 archive + hash-check。

## 2026-05-09 · Claude Code (Stage 2 文献校准 + A 方案授权)
**完成 / Done**:
- 联网搜索 RML2016.10A 真实 avg-across-SNR SOTA 与超参经验：发现 LENet-M ~0.6463、SigFormer 0.6371、ICRNNA 0.6324、CC-MSNet 0.6286；我们的 CLDNN 0.6129 离 SOTA 还有 2–3 pp。
- 把"95%+"声明的真伪辨清：那些数字几乎都是高 SNR 单点 acc，不是 avg-across-SNR，不能直接对标。
- 文献给出的"涨点路径"分三族（架构 / 增强 / 超参）整理到 `docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md`，附完整 Sources。
- 与用户对齐选择 A 方案：单次组合实验 = `fusion_cldnn_stft` (CLDNN-style I/Q encoder + STFT 2D-CNN 分支) + signal-domain augmentation (phase rotation + cyclic time shift, train-only) + label smoothing 0.1。
- 在 `04-decisions.md` 顶部加 ADR；`05-current-state.md` 同步 current goal、Stage 2 literature calibration、next steps。

**进行中 / In progress**: 接下来执行 A 方案：(1) 加 `CLDNNIQBranch` + `FusionCldnnStftNet`；(2) 加信号增强 + trainer 钩子；(3) loss factory 加 `label_smoothing`；(4) config + orchestrator + 服务器训练；(5) analysis + manuscript fragment。

**下一步建议 / Next**: 若 A 成功（fusion 超过 CLDNN baseline），论文叙事翻盘，5.1/5.2/6 都需要补正面段落；若 A 失败，作为第三层负面证据进入 7.x sensitivity subsection。两种情形都不动 Stage 5A/5B。

**注意 / Watch out**:
- 信号增强**仅 train loader 启用**；val 与 test 保持原信号。
- Augmentation 不用 amplitude scaling 与 additive noise（会改变有效 SNR，与 SNR-conditioned 协议冲突）。
- Image-style mixup 在 I/Q 上不可用（[Huang et al. 2022](https://arxiv.org/abs/2204.03737) 已证伪）。
- 复值 CLDNN 是更激进的下一步（文献最一致涨点路径），但需要写半天复值层代码，留为 future work。

## 2026-05-09 · Claude Code (P1.3 + P1.2 + P2.5 串行执行)
**完成 / Done**:
- **P1.3（A，低 SNR 混淆矩阵）**：用 `scripts/paper/build_low_snr_confusion_matrices.py` 后处理 27 份 Stage 5A `predictions_test.csv`，输出 27 张 PNG（9 模型 × 3 视角：raw / normalized / per-seed）+ summary CSV/MD 到 `results/paper_stage6/low_snr_confusion_extended/`。关键发现：7/9 稳定模型在 SNR<=-6 dB 上把数字调制（8PSK/BPSK/QPSK/CPFSK/GFSK）误判成 AM-SSB 的比例 0.63-0.81，AM-SSB 自身 low-SNR acc 0.87-0.95；MCLDNN 因 seed 2025/3407 崩塌呈现 AM-DSB 偏置。
- **P1.2（B，FLOPs/MACs/CPU 延迟）**：新增 `src/radioml_amc/profiling/complexity.py` 的补充测量脚本 `scripts/paper/measure_extended_complexity_latency.py`，在服务器（EPYC 7B12, num_threads=1, torch 2.9.1+cu128）跑 thop + torch.utils.benchmark，得 9 模型 MACs / FLOPs / CPU bs1 / CPU bs256（warmup 50, measured 200）。286 秒完成，输出到 `results/paper_stage6/extended_complexity_latency/`。关键发现：MCLDNN 49 M MACs / 573 ms 最重；fusion_iq_stft 2.0 M MACs 比 ResNet1D 4.9 M 还少；lwamcnet 参数最少但 CPU 最慢（depthwise/grouped 在单线程 CPU 上不划算）。
- **P2.5（C，SNR 加权 CE）**：新增 `src/radioml_amc/training/losses.py`（`SnrWeightedCrossEntropy` + `build_criterion` + `compute_loss`），trainer 接入 `train.loss` 配置，向后兼容 Stage 5A（无 cfg = plain CE）。新增 `configs/paper/rml2016a_low_snr_weighted_ce_3090.yaml`（low=2.0, mid=1.0, high=0.7）和 orchestrator `scripts/paper/run_low_snr_weighted_ce_training.py`。tmux 跑完 6 cells（cldnn + fusion_iq_stft × 3 seed），22.8 分钟，0 失败。
- 三份分析文档：`PAPER_STAGE6_LOW_SNR_CONFUSION_ANALYSIS.md`、`PAPER_STAGE6_EXTENDED_COMPLEXITY_ANALYSIS.md`、`PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_ANALYSIS.md`。
- 三份 manuscript 子节：`section5_2_addendum_low_snr_per_class.md`、`section5_4_addendum_complexity_latency_filled.md`、`section7_8_low_snr_weighted_ce_outcome.md`。
- `PAPER_STAGE_INDEX.md` 增加 3 个 Stage 6 子阶段行 + 3 个新 evidence label policy。

**P2.5 关键结果（mean 跨 3 seed）**:
- cldnn: ΔOverall vs Stage 5A = -0.0233; ΔLow-SNR = +0.0058
- fusion_iq_stft: ΔOverall vs Stage 5A = -0.0067; ΔLow-SNR = +0.0042
- 低 SNR 涨幅集中在 -8 至 -4 dB 转折区；-20 至 -16 dB 仍 ~chance level (0.09-0.11)；说明简单 2× 加权改不动深度低 SNR 的崩塌。

**进行中 / In progress**: 等用户决定下一步——继续 P2.x（focal/continuous SNR weighting、augmentation、复值网、P2.4 `fusion_cldnn_stft`），或转 RadioML2018.01A subset，或冻结证据包定稿。

**下一步建议 / Next**:
- **若定稿**：将 Section 5.1-5.5 + 6 + 7 + 5.2.A + 5.4.A + 7.7 + 7.8 拼合，列出 figures/tables inventory，冻结 evidence package。
- **若继续实验**：必须先注册新 evidence label + 新输出根；不要碰 Stage 5A/5B、P1.1、P1.2、P1.3、P2.5 现有 artefacts。

**注意 / Watch out**:
- 18 个 best_model.pt（P1.1 12 + P2.5 6）仍在服务器，未本地归档；同 Stage 5A 策略：单独 archive 路径并 hash-check。
- 服务器 i-1.gpushare.com:62244 仍在租用；不再用建议销毁实例或改密。
- `scripts/_remote_*.py`、`_uncommitted_code.tar.gz` 是带口令的本地辅助文件，**不进 Git**。

## 2026-05-09 · Claude Code (P1.1 extended-budget robustness check)
**完成 / Done**:
- 在新租用的 gpushare 实例 `i-1.gpushare.com:62244`（RTX 3090 24 GB, Ubuntu 22.04, Python 3.11.12, PyTorch 2.9.1+cu128, NVIDIA driver 570.211.01）上完整部署项目：把本地 `paper-sci-track` 分支推到 GitHub、SFTP 同步 59 个未提交文件、上传数据集 `RML2016.10a_dict.pkl` 612 MB（MD5 `61bf35ac7f0b7d8843613453447ea290`）、安装 scipy/sklearn/matplotlib/pandas/pywavelets/thop/pytest/tqdm 并 `pip install -e .`、过 mock smoke 与 GPU forward+backward 验证。
- 给 trainer 加了**可选** `train.scheduler` 配置（cosine + 线性 warmup），默认行为不变，向后兼容 Stage 5A。
- 新增 `configs/paper/rml2016a_extended_budget_3090.yaml` 和 `scripts/paper/run_extended_budget_training.py`：epoch 50、warmup 5、cosine LR、early-stop patience 15、独立输出根 `results/paper_stage6/extended_budget_3090/rml2016a/`，evidence label `EXTENDED_BUDGET_3090`，仅跑 4 个模型 × 3 seed。
- 在 tmux 中跑完 12/12 cells，0 失败，54.4 分钟。`docs/paper/PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md`（自动生成）和 `docs/paper/PAPER_STAGE6_EXTENDED_BUDGET_ANALYSIS.md`（分析附录）已落地，新增 manuscript subsection `docs/paper/manuscript/section7_7_training_budget_sensitivity.md`。
- 关键发现：ΔOverall 全部在 ±1 pp 内（ranking 保持，`cldnn` 仍最强）；ΔLow-SNR 全部为负（最大跌幅在 `fusion_iq_stft`，−0.89 pp）；best_epoch：`resnet1d` 15–20（≤Stage 5A 边界）、`cldnn` 23–27、`iq_param_matched` 21–27、`fusion_iq_stft` 34–42。

**进行中 / In progress**: 等待用户决定下一步（P1.2 FLOPs+CPU latency、P1.3 低 SNR 混淆矩阵、或 P2.5 低 SNR 加权 CE 训练）。

**下一步建议 / Next**:
- 推荐顺序为 P1.3（纯后处理 Stage 5A predictions，最快闭合 manuscript 空缺）→ P1.2（thop + torch.utils.benchmark 补全 complexity_latency_table.csv）→ P2.5（loss factory + 重训）。
- P2.5 是更高 ROI 的方向，因为 P1.1 已经证明仅延长 budget 不能救低 SNR，反而伤害低 SNR；改 loss 信号才是对症方案。
- 12 个新 `best_model.pt` 仍在服务器，未本地归档；与 Stage 5A 保持同样策略，需要时单独归档并 hash-check。

**注意 / Watch out**:
- Stage 5A/5B 主表、低 SNR 表、paired statistical tests 不能被新数据污染；P1.1 全部走独立 evidence label `EXTENDED_BUDGET_3090` 与独立输出根。
- 本轮 GPU 从 4070 (Ada sm_89) 换成 3090 (Ampere sm_86)，cuDNN kernel 选择可能不同，因此与 Stage 5A 的 paired bootstrap/McNemar 不能跨硬件直接做。
- `scripts/_remote_*.py` 是含口令通过 argv 注入的本地辅助脚本，**不应进入 Git**；服务器密码已通过聊天传输，使用结束后建议销毁实例或改密。

## 2026-05-09 · Codex
**完成 / Done**: 使用 `SHENAO1/ai-handoff-init` 初始化 `.ai-context/`、`CLAUDE.md`、`AGENTS.md` 和 `.github/copilot-instructions.md`；将 `docs/session_state.md` 的 baton 迁移到 `.ai-context/05-current-state.md`；补全 overview、architecture、conventions、glossary、ADR 和 known issues。  
**进行中 / In progress**: Manuscript drafting 和 artifact packaging 仍处于 evidence-boundary guardrails 下。  
**下一步建议 / Next**: 若继续实验，先决定是否单独归档 27 个 Stage 5A server `best_model.pt`；若继续写作，只使用 Stage 5A/5B `PROJECT_SUPPORTED` evidence 支撑主表结论。  
**注意 / Watch out**: 当前内层仓库已有大量既有脏文件；不要回滚无关改动，不要误提交 `results/`、`paper_package/`、`runs/` 或 checkpoint。

## 2026-05-08 · Prior Baton
**完成 / Done**: 完成环境与同步审计；记录本地 CPU 环境、服务器 RTX 4070 环境、prediction archive、statistical-test archive、manuscript drafts 和未同步权重状态。  
**进行中 / In progress**: Evidence-bounded manuscript drafting。  
**下一步建议 / Next**: 若需要本地完整权重归档，先同步 27 个服务器 `best_model.pt` 到单独 archive/package path 并 hash-check。  
**注意 / Watch out**: No training, no tiny subset, no RadioML2018.01A, no Stage 5A/5B overwrite; Stage 6B diagnostic remains excluded from main tables.
