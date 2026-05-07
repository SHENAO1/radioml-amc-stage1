# 阶段索引

| 阶段 | 名称 | 状态 | 主要目标 | 当前结果 | 文档路径 | 下一步 |
|---|---|---|---|---|---|---|
| Stage 1 | 本地 mock 工程闭环 | Done | 跑通 mock 数据、loader 接口、CNN1D/ResNet1D、训练评估、可视化、报告和 pytest | `.s... [100%]`，mock CNN1D/ResNet1D run 已生成；仅用于工程 smoke test | `docs/stages/STAGE_01_LOCAL_MOCK_ENGINEERING.md` | 进入真实数据 baseline |
| Stage 1.5 | RadioML2016.10A 真实数据 baseline | Done | 强化真实数据读取、subset/full 配置、baseline 协议、对比脚本、阶段报告和过程文档 | 工程能力已补充；真实 RadioML2016.10A subset baseline 已在 Stage 1.6 跑通；full 训练仍待服务器执行 | `docs/stages/STAGE_015_RML2016A_BASELINE.md` | 服务器执行 full baseline |
| Stage 1.6 | 真实 RadioML2016.10A 数据接入与 baseline 执行 | Partial Done | 完成真实数据下载说明、数据接入检查、subset baseline 验证路径和服务器 full baseline 准备 | 真实 subset done：CNN1D Acc 0.8461，ResNet1D Acc 0.9070；comparison 已生成；full pending | `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md` | 在服务器执行 full baseline；可并行进入 Stage 2 工程开发 |
| Stage 2 | STFT/CWT 时频分支与多视图融合 | Done | 新增 on-the-fly STFT/CWT 特征、时频 CNN 分支和 I/Q + 时频融合模型 | 工程已完成；mock smoke 和真实 subset 最小闭环均跑通 | `docs/stages/STAGE_02_TIME_FREQUENCY_MULTIVIEW.md` | Stage 2.1 已执行真实 subset 完整消融 |
| Stage 2.1 | RadioML2016.10A 真实 subset 完整消融 | Done | 固定真实 subset 协议，完成 STFT/CWT/融合模型消融，并纳入 Stage 1.6 baseline 对照 | single-seed subset：ResNet1D 0.9070 最优；最佳融合为 `fusion_iq_stft_cwt` 0.8328；low SNR N/A | `docs/stages/STAGE_021_REAL_SUBSET_ABLATION.md` | 进入 Stage 2.2：服务器 full baseline/full ablation |
| Stage 2.2 | RadioML2016.10A full baseline/full ablation | Done | 在服务器 full 数据上补齐正式 baseline 和主要融合模型对比 | full single-seed：ResNet1D 0.5968 最优；`fusion_iq_stft` 0.5782；full CWT 三视图在 RTX 4070 上 optional skipped | `docs/stages/STAGE_022_FULL_ABLATION.md` | 进入 Stage 3：低 SNR 鲁棒性与误差分析 |
| Stage 3 | 低 SNR 鲁棒性与消融实验 | Pending | 重点评估低 SNR，补充鲁棒训练和系统消融 | 未开始 | 待创建 | 基于 RadioML2016.10A full 结果展开 |
| Stage 4 | RadioML2018.01A 扩展验证 | Pending | 扩展到 RadioML2018.01A，验证跨数据集泛化 | 未开始 | 待创建 | 等 Stage 2/3 协议稳定后进入 |
| Stage 5 | 论文撰写与投稿材料整理 | Pending | 整理图表、实验表格、方法描述和投稿材料 | 未开始 | 待创建 | 等正式实验完成后进入 |
