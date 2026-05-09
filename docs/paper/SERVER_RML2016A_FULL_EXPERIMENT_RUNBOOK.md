# Server RadioML2016.10A Full Experiment Runbook

Date: 2026-05-07

Scope: server-side execution guidance for the future RadioML2016.10A 3-seed
main-table experiment. This runbook is not an instruction to start training from
the local preflight session.

## Guardrails

- Do not start full training until Stage 4E explicitly approves the server run.
- Do not run RadioML2018.01A in this stage.
- Use the fixed split artifact for every model and every train seed.
- Keep train seeds separate from the split seed.
- Treat any subset or mock result as `PRELIMINARY` / `SMOKE TEST`.
- Do not write that fusion is comprehensively better than baselines.

## Required Inputs

- Raw dataset: `data/raw/radioml2016/RML2016.10a_dict.pkl`
- Split NPZ: `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
- Split summary: `data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json`
- Template: `configs/paper/rml2016a_main_table_full_template.yaml`

## Pre-Run Checks

Run these before any full training command:

```powershell
git status --short --branch
python -m pytest --basetemp .pytest_tmp\server_preflight_tests
python scripts/paper/create_split_artifact.py --config configs/stage2_rml2016a_real_full.yaml --output-dir data/splits/rml2016a --dataset rml2016a --strategy stratified_by_mod_snr --seed 42 --test-size 0.2 --val-size 0.1
python scripts/paper/measure_complexity_latency.py --config configs/stage2_rml2016a_real_full.yaml --model cnn1d --device cpu --warmup-iters 1 --measured-iters 2
```

The split artifact command is idempotent only if the source data and split
parameters are unchanged. Preserve the generated summary with the final results.

## Blocking Implementation Check

Before running the 3-seed experiment, confirm that the training entry point loads
`data.split_artifact_npz` and does not regenerate train/val/test splits from the
train seed. The desired protocol is:

- split seed: always `42`;
- train seeds: `42`, `2025`, `3407`;
- test indices: identical for all models and all train seeds.

If the trainer still calls `make_splits(..., seed=train_seed)` for each seed,
do not run the full experiment.

## Main-Table Models

- `cnn1d`
- `resnet1d`
- `tfcnn_stft`
- `fusion_iq_stft`
- `cldnn`
- `mcldnn`
- `lwamcnet`
- `iq_param_matched`
- `gated_fusion_iq_stft`

## Required Per-Run Artifacts

Each run directory must contain:

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

## Final Complexity and Latency

The Stage 4E smoke setting is not final evidence. For final reporting use:

- warmup iterations: at least `50`;
- measured iterations: at least `200`;
- batch sizes: `1` and `256`;
- GPU forward latency excluding preprocessing;
- GPU latency including preprocessing for STFT models;
- CPU latency including preprocessing;
- peak inference memory.

## Result Handling

Write full results under:

```text
results/paper_stage2/rml2016a/<model_id>/seed_<train_seed>/
```

Aggregate only after all required model-seed cells finish and the per-run V2
artifact schema passes validation. Report mean/std across train seeds and keep
single-seed or failed-cell evidence out of the main paper table.
