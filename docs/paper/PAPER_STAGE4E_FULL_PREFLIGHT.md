# Paper-Stage 4E Full Experiment Preflight

Date: 2026-05-07

Stage: Paper-Stage 4E

Scope: full RadioML2016.10A main-table preflight only. No full training was
started.

This report is protocol and engineering readiness evidence. It is not model
performance evidence.

## Guardrails

- No RadioML2016.10A full training was run.
- No RadioML2018.01A loading or training was run.
- Only unit tests, config parsing, model construction, split artifact creation,
  artifact schema dry-run, and complexity/latency smoke measurement were run.
- Mock/subset/synthetic outputs are `PRELIMINARY` / `SMOKE TEST` only.
- No claim is made that fusion or gated fusion is broadly better than any
  baseline.
- Existing dirty changes were not reverted or overwritten.

## Context Read

Read before preflight work:

- `docs/paper/PAPER_STAGE4D_TEMPORAL_BASELINE.md`
- `docs/paper/PAPER_STAGE4C_BASELINE_HARDENING.md`
- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `docs/paper/BASELINE_MATRIX_STAGE2.md`
- `docs/paper/ABLATION_PLAN_STAGE2.md`
- `git status --short --branch`

Initial branch/status:

- branch: `paper-sci-track`
- existing dirty files were present before Stage 4E; they were preserved.

## Checks Run

Commands:

```text
python scripts/paper/create_split_artifact.py --config configs/stage2_rml2016a_real_full.yaml --output-dir data/splits/rml2016a --dataset rml2016a --strategy stratified_by_mod_snr --seed 42 --test-size 0.2 --val-size 0.1
python -m pytest --basetemp .pytest_tmp\stage4e_suite
python scripts/paper/measure_complexity_latency.py --config configs/stage2_rml2016a_real_full.yaml --model <model_id> --output .pytest_tmp/stage4e_latency_smoke/<model_id>.json --device cpu --batch-size 1 --signal-length 128 --num-classes 11 --warmup-iters 1 --measured-iters 2
```

Unit test result:

```text
33 passed, 1 skipped
```

## Main-Table Readiness

Entry-point status: all requested main-table model ids are registered,
constructible, and produce logits with shape `[2, 11]` on synthetic inputs.

| Model | Required views | Constructible | Synthetic forward | Trainable params |
|---|---|---:|---:|---:|
| `cnn1d` | `iq` | yes | yes | 37,131 |
| `resnet1d` | `iq` | yes | yes | 111,755 |
| `tfcnn_stft` | `stft` | yes | yes | 24,123 |
| `fusion_iq_stft` | `iq+stft` | yes | yes | 98,299 |
| `cldnn` | `iq` | yes | yes | 241,675 |
| `mcldnn` | `iq` | yes | yes | 406,199 |
| `lwamcnet` | `iq` | yes | yes | 20,395 |
| `iq_param_matched` | `iq` | yes | yes | 136,395 |
| `gated_fusion_iq_stft` | `iq+stft` | yes | yes | 134,780 |

Required-view check:

- Raw I/Q models correctly require `["iq"]`.
- STFT-only baseline correctly requires `["stft"]`.
- Static and gated I/Q+STFT fusion entries correctly require `["iq", "stft"]`.

## Fixed Split Artifact Status

The required fixed split artifacts were missing at startup and were generated
without training:

```text
data/splits/rml2016a/stratified_by_mod_snr_seed42.npz
data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json
```

NPZ arrays:

| Array | Shape | Dtype |
|---|---:|---|
| `train_idx` | 154,000 | `int64` |
| `val_idx` | 22,000 | `int64` |
| `test_idx` | 44,000 | `int64` |

Summary status:

- dataset: `rml2016a`
- split id: `stratified_by_mod_snr_seed42`
- split strategy: `stratified_by_mod_snr`
- split seed: `42`
- total samples: `220000`
- class mapping and SNR list: present
- per-split modulation, SNR, and modulation-SNR counts: present
- source path metadata: present
- source checksum: not computed; recommended before archival if checksum tooling
  is added.

## V2 Artifact Schema Check

Synthetic schema dry-run output:

```text
.pytest_tmp/stage4e_schema/<model_id>/
```

For every requested model, the dry-run produced the Stage 4E requested file set:

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

CSV column checks:

- `predictions_test.csv`: required metadata columns plus `logit_*` and `prob_*`
  class columns are present.
- `metrics_per_snr.csv`: `dataset`, `model_id`, `split_id`, `train_seed`,
  `snr_db`, `num_samples`, `accuracy`, `macro_f1`, and `balanced_accuracy` are
  present.
- `metrics_per_class.csv`: `dataset`, `model_id`, `split_id`, `train_seed`,
  `class_id`, `modulation`, `num_samples`, and `accuracy` are present.

Schema gaps to fix before final paper artifacts:

- `complexity.json` currently lacks the V2 `dataset` field.
- Training-loop `latency.json` is a placeholder, not the final nested latency
  schema from `METRICS_AND_LOGGING_SPEC.md`.
- `scripts/paper/measure_complexity_latency.py` produces useful smoke JSON, but
  its latency keys do not yet exactly match the final V2 names
  (`batch_sizes`, `gpu_forward_excluding_preprocess_ms`,
  `gpu_including_preprocess_ms`, `cpu_including_preprocess_ms`,
  `stft_preprocess_ms`).
- `EXPERIMENT_PROTOCOL_V2.md` also requires `config_resolved.yaml`; the current
  training path saves `config.yaml`. The final full-run harness should write
  `config_resolved.yaml` or an equivalent resolved config artifact.

## Complexity and Latency Smoke Check

Settings:

- device: CPU
- batch size: `1`
- warmup iterations: `1`
- measured iterations: `2`
- input length: `128`

Output:

```text
.pytest_tmp/stage4e_latency_smoke/<model_id>.json
```

All nine smoke commands completed successfully. These numbers are command-chain
checks only and must not be used in the final complexity/latency table.

| Model | Params | CPU forward mean ms | Evidence tag |
|---|---:|---:|---|
| `cnn1d` | 37,131 | 1.0067 | `SMOKE TEST` |
| `resnet1d` | 111,755 | 9.3035 | `SMOKE TEST` |
| `tfcnn_stft` | 24,123 | 1.8120 | `SMOKE TEST` |
| `fusion_iq_stft` | 98,299 | 1.0581 | `SMOKE TEST` |
| `cldnn` | 241,675 | 1.1067 | `SMOKE TEST` |
| `mcldnn` | 406,199 | 2.7654 | `SMOKE TEST` |
| `lwamcnet` | 20,395 | 8.4237 | `SMOKE TEST` |
| `iq_param_matched` | 136,395 | 1.8701 | `SMOKE TEST` |
| `gated_fusion_iq_stft` | 134,780 | 15.0629 | `SMOKE TEST` |

Final reporting must rerun controlled measurement with at least 50 warmup
iterations and 200 measured iterations, batch sizes `1` and `256`, GPU forward
latency excluding preprocessing, full latency including preprocessing, CPU
latency including preprocessing, and peak inference memory.

## Full Experiment Template and Runbook

No complete non-executing main-table full experiment template existed in
`configs/paper/` at startup. Added:

- `configs/paper/rml2016a_main_table_full_template.yaml`
- `docs/paper/SERVER_RML2016A_FULL_EXPERIMENT_RUNBOOK.md`

Template parse check passed:

- `execution.auto_run`: `false`
- models: 9
- train seeds: `42`, `2025`, `3407`

The runbook explicitly blocks server execution until fixed split artifact
loading is confirmed in the trainer.

## Protocol Blocker Found

The project can create and load split artifacts in `src/radioml_amc/data/split.py`,
but the current `run_training()` path still calls `make_splits(..., seed=seed)`.
Because `seed` is also the training seed, a naive 3-seed full experiment would
use different test splits for seeds `42`, `2025`, and `3407`.

This violates `EXPERIMENT_PROTOCOL_V2.md`, which requires:

- split seed fixed at `42`;
- identical test set for all compared models and train seeds;
- training-seed variation isolated from test-set variation.

## Full Training Status

Full training was not run.

Specifically:

- no full RadioML2016.10A baseline or fusion training;
- no 3-seed training;
- no RadioML2018.01A run;
- no paper-performance comparison;
- no superiority claim.

## Go/No-Go Decision

Decision: **NO-GO for immediate server full RadioML2016.10A 3-seed training
as-is**.

Reason:

- model entry points are ready;
- fixed split artifact now exists;
- V2 file-level artifact path is mostly ready;
- complexity/latency smoke command chain works;
- but the current training path does not yet prove that all train seeds will use
  the same fixed split artifact;
- final complexity/latency JSON schema still needs field-name alignment.

Allowed next step:

- enter a short Stage 4F implementation/preflight patch to make the trainer load
  `data.split_artifact_npz`, keep `split_seed=42` independent from
  `train_seed`, write `config_resolved.yaml`, and align final
  `complexity.json` / `latency.json` fields.

Not allowed yet:

- launching the server full RadioML2016.10A 9-model x 3-seed experiment.

## Server Training Prompt Draft

Use this only after the Stage 4E blockers are fixed and a new preflight confirms
fixed split loading.

```text
你现在扮演“AMC 自动调制识别 SCI 审稿人 + PyTorch 科研工程师 + 实验协议守门人”。

当前项目：
radioml-amc-stage1

当前分支：
paper-sci-track

当前阶段：
Paper-Stage 5A：服务器 RadioML2016.10A full 3-seed main-table run。

前置条件：
1. 已确认 trainer 加载 data/splits/rml2016a/stratified_by_mod_snr_seed42.npz。
2. split_seed 固定为 42，train_seed 分别为 42、2025、3407。
3. 所有模型和所有 train_seed 使用完全相同 test_idx。
4. complexity.json、latency.json、config_resolved.yaml 已符合 V2 schema。
5. 不运行 RadioML2018.01A。

请执行服务器 full experiment：
- dataset: RadioML2016.10A
- split artifact: data/splits/rml2016a/stratified_by_mod_snr_seed42.npz
- train seeds: 42, 2025, 3407
- models:
  cnn1d, resnet1d, tfcnn_stft, fusion_iq_stft, cldnn, mcldnn,
  lwamcnet, iq_param_matched, gated_fusion_iq_stft
- output root:
  results/paper_stage2/rml2016a/<model_id>/seed_<train_seed>/

每个 run 必须输出：
- config_resolved.yaml
- metrics_test.json
- metrics_per_snr.csv
- metrics_per_class.csv
- predictions_test.csv
- confusion_overall.csv
- confusion_low_snr.csv
- complexity.json
- latency.json
- training_summary.json

训练完成后只汇总 mean/std 和 artifact completeness。
不要写“fusion 全面优于 baseline”。
如果 gated 或 fusion 只在 low-SNR 有收益而 overall/mid/high 下降，必须写成 trade-off。
```
