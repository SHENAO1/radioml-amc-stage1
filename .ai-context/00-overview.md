# 00 · 项目概览

<!-- 静态文档。范围或目标发生重大变更时才修订。 -->

## 项目名称
radioml-amc-stage1

## 一句话描述
RadioML2016.10A AMC experiment, evidence packaging, and manuscript drafting project with strict result-boundary guardrails.

## 项目目标
- 围绕 RadioML2016.10A 自动调制识别（AMC）建立可复现的实验、分析、打包和论文写作工程。
- 维护从 Stage 1 mock 闭环、RadioML2016.10A subset/full 实验，到 Paper-Stage 5A/5B 三种子固定划分证据的完整上下文。
- 在论文写作中严格区分 `PROJECT_SUPPORTED`、`CONTROLLED_LATENCY`、`SMOKE TEST` 和 `DIAGNOSTIC` 证据，避免把诊断或 mock 结果写成主表结论。
- 支持多助手协作：Claude Code、Codex、GitHub Copilot 都通过根目录入口文件读取本目录。

## 范围边界

### 本项目做什么（In scope）
- RadioML2016.10A 的数据检查、固定划分、baseline、时频/多视图模型、低 SNR 分析、统计检验和 manuscript drafting。
- 基于已归档预测文件和聚合表进行论文级结果审计、图表整理和结论边界维护。
- 在明确 protocol 授权后，在服务器 GPU 环境执行新的 full、subset 或 diagnostic 实验。
- 维护 `docs/`、`results/`、`paper_package/` 中的证据索引、manifest、写作草稿和交接记录。

### 本项目不做什么（Out of scope）
- 不把 RadioML 数据集、`runs/`、checkpoint、`.venv/` 或 Kaggle token 提交到 Git。
- 不把 Stage 6B smoke/diagnostic 输出合并进 Stage 5A/5B 主表或统计检验。
- 不在未授权的情况下启动新训练、RadioML2018.01A、tiny subset diagnostic 或服务器同步。
- 不声称融合模型全面优于 baseline，不声称 RadioML2018.01A 已完成，不声称 SOTA。

## 成功标准
- [x] Stage 5A/5B RadioML2016.10A full fixed-split 证据可追溯到模型、seed、预测归档、统计检验和 manifest。
- [x] 当前 manuscript 草稿遵守 evidence-boundary guardrails，不新增未支持结论。
- [ ] 若需要本地完整归档，27 个服务器 Stage 5A `best_model.pt` 权重需单独同步到 archive/package 路径并 hash-check。
- [ ] 后续任何新实验都必须先有明确 protocol、输出根目录和 evidence label。

## 相关资源
- `README.md`：项目路线、阶段结果和当前建议。
- `docs/session_state.md`：旧 baton 兼容入口，已迁移为指向 `.ai-context/`。
- `docs/paper/EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`：最近一次环境与同步审计记录。
- `docs/paper/PAPER_STAGE_INDEX.md`：论文阶段索引和证据标签策略。
- `docs/paper/CURRENT_EXPERIMENT_SNAPSHOT.md`：Stage 2.2 full 结果快照和结论边界。
- `paper_package/predictions_archive_20260508`：Stage 5A 9 模型 x 3 seeds 预测归档。
