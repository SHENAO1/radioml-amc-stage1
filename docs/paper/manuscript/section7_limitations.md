---
status: draft
section: 7 Limitations
evidence_sources: Section 4, Sections 5.1-5.5, Section 6, manifests, environment/sync record, Stage 6A/6B protocol docs
warning: limitations only; no new claims; no diagnostic-as-result claim
---

# Section 7 Limitations

Evidence markers used in this draft: P1 = `section4_experimental_protocol.md`; R1 = `section5_1_overall_fixed_split_results.md`; R2 = `section5_2_low_snr_fusion_tradeoff.md`; R3 = `section5_3_gated_fusion_outcome.md`; R4 = `section5_4_latency_complexity_caveat.md`; R5 = `section5_5_mcldnn_anomaly_retained_negative_evidence.md`; D1 = `section6_discussion.md`; A1 = `main_table_metrics.csv`; A2 = `low_snr_table.csv`; A3 = `complexity_latency_table.csv`; S1 = `statistical_tests_summary.md`; M1 = `ARTIFACT_MANIFEST_PAPER_PACKAGE_20260508.csv`; M2 = `ARTIFACT_MANIFEST_PREDICTIONS_ARCHIVE_20260508.csv`; E1 = `EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`; B1 = `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`; B2 = `PAPER_STAGE6B_SCREENING_PROTOCOL_AND_CANDIDATE_QUEUE.md`.

## 7. Limitations

### 7.1 Dataset and split scope

The supported experimental evidence is limited to RadioML2016.10A under the fixed split `stratified_by_mod_snr_seed42`. The benchmark therefore supports claims about the evaluated 9-model, 3-seed matrix within this dataset and split protocol, but it does not support cross-dataset generalization. No RadioML2018.01A experiment is included in the evidence package, and no result from another dataset is used in the main tables, paired statistical tests, or discussion. Evidence: P1, R1, D1, A1, B1.

The fixed split is useful for reducing sampling variation between model rows, but it also means that the results are tied to one registered partition of RadioML2016.10A. The paired tests strengthen within-split comparisons because predictions are matched by split, seed, and sample identifier, yet they do not replace evaluation on additional splits or datasets. The current manuscript should therefore present its findings as fixed-split evidence rather than as a general AMC ranking. Evidence: P1, S1, M2.

### 7.2 Incomplete deployment-efficiency evidence

The complexity and runtime evidence is incomplete. The supported runtime evidence is restricted to controlled CUDA forward-pass latency with 50 warm-up iterations and 200 measured iterations at batch sizes 1 and 256. These measurements are useful for a scoped runtime comparison, but they do not provide a complete deployment assessment. Evidence: R4, D1, A3, B1.

Several quantities needed for a broader efficiency analysis remain unavailable or incomplete. The aggregate MACs and FLOPs fields are empty, CPU latency is not reported, and STFT preprocessing-inclusive latency is not complete. As a result, the manuscript should not claim CPU runtime behavior, operation-count efficiency, end-to-end preprocessing cost, or hardware-portable deployment behavior from the available evidence. Evidence: R4, D1, A3, E1, B1.

### 7.3 Fusion and gated-fusion interpretation limits

The fusion results should be interpreted as model-specific trade-offs rather than general evidence that multi-view fusion is stronger. The static `fusion_iq_stft` row was close to CLDNN in the low-SNR subset and had a small low-SNR gain over the parameter-matched I/Q baseline, but it was lower overall and did not show a significant low-SNR advantage over CLDNN. This limits the supported interpretation to low-SNR complementarity under the evaluated protocol. Evidence: R2, D1, A1, A2, S1.

The gated fusion row has an even narrower interpretation. In this evidence set, `gated_fusion_iq_stft` did not improve the static fusion baseline and was lower than CLDNN in both overall and low-SNR comparisons. Therefore, it should be treated as a retained negative result for this implementation and protocol, not as evidence of improved robustness. Future fusion, amplitude-phase, or SNR-aware candidates remain planning or diagnostic candidates unless evaluated under a later approved full protocol. Evidence: R3, D1, A1, A2, S1, B1, B2.

### 7.4 Retained MCLDNN anomaly

The MCLDNN row is a limitation of the current benchmark because two of the three registered seeds collapsed to chance-level single-class behavior. Seeds `2025` and `3407` remain part of the Stage 5A/5B evidence and are not excluded from the aggregate. The resulting row should be read as retained negative evidence about stability under the registered protocol, not as a clean representative estimate of a tuned MCLDNN family. Evidence: R5, D1, A1, A2, M2, B1.

This limitation also constrains future interpretation. A later `mcldnn_stable_v2` diagnostic, if implemented, would need a separate model identifier and diagnostic evidence label. It could investigate the collapse mechanism, but it could not retroactively replace, sanitize, or repair the retained Stage 5A MCLDNN aggregate. Evidence: R5, D1, B1, B2.

### 7.5 Artifact and environment limitations

The local evidence package is sufficient for manuscript drafting and statistical interpretation, but it is not a complete local training-weight archive. The paper package contains synced aggregate evidence, diagnostic smoke metadata, and prediction archives; the prediction archive covers 27 Stage 5A prediction files across 9 models and 3 seeds. However, the complete 27 Stage 5A `best_model.pt` files remain on the server and are not synced into the local Stage 5A result tree or paper package. If later work requires model loading, inference replay, or archival completeness, those weights should be synced into a separate archive path and hash-checked before use. Evidence: M1, M2, E1.

There are also package and environment constraints. The paper package manifest records three protocol-expected files missing on the server-side aggregate path, and the statistical `significance_tests.json` exists in the separate statistical-tests package rather than as a rewrite of the Stage 5B aggregate directory. The local environment is CPU-only PyTorch, while the server environment provides the CUDA-capable PyTorch/GPU setup used for future experiments if a later protocol authorizes them. These differences are acceptable for writing and audit work, but they should be recorded before any future experimental continuation. Evidence: M1, E1, S1.

### 7.6 Diagnostic candidates are not main evidence

Stage 6B smoke and diagnostic outputs are excluded from the main result evidence. The existing Stage 6B smoke output verifies code-path and artifact-writer execution for an engineering candidate, but its mock data, diagnostic root, and evidence label prevent it from supporting performance claims or main-table entries. Evidence: P1, D1, B1, B2.

The same boundary applies to future candidate work. Low-SNR weighted loss, amplitude-phase fusion, temporal hybrids, augmentation, or MCLDNN stability diagnostics may be useful for screening, but they remain outside the current main evidence unless a later explicit protocol authorizes a new full experiment. In the current manuscript, they should be treated as future diagnostic directions rather than completed experimental results. Evidence: B1, B2.
