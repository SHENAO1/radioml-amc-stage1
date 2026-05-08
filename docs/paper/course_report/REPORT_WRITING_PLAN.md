# Course Report Writing Plan

报告标题：基于时频特征与深度神经网络融合的无线电调制识别方法研究

本文件只规划课程报告正文写作，不生成完整正文。本报告的所有 claim 必须绑定已有 evidence source；不得启动新实验、重建主表或把 Stage 6B smoke/diagnostic 混入主结果。

## 全局证据边界

- 主实验范围：RadioML2016.10A，固定划分 `stratified_by_mod_snr_seed42`，9 个模型行，3 个训练种子 `42;2025;3407`。
- 主结果证据：`main_table_metrics.csv`、`low_snr_table.csv`、`complexity_latency_table.csv`。
- 统计检验证据：`paired_bootstrap_accuracy_deltas.csv`、`mcnemar_tests.csv`，均来自 Stage 5A archived predictions。
- 归档证据：paper package manifest、predictions archive manifest、environment/sync status。
- 排除边界：Stage 6B smoke/diagnostic 只能作为工程或未来诊断边界，不得作为主结果。

## 章节计划

| 章节 | 每章目标 | 可使用 evidence source | 可写 claim | 禁止 claim | 应生成的表格/图 |
|---|---|---|---|---|---|
| 摘要 | 概括任务、协议、模型矩阵、主要观察与边界。 | Section 4-7 manuscript drafts；main/low-SNR/statistical/latency tables；manifest/env。 | 固定协议内完成 9 模型 x 3 seed 比较；结论为 protocol-bounded。 | SOTA；跨数据集泛化；广义 fusion/gated 优越；deployment superiority。 | 无，摘要不放表图。 |
| 第 1 章 绪论 | 说明 AMC 背景、I/Q 与 STFT 动机、课程报告研究问题。 | `section4_experimental_protocol.md`；`section6_discussion.md`。 | 本报告关注固定 RadioML2016.10A 协议下时域、时频和融合模型对比。 | RadioML2018.01A 结果；未验证工程部署优势；SOTA。 | 可生成“研究流程/证据边界”示意图。 |
| 第 2 章 数据集、协议与评价指标 | 明确数据集、固定划分、模型矩阵、种子、评价指标和统计检验协议。 | `section4_experimental_protocol.md`；main/low-SNR/statistical CSV；manifest。 | 使用 fixed split；low-SNR 定义为 `snr_db <= -6`；统计检验按 split/seed/sample 配对。 | 重建 split；新增 tiny subset；删除 MCLDNN failed seeds。 | 协议概要表；模型矩阵表；评价指标说明表。 |
| 第 3 章 模型方法与融合结构 | 描述模型类别、输入视图和比较目的。 | `main_table_metrics.csv` 的 `model_id`、`input_views`、`params_*`；Section 4。 | 模型矩阵覆盖 I/Q-only、STFT-only、I/Q+STFT、temporal、lightweight、parameter-matched control。 | 证明任意结构广义更强；把 gated 写成成功鲁棒改进。 | 模型输入视图表；方法结构示意图。 |
| 第 4 章 实验结果与统计检验 | 展示主表、low-SNR trade-off、paired bootstrap、McNemar、latency 和 MCLDNN anomaly。 | `main_table_metrics.csv`；`low_snr_table.csv`；`complexity_latency_table.csv`；paired bootstrap；McNemar；Section 5.1-5.5。 | CLDNN 是本固定协议内 overall 最强观察值；static fusion 是 low-SNR trade-off；gated fusion 是本证据集负结果；MCLDNN anomaly retained。 | SOTA；fusion/gated broad superiority；Stage 6B 作为结果；deployment superiority。 | 主结果表；low-SNR 表；统计检验表；latency/complexity 表；MCLDNN seed anomaly 摘要表。 |
| 第 5 章 讨论、局限性与可复现性 | 解释协议边界、低信噪比折中、runtime 证据限制、MCLDNN 异常和归档状态。 | Section 6；Section 7；manifest；env/sync record。 | 结果为 fixed-split evidence；latency 仅为 controlled CUDA forward-pass；weights 未完整本地同步。 | CPU/FLOPs/preprocessing-inclusive latency claim；跨硬件部署结论；用 diagnostic repair Stage 5A。 | 证据类别与用途表；复现/归档状态表。 |
| 第 6 章 总结 | 收束课程作业贡献和保守结论。 | 正文已引用证据。 | 总结完成协议化比较、统计检验和证据包整理。 | 新增未在正文论证的 claim。 | 无或简表。 |
| 附录 A 证据包与实验环境 | 记录 artifact manifest、predictions archive、statistical-test package、环境和排除规则。 | `ARTIFACT_MANIFEST_PAPER_PACKAGE_20260508.csv`；`ARTIFACT_MANIFEST_PREDICTIONS_ARCHIVE_20260508.csv`；`EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`。 | package rows/hash statuses；prediction archive 为 27 files；local CPU-only，server CUDA。 | 暗示本轮新跑实验；宣称本地已有完整 Stage 5A weights。 | Manifest 摘要表；环境对比表；Stage 6B 排除规则表。 |

## 优先生成的表格

1. `tables/protocol_summary.tex`：数据集、split、seeds、模型数、low-SNR 定义、统计检验来源。
2. `tables/main_results_summary.tex`：从 `main_table_metrics.csv` 转写核心模型 overall accuracy、macro-F1、low/mid/high-SNR accuracy。
3. `tables/low_snr_tradeoff.tex`：CLDNN、fusion、iq_param_matched、gated fusion 的 low-SNR 结果与关键统计检验。
4. `tables/statistical_tests_summary.tex`：paired bootstrap 与 McNemar 的主要比较。
5. `tables/latency_complexity_summary.tex`：参数量、受控 CUDA forward latency、memory、train time。
6. `tables/evidence_package_summary.tex`：paper package、prediction archive、statistical tests、missing/diagnostic-only 项。

## 优先生成的图

1. 固定协议流程图：dataset -> split -> model matrix -> predictions archive -> statistical tests。
2. Overall/low-SNR accuracy 条形图：只使用 Stage 5A/5B aggregate evidence。
3. Accuracy-latency 散点图：明确标注 `CONTROLLED_LATENCY only`。
4. Evidence boundary 图：`PROJECT_SUPPORTED`、`CONTROLLED_LATENCY`、`SMOKE TEST/DIAGNOSTIC` 的可用范围。

## 写作顺序建议

1. 先写第 2 章，锁定协议、数据和评价指标，避免后续 claim 漂移。
2. 再写第 4 章，把结果表和统计检验绑定到证据源。
3. 然后写第 3 章方法和第 5 章讨论。
4. 最后写绪论、摘要和总结。
