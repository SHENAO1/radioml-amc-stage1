# 提示词：减少文字 + 增加图（5 张新图 + 4 段删减）

> 直接复制下面 ` ``` ` 包裹的整段提示词作为下次会话的第一条消息发给 Claude Code（或其他 AI 助手）。
> 该提示词假设助手会先读 `.ai-context/` 与 `docs/paper/course_report/review/FIGURE_DATA_AUDIT_20260510.md` 取上下文。
> 所有数据源已在本地，**不需要重新启动服务器**；纯本地后处理 + LaTeX 改动。

---

## 复制下面这段（完整提示词）

````
我要继续按"减少文字 + 增加图"方向优化课程报告 (docs/paper/course_report/main.tex)。
先严格阅读以下三份文件取上下文：

1. docs/paper/course_report/review/FIGURE_DATA_AUDIT_20260510.md
   （了解所有图、CSV 数据源、报告数字 vs CSV 的核对结果）
2. .ai-context/05-current-state.md 与 .ai-context/06-session-log.md 顶部条目
   （项目当前状态）
3. docs/paper/course_report/main.tex 与各 sections/*.tex
   （报告当前章节结构）

阅读完后按下面顺序执行四件事，每件事完成后做一次小 git commit。**不要重启服务器**：
所有操作均为本地数据后处理 + LaTeX 改动。

【新增图：5 张】

(A) fig19_ablation_grouped_bars.pdf
- 数据源：results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/<variant>/fusion_cldnn_stft/seed_*/metrics_test.json
            + results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_*/metrics_test.json
- 内容：4 个变体 (arch_only / arch_aug / arch_ls / full) × 4 个 SNR 分组 (Overall/Low/Mid/High)
        分组条形图，每柱顶 mean ± std 误差棒，best 加粗
- 加水平虚线标注 Stage 5A CLDNN baseline (overall=0.6129)
- 写脚本 scripts/paper/plot_ablation_grouped.py，输出
  docs/paper/course_report/figures/fig19_ablation_grouped_bars.{pdf,png}

(B) fig20_proposed_paired_forest.pdf
- 数据源：results/paper_stage6/proposed_paired_tests/paired_bootstrap.csv
- 内容：森林图，纵轴比较名 (proposed vs P1.1 / vs arch_only / vs arch_aug / vs arch_ls)
        每个 × 2 scope (overall / low_snr)，共 8 行；横轴 paired bootstrap delta with 95% CI；
        垂直零线，CI 不跨 0 的标实心，跨 0 的标空心
- 写脚本 scripts/paper/plot_proposed_paired_forest.py

(C) fig21_proposed_ablation_training_curves.pdf
- 数据源：每个变体的 training_summary.json（含 history 列表，每 epoch 有 train_loss/train_acc/val_loss/val_acc）
        路径：results/paper_stage6/.../<variant>/fusion_cldnn_stft/seed_42/training_summary.json
        （只用 seed_42，3 seed 取均值反而模糊）
- 内容：2x2 子图：
        (a) 提案 (full) train/val accuracy 随 epoch 曲线
        (b) arch_only train/val accuracy 曲线 (展示无 aug 时收敛更快但终值低)
        (c) arch_aug train/val accuracy 曲线 (展示加 aug 后收敛更慢但终值更高)
        (d) 4 个变体 val accuracy 重叠对比
- 横轴 0–50 epoch，纵轴 0–1.0 accuracy
- 写脚本 scripts/paper/plot_proposed_training_curves.py

(D) fig22_proposed_vs_stage5a_delta_heatmap.pdf
- 数据源：paper_package/server_sync_20260508/.../main_table_metrics.csv (Stage 5A 9 模型)
        + results/paper_stage6/.../fusion_cldnn_stft_aug_ls_3090/.../metrics_test.json (proposed 3 seed mean)
- 内容：9 行 (Stage 5A 9 模型) × 4 列 (Overall/Low/Mid/High)
        每格 = 提案 mean − 该 baseline mean，单位百分点
        色阶：红 (-) / 绿 (+)，绝对值越大颜色越饱和
        提案 vs cldnn 那一行加粗框
- 写脚本 scripts/paper/plot_delta_heatmap.py

(E) fig23_augmentation_visualization.pdf
- 数据源：data/raw/radioml2016/RML2016.10a_dict.pkl (一个 QPSK @ +6 dB 样本)
- 内容：4 子图 ([2,128] 信号波形可视化)：
        (a) 原始 I/Q 时序波形
        (b) 经过 phase rotation θ=π/3 后
        (c) 经过 cyclic time shift k=+8 后
        (d) 同时经过两者
- 每子图横轴 sample index 0-127，纵轴 amplitude，I 通道蓝色实线 / Q 通道橙色虚线
- 写脚本 scripts/paper/plot_augmentation_demo.py

【删减文字：4 段】

(F) §3.6 提案模型与训练侧干预
- 删除"信号域增强 仅在训练集启用：以概率 0.5 做相位旋转 ... 与以概率 0.5 做循环时移..."
  整段中关于变换数学描述的部分（保留 ``保标签''、``保有效 SNR'' 等关键陈述）
- 改为：``两者对调制类型分类保标签且保有效 SNR (图~\ref{fig:augmentation-demo})；
  幅度缩放与加性高斯噪声因会改变有效 SNR 而不予采用..."
- 在该段后插入 \begin{figure}...\includegraphics{fig23_augmentation_visualization.pdf}...

(G) §4.7.4 提案模型单干预消融与配对统计检验
- 现有内容：introduction 段 + ablation_results 表 + paired_tests_summary 表 + 三段
  以"第一/第二/第三"开头的解读
- 改为：introduction 段 (1 句) + ablation_results 表 + 引用 fig19 + paired_tests 表 +
  引用 fig20 + 一段总结性文字 (约 200 字)，把原三段压缩到一起
- 在表 tab:proposed-ablation-results 后插入 fig19；
  在表 tab:proposed-paired-tests 后插入 fig20

(H) §5 提案模型反超的解释边界
- 现有 1 段长文字 (约 400 字)
- 改为：引用 fig21 训练曲线，用 ``图~\ref{fig:proposed-training-curves} 显示
  arch_aug 与 full 在训练后期 val 曲线分离..." 这种证据指向，文字压缩到 200 字
- 在该段前/后插入 fig21

(I) §4.7.3 提案模型 fusion_cldnn_stft+增强+标签平滑
- 现有：1 个表 (tab:proposed-fusion-cldnn-stft-results) + 引用 fig17 的段 + 文献对比段 +
  解释边界段
- 改为：保留原表，在表后插入 fig22 (Δ 热力图给所有 baseline 而不只是 CLDNN/fusion_iq_stft)，
  把 ``提案模型在四个指标上同时正向超过..." 的段压缩到 1 句话

【ref.bib 不需要新增引用】所有改动只重排现有素材。

【LaTeX 编译验证】
每完成 (A)-(I) 中的一项就：
- python scripts/paper/plot_*.py (检查 rc=0)
- cd docs/paper/course_report && xelatex main.tex && biber main && xelatex main.tex && xelatex main.tex
- 检查 main.log 末尾的 ``Output written on main.pdf (XX pages)" 与 0 undefined reference

【Git】
每完成一个新图或一段删减，做一次小 commit，便于回滚：
- "feat(figures): 新增 figXX_xxx + 改 §X.X 引用"
- "docs(report): §X.X 删减 + 引用 figXX"

最后做一次综合 commit 消息，覆盖：
- 新增图数量 (5)
- 删减段数 (4)
- 起止页数变化 (51 -> ?)
- 各段对应的旧字符数 / 新字符数
然后 git push origin paper-sci-track。

【验收标准】
1. PDF 编译通过，0 undefined reference；
2. fig19-fig23 的数据来源全部从本地 CSV/JSON/pkl 读取，**不能 hardcode 数字** (即使可以从已知正确的报告里 copy)；
3. 5 张新图都有 caption，caption 注明数据源 (e.g., ``三种子均值，metrics_test.json'')；
4. 删减后正文中**不能出现孤立的 \ref{fig:...} 而无解释**——每个图引用前后必须有 1 句话告诉读者图里看什么；
5. 报告核心结论 (CLDNN 0.6129 / 提案 0.6264 / +1.35 pp 拆分) 不变。

【可选优化项 (如果时间允许)】
- 把附录 A 的 ``Training curve" 4 个 PNG 缩略图换成 1 张 TikZ 流程图 (展示 Stage 5A → 扩展实验 → 消融的 evidence label 演化)
- §5.3 融合失败诊断中关于 QAM16/QAM64 召回率 ``一降一升" 的论点，做成 fig13 的子图突出显示

如服务器需要重新启用 (例如要重训某个 cell)，先告诉我，我会让用户提供新的 SSH 信息。
````

---

## 使用说明

1. **复制以上代码块**（从 `我要继续按"减少文字 + 增加图"` 到结尾的反引号之前）。
2. 把整段贴给 Claude Code（或其他 AI 助手）作为新会话的第一条消息。
3. 助手会先读三份上下文文件再开始工作。
4. **如果只想做部分图**：把 (A)-(I) 的列表删一些，留你想要的 2-3 张就好。
5. **如果想要更激进**：在助手做完后再补一句"加做可选优化项"。

## 我的优先建议

如果只能做 3 张图，优先级排序：
1. **fig19 消融条形图**（最大替代价值，能把 §4.7.4 一整段压成 1 句）
2. **fig22 Δ 热力图**（视觉冲击最强，1 张图说完"提案 vs 9 baseline 全表"）
3. **fig21 训练曲线**（最能解释为什么 arch+aug 比 full 略好）

只做这 3 张：净省 ~1 页，信息密度大幅提升，而且都基于已有数据，2-3 小时可完成。