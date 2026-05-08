# Course Report Evidence Map

本文件定义课程报告正文 claim 与已有 artifact 的绑定关系。除非后续有明确协议授权，本报告不得引入新实验结果，不得重建 Stage 5A/5B 主表，不得使用 Stage 6B smoke/diagnostic 支撑主结论。

## 主表证据

- Source: `paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/main_table_metrics.csv`
- Evidence label: `PROJECT_SUPPORTED`
- Covers: 9 model rows, 3 seeds (`42;2025;3407`), fixed split `stratified_by_mod_snr_seed42`, overall/low/mid/high-SNR accuracy, macro-F1, balanced accuracy, parameter count, latency summary fields.
- Allowed claims:
  - CLDNN has the highest observed overall mean accuracy in this fixed protocol: `0.612932`.
  - ResNet1D and `iq_param_matched` are closest I/Q baselines by overall accuracy in the main table.
  - Static fusion and gated fusion do not exceed CLDNN overall in this evidence set.
  - MCLDNN row remains in the aggregate with high variance and retained failed seeds.
- Forbidden claims:
  - SOTA or broad AMC ranking.
  - Cross-dataset generalization.
  - Fusion or gated fusion broad superiority.
  - Any result involving RadioML2018.01A.

## Low-SNR 证据

- Source: `paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/low_snr_table.csv`
- Evidence label: `PROJECT_SUPPORTED`
- Definition: `snr_db <= -6`, `17600` samples per seed.
- Allowed claims:
  - CLDNN low-SNR mean accuracy: `0.222386`.
  - Static `fusion_iq_stft` low-SNR mean accuracy: `0.221326`, close to CLDNN and above `iq_param_matched` (`0.216345`) in the aggregate table.
  - `gated_fusion_iq_stft` low-SNR mean accuracy: `0.211307`, below static fusion and CLDNN.
  - The supported interpretation is low-SNR trade-off, not broad fusion superiority.
- Forbidden claims:
  - Static fusion is significantly better than CLDNN at low SNR.
  - Gated fusion improves robustness.
  - Low-SNR behavior generalizes beyond this fixed split and model matrix.

## 统计检验证据

- Paired bootstrap source: `paper_package/statistical_tests_20260508/paired_bootstrap_accuracy_deltas.csv`
- McNemar source: `paper_package/statistical_tests_20260508/mcnemar_tests.csv`
- Evidence label: `PROJECT_SUPPORTED`
- Pairing rule: paired by `split_id`, `train_seed`, and `sample_id`; derived from archived Stage 5A predictions.
- Allowed claims:
  - CLDNN vs ResNet1D overall bootstrap delta: `+0.017015`, CI `[0.015318, 0.018697]`; McNemar `p = 1.51833659507e-87`.
  - CLDNN vs `iq_param_matched` overall bootstrap delta: `+0.018470`, CI `[0.016788, 0.020159]`; McNemar `p = 2.85981274787e-104`.
  - `fusion_iq_stft` vs CLDNN low-SNR bootstrap delta: `-0.001061`, CI `[-0.003939, 0.001838]`, crosses zero; McNemar `p = 0.476423079166`.
  - `fusion_iq_stft` vs `iq_param_matched` low-SNR bootstrap delta: `+0.004981`, CI `[0.001970, 0.007973]`; McNemar `p = 0.00106333273429`.
  - `gated_fusion_iq_stft` vs `fusion_iq_stft` deltas are negative for overall and low-SNR scopes.
- Forbidden claims:
  - Any statistical significance statement for comparisons absent from the CSV files.
  - Any test involving Stage 6B outputs.
  - Any bootstrap or McNemar result recomputed in prose without artifact support.

## Latency/Complexity 证据

- Source: `paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/complexity_latency_table.csv`
- Evidence label: `CONTROLLED_LATENCY`
- Protocol: CUDA device, 50 warm-up iterations, 200 measured iterations, batch sizes 1 and 256.
- Allowed claims:
  - Report controlled CUDA forward latency and parameter counts as scoped runtime evidence.
  - CLDNN: 241,675 trainable parameters; batch-1 CUDA forward mean `1.306352 ms`; batch-256 mean `1.543833 ms`.
  - `iq_param_matched`: 136,395 trainable parameters; batch-1 mean `1.250068 ms`; batch-256 mean `1.273155 ms`.
  - Static fusion: 98,299 trainable parameters; batch-1 mean `1.844381 ms`; batch-256 mean `1.857622 ms`.
  - Gated fusion: 134,780 trainable parameters; batch-1 mean `2.535083 ms`; batch-256 mean `2.545334 ms`.
- Forbidden claims:
  - CPU latency claim.
  - FLOPs/MACs efficiency claim, because aggregate MACs/FLOPs fields are empty.
  - STFT preprocessing-inclusive or end-to-end deployment latency claim.
  - Hardware-portable deployment superiority.

## MCLDNN Anomaly 证据

- Sources:
  - `paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/main_table_metrics.csv`
  - `docs/paper/manuscript/section5_5_mcldnn_anomaly_retained_negative_evidence.md`
  - `docs/paper/ARTIFACT_MANIFEST_PREDICTIONS_ARCHIVE_20260508.csv`
- Evidence label: `PROJECT_SUPPORTED`
- Allowed claims:
  - MCLDNN aggregate remains retained negative evidence.
  - Overall accuracy is `0.250083 +/- 0.275698`; macro-F1 is `0.199852 +/- 0.319911`.
  - Seeds `2025` and `3407` collapsed to chance-level single-class behavior and remain included.
  - The conservative interpretation is optimization/initialization sensitivity under the registered protocol, not proven data corruption.
- Forbidden claims:
  - Remove failed seeds from aggregate.
  - Recompute a cleaned MCLDNN result.
  - Use future diagnostic `mcldnn_stable_v2` to repair Stage 5A evidence.

## Package/Manifest/Env 证据

- Paper package manifest: `docs/paper/ARTIFACT_MANIFEST_PAPER_PACKAGE_20260508.csv`
- Predictions archive manifest: `docs/paper/ARTIFACT_MANIFEST_PREDICTIONS_ARCHIVE_20260508.csv`
- Environment and sync record: `docs/paper/EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`
- Allowed claims:
  - Paper package contains synced aggregate evidence and diagnostic-only metadata; manifest rows: 299.
  - Prediction archive contains 27 Stage 5A prediction files, covering 9 models x 3 seeds, with `archive_hash_match`.
  - Statistical-test package contains paired bootstrap, McNemar, significance JSON, summary, and manifests.
  - Complete Stage 5A `best_model.pt` weights are present on server but not synced locally.
  - Local environment is CPU-only PyTorch; server environment has CUDA-capable PyTorch and NVIDIA GeForce RTX 4070.
- Forbidden claims:
  - Local package is a complete trained-weight archive.
  - Statistical tests were generated by rewriting Stage 5B aggregate outputs.
  - This report-writing round ran training or diagnostics.

## Stage 6B Smoke/Diagnostic 排除规则

- Stage 6B evidence labels: `SMOKE TEST`, `DIAGNOSTIC`
- Manifest policy: diagnostic-only, synced for engineering traceability, excluded from Stage 5A/5B main tables.
- Required report wording:
  - Stage 6B smoke/diagnostic outputs may be mentioned only in evidence-boundary, reproducibility, or future-work sections.
  - They must not appear in main result tables, accuracy comparisons, statistical tests, abstract conclusions, or summary conclusions.
  - Any future diagnostic must use separate model identifiers, output roots, and evidence labels before it can be described.
- Explicit forbidden actions:
  - Do not merge Stage 6B metrics into `main_table_metrics.csv` or derived course-report tables.
  - Do not cite Stage 6B mock/tiny/subset/smoke results as performance evidence.
  - Do not describe diagnostic candidates as successful repairs of Stage 5A/5B artifacts.
