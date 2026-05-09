# Paper-Stage 4A Readiness Report

Date: 2026-05-07

Stage: Paper-Stage 4A

Scope: validate the V2 experiment infrastructure, mock/subset smoke paths, and
minimal scalar gated-fusion prototype before any full RadioML2016.10A training.

This report is engineering readiness evidence only. It is not paper performance
evidence.

## Guardrails

- No RadioML2016.10A full training was run.
- No RadioML2018.01A experiment was run.
- Only unit tests, mock smoke tests, and one tiny RadioML2016.10A subset smoke
  test were run.
- All smoke outputs are `PRELIMINARY` or `SMOKE TEST`.
- No claim is made that fusion or gated fusion is better than any baseline.

## Context Read

The following protocol files were read before validation:

- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `docs/paper/BASELINE_MATRIX_STAGE2.md`
- `docs/paper/ABLATION_PLAN_STAGE2.md`
- `docs/paper/SNR_AWARE_GATED_FUSION_DESIGN_V1.md`

The following Stage 3 implementation files were inspected:

- `src/radioml_amc/data/split.py`
- `src/radioml_amc/reporting/paper_outputs.py`
- `src/radioml_amc/training/metrics.py`
- `src/radioml_amc/training/trainer.py`
- `src/radioml_amc/models/gated_fusion.py`
- `src/radioml_amc/profiling/complexity.py`
- `scripts/paper/create_split_artifact.py`
- `scripts/paper/measure_complexity_latency.py`

## Unit Tests

Command:

```text
python -m pytest --basetemp .pytest_tmp\stage4a_final_suite
```

Result:

```text
24 passed, 1 skipped in 4.79s
```

Earlier full-suite run also passed:

```text
24 passed, 1 skipped in 9.40s
```

## Mock Split Artifact Smoke Test

Command:

```text
python scripts\paper\create_split_artifact.py --config .pytest_tmp\stage4a_mock_config.yaml --output-dir .pytest_tmp\stage4a_split --dataset mock_radioml --strategy stratified_by_mod_snr --seed 42
```

Result:

- `.pytest_tmp/stage4a_split/stratified_by_mod_snr_seed42.npz` created.
- `.pytest_tmp/stage4a_split/stratified_by_mod_snr_seed42_summary.json` created.

Status: passed.

## Complexity and Latency Smoke Tests

Commands:

```text
python scripts\paper\measure_complexity_latency.py --config .pytest_tmp\stage4a_mock_config.yaml --model cnn1d --output .pytest_tmp\stage4a_latency\cnn1d.json --device cpu --warmup-iters 1 --measured-iters 2
python scripts\paper\measure_complexity_latency.py --config .pytest_tmp\stage4a_mock_config.yaml --model resnet1d --output .pytest_tmp\stage4a_latency\resnet1d.json --device cpu --warmup-iters 1 --measured-iters 2
python scripts\paper\measure_complexity_latency.py --config .pytest_tmp\stage4a_mock_config.yaml --model fusion_iq_stft --output .pytest_tmp\stage4a_latency\fusion_iq_stft.json --device cpu --warmup-iters 1 --measured-iters 2
python scripts\paper\measure_complexity_latency.py --config .pytest_tmp\stage4a_mock_config.yaml --model gated_fusion_iq_stft --output .pytest_tmp\stage4a_latency\gated_fusion_iq_stft.json --device cpu --warmup-iters 1 --measured-iters 2
```

Result files:

- `.pytest_tmp/stage4a_latency/cnn1d.json`
- `.pytest_tmp/stage4a_latency/resnet1d.json`
- `.pytest_tmp/stage4a_latency/fusion_iq_stft.json`
- `.pytest_tmp/stage4a_latency/gated_fusion_iq_stft.json`

Status: passed after a small fix.

Issue found and fixed:

- Initial latency smoke failed for `cnn1d` and `resnet1d` because the script
  inherited `features.views=["iq","stft"]` from the config and passed a dict to
  I/Q-only models.
- Fix: `scripts/paper/measure_complexity_latency.py` now forces
  `features.views = model_required_views(model_id)` before creating synthetic
  input.

Remaining limitation:

- FLOPs/MACs remain `null`; current script measures parameter count and latency
  only. FLOPs/MACs should be added before final paper tables.

## Mock 1-Epoch Training Smoke Test

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4a_mock_config.yaml --models cnn1d resnet1d fusion_iq_stft gated_fusion_iq_stft --output .pytest_tmp\stage4a_comparison
```

Run directories:

- `.pytest_tmp/stage4a_runs/20260507_225308_cnn1d`
- `.pytest_tmp/stage4a_runs/20260507_225311_resnet1d`
- `.pytest_tmp/stage4a_runs/20260507_225311_fusion_iq_stft`
- `.pytest_tmp/stage4a_runs/20260507_225312_gated_fusion_iq_stft`

Required artifact check:

| Run | Required files complete |
|---|---|
| `cnn1d` | yes |
| `resnet1d` | yes |
| `fusion_iq_stft` | yes |
| `gated_fusion_iq_stft` | yes |

Files checked for each run:

- `metrics.json`
- `metrics_test.json`
- `metrics_per_snr.csv`
- `metrics_per_class.csv`
- `predictions_test.csv`
- `confusion_overall.csv`
- `confusion_low_snr.csv`
- `complexity.json`
- `latency.json`
- `training_summary.json`

Status: passed.

Important caveat:

- Mock accuracy values are engineering smoke-test outputs only. They must not be
  cited as research evidence.

## RadioML2016.10A Real Subset Smoke Test

Availability check:

- `data/raw/radioml2016/RML2016.10a_dict.pkl` exists.

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4a_real_subset_config.yaml --models gated_fusion_iq_stft --output .pytest_tmp\stage4a_real_subset_comparison
```

Subset settings:

- modulations: `BPSK`, `QPSK`, `8PSK`, `QAM16`
- SNRs: `-6`, `0`, `6`, `12`
- max samples per modulation-SNR group: `10`
- total samples: `160`
- epochs: `1`
- device: CPU

Run directory:

- `.pytest_tmp/stage4a_real_subset_runs/20260507_225415_gated_fusion_iq_stft`

Required artifact check:

| Run | Required files complete |
|---|---|
| `gated_fusion_iq_stft` real subset smoke | yes |

Status: passed.

Important caveat:

- This is a tiny subset smoke test only. Its accuracy is not a research result.

## Gated Fusion Prototype Checks

Command:

```text
$env:PYTHONPATH='src'; python -
```

Checks performed:

- `model_required_views("gated_fusion_iq_stft") == ["iq", "stft"]`
- forward shape is `[batch, num_classes]`
- `forward_with_aux` returns `gate_scalar`
- `gate_scalar` shape is `[batch, 1]`
- `gate_scalar` values are in `[0, 1]`
- complexity/latency script supports `gated_fusion_iq_stft`

Result:

```text
gated_fusion_iq_stft checks passed
```

Status: passed.

## Infrastructure Readiness

Ready:

- fixed split artifact save/load;
- sample-level prediction CSV;
- per-SNR metrics;
- per-class metrics;
- macro-F1 and low-SNR macro-F1;
- confusion CSV outputs;
- complexity JSON skeleton;
- latency JSON skeleton;
- minimal scalar SNR-free gated-fusion model registration;
- mock and tiny real-subset smoke paths.

Not yet paper-ready:

- no full RadioML2016.10A V2 reruns;
- no multi-seed main-table results;
- no CLDNN/CNN-LSTM baseline;
- no MCLDNN baseline;
- no LWAMCNet or MCNet baseline;
- no parameter-matched I/Q-only baseline;
- no FLOPs/MACs implementation;
- no final latency protocol with production warmup/measured iteration counts;
- no gated-fusion performance evidence.

## Go/No-Go Decision

Decision: allow entry into Stage 4B.

Rationale:

- The V2 infrastructure passes unit tests and smoke tests.
- The gated-fusion prototype is callable and measurable.
- Required artifact files are generated for mock and tiny real-subset smoke
  runs.

Boundary:

- Do not begin full RadioML2016.10A training yet.
- Stage 4B should choose and implement stronger baselines and a
  parameter-matched I/Q-only control before any gated-fusion paper claim.

## Issues to Fix Before Full Paper Experiments

Must fix:

- Implement at least one strong baseline path, preferably MCLDNN or CLDNN first.
- Implement a parameter-matched I/Q-only baseline.
- Add FLOPs/MACs measurement or explicitly document why unavailable.
- Replace placeholder `latency.json` from the training loop with measured
  latency reports from `scripts/paper/measure_complexity_latency.py` before main
  tables.

Should fix:

- Improve `scripts/run_stage2_ablations.py` message that currently says mock
  ablation even when a real subset smoke test is run.
- Add gate-value logging to `predictions_test.csv` for gated models; current
  trainer logs logits and probabilities but not gate columns.
- Add an aggregate main-table builder for multi-seed runs after baselines are
  implemented.

## Stage 4B Prompt Draft

```text
You are acting as an AMC SCI reviewer, PyTorch research engineer, and experiment
protocol gatekeeper.

Current project:
radioml-amc-stage1

Current branch:
paper-sci-track

Current stage:
Paper-Stage 4B: strong baseline implementation priority and first baseline
implementation.

Strict rules:
1. Do not run RadioML2016.10A full training.
2. Do not run RadioML2018.01A.
3. Use only unit tests, mock smoke tests, and at most tiny real-subset smoke
   tests with one epoch.
4. Do not claim fusion or gated fusion is better.
5. Do not overwrite existing dirty changes.

Start by reading:
- docs/paper/PAPER_STAGE4A_READINESS_REPORT.md
- docs/paper/BASELINE_MATRIX_STAGE2.md
- docs/paper/EXPERIMENT_PROTOCOL_V2.md
- docs/paper/METRICS_AND_LOGGING_SPEC.md
- docs/paper/ABLATION_PLAN_STAGE2.md
- git status

Tasks:
1. Review the required baseline candidates:
   - CLDNN or CNN-LSTM
   - MCLDNN
   - LWAMCNet or MCNet
   - parameter-matched I/Q-only baseline
2. Decide which two should be implemented first for maximum review value and
   lowest engineering risk.
3. Implement only the first selected baseline and the parameter-matched I/Q-only
   baseline if feasible.
4. Register the new model(s) in the model builder and required-view mapping.
5. Add focused unit tests for forward shape, parameter count, and
   model_required_views.
6. Run full unit tests with repository-local basetemp.
7. Run mock 1-epoch smoke test only for the new baseline(s).
8. Verify V2 artifacts are generated.
9. Write docs/paper/PAPER_STAGE4B_BASELINE_READINESS.md with:
   - baseline choice rationale;
   - implemented files;
   - tests and smoke results;
   - remaining baselines;
   - whether Stage 4C may start.

All results must be labeled PRELIMINARY or SMOKE TEST. Accuracy from mock or
tiny subset runs must not be used as research evidence.
```

