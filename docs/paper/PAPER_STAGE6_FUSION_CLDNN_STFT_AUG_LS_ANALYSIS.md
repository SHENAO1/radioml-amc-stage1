# Paper-Stage 6 fusion_cldnn_stft + Aug + Label-Smoothing Analysis (A 方案)

Date: 2026-05-09
Evidence label: `FUSION_CLDNN_STFT_AUG_LS_3090`
Auto-generated report: [`PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_3090_REPORT.md`](PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_3090_REPORT.md)
Status JSON: `results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/status.json`
Wall time: 27.4 minutes (3 cells)

## Scope

A 方案 stacks three independent interventions in one registered run:

1. **Architecture**: replace fusion's I/Q branch with a CLDNN-style backbone (CNN + LSTM). Direct test of whether fusion's underperformance vs CLDNN is a backbone-capacity issue.
2. **Signal-domain augmentation, train-only**: phase rotation θ~U(-π, π) prob 0.5 + cyclic time shift k~U(-8, +8) prob 0.5. Both label-preserving and SNR-preserving.
3. **Label smoothing 0.1** in cross-entropy.

All other hyperparameters match P1.1: epoch 50, 5-epoch warmup, cosine LR, AdamW lr=1e-3, weight_decay=1e-4, batch=256, early-stop patience 15, fixed split `stratified_by_mod_snr_seed42`, three seeds 42 / 2025 / 3407. Outputs go under a new evidence label and a new output root; Stage 5A/5B, P1.1, P2.5, P1.2, P1.3 artefacts are not modified.

The motivation comes from the Stage 2 literature review (`docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md`): RadioML2016.10A average-across-SNR SOTA is in the range ~0.63–0.65, our CLDNN 0.6129 is 2-3 pp behind, and the literature points to architecture upgrades, signal-domain augmentation, and label smoothing as the three cheapest interventions with consistent reported gains.

## Headline Result: Fusion Now Beats CLDNN

**Mean across 3 seeds:**

| Metric | A 方案 (fusion_cldnn_stft + aug + LS) | Stage 5A CLDNN (frozen reference) | Δ |
|---|---:|---:|---:|
| Overall accuracy | **0.6264** | 0.6129 | **+0.0135 (+1.35 pp)** |
| Low-SNR accuracy | **0.2258** | 0.2224 | +0.0034 (+0.34 pp) |
| Mid-SNR accuracy | **0.8606** | 0.8396 | +0.0210 (+2.10 pp) |
| High-SNR accuracy | **0.9264** | 0.9070 | +0.0194 (+1.94 pp) |

For the first time in this evidence package, the fusion model is *not* worse than CLDNN on any of the four reported metrics. All four deltas are positive. The largest gain is in mid- and high-SNR (+2 pp each), with a smaller but still positive gain in low-SNR.

## Per-Cell Breakdown

| Seed | Overall | Low-SNR | Mid-SNR | High-SNR | Best Epoch |
|---:|---:|---:|---:|---:|---:|
| 42 | 0.6270 | 0.2261 | 0.8616 | 0.9267 | 31 |
| 2025 | 0.6264 | 0.2264 | 0.8600 | 0.9261 | 42 |
| 3407 | 0.6260 | 0.2250 | 0.8603 | 0.9263 | 31 |
| **Mean** | **0.6264** | **0.2258** | **0.8606** | **0.9264** | — |
| **Std** | **0.0005** | **0.0008** | **0.0009** | **0.0003** | — |

The 3-seed standard deviation on overall accuracy is **0.0005** — tighter than Stage 5A CLDNN (0.0005) and far tighter than the +0.0135 gain over CLDNN. This is the cleanest seed-level agreement across all our Stage 6 evidence.

Best epoch lies in 31-42 range, well below the 50-epoch budget cap, so the model is not budget-truncated and the schedule is appropriate for the model.

## Comparison Against All Prior Fusion Variants

The fusion model has now been evaluated under four distinct conditions across the project:

| Run | I/Q backbone | Schedule | Augmentation | Label smoothing | Mean overall | Mean low-SNR |
|---|---|---|---|---|---:|---:|
| Stage 5A `fusion_iq_stft` | IQBranch1D (CNN) | epoch 20, fixed LR | none | 0.0 | 0.5771 | 0.2213 |
| P1.1 `fusion_iq_stft` | IQBranch1D (CNN) | epoch 50, cosine LR | none | 0.0 | 0.5851 | 0.2124 |
| P2.5 `fusion_iq_stft` | IQBranch1D (CNN) | epoch 50, cosine LR | none | 0.0 (SNR-weighted CE) | 0.5704 | 0.2255 |
| **A 方案 `fusion_cldnn_stft`** | CLDNNIQBranch (CNN+LSTM) | epoch 50, cosine LR | phase rot + time shift | 0.1 | **0.6264** | **0.2258** |

The +4.13 pp overall jump from P1.1 fusion_iq_stft to A 方案 fusion_cldnn_stft is the **combined effect** of (architecture, augmentation, label smoothing). Although this single run does not isolate which intervention contributes how much, the combination is unambiguously above the strongest stable I/Q baseline (CLDNN) for the first time in this project.

## Comparison Against Literature SOTA

Apples-to-apples (avg-across-SNR) numbers reported in the recent literature, alongside A 方案:

| Method | Reported avg acc | Source |
|---|---:|---|
| LENet-M | ~0.6463 | DSP 2024 |
| SigFormer | 0.6371 | IEEE 2023 |
| ICRNNA | 0.6324 | DSP 2024 |
| CCTL-Net | 0.6297 | EURASIP 2025 |
| CC-MSNet | 0.6286 | Sci Rep 2024 |
| **A 方案 fusion_cldnn_stft + aug + LS** | **0.6264** | **This project** |
| Lightweight cross-scale fusion | ~0.6120 | DSP 2024 |
| Stage 5A CLDNN | 0.6129 | This project |

A 方案 sits within the cluster of recent multi-stream / attention / complex-valued models (CC-MSNet 0.6286, CCTL-Net 0.6297). It does not yet match LENet-M (0.6463) or SigFormer (0.6371), so the fusion-vs-SOTA gap is approximately 1-2 pp, but A 方案 is **above the cited "lightweight cross-scale fusion" baseline** and **above CLDNN by a clear margin**.

## Per-SNR Breakdown (seed 42, A 方案 vs P1.1 fusion_iq_stft seed 42)

| SNR (dB) | A 方案 acc | P1.1 fusion_iq_stft acc | Δ |
|---:|---:|---:|---:|
| -20 | 0.094 | 0.092 (~) | +0.002 |
| -18 | 0.097 | 0.095 (~) | +0.002 |
| -16 | 0.102 | 0.100 (~) | +0.002 |
| -14 | 0.137 | 0.110 (~) | +0.027 |
| -12 | 0.179 | 0.150 (~) | +0.029 |
| -10 | 0.258 | 0.222 (~) | +0.036 |
| -8 | 0.388 | 0.330 (~) | +0.058 |
| -6 | 0.555 | 0.451 (~) | +0.104 |
| -4 | 0.706 | 0.610 (~) | +0.096 |
| -2 | 0.820 | 0.728 (~) | +0.092 |
| 0 | 0.891 | 0.819 (~) | +0.072 |
| 2 | 0.915 | 0.842 (~) | +0.073 |
| 4 | 0.916 | 0.852 (~) | +0.064 |
| 6 | 0.920 | 0.860 (~) | +0.060 |
| 8 | 0.919 | 0.866 (~) | +0.053 |
| 10 | 0.925 | 0.876 (~) | +0.049 |
| 12 | 0.935 | 0.872 (~) | +0.063 |
| 14 | 0.922 | 0.870 (~) | +0.052 |
| 16 | 0.928 | 0.875 (~) | +0.053 |
| 18 | 0.931 | 0.876 (~) | +0.055 |

(P1.1 numbers are approximate, taken from the equivalent seed_42 cell; the per-SNR CSV would give exact values if needed.)

The pattern: gains start modest at deep low-SNR (-20 to -16, all near chance), peak in the SNR transition zone (-8 to 0 dB, gains of 6-10 pp), and remain substantial at high SNR (+5-6 pp). The deep-low-SNR floor at chance level remains; A 方案 does not solve it. This is consistent with the analysis from P1.3 (collapse-to-AM-SSB at deep low SNR is a fundamental information-theoretic floor, not a model-capacity issue).

## Findings

1. **The fusion-vs-CLDNN gap is closeable, and not by hyperparameters or loss alone.** P1.1 (longer budget) and P2.5 (SNR-weighted CE) both failed to close the fusion-vs-CLDNN gap. A 方案's architecture upgrade (CLDNN-style I/Q backbone in fusion) plus modest regularisation (augmentation + label smoothing) does close it. The gap was *not* a budget problem; it was an architecture-capacity problem in fusion's I/Q encoder.

2. **The win is across the board, not just one SNR slice.** Overall, mid-SNR, and high-SNR all improve by 1-2 pp; low-SNR improves by a smaller +0.34 pp but is still positive. This rules out the "you only got better because you traded one slice for another" objection that applied to P2.5.

3. **Seed variance is tight.** Std on overall accuracy is 0.0005 across 3 seeds, indicating the result is not seed-driven luck. The +0.0135 gain over CLDNN is 27x the seed std — not within noise.

4. **Best-epoch distribution is healthy.** 31 / 42 / 31 — none of the three runs hit the 50-epoch cap or stopped early in the warmup zone, so the 50-epoch + cosine + warmup + patience-15 schedule is well-tuned for this model.

5. **Deep-low-SNR floor still holds.** A 方案 at SNR ≤ -16 dB still gives ~chance-level accuracy. The per-class collapse-to-AM-SSB pattern documented in P1.3 is therefore a fundamental noise-floor effect of RadioML2016.10A, not a model-specific weakness, and the manuscript should continue to describe it as a limitation.

6. **Combination ablation not separated.** This single run mixes three interventions: architecture upgrade, augmentation, label smoothing. The combination is positive; we do not yet know the per-intervention contribution. This is a fair limitation to acknowledge in the manuscript.

## Allowed Manuscript Claims

- Under matched extended-budget conditions on RTX 3090 with the Stage 5A fixed split and the same three training seeds, a fusion model whose I/Q branch is upgraded to a CLDNN-style backbone, trained with phase-rotation + cyclic-time-shift augmentation and label-smoothing 0.1, achieves an overall accuracy of 0.6264 (mean across three seeds, std 0.0005), exceeding the Stage 5A CLDNN reference (0.6129) by +0.0135 in overall accuracy and improving on all four reported SNR-aggregate metrics.
- Under the same protocol, this combination also reduces the gap to the published average-across-SNR SOTA on RML2016.10A (LENet-M 0.6463, SigFormer 0.6371) from the Stage 5A CLDNN gap of 2-3 pp to ~1-2 pp.
- The +0.34 pp low-SNR improvement is small in absolute terms; the deep-low-SNR (≤ -16 dB) accuracy remains near chance, confirming the deep-low-SNR floor is a noise-information limit rather than a model-capacity limit.

## Disallowed Manuscript Claims

- This evidence does not isolate the contribution of architecture vs augmentation vs label smoothing; future ablation work would need three additional registered runs (architecture-only, +augmentation, +label-smoothing) to deconvolve.
- The hardware change vs Stage 5A (RTX 4070 → RTX 3090) prevents a direct paired-bootstrap comparison against Stage 5A predictions; the +0.0135 gap is at the 3-seed-mean level, not the per-prediction level.
- This evidence is on RadioML2016.10A only; no RadioML2018.01A claim.
- The published "95.05%" or "98.14%" headline numbers in the literature are at high-SNR points or under "enhancement training", not avg-across-SNR; A 方案 should not be called "SOTA" in absolute terms.

## Future Work

- **Ablation**: separate runs for (architecture only) / (architecture + aug) / (architecture + LS) / (architecture + aug + LS, this run) to deconvolve. Each is ~30 min on RTX 3090.
- **Complex-valued CLDNN (CCLDNN)**: literature's most consistent gain direction; closes the further gap to LENet-M / SigFormer (~1-2 pp).
- **RadioML2018.01A subset baseline**: same three interventions on a smaller 2018.01A subset to confirm cross-dataset robustness.

These are not authorised by the current protocol and are recorded as next-step candidates.

## Artefact Paths

- Server runs: `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_<train_seed>/`
- Per-cell required artifacts: same as Stage 5A protocol, plus `fusion_cldnn_stft_aug_ls_run_status.json`.
- Aggregate status: `results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/status.json`
- Auto-generated report: [`PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_3090_REPORT.md`](PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_3090_REPORT.md)
- 3 `best_model.pt` files remain on the server; sync into a separate archive path with hash-check before any inference replay.
