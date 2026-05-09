# Paper-Stage 6 Extended Budget Analysis (RTX 3090)

Date: 2026-05-09
Evidence label: `EXTENDED_BUDGET_3090`
Auto-generated report: [`PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md`](PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md)
Status JSON: `results/paper_stage6/extended_budget_3090/rml2016a/status.json`
Server log: `results/paper_stage6/extended_budget_3090/rml2016a/run.log`

## Scope

This document is an analytical addendum to the auto-generated training report. It compares the P1.1 extended-budget run against the frozen Stage 5A baseline on the same fixed split (`stratified_by_mod_snr_seed42`), and records claim boundaries.

It does **not** modify, replace, or re-aggregate Stage 5A/5B evidence. The Stage 5A main table, low-SNR table, paired statistical tests, and predictions archive remain authoritative for the manuscript main results.

## Hardware and Software Delta

| Item | Stage 5A (frozen) | P1.1 (this run) |
|---|---|---|
| GPU | NVIDIA GeForce RTX 4070, 12 GB | NVIDIA GeForce RTX 3090, 24 GB |
| Architecture | Ada (sm_89) | Ampere (sm_86) |
| NVIDIA driver | 570.211.01 | 570.211.01 |
| CUDA reported | 12.8 | 12.8 |
| PyTorch | 2.9.1+cu128 | 2.9.1+cu128 |
| Python | 3.11.12 | 3.11.12 |
| OS | Ubuntu 22.04 | Ubuntu 22.04.5 |
| Server path | `/hy-tmp/radioml-amc-stage1` | `/hy-tmp/radioml-amc-stage1` (new instance) |
| Epoch budget | 20 | 50 |
| LR schedule | constant 1e-3 (AdamW) | linear warmup 5 + cosine annealing |
| Early-stop patience | 6 | 15 |
| Output root | `results/paper_stage2/rml2016a` | `results/paper_stage6/extended_budget_3090/rml2016a` |
| Models in this run | 9 | 4 (`cldnn`, `resnet1d`, `iq_param_matched`, `fusion_iq_stft`) |
| Train seeds | `42`, `2025`, `3407` | `42`, `2025`, `3407` |
| Total cells | 27 | 12 |
| Wall time | (server-recorded) | 54.4 minutes |

Numerical results are not byte-identical to Stage 5A even for the same `(model, seed)` because the GPU architecture changed; cuDNN may select different convolution kernels under the same algorithm flags. This is registered as a known confound and prevents merging the two evidence sets into one row.

## Aggregate Comparison (mean across 3 seeds)

| Model | Overall (P1.1) | Overall (Stage 5A) | ΔOverall | Low-SNR (P1.1) | Low-SNR (Stage 5A) | ΔLow-SNR | Mid-SNR (P1.1) | Mid-SNR (Stage 5A) | ΔMid-SNR | High-SNR (P1.1) | High-SNR (Stage 5A) | ΔHigh-SNR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cldnn | 0.61448 | 0.61293 | +0.00154 | 0.22205 | 0.22239 | -0.00034 | 0.84371 | 0.83960 | +0.00412 | 0.90848 | 0.90700 | +0.00149 |
| resnet1d | 0.59633 | 0.59592 | +0.00042 | 0.20540 | 0.20587 | -0.00047 | 0.82194 | 0.81972 | +0.00222 | 0.89197 | 0.89217 | -0.00020 |
| iq_param_matched | 0.60111 | 0.59446 | +0.00665 | 0.21424 | 0.21635 | -0.00210 | 0.82447 | 0.81215 | +0.01232 | 0.89359 | 0.88093 | +0.01265 |
| fusion_iq_stft | 0.58510 | 0.57710 | +0.00800 | 0.21240 | 0.22133 | -0.00892 | 0.80247 | 0.78581 | +0.01666 | 0.86464 | 0.84275 | +0.02189 |

## Best-Epoch Distribution

| Model | seed 42 | seed 2025 | seed 3407 | Stage 5A epoch budget | Comment |
|---|---:|---:|---:|---:|---|
| cldnn | 24 | 23 | 27 | 20 | Slightly under-budgeted in Stage 5A; budget extension recovers ~+0.15 pp overall. |
| resnet1d | 15 | 17 | 20 | 20 | Stage 5A budget 20 was already at or above the validation peak; extension does not meaningfully improve overall accuracy. |
| iq_param_matched | 27 | 26 | 21 | 20 | Marginally under-budgeted in Stage 5A; extension recovers ~+0.67 pp overall. |
| fusion_iq_stft | 34 | 42 | 36 | 20 | Strongest under-budgeting, best epoch 34-42; extension recovers ~+0.80 pp overall but **loses 0.89 pp on low-SNR**. |

## Findings

1. **Stage 5A was not materially under-budgeted for the 4 evaluated models.** All four overall-accuracy deltas are below 1 percentage point. ResNet1D's best epoch lies inside the Stage 5A budget window (15-20). For CLDNN and `iq_param_matched`, Stage 5A truncated 4-7 epochs early but lost <1 pp. The previously held hypothesis that "Stage 5A overall accuracy is artificially capped by epoch budget" is not supported by this evidence.

2. **Low-SNR accuracy degraded uniformly under the extended budget.** All four models show a small but consistent low-SNR decrease (-0.03 to -0.89 pp). The largest decrease is on `fusion_iq_stft` (-0.89 pp). Mid- and high-SNR accuracy improved correspondingly (+0.22 to +2.19 pp). The implied effect of cosine LR + epoch 50 is to push the models toward better high-SNR fitting at the cost of low-SNR generalization, which is the opposite of the optimization target for the multi-view low-SNR research question.

3. **The fusion under-budget gap was the largest in absolute epoch terms but not the most useful in result terms.** `fusion_iq_stft` was the only model whose best epoch (34-42) exceeded the Stage 5A budget by a wide margin, yet the recovered overall improvement (+0.80 pp) is still 3 pp below CLDNN, and the low-SNR position relative to CLDNN narrows further. Budget alone therefore cannot close the fusion vs CLDNN gap, which constrains future fusion work to backbone or training-objective changes rather than longer training.

4. **Hardware change consistently shifts results by single-digit basis points.** Across all four models, ΔOverall is within ±1 pp and the ranking ordering relative to Stage 5A is preserved (CLDNN > {iq_param_matched, resnet1d} > fusion_iq_stft). The hardware change is not a confound that flips conclusions in this evaluation, but it does prevent direct paired statistical comparison against Stage 5A predictions.

## Allowed Statements

- Under the same fixed split and three-seed protocol, an extended training budget (epoch 50, cosine LR, 5-epoch warmup) on RTX 3090 yields overall accuracies within ±1 pp of Stage 5A for all four evaluated models.
- The CLDNN-best-overall observation persists under the extended budget (`cldnn` overall 0.6145 > `iq_param_matched` 0.6011 > `resnet1d` 0.5963 > `fusion_iq_stft` 0.5851).
- Low-SNR accuracy did not improve under the extended budget for any of the four models; for `fusion_iq_stft` it decreased by approximately 0.9 pp.

## Disallowed Statements

- This evidence does not justify replacing or recomputing Stage 5A means. The hardware change prevents a clean paired comparison.
- This evidence does not include `cnn1d`, `tfcnn_stft`, `cldnn`-low-SNR-superiority claims beyond Stage 5A's own bootstrap CIs, MCLDNN, `lwamcnet`, or `gated_fusion_iq_stft`. Statements about those rows must continue to come from Stage 5A/5B evidence.
- This evidence does not include RadioML2018.01A.

## Claim Boundary For Manuscript Use

This addendum can be used for one purpose only: as a **sensitivity / robustness check** confirming that Stage 5A's main-table results are not produced by an unrealistically short training budget. The extended-budget run is reported under a separate evidence label `EXTENDED_BUDGET_3090` and a separate output root, and it does not enter the Stage 5A main table, low-SNR table, or paired statistical tests.

If a future protocol explicitly authorizes a re-aggregation, that authorization must register both the GPU/architecture change and the LR schedule change as protocol changes, and it must produce a new evidence label rather than overwriting Stage 5A.

## Artifact Paths

- Server runs: `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/<model_id>/seed_<train_seed>/`
- Per-cell required artifacts: `config_resolved.yaml`, `metrics_test.json`, `metrics_per_snr.csv`, `metrics_per_class.csv`, `predictions_test.csv`, `confusion_overall.csv`, `confusion_low_snr.csv`, `complexity.json`, `latency.json`, `training_summary.json`, `extended_budget_run_status.json`, plus `best_model.pt` and `plots/`.
- Aggregate status: `results/paper_stage6/extended_budget_3090/rml2016a/status.json`
- Auto-generated report: [`PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md`](PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md).

## Required Local Sync If Future Work Needs Weights

The 12 P1.1 `best_model.pt` files remain on the server (`results/paper_stage6/extended_budget_3090/rml2016a/<model_id>/seed_<train_seed>/best_model.pt`). They have not been pulled into the local repository. If subsequent inference, ablation, or paired-comparison work requires these checkpoints locally, follow the same archive policy as Stage 5A: pull into a separate archive path with hash check, do not overwrite `results/`.
