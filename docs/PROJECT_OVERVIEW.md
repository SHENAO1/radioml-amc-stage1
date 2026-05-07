# 项目总览：RadioML 自动调制识别阶段化实验工程

## 1. 项目背景

本项目面向无线电自动调制识别 AMC，是机器学习结课作业的阶段化实验工程。当前先完成可复现实验闭环，后续希望扩展为会议或 SCI 论文级实验，包括真实数据 baseline、时频特征、多视图融合、低 SNR 鲁棒性和跨数据集验证。

## 2. 当前研究题目

《基于时频特征与深度神经网络融合的无线电调制识别方法研究——以 RadioML2016.10A 与 RadioML2018.01A 数据集为例》

## 3. 项目总体路线

- Stage 1：本地 mock 工程闭环。
- Stage 1.5：RadioML2016.10A 真实数据 baseline。
- Stage 2：STFT/CWT 时频分支与多视图融合。
- Stage 3：低 SNR 鲁棒性与消融实验。
- Stage 4：RadioML2018.01A 扩展验证。
- Stage 5：论文撰写与投稿材料整理。

## 4. 当前工程结构

- `src/`：核心 Python 包，包含数据读取、划分、模型、训练、指标、可视化和报告逻辑。
- `scripts/`：命令行入口，包括数据检查、可视化、训练、评估、报告和 baseline 对比。
- `configs/`：阶段配置文件，区分 mock、本地真实 subset 和服务器真实 full。
- `reports/`：正式报告模板或可复用报告结构。
- `docs/`：阶段过程文档、进展日志、实验摘要和下一阶段提示词。
- `runs/`：每次运行产物，包括 metrics、plots、checkpoint、logs，不进入 Git。

## 5. 数据策略

- 本地先使用 mock 数据验证工程链路。
- 然后使用 RadioML2016.10A subset 做小规模真实数据测试。
- 服务器上使用 RadioML2016.10A full 做正式 baseline 训练。
- 后续再考虑 RadioML2018.01A 扩展验证。
- 数据集不进入 Git，必须手动放置或在服务器下载。

## 6. 实验记录策略

- `runs/` 保存每次运行产物。
- `docs/` 保存阶段过程、风险、下一步计划和实验摘要。
- `reports/` 保存偏正式实验报告结构。
- `docs/EXPERIMENT_LOG.md` 保存实验摘要表。
- `docs/NEXT_STAGE_PROMPTS.md` 保存下一阶段提示词，便于继续交接给 Codex。
