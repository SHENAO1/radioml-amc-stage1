# 提示词：精简所有图注（caption）至学术规范

> 直接复制下面 ` ``` ` 包裹的整段提示词作为下次会话的第一条消息发给 Claude Code（或其他 AI 助手）。
> 该提示词假设助手会先读 `.ai-context/` 与 `docs/paper/course_report/review/FIGURE_DATA_AUDIT_20260510.md` 取上下文。
> 本提示词只改 LaTeX 中的 `\caption{...}` 与少量正文衔接语句，不改图本身、不改数据。

## 当前图注的三类常见问题

1. **术语翻译表**：`图中术语对照: Overall=整体, Low SNR=低信噪比 ...`——学术 caption 不放术语表；轴标签和图例已经表达了同样的信息。
2. **逐字描述线型颜色**：`(粗实线，红)、(实线，蓝)、(虚线，灰)`——这是图例（`\legend{...}` / matplotlib `legend`）的工作，不属于 caption。
3. **正文级别的解读**：`arch_aug 在后期与 full 分离，与消融表数值一致`——观察性结论应放正文，caption 只描述图本身。

## 学术规范的图注结构

> **{图描述句（≤20 字的名词性短语，含数据范围）}** {可选 1 句辅助说明}（{可选括号注明数据源、子图标号）

例：`提案模型 fusion\_cldnn\_stft + aug + LS 与三个对照的逐 SNR 准确率曲线（三训练种子均值）。`

## 复制下面这段（完整提示词）

````
我要精简课程报告 docs/paper/course_report/main.tex 中所有图注 (caption) 至学术规范长度。
先严格阅读以下三份文件取上下文：

1. docs/paper/course_report/review/FIGURE_DATA_AUDIT_20260510.md
2. .ai-context/05-current-state.md 与 .ai-context/06-session-log.md 顶部条目
3. docs/paper/course_report/sections/*.tex 中所有 \caption{...} 块

阅读完后按下面规则精简全部 14 个数据图的 caption（fig01/02/03/10 是 TikZ 示意图，
caption 已经简洁，不动）：

【三条铁律】
(1) 删除 ``图中术语对照：X=中文，Y=中文'' 这类英中翻译表；轴标签和图例本身就说明术语。
(2) 删除逐字描述线型/颜色的句子；图例在图内已经标了。
(3) 删除观察性解读（``X 与 Y 分离''、``这说明...''）；这些放正文，不放 caption。

【目标长度】每个 caption ≤ 80 字（中文），最好 40-60 字。

【目标结构】
开头：1 个名词性短语描述图内容（数据范围 + 模型范围）
可选：1 句最关键的视觉规约（如颜色编码、阴影区含义、几何记号）
括号：(数据源 .csv 名 + 三种子均值/seed 等)

【具体修改清单】

(1) §4.1 fig:accuracy-by-snr-group (fig04)
当前：``图中术语对照：Overall=整体，Low/Mid/High SNR=低/中/高信噪比，Accuracy=准确率。
       固定划分下 9 个模型行的整体、低信噪比、中信噪比和高信噪比准确率对比。
       证据源：main_table_metrics.csv。''
改为：``9 个模型在 4 个 SNR 分组下的准确率对比（三种子均值±std，main\_table\_metrics.csv）。''

(2) §4.1 fig:full-snr-accuracy-macro-f1 (fig11)
当前：``图中术语对照：SNR=信噪比，Accuracy=准确率，Macro F1=宏平均 F1。代表模型在完整
       信噪比轴上的准确率与宏平均 F1 曲线。证据源：metrics_per_snr.csv。''
改为：``代表模型在 -20 至 +18 dB 的逐 SNR 准确率与宏平均 F1（三种子聚合，metrics\_per\_snr.csv）。''

(3) §4.1 fig:model-class-accuracy-heatmap (fig12)
当前：``图中术语对照：Overall class accuracy by model=各模型整体类别准确率，
       Accuracy=准确率。9 个模型行在 11 类调制方式上的类别准确率热力图。
       证据源：metrics_per_class.csv。''
改为：``9 个模型 × 11 类调制的整体类别准确率热力图（metrics\_per\_class.csv）。''

(4) §4.2 fig:bootstrap-delta-forest (fig06)
当前：``图中术语对照：Accuracy delta=准确率差值，95\% CI=95\% 置信区间。已登记模型对的
       配对自助法准确率差值及 95\% 置信区间。差值定义为前一模型准确率减去后一模型准确率。''
改为：``已登记模型对配对自助法的准确率差值与 95\% CI（10000 重采样，paired\_bootstrap\_accuracy\_deltas.csv）。
       差值方向为 model\_a − model\_b。''

(5) §4.3 fig:low-snr-per-snr (fig05)
当前：``图中术语对照：SNR=信噪比，Accuracy=准确率。低信噪比区间内代表模型的逐信噪比
       准确率曲线。低信噪比范围为 \lowSNR{}。''
改为：``代表模型在低信噪比区间（\lowSNR{}）的逐 SNR 准确率曲线（low\_snr\_table.csv）。''

(6) §4.3 fig:paired-disagreement-by-snr (fig14)
当前：``图中术语对照：Share=样本占比，correct only=仅该模型正确，SNR=信噪比。关键模型
       对在各信噪比点上的配对正确性分歧。正向柱表示前一模型正确而后一模型错误的样本更多，
       负向柱表示相反方向更多。''
改为：``关键模型对在各 SNR 点的配对正确性净分歧（``仅 A 正确'' 占比 − ``仅 B 正确'' 占比，
       predictions\_test.csv 三种子聚合）。''

(7) §4.3 fig:low-snr-class-recall-delta (fig13)
当前：``图中术语对照：Recall delta=召回率差值，Fusion - IQ matched=融合减参数匹配 I/Q，
       Fusion - CLDNN=融合减 CLDNN。静态 I/Q--STFT 融合在低信噪比范围内相对参数匹配 I/Q
       控制模型和 CLDNN 的类别召回率差值。''
改为：``静态 fusion\_iq\_stft 相对 iq\_param\_matched 与 CLDNN 在低 SNR 各调制类别的召回率
       差值 Δrecall（confusion\_low\_snr.csv 三种子聚合）。''

(8) §4.5 fig:accuracy-latency-params (fig07)
当前：``图中术语对照：Overall accuracy=整体准确率，Batch-1 latency=批量 1 延迟，
       Params=参数量。固定协议下整体准确率、受控 CUDA 批量 1 前向延迟与参数量的关系。
       STFT 预处理耗时未计入该图。''
改为：``9 个模型的整体准确率 vs.\ CUDA 批量 1 前向延迟，气泡大小 \(\propto\) 参数量
       （warmup 50 / measured 200，complexity\_latency\_table.csv）。STFT 预处理耗时未计入。''

(9) §4.6 fig:seed-stability-all-models (fig15)
当前：``图中术语对照：Overall accuracy=整体准确率，Low-SNR accuracy=低信噪比准确率。
       9 个模型行在三个训练种子上的整体准确率与低信噪比准确率稳定性。''
改为：``9 个模型在 3 个训练种子上的整体与低信噪比准确率稳定性散点（metrics\_test.json）。''

(10) §4.7.3 fig:proposed-per-snr (fig17)
当前：``图中术语对照：SNR=信噪比，Test accuracy=测试集准确率。提案模型 (粗实线，红) 与
       Stage 5A CLDNN (实线，蓝)、Stage 5A fusion\_iq\_stft (虚线，灰)、P1.1 fusion\_iq\_stft
       同 schedule (点线，橙) 的逐 SNR 准确率曲线。所有曲线均为三训练种子均值。灰色阴影区
       为低信噪比范围 (\(\le -6\) dB)，绿色阴影区为高信噪比范围 (\(\ge 8\) dB)。''
改为：``提案模型与三类对照的逐 SNR 准确率曲线（三训练种子均值）。
       灰/绿阴影区分别为低 SNR (\(\le -6\) dB) 与高 SNR (\(\ge 8\) dB) 范围。''
       【注】线型与颜色对照交给 matplotlib legend，不再写入 caption。

(11) §3.6 fig:augmentation-demo (fig23)
当前：``信号域增强示意（QPSK @ +6 dB，样本索引 0，数据源：\texttt{data/raw/radioml2016/RML2016.10a\_dict.pkl}）。
       蓝色实线=I 通道，橙色虚线=Q 通道。(a) 原始 I/Q 时序；(b) 相位旋转 \(\theta=\pi/3\)；
       (c) 循环时移 \(k=+8\)；(d) 两者叠加。四种条件下信号能量不变，调制类别不变，说明
       两种变换均为保标签且保有效 SNR 的信号域增强。''
改为：``信号域增强示例（QPSK @ +6 dB 单样本）。
       (a) 原始；(b) 相位旋转 \(\theta=\pi/3\)；(c) 循环时移 \(k=+8\)；(d) 两者叠加。
       I/Q 通道线型见图例。''
       【注】最后那句关于 ``保标签'' 的论述移到正文 §3.6 已经讲过，不在 caption 重复。

(12) §5.5 fig:proposed-training-curves (fig21)
当前：``四个消融变体（seed 42）训练过程曲线（数据源：各变体 \texttt{seed\_42/metrics.csv}）。
       (a) \texttt{full}；(b) \texttt{arch\_only}；(c) \texttt{arch\_aug}；(d) 四变体验证集
       准确率叠加对比。\texttt{arch\_aug} 在后期与 \texttt{full} 分离，与消融表数值一致。''
改为：``四个消融变体（seed 42）训练曲线（metrics.csv）。
       (a) \texttt{full}；(b) \texttt{arch\_only}；(c) \texttt{arch\_aug}；(d) 四变体 val acc 叠加。''
       【注】``\texttt{arch\_aug} 与 \texttt{full} 分离'' 这句解读移到正文段。
       搜索 §5 ``提案模型反超的解释边界'' 段，把这句话加到正文：
       ``图~\ref{fig:proposed-training-curves} 显示 \texttt{arch\_aug} 在训练后期 val 准确率
        略高于 \texttt{full}，与消融表的 0.6284 vs.\ 0.6264 数值方向一致。''

(13) 附录 fig:low-snr-confusion-panels (fig08)
保留当前 caption 即可（已经简洁），但删去多余的 ``证据源:'' 后缀。

(14) 附录 fig:overall-confusion-panels (fig16)
同 (13)。

【辅助任务】
(15) 检查 §4.7.7 ablation 表 \input{tables/ablation_results} 与 \input{tables/paired_tests_summary}
     是否有类似冗长的 caption；若有，按同样规则精简：
     - 不放术语翻译
     - 不放图例描述
     - 不放正文级别的解读

(16) 检查 §3.6 ``信号域增强'' 文字段是否在 fig23 caption 简化后仍能让读者读懂图——
     若需要，在正文段加一句话补充 ``两种变换均保标签、保有效 SNR''。

【LaTeX 编译验证】
- 修改后必须 cd docs/paper/course_report && rm -f main.bcf main.bbl main.aux &&
  xelatex main.tex && biber main && xelatex main.tex && xelatex main.tex
- 检查 main.log 末尾的 ``Output written on main.pdf (XX pages)'' 与 0 undefined reference

【Git】
- 一次完整 commit："docs(report): 精简全部 14 张数据图 caption 至学术规范长度"
- commit 消息列出每个 fig 的字符数变化（before/after）
- git push origin paper-sci-track

【验收标准】
1. 14 个数据图 caption 全部 ≤ 80 字（中文）；目标 40-60 字。
2. 全部 caption 不再含 ``图中术语对照: X=中文'' 表。
3. 全部 caption 不再含 ``X (粗实线，红色)'' 这类线型描述。
4. 全部 caption 不再含 ``X 说明 Y'' 这类正文级别解读；解读移到正文。
5. PDF 编译通过、0 undefined reference。
6. 报告核心数字（CLDNN 0.6129 / 提案 0.6264 / +1.35 pp）不变。
7. 任何被移到正文的解读句必须能被找到（不是删掉了事）。

可选优化项（如果时间允许）：
- 把所有图注里的 ``证据源: xxx.csv'' 统一改成短括号 ``(xxx.csv)''，更紧凑。
- 检查 fig07 (accuracy-latency-params) 的图例，确保 caption 不需要再强调 ``CUDA 前向延迟''
  这种概念，因为图标题已经是 "Accuracy / Latency / Params bubble"。
````

---

## 使用说明

1. 复制以上 ` ```` ` 包裹的整段，作为下次会话第一条消息。
2. 助手会按 14 项清单逐一改 caption，并把被删的"解读句"对应迁移到正文。
3. 编译后预期：PDF 51 → 50 页（caption 缩减腾出空间使图与正文更紧凑），美观度大幅提升。
4. 若你不希望连带修改正文（即 §5.5 把 caption 解读句搬到正文），告诉助手"只精简 caption 不改正文"。

## 核心原则速查

| 应放在 | 内容 |
|---|---|
| **轴标签** | ``Test accuracy''、``SNR (dB)'' 等单位/变量 |
| **图例 (legend)** | 颜色 / 线型 / 形状 → 模型名映射 |
| **图标题（matplotlib title）** | 1 行内的图主题（可选） |
| **caption（学术）** | 1 个名词性短语 + 关键视觉规约 + 数据源括号 |
| **正文** | 解读句、对比观察、机制猜测、限制 |

把现在的 caption 砍 60-70% 字符量是常规操作。每条上面"改为"后的版本就是目标长度。
