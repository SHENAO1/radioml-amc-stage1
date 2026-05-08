---
status: draft
section: 6 Discussion
evidence_sources: Section 4, Sections 5.1-5.5, main/low-SNR/latency/statistical artifacts, Stage 6A/6B protocol docs
warning: interpretation only; no SOTA claim; no diagnostic-as-result claim
---

# Section 6 Discussion

Evidence markers used in this draft: P1 = `section4_experimental_protocol.md`; R1 = `section5_1_overall_fixed_split_results.md`; R2 = `section5_2_low_snr_fusion_tradeoff.md`; R3 = `section5_3_gated_fusion_outcome.md`; R4 = `section5_4_latency_complexity_caveat.md`; R5 = `section5_5_mcldnn_anomaly_retained_negative_evidence.md`; A1 = `main_table_metrics.csv`; A2 = `low_snr_table.csv`; A3 = `complexity_latency_table.csv`; S1 = `paired_bootstrap_accuracy_deltas.csv`; S2 = `mcnemar_tests.csv`; S3 = `statistical_tests_summary.md`; B1 = `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`; B2 = `PAPER_STAGE6B_SCREENING_PROTOCOL_AND_CANDIDATE_QUEUE.md`.

## 6. Discussion

### 6.1 Protocol-bounded interpretation of the fixed-split benchmark

The central value of this experiment is the controlled comparison protocol rather than an unrestricted performance claim. The main evidence is limited to RadioML2016.10A, the fixed split `stratified_by_mod_snr_seed42`, and the retained three-seed matrix. Within that setting, CLDNN is the strongest observed model among the evaluated rows: it has the highest overall mean accuracy in the main table and is supported by paired bootstrap and McNemar comparisons against the nearest I/Q baselines, `resnet1d` and `iq_param_matched`. This evidence should be read as a protocol-bounded result: it identifies the strongest model in the current fixed-split benchmark, not a universal ranking across datasets, implementations, or deployment settings. Evidence: P1, R1, A1, S1, S2, S3.

The fixed-split design also changes how the weaker rows should be interpreted. Because all model rows share the same split and seed set, a weaker aggregate result is still informative evidence rather than a disposable failed attempt. This is important for the fusion rows and especially for the MCLDNN anomaly: both positive and negative observations are part of the same audit trail. The benchmark therefore supports transparent comparison, but it does not support selective reporting or post hoc removal of inconvenient seeds. Evidence: P1, R1, R5, A1, B1.

### 6.2 Accuracy versus low-SNR trade-offs

The low-SNR results show why overall accuracy alone is not sufficient for AMC interpretation. The static `fusion_iq_stft` row reached a low-SNR mean close to CLDNN and slightly above the parameter-matched I/Q baseline, but it also lost overall accuracy relative to both references. The paired tests reinforce this trade-off: `fusion_iq_stft` did not show a significant low-SNR advantage over CLDNN because the low-SNR confidence interval crossed zero and the McNemar test did not support a paired correctness difference in that scope. At the same time, it showed a small low-SNR gain over `iq_param_matched`, while remaining lower overall. Evidence: R2, A1, A2, S1, S2, S3.

This pattern suggests complementarity under low-SNR conditions, not a general improvement from adding the STFT view. The STFT branch may contribute information for some low-SNR examples, but the aggregate evidence shows that this benefit is not sufficient to offset overall, mid-SNR, and high-SNR losses. The supported interpretation is therefore a low-SNR trade-off: the fusion design is useful for understanding how an additional view behaves under difficult SNR conditions, but it is not justified as a broadly stronger model in this evidence set. Evidence: R2, A1, A2, S1, S3.

### 6.3 Why gated fusion should be treated as a negative result in this evidence set

The gated fusion row should be interpreted as a negative result for the evaluated implementation and protocol. If the gate had successfully learned a beneficial view-weighting strategy, it would be expected to improve the static fusion row or at least preserve its low-SNR behavior. Instead, `gated_fusion_iq_stft` was lower than `fusion_iq_stft` in both overall and low-SNR accuracy. The paired bootstrap intervals for `gated_fusion_iq_stft` versus `fusion_iq_stft` were negative in both scopes and did not cross zero, and the McNemar tests favored the static fusion row. Evidence: R3, A1, A2, S1, S2, S3.

The result should not be generalized into a claim that gating is inherently ineffective. It does show that this particular gated I/Q-STFT design did not improve the static fusion baseline under the current fixed-split evidence set. This distinction matters because Stage 6A and Stage 6B keep future candidates, such as alternative views, SNR-aware objectives, or diagnostic gating variants, outside the main result evidence unless they pass a later approved protocol. For the current manuscript, the gated row is best treated as retained negative evidence that constrains the interpretation of the fusion direction. Evidence: R3, B1, B2.

### 6.4 Runtime evidence as scoped CUDA latency, not deployment efficiency

The runtime evidence supports only a scoped CUDA forward-latency discussion. The latency table was produced under a controlled protocol with 50 warm-up iterations, 200 measured iterations, and batch sizes 1 and 256. Within that scope, the table provides useful context: CLDNN combines the strongest observed accuracy with measured CUDA forward times of 1.306352 ms at batch size 1 and 1.543833 ms at batch size 256, while `iq_param_matched`, `fusion_iq_stft`, and `gated_fusion_iq_stft` show different timing and parameter-count profiles. These values can support a bounded accuracy-runtime discussion, but only under the recorded CUDA measurement setting. Evidence: R4, A1, A3, B1.

The available evidence does not support broader runtime claims. The MACs and FLOPs fields are empty, CPU latency is not reported, and STFT preprocessing-inclusive latency is not complete. As a result, the manuscript should not infer end-to-end runtime behavior, hardware portability, or preprocessing cost from the CUDA forward table alone. The correct interpretation is that the current evidence identifies controlled forward-pass timing differences, while a more complete runtime study would require additional CPU, preprocessing, and operation-count measurements under a separately registered protocol. Evidence: R4, A3, B1.

### 6.5 Retained negative evidence and reproducibility implications

The MCLDNN anomaly illustrates why retained negative evidence is part of a reproducible protocol. The main table keeps all three registered MCLDNN seeds, including the seed `2025` and seed `3407` chance-level collapses. The Stage 5B audit did not identify a split, label, schema, or artifact corruption issue that would justify deleting those seeds; instead, it interpreted the behavior as optimization or initialization sensitivity under the Stage 5A hyperparameter setting. Retaining this row prevents the benchmark from becoming a post hoc selection of successful runs only. Evidence: R5, A1, A2, B1.

This retained anomaly does not invalidate the rest of the benchmark. The other rows remain interpretable under the same fixed split, seed policy, artifact schema, and statistical-test framework. The anomaly does, however, limit how MCLDNN should be discussed: it is not a clean representative estimate of a tuned MCLDNN family, and it should not be repaired retroactively by a future diagnostic run. Stage 6B explicitly separates mock, subset, smoke, and diagnostic outputs from Stage 5A/5B main evidence. Future diagnostics may investigate the seed-collapse mechanism, but they must remain outside the main tables unless a later full protocol creates a new evidence category. Evidence: P1, R5, S3, B1, B2.

