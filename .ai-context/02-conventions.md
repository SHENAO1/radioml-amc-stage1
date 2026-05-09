# 02 · 代码与协作约定

<!-- 静态文档。团队约定变更时更新。 -->

## 代码风格
- Python 代码优先保持现有风格：类型清晰、函数职责单一、配置驱动，不为一次性实验引入大框架。
- Markdown 文档使用简洁标题和证据路径；实验结论必须能追溯到具体 run、aggregate、manifest 或 audit record。
- 新增复杂逻辑时补测试；只改文档时不运行训练，必要时运行 `git diff --check`。

## 命名约定
- 阶段文档使用 `STAGE_*` 或 `PAPER_STAGE*` 前缀，保持与现有 `docs/` 体系一致。
- 结果 evidence label 只使用已定义语义：`PROJECT_SUPPORTED`、`CONTROLLED_LATENCY`、`SMOKE TEST`、`DIAGNOSTIC`。
- 模型名保持现有 slug。Stage 5A 主表覆盖的 9 个模型为：`cnn1d`、`resnet1d`、`cldnn`、`mcldnn`、`lwamcnet`、`tfcnn_stft`、`iq_param_matched`、`fusion_iq_stft`、`gated_fusion_iq_stft`；subset 消融另含 `fusion_iq_stft_cwt`（full CWT 在 RTX 4070 上 optional skipped）。

## 目录约定
- 代码进 `src/radioml_amc/`，命令行入口进 `scripts/`，实验配置进 `configs/`，文档和 manuscript 进 `docs/`。
- `runs/` 用于开发 run 输出，`results/` 用于 paper-stage structured evidence，`paper_package/` 用于同步和归档包。
- 不把数据集、checkpoint、大型 prediction 文件、`.venv/`、Kaggle token 或临时缓存纳入 Git。

## 提交与分支
- 当前内层仓库分支是 `paper-sci-track`；外层目录仍把 `radioml-amc-stage1/` 视为未跟踪目录。
- 本次上下文初始化不 stage、不 commit、不 push。后续提交前必须先审查 `git status --short`，避免误提交 `results/`、`paper_package/`、`runs/` 或权重。
- 不回滚既有脏文件，除非用户明确要求。

## 测试策略
- 代码或脚本改动优先运行相关 pytest、`python -m compileall -q src scripts` 和 `git diff --check`。
- 文档/上下文-only 改动只需检查目标文件存在、入口文件足够薄、Markdown 无尾随空白。
- 新训练或 diagnostic 不属于测试步骤；必须由明确 protocol 单独授权。

## AI 助手协作约定
- **回复语言**：所有面向用户的回复、解释、总结、状态更新一律使用简体中文；代码、命令、文件路径、英文专有名词（如模型名、`PROJECT_SUPPORTED` 等 evidence label、库名）保持原样。新增 Markdown 文档默认中文撰写；既有英文文档（如 `EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_*.md`）不强制翻译。该规则于 2026-05-09 由用户明确要求。
- 进入会话先读 `.ai-context/05-current-state.md` 和 `.ai-context/06-session-log.md` 顶部条目；旧 `docs/session_state.md` 只作为兼容跳转。
- 会话结束更新 `05-current-state.md`，并在 `06-session-log.md` 顶部追加一条新记录。
- 架构、依赖、训练协议、证据边界或同步策略改变时，在 `04-decisions.md` 顶部追加 ADR。
- 不确定的实验事实必须从 `docs/`、`results/`、`paper_package/` 或 run artifact 查证，不能依赖聊天历史。
- Mock、subset、diagnostic 和 full evidence 必须在回复与文档中明确区分。
