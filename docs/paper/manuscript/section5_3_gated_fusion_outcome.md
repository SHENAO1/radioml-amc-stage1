---
status: draft
section: 5.3 Gated Fusion Outcome
evidence_sources: main_table_metrics.csv, low_snr_table.csv, paired_bootstrap_accuracy_deltas.csv, mcnemar_tests.csv, Stage 6A/6B protocol docs
warning: gated fusion underperformed in this evidence set; no robustness claim; diagnostic and smoke outputs are excluded from main results
---

# Section 5.3 Gated Fusion Outcome

Evidence markers used in this draft: R1 = `main_table_metrics.csv`; R2 = `low_snr_table.csv`; R3 = `paired_bootstrap_accuracy_deltas.csv`; R4 = `mcnemar_tests.csv`; R5 = `statistical_tests_summary.md`; B1 = `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`; B2 = `PAPER_STAGE6B_SCREENING_PROTOCOL_AND_CANDIDATE_QUEUE.md`; P1 = `section4_experimental_protocol.md`; P2 = `section5_1_overall_fixed_split_results.md`; P3 = `section5_2_low_snr_fusion_tradeoff.md`.

## 5.3 Gated Fusion Outcome

This subsection addresses RQ3: whether the gated I/Q-STFT fusion variant improved the static fusion baseline under the same fixed RadioML2016.10A protocol. The comparison focuses on `gated_fusion_iq_stft` relative to the static `fusion_iq_stft` row and to the CLDNN reference used in the previous subsections. As in Section 5.1 and Section 5.2, the interpretation is protocol-bounded and excludes Stage 6B smoke or diagnostic outputs. Evidence: P1, P2, P3, B1, B2.

In the overall main table, the gated variant did not improve the static fusion baseline. `gated_fusion_iq_stft` reached an overall mean accuracy of 0.571947, while `fusion_iq_stft` reached 0.577098 and `cldnn` reached 0.612932. The observed ordering for the overall metric was therefore `gated_fusion_iq_stft` below `fusion_iq_stft`, and both fusion rows below CLDNN. This statement is limited to the evaluated fixed-split evidence set and should not be read as a general conclusion about all possible gating mechanisms. Evidence: R1.

The same pattern appeared in the low-SNR subset. Under the `snr_db <= -6` definition, `gated_fusion_iq_stft` reached a low-SNR mean accuracy of 0.211307, compared with 0.221326 for `fusion_iq_stft` and 0.222386 for `cldnn`. Thus, the gated variant underperformed in both the overall and low-SNR comparisons included in this evidence package. The result does not support a robustness claim for the gated variant. Evidence: R1, R2.

The paired tests support the same interpretation when the gated variant is compared directly with static fusion. For `gated_fusion_iq_stft` versus `fusion_iq_stft`, the overall paired bootstrap delta was -0.005152 with a 95% confidence interval of [-0.006841, -0.003462], which did not cross zero. In the low-SNR subset, the paired bootstrap delta was -0.010019 with a 95% confidence interval of [-0.012746, -0.007292], also not crossing zero. The paired McNemar tests favored the static fusion row as well: for the overall scope, b = 6136, c = 6816, and p = 2.42770091886e-09; for the low-SNR scope, b = 2499, c = 3028, and p = 1.22840259689e-12. Evidence: R3, R4, R5.

The supported conclusion is therefore that the gated fusion variant did not improve the static fusion baseline in this experiment. This does not rule out future gating, amplitude-phase fusion, or SNR-aware training variants, but such variants should be treated as diagnostic candidates unless they are evaluated under the full fixed-split protocol. The Stage 6A and Stage 6B planning documents explicitly separate such future candidates from Stage 5A/5B main-table evidence; any smoke or diagnostic outputs remain outside the main results. Evidence: B1, B2.
