# 课程报告严格审稿意见 (2026-05-09)

Reviewer: Claude Code（在 Stage 6 实验完成、`a332b7c` 报告返修提交后）
对照样本: CC-MSNet (Sci Rep 2024)、SigFormer (IEEE 2023)、AI/ML AMR Survey (arXiv 2502.05315)、AMR-Benchmark、LENet-M (DSP 2024)、ICRNNA (Heliyon 2025)
报告版本: `docs/paper/course_report/main.pdf`（48 页，commit `a332b7c`）

## 审稿统计快照

- 章节: 6 章中文论文式（典型期刊论文 4-5 章）
- 引用密度: §1=4, §2=3, §3=6, §4=7, §5=0, §6=0, abstract=0；**总计 20 个 \cite**（典型 ML 期刊论文 30-60 个）
- 图: 16 张（fig01-fig16）；表: 12 张
- 摘要长度: ~480 字中文（典型期刊摘要 130-250 词）
- mean±std 报告: ✅（多数论文是 single-seed）
- 配对统计检验: ✅ Stage 5A 主表，❌ 提案模型
- 单干预消融: ❌

---

## 🔴 必须改（不改会被审稿质疑）

### 1. 提案模型缺乏单点消融

**现状**: `fusion_cldnn_stft + 增强 + label smoothing` 把三项干预捆绑成一次训练，整体 +1.35 pp；§5 已承认这是 limitation。

**问题**:
- 文献中（CC-MSNet, SigFormer 等）所有提出新方法的论文都做模块消融。
- 审稿: "既然没消融，怎么知道 CLDNN backbone 是不是唯一起作用？说不定 augmentation 一项就能涨 1.3 pp，那架构升级就成了空话。"

**建议**: 再跑 3 个对照（每个 3 seeds × 50 epoch on 3090，约 1.5 小时总时间）：
- (a) `fusion_cldnn_stft` only（无增强、无 label smoothing）
- (b) `fusion_cldnn_stft + augmentation` only
- (c) `fusion_cldnn_stft + label smoothing` only
- (d)（已有）`fusion_cldnn_stft + augmentation + label smoothing`

如果不能再训练，至少在 §3 末段或 §5 末段显式承认"因实验资源限制未做单点消融，列为未来工作"——不能仅一笔带过。

### 2. 提案模型缺少配对统计检验

**现状**: 表 4.x 给 mean±std (σ=0.0005)，但没有 paired bootstrap 置信区间或 McNemar 检验；Stage 5A 主表（§4.2）则给了配对检验。

**问题**: +1.35 pp 仅用 27σ 论据解释——σ 是 between-seed std，不是配对检验。

**建议**:
- proposal seed 42 vs P1.1 fusion_iq_stft seed 42 → paired bootstrap on test predictions（同硬件、同 schedule，仅模型/损失/增强不同，**完全可以做**）
- 与 Stage 5A CLDNN 的对比因硬件不同不能做样本级配对，但可以用 between-seed-mean 的 unpaired t-test 做近似检验，或在文中明确写"两个 mean 的差距是 27 倍 within-seed std，因此即使有跨硬件 cuDNN 漂移也不可能解释"

### 3. 文献对比表口径混乱

**现状**（§4.7.5 Table 4.7）: 一列 "avg-across-SNR"，一列 "高 SNR 区间或单点"。但**不同模型的"高 SNR"定义不同**——MCLDNN 用 avg(SNR>0)、CLDNN2 用 peak、本文用 avg(SNR≥8)。

**问题**: 这是审稿人最爱挑的毛病。

**建议**: 把"高 SNR"一列至少分成两个 sub-column: `avg SNR>0` 与 `peak`。原论文未给 `avg(SNR>0)` 的留 `--`；给的是 `peak SNR=10dB` 的注明 `(at +10 dB)`。

### 4. Abstract 太长

**现状**: ~480 字中文（英文化后约 380 词）。标准期刊摘要 150-250 词；CC-MSNet 摘要 130 词。

**建议**: 抽出 4 个句子结构（Background / Methods / Results / Conclusion），每段 1-2 句。砍掉 "扩展实验中…分组 SNR 加权交叉熵在低信噪比上小幅获益但中高信噪比代价更大" 这种 §5 sensitivity 内容（abstract 不讲 sensitivity），仅保留主表 + 提案模型结果。

### 5. 引用密度过低，缺少近 2 年代表性论文

**现状**:
- §5 讨论 0 引用、§6 结论 0 引用 → 严重不足
- 主表 9 个模型行只有 cldnn / mcldnn / lwamcnet / petcgdnn 引用了原始论文，cnn1d / resnet1d / fusion_iq_stft 等无来源引用

**建议**:
- §3 每个模型行至少给一个 \cite（表格列里加"来源"，或在文段里 anchor）
- §5 讨论里每个 mechanism-level 解释加 1-2 个引用（"CNN+LSTM 序列建模" → Sainath 2015 / West 2017；"标签平滑" → Szegedy 2016）
- 加 `Szegedy 2016 (label smoothing)`、`Krogh & Hertz 1992 (weight decay)` 等标准引用

---

## 🟡 应该改（提升专业度）

### 6. 章节结构不够紧凑

**现状**: 6 章中文论文式结构。期刊论文典型 4-5 章: Introduction / Methods / Experiments / Discussion + Conclusion。

**建议**: 把 §2 数据集与协议 + §3 方法合并成一章 "Methods"，下设 2-3 节（数据集协议 / 模型矩阵 / 提案模型）。当前 §2 90 行 + §3 140 行 = 230 行，合并后控制在 200 行内更紧凑。或在 §2 开头加一句"本章给出实验所需的数据与协议设置；模型描述见第 3 章"来串联。

### 7. §4.7 各小节没有图，全是表

**现状**: §4.1-4.6（Stage 5A 主结果）有 7 张图，§4.7（Stage 6 扩展）只有 2 张表，0 张图。

**建议**: 至少加一张 **per-SNR accuracy curve 对比图**:
- Stage 5A CLDNN（实线）
- Stage 5A fusion_iq_stft（虚线）
- P1.1 fusion_iq_stft（点线，同 schedule 对照）
- 提案模型 fusion_cldnn_stft + aug + LS（粗实线）

数据已在本地（4 个 metrics_per_snr.csv），matplotlib 一张 PDF 就能加进 §4.7.6。这是审稿人最直观的"提案模型如何反超"证据。

### 8. 提案模型数学描述不完整

**现状**（§3）:
```
h_IQ = LSTM(f_1D(x_IQ))_last
h_STFT = f_2D(x_STFT)
y_hat = c([h_IQ, h_STFT])
```

太简略。审稿会问：
- LSTM 隐藏维度是多少？（你的代码里 128）
- f_2D 的具体层次（卷积通道数、激活、归一化）？
- c 分类头的隐藏维（代码里 max(96, min(256, total_dim))）？
- 为什么选 last hidden state 而不是 attention pooled？

**建议**: 给一张表 "Layer-by-layer architecture of fusion_cldnn_stft"，列出每层的输入/输出 shape。

### 9. 不可重复性细节缺失

- PyTorch 版本号没写在正文（只在 appendix）
- 优化器是 AdamW 还是 Adam？β1, β2 默认值？
- 早停 patience=15 的 metric 是 val_loss 还是 val_acc？
- batch_size, num_workers, learning_rate 这些虽然在 §2.4 有，但没解释**为什么是 1e-3 而不是 5e-4 或其他**（虽然你的文献调研说 1e-3 是惯例，可在文中引用）

**建议**: §3 末段补一个 "Implementation details" 子节，3-4 句话覆盖优化器超参与早停 metric。

### 10. §5 讨论的"解释"段落过强

**现状**（提案模型反超解释）:
> "三项干预联合作用，共同把整体、低、中、高信噪比同时推高，不出现以低信噪比换整体或以中高信噪比换低信噪比的'拆东补西'。"

**问题**: 这个解释没有证据支撑——怎么知道"不出现拆东补西"是这三项干预的功劳，而不是别的因素（如 cuDNN 选了不同 kernel）？

**建议**: 改成更谨慎的表述：
> "提案模型的四指标同时正向**与拆东补西失败模式形成对比**，但其机制层面的因果归因需要单点消融来确认；本节解释属于事后机制猜测（post-hoc mechanistic speculation），不是已被实验隔离的因果声明。"

### 11. 主表 (Table 4.x) 没有 best 加粗

**现状**: 所有数字都是普通字体。审稿/读者扫一眼 9 行 × 8 列表格找不到"哪个最好"。

**建议**: 在 LaTeX 里加 `\textbf{...}` 把每列最高值加粗（low/mid/high SNR 各列分别看 cldnn / fusion_iq_stft / cldnn / cldnn）。

### 12. 缺少跨数据集验证的 honest 承诺

**现状**: §5 局限表第 4 行说"数据集只覆盖 RML2016.10A，尚未在 RML2018.01A 上验证"，后续处理写了"选择 RML2018.01A 子集"。但这个实验**不会做**（已经定稿）。

**问题**: 审稿会判定为"承诺但不兑现"。

**建议**: 要么删掉这条承诺，要么写得更具体——比如"作为未来工作的第一优先项"或者直接写"本课程报告不计划在 RML2018.01A 上验证；该数据集结果留给后续研究"。诚实比许诺好。

---

## 🟢 可以改（锦上添花）

### 13. 引言里加一张方法对比"全景图"

- 现状: §1 有 fig01_protocol_pipeline（数据 → 模型 → 表）
- 建议: 加一张图把"我们在 SOTA 坐标系里的位置"画出来——x 轴 = MACs / 参数量，y 轴 = avg-across-SNR accuracy。点出 LENet-M、SigFormer、CC-MSNet、CLDNN、本文提案模型等。读者一眼就能看到位置。

### 14. Appendix 缺少 hyperparameter tabulation

- 现状: appendix_a 只讲 evidence environment
- 建议: 加 Appendix B "Complete hyperparameter table"，列出所有训练超参（同 P1.1, P2.5, A 方案 三列），便于复现者直接复制。

### 15. §5 的"协议局限"表格 5 行过密

- 表格在 0.34/0.66 列宽分配下文字挤得很紧
- 改为 3 列（局限 / 严重程度 / 后续处理）能减轻视觉负担

### 16. 标题不够具体

- 当前: 《基于时频特征与深度神经网络融合的无线电调制识别方法研究》
- 这个题目没体现具体贡献——审稿一看就知道是泛泛之题
- 建议改为:
  - 《基于 CLDNN-STFT 融合与信号域增强的无线电调制识别协议化研究》
  - 或《面向 RadioML2016.10A 的固定划分多视图融合调制识别：基线、扩展实验与提案模型评估》（更长但更准确）

### 17. PDF 排版细节

- 表 4.x（提案对比表）的 +0.0135 等差值数字应加粗或加颜色区分正/负
- §4.7.5 文献对比表的"未单列"用 `--`（emdash）替代会更专业
- §3 的方程编号断裂（fusion-cldnn-stft 一个等号包了三个 = 号），用 `align` 比 `equation` 更合适

---

## 推荐修改顺序（按 ROI）

### 本周内一定要做（必须改 1, 2, 3）
- 跑 3 个 ablation cell（~1.5 小时训练）→ 解决"未做消融"的最大短板
- 加 paired bootstrap on 提案 vs P1.1 fusion → 解决统计检验缺失
- 修文献对比表口径 → 防止审稿人挑致命毛病

### 本周内尽量做（必须改 4, 5；应该改 7）
- Abstract 砍一半
- §5 §6 各加 3-5 个引用
- 加 §4.7 per-SNR 对比图

### 如果还有时间
- 应该改 6, 8, 9, 10, 11
- 可以改的全部

---

## 必做项的实操约束

- **必须改 1（消融实验）需要服务器 GPU**。三个 cell × 50 epoch × 3 seeds，约 1.5 小时（按 P2.5 / A 方案 的服务器跑速估算）
- 服务器 i-1.gpushare.com:62244 在审稿时已计划关机；需要重新启动或保持开机
- **决策点**: 关机前完成 ablation，还是关机后再开新机器跑

## 评审人位置

本审稿假设读者是**普通 ML 期刊审稿人**（IEEE Trans. / IET / Sci Rep 级别），并按那种期刊的最低门槛严格度提意见。课程报告本身的接受标准更宽松，但准备投稿或上传 arXiv 时这些点都会再次成为问题。
