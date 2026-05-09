---
status: draft
section: 5.4 Addendum - Filled MACs / FLOPs / CPU Latency
evidence_sources: PAPER_STAGE6_EXTENDED_COMPLEXITY_ANALYSIS.md, results/paper_stage6/extended_complexity_latency/extended_complexity_latency.csv
warning: separate evidence label CONTROLLED_LATENCY_EXTENDED; not merged into Stage 5A complexity_latency_table.csv; same PyTorch / CUDA build, different device target
---

# Section 5.4 Addendum: Filled MACs / FLOPs / CPU Latency

Evidence markers used in this draft: B1 = `PAPER_STAGE6_EXTENDED_COMPLEXITY_ANALYSIS.md`; B2 = `results/paper_stage6/extended_complexity_latency/extended_complexity_latency.csv`; A3 = `complexity_latency_table.csv` (Stage 5A); P1 = `section4_experimental_protocol.md`; P4 = `section5_4_latency_complexity_caveat.md`.

## 5.4.A Addendum: Filled MACs / FLOPs / CPU latency

This addendum fills the three quantities that Section 5.4 explicitly recorded as empty: MACs, FLOPs, and CPU forward-pass latency. These quantities are reported under the new evidence label `CONTROLLED_LATENCY_EXTENDED` and are stored in `results/paper_stage6/extended_complexity_latency/extended_complexity_latency.csv`. The Stage 5A `complexity_latency_table.csv` is not modified. The PyTorch / CUDA build is identical to Stage 5A's controlled-latency protocol; only the device target changed from CUDA to CPU. Evidence: B1, B2, P1, P4.

The MAC counts are produced by `thop.profile` with a single synthetic sample of the model's required input view. FLOPs are reported as twice the MAC count, following the standard convention used by thop. CPU forward latency is reported as the median over 200 measured iterations after 50 warmup iterations, with `torch.set_num_threads(1)` to reduce variance and to represent a single-thread proxy. Batch sizes are 1 and 256, matching the Stage 5A controlled-latency batches. Evidence: B1, B2, P1.

The MAC ranking under this measurement is `mcldnn` (49.1 M) > `cldnn` (8.7 M) > `resnet1d` (4.9 M) ~ `iq_param_matched` (4.9 M) > `gated_fusion_iq_stft` (2.05 M) ~ `fusion_iq_stft` (2.02 M) > `cnn1d` (1.55 M) ~ `lwamcnet` (1.50 M) > `tfcnn_stft` (0.42 M). Under this same measurement the CPU bs=1 latency ranking is `tfcnn_stft` (0.36 ms) < `cnn1d` (0.41 ms) < `iq_param_matched` (0.69 ms) < `fusion_iq_stft` (0.83 ms) < `resnet1d` (0.89 ms) < `gated_fusion_iq_stft` (1.00 ms) < `cldnn` (1.06 ms) < `lwamcnet` (2.33 ms) < `mcldnn` (2.99 ms). At bs=256 the throughput-style ranking re-orders with `tfcnn_stft` 22.0 ms fastest and `mcldnn` 572.5 ms slowest, with `cldnn` at 182.6 ms intermediate. Evidence: B2.

Two observations should constrain the manuscript discussion. First, `fusion_iq_stft` and `gated_fusion_iq_stft` are both *cheaper in MACs* than the I/Q baselines `resnet1d` and `iq_param_matched`. This rules out the explanation that fusion underperforms because it allocates more compute, and it ties the Section 5.2 trade-off discussion to information / architecture, not to capacity. Second, `lwamcnet` has the smallest parameter count in the matrix (20.4 k) but the second-slowest CPU bs=1 latency (2.33 ms), because depthwise / grouped convolutions used in lightweight AMC architectures do not pay off on a single-thread CPU at small batch. Therefore an efficiency argument that mixes parameter count with CPU latency without a hardware tag would be misleading; the manuscript should cite the table values, not paraphrase them as "lightweight" / "heavy". Evidence: B1, B2, P4.

The addendum also confirms why MCLDNN should not be promoted as a deployment candidate even if its accuracy were stable: MCLDNN's MAC count is 5.7x CLDNN's and its CPU bs=256 latency is 3.1x CLDNN's. Combined with the retained MCLDNN seed-collapse anomaly recorded in Section 5.5, MCLDNN simultaneously has the worst stability and the worst measured runtime in this evaluation set. This statement is bounded to the evaluated environment and `num_threads=1` setting. Evidence: B1, B2, P4.

The addendum does not add STFT-preprocessing-inclusive latency, ARM / mobile / DSP results, or FLOPs for non-standard layers. Section 5.4 should continue to caveat those gaps. Future work that needs deployment-grade timing must re-run the script on the target hardware, which is supported by the script's host metadata block. Evidence: B1.
