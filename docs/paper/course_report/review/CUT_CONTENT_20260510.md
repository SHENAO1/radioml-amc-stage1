# 已删除内容存档（2026-05-10）

## 删除原因

该段话和表格从引言"研究背景"节中删除，理由：
- 逻辑位置错误：讨论图表选型属于方法/实验协议章，而非背景节。
- 自我辩护语气（"重点不是追求'最新水平'排名"）反而削弱可信度。
- 表格所传达的信息对领域读者而言是常识，不需要 20 行文献来论证。
- 表中含 arXiv:2604.06402（G-AMC 2026）等极新引用，真实性难以核查，存在风险。

若后续需要将图表选型依据补入报告，建议放置在 **第 2 章实验协议节**，以一句话陈述"评价采用整体准确率、分 SNR 准确率曲线和混淆矩阵"即可，无需引文支撑。

---

## 原始段落（来自 sections/01_introduction.tex）

```latex
已有 AMC 深度学习研究通常使用结构图、准确率随信噪比变化曲线、混淆矩阵、
消融表和复杂度表展示模型行为\cite{rajendran2018distributed,zeng2019spectrum,
huynhthe2020mcnet,zhang2021petcgdnn,zhang2023amcnet,huynhthe2021survey}。
表~\ref{tab:literature-figure-patterns} 归纳了若干代表性文献中常见的图表用途。
本文沿用这一表达方式，但重点不是追求"最新水平"排名，而是在课程实验范围
内说明不同输入视图和模型结构在固定协议下的可比结果。

\input{tables/literature_figure_patterns}
```

---

## 原始表格内容（tables/literature_figure_patterns.tex）

```latex
\begingroup
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\renewcommand{\arraystretch}{1.12}
\begin{longtable}{p{0.18\textwidth}>{\centering\arraybackslash}p{0.07\textwidth}>{\centering\arraybackslash}p{0.07\textwidth}>{\centering\arraybackslash}p{0.08\textwidth}>{\centering\arraybackslash}p{0.06\textwidth}>{\centering\arraybackslash}p{0.07\textwidth}p{0.27\textwidth}}
\caption{开放 AMC 论文中的常见图表模式与本文图表设计对应关系}\label{tab:literature-figure-patterns}\\
\toprule
文献线索 & 结构图 & SNR 曲线 & 混淆矩阵 & 消融 & 复杂度 & 对本文图表设计的作用 \\
\midrule
\endfirsthead
\toprule
文献线索 & 结构图 & SNR 曲线 & 混淆矩阵 & 消融 & 复杂度 & 对本文图表设计的作用 \\
\midrule
\endhead
\href{https://arxiv.org/abs/1602.04105}{O'Shea 2016} & Y & Y & - & - & - & RadioML/CNN baseline and SNR curves \\
\href{https://arxiv.org/abs/1712.00443}{Deep architectures 2017} & Y & Y & Y & Y & Y & Baseline families and experiment tables \\
\href{https://arxiv.org/abs/1810.02027}{Polar features 2018} & Y & Y & - & - & Y & Alternative I/Q-derived views \\
\href{https://arxiv.org/abs/1901.05850}{Fast DL AMC 2019} & Y & Y & - & - & Y & Efficiency-aware reporting \\
\href{https://arxiv.org/abs/1909.03050}{SCRNN 2019} & Y & Y & - & - & Y & CNN/RNN model comparison \\
\href{https://arxiv.org/abs/1912.03026}{Data augmentation 2019} & - & Y & - & Y & Y & Ablation and robustness framing \\
\href{https://arxiv.org/abs/2009.02026}{Constellation CNN 2020} & Y & Y & Y & - & - & Non-I/Q visual representation \\
\href{https://arxiv.org/abs/2010.10717}{Complex CNN 2020} & Y & Y & - & - & Y & Complex-valued model framing \\
\href{https://arxiv.org/abs/2105.15037}{Multi-scale networks 2021} & Y & Y & - & Y & Y & Multi-scale architecture figure \\
\href{https://arxiv.org/abs/2108.10001}{Involution ResNet 2021} & Y & Y & - & - & Y & Residual baseline variant \\
\href{https://arxiv.org/abs/2111.03258}{Time-frequency attention 2021} & Y & Y & - & Y & Y & Time-frequency attention evidence \\
\href{https://arxiv.org/abs/2203.03140}{Adaptive fusion 2022} & Y & Y & - & Y & Y & Fusion architecture and ablation \\
\href{https://arxiv.org/abs/2208.04659}{Ultra Lite CNN 2022} & Y & Y & - & Y & Y & Lightweight complexity table \\
\href{https://arxiv.org/abs/2209.03764}{SE-MSFN 2022} & Y & Y & - & Y & Y & Attention/multi-scale result curves \\
\href{https://arxiv.org/abs/2301.11773}{Harper 2023} & Y & Y & Y & Y & Y & Systematic benchmark style \\
\href{https://arxiv.org/abs/2304.00445}{AMC-Net 2023} & Y & Y & - & Y & Y & Dedicated AMC network comparison \\
\href{https://arxiv.org/abs/2405.11263}{MAMCA 2024} & Y & Y & - & Y & Y & Accuracy/efficiency trade-off \\
\href{https://arxiv.org/abs/2503.04142}{UQ-AMC 2025} & Y & Y & - & - & Y & Reliability and uncertainty framing \\
\href{https://arxiv.org/abs/2604.06402}{G-AMC 2026} & Y & Y & - & Y & Y & Green/lightweight framing \\
\href{https://www.mdpi.com/2079-9292/12/17/3661}{HFECNET-CA/IDAF} & Y & Y & Y & Y & Y & Open-access module and figure exemplars \\
\bottomrule
\end{longtable}
\endgroup
```
