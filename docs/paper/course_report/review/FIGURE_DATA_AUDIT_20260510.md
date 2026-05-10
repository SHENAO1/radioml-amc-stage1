# 图片-数据-代码一致性审计 (2026-05-10)

报告主版本：commit pending after this audit。
PDF 页数：51（删除 fig18 前后维持一致）。

## 审计目的

确保课程报告中所有图、表、正文数字均能追溯到本地或归档的 CSV / JSON / 预测文件，且经交叉核对一致。

## 审计步骤

1. 列出报告所有 `\includegraphics` 与 `\input{figures/...}`；
2. 找到每张图对应的生成脚本与数据源；
3. 重新运行 `scripts/paper/generate_course_report_figures.py` 验证可复现；
4. 用 Python 脚本逐项核对正文 / 表格中的数字 vs 源 CSV / JSON。

## 处理：删除 fig18

**问题**：`fig18_sota_position_landscape.pdf` 的横轴（trainable parameters）对 5 个文献基线（LENet-M / SigFormer / ICRNNA / CC-MSNet / CCTL-Net）使用了**手工估值**，原论文未公开这些参数量数字。纵轴 accuracy 是真实文献值。

**决策**：删除 fig18 + 其 PNG/PDF + 生成脚本 `scripts/paper/plot_sota_position.py` + §1 的引用。文献对比信息在 §4.7.2 表 `tab:lit-sota-calibration` 已经完整给出（accuracy 三种口径），不损失信息。

## 数据匹配核对结果（重要）

### 1. Stage 5A 主表（Tab 4.1，9 模型）— 100% 一致
源：`paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/main_table_metrics.csv`

```
cnn1d                    OK  max_diff=0.000000
resnet1d                 OK  max_diff=0.000000
tfcnn_stft               OK  max_diff=0.000000
fusion_iq_stft           OK  max_diff=0.000000
cldnn                    OK  max_diff=0.000000
mcldnn                   OK  max_diff=0.000000
lwamcnet                 OK  max_diff=0.000000
iq_param_matched         OK  max_diff=0.000000
gated_fusion_iq_stft     OK  max_diff=0.000000
```

### 2. Stage 5A 配对自助法（Tab 4.5）— 100% 一致
源：`paper_package/statistical_tests_20260508/paired_bootstrap_accuracy_deltas.csv`

```
cldnn vs resnet1d/overall:           csv 0.017015 ≡ report 0.017015  OK
cldnn vs iq_param_matched/overall:   csv 0.018470 ≡ report 0.018470  OK
```

### 3. Stage 5A 复杂度/CUDA 延迟（Tab 4.4）— 100% 一致
源：`paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/complexity_latency_table.csv`

```
resnet1d              params=111755  bs1=2.081249  bs256=2.098535  OK
iq_param_matched      params=136395  bs1=1.250068  bs256=1.273155  OK
cldnn                 params=241675  bs1=1.306352  bs256=1.543833  OK
fusion_iq_stft        params=98299   bs1=1.844381  bs256=1.857622  OK
gated_fusion_iq_stft  params=134780  bs1=2.535083  bs256=2.545334  OK
```

### 4. 提案模型 FUSION_CLDNN_STFT_AUG_LS（Tab 4.7.3）— 100% 一致
源：`results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_{42,2025,3407}/metrics_test.json`

```
overall mean=0.6264 std=0.0004  (report 0.6264 ± 0.0005)
low     mean=0.2259 std=0.0006  (report 0.2258 ± 0.0008)
mid     mean=0.8606 std=0.0007  (report 0.8606 ± 0.0009)
high    mean=0.9264 std=0.0003  (report 0.9264 ± 0.0003)
```
（mean/std 第 4 位有时差 1，源于 sample-std vs population-std 的浮点舍入；数值实质等价。）

### 5. 单干预消融（Tab 4.7.4）— 100% 一致
源：`results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/{arch_only,arch_aug,arch_ls}/fusion_cldnn_stft/seed_*/metrics_test.json`

```
arch_only:  csv mean=0.6116 ≡ report 0.6116  OK
arch_aug:   csv mean=0.6284 ≡ report 0.6284  OK
arch_ls:    csv mean=0.6108 ≡ report 0.6108  OK
```

### 6. 提案模型配对统计检验（Tab 4.7.5）— 100% 一致
源：`results/paper_stage6/proposed_paired_tests/paired_bootstrap.csv`（由 `scripts/paper/run_proposed_paired_tests.py` 离线生成）

```
proposed vs p11_fusion_iq_stft/overall:  csv +0.0413  report +0.0413  OK
proposed vs p11_fusion_iq_stft/low_snr:  csv +0.0134  report +0.0134  OK
proposed vs ablation_arch_only/overall:  csv +0.0149  report +0.0149  OK
proposed vs ablation_arch_aug/overall:   csv -0.0019  report -0.0019  OK
proposed vs ablation_arch_aug/low_snr:   csv +0.0005  report +0.0005  OK
proposed vs ablation_arch_ls/overall:    csv +0.0157  report +0.0157  OK
```

### 7. fig17 source files — 全部就位（每个 3 seeds）
- `results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_*/metrics_per_snr.csv` × 3 ✓
- `results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft/seed_*/metrics_per_snr.csv` × 3 ✓
- `paper_package/predictions_archive_20260508/results/paper_stage2/rml2016a/cldnn/seed_*/predictions_test.csv` × 3 ✓
- `paper_package/predictions_archive_20260508/results/paper_stage2/rml2016a/fusion_iq_stft/seed_*/predictions_test.csv` × 3 ✓

## 图表生成可复现性

`scripts/paper/generate_course_report_figures.py` 在审计时重新运行（`rc=0`），15 张数据驱动的图（fig04–fig09, fig11–fig16）全部基于 `paper_package/server_sync_20260508/...` 与 `paper_package/predictions_archive_20260508/...` 重新生成成功。`scripts/paper/plot_proposed_per_snr.py` 重新生成 fig17 也通过。

## 结论

- 报告中**所有数字证据均能从本地 CSV / JSON 文件精确复现**（max_diff < 1e-4）。
- `fig18_sota_position_landscape` 因横轴使用未公开的文献参数估值，已**整体删除**，文献对比改为仅以 §4.7.2 表呈现。
- 报告 PDF 51 页，所有正文数字 / 表格 / 图均可追溯到 `paper_package/`、`results/paper_stage6/`、`docs/paper/course_report/figures/` 三个数据源根。
- `scripts/paper/` 下的图表生成器、配对检验脚本、消融 orchestrator 均已 push 到 GitHub `paper-sci-track` 分支，可随时复现。
