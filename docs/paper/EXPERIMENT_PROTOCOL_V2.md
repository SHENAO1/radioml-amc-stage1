# Experiment Protocol V2

Date: 2026-05-07

Stage: Paper-Stage 2

Purpose: freeze a review-grade experiment protocol before adding new large
training runs. This document is a protocol specification only. It does not
claim that the proposed method works.

## Claim Boundary

Current project-supported facts:

- On RadioML2016.10A full single-seed, ResNet1D is currently best overall.
- `fusion_iq_stft` is only weakly better in the low-SNR group.
- `fusion_iq_stft` is worse than ResNet1D in overall, mid-SNR, and high-SNR
  accuracy.
- Current results cannot support a claim that fusion is comprehensively better
  than I/Q baselines.

Literature-supported facts:

- I/Q CNN, ResNet, CLDNN, MCLDNN, lightweight CNN, attention, complex-valued,
  time-frequency, and multi-view AMC methods are all established prior art.
- Low-SNR robustness and SNR-aware learning are active research directions.
- Reviewers can reasonably expect per-SNR results, ablations, and complexity
  reporting.

Still hypotheses:

- STFT provides complementary low-SNR information after controlling for extra
  parameters and preprocessing cost.
- A lightweight SNR-aware or reliability-aware gate can preserve I/Q behavior at
  mid/high SNR while using STFT selectively at low SNR.
- The current low-SNR trend survives multi-seed testing and stronger baselines.

## Dataset Scope

Primary Stage 2 dataset:

- RadioML2016.10A full dataset.

Stage 2 optional validation:

- RadioML2016.10B or a smaller sanity validation dataset, only if already
  available and storage/runtime are controlled.

Stage 3 validation:

- RadioML2018.01A should be treated as Stage 3 unless the split, logging,
  storage, and baseline protocol are already stable on RadioML2016.10A.
- RadioML2018.01A is required before making a strong generality claim.

Subset policy:

- Subset runs are allowed only for smoke testing, code validation, and cost
  screening.
- Subset results must never appear in the main paper table.
- Every result artifact must include `dataset`, `subset`, `split_id`, and
  `train_seed` metadata.

## Fixed Split Protocol

Use one fixed split for the primary paired comparison:

- split strategy: `stratified_by_mod_snr`
- split seed: `42`
- train/validation/test ratio: `0.70 / 0.10 / 0.20`
- test set: identical across all compared models and seeds

Rationale:

- The existing `make_splits` function supports modulation-SNR stratification.
- A fixed test set enables paired tests such as McNemar and sample bootstrap.
- Training-seed variation should be isolated from test-set variation.

Required split artifacts:

```text
data/splits/rml2016a/stratified_by_mod_snr_seed42.npz
data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json
```

Required NPZ arrays:

- `train_idx`
- `val_idx`
- `test_idx`

Required summary fields:

- dataset name and version;
- source file checksum if available;
- split strategy;
- split seed;
- split ratios;
- class mapping;
- SNR list;
- total sample count;
- per-split modulation counts;
- per-split SNR counts;
- per-split modulation-SNR counts.

Optional robustness split:

- After the main protocol is complete, run split seeds `2025` and `3407` for an
  appendix-level split-sensitivity check.
- Do not mix split-seed and train-seed variance in the main table.

## Training Seed Protocol

Main-table training seeds:

- `42`
- `2025`
- `3407`

Rules:

- All main-table models use the same split artifact.
- All main-table models use the same training seeds.
- Report each seed separately in raw result files.
- Report mean and standard deviation in paper tables.
- Do not claim stable improvement from a single seed.

Recommended deterministic controls:

- set Python, NumPy, and PyTorch seeds;
- record CUDA/cuDNN deterministic flags;
- record hardware, PyTorch version, CUDA version, and GPU model;
- record exact config file and Git commit hash if available.

## SNR Group Definition

Freeze the current project grouping for continuity:

| Group | SNR values |
|---|---|
| Low SNR | `snr <= -6` dB |
| Mid SNR | `-4 <= snr <= 6` dB |
| High SNR | `snr >= 8` dB |

For RadioML2016.10A, this corresponds to:

- low: `-20, -18, -16, -14, -12, -10, -8, -6`
- mid: `-4, -2, 0, 2, 4, 6`
- high: `8, 10, 12, 14, 16, 18`

Boundary-sensitivity ablation:

- Low-SNR alternative A: `snr <= -8`.
- Low-SNR alternative B: `snr <= -4`.
- This belongs in the ablation/appendix, not the primary claim.

## Main Result Artifacts

Use this directory shape:

```text
results/paper_stage2/rml2016a/<model_id>/seed_<train_seed>/
```

Required files per run:

- `config_resolved.yaml`
- `metrics_test.json`
- `metrics_per_snr.csv`
- `metrics_per_class.csv`
- `predictions_test.csv`
- `confusion_overall.csv`
- `confusion_low_snr.csv`
- `complexity.json`
- `latency.json`
- `training_summary.json`

Required aggregate files:

```text
results/paper_stage2/rml2016a/aggregate/main_table_mean_std.csv
results/paper_stage2/rml2016a/aggregate/per_snr_mean_std.csv
results/paper_stage2/rml2016a/aggregate/significance_tests.json
```

## Per-SNR Accuracy Output

Required columns for `metrics_per_snr.csv`:

| Column | Description |
|---|---|
| `dataset` | dataset id, e.g. `rml2016a` |
| `model_id` | model identifier |
| `split_id` | split artifact id |
| `train_seed` | training seed |
| `snr_db` | integer SNR in dB |
| `num_samples` | test samples at this SNR |
| `accuracy` | per-SNR accuracy |
| `macro_f1` | per-SNR macro-F1 |
| `balanced_accuracy` | per-SNR balanced accuracy |

Aggregate per-SNR table:

- one row per `model_id` and `snr_db`;
- include `accuracy_mean`, `accuracy_std`, `macro_f1_mean`, and
  `macro_f1_std` across seeds.

## Sample-Level Prediction Schema

Required columns for `predictions_test.csv`:

| Column | Description |
|---|---|
| `sample_id` | original dataset index |
| `dataset` | dataset id |
| `split_id` | fixed split id |
| `split` | `test` |
| `model_id` | model identifier |
| `train_seed` | training seed |
| `snr_db` | integer SNR in dB |
| `modulation` | class name |
| `y_true` | integer class id |
| `y_pred` | predicted integer class id |
| `correct` | 0 or 1 |
| `logit_<class>` | one column per class |
| `prob_<class>` | one column per class |

Optional columns for gated models:

- `gate_scalar`
- `gate_iq_mean`
- `gate_tf_mean`
- `snr_group_pred`
- `snr_estimate_db`
- `branch_iq_confidence`
- `branch_tf_confidence`

Rules:

- Save logits before applying any calibration.
- Use the same class order across all models.
- Do not overwrite predictions when rerunning a seed; use unique run ids.

## Statistical Testing

Primary comparison:

- proposed gated model versus ResNet1D;
- proposed gated model versus MCLDNN or the strongest reproduced I/Q baseline;
- proposed gated model versus `fusion_iq_stft` static fusion;
- proposed gated model versus parameter-matched I/Q-only baseline.

Required tests:

- paired bootstrap confidence interval for low-SNR accuracy difference;
- paired bootstrap confidence interval for overall accuracy difference;
- McNemar test on paired test predictions for overall and low-SNR subsets;
- seed-level mean/std reporting for every metric.

Bootstrap protocol:

- sample test-set rows with replacement;
- preserve paired predictions from both models;
- use at least 10,000 bootstrap resamples for final tables;
- report 95 percent confidence interval of the metric difference.

Interpretation rules:

- With only 3 seeds, seed-level statistical power is low. Treat mean/std as
  stability evidence, not as a full significance proof.
- If confidence intervals include zero, describe the result as inconclusive.
- If low-SNR improves but overall falls, state it as a trade-off and do not
  claim general superiority.

## Complexity and Latency Protocol

Required complexity metrics:

- trainable parameters;
- total parameters;
- FLOPs or MACs for a fixed input shape;
- model forward GPU latency excluding preprocessing;
- full GPU latency including preprocessing;
- full CPU latency including preprocessing;
- peak inference memory;
- training time per epoch.

Fixed measurement settings:

- input length: RadioML2016.10A native length;
- batch sizes: `1` for deployment latency and `256` for throughput;
- warmup iterations: at least `50`;
- measured iterations: at least `200`;
- report mean, median, p95, and standard deviation;
- run model in eval mode;
- wrap inference in `torch.no_grad()`;
- call `torch.cuda.synchronize()` before and after GPU timing.

STFT accounting:

- `latency_excluding_preprocess`: model forward with all views already prepared.
- `latency_including_preprocess`: I/Q input to final logits, including STFT
  feature construction.
- `stft_preprocess_latency`: STFT feature construction only.
- If STFT is cached, report cache build time and cache size.
- If STFT is on-the-fly, report CPU and GPU preprocessing separately if both
  implementations exist.

Memory accounting:

- GPU peak inference memory should include model parameters, activations, and
  preprocessed view tensors.
- Report CPU memory or cache size for cached STFT in the appendix if cache is
  used.

## Main Table Acceptance Criteria

A model may enter the main paper table only if:

- it was evaluated on the fixed full RadioML2016.10A test split;
- it has 3 training seeds or is clearly marked as preliminary;
- it has per-SNR and grouped-SNR metrics;
- it has sample-level predictions;
- it has complexity and latency measurements;
- it uses the same class mapping and split as the baselines.

## Go/No-Go for Gated Fusion Implementation

Proceed to full gated-fusion experiments only after:

- split artifact generation and prediction logging are implemented;
- CNN1D, ResNet1D, and static `fusion_iq_stft` can be reproduced with the V2
  artifact format;
- at least one stronger baseline plan is implemented or scheduled.

Numerical go criteria for a proposed gated model:

- low-SNR mean accuracy must exceed ResNet1D and MCLDNN-style baseline by at
  least `0.01` absolute accuracy or have a positive paired bootstrap CI;
- low-SNR mean accuracy must exceed static `fusion_iq_stft`;
- mid-SNR and high-SNR drops versus ResNet1D should each be no worse than
  `0.01` absolute accuracy unless the paper is explicitly reframed as a
  low-SNR-only trade-off;
- overall mean accuracy should be at least ResNet1D mean minus `0.005`;
- parameter count should be no more than `1.5x` ResNet1D unless accuracy and
  latency gains clearly justify it;
- full latency including STFT should be no more than `2x` ResNet1D for a
  lightweight claim.

No-go or reframe conditions:

- low-SNR gain disappears across seeds;
- static fusion performs as well as the gate;
- parameter-matched I/Q-only model matches the gate;
- STFT preprocessing dominates latency and breaks the lightweight claim;
- mid/high-SNR collapse remains similar to the current static fusion result.

If low-SNR improves but overall falls:

- reframe as a low-SNR operating-mode method;
- report the overall trade-off explicitly;
- avoid broad AMC superiority language;
- consider an SNR-triggered deployment policy rather than a universal model.

