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
