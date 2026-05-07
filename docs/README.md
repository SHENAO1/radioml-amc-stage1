# docs 文档体系说明

`docs/` 用于记录 RadioML AMC 项目的阶段过程、工程进展、实验摘要、风险和下一阶段计划。该目录适合进入 Git，用于后续复盘、交接和继续实验。

## 1. 目录用途

- `docs/`：阶段过程管理、项目进展、下一阶段计划、实验摘要，进入 Git。
- `reports/`：实验报告模板或偏正式报告结构，可用于结课作业和论文草稿。
- `runs/`：每次运行的真实产物，包括 metrics、plots、checkpoint、logs，不进入 Git。

## 2. 顶层文档作用

- `PROJECT_OVERVIEW.md`：项目背景、研究题目、总体路线、工程结构和数据策略。
- `STAGE_INDEX.md`：所有阶段的状态索引和下一步。
- `PROGRESS_LOG.md`：按日期记录阶段推进过程、命令和问题。
- `EXPERIMENT_LOG.md`：按实验 ID 汇总关键指标和 run_dir。
- `NEXT_STAGE_PROMPTS.md`：保存每个阶段结束后可直接给 Codex 的下一阶段提示词。

## 3. stages/ 阶段文档作用

- `STAGE_TEMPLATE.md`：后续阶段过程文档模板。
- `STAGE_01_LOCAL_MOCK_ENGINEERING.md`：第一阶段本地 mock 工程闭环记录。
- `STAGE_015_RML2016A_BASELINE.md`：阶段 1.5 RadioML2016.10A baseline 接入记录。

## 4. reports/ 与 docs/ 的区别

`reports/` 和 run 内的报告偏实验结果，记录某次实验或某个 run 的指标、图表路径和模型对比，可进入课程报告或论文草稿。

`docs/stages/` 偏过程管理，记录阶段定位、目标、完成项、未完成问题、风险、验收标准和下一阶段提示词。二者都保留，不能互相替代。

## 5. runs/ 与 docs/ 的区别

`runs/` 保存每次运行的真实产物，包括 `metrics.json`、`metrics.csv`、`best_model.pt`、`plots/` 和 `logs.txt`。这些文件可能很大或频繁变化，不进入 Git。

`docs/` 只记录摘要和相对路径，例如 `runs/20260507_120214_cnn1d/plots/confusion_matrix.png`，不嵌入图片或 checkpoint。

## 6. 阶段结束后如何更新

每个阶段结束时至少更新：

- `docs/STAGE_INDEX.md`
- `docs/PROGRESS_LOG.md`
- `docs/EXPERIMENT_LOG.md`
- `docs/NEXT_STAGE_PROMPTS.md`
- 对应的 `docs/stages/STAGE_*.md`

如果有新 run，只记录 run_dir、关键指标和图表路径。mock run 必须标注为工程 smoke test，不能写成正式实验结论。

## 7. 文档中允许记录什么

- 阶段目标、范围限制和验收标准。
- 执行过的关键命令。
- run_dir、报告路径、图表相对路径。
- `overall_accuracy`、per-SNR accuracy、per-class accuracy 等摘要。
- 当前问题、风险和下一步计划。
- 下一阶段提示词。

## 8. 文档中不允许记录什么

- RadioML 数据集内容或大文件。
- checkpoint、`.pt`、`.pth`、`.pkl`、`.bz2` 等二进制内容。
- 完整训练日志的大段复制。
- 图片二进制或 base64。
- Kaggle token、服务器密钥或本地绝对数据路径。
- 将 mock 结果包装成真实实验结论。
