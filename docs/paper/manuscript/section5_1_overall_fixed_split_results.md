---
status: draft
section: 5.1 Overall Fixed-Split Results
evidence_sources: main_table_metrics.csv, paired_bootstrap_accuracy_deltas.csv, mcnemar_tests.csv
warning: protocol-bounded results; no SOTA claim; diagnostic and smoke outputs are excluded from main results
---

# Section 5.1 Overall Fixed-Split Results

Evidence markers used in this draft: R1 = `main_table_metrics.csv`; R2 = `paired_bootstrap_accuracy_deltas.csv`; R3 = `mcnemar_tests.csv`; R4 = `statistical_tests_summary.md`; P1 = `section4_experimental_protocol.md`.

## 5.1 Overall Fixed-Split Results

This subsection addresses RQ1: which evaluated model provides the strongest overall result under the fixed RadioML2016.10A protocol. The comparison uses the fixed split `stratified_by_mod_snr_seed42` and three training seeds, `42`, `2025`, and `3407`, as defined in the experimental protocol. The results in this subsection are therefore protocol-bounded and do not imply cross-dataset generalization or a state-of-the-art claim. Evidence: P1, R1.

Across the nine evaluated model rows, `cldnn` achieved the highest observed overall mean accuracy in the main table, with an overall accuracy of 0.612932 and a macro-F1 of 0.633238. The next closest overall accuracy values were observed for `resnet1d` at 0.595917 and `iq_param_matched` at 0.594462. Other rows, including `cnn1d`, `tfcnn_stft`, `lwamcnet`, `fusion_iq_stft`, and `gated_fusion_iq_stft`, remained below the CLDNN overall mean in this fixed-split table. Evidence: R1.

The paired statistical tests provide additional support for the overall CLDNN comparison against the two closest I/Q baselines. For `cldnn` versus `resnet1d`, the paired bootstrap accuracy delta was +0.017015 with a 95% confidence interval of [0.015318, 0.018697], and the interval did not cross zero. The corresponding McNemar test also supported a paired correctness difference, with b = 7529, c = 5283, and p = 1.51833659507e-87. For `cldnn` versus `iq_param_matched`, the paired bootstrap delta was +0.018470 with a 95% confidence interval of [0.016788, 0.020159], again not crossing zero, and the McNemar test reported b = 7534, c = 5096, and p = 2.85981274787e-104. Evidence: R2, R3, R4.

The overall rows for the fusion models should be interpreted cautiously. In the main table, `fusion_iq_stft` and `gated_fusion_iq_stft` did not exceed the CLDNN overall mean under this fixed-split protocol. This observation is reported only as an overall-result statement; the low-SNR behavior and fusion trade-offs are deferred to the later RQ2 and RQ3 subsections. The wording here should not be read as a broad claim against multi-view fusion in general. Evidence: R1, R4.

The `mcldnn` row is retained in the same main table rather than removed or sanitized. Its aggregate overall value reflects the registered three-seed protocol, including the retained chance-level seeds noted in the audit evidence. This subsection does not analyze the failure mechanism; the MCLDNN stability issue is reserved for the later RQ5 anomaly discussion. Evidence: R1, R4.
