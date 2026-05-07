# Next Paper Stage Prompts

## Paper-Stage 1 Prompt Draft

你现在扮演“AMC 自动调制识别 SCI 论文方向顾问 + 机器学习科研工程架构师 + 文献综述助手 + PyTorch 实验协议审稿人”。

当前项目是 `radioml-amc-stage1` 的 `paper-sci-track` 分支。不要改代码，不要启动训练，不要覆盖课程项目主线。

任务名称：

Paper-Stage 1：文献综述与 gap 固化

当前已有事实：

- RadioML2016.10A full 上 ResNet1D 是当前 overall 最优模型，overall accuracy 为 0.5968。
- `fusion_iq_stft` overall accuracy 为 0.5782，低于 ResNet1D。
- `fusion_iq_stft` low-SNR accuracy 为 0.2222，高于 ResNet1D 的 0.2091 和 CNN1D 的 0.2032。
- 当前不能宣称融合模型全面优于 baseline。
- 当前可探索方向是 SNR-aware lightweight multi-view fusion for low-SNR robust AMC。

请完成：

1. 不改代码，只维护 `docs/paper/` 下的文献综述与 gap 文档。
2. 先建立文献表，字段至少包括 paper title、year、dataset、input representation、model、low-SNR experiment、per-SNR result、complexity report、ablation、limitation、relevance to this project。
3. 围绕以下关键词检索和归类：automatic modulation classification、RadioML2016.10A、RadioML2018.01A、low SNR modulation classification、time-frequency modulation recognition、multi-view fusion AMC、SNR-aware deep learning、lightweight AMC、complex neural network AMC、attention AMC。
4. 明确当前方法方向是否有发表空间。
5. 明确需要补齐哪些实验，尤其是 multi-seed、per-SNR、low-SNR confusion matrix、complexity、RadioML2018.01A。
6. 输出可用于论文 Related Work 的结构，包括 I/Q deep learning baselines、time-frequency AMC、multi-view fusion、low-SNR robust AMC、lightweight/complexity-aware AMC。
7. 所有结论必须区分“已由本项目实验支持”和“需要文献或实验进一步验证”。

交付格式：

1. 更新或新增的文档列表。
2. 文献表摘要。
3. 已验证的 research gap。
4. 仍不确定的问题。
5. 下一阶段 Paper-Stage 2 的建议。
