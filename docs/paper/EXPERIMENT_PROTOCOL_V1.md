# Experiment Protocol V1

## Purpose

This protocol upgrades the SCI-track experiments from course-project evidence to
paper-oriented evidence. It should be finalized before large-scale training.

## Datasets

- Primary: RadioML2016.10A.
- Extension: RadioML2018.01A after the RadioML2016.10A protocol stabilizes.
- Subset experiments are allowed for debugging and early screening only.
- Full-dataset results must be clearly separated from subset results.

## Split Strategy

- Use stratified splits by modulation and SNR.
- Keep train/validation/test split definitions fixed across compared models.
- Record split seed, split ratios, class mapping, SNR list, and sample counts.
- Avoid comparing models trained with different split protocols.

## Seed Strategy

- Use at least three seeds for main paper tables.
- Suggested seeds: 42, 2025, and 3407.
- Report single-seed results only as preliminary evidence.
- Report mean and standard deviation for final claims.

## Metrics

- Overall accuracy.
- Per-SNR accuracy.
- Low/mid/high-SNR grouped accuracy.
- Per-class accuracy.
- Confusion matrix.
- Low-SNR-only confusion matrix if sample-level predictions are saved.
- Accuracy and robustness trade-off plots.

## Complexity Metrics

- Parameter count.
- FLOPs or MACs with a fixed input shape.
- Inference latency.
- Training time.
- Peak GPU memory usage.
- Feature extraction cost for STFT or CWT.
- Hardware and software environment.

## Statistical Reporting

- Report mean plus/minus standard deviation over seeds.
- Keep raw per-seed tables.
- Avoid claiming stable improvements from a single seed.
- When differences are small, describe them as tentative unless statistical
  evidence supports a stronger claim.

## Model Comparisons

Baselines:

- CNN1D.
- ResNet1D.
- TF-CNN with STFT.
- `fusion_iq_stft`.

Planned proposed method:

- SNR-aware gated fusion.
- SNR-free reliability-gated fusion.

## Ablation Dimensions

- Branch: I/Q only, STFT only, I/Q + STFT.
- Gate: no gate, fixed gate, learned gate, SNR-supervised gate, SNR-free gate.
- Loss: standard cross entropy, low-SNR weighted loss.
- Sampler: default sampler, SNR-balanced sampler.
- Augmentation: noise, phase, amplitude, time shift, or other validated signal
  augmentations.

## Experiment Rules

- Do not write subset results as full results.
- Do not write single-seed results as stable conclusions.
- Do not claim the fusion model is comprehensively better than baselines unless
  overall, per-SNR, per-class, complexity, and multi-seed evidence support it.
- Do not use CWT full as a main direction until compute cost is controlled.
- Do not start RadioML2018.01A full experiments before the protocol and storage
  rules are ready.

## Minimum Acceptance for a Paper-Level Result

- Full RadioML2016.10A result.
- At least three seeds for the main comparison.
- Per-SNR and low/mid/high grouped metrics.
- Complexity table.
- Ablation table for the proposed mechanism.
- Clear statement of limitations.
