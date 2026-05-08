# Paper Stage Index

| Paper stage | Status | Goal | Main artifacts | Training needed | Server needed |
|---|---|---|---|---|---|
| Paper-Stage 0 | Draft completed | Create branch and paper documentation skeleton | `docs/paper/`, `configs/paper/`, `scripts/paper/`, `paper_experiments/` README files | No | No |
| Paper-Stage 1 | Draft completed | Literature review and gap consolidation | `LITERATURE_REVIEW_STAGE1.md` | No | No |
| Paper-Stage 2 | Draft completed | Upgrade paper-level experiment protocol | `EXPERIMENT_PROTOCOL_V2.md`, `BASELINE_MATRIX_STAGE2.md`, `METRICS_AND_LOGGING_SPEC.md`, `ABLATION_PLAN_STAGE2.md`, `SNR_AWARE_GATED_FUSION_DESIGN_V1.md` | No | No |
| Paper-Stage 3 | Superseded by Stage 4/5 evidence | SNR-aware gated fusion prototype and low-SNR analysis infrastructure | `PAPER_STAGE4A_READINESS_REPORT.md`, Stage 3/4 tests and scripts | Smoke/subset only | Usually no |
| Paper-Stage 4 | Completed as readiness hardening | Baseline hardening, temporal/lightweight baselines, fixed split and V2 schema | `PAPER_STAGE4B_BASELINE_READINESS.md`, `PAPER_STAGE4C_BASELINE_HARDENING.md`, `PAPER_STAGE4D_TEMPORAL_BASELINE.md`, `PAPER_STAGE4F_FIXED_SPLIT_SCHEMA_HARDENING.md` | Smoke/subset only in those stages | Yes for later full |
| Paper-Stage 5A | Completed | Full RadioML2016.10A 3-seed fixed-split execution | `PAPER_STAGE5A_FULL_RML2016A_TRAINING_REPORT.md`, `results/paper_stage2/rml2016a/stage5a_status.json` | Completed; no rerun authorized here | Yes |
| Paper-Stage 5B | Completed | Result audit, anomaly diagnosis, and table preparation | `PAPER_STAGE5B_RESULT_AUDIT_AND_TABLES.md`, `results/paper_stage2/rml2016a/aggregate/*` | No | Yes |
| Paper-Stage 6A | Completed as plan | Optimization literature alignment and experiment queue | `PAPER_STAGE6A_OPTIMIZATION_LITERATURE_AND_EXPERIMENT_PLAN.md` | No | No |
| Paper-Stage 6B | Protocol ready; one mock smoke completed | Controlled diagnostic/smoke screening queue | `PAPER_STAGE6B_SCREENING_PROTOCOL_AND_CANDIDATE_QUEUE.md`, `results/paper_stage6/diagnostic/stage6b/fusion_iq_amp_phase_static/*` | Mock/subset diagnostic only if explicitly approved | Usually yes for subset |
| Paper writing | Not started | Paper outline, figure/table inventory, bounded manuscript drafting | Not yet created | No new training unless a documented gap remains | No |

## Stage Notes

Paper-Stage 0 freezes existing evidence and creates the planning structure. It
must not change the stable course-project workflow.

Paper-Stage 1 decides whether the planned method has enough novelty and what
published baselines must be considered.

Paper-Stage 2 prevents uncontrolled experiment growth by fixing seeds, metrics,
splits, complexity reporting, and claim boundaries before implementation.

Paper-Stage 3 and Paper-Stage 4 produced engineering readiness, baseline
hardening, fixed-split handling, schema hardening, and smoke/subset-only checks.
Mock/subset outputs from these stages are not main-table evidence.

Paper-Stage 5A completed the full RadioML2016.10A fixed-split 3-seed matrix for
nine model rows. Paper-Stage 5B audited the artifacts and produced main,
low-SNR, and controlled latency aggregate tables.

Paper-Stage 6A is a planning and claim-boundary artifact. It does not authorize
training and does not add performance evidence.

Paper-Stage 6B is diagnostic/smoke only. The existing `fusion_iq_amp_phase`
mock smoke is `SMOKE TEST` evidence and must not be merged into Stage 5A/5B
tables.

## Evidence Label Policy

- `PROJECT_SUPPORTED`: full RadioML2016.10A Stage 5A/5B evidence eligible for
  bounded main RML2016A tables.
- `CONTROLLED_LATENCY`: controlled CUDA latency evidence eligible for a
  clearly scoped complexity/latency table.
- `SMOKE TEST` / `DIAGNOSTIC`: engineering screening only; never main-table
  evidence and never merged into Stage 5A/5B aggregate outputs.

## Current Top Priority

The next recommended work item is artifact packaging/audit or a paper
outline/table inventory based on completed Stage 5A/5B evidence. Any later tiny
subset must remain `DIAGNOSTIC` and must include same-subset controls:
`iq_param_matched`, `cldnn`, and `resnet1d`.
