# Paper Idea V1

## Tentative Chinese Title

面向低信噪比鲁棒自动调制识别的 SNR 感知轻量多视图融合方法

## Tentative English Title

SNR-Aware Lightweight Multi-View Fusion for Robust Automatic Modulation
Classification under Low-SNR Conditions

## Research Question

Can an SNR-aware or reliability-aware fusion mechanism preserve the strong
overall performance of I/Q baselines while using time-frequency representations
to improve low-SNR modulation classification?

## Current Observation

RadioML2016.10A full experiments show that ResNet1D is the best overall model,
while simple I/Q + STFT fusion has a small low-SNR advantage but lower overall,
mid-SNR, and high-SNR accuracy.

## Core Hypothesis

The weakness of simple fusion is not necessarily caused by STFT being useless.
It may be caused by static fusion applying the time-frequency branch with the
same strength across all SNR regions. A lightweight reliability gate may learn
when the STFT branch should contribute more and when the raw I/Q branch should
dominate.

## Method Motivation

Low-SNR signals may obscure time-domain details but preserve partial
time-frequency structures. High-SNR samples may already be well handled by raw
I/Q residual models, making extra time-frequency features unnecessary or even
harmful. SNR-aware gated fusion directly targets this trade-off.

## Expected Contributions

- A lightweight multi-view AMC framework using raw I/Q and STFT features.
- An SNR-aware or SNR-free reliability gate for adaptive branch weighting.
- A low-SNR-focused experiment protocol with per-SNR, grouped-SNR, and per-class
  analysis.
- A complexity-aware comparison showing accuracy, parameter count, FLOPs,
  latency, training time, and memory cost.
- A bounded empirical conclusion on when time-frequency fusion helps AMC.

## Evidence Needed

- Literature review showing the current gap in SNR-aware lightweight fusion.
- At least three seeds for main RadioML2016.10A full experiments.
- Per-SNR curves and low/mid/high grouped accuracy.
- Low-SNR-only confusion matrices and class-level analysis.
- Ablations for gate type, branch removal, weighted loss, sampler, and
  augmentation.
- RadioML2018.01A validation if compute budget allows.

## Claims to Avoid

- Do not claim state of the art without a complete and fair comparison.
- Do not claim fusion is universally better than I/Q baselines.
- Do not present subset results as full-dataset results.
- Do not present single-seed differences as stable statistical conclusions.
- Do not treat CWT full experiments as completed.
