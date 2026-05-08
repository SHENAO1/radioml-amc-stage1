# Paper-Stage 6B Screening Protocol and Candidate Queue

Date: 2026-05-08

Project: `radioml-amc-stage1`

Server target path: `/hy-tmp/radioml-amc-stage1`

Scope: post-Stage6A controlled mock/subset/smoke screening preparation and evidence-bounded candidate queue.

This is a protocol and engineering planning artifact. It is not paper prose and it is not full-training evidence.

## Hard Guardrails

- RadioML2018.01A must not be run.
- No new full training is authorized by this document.
- Stage 5A and Stage 5B artifacts must not be overwritten, deleted, renamed, or selectively cleaned.
- Stage 6B mock, subset, smoke, and diagnostic outputs must not be merged into Stage 5A or Stage 5B tables.
- MCLDNN seed `2025` and seed `3407` chance-level Stage 5A results remain retained as protocol evidence.
- Any executed Stage 6B output must be labelled `DIAGNOSTIC` or `SMOKE TEST`.
- Permitted execution is limited to unit tests, model forward checks, one-batch overfit checks, mock smoke, or explicitly approved tiny subset screening.

## Startup Evidence Read Status

Readable evidence:

- `docs/paper/PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`
- `docs/paper/PAPER_STAGE5A_FULL_RML2016A_TRAINING_REPORT.md`
- `docs/paper/PAPER_STAGE5B_RESULT_AUDIT_AND_TABLES.md`
- `results/paper_stage2/rml2016a/stage5a_status.json`
- `results/paper_stage2/rml2016a/aggregate/main_table_metrics.csv`
- `results/paper_stage2/rml2016a/aggregate/main_table_metrics.md`
- `results/paper_stage2/rml2016a/aggregate/low_snr_table.csv`
- `results/paper_stage2/rml2016a/aggregate/complexity_latency_table.csv`
- `results/paper_stage6/diagnostic/stage6b/fusion_iq_amp_phase_static/20260508_093001_fusion_iq_amp_phase/`

Missing evidence:

- `docs/session_state.md`
- `docs/progress.md`
- `results/latest/`

Evidence status correction:

- Stage 5B audit and aggregate CSV/Markdown files are present and readable.
- Stage 6A plan is present and readable after the consistency repair that created `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md`.
- `results/latest/` remains missing and is not used as evidence.

Initial dirty-file status before this Stage 6B edit already showed existing modified and untracked files, including `README.md`, `docs/`, `configs/`, `src/radioml_amc/`, `results/`, and tests. Those files are treated as existing user/project work and are not reverted.

## Evidence Label Policy

| Label | Meaning | Stage 6B use |
|---|---|---|
| `PROJECT_SUPPORTED` | Full Stage 5A/5B RadioML2016.10A evidence. | Reference only; Stage 6B must not alter it. |
| `CONTROLLED_LATENCY` | Controlled Stage 5B CUDA latency evidence. | Reference only for complexity expectations. |
| `SMOKE TEST` | Mock/synthetic code-path execution. | Engineering readiness only; never main-table evidence. |
| `DIAGNOSTIC` | Mock/subset/debug screening. | Qualitative screening only; never Stage 5A/5B table evidence. |

## Stage 5A Evidence Snapshot For Screening Gates

Stage 5A completed 27/27 full RadioML2016.10A cells with fixed split `stratified_by_mod_snr_seed42` and train seeds `42`, `2025`, `3407`.

Reference means from Stage 5A:

| Model | Overall mean | Low-SNR mean | Mid-SNR mean | High-SNR mean | Use in Stage 6B |
|---|---:|---:|---:|---:|---|
| `cldnn` | 0.6129 | 0.2224 | 0.8396 | 0.9070 | Strong stable baseline and main low-SNR target |
| `resnet1d` | 0.5959 | 0.2059 | 0.8197 | 0.8922 | Stable CNN reference |
| `iq_param_matched` | 0.5945 | 0.2163 | 0.8121 | 0.8809 | Required control for fusion claims |
| `fusion_iq_stft` | 0.5771 | 0.2213 | 0.7858 | 0.8428 | Fusion warning: low-SNR does not justify overall damage |
| `mcldnn` | 0.2501 | 0.1313 | 0.3182 | 0.3403 | Diagnostic only because seeds 2025/3407 collapsed |

Screening should favor candidates that plausibly improve low-SNR performance without damaging mid/high SNR or overall accuracy. Any tiny subset signal must be compared against `cldnn`, `resnet1d`, and `iq_param_matched` in the same harness before a later pilot is considered.

## Code Support Matrix

| Capability | Current status | Evidence | Stage 6B consequence |
|---|---|---|---|
| Model registry | Partial support | `cnn1d`, `resnet1d`, `cldnn`, `mcldnn`, `lwamcnet`, `iq_param_matched`, `fusion_iq_amp_phase`, and other existing names are in `src/radioml_amc/training/trainer.py`. | `fusion_iq_amp_phase` is directly usable. `tcn_gru` and `mcldnn_stable_v2` are missing. |
| Feature views | Supported | `SignalDataset` supports `iq`, `amp_phase`, `stft`, and `cwt`. | IQ plus amplitude/phase static fusion can be smoke tested now. |
| Trainer loss hook | Missing | Trainer currently instantiates plain `nn.CrossEntropyLoss()`. | Low-SNR weighted CE cannot be claimed or screened until a loss hook is added and unit tested. |
| Augmentation hook | Missing | `SignalDataset` and `_loop` do not apply train-time transforms. | Cheap augmentation is protocol-planned only until transform hooks exist. |
| Diagnostic output root | Supported by config | Stage 6B templates point to `results/paper_stage6/diagnostic/stage6b/...`. | Diagnostic outputs can be isolated from Stage 5 paths. |
| No-overwrite guard | Strengthened for Stage 6B scope | Timestamped run directories already use `exist_ok=False`; Stage 6B diagnostic/smoke roots now refuse protected `results/paper_stage2/rml2016a` output roots. | Stage 6B configs should stay outside Stage 5 result roots. |
| Evidence tag / run metadata | Strengthened | Trainer now resolves `evidence.tag` / `outputs.evidence_tag` and writes it into resolved config, metrics, and training summary. | Stage 6B smoke and diagnostic runs can carry explicit `SMOKE TEST` or `DIAGNOSTIC` labels. |

## Config Templates Added

All templates are non-full-run Stage 6B artifacts:

- `configs/paper/stage6b/low_snr_weighted_ce_cldnn_resnet1d_template.yaml`
- `configs/paper/stage6b/fusion_iq_amp_phase_static_smoke.yaml`
- `configs/paper/stage6b/tcn_gru_temporal_hybrid_template.yaml`
- `configs/paper/stage6b/mcldnn_stable_v2_diagnostic_template.yaml`
- `configs/paper/stage6b/cheap_augmentation_template.yaml`

Only `fusion_iq_amp_phase_static_smoke.yaml` maps to a currently supported model path. The other templates are queue definitions and must not be interpreted as implemented experiments.

## Executed Stage 6B Smoke Evidence

One Stage 6B mock smoke output is present:

- Run root: `results/paper_stage6/diagnostic/stage6b/fusion_iq_amp_phase_static/20260508_093001_fusion_iq_amp_phase/`
- Model: `fusion_iq_amp_phase`
- Feature views: `iq`, `amp_phase`
- Dataset: `mock_rml2016a_style`
- Data mode: `mock`
- Train seed: `42`
- Epochs requested: `1`
- Device: CPU
- Evidence tag: `SMOKE TEST`
- Artifacts include config, metrics, per-SNR/per-class metrics, predictions, confusion CSVs, complexity, latency placeholder, split summary, and training summary.

Interpretation:

- This run verifies that the `fusion_iq_amp_phase` mock path and artifact writer execute.
- Its accuracy values are synthetic smoke evidence and must not be used for research claims or Stage 5A/5B tables.
- Its `latency.json` is a training-loop placeholder, not a `CONTROLLED_LATENCY` measurement.

## Candidate 1: Low-SNR Weighted CE On CLDNN/ResNet1D

Status: not directly executable as weighted CE in current code.

Purpose:

- Directly target the low-SNR gap where the best current stable model reaches only about `0.2224`.
- Use `cldnn` and `resnet1d` because both are stable Stage 5A references.

Mock/smoke scheme:

- Unit test a loss factory before any training: `plain_ce`, `snr_group_weighted_ce`.
- On mock data, verify that low-SNR samples receive the intended scalar weights.
- Run at most one mock smoke epoch after the hook exists, with `evidence.tag=DIAGNOSTIC`.
- No result may be used as performance evidence.

Tiny subset scheme after hook approval:

- Data: RadioML2016.10A tiny subset only, fixed split derivation, capped samples per modulation/SNR.
- Seeds: start with `42`; add `2025` only if seed 42 is stable.
- Grid: low/mid/high weights `1/1/1`, `1.5/1/1`, `2/1/1`.
- Pass gate: no training instability; low-SNR improves against same-subset CLDNN/ResNet control without clear high-SNR collapse.

Decision:

- Not allowed into tiny subset until the loss hook exists and unit tests pass.

## Candidate 2: IQ Plus Amplitude/Phase Static Fusion

Status: directly supported; mock smoke has completed successfully as `SMOKE TEST` evidence.

Purpose:

- Test a physically meaningful second 1D view that is more aligned with I/Q signals than the weak standalone STFT branch.
- Compare against `iq_param_matched`, not just vanilla CNN.

Mock/smoke scheme:

- Config: `configs/paper/stage6b/fusion_iq_amp_phase_static_smoke.yaml`.
- Model: `fusion_iq_amp_phase`.
- Views: `["iq", "amp_phase"]`.
- Data: mock only, one epoch max if executed.
- Output root: `results/paper_stage6/diagnostic/stage6b/fusion_iq_amp_phase_static`.
- Evidence tag: `SMOKE TEST`.

Tiny subset scheme after approval:

- Candidate: `fusion_iq_amp_phase`; tiny subset would still be `DIAGNOSTIC` only.
- Controls in same subset: `iq_param_matched`, `cldnn`, `resnet1d`.
- SNR reporting: overall, low, mid, high; no low-SNR-only selection.
- Pass gate: subset low-SNR improvement over `iq_param_matched` or `cldnn` without mid/high damage large enough to make the model scientifically unattractive.

Decision:

- Eligible for a later explicitly approved tiny subset diagnostic because the mock smoke exists. The tiny subset must use same-subset `iq_param_matched`, `cldnn`, and `resnet1d` controls and must not be merged into Stage 5A/5B tables.

## Candidate 3: TCN-GRU Temporal Hybrid

Status: not implemented in the current model registry.

Purpose:

- Test a bounded-cost temporal hybrid close to the winning CLDNN family before considering heavier transformer or graph models.

Mock/smoke scheme:

- Add a separate `tcn_gru` model, not an alias for CLDNN.
- Unit tests: forward shape, parameter count, model registry, required views.
- One-batch mock overfit only after forward tests pass.
- Evidence tag: `DIAGNOSTIC`.

Tiny subset scheme after implementation approval:

- Seed `42` only at first.
- Architecture start point: TCN channels `64`, kernel `5`, dilations `[1,2,4]`, GRU hidden `64`, unidirectional.
- Pass gate: stable training and subset metrics competitive with CLDNN overall, with low/mid-SNR signal worth a second seed.

Decision:

- Not allowed into tiny subset until model registry support and unit tests exist.

## Candidate 4: MCLDNN-Stable-v2 Diagnostic

Status: original `mcldnn` exists; `mcldnn_stable_v2` does not exist.

Purpose:

- Diagnose MCLDNN seed-collapse behavior without touching or cleaning the Stage 5A MCLDNN evidence.

Mock/smoke scheme:

- Add a new model name `mcldnn_stable_v2`; do not overwrite `mcldnn`.
- Unit tests: forward shape, parameter count, registry alias exclusion.
- Diagnostic checks: first-batch loss, prediction histogram, gradient norm logging.
- One-batch mock overfit before any real subset.
- Evidence tag: `DIAGNOSTIC`.

Tiny subset scheme after implementation approval:

- Seeds: `42`, `2025`, `3407` because the failure mode is seed-specific.
- Optimizer check: AdamW vs Adam; learning rates `1e-3`, `5e-4`, `1e-4`; gradient clip `1.0`.
- Pass gate: no chance-level collapse across all three seeds on tiny subset.

Decision:

- Not allowed into tiny subset until stable-v2 is implemented as a separate model and mock diagnostics pass.

## Candidate 5: Cheap Signal Augmentation

Status: not implemented in the current training/data pipeline.

Purpose:

- Screen low-cost label-preserving robustness transforms before high-burden GAN/diffusion augmentation.

Candidate transforms:

- Time shift with bounded circular shift.
- Phase rotation.
- Amplitude scaling.
- Calibrated additive noise.

Mock/smoke scheme:

- Add deterministic transform unit tests before training.
- Verify shape preservation, finite values, reproducible RNG, and no label mutation.
- One mock smoke epoch only after transforms are wired into the train loader.
- Evidence tag: `DIAGNOSTIC`.

Tiny subset scheme after hook approval:

- Controls: same model without augmentation on identical subset.
- Start with CLDNN or ResNet1D; do not combine with weighted CE in the first screen.
- Pass gate: no obvious loss of high-SNR accuracy and at least a qualitative low-SNR robustness signal.

Decision:

- Not allowed into tiny subset until augmentation hooks and transform unit tests exist.

## Queue Decision

| Priority | Candidate | Current code readiness | Next allowed action |
|---:|---|---|---|
| 1 | IQ + amp_phase static fusion | Supported; mock smoke completed | Tiny subset diagnostic only if explicitly approved, with `iq_param_matched`, `cldnn`, and `resnet1d` same-subset controls |
| 2 | Low-SNR weighted CE on CLDNN/ResNet1D | Missing loss hook | Add and unit-test loss hook before tiny subset |
| 3 | TCN-GRU temporal hybrid | Missing model | Add model and registry tests before tiny subset |
| 4 | MCLDNN-stable-v2 diagnostic | Missing stable-v2 model | Add separate diagnostic model and mock overfit checks |
| 5 | Cheap augmentation | Missing augmentation hook | Add deterministic transform hook and unit tests |

Only `fusion_iq_amp_phase` is currently eligible to move toward a later tiny subset diagnostic. The other four candidates remain queued behind missing infrastructure.

## Exclusion Rules For Stage 6B Outputs

A Stage 6B output is excluded from Stage 5A and Stage 5B main tables if any of the following is true:

- `data.mode` is `mock`;
- `evidence.tag` is `DIAGNOSTIC` or `SMOKE TEST`;
- run root contains `diagnostic`, `smoke`, `subset`, `debug`, or `stage6b`;
- dataset is capped by modulation, SNR, samples per group, or any subset setting;
- epochs, seeds, split protocol, metric schema, latency protocol, or artifact schema differ from the frozen Stage 5A full-run protocol;
- model is a diagnostic variant such as `mcldnn_stable_v2`;
- augmentation, loss reweighting, gradient probes, or debug logging are active.

Diagnostic results may be summarized qualitatively in Stage 6 notes only. They must not be merged into Stage 5A/5B aggregate CSVs or paper main tables.

## Required Next Step

Before any Stage 6B execution:

1. Confirm the exact candidate and config path.
2. Confirm the run root is under `results/paper_stage6/diagnostic/stage6b/`.
3. Confirm `evidence.tag` is `DIAGNOSTIC` or `SMOKE TEST`.
4. Confirm `data.mode=mock` or tiny subset settings are explicit.
5. Confirm no command is a full RadioML2016.10A training command.

No full run is authorized by this protocol.
