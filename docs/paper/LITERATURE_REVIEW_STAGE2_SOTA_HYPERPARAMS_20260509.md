# Stage 2 Literature Review: RML2016.10A SOTA + Hyperparameter Recipes

Date: 2026-05-09
Scope: Targeted literature search to recalibrate the project's improvement budget against published SOTA on RadioML2016.10A and identify training-recipe interventions worth testing under our existing fixed-split protocol. This document is **planning evidence**, not new experimental evidence; it does not modify Stage 5A/5B artefacts and does not produce performance claims of its own.

## Why This Review

After P1.1 (extended budget) and P2.5 (SNR-weighted CE) both produced negative results (overall accuracy unchanged or worse, low-SNR collapse-to-AM-SSB intact), we needed to recalibrate before committing to another training run. Two questions:

1. **What is the realistic apples-to-apples ceiling on RadioML2016.10A?** The "95%+ accuracy" numbers commonly cited in industry slides are at high-SNR (≥0 dB) only and are not comparable to our average-across-all-SNRs metric.
2. **Which intervention is most likely to move our CLDNN above 0.6129 average accuracy?** We have three families on the table: architecture upgrade, data augmentation, hyperparameter tweaks.

## Apples-to-Apples Average-Across-All-SNRs SOTA on RadioML2016.10A

The metric reported below is mean test accuracy across the full SNR range (-20 dB to +18 dB, 20 levels), which matches our own `overall_accuracy`. Numbers are taken from the cited papers; we did not re-run them. Cross-paper comparison is approximate because train/test split policies differ between publications.

| Method | Reported avg acc | Architecture family | Notes |
|---|---:|---|---|
| LENet-M | ~0.6463 | Lightweight CNN | Currently the highest reliably reported avg-across-SNR figure we found. |
| SigFormer | 0.6371 | Pyramid Transformer w/ dual-attention | Robust under incomplete signals. |
| ICRNNA | 0.6324 | RNN + attention | Cross-scale feature fusion. |
| CC-MSNet | 0.6286 | Complex-valued CNN, multi-stream | Treats I/Q as a complex tensor. |
| CCTL-Net | 0.6297 | Complex-valued hybrid | +SE attention. |
| Lightweight cross-scale fusion | ~0.6120 | Multi-level recurrent CNN | |
| **Our CLDNN (Stage 5A)** | **0.6129** | CNN + LSTM | Reference for this project. |
| Our `iq_param_matched` | 0.5945 | CNN | Parameter-matched I/Q control. |
| Our ResNet1D | 0.5959 | 1D ResNet | |
| Our `fusion_iq_stft` | 0.5771 | I/Q + STFT static fusion | Static fusion underperforms CLDNN. |

**Implication**: The realistic ceiling is around **0.63–0.65 avg-across-SNR**. Our CLDNN is **2–3 percentage points** below the highest published numbers, and the gap is *not* zero. There is meaningful room to improve.

The "95.05% on RML2016.10A" claim from the dual-attention Transformer paper is a single-SNR-point or "with enhancement training" figure and is not directly comparable to our protocol.

## What Actually Moves The Needle (Per The Literature)

### A. Architecture changes that have repeatedly delivered +1–2 pp
- **Complex-valued networks (CC-MSNet, CCTL-Net)**. Treating I/Q as one complex tensor rather than two real channels is the most consistently reported gain in the 2024–2025 AMR literature. Mechanism: complex convolution preserves phase relationships that real-channel networks must learn implicitly.
- **Transformer / attention hybrids (SigFormer, AMC-Transformer, dual-attention CNN-Transformer)**. Adding a Transformer block on top of CNN features gives small but consistent gains. The simpler "small Transformer encoder over CNN feature map" works better than pure Transformer-from-scratch in the AMR setting.
- **Stronger I/Q backbone in fusion** (our `fusion_cldnn_stft` candidate). Our current static fusion uses a CNN1D-style I/Q branch that is *weaker* in MACs (2.0 M) than even ResNet1D (4.9 M, P1.2 evidence). Replacing the I/Q branch with a CLDNN-style backbone is the most direct test of whether fusion's underperformance vs CLDNN is a backbone capacity issue.

### B. Data augmentation: signal-domain only
- **Image-style mixup directly on I/Q does not work** ([Huang et al. 2022, "Mixing Signals"](https://arxiv.org/abs/2204.03737)). Linear interpolation of I/Q + label interpolation produces non-physical signals.
- **Phase rotation** (apply rotation matrix `[[cos θ, -sin θ], [sin θ, cos θ]]` to (I, Q)) is **label-preserving for the AMC classification task**: the modulation type does not depend on absolute phase, only on the relative structure within the modulation. A random `θ ~ U(-π, π)` is the canonical choice.
- **Time shift** (cyclic roll along the 128-sample axis by a small `k`) is also label-preserving for quasi-stationary signals.
- **Amplitude scaling** changes effective SNR; using it would conflict with our SNR-conditioned analysis pipeline.
- **Additive Gaussian noise** also changes effective SNR; same caveat.
- **SigAugment** (Liu 2023, [Apple Sci 13(5):3177](https://www.mdpi.com/2076-3417/13/5/3177)) reports best results at S=4 augmentation strength on RML2016.10A.

### C. Hyperparameter / training-recipe tweaks
- **Label smoothing 0.1**: standard regularization, typically +0.3–0.5 pp; cheap to add. Conflicts with mixup (don't combine), but we are not using mixup.
- **Learning rate / batch size linear scaling rule**: standard ML wisdom. We are at LR=1e-3, batch=256, which is consistent with published recipes.
- **Warmup + cosine annealing**: already implemented in P1.1 (5-epoch warmup + 50-epoch cosine); P1.1 evidence confirms convergence within budget.
- **Stochastic Weight Averaging (SWA)**: not investigated by AMR papers we surveyed; lower priority.

## What Has Already Been Ruled Out On Our Project

Documented in this project's evidence package:

- **Longer training budget alone** does not shift the overall ranking or low-SNR floor. Stage 5A is not undertrained for the 4 retained models. (See `PAPER_STAGE6_EXTENDED_BUDGET_ANALYSIS.md` and `section7_7_training_budget_sensitivity.md`.)
- **Group-based SNR-weighted CE** (low=2.0, mid=1.0, high=0.7) shifts low-SNR aggregate up by less than 1.5 pp at a larger overall and mid/high cost; deep low-SNR collapse is unchanged. (See `PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_ANALYSIS.md` and `section7_8_low_snr_weighted_ce_outcome.md`.)
- **The collapse-to-AM-SSB pattern at low SNR is not a model-specific quirk** but a shared failure mode across 7/9 of our Stage 5A models. (See `PAPER_STAGE6_LOW_SNR_CONFUSION_ANALYSIS.md` and `section5_2_addendum_low_snr_per_class.md`.)
- **Compute is not the fusion bottleneck**: fusion has *fewer* MACs than ResNet1D and *fewer* MACs than `iq_param_matched`. (See `PAPER_STAGE6_EXTENDED_COMPLEXITY_ANALYSIS.md` and `section5_4_addendum_complexity_latency_filled.md`.)

## Decision For The Next Experiment (A 方案)

Combine three independent interventions in a single registered run, so that we either find a positive contribution (paper narrative recovers) or land a single multi-front negative result (limitations strengthen):

1. **Architecture**: replace fusion's I/Q branch with a CLDNN-style backbone (CNN+LSTM). New model id: `fusion_cldnn_stft`. Expected to test whether fusion's underperformance vs CLDNN is a backbone-capacity issue.
2. **Data augmentation**: phase rotation (θ ~ U(-π, π), prob 0.5) + cyclic time shift (k ~ U(-8, +8), prob 0.5), train-only. Skip amplitude scaling and additive noise to preserve SNR labels.
3. **Label smoothing 0.1** in cross-entropy.

Schedule and split inherit from P1.1: epoch 50, 5-epoch warmup, cosine LR, AdamW, early-stop patience 15, fixed split `stratified_by_mod_snr_seed42`, three seeds 42 / 2025 / 3407.

Output goes under a new evidence label `FUSION_CLDNN_STFT_AUG_LS_3090` and a new output root `results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/`. Stage 5A/5B, P1.1 / P1.2 / P1.3 / P2.5 artefacts are not modified.

Comparison points: same fixed split, three seeds, separate runner.

- **Reference 1**: Stage 5A `cldnn` (overall 0.6129).
- **Reference 2**: Stage 5A `fusion_iq_stft` (overall 0.5771; the model we are upgrading).
- **Reference 3**: P1.1 `fusion_iq_stft` (overall 0.5851; same schedule as A, no augmentation, no label smoothing, weaker IQ backbone).
- **A 方案 target**: beat 0.6129 on overall accuracy (or come within 1 pp while gaining on low-SNR), as a "fusion can be at-parity or better with the strongest I/Q baseline once we close the architecture gap" claim.

## Disallowed / Out-Of-Scope Statements For This Document

- No quantitative claim about A 方案 performance is made here; that is the empirical question of the next experiment.
- No claim about RadioML2018.01A; the project has not run it.
- No claim that complex-valued networks would necessarily produce a larger gain than the chosen combination; that is a separate, untested hypothesis.

## Sources Consulted

- [Efficient convolutional dual-attention transformer for AMR (Applied Intelligence 2024)](https://link.springer.com/article/10.1007/s10489-024-06202-6)
- [CC-MSNet: complex-valued convolutional fusion-type multi-stream spatiotemporal network (Sci Rep 2024)](https://www.nature.com/articles/s41598-024-73547-w)
- [Lightweight cross-scale feature fusion enhanced multi-level recurrent CNN (DSP 2024)](https://www.sciencedirect.com/science/article/abs/pii/S1051200424005682)
- [AMR-Benchmark: unified baselines on RML2016.10a/10b/2018.01a/HisarMod2019.1](https://github.com/Richardzhangxx/AMR-Benchmark)
- [Mixing Signals: signal-domain mixup augmentation for AMR (arXiv 2022)](https://arxiv.org/abs/2204.03737)
- [Data Augmentation for DL-based Radio Modulation Classification (arXiv 1912.03026)](https://ar5iv.labs.arxiv.org/html/1912.03026)
- [SigAugment evaluation on RML2016.10A (Applied Sciences 13 (5):3177)](https://www.mdpi.com/2076-3417/13/5/3177)
- [AI/ML-Based AMR survey (arXiv 2502.05315)](https://arxiv.org/abs/2502.05315)
- [Improved AMR using DL with additive attention](https://www.sciencedirect.com/science/article/pii/S2590123025008606)
- [MAE-SigNet: masked-autoencoder multi-scale attention](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/cmu2.12856)
- [Pyramid Signal Transformer / SigFormer (IEEE 2023)](https://ieeexplore.ieee.org/document/10001593/)
- [LR vs batch size linear scaling rule discussion](https://www.baeldung.com/cs/learning-rate-batch-size)
