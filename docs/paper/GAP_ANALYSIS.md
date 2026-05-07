# Gap Analysis

## Purpose

This file is a working gap-analysis framework. It does not claim that a complete
literature review has already been finished. Each gap must later be validated
against recent AMC literature.

## Common AMC Method Routes

- Raw I/Q deep learning baselines such as CNN, ResNet, LSTM/GRU, and hybrid
  temporal models.
- Time-frequency methods using STFT, spectrograms, CWT, or related transforms.
- Constellation, amplitude-phase, and handcrafted feature representations.
- Complex-valued neural networks and signal-aware architectures.
- Attention-based or Transformer-style models.
- Multi-view or multi-branch fusion methods combining I/Q and transformed views.
- Robustness strategies for low SNR, channel impairment, and domain shift.

## Strengths of I/Q Baselines

- Directly use the original signal representation.
- Avoid extra feature extraction cost.
- Strong high-SNR performance in current RadioML2016.10A experiments.
- Simple training and fast inference compared with on-the-fly time-frequency
  extraction.
- Easier to reproduce and compare.

## Strengths of STFT and Time-Frequency Methods

- Expose local spectral and temporal structures.
- May suppress or reorganize noise effects in ways that help low-SNR samples.
- Provide complementary views when raw time-domain patterns are ambiguous.
- Are intuitive for signal-processing explanation and visualization.

## Problems with Simple Concatenation Fusion

- Treats all SNR regions and all modulation classes with the same fusion policy.
- Can overuse a costly branch when the I/Q branch is already reliable.
- May degrade high-SNR accuracy if STFT features introduce unnecessary variance.
- Does not explicitly model branch reliability.
- Can improve low-SNR accuracy while reducing overall accuracy.

## Core Low-SNR Challenges

- Noise can destroy discriminative I/Q waveform details.
- Some modulation classes become highly confused at very low SNR.
- Improvements can be small and seed-sensitive.
- Overall accuracy can hide low-SNR changes because high-SNR samples are easier.
- Robustness gains must be separated from increased model size or compute cost.

## Gap Observed in This Project

The current full RadioML2016.10A results show a trade-off:

- ResNet1D is best overall.
- `fusion_iq_stft` is better in low-SNR grouped accuracy.
- `fusion_iq_stft` is worse in mid-SNR, high-SNR, and overall accuracy.

This suggests a gap for adaptive fusion: a model should use STFT information when
it is reliable and useful, while preserving I/Q baseline behavior elsewhere.

## Gaps to Validate by Literature Review

- Whether existing AMC papers already solve SNR-aware multi-view fusion in a
  lightweight and reproducible way.
- Whether per-SNR and low-SNR-only results are commonly reported.
- Whether complexity reports include FLOPs, latency, memory, and training cost.
- Whether RadioML2016.10A and RadioML2018.01A are both used for validation.
- Whether published fusion methods rely on heavy attention or Transformer models
  that are outside the intended lightweight scope.
- Whether adaptive gates are supervised by SNR labels, learned without SNR labels,
  or not studied in this context.
