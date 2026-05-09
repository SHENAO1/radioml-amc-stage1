# 04 · 决策日志（ADR）

<!-- 追加型文档。每次做出架构/技术/流程上的决策，在顶部加一条。 -->

> 删除决策 = 删历史。作废的决策写”推翻先前决策（见 YYYY-MM-DD 条目）”而不是移除。

---

## 2026-05-09 · A 方案：fusion_cldnn_stft + 信号域增强 + label smoothing 作为单次组合实验

**背景**: P1.1（延长 budget）和 P2.5（SNR 加权 CE）均得到负结果，论文 fusion 叙事仍停留在"trade-off"层面。需要在投入下一项实验前先做文献校准（结果落在 `docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md`）。文献核心结论：
- RML2016.10A 平均-跨-SNR 真实 SOTA 约 0.63–0.65（LENet-M 0.6463、SigFormer 0.6371、ICRNNA 0.6324、CC-MSNet 0.6286 等）；我们的 CLDNN 0.6129 离 SOTA 还有 2–3 pp，存在改进空间。
- 文献中"涨点"路径分三族：架构升级（复值网络 / Transformer 混合 / 强 backbone）、信号域增强（phase rotation + time shift；图像式 mixup 不可用）、超参（label smoothing 0.1 等）。
- 我们的 fusion_iq_stft MACs (2.0 M) 比 ResNet1D (4.9 M) 还少（P1.2 已证），所以 fusion 输 cldnn 是 backbone 容量不足，不是算力不足。

**选项**:
- A: 单次跑组合干预（架构升级 + 增强 + label smoothing）。如成功则论文叙事翻盘；如失败则三重负面证据更硬。
- B: 串行单点干预（先 fusion_cldnn_stft，再单独加增强，再单独加 ls）。证据更干净但成本三倍且每点边际收益小。
- C: 投复值 CLDNN（CCLDNN），文献最一致涨点路径，但需写半天复值层代码。
- D: 不再做实验，直接定稿。

**决策**: 选择 A。组合三个独立干预到一个 evidence label `FUSION_CLDNN_STFT_AUG_LS_3090` 下，单次训练判定。

**理由**:
1. 时间预算有限；A 一次训练（~1 小时）就能同时回答"架构、数据、超参"三个 reviewer 关切。
2. P1.1 和 P2.5 已经把"单一干预无效"立得很稳，再做单点对比的边际信息少；A 的设计就是要打组合拳，无论结果正负都比单点更有说服力。
3. C 复值 CLDNN 代码量大且与现有 trainer / loss factory / 数据流 接口冲突大，留作将来工作。

**影响**:
- 新增模型 `fusion_cldnn_stft`：CLDNN-style I/Q encoder（CNN+LSTM 去掉分类头）+ STFT 2D-CNN 分支 + 融合 MLP 头。
- 新增 train-only 信号域增强（phase rotation θ~U(-π,π), prob 0.5；cyclic time shift k~U(-8,+8), prob 0.5）。**仅训练集启用**，验证集和测试集不增强；**跳过** amplitude scaling 与 additive noise 以避免与 SNR 标签矛盾。
- Loss factory 新增 `label_smoothing` 参数：`build_criterion({"name": "ce", "label_smoothing": 0.1})` → `nn.CrossEntropyLoss(label_smoothing=0.1)`，与现有 plain CE 与 SnrWeightedCE 路径并列。
- 新 evidence label `FUSION_CLDNN_STFT_AUG_LS_3090` 写入 `PAPER_STAGE_INDEX.md` 的 policy；新输出根 `results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/`，不污染 Stage 5A/5B、P1.1、P2.5 现有 artefacts。

**状态**: 生效；文献依据见 `docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md`。

## 2026-05-09 · 三个新 evidence label 与 trainer 可选 loss 钩子

**背景**: P1.1 之后串行完成 P1.3（低 SNR 混淆）、P1.2（FLOPs/CPU 延迟）、P2.5（SNR 加权 CE）。需要把三类新证据与 Stage 5A 严格分开，并给 trainer 加钩子接入 SNR-aware loss。

**选项**:
- A: 把所有新证据合并到 Stage 5A `complexity_latency_table.csv` / aggregate 主表，统一报告。
- B: 每类新证据用独立 evidence label + 独立输出根，原 Stage 5A 不动；trainer 加可选钩子，向后兼容。

**决策**: 选择 B。新 label 三个：
- `CONTROLLED_LATENCY_EXTENDED`：与 `CONTROLLED_LATENCY` 同 PyTorch/CUDA，但 device=CPU；MACs/FLOPs/CPU 延迟独立文件。
- `LOW_SNR_WEIGHTED_CE_3090`：SNR 加权 CE 干预实验，独立 status/report/output root。
- 低 SNR 混淆矩阵复用原 `PROJECT_SUPPORTED` 标签（仅是 Stage 5A predictions 的后处理），但物理上保存到 `results/paper_stage6/low_snr_confusion_extended/` 而非 Stage 5B aggregate 目录。

**理由**:
1. Stage 5A/5B 的 27 份 predictions 与统计检验已冻结，任何新数据都不能直接污染主表。
2. trainer 钩子（`train.loss`、`train.scheduler`）默认 `None`，对 Stage 5A 复现完全向后兼容；但允许后续 P2.x 候选实验使用同一份 trainer 而不需要分支代码。
3. 每个新 label 在 `PAPER_STAGE_INDEX.md` 的 Evidence Label Policy 段都明确列出"可写入 Section X.x"，避免 manuscript 误用。

**影响**:
- 新增 `src/radioml_amc/training/losses.py`（loss factory + SNR-aware CE）。
- Trainer 在两个挂钩点（`build_criterion(train_cfg.get("loss"))`、`compute_loss(criterion, logits, y, snr_dev)`）保持 backward compatible。
- 新增 6 份 P2.5 best_model.pt + 12 份 P1.1 best_model.pt 留在服务器；未来如需本地归档，按既有策略（单独 archive 路径 + hash-check）。
- Manuscript Section 7 已分别接收 7.7（budget 干预）和 7.8（loss 干预）两个 sensitivity 段落；Section 5.2.A 和 5.4.A 是 addendum 而非主节修改。

**状态**: 生效

## 2026-05-09 · P1.1 扩展训练 budget 走独立 evidence label，不修改 Stage 5A

**背景**: 用户希望评估 Stage 5A 的 epoch=20 budget 是否欠训练。原服务器（RTX 4070）已停用，新租实例为 RTX 3090（Ampere sm_86），与 Stage 5A 的 RTX 4070（Ada sm_89）架构不同。

**选项**:
- A: 把 P1.1 结果合并进 Stage 5A 主表，用更高的 epoch budget 重新报告。
- B: 把 P1.1 结果作为独立 evidence label `EXTENDED_BUDGET_3090`，单独输出根 `results/paper_stage6/extended_budget_3090/`，仅作为 sensitivity / robustness check 引用。

**决策**: 选择 B。

**理由**:
1. 硬件架构变化（Ada → Ampere）会导致 cuDNN kernel 选择差异，相同 seed 也无法位级复现 Stage 5A 输出，paired bootstrap/McNemar 不能跨硬件直接做。
2. LR schedule 也同时变化（constant 1e-3 → cosine + warmup 5），与 Stage 5A 不能等价比较。
3. Stage 5A/5B 已经是 frozen evidence package，预测档、统计检验和 manuscript 引用都基于其原始数值。

**影响**:
- Trainer 新增可选 `train.scheduler`（cosine + warmup）参数，默认 `None`，对 Stage 5A 复现完全向后兼容。
- 新增 `configs/paper/rml2016a_extended_budget_3090.yaml`、`scripts/paper/run_extended_budget_training.py`、`docs/paper/PAPER_STAGE6_EXTENDED_BUDGET_*.md`、`docs/paper/manuscript/section7_7_training_budget_sensitivity.md`。
- Manuscript 中 Section 7.7 明确该证据等级与硬件 confound，避免与主表混用。

**状态**: 生效

## 2026-05-09 · AI 助手回复语言统一为简体中文

**背景**: 用户明确要求后续开发协作中助手的回复使用中文。

**选项**:
- A: 默认英文，遇到中文提问时再切回中文。
- B: 强制简体中文，仅代码/命令/路径/英文专有名词保留原样。

**决策**: 选择 B。三个助手入口文件（`CLAUDE.md`、`AGENTS.md`、`.github/copilot-instructions.md`）顶部均显式声明，并在 `02-conventions.md` 的”AI 助手协作约定”中作为第一条写入。

**理由**: 用户母语为中文，统一语言降低沟通成本；术语层面保留英文可避免与代码、日志、manifest、evidence label 失配。

**影响**: 后续新增 Markdown 默认中文撰写；既有英文审计文档（如 `EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_*.md`）不强制翻译，避免破坏证据链与 manifest 引用。

**状态**: 生效

## 2026-05-09 · 使用 `.ai-context/` 作为跨助手主上下文

**背景**: 项目已经有 `docs/session_state.md` 等 durable context，但 Claude Code、Codex 和 GitHub Copilot 需要统一入口，避免每次切换助手都重新解释当前状态。

**选项**:
- A: 继续只维护 `docs/session_state.md`。
- B: 用 `ai-handoff-init` 生成 `.ai-context/` 和三个 thin entry files。

**决策**: 选择 B。`CLAUDE.md`、`AGENTS.md`、`.github/copilot-instructions.md` 指向 `.ai-context/`，`docs/session_state.md` 改为兼容跳转。

**理由**: `.ai-context/` 同时覆盖静态项目背景、动态 baton、ADR、session log 和 known issues，更适合跨助手长期维护。

**影响**: 新增 `.ai-context/` 9 个文件和 3 个助手入口文件；后续 session start/end 以 `.ai-context/05-current-state.md` 和 `06-session-log.md` 为准。

**状态**: 生效

## 2026-05-09 · 保持 Stage 5A/5B evidence boundary，不合并 diagnostic

**背景**: 当前 manuscript drafting 依赖 Stage 5A/5B full RadioML2016.10A 证据，同时存在 Stage 6B smoke/diagnostic 输出。

**选项**:
- A: 把所有已有结果都放进同一主表。
- B: 严格按 evidence label 使用结果。

**决策**: 选择 B。`PROJECT_SUPPORTED` 才能进入有边界主表；`SMOKE TEST` 和 `DIAGNOSTIC` 只用于工程或诊断说明。

**理由**: 混合不同证据等级会直接破坏论文结论可信度，尤其是 tiny subset 或 mock 输出不能代表 full dataset。

**影响**: Manuscript、tables、figures、统计检验和回复都必须显式区分证据等级；Stage 6B 不写入 Stage 5A/5B aggregate。

**状态**: 生效

## 2026-05-09 · 新训练必须先有显式 protocol 和输出根目录

**背景**: 本地环境无 CUDA，服务器可训练但已有 Stage 5A/5B artifacts 不能被覆盖。

**选项**:
- A: 需要时直接运行训练脚本。
- B: 只有在用户明确授权 protocol、模型、数据范围、seed、输出 root 和 evidence label 后才运行。

**决策**: 选择 B。

**理由**: 训练输出可能覆盖关键证据或引入无法解释的结果；protocol-first 能保证可复现性和结论边界。

**影响**: 后续任何 full、subset、tiny subset、RadioML2018.01A 或 diagnostic run 都必须先记录 protocol，并使用新的输出根目录。

**状态**: 生效

## 2026-05-09 · Stage 5A 权重同步只进入单独 archive/package 路径

**背景**: 27 个 Stage 5A `best_model.pt` 仍在服务器，本地已同步 predictions archive 和统计 artifacts，但本地 Stage 5A result tree 没有完整权重矩阵。

**选项**:
- A: 把服务器权重直接同步回本地 `results/`。
- B: 如需权重，先同步到单独 archive/package 路径并 hash-check。

**决策**: 选择 B。

**理由**: 直接覆盖 `results/` 或 Stage 5A/5B roots 容易破坏既有证据树；单独归档更安全。

**影响**: 后续若需要本地 inference、resume 或完整归档，必须先建立权重 archive 并生成 manifest。

**状态**: 生效
