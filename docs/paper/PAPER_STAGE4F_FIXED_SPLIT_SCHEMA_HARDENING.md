# Paper-Stage 4F Fixed Split and V2 Schema Hardening

Date: 2026-05-07

Stage: Paper-Stage 4F

Scope: fix the Stage 4E protocol blocker by enforcing fixed split artifact
loading and harden V2 artifact schemas. No full training was started.

This report is protocol and engineering readiness evidence only. It is not
paper performance evidence.

## Guardrails

- No RadioML2016.10A full training was run.
- No RadioML2018.01A loading or training was run.
- Only unit tests, config parsing, a tiny mock 1-epoch smoke, fixed split
  artifact checks, and CPU complexity/latency smoke measurement were run.
- Mock and synthetic outputs are `PRELIMINARY` / `SMOKE TEST` only.
- No claim is made that fusion or gated fusion is better than any baseline.
- Existing dirty changes were not reverted.

## Context Read

Read before implementation:

- `docs/paper/PAPER_STAGE4E_FULL_PREFLIGHT.md`
- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `git status --short --branch`

Stage 4E blocker addressed:

- Previous behavior: `run_training()` generated splits with `seed=project.seed`.
- Risk: train seeds `42`, `2025`, and `3407` would create different test sets.
- Required behavior: split artifact seed stays fixed at `42`; train seed varies
  independently.

## Implementation Summary

Updated `src/radioml_amc/training/trainer.py`:

- added `resolve_experiment_splits()`;
- when `data.split_artifact_npz` is configured, the trainer loads the fixed
  artifact instead of regenerating splits;
- `data.split_summary_json` is loaded when present;
- `split_id` now comes from the fixed split summary, not from train seed;
- fallback split generation supports explicit `data.split_seed`;
- run and evaluation paths both use the same split resolver;
- run directories now save both `config.yaml` and `config_resolved.yaml`;
- `metrics.json` and `training_summary.json` include `split_id` and
  `train_seed`;
- training/evaluation latency placeholders now use V2 top-level latency keys.

Updated `src/radioml_amc/profiling/complexity.py`:

- `complexity.json` now includes the V2 `dataset` field;
- `measure_latency()` now emits V2 top-level keys:
  - `batch_sizes`
  - `gpu_forward_excluding_preprocess_ms`
  - `gpu_including_preprocess_ms`
  - `cpu_including_preprocess_ms`
  - `stft_preprocess_ms`
  - `peak_inference_memory_mb`
- legacy flat latency keys are preserved for compatibility with existing tests
  and scripts.

Updated `scripts/paper/measure_complexity_latency.py`:

- passes dataset metadata into `summarize_model_complexity()`.

Updated `configs/stage2_rml2016a_real_full.yaml`:

- added fixed split artifact paths:
  - `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
  - `data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json`

Added tests:

- `tests/test_stage4f_fixed_split_schema.py`

## Fixed Split Verification

New tests verify:

- a split artifact generated with split seed `42` is reused unchanged for train
  seeds `2025` and `3407`;
- `test_idx` is identical across train seeds when the artifact is configured;
- explicit `data.split_seed=42` also decouples split seed from train seed in the
  non-artifact fallback path;
- loaded split summaries retain `split_id=stratified_by_mod_snr_seed42`;
- run config output includes `config_resolved.yaml`.

Tiny mock 1-epoch smoke:

- dataset: synthetic mock only;
- model: `cnn1d`;
- epochs: `1`;
- device: CPU;
- split source: artifact;
- split id: `stratified_by_mod_snr_seed42`;
- output had no missing required V2 files.

The smoke accuracy is not reported here because it is not research evidence.

## V2 Schema Verification

Mock run artifact check passed for:

- `config_resolved.yaml`
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

Schema hardening result:

- `complexity.json`: V2 required top-level fields present.
- `latency.json`: V2 required top-level fields present.
- `predictions_test.csv`: V2 sample-level schema still produced.
- `metrics_per_snr.csv`: V2 per-SNR columns still produced.
- `metrics_per_class.csv`: V2 per-class columns still produced.

## Complexity and Latency Smoke

Settings:

- device: CPU
- batch size: `1`
- warmup iterations: `1`
- measured iterations: `2`
- signal length: `128`

All main-table smoke commands completed and emitted V2 required latency and
complexity top-level fields:

- `cnn1d`
- `resnet1d`
- `tfcnn_stft`
- `fusion_iq_stft`
- `cldnn`
- `mcldnn`
- `lwamcnet`
- `iq_param_matched`
- `gated_fusion_iq_stft`

These latency numbers are `SMOKE TEST` command-chain evidence only. Final tables
still require the V2 protocol settings: at least 50 warmup iterations, at least
200 measured iterations, batch sizes `1` and `256`, GPU/CPU measurements, and
preprocessing-inclusive measurements for STFT models.

## Test Results

Commands:

```text
python -m py_compile src/radioml_amc/training/trainer.py src/radioml_amc/profiling/complexity.py scripts/paper/measure_complexity_latency.py
python -m pytest tests/test_stage4f_fixed_split_schema.py --basetemp .pytest_tmp\stage4f_unit
python -m pytest --basetemp .pytest_tmp\stage4f_suite
```

Results:

```text
5 passed in tests/test_stage4f_fixed_split_schema.py
38 passed, 1 skipped in full test suite
```

## Full Training Status

Full training was not run.

Specifically:

- no full RadioML2016.10A training;
- no 3-seed main-table training;
- no RadioML2018.01A loading or training;
- no paper result comparison;
- no superiority claim for fusion or gated fusion.

## Go/No-Go Decision

Decision: **GO for server-side RadioML2016.10A full experiment execution
preparation**, with strict execution controls.

The Stage 4E blocker is fixed:

- fixed split artifact loading is implemented;
- train seed no longer has to determine test split;
- V2 schema gaps found in Stage 4E are addressed at the top-level artifact
  schema level;
- tests and smoke checks pass.

Execution controls still required:

- run only RadioML2016.10A, not RadioML2018.01A;
- use `configs/stage2_rml2016a_real_full.yaml` or the paper template with the
  fixed split artifact paths;
- verify each run's `split_summary.json` says `split_source=artifact` and
  `split_id=stratified_by_mod_snr_seed42`;
- verify all model-seed cells share identical `test_idx`;
- keep final latency measurement separate from smoke settings and use the V2
  final warmup/measured iteration counts;
- report any fusion/gated result as a trade-off if low-SNR improves while
  overall, mid-SNR, or high-SNR degrades.

## Server Execution Prompt Draft

```text
你现在扮演“AMC 自动调制识别 SCI 审稿人 + PyTorch 科研工程师 + 实验协议守门人”。

当前项目：
radioml-amc-stage1

当前分支：
paper-sci-track

当前阶段：
Paper-Stage 5A：服务器 RadioML2016.10A full 3-seed main-table execution。

严格遵守：
1. 只运行 RadioML2016.10A，不运行 RadioML2018.01A。
2. 使用固定 split artifact：
   data/splits/rml2016a/stratified_by_mod_snr_seed42.npz
   data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json
3. split_id 必须始终为 stratified_by_mod_snr_seed42。
4. train_seed 分别为 42、2025、3407。
5. 每个模型、每个 train_seed 的 test_idx 必须完全相同。
6. 不写“fusion 全面优于 baseline”。
7. 如 fusion/gated 只改善 low-SNR 但损失 overall/mid/high，必须写成 trade-off。

运行模型：
cnn1d, resnet1d, tfcnn_stft, fusion_iq_stft, cldnn, mcldnn,
lwamcnet, iq_param_matched, gated_fusion_iq_stft

每个 run 必须保留：
config_resolved.yaml, metrics_test.json, metrics_per_snr.csv,
metrics_per_class.csv, predictions_test.csv, confusion_overall.csv,
confusion_low_snr.csv, complexity.json, latency.json, training_summary.json。

训练完成后先做 artifact completeness 和 fixed split consistency audit，
再汇总 3-seed mean/std。不要把单 seed 或失败 cell 写入主表结论。
```
