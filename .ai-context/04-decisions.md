# 04 · 决策日志（ADR）

<!-- 追加型文档。每次做出架构/技术/流程上的决策，在顶部加一条。 -->

> 删除决策 = 删历史。作废的决策写”推翻先前决策（见 YYYY-MM-DD 条目）”而不是移除。

---

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
