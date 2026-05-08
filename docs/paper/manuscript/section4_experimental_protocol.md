---
status: draft
evidence_sources: E1-E11
warning: not final manuscript; no SOTA claim; diagnostic and smoke outputs are excluded from main results
---

# Section 4 Experimental Protocol

Evidence markers used in this draft: E1 = `PAPER_STAGE_INDEX.md`; E2 = packaged Stage 5B audit report; E3 = `main_table_metrics.csv`; E4 = `low_snr_table.csv`; E5 = `complexity_latency_table.csv`; E6 = paired bootstrap CSV; E7 = McNemar CSV; E8 = statistical-test summary; E9 = package manifest; E10 = predictions archive manifest; E11 = Stage 6A/6B protocol boundary documents.

## 4. Experimental Protocol

### 4.1 Dataset and Fixed Split

All main experiments in this study were conducted on RadioML2016.10A only. No RadioML2018.01A experiment is included in the evidence package, and no result from another dataset is used in the main tables or statistical comparisons. The main experimental protocol uses a fixed split identified as `stratified_by_mod_snr_seed42`, which was audited across the completed Stage 5A/5B artifacts. The split was treated as an artifact-level protocol component rather than regenerated independently for each model run. Evidence: E1, E2, E3, E9.

The fixed-split design was used to reduce confounding between model differences and sampling variation. All protocol-supported main results are therefore interpreted within this RadioML2016.10A fixed-split setting. Claims in later sections should be read as dataset- and protocol-bounded observations, not as cross-dataset generalization claims. Evidence: E1, E2, E11.

### 4.2 Model Matrix and Input Views

The main model matrix consists of nine planned model rows: `cnn1d`, `resnet1d`, `tfcnn_stft`, `fusion_iq_stft`, `cldnn`, `mcldnn`, `lwamcnet`, `iq_param_matched`, and `gated_fusion_iq_stft`. These models cover raw I/Q baselines, time-frequency input, temporal models, lightweight architectures, a parameter-matched I/Q control, and static or gated multi-view fusion variants. Evidence: E2, E3.

Input views were recorded in the aggregate table and used as part of the model identity. The I/Q-only rows include `cnn1d`, `resnet1d`, `cldnn`, `mcldnn`, `lwamcnet`, and `iq_param_matched`; `tfcnn_stft` uses an STFT view; `fusion_iq_stft` and `gated_fusion_iq_stft` use I/Q plus STFT views. These definitions describe the evaluated model matrix only and do not imply that any fusion variant is generally superior. Evidence: E2, E3, E11.

### 4.3 Training Seeds and Evaluation Metrics

Each main model row was evaluated over three training seeds: `42`, `2025`, and `3407`. The Stage 5B audit verified that the planned 9-model by 3-seed matrix was completed and that the expected split identifier and training seed metadata were present in the audited artifacts. The MCLDNN seeds `2025` and `3407` are retained in the protocol-supported evidence, including their chance-level behavior, and are not excluded from the aggregate row. Evidence: E2, E3.

The aggregate evaluation reports overall accuracy, low-, mid-, and high-SNR accuracy summaries, macro-F1, and balanced accuracy. The low-SNR subset is explicitly defined as `snr_db <= -6`, with low-SNR metrics reported separately from the full test split. Mid- and high-SNR summaries are taken from the packaged aggregate tables and are used as reported protocol fields. Evidence: E3, E4.

### 4.4 Artifact Logging and Evidence Labels

The study uses artifact-level evidence labels to separate main experimental evidence from diagnostic or engineering checks. `PROJECT_SUPPORTED` denotes full RadioML2016.10A Stage 5A/5B evidence eligible for bounded main-table use. `CONTROLLED_LATENCY` denotes the controlled CUDA latency measurements used for the complexity and latency table. `SMOKE TEST` and `DIAGNOSTIC` denote engineering or screening outputs and are not eligible for main result tables. Evidence: E1, E2, E5, E9, E11.

The packaged evidence includes aggregate result tables, latency summaries, prediction archives, and statistical-test artifacts. The statistical tests are derived from archived Stage 5A `predictions_test.csv` files rather than from regenerated model outputs. This artifact separation is used to preserve the original Stage 5A/5B results while enabling paired statistical analysis. Evidence: E6, E7, E8, E9, E10.

### 4.5 Paired Statistical Testing

Paired statistical comparisons were computed from the Stage 5A prediction archives. For each comparison, predictions were paired by `split_id`, `train_seed`, and `sample_id`, ensuring that both models were evaluated on the same test examples under the same split and seed grouping. The paired bootstrap analysis estimates the accuracy delta, defined as `accuracy_delta = acc(model_a) - acc(model_b)`, with 10,000 resamples and bootstrap seed `42`. Evidence: E6, E8, E10.

McNemar tests were also computed from paired correctness outcomes. For each paired comparison, the discordant counts were defined as cases where model A was correct and model B was wrong, and cases where model A was wrong and model B was correct. Statistical-test outputs are reported for both the overall test split and the low-SNR subset `snr_db <= -6`. These tests are used only for the specified Stage 5A comparisons and do not include Stage 6B smoke or diagnostic outputs. Evidence: E6, E7, E8.

### 4.6 Controlled CUDA Latency Measurement

Latency evidence is restricted to controlled CUDA forward-pass measurements. The latency protocol uses 50 warm-up iterations and 200 measured iterations, with batch sizes `1` and `256`. These measurements are reported under the `CONTROLLED_LATENCY` evidence label and are suitable for a scoped complexity and latency table. Evidence: E2, E5.

The latency evidence should not be interpreted as CPU latency, FLOPs/MACs evidence, or preprocessing-inclusive deployment latency. The packaged complexity table contains parameter counts, CUDA forward timing, peak inference memory, and training time per epoch, but the aggregate MACs/FLOPs fields and CPU or preprocessing-inclusive latency fields are not complete evidence for broad deployment claims. Evidence: E5, E11.

### 4.7 Exclusion of Diagnostic and Smoke Outputs

Stage 6B smoke, mock, subset, and diagnostic outputs are explicitly excluded from the main experimental results. The Stage 6B evidence is limited to engineering or screening status and must not be merged into Stage 5A/5B aggregate tables, statistical tests, or main conclusions. Evidence: E1, E8, E11.

This exclusion also applies to any future diagnostic run unless a later protocol explicitly authorizes a new evidence category. In the current manuscript scope, RadioML2016.10A Stage 5A/5B artifacts provide the main `PROJECT_SUPPORTED` evidence, controlled CUDA measurements provide `CONTROLLED_LATENCY` evidence, and smoke or diagnostic outputs remain outside the main experimental protocol. Evidence: E1, E2, E8, E9, E11.
