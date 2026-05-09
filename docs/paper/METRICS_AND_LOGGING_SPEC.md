# Metrics and Logging Specification

Date: 2026-05-07

Purpose: define result schemas and metric semantics for Paper-Stage 2. This
document is designed to make later experiments auditable and statistically
comparable.

## Metric Definitions

| Metric | Required | Scope | Definition |
|---|---|---|---|
| Overall accuracy | yes | main table | correct test predictions divided by all test samples |
| Low-SNR accuracy | yes | main table | accuracy on `snr <= -6` dB |
| Mid-SNR accuracy | yes | main table | accuracy on `-4 <= snr <= 6` dB |
| High-SNR accuracy | yes | main table | accuracy on `snr >= 8` dB |
| Per-SNR accuracy | yes | curve/table | accuracy for each SNR value |
| Macro-F1 | yes | main table | unweighted mean F1 over modulation classes |
| Low-SNR Macro-F1 | yes | main table | macro-F1 restricted to low-SNR samples |
| Balanced accuracy | recommended | appendix/main | mean recall over classes |
| Per-class accuracy | yes | appendix | class-wise accuracy |
| Confusion matrix | yes | appendix | full test confusion matrix |
| Low-SNR confusion matrix | yes | appendix | confusion matrix restricted to low-SNR samples |
| Params | yes | complexity table | trainable and total parameter counts |
| FLOPs/MACs | yes | complexity table | fixed-shape compute estimate |
| GPU latency excluding preprocessing | yes | complexity table | model forward only |
| GPU latency including preprocessing | yes | complexity table | feature extraction plus forward |
| CPU latency including preprocessing | yes | complexity table | CPU end-to-end inference |
| Peak inference memory | yes | complexity table | max allocated memory during inference |
| Training time per epoch | yes | complexity table | wall-clock time per epoch |

## Main Table Schema

Required columns for `main_table_mean_std.csv`:

| Column | Description |
|---|---|
| `dataset` | e.g. `rml2016a` |
| `split_id` | split artifact id |
| `model_id` | model identifier |
| `input_views` | e.g. `iq`, `stft`, `iq+stft` |
| `num_seeds` | number of training seeds |
| `overall_acc_mean` | mean over seeds |
| `overall_acc_std` | std over seeds |
| `low_snr_acc_mean` | mean over seeds |
| `low_snr_acc_std` | std over seeds |
| `mid_snr_acc_mean` | mean over seeds |
| `mid_snr_acc_std` | std over seeds |
| `high_snr_acc_mean` | mean over seeds |
| `high_snr_acc_std` | std over seeds |
| `macro_f1_mean` | mean macro-F1 |
| `macro_f1_std` | std macro-F1 |
| `low_snr_macro_f1_mean` | mean low-SNR macro-F1 |
| `low_snr_macro_f1_std` | std low-SNR macro-F1 |
| `params_trainable` | trainable parameter count |
| `macs` | MAC count if available |
| `flops` | FLOP count if available |
| `gpu_latency_ms_excl_pre_mean` | GPU forward latency |
| `gpu_latency_ms_incl_pre_mean` | GPU end-to-end latency |
| `cpu_latency_ms_incl_pre_mean` | CPU end-to-end latency |
| `peak_inference_memory_mb` | peak memory |
| `train_time_sec_per_epoch_mean` | mean epoch time |
| `notes` | important caveats |

## Per-SNR Table Schema

Required columns:

- `dataset`
- `split_id`
- `model_id`
- `snr_db`
- `num_samples`
- `accuracy_mean`
- `accuracy_std`
- `macro_f1_mean`
- `macro_f1_std`
- `balanced_accuracy_mean`
- `balanced_accuracy_std`

The paper should include a per-SNR curve. The table can be placed in the
appendix if space is limited.

## Prediction File Schema

Use CSV for simple inspection and optional Parquet for storage efficiency.

Required columns:

- `sample_id`
- `dataset`
- `split_id`
- `split`
- `model_id`
- `train_seed`
- `snr_db`
- `snr_group`
- `modulation`
- `y_true`
- `y_pred`
- `correct`
- `logit_<class_name>`
- `prob_<class_name>`

Optional gated-model columns:

- `gate_scalar`
- `gate_iq_mean`
- `gate_tf_mean`
- `gate_iq_entropy`
- `gate_tf_entropy`
- `snr_group_pred`
- `snr_estimate_db`

Quality rules:

- Each test sample should appear once per model and seed.
- Class-name columns must use the same class order for all models.
- Probabilities must be derived from saved logits using softmax.
- Any calibration or temperature scaling must be recorded separately.

## Complexity JSON Schema

Required fields:

```json
{
  "dataset": "rml2016a",
  "model_id": "resnet1d",
  "input_shapes": {"iq": [1, 2, 128]},
  "params_trainable": 0,
  "params_total": 0,
  "macs": null,
  "flops": null,
  "feature_preprocess": {
    "uses_stft": false,
    "uses_cwt": false,
    "cached": false,
    "cache_size_mb": null
  },
  "software": {
    "python": "",
    "pytorch": "",
    "cuda": ""
  },
  "hardware": {
    "gpu": "",
    "cpu": "",
    "ram_gb": null
  }
}
```

## Latency JSON Schema

Required fields:

```json
{
  "model_id": "fusion_iq_stft",
  "batch_sizes": [1, 256],
  "warmup_iters": 50,
  "measured_iters": 200,
  "gpu_forward_excluding_preprocess_ms": {
    "batch_1": {"mean": null, "median": null, "p95": null, "std": null},
    "batch_256": {"mean": null, "median": null, "p95": null, "std": null}
  },
  "gpu_including_preprocess_ms": {
    "batch_1": {"mean": null, "median": null, "p95": null, "std": null}
  },
  "cpu_including_preprocess_ms": {
    "batch_1": {"mean": null, "median": null, "p95": null, "std": null}
  },
  "stft_preprocess_ms": {
    "batch_1": {"mean": null, "median": null, "p95": null, "std": null}
  },
  "peak_inference_memory_mb": null
}
```

## Reporting Rules

- Main paper claims use full-dataset 3-seed mean/std only.
- Single-seed values are allowed only as preliminary engineering evidence.
- If the best model is not best overall, state the trade-off.
- Always report whether preprocessing is included in latency.
- Do not compare a cached-STFT latency number to an on-the-fly I/Q latency
  number without labeling the difference.
- Do not hide failed SNR regions by reporting only overall accuracy.

## Evidence Tags

Every final table should include a short evidence tag:

- `PROJECT_SUPPORTED`: directly supported by this project's full experiments.
- `LITERATURE_SUPPORTED`: adopted from literature or used as prior-art context.
- `HYPOTHESIS_TEST`: proposed mechanism still under evaluation.
- `PRELIMINARY`: subset or single-seed result, not a paper claim.

