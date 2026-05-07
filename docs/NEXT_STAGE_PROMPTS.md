# 下一阶段提示词归档

## Stage 1 → Stage 1.5

```text
当前项目已完成 Stage 1：本地 mock 工程闭环。已有能力包括 mock 数据 smoke test、RadioML2016.10A loader 初版、CNN1D baseline、ResNet1D baseline、训练、评估、可视化、报告生成和 pytest smoke tests。已验证命令包括 check_dataset、visualize_examples、train_cnn1d、train_resnet1d、evaluate_model、make_report 和 pytest -q；pytest 输出为 .s... [100%]，其中 s 是真实 RadioML2016.10A 文件不存在时按预期 skip。

请进入 Stage 1.5：不要实现论文创新模型、STFT/CWT 训练分支或多视图融合。目标是把第一阶段从 mock 工程闭环推进到真实 RadioML2016.10A baseline 闭环：审计现有代码，确认 mock 流程仍可运行，补充 docs 过程文档体系，强化 RadioML2016.10A 自动路径检测与 .pkl/.pkl.bz2 读取能力，新增真实 subset/full 配置，固定 CNN1D 和 ResNet1D baseline 协议，生成 baseline 对比表和 stage1_5_report.md，并更新 README、.gitignore 和 pytest。

验收标准：无真实数据时 mock check/train 和 pytest 必须通过；有真实数据时 subset check、visualize、run_stage1_5_baselines 必须跑通；服务器 full 配置可直接用于全量训练。mock 结果必须标注为 smoke test，不能作为正式实验结论。
```

## Stage 1.5 → Stage 2

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 实验审计工程师。

当前阶段完成情况摘要：
- Stage 1 已完成本地 mock 工程闭环，pytest smoke tests 可通过。
- Stage 1.5 已补充 docs 过程文档体系、RadioML2016.10A 自动路径检测、.pkl/.pkl.bz2 读取、真实 subset/full 配置、CNN1D/ResNet1D baseline 协议、baseline 批量脚本、run 对比脚本、dataset/split/label/metrics 输出和 stage1_5_report.md 生成逻辑。
- 当前未检测到真实 RadioML2016.10A 数据时，真实 baseline 训练状态为 pending；如果已有真实数据，请先读取 docs/session_state.md、docs/progress.md 或 docs/PROGRESS_LOG.md，并以最新 run evidence 为准。

已有 baseline 结果摘要：
- mock CNN1D、mock ResNet1D 和 mock eval 已记录在 docs/EXPERIMENT_LOG.md，均只能作为工程 smoke test，不能作为正式实验结论。
- 如果 Stage 1.5 真实 subset/full 已运行，请从对应 run_dir 的 metrics.json、baseline_comparison.md 和 docs/EXPERIMENT_LOG.md 读取真实指标，不要依赖聊天历史。

Stage 2 主题：STFT/CWT 时频分支与 I/Q 多视图融合。

第二阶段目标：
1. 新增 STFT/CWT on-the-fly 特征接口，不离线保存全量 STFT 图片。
2. 新增时频 CNN 分支，用于处理 STFT/CWT 张量。
3. 新增 I/Q + 时频双分支或三分支融合模型。
4. 保留 CNN1D 和 ResNet1D 作为 baseline，不破坏 Stage 1.5 真实数据训练流程。
5. 新增消融实验：
   - I/Q only；
   - STFT only；
   - CWT only；
   - I/Q + STFT；
   - I/Q + CWT；
   - I/Q + STFT + CWT。
6. 重点评估低 SNR 鲁棒性，输出 overall accuracy、per-SNR accuracy、low/mid/high SNR accuracy、per-class accuracy、confusion matrix、normalized confusion matrix 和模型复杂度统计。
7. 继续更新 docs/ 阶段文档、PROGRESS_LOG.md、EXPERIMENT_LOG.md、STAGE_INDEX.md 和 NEXT_STAGE_PROMPTS.md。

第二阶段不做什么：
- 不自动下载大数据集；
- 不把 RadioML 数据集加入 Git；
- 不把 checkpoint 或 runs 产物加入 Git；
- 不离线保存全量 STFT/CWT 图片；
- 不直接引入 Transformer 或复杂注意力机制，除非 baseline 和消融已稳定；
- 不用 mock 结果冒充真实实验结果。

建议实现顺序：
1. 审计 Stage 1.5 最新代码和真实 baseline 结果。
2. 在 src/radioml_amc/features/ 中新增 on-the-fly STFT/CWT 变换接口，并补单元测试。
3. 扩展 Dataset 或 collate 逻辑，使 I/Q、STFT、CWT 可按配置动态返回。
4. 新增时频 CNN 分支和融合模型，保持接口清晰。
5. 新增 configs/stage2_* 配置，区分 mock、real subset、real full 和 ablation。
6. 新增 scripts/run_stage2_ablations.py 批量运行消融实验。
7. 生成 stage2_report.md、ablation_comparison.csv 和 ablation_comparison.md。
8. 运行 pytest -q、mock smoke test、真实 subset 小规模训练。

第二阶段验收标准：
- Stage 1.5 原有 mock 和真实 baseline 命令仍可运行。
- STFT/CWT 特征为 on-the-fly 计算，不产生全量图片数据集。
- 至少跑通 mock 消融 smoke test。
- 有真实 RadioML2016.10A 时，至少跑通 subset 消融实验。
- 输出 per-SNR、low/mid/high SNR、per-class、混淆矩阵、归一化混淆矩阵和复杂度统计。
- docs/ 阶段文档和 EXPERIMENT_LOG.md 已更新，真实与 mock 结果明确区分。
```

## Stage 1.6 → Stage 2

当前 Stage 1.6 状态为 Partial Done：真实 RadioML2016.10A subset baseline 已完成，服务器 full baseline 尚未执行。

可以进入 Stage 2 的工程开发；论文实验仍需补齐 full baseline。如果服务器 full baseline 也完成，可以正式进入 Stage 2 的论文实验与消融阶段。

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 训练工程师。

请先读取 durable context：
1. 如果 docs/session_state.md 存在，先读取它；
2. 再读取 docs/PROGRESS_LOG.md；
3. 读取 docs/stages/STAGE_016_REAL_DATA_EXECUTION.md；
4. 读取 docs/EXPERIMENT_LOG.md；
5. 如果已有真实 run_dir，读取对应 metrics.json、baseline_comparison.md 和关键 plots 路径。

进入 Stage 2 前置条件：
- 已完成真实 RadioML2016.10A subset baseline；
- 服务器 full baseline 尚未完成，论文实验前仍需补齐；
- `runs/stage1_6_real_subset_comparison/baseline_comparison.md` 和 `baseline_comparison.csv` 已生成；
- CNN1D/ResNet1D run 中 `accuracy_vs_snr.png` 已生成；
- docs/EXPERIMENT_LOG.md 已记录真实 subset 实验；
- mock smoke test 不能作为正式实验依据。

真实 subset baseline 摘要：
- CNN1D run_dir: `runs/20260507_153710_cnn1d/`
- ResNet1D run_dir: `runs/20260507_153719_resnet1d/`
- CNN1D overall accuracy: 0.8461
- ResNet1D overall accuracy: 0.9070
- low SNR accuracy: N/A，因为当前 subset 不含 `SNR <= -6`

Stage 2 目标：
1. 新增 STFT/CWT on-the-fly 特征接口，不离线保存全量 STFT/CWT 图片。
2. 新增时频 CNN 分支。
3. 新增 I/Q + STFT、I/Q + CWT、I/Q + STFT + CWT 多视图融合模型。
4. 保留 CNN1D 和 ResNet1D baseline，不破坏 Stage 1.6 的 check_dataset、visualize、run_stage1_5_baselines 和 compare_runs 流程。
5. 新增 configs/stage2_* 配置，区分 mock、real subset、real full 和 ablation。
6. 新增 scripts/run_stage2_ablations.py 批量运行消融实验。
7. 输出 overall accuracy、per-SNR accuracy、low/mid/high SNR accuracy、per-class accuracy、confusion matrix、normalized_confusion_matrix、模型复杂度统计和训练耗时。
8. 继续更新 docs/STAGE_INDEX.md、docs/PROGRESS_LOG.md、docs/EXPERIMENT_LOG.md、docs/NEXT_STAGE_PROMPTS.md 和新的 Stage 2 过程文档。

Stage 2 不做：
- 不自动下载大数据集；
- 不把 RadioML 数据集加入 Git；
- 不把 checkpoint 或 runs 产物加入 Git；
- 不离线保存全量 STFT/CWT 图片；
- 不直接引入 Transformer 或复杂注意力机制，除非真实 baseline 和消融已经稳定。
```

## Stage 2 工程闭环 → Stage 2 正式消融

当前 Stage 2 状态为 Partial Done：工程能力已完成，mock smoke 和真实 subset 最小闭环已跑通；完整真实 subset/full 消融仍待执行。

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 训练工程师。

启动前请按 durable context 规则读取：
1. docs/PROGRESS_LOG.md
2. docs/STAGE_INDEX.md
3. docs/stages/STAGE_02_TIME_FREQUENCY_MULTIVIEW.md
4. docs/EXPERIMENT_LOG.md
5. runs/stage2_real_subset_ablation/baseline_comparison.md
6. runs/20260507_161048_tfcnn_stft/metrics.json
7. runs/20260507_161030_fusion_iq_stft_cwt/metrics.json

当前真实 baseline 摘要：
- 数据集：RadioML2016.10A
- subset：4 类、8 个 SNR、每组 200 条
- CNN1D Acc：0.8461
- ResNet1D Acc：0.9070
- Low SNR Acc：N/A，因为 subset 不含 SNR <= -6
- full baseline 尚未训练，论文正式实验前仍需补齐

Stage 2 已完成：
1. STFT/CWT on-the-fly 特征接口已实现，不离线保存全量图片。
2. `tfcnn_stft`、`tfcnn_cwt` 时频 CNN 分支已实现。
3. `fusion_iq_stft`、`fusion_iq_cwt`、`fusion_iq_stft_cwt` 多视图融合模型已实现。
4. `configs/stage2_*` 配置和 `scripts/run_stage2_ablations.py` 已新增。
5. mock smoke 已跑通：`fusion_iq_stft_cwt`，Acc 0.2308，仅工程验证。
6. real subset 最小闭环已跑通：`tfcnn_stft`，1 epoch Acc 0.4047，仅工程闭环。
7. Stage 1.6 原有 check_dataset、visualize_examples、run_stage1_5_baselines、compare_runs 已回归验证。

下一步目标：
1. 不破坏 Stage 1.6 baseline 命令。
2. 在真实 subset 上运行完整 Stage 2 消融：tfcnn_stft、tfcnn_cwt、fusion_iq_stft、fusion_iq_cwt、fusion_iq_stft_cwt。
3. 对齐 epochs、batch_size、seed、split 和报告字段，输出 comparison。
4. 更新 docs/EXPERIMENT_LOG.md，明确 mock smoke、1-epoch 工程闭环和正式 subset 消融的区别。
5. full baseline 和 full Stage 2 消融建议迁移到 GPU 服务器。

严格不做：
- 不自动下载大数据集；
- 不把 RadioML 数据、runs 或 checkpoint 加入 Git；
- 不离线保存全量 STFT/CWT 图片；
- 不引入 Transformer 或复杂注意力机制；
- 不用 mock 结果冒充真实结果。
```

## Stage 2.1 → Stage 2.2

当前 Stage 2.1 状态为 Done：RadioML2016.10A 真实 subset 完整消融已完成，Stage 1.6 baseline 已纳入统一对比。下一阶段优先进入服务器 full baseline/full ablation，不要直接进入 RadioML2018.01A。

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理和 PyTorch 训练工程师。

启动前请按 durable context 规则读取：
1. docs/PROGRESS_LOG.md
2. docs/STAGE_INDEX.md
3. docs/stages/STAGE_021_REAL_SUBSET_ABLATION.md
4. docs/EXPERIMENT_LOG.md
5. runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_comparison.md
6. runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_summary.json

当前 Stage 2.1 真实 subset 结果：
- 数据集：RadioML2016.10A real subset
- subset：4 类、8 个 SNR、每组 200 条
- seed：42
- epochs：5
- batch size：128
- low SNR：N/A，因为 subset 不含 SNR <= -6
- CNN1D：0.8461
- ResNet1D：0.9070
- tfcnn_stft：0.5961
- tfcnn_cwt：0.6539
- fusion_iq_stft：0.8320
- fusion_iq_amp_phase：0.8086
- fusion_iq_stft_cwt：0.8328

当前结论：
- subset 最佳模型仍是 ResNet1D，Acc 0.9070。
- Stage 2.1 最佳融合模型是 fusion_iq_stft_cwt，Acc 0.8328，但未超过 CNN1D/ResNet1D baseline。
- 当前结果可以写入结课报告的 subset 消融章节，但必须标注 single-seed、real subset、low SNR N/A、非 full dataset。

Stage 2.2 目标：
1. 在服务器或 GPU 环境补齐 RadioML2016.10A full baseline：CNN1D、ResNet1D。
2. 在 full 数据上运行主要 Stage 2 模型：优先 fusion_iq_stft、fusion_iq_stft_cwt；资源足够再补 tfcnn_cwt。
3. 生成 full comparison，字段保持 Stage 2.1 一致。
4. 更新 docs/stages/STAGE_022_FULL_ABLATION.md、STAGE_INDEX、PROGRESS_LOG、EXPERIMENT_LOG 和 NEXT_STAGE_PROMPTS。
5. 明确 full 结果和 subset 结果的区别。

严格不做：
- 不自动下载大数据集，除非用户明确要求并提供服务器环境；
- 不打印或接触 Kaggle token；
- 不把 data/raw、runs、checkpoint、.venv 加入 Git；
- 不进入 RadioML2018.01A；
- 不引入 Transformer 或复杂注意力机制；
- 不离线保存全量 STFT/CWT 图片。
```

## Stage 2.2 → Stage 3

当前 Stage 2.2 状态为 Done：RadioML2016.10A full 数据检查、CNN1D/ResNet1D full baseline 和 `fusion_iq_stft` full 消融已完成。下一阶段优先进入低 SNR 鲁棒性与误差分析，不要直接进入 RadioML2018.01A。

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、无线电 AMC 研究助理、PyTorch 消融实验负责人和论文实验分析助手。

启动前请按 durable context 规则读取：
1. docs/PROGRESS_LOG.md
2. docs/STAGE_INDEX.md
3. docs/stages/STAGE_022_FULL_ABLATION.md
4. docs/EXPERIMENT_LOG.md
5. runs/stage2_2_full_ablation_comparison/stage2_2_full_comparison.md
6. runs/stage2_2_full_ablation_comparison/stage2_2_full_summary.json
7. runs/20260507_192755_cnn1d/metrics.json
8. runs/20260507_193019_resnet1d/metrics.json
9. runs/20260507_193548_fusion_iq_stft/metrics.json

当前 Stage 2.2 full 结果：
- 数据集：RadioML2016.10A full
- 样本数：220000
- 类别数：11
- SNR：20 个，范围 -20 到 18
- seed：42
- low SNR 现在有真实 full 结果
- CNN1D：overall 0.5855，low 0.2032，mid 0.8017，high 0.8790
- ResNet1D：overall 0.5968，low 0.2091，mid 0.8155，high 0.8950
- fusion_iq_stft：overall 0.5782，low 0.2222，mid 0.7856，high 0.8455
- 当前 full 最佳 overall：ResNet1D
- `fusion_iq_stft` 在 low SNR 上略高于 baseline，但 overall/mid/high 未超过 ResNet1D
- `fusion_iq_stft_cwt` 在 RTX 4070 12GB 上 optional skipped：on-the-fly CWT CPU-bound、NNPACK warning flood、日志快速膨胀、GPU 利用率接近 0%

Stage 3 核心目标：
1. 不重建项目。
2. 不删除已有 runs。
3. 不破坏 Stage 1/1.5/1.6/2/2.1/2.2 旧流程。
4. 基于 RadioML2016.10A full 结果做低 SNR 鲁棒性和误差分析。
5. 重点比较 CNN1D、ResNet1D、fusion_iq_stft 在 SNR <= -6 的表现。
6. 输出 low/mid/high SNR 表格、per-SNR 曲线对照、per-class 低 SNR 表格和混淆矩阵分析。
7. 分析 `fusion_iq_stft` 为什么 low SNR 略优但 overall 不优。
8. 如需新增训练策略，优先考虑轻量方法：
   - low SNR sample weighting；
   - SNR-balanced sampler；
   - 只在现有 CNN/ResNet/融合结构上调整训练协议；
   - 不引入 Transformer 或复杂注意力机制。
9. 生成 Stage 3 文档：
   - docs/stages/STAGE_03_LOW_SNR_ANALYSIS.md
   - 更新 docs/STAGE_INDEX.md
   - 更新 docs/PROGRESS_LOG.md
   - 更新 docs/EXPERIMENT_LOG.md
   - 更新 docs/NEXT_STAGE_PROMPTS.md
   - 必要时更新 README.md

严格限制：
- 不自动下载大数据集。
- 不把 data/raw、runs、checkpoint、.venv 加入 Git。
- 不进入 RadioML2018.01A。
- 不引入 Transformer 或复杂注意力机制。
- 不离线保存全量 STFT/CWT 图片。
- 不把 subset 结果写成 full 结果。
- 不把 mock 结果写成真实结果。
- CWT full 三视图已记录为 optional skipped，不要在未优化成本前反复强跑。

本阶段完成后，请输出：
1. 使用的 run_dir。
2. 低 SNR 对比表。
3. 关键 per-SNR 曲线和混淆矩阵路径。
4. 当前低 SNR 最优模型。
5. 当前 full overall 最优模型。
6. 是否需要新增训练策略或只做报告分析。
7. 是否可以进入 RadioML2018.01A。
8. Git 状态和是否误加入数据/runs/checkpoint。
```

## Stage 3 → Stage 3.1

当前 Stage 3 状态为 Done：已经基于 RadioML2016.10A full 结果完成低 SNR 分析。`fusion_iq_stft` 在 low SNR 上比 ResNet1D 高 +0.0131，但 overall 低 -0.0186。下一步如果希望强化低 SNR 证据，优先做轻量训练策略实验，而不是增加复杂模型。

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习实验复现工程师、AMC 低 SNR 鲁棒性研究助理和 PyTorch 训练策略工程师。

请进入 Stage 3.1：
低 SNR weighted loss / SNR-balanced sampler 小规模改进实验。

启动前请按 durable context 规则读取：
1. docs/STAGE_INDEX.md
2. docs/PROGRESS_LOG.md
3. docs/stages/STAGE_03_LOW_SNR_ANALYSIS.md
4. docs/EXPERIMENT_LOG.md
5. runs/stage3_low_snr_analysis/stage3_low_snr_summary.md
6. runs/stage3_low_snr_analysis/stage3_low_snr_summary.json
7. runs/20260507_193019_resnet1d/metrics.json
8. runs/20260507_193548_fusion_iq_stft/metrics.json

当前已知结果：
- RadioML2016.10A full overall 最佳：ResNet1D，0.5968。
- 当前 low SNR 最佳：fusion_iq_stft，0.2222。
- fusion_iq_stft 相比 ResNet1D：low SNR +0.0131，overall -0.0186。
- low-SNR-only confusion matrix 暂缺，因为 Stage 2.2 未保存 prediction-level 输出。

Stage 3.1 目标：
1. 不重建项目。
2. 不删除已有 runs。
3. 不破坏 Stage 1/1.5/1.6/2/2.1/2.2/3 旧流程。
4. 新增轻量 low SNR 改进配置和必要代码：
   - low-SNR weighted loss；或
   - SNR-balanced sampler；
   - 优先选择对现有 trainer 侵入最小的实现。
5. 优先在 subset 或小规模 full 子集上做 smoke，确认训练链路可运行。
6. 如资源允许，只跑一个最小对照实验，不要大规模重跑所有模型。
7. 输出 comparison，重点观察 low SNR 是否提升，overall 是否严重下降。
8. 如果实现需要保存 predictions，可新增 evaluate/save_predictions 轻量脚本，用于后续 low-SNR confusion matrix。
9. 更新 docs/stages/STAGE_031_LOW_SNR_IMPROVEMENT.md、STAGE_INDEX、PROGRESS_LOG、EXPERIMENT_LOG、NEXT_STAGE_PROMPTS。

严格限制：
- 不引入 Transformer 或复杂注意力机制。
- 不进入 RadioML2018.01A。
- 不自动下载大数据集。
- 不把 data/raw、runs、checkpoint、.venv 加入 Git。
- 不离线保存全量 STFT/CWT 图片。
- 不用 mock 结果冒充真实结果。
- 不把 subset 小实验写成 full 正式结果。

本阶段完成后请输出：
1. 新增配置/代码文件。
2. 实际运行命令。
3. smoke 或小规模实验结果。
4. low SNR 是否提升。
5. overall 是否下降。
6. 是否值得在服务器 full 上正式复跑。
7. Git 状态和是否误加入数据/runs/checkpoint。
```

## Stage 3 → Stage 5.0

当前 Stage 3 已经具备结课报告初稿所需的主要证据：mock 工程闭环、真实 subset baseline、真实 subset 消融、RadioML2016.10A full baseline/full ablation 和低 SNR 分析。若课程时间优先，可以先进入报告初稿，把 Stage 3.1 作为可选增强实验。

```text
你现在继续维护项目 radioml-amc-stage1，角色是机器学习课程报告写作助手、AMC 实验复现工程师、结果图表整理助手和 GitHub 文档维护助手。

请进入 Stage 5.0：
机器学习结课报告初稿生成。

启动前请读取：
1. README.md
2. docs/STAGE_INDEX.md
3. docs/PROGRESS_LOG.md
4. docs/EXPERIMENT_LOG.md
5. docs/stages/STAGE_016_REAL_DATA_EXECUTION.md
6. docs/stages/STAGE_021_REAL_SUBSET_ABLATION.md
7. docs/stages/STAGE_022_FULL_ABLATION.md
8. docs/stages/STAGE_03_LOW_SNR_ANALYSIS.md
9. runs/stage2_1_real_subset_ablation_comparison/stage2_1_ablation_comparison.md
10. runs/stage2_2_full_ablation_comparison/stage2_2_full_comparison.md
11. runs/stage3_low_snr_analysis/stage3_low_snr_summary.md

报告目标：
1. 生成一份中文机器学习结课报告初稿，题目为：
   《基于时频特征与深度神经网络融合的无线电调制识别方法研究——以 RadioML2016.10A 与 RadioML2018.01A 数据集为例》
2. 当前实际只完成 RadioML2016.10A，因此报告中必须明确 RadioML2018.01A 是后续扩展，不写成已完成。
3. 报告结构建议：
   - 摘要
   - 引言
   - 数据集与任务定义
   - 方法：CNN1D、ResNet1D、STFT/CWT on-the-fly、多视图融合
   - 实验设置
   - subset 实验结果
   - full 实验结果
   - 低 SNR 分析
   - 复杂度与耗时分析
   - 局限性
   - 结论与未来工作
4. 使用真实结果表，不要用 mock 结果当正式实验。
5. 结论必须谨慎：
   - 可以写 ResNet1D 是当前 full overall 最优；
   - 可以写 STFT 融合在 low SNR 有小幅提升；
   - 不可以写融合全面优于 baseline；
   - 不可以写 CWT full 已完成；
   - 不可以写 RadioML2018.01A 已验证；
   - 不可以写 SOTA。
6. 汇总并引用关键图表路径：
   - per-SNR 曲线
   - confusion matrix
   - per-class accuracy
   - Stage 3 low SNR 分析图
7. 输出到 docs/report/ 或 reports/，并更新 README 或 docs 索引。

严格限制：
- 不删除已有 docs/runs。
- 不把 data/raw、runs、checkpoint、.venv 加入 Git。
- 不伪造结果。
- 不把 subset 写成 full。
- 不把 mock 写成真实。

完成后请输出：
1. 报告文件路径。
2. 使用的实验结果表。
3. 引用的图表路径。
4. 当前结论边界。
5. 是否还建议补 Stage 3.1。
6. Git 状态。
```
