# Paper-Stage 6 Extended Complexity / Latency Analysis (P1.2)

Date: 2026-05-09
Evidence label: `CONTROLLED_LATENCY_EXTENDED`
Source script: [`scripts/paper/measure_extended_complexity_latency.py`](../../scripts/paper/measure_extended_complexity_latency.py)
Output dir: `results/paper_stage6/extended_complexity_latency/`
Auto-generated table: [`extended_complexity_latency.md`](../../results/paper_stage6/extended_complexity_latency/extended_complexity_latency.md), CSV/JSON co-located.

## Scope

Stage 5A's `complexity_latency_table.csv` reported parameter counts and controlled CUDA forward-pass latency, but its MACs / FLOPs and CPU-latency cells were empty (cf. [`section5_4_latency_complexity_caveat.md`](manuscript/section5_4_latency_complexity_caveat.md)). This addendum fills those cells under a new evidence label so the original Stage 5A artefact is not modified.

Measurements were taken on the RTX 3090 server `i-2.gpushare.com` (Linux 5.15, AMD EPYC 7B12, 64-core / 128-thread CPU, 503 GB RAM). Each measurement uses:

- **MACs**: `thop.profile` with a single synthetic sample, default counters (Conv1D / Conv2D / Linear / BN supported); FLOPs reported as `2 * MACs` per the convention.
- **CPU forward latency**: `torch.utils.benchmark.Timer.timeit(measured=200)` after 50 warmup iterations, with `torch.set_num_threads(1)` to reduce variance and to represent a single-thread deployment proxy.
- **Batch sizes**: 1 (per-sample latency proxy) and 256 (throughput proxy, matching the Stage 5A controlled-latency batch).

PyTorch and CUDA build are identical to the Stage 5A `CONTROLLED_LATENCY` measurement protocol (`torch 2.9.1+cu128`); only the device target changed (CPU vs CUDA).

## Aggregate Table

| model | params | MACs (1 sample) | FLOPs (~2x MACs) | CPU bs=1 ms | CPU bs=256 ms |
|---|---:|---:|---:|---:|---:|
| **tfcnn_stft** | 24,123 | 424,704 | 849,408 | **0.363** | **21.992** |
| **cnn1d** | 37,131 | 1,553,920 | 3,107,840 | 0.411 | 61.285 |
| iq_param_matched | 136,395 | 4,945,408 | 9,890,816 | 0.688 | 74.088 |
| fusion_iq_stft | 98,299 | 2,015,488 | 4,030,976 | 0.834 | 83.240 |
| resnet1d | 111,755 | 4,929,024 | 9,858,048 | 0.891 | 90.929 |
| gated_fusion_iq_stft | 134,780 | 2,051,712 | 4,103,424 | 0.996 | 52.292 |
| **cldnn** | 241,675 | 8,668,544 | 17,337,088 | 1.055 | 182.586 |
| lwamcnet | 20,395 | 1,504,096 | 3,008,192 | 2.327 | 52.871 |
| **mcldnn** | 406,199 | 49,097,472 | 98,194,944 | **2.994** | **572.462** |

(IQR was effectively zero in all cells; `torch.utils.benchmark` adapted iteration counts after warmup and batched timing.)

## Findings

1. **MCLDNN is by far the most expensive model.** 49.1 M MACs is 5.7x CLDNN's 8.7 M and 32.5x ResNet1D's 4.9 M; CPU bs=256 latency is 572 ms vs 183 ms for CLDNN. Combined with Stage 5A's MCLDNN seed-collapse anomaly, this makes MCLDNN the model with both the worst stability and the worst measured runtime in the matrix.

2. **`fusion_iq_stft` has fewer MACs than `resnet1d`.** Static fusion runs at 2.0 M MACs vs ResNet1D's 4.9 M; gated fusion at 2.05 M MACs is also lighter than ResNet1D. This rules out "fusion underperforms because it does less compute" as a viable explanation. The fusion accuracy gap relative to CLDNN is therefore not closed by adding compute (consistent with the P1.1 budget-extension finding).

3. **CLDNN sits at the accuracy / cost knee.** CLDNN's 8.7 M MACs and 1.06 ms CPU bs=1 latency are within 1.3x of ResNet1D's compute, but its accuracy lead at low/mid/high SNR (Stage 5A) is real and not an artefact of higher compute capacity within this matrix.

4. **`tfcnn_stft` is the lightest path but does not justify its accuracy floor.** 0.42 M MACs and 0.36 ms CPU bs=1 latency are the lowest in the matrix, but the Stage 5A overall accuracy 0.5063 is also the lowest among the eight stable rows. The STFT-only branch carries little useful information on its own; this is consistent with `fusion_iq_stft` outperforming `tfcnn_stft` overall but the fusion still falling behind I/Q-only baselines.

5. **`lwamcnet` is parameter-cheap (20k) but CPU-latency expensive (2.3 ms bs=1).** Depthwise / grouped convolutions used in lightweight AMC nets do not pay off on a single-thread CPU at small batch; `cnn1d` (37k params, 0.41 ms) and `tfcnn_stft` (24k params, 0.36 ms) are both faster despite more parameters. A deployment-cost claim must therefore be tied to a specific hardware target.

6. **CPU bs=256 throughput correlates with MACs but not strictly with parameter count.** MCLDNN > CLDNN > ResNet1D ~ iq_param_matched > fusion_iq_stft > cnn1d > gated_fusion_iq_stft ~ lwamcnet > tfcnn_stft. Gated fusion is faster than its parameter count suggests (134k params, 52 ms) because the gate adds little additional compute on top of the static fusion path.

## Manuscript Implications

- Section 5.4 ("Latency and Complexity Caveat") can now cite this addendum to fill in MACs/FLOPs for all nine models and to add a single-thread CPU latency comparison. The original Stage 5A `complexity_latency_table.csv` is not modified; this is a separately labelled addendum.
- The compute argument can be added to the Section 6 discussion of why fusion underperforms: under the evaluated implementation, fusion is **simultaneously cheaper in MACs and weaker in accuracy** than ResNet1D / iq_param_matched, so the gap is an information / architecture issue rather than a budget or capacity issue.

## Disallowed Statements

- These measurements do not provide STFT preprocessing-inclusive latency. The current measurement applies the model to *already-prepared* synthetic STFT tensors of the right shape; the cost of building those tensors from raw I/Q is not captured.
- These measurements use a server-class CPU (EPYC 7B12) with `num_threads=1`. They are not deployment-grade results for ARM, x86 mobile, or DSP targets, and they should not be presented as such.
- These measurements do not include FLOPs for operations thop does not natively support (e.g., custom complex-valued layers if added later). Future work that adds non-standard layers must re-validate the count.

## Reproducibility

- Run the script in-place on any host with the project's training environment:
  - `python scripts/paper/measure_extended_complexity_latency.py`
- Output is deterministic given a fixed PyTorch / CUDA build because the synthetic inputs are sampled from `torch.randn` with default global RNG and timing aggregation uses median over 200 iterations after 50 warmup.
- For a different host's CPU latency profile, re-run on that host; the script writes a JSON metadata block with `host`, `platform`, and PyTorch versions so multiple runs from different hardware can be compared.
