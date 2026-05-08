# Paper-Stage 6A Optimization Literature and Experiment Plan

Date: 2026-05-08

Project: `radioml-amc-stage1`

Server target path: `/hy-tmp/radioml-amc-stage1`

Scope: evidence-bounded optimization and literature-aligned experiment planning after Stage 5A/5B. This is a protocol and planning artifact only. It is not paper prose and it is not new experiment evidence.

## Hard Guardrails

- RadioML2018.01A must not be run under this plan unless a later, explicit protocol authorizes it.
- No full training is authorized by this document.
- No tiny subset, smoke, or diagnostic execution is authorized by this document.
- Stage 5A and Stage 5B artifacts must not be overwritten, deleted, renamed, selectively cleaned, or re-aggregated in a way that hides failed seeds.
- MCLDNN seed `2025` and seed `3407` chance-level Stage 5A results remain retained as protocol evidence.
- Stage 6B mock, smoke, subset, and diagnostic outputs must never be merged into Stage 5A/5B main tables.
- This document does not assert that fusion or gated fusion is generally superior to I/Q baselines.

## Evidence Read For This Plan

Readable project evidence:

- `docs/paper/PAPER_STAGE5A_FULL_RML2016A_TRAINING_REPORT.md`
- `docs/paper/PAPER_STAGE5B_RESULT_AUDIT_AND_TABLES.md`
- `docs/paper/PAPER_STAGE6B_SCREENING_PROTOCOL_AND_CANDIDATE_QUEUE.md`
- `results/paper_stage2/rml2016a/stage5a_status.json`
- `results/paper_stage2/rml2016a/aggregate/main_table_metrics.csv`
- `results/paper_stage2/rml2016a/aggregate/main_table_metrics.md`
- `results/paper_stage2/rml2016a/aggregate/low_snr_table.csv`
- `results/paper_stage2/rml2016a/aggregate/complexity_latency_table.csv`
- `results/paper_stage6/diagnostic/stage6b/fusion_iq_amp_phase_static/20260508_093001_fusion_iq_amp_phase/`
- `docs/paper/EXPERIMENT_PROTOCOL_V2.md`
- `docs/paper/BASELINE_MATRIX_STAGE2.md`
- `docs/paper/METRICS_AND_LOGGING_SPEC.md`
- `docs/paper/LITERATURE_REVIEW_STAGE1.md`

Missing or not used as evidence:

- `docs/session_state.md` is missing.
- `docs/progress.md` is missing.
- `results/latest/` is missing.
- No RadioML2018.01A result evidence exists in this repository audit.

## Evidence Labels

| Label | Meaning | Allowed paper use |
|---|---|---|
| `PROJECT_SUPPORTED` | Full RadioML2016.10A Stage 5A/5B evidence using the fixed split and three train seeds. | Main RML2016A experimental tables and bounded claims. |
| `CONTROLLED_LATENCY` | Stage 5B controlled CUDA latency evidence using warmup `50`, measured `200`, and batch sizes `1` and `256`. | Complexity/latency table with the measured scope stated. |
| `SMOKE TEST` | Mock or synthetic execution used only to verify code paths. | Engineering readiness notes only; never main-table evidence. |
| `DIAGNOSTIC` | Mock/subset/debug investigation used to screen mechanisms or failure modes. | Qualitative diagnostic discussion only; never Stage 5A/5B main-table evidence. |
| `LITERATURE_SUPPORTED` | Claim boundary or baseline expectation supported by prior work summaries. | Related-work motivation and reviewer expectation framing, not project performance evidence. |

## Stage 5A/5B Evidence Summary

Stage 5A completed all 27 planned full RadioML2016.10A cells: 9 models times 3 train seeds (`42`, `2025`, `3407`). Every completed run used fixed split `stratified_by_mod_snr_seed42` with `split_source=artifact`.

Main Stage 5B aggregate facts:

| Model | Views | Overall mean | Low-SNR mean | Mid-SNR mean | High-SNR mean | Evidence |
|---|---|---:|---:|---:|---:|---|
| `cnn1d` | iq | 0.581992 | 0.209508 | 0.795606 | 0.865025 | `PROJECT_SUPPORTED` |
| `resnet1d` | iq | 0.595917 | 0.205871 | 0.819722 | 0.892172 | `PROJECT_SUPPORTED` |
| `tfcnn_stft` | stft | 0.506303 | 0.171307 | 0.689975 | 0.769293 | `PROJECT_SUPPORTED` |
| `fusion_iq_stft` | iq+stft | 0.577098 | 0.221326 | 0.785808 | 0.842753 | `PROJECT_SUPPORTED`; trade-off only |
| `cldnn` | iq | 0.612932 | 0.222386 | 0.839596 | 0.906995 | `PROJECT_SUPPORTED`; strongest stable main result |
| `mcldnn` | iq | 0.250083 | 0.131307 | 0.318232 | 0.340303 | `PROJECT_SUPPORTED`; anomaly row |
| `lwamcnet` | iq | 0.551091 | 0.202538 | 0.750960 | 0.815960 | `PROJECT_SUPPORTED` |
| `iq_param_matched` | iq | 0.594462 | 0.216345 | 0.812146 | 0.880934 | `PROJECT_SUPPORTED`; fusion parameter control |
| `gated_fusion_iq_stft` | iq+stft | 0.571947 | 0.211307 | 0.784015 | 0.840732 | `PROJECT_SUPPORTED`; trade-off only |

Interpretation constraints:

- CLDNN is the strongest stable model on overall, low-SNR, mid-SNR, high-SNR, and macro-F1 among the completed Stage 5B table candidates.
- Static `fusion_iq_stft` has a low-SNR mean close to CLDNN, but it loses overall, mid-SNR, and high-SNR accuracy relative to CLDNN and ResNet1D.
- `gated_fusion_iq_stft` does not improve the Stage 5B main result; it should be described as an observed trade-off, not as a successful final method.
- MCLDNN seed `2025` and `3407` collapsed to chance-level single-class predictions. The aggregate row is retained and must not be sanitized.

## Literature-Aligned Optimization Targets

The Stage 1 literature review establishes that raw I/Q baselines, CLDNN/MCLDNN-style temporal models, lightweight CNNs, complex-valued networks, time-frequency representations, multi-view fusion, attention, and SNR-aware low-SNR learning are all established prior art. The viable project gap is therefore narrow:

- improve low-SNR behavior without damaging mid/high-SNR behavior;
- control for extra parameters using `iq_param_matched`;
- control preprocessing and inference cost explicitly;
- avoid claiming novelty from generic fusion, generic attention, or generic SNR awareness;
- use diagnostics to decide whether any optimization deserves later full protocol approval.

## Optimization Candidate Queue

| Priority | Candidate | Current readiness | Evidence boundary | Required preconditions before any tiny subset |
|---:|---|---|---|---|
| 1 | IQ plus amplitude/phase static fusion | Model and feature views currently supported; one mock smoke exists in Stage 6B | `SMOKE TEST` only so far | Same-subset controls must include `iq_param_matched`, `cldnn`, and `resnet1d`; no result may enter Stage 5A/5B tables. |
| 2 | Low-SNR weighted cross entropy | Loss hook missing | `DIAGNOSTIC` only after implementation | Add loss factory, unit-test per-SNR weighting, verify no protected output root writes. |
| 3 | Cheap signal augmentation | Train-time transform hook missing | `DIAGNOSTIC` only after implementation | Add deterministic transform hook and tests for time shift, phase rotation, amplitude scaling, and additive noise. |
| 4 | TCN-GRU temporal hybrid | Model missing | `DIAGNOSTIC` only after implementation | Add separate model id, registry tests, forward-shape tests, and parameter-count checks. |
| 5 | MCLDNN-stable-v2 diagnostic | Separate diagnostic model missing | `DIAGNOSTIC` only | Keep original `mcldnn` untouched; add a distinct model id and seed-collapse diagnostics. |

## Candidate Gates

### Candidate 1: IQ Plus Amplitude/Phase Static Fusion

Status: code path is supported and Stage 6B has a completed mock smoke run.

Current evidence:

- Run root: `results/paper_stage6/diagnostic/stage6b/fusion_iq_amp_phase_static/20260508_093001_fusion_iq_amp_phase/`
- Dataset: `mock_rml2016a_style`
- Data mode: `mock`
- Train seed: `42`
- Epochs: `1`
- Evidence tag: `SMOKE TEST`

Allowed interpretation: the model, feature view wiring, artifact writing, and smoke path execute. The numeric accuracy values are synthetic smoke outputs and cannot support a research conclusion.

Next allowed action if explicitly approved later: a tiny subset diagnostic, not a main experiment. It must include same-subset `iq_param_matched`, `cldnn`, and `resnet1d` controls, and its output root must remain under `results/paper_stage6/diagnostic/stage6b/`.

### Candidate 2: Low-SNR Weighted Cross Entropy

Status: planned only. The trainer currently uses plain cross entropy and does not expose a tested SNR-aware loss hook.

Required engineering before any diagnostic run:

- implement a loss factory with a plain CE path and a weighted CE path;
- unit-test that low/mid/high SNR samples receive the intended weights;
- write evidence tag `DIAGNOSTIC` into config, metrics, and training summary;
- keep all outputs outside Stage 5A/5B roots.

Scientific gate for any later full approval: low-SNR improvement must be judged against CLDNN and ResNet1D, not against a weak standalone baseline.

### Candidate 3: Cheap Signal Augmentation

Status: planned only. Train-time augmentation hooks are missing.

Required engineering before any diagnostic run:

- deterministic transform API;
- tests for shape preservation, finite values, reproducible RNG, and label invariance;
- one mock smoke only after transform tests pass.

Scientific gate for any later full approval: augmentation must not improve low-SNR by merely damaging high-SNR or shifting the class distribution.

### Candidate 4: TCN-GRU Temporal Hybrid

Status: planned only. No supported model id exists in the registry.

Required engineering before any diagnostic run:

- add a separate `tcn_gru` model;
- add registry, forward-shape, and parameter-count tests;
- perform one-batch mock overfit before any real subset diagnostic.

Scientific gate for any later full approval: the model must be competitive with CLDNN overall and show a reason to add complexity.

### Candidate 5: MCLDNN-Stable-v2 Diagnostic

Status: planned only. Original Stage 5A `mcldnn` artifacts are retained and must not be touched.

Required engineering before any diagnostic run:

- add a separate model id such as `mcldnn_stable_v2`;
- add first-batch loss, prediction histogram, and gradient norm diagnostic logging;
- test seeds `42`, `2025`, and `3407` only in a labelled diagnostic scope.

Scientific gate for any later full approval: all three seeds must avoid chance-level collapse on the same diagnostic subset before any full-run discussion.

## Table And Artifact Readiness

Ready for bounded paper preparation:

- Stage 5B main RML2016A table: `PROJECT_SUPPORTED`.
- Stage 5B low-SNR table: `PROJECT_SUPPORTED`.
- Stage 5B controlled CUDA latency table: `CONTROLLED_LATENCY`.
- MCLDNN anomaly table and diagnostic explanation: `PROJECT_SUPPORTED` anomaly evidence.

Still incomplete or cautionary:

- `complexity_latency_table.csv` contains controlled CUDA latency, but FLOPs/MACs fields are empty in the aggregate rows.
- CPU end-to-end latency and STFT preprocessing-inclusive latency are not complete enough for a broad deployment claim.
- `EXPERIMENT_PROTOCOL_V2.md` names `significance_tests.json` and per-SNR mean/std aggregate outputs as desired final artifacts; current Stage 5B aggregate files cover the main table and low-SNR table but do not close all statistical-test expectations.
- RadioML2018.01A has not been run and cannot be claimed.

## Recommended Next Sequence

1. Finish documentation consistency: Stage index, Stage 6A, and Stage 6B status must agree on what evidence exists.
2. Package/audit artifacts before paper writing: record exact Stage 5A/5B source files, aggregate outputs, and evidence labels.
3. Prepare a paper outline and figure/table inventory using only `PROJECT_SUPPORTED`, `CONTROLLED_LATENCY`, and clearly separated `SMOKE TEST`/`DIAGNOSTIC` notes.
4. Only after the above, consider an explicitly approved Stage 6B tiny subset diagnostic for `fusion_iq_amp_phase` with same-subset `iq_param_matched`, `cldnn`, and `resnet1d` controls.

## Required Claim Boundaries

- It is acceptable to write that the project has a complete, fixed-split, 3-seed RadioML2016.10A benchmark matrix.
- It is acceptable to write that CLDNN is the strongest observed Stage 5B model under the current protocol.
- It is acceptable to write that static fusion and gated fusion showed trade-offs, not overall superiority.
- It is acceptable to discuss MCLDNN seed collapse as retained anomaly evidence.
- It is not acceptable to write that Stage 6B smoke accuracy supports a method claim.
- It is not acceptable to write that RadioML2018.01A was evaluated.
- It is not acceptable to remove MCLDNN failed seeds from the main aggregate.

## Current Decision

Decision: GO for bounded paper planning and artifact packaging; NO-GO for any new full training from this document.

The next most defensible work item is artifact packaging/audit or paper outline/table inventory, not another training run. A later tiny subset may be useful only as `DIAGNOSTIC` screening and only with same-subset controls.
