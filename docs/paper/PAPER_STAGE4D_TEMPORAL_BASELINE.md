# Paper-Stage 4D Temporal Baseline Report

Date: 2026-05-07

Stage: Paper-Stage 4D

Scope: complete the reviewer-standard raw I/Q temporal baseline entry point
without running RadioML2016.10A full training.

This report is engineering readiness evidence only. It is not paper performance
evidence.

## Guardrails

- No RadioML2016.10A full training was run.
- No RadioML2018.01A loading or training was run.
- Only unit tests, a mock 1-epoch smoke test, and a tiny RadioML2016.10A subset
  1-epoch smoke test were run.
- Mock and subset accuracy values are `PRELIMINARY` / `SMOKE TEST` only.
- No claim is made that fusion or gated fusion is better than any baseline.
- Existing dirty Stage 4A/4B/4C changes were not reverted.

## Context Read

The following files were read before implementation:

- `docs/paper/PAPER_STAGE4C_BASELINE_HARDENING.md`
- `docs/paper/PAPER_STAGE4B_BASELINE_READINESS.md`
- `docs/paper/BASELINE_MATRIX_STAGE2.md`
- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `docs/paper/ABLATION_PLAN_STAGE2.md`
- `git status --short --branch`

## Current Project Completion Update

Engineering entry points now available:

- Existing raw I/Q baselines: `cnn1d`, `resnet1d`.
- Existing time-frequency and fusion entries: `tfcnn_stft`,
  `fusion_iq_stft`, `gated_fusion_iq_stft`.
- Strong baseline additions from Stage 4B/4C: `mcldnn`,
  `iq_param_matched`, `lwamcnet`.
- New Stage 4D temporal entry: `cldnn`, with CNN-LSTM aliases.
- V2 artifact path for smoke runs: metrics JSON, per-SNR/class CSVs,
  predictions, confusion CSVs, complexity skeleton, latency placeholder, and
  training summary.

Still not full-paper evidence:

- No fixed-split full RadioML2016.10A rerun has been performed for this
  baseline set.
- No 3-seed main-table result exists for `cldnn`.
- FLOPs/MACs remain `null` in the current complexity skeleton.
- `latency.json` from training remains a placeholder; controlled latency still
  requires `scripts/paper/measure_complexity_latency.py` with V2 measurement
  settings.

## Why Stage 4D Was Still Needed

Stage 4C left the minimum main-table baseline matrix incomplete. The Stage 2
baseline matrix marks `CLDNN or CNN-LSTM` as P1 because reviewers commonly
expect a recurrent temporal AMC comparator beyond CNN and ResNet families.

MCLDNN reduces the temporal-baseline risk but does not fully replace this
entry:

- MCLDNN is a multi-channel I/Q, I-only, and Q-only architecture.
- A simpler single-stream raw I/Q CNN+LSTM/CLDNN baseline is a cleaner temporal
  control.
- The minimum main table lists CLDNN/CNN-LSTM separately from MCLDNN.
- The purpose here is reviewer-standard coverage and full-experiment risk
  reduction, not smoke accuracy optimization.

## CLDNN/CNN-LSTM Selection

Final choice: `cldnn`.

Rationale:

- CLDNN explicitly covers the CNN + LSTM + dense classifier family reviewers
  recognize as a temporal AMC baseline.
- It consumes only raw I/Q `[B, 2, L]`, matching the requested default priority.
- It complements MCLDNN by providing a single-stream temporal baseline rather
  than another multi-channel design.
- It is medium-cost and suitable for RadioML2016.10A preflight without adding
  STFT/CWT preprocessing confounds.

Registered aliases:

- `cldnn`
- `cldnn_iq`
- `cnn_lstm`
- `cnn_lstm_iq`
- `iq_cldnn`

Required views:

- `["iq"]`

Implemented architecture:

- input `[B, 2, L]`;
- three Conv1d feature blocks with channels `64 -> 128 -> 128`;
- two max-pooling reductions before the recurrent block;
- one 128-unit LSTM layer over the convolutional feature sequence;
- one 128-unit dense hidden layer with dropout;
- final linear classifier returning logits.

Parameter count:

| Model | Classes | Trainable parameters |
|---|---:|---:|
| `cldnn` | 4 | 240,772 |
| `cldnn` | 11 | 241,675 |

## Added or Modified Files

Modified:

- `src/radioml_amc/models/baselines.py`
  - added `CLDNN`.
- `src/radioml_amc/models/__init__.py`
  - exported `CLDNN`.
- `src/radioml_amc/training/trainer.py`
  - registered `cldnn` and CNN-LSTM aliases in `model_required_views`;
  - registered the same aliases in `build_model`.

Added:

- `tests/test_stage4d_temporal_baseline.py`
- `.pytest_tmp/stage4d_mock_config.yaml`
- `.pytest_tmp/stage4d_real_subset_config.yaml`
- `docs/paper/PAPER_STAGE4D_TEMPORAL_BASELINE.md`

## Unit Tests

Command:

```text
python -m pytest --basetemp .pytest_tmp\stage4d_suite
```

Result:

```text
33 passed, 1 skipped in 5.01s
```

New Stage 4D tests cover:

- `cldnn` forward shape;
- exact 4-class parameter count;
- mapping input support through `{"iq": tensor}`;
- `build_model` registration;
- `model_required_views` registration.

## Mock 1-Epoch Smoke Test

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4d_mock_config.yaml --models cldnn --output .pytest_tmp\stage4d_comparison
```

Run directory:

- `.pytest_tmp/stage4d_runs/20260507_234425_cldnn`

Result: passed.

Evidence tag: `PRELIMINARY`.

Accuracy printed by this smoke command is `SMOKE TEST` only and must not be
used as research evidence.

## Tiny Real Subset Smoke Test

Availability check:

- `data/raw/radioml2016/RML2016.10a_dict.pkl` exists.

Command:

```text
python scripts\run_stage2_ablations.py --config .pytest_tmp\stage4d_real_subset_config.yaml --models cldnn --output .pytest_tmp\stage4d_real_subset_comparison
```

Subset settings:

- modulations: `BPSK`, `QPSK`, `8PSK`, `QAM16`
- SNRs: `-6`, `0`, `6`, `12`
- max samples per modulation-SNR group: `10`
- total samples: `160`
- epochs: `1`
- device: CPU

Run directory:

- `.pytest_tmp/stage4d_real_subset_runs/20260507_234449_cldnn`

Result: passed.

Evidence tag: `PRELIMINARY`.

Accuracy printed by this subset command is `SMOKE TEST` only and must not be
used as research evidence.

## Smoke Artifact Check

Required files were present for both Stage 4D smoke run directories:

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

| Run | Required files complete | Evidence tag |
|---|---|---|
| mock `cldnn` | yes | `PRELIMINARY` |
| tiny real subset `cldnn` | yes | `PRELIMINARY` |

## Full Training Status

Full training was not run.

Specifically:

- no RadioML2016.10A full split training;
- no multi-seed full baseline training;
- no RadioML2018.01A loading or training;
- no performance comparison claim against fusion or gated fusion.

## Full Experiment Preflight Decision

Decision: allow entry into full experiment preflight, but not full experiment
execution yet.

Preflight may check:

- resolved configs for the full fixed split;
- model construction for all main-table entries;
- split artifact availability and checksum metadata;
- output directory naming;
- dry-run artifact schema expectations;
- controlled complexity/latency command readiness.

Full RadioML2016.10A training still requires a separate explicit promotion
decision because Stage 4D only validated engineering entry points.

## Next Stage Prompt Draft

```text
你现在扮演“AMC 自动调制识别 SCI 审稿人 + PyTorch 科研工程师 + 实验协议守门人”。

当前项目：
radioml-amc-stage1

当前分支：
paper-sci-track

当前阶段：
Paper-Stage 4E：full experiment preflight, no full training yet

请严格遵守：
1. 不要启动 RadioML2016.10A full training。
2. 不要启动 RadioML2018.01A。
3. 只允许运行单元测试、配置解析、模型构造、split/artifact schema dry-run、
   complexity/latency smoke measurement。
4. 不要写“fusion 全面优于 baseline”。
5. 不要覆盖已有 dirty changes。
6. mock/subset accuracy 只能标记为 PRELIMINARY 或 SMOKE TEST。

启动时请先读取：
1. docs/paper/PAPER_STAGE4D_TEMPORAL_BASELINE.md
2. docs/paper/PAPER_STAGE4C_BASELINE_HARDENING.md
3. docs/paper/EXPERIMENT_PROTOCOL_V2.md
4. docs/paper/METRICS_AND_LOGGING_SPEC.md
5. docs/paper/BASELINE_MATRIX_STAGE2.md
6. git status

请完成：
1. 汇总 main-table baseline entry points 是否全部可构造：
   cnn1d, resnet1d, tfcnn_stft, fusion_iq_stft, cldnn, mcldnn,
   lwamcnet, iq_param_matched, gated_fusion_iq_stft。
2. 检查固定 split artifact 是否存在；如缺失，只生成 split artifact，不训练模型。
3. 检查每个模型的 V2 artifact 输出 schema 和 required views。
4. 对各模型运行受控 complexity/latency smoke，使用很小 warmup/measured iters，
   仅验证命令链路。
5. 输出 docs/paper/PAPER_STAGE4E_FULL_PREFLIGHT.md，包含 go/no-go 结论：
   是否允许进入 full RadioML2016.10A 3-seed experiment。
```
