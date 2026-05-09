# Paper-Stage 4C Baseline Hardening Report

Date: 2026-05-07

Stage: Paper-Stage 4C

Scope: audit the current MCLDNN engineering entry point and add the next strong
reviewer-facing baseline without running RadioML2016.10A full training.

This report is engineering readiness evidence only. It is not paper performance
evidence.

## Guardrails

- No RadioML2016.10A full training was run.
- No RadioML2018.01A experiment was run.
- Only unit tests, a mock 1-epoch smoke test, and a tiny RadioML2016.10A subset
  1-epoch smoke test were run.
- Mock and subset outputs are `PRELIMINARY` / `SMOKE TEST` only.
- No claim is made that fusion or gated fusion is better than any baseline.
- Existing dirty Stage 4A/4B changes were not reverted.

## Context Read

The following files were read before implementation:

- `docs/paper/PAPER_STAGE4B_BASELINE_READINESS.md`
- `docs/paper/PAPER_STAGE4A_READINESS_REPORT.md`
- `docs/paper/BASELINE_MATRIX_STAGE2.md`
- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `docs/paper/ABLATION_PLAN_STAGE2.md`
- `git status --short --branch`

External architecture anchors checked:

- Official MCLDNN repository: <https://github.com/wzjialang/MCLDNN>
- Official MCLDNN code: <https://raw.githubusercontent.com/wzjialang/MCLDNN/master/MCLDNN.py>
- MCLDNN paper DOI: <https://doi.org/10.1109/LWC.2020.2999453>
- LWAMCNet paper DOI: <https://doi.org/10.3390/electronics10212679>

## Current Project Completion Assessment

Ready as engineering entry points:

- V2 metric artifacts, sample-level predictions, per-SNR/class metrics, confusion
  CSVs, complexity JSON skeleton, and latency JSON skeleton.
- Existing I/Q baselines: `cnn1d`, `resnet1d`.
- Existing time-frequency and fusion entries: `tfcnn_stft`, `fusion_iq_stft`,
  `gated_fusion_iq_stft`.
- Stage 4B baselines: `mcldnn`, `iq_param_matched`.
- Stage 4C lightweight baseline: `lwamcnet`.

Not yet full-paper ready:

- No full fixed-split RadioML2016.10A V2 reruns.
- No 3-seed main-table results.
- No CLDNN/CNN-LSTM baseline yet.
- FLOPs/MACs are still `null` in the current complexity skeleton.
- Training-loop `latency.json` remains a placeholder; final tables still need
  controlled latency runs with V2 warmup/measured iteration counts.

## MCLDNN Fidelity Audit

Official structure:

- Three inputs: combined I/Q, I-only, and Q-only streams.
- Combined I/Q branch: `Conv2D(50, (2, 8), padding="same", relu)`.
- I and Q branches: separate `Conv1D(50, 8, padding="causal", relu)`.
- Independent I/Q features are concatenated, processed by
  `Conv2D(50, (1, 8), padding="same", relu)`, then concatenated with the joint
  I/Q branch.
- Fused tensor uses `Conv2D(100, (2, 5), padding="valid", relu)`.
- Temporal section reshapes to `(124, 100)`, then uses two 128-unit CuDNNLSTM
  layers.
- Classifier uses two 128-unit SELU dense layers with dropout 0.5, then softmax.

Current PyTorch consistency points:

- Accepts raw `[B, 2, 128]` I/Q and internally derives the joint I/Q, I-only,
  and Q-only streams.
- Preserves the official convolution channel counts and kernel sizes:
  `(2, 8)`, `8`, `(1, 8)`, and `(2, 5)`.
- Preserves causal 1D padding for the I and Q branches.
- Preserves the temporal shape contract: length 128 becomes 124 steps after the
  valid `(2, 5)` convolution.
- Preserves two 128-unit LSTM layers and two SELU FC layers with FC dropout 0.5.
- Produces logits for `CrossEntropyLoss`, which is the correct PyTorch training
  interface even though the original Keras model ends with softmax.

Engineering simplifications or deviations:

- This is a PyTorch reimplementation, not a weight-compatible Keras port.
- The training protocol follows project V2, not the official repository's
  original random split seed, batch size 400, Adam schedule, callbacks, or early
  stopping settings.
- PyTorch default initializers are used; the official Keras code specifies
  `glorot_uniform` on convolutional and dense layers.
- CuDNNLSTM kernel-level behavior is not exactly reproduced by `nn.LSTM`.
- The final layer returns logits instead of softmax probabilities.

Hardening performed in Stage 4C:

- The MCLDNN PyTorch LSTM block was changed from `dropout=0.5` inside
  `nn.LSTM(num_layers=2)` to `dropout=0.0`, because the official code does not
  apply dropout between the two CuDNNLSTM layers. FC dropout remains 0.5.

Judgment:

- The current `mcldnn` is sufficient as a Stage 2 main-table engineering entry
  point if it is described as a PyTorch MCLDNN-style reimplementation trained
  under the same V2 protocol as all local baselines.
- It is not sufficient to claim exact reproduction of the original MCLDNN paper
  numbers without a separate Keras/official-code reproduction or a tighter
  initializer/training-protocol compatibility study.

## Stage 4C Baseline Choice

Candidate comparison:

| Candidate | Review value now | Risk if delayed | Stage 4C decision |
|---|---|---|---|
| LWAMCNet | Directly addresses the lightweight/deployment-aware framing and gives a low-parameter raw I/Q comparator. | High if the paper continues to use lightweight or deployment language. | Implement now. |
| CLDNN/CNN-LSTM | Adds reviewer-standard temporal coverage. | Still meaningful, but MCLDNN already covers a stronger CNN+LSTM multi-channel family. | Defer to Stage 4D. |

Final choice: `lwamcnet`.

Rationale:

- The paper track still emphasizes lightweight and deployment-aware comparison.
- Stage 4B already added MCLDNN, reducing the immediate temporal-baseline gap.
- LWAMCNet gives a strong complexity-control anchor against any future
  lightweight fusion claim.

## LWAMCNet Implementation Notes

Added model id aliases:

- `lwamcnet`
- `lwamcnet_iq`
- `lw_amc_net`
- `lightweight_amc`

Required views:

- `["iq"]`

Implemented 2016.10A-scale architecture:

- input `[B, 2, 128]`;
- first `2 x 5` convolution with 64 channels;
- three DSC residual stacks;
- each stack uses linear `1 x 1` channel fusion, two DSC residual units, and
  `1 x 2` max pooling;
- global depthwise convolution over the final length-16 feature map;
- one linear classifier returning logits.

Parameter count:

| Model | Classes | Trainable parameters |
|---|---:|---:|
| `lwamcnet` | 4 | 20,164 |
| `lwamcnet` | 11 | 20,395 |

Fidelity boundary:

- The implementation follows the paper's RadioML2016.10A description: three DSC
  residual stacks and no final post-stack `1 x 1` feature-dimension raise.
- It is an engineering baseline entry point, not an exact reproduction claim.

## Added or Modified Files

Modified:

- `src/radioml_amc/models/baselines.py`
  - added `LWAMCNet` and DSC/GDWConv helper modules;
  - hardened MCLDNN LSTM dropout fidelity.
- `src/radioml_amc/models/__init__.py`
  - exported `LWAMCNet`.
- `src/radioml_amc/training/trainer.py`
  - registered `lwamcnet` aliases in `model_required_views`;
  - registered `lwamcnet` aliases in `build_model`.

Added:

- `tests/test_stage4c_lwamcnet.py`
- `.pytest_tmp/stage4c_mock_config.yaml`
- `.pytest_tmp/stage4c_real_subset_config.yaml`
- `docs/paper/PAPER_STAGE4C_BASELINE_HARDENING.md`

## Unit Tests

Command:

```text
python -m pytest --basetemp .pytest_tmp\stage4c_suite
```

Final result after the MCLDNN hardening edit:

```text
30 passed, 1 skipped in 10.23s
```

New Stage 4C tests cover:

- `lwamcnet` forward shape;
- exact `lwamcnet` 4-class parameter count;
- rejection of unsupported signal length;
- `build_model` registration;
- `model_required_views` registration.

## Mock 1-Epoch Smoke Test

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4c_mock_config.yaml --models lwamcnet --output .pytest_tmp\stage4c_comparison
```

Run directory:

- `.pytest_tmp/stage4c_runs/20260507_232136_lwamcnet`

Result: passed.

Evidence tag: `PRELIMINARY`.

Accuracy printed by this smoke command is `SMOKE TEST` only and must not be
used as research evidence.

## Tiny Real Subset Smoke Test

Availability check:

- `data/raw/radioml2016/RML2016.10a_dict.pkl` exists.

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4c_real_subset_config.yaml --models lwamcnet --output .pytest_tmp\stage4c_real_subset_comparison
```

Subset settings:

- modulations: `BPSK`, `QPSK`, `8PSK`, `QAM16`
- SNRs: `-6`, `0`, `6`, `12`
- max samples per modulation-SNR group: `10`
- total samples: `160`
- epochs: `1`
- device: CPU

Run directory:

- `.pytest_tmp/stage4c_real_subset_runs/20260507_232201_lwamcnet`

Result: passed.

Evidence tag: `PRELIMINARY`.

Accuracy printed by this subset command is `SMOKE TEST` only and must not be
used as research evidence.

## Smoke Artifact Check

Required files were present for both Stage 4C smoke run directories:

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
| mock `lwamcnet` | yes |
| tiny real subset `lwamcnet` | yes |

## Full Training Status

Full training was not run.

Specifically:

- no RadioML2016.10A full split training;
- no multi-seed full baseline training;
- no RadioML2018.01A loading or training;
- no performance comparison claim against fusion or gated fusion.

## Stage 4D Go/No-Go

Decision: allow entry into Stage 4D, but keep the same no-full-training
boundary unless a separate explicit protocol decision promotes full runs.

Recommended Stage 4D focus:

1. Add the remaining reviewer-standard CLDNN/CNN-LSTM baseline.
2. Add focused tests and mock/tiny-subset smoke evidence.
3. Re-check full main-table readiness after CLDNN/CNN-LSTM, MCLDNN,
   LWAMCNet, and parameter-matched I/Q all exist in the same V2 artifact path.

## Stage 4D Prompt Draft

```text
You are acting as an AMC SCI reviewer, PyTorch research engineer, and
experiment protocol gatekeeper.

Current project:
radioml-amc-stage1

Current branch:
paper-sci-track

Current stage:
Paper-Stage 4D: reviewer-standard temporal baseline completion.

Strict rules:
1. Do not run RadioML2016.10A full training.
2. Do not run RadioML2018.01A.
3. Use only unit tests, mock 1-epoch smoke tests, and tiny real-subset
   1-epoch smoke tests.
4. Do not claim fusion or gated fusion is better than any baseline.
5. Do not overwrite existing dirty changes.
6. Treat all mock/subset accuracy as PRELIMINARY / SMOKE TEST only.

Start by reading:
- docs/paper/PAPER_STAGE4C_BASELINE_HARDENING.md
- docs/paper/PAPER_STAGE4B_BASELINE_READINESS.md
- docs/paper/BASELINE_MATRIX_STAGE2.md
- docs/paper/EXPERIMENT_PROTOCOL_V2.md
- docs/paper/METRICS_AND_LOGGING_SPEC.md
- docs/paper/ABLATION_PLAN_STAGE2.md
- git status

Tasks:
1. Implement a reviewer-standard CLDNN or CNN-LSTM raw I/Q baseline.
2. Register it in build_model and model_required_views.
3. Add forward shape, parameter count, build_model, and required-view tests.
4. Run:
   - python -m pytest --basetemp .pytest_tmp\stage4d_suite
   - mock 1-epoch smoke test for the new baseline
   - tiny real subset 1-epoch smoke test if RadioML2016.10A is available
5. Verify V2 artifacts:
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
6. Write docs/paper/PAPER_STAGE4D_TEMPORAL_BASELINE.md with:
   - CLDNN/CNN-LSTM architecture rationale;
   - changed files;
   - tests and smoke results;
   - artifact check;
   - explicit no-full-training statement;
   - go/no-go decision for pre-full experiment readiness.
```
