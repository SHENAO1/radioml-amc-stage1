# 下一步执行提示词（方案 A：按审稿意见返修）

> 直接复制下面这段提示词喂给 Claude Code（或其他助手），它会从你**关掉服务器之后**的状态接手，按方案 A 完成必须改的 1、2、3 项与必须改的 4、5（无需服务器）。
> 如果你重新启动服务器，先把新的 SSH host/port/password 写进提示词的"服务器接入"段，再发送。
> 提示词假设助手会先读 `.ai-context/`、`docs/paper/course_report/review/STRICT_REVIEW_20260509.md` 与 `docs/paper/course_report/main.tex` 取上下文。

---

## 复制下面这段（完整提示词）

```
我要继续按方案 A 处理课程报告（路径 docs/paper/course_report/main.tex）。先严格阅读以下三份文件取上下文：

1. docs/paper/course_report/review/STRICT_REVIEW_20260509.md（本次审稿意见与必改项 1-5）
2. .ai-context/05-current-state.md 与 .ai-context/06-session-log.md 顶部条目（项目当前状态）
3. docs/paper/PAPER_STAGE_INDEX.md（已登记的 evidence label 与 policy）

阅读完后按下面顺序执行五件事：

【阶段一：必须改 #3 与 #4 与 #5（无需服务器，立刻可做）】

(A) 修文献对比表口径（审稿意见 #3）
- 编辑 docs/paper/course_report/sections/04_results_statistical_tests.tex 的 §4.7.5 文献校准表
  （label = tab:lit-sota-calibration）
- 把"高 SNR 区间或单点"一列拆成两个 sub-column：avg(SNR>0 dB) 与 peak SNR
- 没数据的留 -- (emdash)；给 peak 但未注明 SNR 点的标 (at +X dB)
- 我们自己的提案模型行需要在两个 sub-column 都给数：avg(SNR>0) 用 metrics_per_snr.csv
  自己计算（取 SNR ∈ {2,4,6,8,10,12,14,16,18} 共 9 点平均），peak SNR 取最高单点

(B) Abstract 砍一半（审稿意见 #4）
- 编辑 docs/paper/course_report/sections/abstract.tex
- 抽出标准 4-block 结构（Background / Methods / Results / Conclusion）
- 删除 §5 sensitivity 内容（"延长训练预算未显著改变排序" 等）
- 仅保留：研究问题 + 主表最强模型 (CLDNN 0.6129) + 提案模型 (0.6264, +1.35 pp) + 限制
- 目标长度 250 字以内中文（约 200 词英文等价）

(C) 补 §5 §6 引用（审稿意见 #5）
- 在 docs/paper/course_report/ref.bib 加：
  - Szegedy 2016 Inception-v3（label smoothing 出处）
  - Krogh & Hertz 1992（weight decay 经典出处）
  - Loshchilov & Hutter 2017 SGDR（cosine LR scheduler 出处）
  - Kingma & Ba 2015 Adam / Loshchilov & Hutter 2019 AdamW
- 在 sections/05_discussion_limitations_reproducibility.tex 与 sections/06_conclusion.tex 中
  按机制层面的解释加 \cite，目标 §5 ≥4 引用、§6 ≥2 引用
- §3 的模型矩阵表（label = tab:method-family-matrix）补 cnn1d / resnet1d / fusion_iq_stft 的
  来源引用（O'Shea 2016 cnn / He 2016 resnet / 自定义需说明）

(D) §5 讨论的解释段落语气校准（审稿意见 #10）
- §5 "提案模型反超的解释" 一节：把"三项干预联合作用，共同把…同时推高，不出现拆东补西"
  改为更谨慎的表述（具体替换文本见审稿意见 #10）
- 强调 "post-hoc mechanistic speculation"，不是已被实验隔离的因果声明

(E) 主表加粗最优值（审稿意见 #11）
- §4.1 的 tab:course-main-results-excerpt：每列最高值加 \textbf{...}

(F) 删除 RML2018.01A 跨数据集承诺（审稿意见 #12）
- §5 局限表 tab:protocol-limitations-next 第 4 行：把"选择 RML2018.01A 子集..."后续处理改为
  "记入未来工作但不在本报告范围内"

(G) 编译验证：cd docs/paper/course_report && biber main && xelatex main.tex && xelatex main.tex
   - 检查 log，确认 0 undefined reference 与少量 warning
   - 提交一次 commit："docs(report): 应用审稿意见非训练改动 (3/4/5/10/11/12)"

【阶段二：必须改 #1 消融实验（需要服务器，本阶段需要确认是否启动）】

(H) 启动服务器或确认现有服务器是否可用
- 如果旧服务器已关：让用户提供新 SSH 信息
- 如果旧服务器仍在：用 scripts/_remote_check.py 验证连通

(I) 写新的消融训练 orchestrator
- 复制 scripts/paper/run_fusion_cldnn_stft_aug_ls_training.py 为 run_fusion_cldnn_stft_ablation.py
- ALLOWED_MODELS 仍为 ["fusion_cldnn_stft"]，但 RESULT_ROOT 改为
  results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a
- 通过 --variant 参数选择三种配置：
  - "arch_only": train.augmentation.enabled=False, train.loss.label_smoothing=0.0
  - "arch_aug":  train.augmentation.enabled=True,  train.loss.label_smoothing=0.0
  - "arch_ls":   train.augmentation.enabled=False, train.loss.label_smoothing=0.1
- 输出根加 variant 子目录
- 新 evidence label：FUSION_CLDNN_STFT_ABLATION_3090
- 在 docs/paper/PAPER_STAGE_INDEX.md 登记新 label policy

(J) 同步 + 启动 + watcher
- 用 scripts/_remote_push_files.py 推 orchestrator + config 到服务器
- tmux session "pab" 跑三 variant 串行（每 variant 3 seeds × 50 epoch ≈ 30 分钟，总 ~1.5 小时）
- 用 scripts/_remote_watch_*.py 模式写新 watcher 后台监控
- 跑完拉回所有 metrics CSV 与 status JSON

【阶段三：必须改 #2 配对统计检验（消融完成后）】

(K) 写 paired bootstrap 脚本
- 在 scripts/paper/ 下新建 run_proposed_paired_tests.py
- 输入：A 方案 fusion_cldnn_stft 的 predictions_test.csv（seed 42/2025/3407）
       与 P1.1 fusion_iq_stft 的 predictions_test.csv（同 seed）
       与 三个 ablation variant 的 predictions_test.csv
- 配对键：(split_id, train_seed, sample_id)
- 计算：
  - 提案 vs P1.1 fusion 的 paired bootstrap 准确率差值（10000 重采样，bootstrap_seed=42）
  - 提案 vs 三个 ablation variant 的同样检验
  - McNemar 检验
- 输出：results/paper_stage6/proposed_paired_tests/{paired_bootstrap.csv, mcnemar.csv, summary.md}

【阶段四：报告整合】

(L) 写 §4.7.7 "提案模型消融与配对检验" 子节
- 表格：4 个 variant × (overall, low, mid, high) mean±std
- 表格：proposed vs P1.1 / proposed vs ablation 的 paired bootstrap CI 与 McNemar p
- 几句解释每个干预的边际贡献

(M) 加审稿意见 #7 的 per-SNR 对比图
- 数据：4 条曲线（Stage 5A CLDNN / Stage 5A fusion_iq_stft / P1.1 fusion_iq_stft / 提案模型）
- 4 个 metrics_per_snr.csv 已在本地
- 写脚本 scripts/paper/plot_proposed_per_snr.py，输出 PDF/PNG 到 docs/paper/course_report/figures/
- 在 §4.7.6 引用该图

(N) 编译验证 + 最终 commit
- biber + xelatex × 2
- commit："feat: 提案模型消融实验 + 配对检验 + per-SNR 对比图"

每个阶段执行完都向用户汇报，等用户确认后再进入下一阶段。如果服务器无法启动，跳过阶段二、三，但在 §3 末与 §5 末显式承认"未做单干预消融，列为未来工作"——这是审稿意见 #1 的最低底线。

最后：提醒用户检查 main.pdf，并在所有变动稳定后再次给 git push origin paper-sci-track。
```

---

## 提示词使用说明

1. **复制以上代码块**（从 `我要继续按方案 A 处理课程报告` 到结尾的反引号之前）
2. 把整段贴给 Claude Code（或其他 AI 助手）作为新会话的第一条消息
3. 助手会先读三份上下文文件再开始工作
4. **如果你已经关闭服务器**：执行到阶段二时助手会问你新的 SSH 信息；如果你不打算重启服务器，直接告诉助手"跳过阶段二、三，按最低底线在 §3 §5 显式声明限制"
5. **如果你不想现在做完所有事**：可以告诉助手"只做阶段一"，然后下次再跑这个提示词做阶段二
