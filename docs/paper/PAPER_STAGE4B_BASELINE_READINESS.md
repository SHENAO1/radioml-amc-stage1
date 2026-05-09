# Paper-Stage 4B Baseline Readiness Report

Date: 2026-05-07

Stage: Paper-Stage 4B

Scope: choose the first strong AMC baselines and validate their engineering
entry points before any full RadioML2016.10A training.

This report is engineering readiness evidence only. It is not paper
performance evidence.

## Guardrails

- No RadioML2016.10A full training was run.
- No RadioML2018.01A experiment was run.
- Only unit tests, mock 1-epoch smoke tests, tiny RadioML2016.10A subset
  1-epoch smoke tests, and synthetic complexity/latency smoke checks were run.
- All mock and subset accuracy values are `PRELIMINARY` / `SMOKE TEST` only.
- No claim is made that fusion or gated fusion is better than any baseline.
- Existing dirty Stage 4A changes were not reverted.

## Context Read

The following files were read before implementation:

- `docs/paper/PAPER_STAGE4A_READINESS_REPORT.md`
- `docs/paper/BASELINE_MATRIX_STAGE2.md`
- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `docs/paper/ABLATION_PLAN_STAGE2.md`
- `git status --short --branch`

External architecture anchor checked for MCLDNN:

- Official MCLDNN implementation: <https://github.com/wzjialang/MCLDNN>
- Paper record: <https://research-portal.uea.ac.uk/en/publications/a-spatiotemporal-multi-channel-learning-framework-for-automatic-m/>

## Baseline Priority Decision

| Candidate | Review risk if absent | Engineering cost | Stage 4B decision | Table placement |
|---|---|---|---|---|
| MCLDNN | Severe. A multi-channel CNN-LSTM baseline directly challenges any low-SNR multi-view claim. | Medium. It can consume raw I/Q and split I/Q internally. | Implement first. | Main table after full fixed-split multi-seed runs. |
| Parameter-matched I/Q-only baseline | Severe. Without it, fusion gains may be a parameter-count artifact. | Low to medium. It is an I/Q-only CNN sized to the gated-fusion parameter budget. | Implement now. | Main table after full fixed-split multi-seed runs. |
| CLDNN or CNN-LSTM | High. Reviewers expect a recurrent temporal baseline. | Low to medium. | Defer behind MCLDNN because MCLDNN already covers CNN+LSTM with stronger multi-channel structure. | Appendix unless MCLDNN is unstable or too costly. |
| LWAMCNet or MCNet | High for a lightweight claim, but less directly tied to the current fusion-vs-I/Q confound. | Medium because architecture fidelity needs citation-level audit. | Temporarily defer, preferably implement LWAMCNet next if the paper keeps a lightweight framing. | Main if implemented faithfully; MCNet can be appendix/future if LWAMCNet is present. |

Selected first two baselines:

1. `mcldnn`
2. `iq_param_matched`

## Implementation Summary

Added:

- `src/radioml_amc/models/baselines.py`
  - `MCLDNN`
  - `ParameterMatchedIQOnlyNet`
  - `count_parameters`
- `tests/test_stage4b_baselines.py`

Modified:

- `src/radioml_amc/models/__init__.py`
  - exports new baseline classes.
- `src/radioml_amc/training/trainer.py`
  - registers `mcldnn`, `mcldnn_iq`, `iq_param_matched`,
    `parameter_matched_iq`, and `param_matched_iq` in `model_required_views`.
  - registers the new model ids in `build_model`.

Temporary smoke configs and outputs:

- `.pytest_tmp/stage4b_mock_config.yaml`
- `.pytest_tmp/stage4b_real_subset_config.yaml`
- `.pytest_tmp/stage4b_runs/`
- `.pytest_tmp/stage4b_real_subset_runs/`
- `.pytest_tmp/stage4b_comparison/`
- `.pytest_tmp/stage4b_real_subset_comparison/`
- `.pytest_tmp/stage4b_latency/`

## Model Entry Points

| Model id | Required views | Forward input | Forward output | Parameters, 4 classes | Parameters, 11 classes |
|---|---|---|---|---:|---:|
| `mcldnn` | `["iq"]` | `[B, 2, 128]` | `[B, C]` logits | 405,296 | 406,199 |
| `iq_param_matched` | `["iq"]` | `[B, 2, 128]` | `[B, C]` logits | 135,492 | 136,395 |
| `gated_fusion_iq_stft` reference | `["iq", "stft"]` | I/Q + STFT dict | `[B, C]` logits | 133,877 | 134,780 |

Parameter control note:

- `iq_param_matched` is I/Q-only and has about `1.012x` the scalar gated
  I/Q+STFT parameter count for both 4-class smoke and 11-class full-class
  construction. It is intended to isolate parameter-budget effects, not to
  compare performance at this stage.

## Unit Tests

Command:

```text
python -m pytest --basetemp .pytest_tmp\stage4b_suite
```

Result:

```text
27 passed, 1 skipped in 5.22s
```

New tests cover:

- `mcldnn` forward shape;
- `iq_param_matched` forward shape;
- exact parameter-count checks for the 4-class smoke construction;
- parameter-budget ratio versus scalar gated fusion;
- `build_model` registration;
- `model_required_views` registration.

## Mock 1-Epoch Smoke Test

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4b_mock_config.yaml --models mcldnn iq_param_matched --output .pytest_tmp\stage4b_comparison
```

Run directories:

- `.pytest_tmp/stage4b_runs/20260507_230424_mcldnn`
- `.pytest_tmp/stage4b_runs/20260507_230428_iq_param_matched`

Result: passed.

Evidence tag: `PRELIMINARY`.

Accuracy values from this run are `SMOKE TEST` only and must not be used as
research evidence.

## Tiny Real Subset Smoke Test

Availability check:

- `data/raw/radioml2016/RML2016.10a_dict.pkl` exists.

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4b_real_subset_config.yaml --models mcldnn iq_param_matched --output .pytest_tmp\stage4b_real_subset_comparison
```

Subset settings:

- modulations: `BPSK`, `QPSK`, `8PSK`, `QAM16`
- SNRs: `-6`, `0`, `6`, `12`
- max samples per modulation-SNR group: `10`
- total samples: `160`
- epochs: `1`
- device: CPU

Run directories:

- `.pytest_tmp/stage4b_real_subset_runs/20260507_230452_mcldnn`
- `.pytest_tmp/stage4b_real_subset_runs/20260507_230459_iq_param_matched`

Result: passed.

Evidence tag: `PRELIMINARY`.

Accuracy values from this run are `SMOKE TEST` only and must not be used as
research evidence.

## Smoke Artifact Check

Required files were present for all four Stage 4B smoke run directories:

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

Artifact check result:

| Run | Required files complete |
|---|---|
| mock `mcldnn` | yes |
| mock `iq_param_matched` | yes |
| tiny real subset `mcldnn` | yes |
| tiny real subset `iq_param_matched` | yes |

## Complexity and Latency Smoke Checks

Commands:

```text
python scripts\paper\measure_complexity_latency.py --config .pytest_tmp\stage4b_mock_config.yaml --model mcldnn --output .pytest_tmp\stage4b_latency\mcldnn.json --device cpu --warmup-iters 1 --measured-iters 2
python scripts\paper\measure_complexity_latency.py --config .pytest_tmp\stage4b_mock_config.yaml --model iq_param_matched --output .pytest_tmp\stage4b_latency\iq_param_matched.json --device cpu --warmup-iters 1 --measured-iters 2
```

Result files:

- `.pytest_tmp/stage4b_latency/mcldnn.json`
- `.pytest_tmp/stage4b_latency/iq_param_matched.json`

Result: passed.

Limitations:

- These are synthetic CPU smoke measurements with `warmup_iters=1` and
  `measured_iters=2`.
- MACs/FLOPs remain `null`, consistent with Stage 4A's documented limitation.
- Final paper latency must use the V2 protocol warmup/measured iteration counts.

## Full Training Status

Full training was not run.

Specifically:

- no RadioML2016.10A full split training;
- no multi-seed full baseline training;
- no RadioML2018.01A training or loading;
- no performance comparison claim against fusion or gated fusion.

## Stage 4C Decision

Decision: allow entry into Stage 4C for baseline hardening and the next baseline
implementation.

Boundary:

- Stage 4C should still avoid full RadioML2016.10A training unless explicitly
  promoted by a separate protocol decision.
- Before paper main-table experiments, audit the MCLDNN implementation against
  the cited paper/code at architecture and hyperparameter level.
- Implement LWAMCNet next if the paper retains a lightweight claim; otherwise
  add a simpler CLDNN/CNN-LSTM appendix baseline first.

## Stage 4C Prompt Draft

```text
You are acting as an AMC SCI reviewer, PyTorch research engineer, and
experiment protocol gatekeeper.

Current project:
radioml-amc-stage1

Current branch:
paper-sci-track

Current stage:
Paper-Stage 4C: baseline hardening and second strong baseline implementation.

Strict rules:
1. Do not run RadioML2016.10A full training unless explicitly promoted in this
   prompt after reading Stage 4B evidence.
2. Do not run RadioML2018.01A.
3. Use only unit tests, mock smoke tests, and tiny real-subset 1-epoch smoke
   tests.
4. Do not claim fusion or gated fusion is better.
5. Do not overwrite existing dirty changes.
6. Treat all mock/subset accuracy as PRELIMINARY / SMOKE TEST only.

Start by reading:
- docs/paper/PAPER_STAGE4B_BASELINE_READINESS.md
- docs/paper/PAPER_STAGE4A_READINESS_REPORT.md
- docs/paper/BASELINE_MATRIX_STAGE2.md
- docs/paper/EXPERIMENT_PROTOCOL_V2.md
- docs/paper/METRICS_AND_LOGGING_SPEC.md
- docs/paper/ABLATION_PLAN_STAGE2.md
- git status

Tasks:
1. Audit the new MCLDNN implementation against the cited MCLDNN paper/code and
   document any architecture deviations before full experiments.
2. Decide whether Stage 4C should implement LWAMCNet or CLDNN/CNN-LSTM next.
   Prefer LWAMCNet if the paper keeps a lightweight-efficiency claim; prefer
   CLDNN/CNN-LSTM if reviewer-standard temporal coverage is the immediate goal.
3. Implement the chosen second baseline with build_model and
   model_required_views registration.
4. Add forward shape, parameter count, build_model, and required-view tests.
5. Run:
   - python -m pytest --basetemp .pytest_tmp\stage4c_suite
   - mock 1-epoch smoke test for the new baseline
   - tiny real subset 1-epoch smoke test if RadioML2016.10A is available
6. Verify V2 artifacts:
   - metrics.json
   - metrics_test.json
   - metrics_per_snr.csv
   - metrics_per_class.csv
   - predictions_test.csv
   - confusion_overall.csv
   - confusion_low_snr.csv
   - complexity.json
   - latency.json
   - training_summary.json
7. Write docs/paper/PAPER_STAGE4C_BASELINE_HARDENING.md with:
   - baseline choice rationale;
   - implementation/audit notes;
   - changed files;
   - test and smoke results;
   - artifact check;
   - explicit no-full-training statement;
   - next go/no-go decision.
```

