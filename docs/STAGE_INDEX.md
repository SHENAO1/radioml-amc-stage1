# 阶段索引

| 阶段 | 名称 | 状态 | 主要目标 | 当前结果 | 文档路径 | 下一步 |
|---|---|---|---|---|---|---|
| Stage 1 | 本地 mock 工程闭环 | Done | 跑通 mock 数据、loader 接口、CNN1D/ResNet1D、训练评估、可视化、报告和 pytest | `.s... [100%]`，mock CNN1D/ResNet1D run 已生成；仅用于工程 smoke test | `docs/stages/STAGE_01_LOCAL_MOCK_ENGINEERING.md` | 进入真实数据 baseline |
| Stage 1.5 | RadioML2016.10A 真实数据 baseline | Done | 强化真实数据读取、subset/full 配置、baseline 协议、对比脚本、阶段报告和过程文档 | 工程能力已补充；真实 RadioML2016.10A subset baseline 已在 Stage 1.6 跑通；full 训练仍待服务器执行 | `docs/stages/STAGE_015_RML2016A_BASELINE.md` | 服务器执行 full baseline |
| Stage 1.6 | 真实 RadioML2016.10A 数据接入与 baseline 执行 | Partial Done | 完成真实数据下载说明、数据接入检查、subset baseline 验证路径和服务器 full baseline 准备 | 真实 subset done：CNN1D Acc 0.8461，ResNet1D Acc 0.9070；comparison 已生成；full pending | `docs/stages/STAGE_016_REAL_DATA_EXECUTION.md` | 在服务器执行 full baseline；可并行进入 Stage 2 工程开发 |
| Stage 2 | STFT/CWT 时频分支与多视图融合 | Partial Done | 新增 on-the-fly STFT/CWT 特征、时频 CNN 分支和 I/Q + 时频融合模型 | 工程已完成；mock `fusion_iq_stft_cwt` smoke 跑通；real subset `tfcnn_stft` 1 epoch 闭环跑通，Acc 0.4047；正式完整消融和 full baseline pending | `docs/stages/STAGE_02_TIME_FREQUENCY_MULTIVIEW.md` | 在真实 subset 上跑完整 Stage 2 消融；论文实验前补 full baseline 和 full 消融 |
| Stage 3 | 低 SNR 鲁棒性与消融实验 | Pending | 重点评估低 SNR，补充鲁棒训练和系统消融 | 未开始 | 待创建 | 等 Stage 2 完成后进入 |
| Stage 4 | RadioML2018.01A 扩展验证 | Pending | 扩展到 RadioML2018.01A，验证跨数据集泛化 | 未开始 | 待创建 | 等 Stage 2/3 协议稳定后进入 |
| Stage 5 | 论文撰写与投稿材料整理 | Pending | 整理图表、实验表格、方法描述和投稿材料 | 未开始 | 待创建 | 等正式实验完成后进入 |
