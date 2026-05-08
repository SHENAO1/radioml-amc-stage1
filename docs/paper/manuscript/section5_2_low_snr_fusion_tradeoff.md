---
status: draft
section: 5.2 Low-SNR Fusion Trade-off
evidence_sources: main_table_metrics.csv, low_snr_table.csv, paired_bootstrap_accuracy_deltas.csv, mcnemar_tests.csv
warning: low-SNR trade-off only; no broad fusion superiority; diagnostic and smoke outputs are excluded from main results
---

# Section 5.2 Low-SNR Fusion Trade-off

Evidence markers used in this draft: R1 = `main_table_metrics.csv`; R2 = `low_snr_table.csv`; R3 = `paired_bootstrap_accuracy_deltas.csv`; R4 = `mcnemar_tests.csv`; R5 = `statistical_tests_summary.md`; P1 = `section4_experimental_protocol.md`; P2 = `section5_1_overall_fixed_split_results.md`.

## 5.2 Low-SNR Fusion Trade-off

This subsection addresses RQ2: whether adding a time-frequency view provides a low-SNR benefit under the fixed RadioML2016.10A protocol. The low-SNR subset follows the protocol definition `snr_db <= -6`, and all comparisons remain tied to the fixed split and the three retained training seeds. The discussion is protocol-bounded and is limited to the static `fusion_iq_stft` row; it does not evaluate gated fusion behavior, latency, or anomaly mechanisms. Evidence: P1, R1, R2.

In the low-SNR aggregate table, `cldnn` reached a low-SNR mean accuracy of 0.222386, while `fusion_iq_stft` reached 0.221326 and `iq_param_matched` reached 0.216345. Thus, the static I/Q-STFT fusion row was close to CLDNN in the low-SNR subset and above the parameter-matched I/Q baseline in the same low-SNR metric. These values should be interpreted as observed fixed-split results rather than as evidence of broad multi-view fusion superiority. Evidence: R1, R2.

The paired low-SNR comparison against CLDNN does not support a claim that `fusion_iq_stft` is better than CLDNN. For `fusion_iq_stft` versus `cldnn`, the low-SNR paired bootstrap accuracy delta was -0.001061 with a 95% confidence interval of [-0.003939, 0.001838], which crossed zero. The paired McNemar test was also not significant in this scope, with b = 2955, c = 3011, and p = 0.476423079166. Therefore, the supported wording is that static fusion did not show a significant low-SNR advantage over CLDNN under this protocol. Evidence: R3, R4, R5.

The comparison against the parameter-matched I/Q baseline shows a more nuanced pattern. In the low-SNR subset, `fusion_iq_stft` had a small positive accuracy delta over `iq_param_matched`, with a bootstrap delta of +0.004981 and a 95% confidence interval of [0.001970, 0.007973]. The paired McNemar test also supported a difference in the low-SNR subset, with b = 3335, c = 3072, and p = 0.00106333273429. However, this low-SNR gain was accompanied by an overall accuracy penalty relative to `iq_param_matched`: the main table reports 0.577098 for `fusion_iq_stft` and 0.594462 for `iq_param_matched`, and the paired overall bootstrap delta for the same comparison was -0.017364. Evidence: R1, R3, R4, R5.

Taken together, these results indicate a low-SNR trade-off rather than a general improvement. The time-frequency view may provide low-SNR complementarity relative to a parameter-matched I/Q baseline, but the evidence does not support a significant low-SNR advantage over CLDNN and does not support a broad fusion-superiority claim. The broader interpretation of fusion behavior is therefore deferred to later discussion, while this subsection records only the bounded RQ2 evidence. Evidence: R1, R2, R3, R4, R5.
