---
status: draft
section: 5.4 Latency and Complexity Caveat
evidence_sources: main_table_metrics.csv, complexity_latency_table.csv, Stage 6A plan
warning: CONTROLLED_LATENCY only; no CPU/FLOPs/preprocessing-inclusive claim
---

# Section 5.4 Latency and Complexity Caveat

Evidence markers used in this draft: R1 = `main_table_metrics.csv`; R2 = `complexity_latency_table.csv`; B1 = `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`; P1 = `section4_experimental_protocol.md`; P2 = `section5_1_overall_fixed_split_results.md`; P3 = `section5_2_low_snr_fusion_tradeoff.md`; P4 = `section5_3_gated_fusion_outcome.md`.

## 5.4 Latency and Complexity Caveat

This subsection addresses RQ4: how the evaluated models compare under the available complexity and latency evidence. The supported latency evidence is restricted to controlled CUDA forward latency. It should be interpreted as a scoped runtime comparison within the measured protocol, not as a complete deployment-efficiency assessment. Evidence: P1, R2, B1.

The controlled latency measurements used 50 warm-up iterations and 200 measured iterations, with batch sizes 1 and 256. The aggregate table reports CUDA forward timing under the `CONTROLLED_LATENCY` evidence label. These measurements are tied to the Stage 5B artifact package and are separated from any Stage 6B smoke or diagnostic outputs. Evidence: P1, R2, B1.

Within this measured scope, the main comparison rows show different relationships between parameter count and CUDA forward timing. `cldnn` has 241,675 trainable parameters and reported CUDA forward times of 1.306352 ms at batch size 1 and 1.543833 ms at batch size 256. `resnet1d` has 111,755 trainable parameters and reported times of 2.081249 ms and 2.098535 ms, while `iq_param_matched` has 136,395 trainable parameters and reported times of 1.250068 ms and 1.273155 ms. The static fusion row, `fusion_iq_stft`, has 98,299 trainable parameters with reported times of 1.844381 ms and 1.857622 ms; the gated fusion row has 134,780 trainable parameters with reported times of 2.535083 ms and 2.545334 ms. These values support a bounded comparison of measured CUDA forward timing, but they should not be converted into a broad efficiency ranking beyond the recorded scope. Evidence: R1, R2.

Several complexity fields remain outside the supported evidence scope. The aggregate MACs and FLOPs fields are empty, and the available package does not provide complete CPU latency or STFT preprocessing-inclusive deployment latency. Consequently, this manuscript should not claim deployment superiority, CPU efficiency, FLOP-level efficiency, or end-to-end preprocessing-inclusive latency advantages. Evidence: R2, B1.

The supported conclusion is therefore limited: the current evidence supports a controlled CUDA forward-latency comparison with reported parameter counts, not a complete deployment-efficiency assessment. Later work could extend the protocol with MACs/FLOPs, CPU measurements, and preprocessing-inclusive timing, but those quantities are not part of the current Stage 5A/5B evidence package. Evidence: R2, B1.
