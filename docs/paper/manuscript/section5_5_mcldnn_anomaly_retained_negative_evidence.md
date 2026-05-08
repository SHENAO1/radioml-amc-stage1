---
status: draft
section: 5.5 MCLDNN Anomaly and Retained Negative Evidence
evidence_sources: Stage 5B audit, main_table_metrics.csv, predictions archive manifest, statistical_tests_summary.md, Stage 6A/6B protocol docs
warning: retained negative evidence; no seed exclusion; no diagnostic repair claim
---

# Section 5.5 MCLDNN Anomaly and Retained Negative Evidence

Evidence markers used in this draft: R1 = `main_table_metrics.csv`; R2 = packaged Stage 5B audit report; R3 = `ARTIFACT_MANIFEST_PREDICTIONS_ARCHIVE_20260508.csv`; R4 = `statistical_tests_summary.md`; B1 = `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`; B2 = `PAPER_STAGE6B_SCREENING_PROTOCOL_AND_CANDIDATE_QUEUE.md`; P1 = `section4_experimental_protocol.md`; P2 = `section5_1_overall_fixed_split_results.md`; P3 = `section5_2_low_snr_fusion_tradeoff.md`; P4 = `section5_3_gated_fusion_outcome.md`; P5 = `section5_4_latency_complexity_caveat.md`.

## 5.5 MCLDNN Anomaly and Retained Negative Evidence

This subsection addresses RQ5: how the MCLDNN row should be interpreted when two of the three registered training seeds collapse to chance-level behavior. The row is retained in the main table as retained negative evidence rather than removed, repaired, or re-aggregated. This treatment follows the fixed-split protocol described in Section 4, where each model row is defined by the same three seeds, `42`, `2025`, and `3407`. Under that protocol, the MCLDNN aggregate is a protocol-supported anomaly and remains part of the complete 9-model by 3-seed benchmark matrix. Evidence: P1, P2, R1, R2.

The aggregate metrics show both the performance degradation and the instability of the MCLDNN row. In the main table, `mcldnn` has an overall accuracy of 0.250083 +/- 0.275698 and a macro-F1 of 0.199852 +/- 0.319911. Its low-, mid-, and high-SNR accuracy summaries are 0.131307 +/- 0.069971, 0.318232 +/- 0.393735, and 0.340303 +/- 0.431963, respectively. The Stage 5B audit explains this high variance by seed-specific collapse: seed `42` reached a test accuracy of 0.568432 and macro-F1 of 0.569253, whereas seeds `2025` and `3407` both remained at 0.090909 test accuracy and 0.015152 macro-F1. Those two chance-level seeds are not removed from the aggregate. Evidence: R1, R2.

The Stage 5B audit did not identify an obvious split, label, schema, or artifact failure that would justify deleting the affected seeds. The three MCLDNN runs used matching normalized configurations except for the seed field, the same fixed split, balanced classes, balanced SNR values, and the same train/validation/test sizes. Required artifacts and V2 schema checks also passed for all three runs. The audit instead indicates that seeds `2025` and `3407` stayed near uniform-loss behavior, early-stopped with best epoch `1`, and produced single-class prediction distributions, while seed `42` escaped this state and learned. The most conservative interpretation is therefore optimization or initialization sensitivity under the Stage 5A hyperparameter setting, not a proven data or artifact corruption issue. Evidence: R2, R3.

This protocol boundary prevents several stronger claims. The failed seeds cannot be excluded to report a cleaned MCLDNN estimate, and the aggregate should not be recomputed after removing them. Similarly, planned `mcldnn_stable_v2` diagnostics or any Stage 6B diagnostic work cannot be described as a repair of the Stage 5A MCLDNN result, because those candidates are separate diagnostic scopes and are not main-table evidence. The Stage 6A and Stage 6B protocol documents require future diagnostics to remain separate from the main evidence, with distinct model identifiers, diagnostic labels, and output roots. The statistical-test summary also keeps MCLDNN prediction files in the archive while noting that the specified paired comparisons did not use MCLDNN. Evidence: R3, R4, B1, B2.

The MCLDNN anomaly therefore limits how the MCLDNN row should be interpreted, but it does not invalidate the fixed-split benchmark. The row should be read as retained negative evidence about stability under the registered protocol, not as a clean representative estimate of a fully tuned MCLDNN family. At the same time, the anomaly does not undermine the validity of the remaining Stage 5A/5B model rows, because the audit verified the shared split and artifact schema across the completed matrix. Future diagnostics may investigate the seed-collapse mechanism, but they must remain separate from the main evidence and cannot retroactively replace the retained Stage 5A aggregate. Evidence: R1, R2, R3, B1, B2.

