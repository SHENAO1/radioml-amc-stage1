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
| Paper-Stage 6 Extended Budget (RTX 3090) | Completed (2026-05-09) | Sensitivity / robustness check that Stage 5A is not under-budgeted | `PAPER_STAGE6_EXTENDED_BUDGET_3090_REPORT.md`, `PAPER_STAGE6_EXTENDED_BUDGET_ANALYSIS.md`, `docs/paper/manuscript/section7_7_training_budget_sensitivity.md`, `results/paper_stage6/extended_budget_3090/rml2016a/*` | Completed; 12 cells × epoch 50 + cosine LR; separate evidence label `EXTENDED_BUDGET_3090` | Yes (RTX 3090) |
| Paper-Stage 6 Low-SNR Confusion Analysis | Completed (2026-05-09) | Per-class low-SNR confusion-matrix breakdown of Stage 5A predictions | `PAPER_STAGE6_LOW_SNR_CONFUSION_ANALYSIS.md`, `docs/paper/manuscript/section5_2_addendum_low_snr_per_class.md`, `results/paper_stage6/low_snr_confusion_extended/*` | No (post-process only) | No |
| Paper-Stage 6 Extended Complexity / Latency | Completed (2026-05-09) | Fill MACs / FLOPs / CPU-latency cells that Stage 5A left empty | `PAPER_STAGE6_EXTENDED_COMPLEXITY_ANALYSIS.md`, `docs/paper/manuscript/section5_4_addendum_complexity_latency_filled.md`, `results/paper_stage6/extended_complexity_latency/*` | No (forward-pass timing only) | Yes for the registered measurement |
| Paper-Stage 6 SNR-Aware Weighted CE (RTX 3090) | Completed (2026-05-09) | Test whether SNR-weighted CE can move the low-SNR / overall trade-off | `PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md`, `PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_ANALYSIS.md`, `docs/paper/manuscript/section7_8_low_snr_weighted_ce_outcome.md`, `results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/*` | Completed; 6 cells × epoch 50 + cosine LR + SnrWeightedCE (low=2.0, mid=1.0, high=0.7); separate evidence label `LOW_SNR_WEIGHTED_CE_3090` | Yes (RTX 3090) |
| Paper-Stage 2 Literature Calibration | Completed (2026-05-09) | Search RML2016.10A SOTA + hyperparameter recipes; calibrate improvement budget | `LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md` | No | No |
| Paper-Stage 6 fusion_cldnn_stft + Aug + LS (RTX 3090) — A 方案 | Completed (2026-05-09) | **Positive contribution**: stronger I/Q backbone in fusion + augmentation + label smoothing; beats Stage 5A CLDNN by +1.35 pp overall | `PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_3090_REPORT.md`, `PAPER_STAGE6_FUSION_CLDNN_STFT_AUG_LS_ANALYSIS.md`, `docs/paper/manuscript/section5_6_proposed_fusion_cldnn_stft.md`, `results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/*` | Completed; 3 cells × epoch 50 + cosine LR + signal aug + label smoothing 0.1; separate evidence label `FUSION_CLDNN_STFT_AUG_LS_3090` | Yes (RTX 3090) |
| Paper writing | In progress | Paper outline, figure/table inventory, bounded manuscript drafting | `docs/paper/manuscript/section{4,5_1..5_5,5_2_addendum,5_4_addendum,5_6,6,7,7_7,7_8}_*.md` | No new training unless a documented gap remains | No |

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

Paper-Stage 6 Extended Budget (RTX 3090) is a sensitivity / robustness check
completed 2026-05-09 on a new gpushare RTX 3090 instance. Four of the nine
Stage 5A models (`cldnn`, `resnet1d`, `iq_param_matched`, `fusion_iq_stft`)
were retrained on the same fixed split with epoch 50, 5-epoch linear warmup,
cosine LR, and early-stop patience 15. ΔOverall vs Stage 5A is within ±1 pp
for all four models with the same ranking; ΔLow-SNR is small and uniformly
negative. The hardware change (RTX 4070 Ada -> RTX 3090 Ampere) is registered
as a confound, so this evidence is reported under a separate label and a
separate output root and does not enter the Stage 5A main table or paired
statistical tests.

## Evidence Label Policy

- `PROJECT_SUPPORTED`: full RadioML2016.10A Stage 5A/5B evidence eligible for
  bounded main RML2016A tables.
- `CONTROLLED_LATENCY`: controlled CUDA latency evidence eligible for a
  clearly scoped complexity/latency table.
- `CONTROLLED_LATENCY_EXTENDED`: forward-pass MACs / FLOPs / single-thread CPU
  latency. Same PyTorch / CUDA build as `CONTROLLED_LATENCY` but device
  target is CPU. Eligible only as an addendum to Section 5.4; the original
  `complexity_latency_table.csv` is not modified.
- `EXTENDED_BUDGET_3090`: 4-model sensitivity check on RTX 3090 with extended
  epoch budget and cosine LR. Eligible only as a sensitivity / robustness
  paragraph in Section 7.7; never merged into Stage 5A main table or paired
  statistical tests.
- `LOW_SNR_WEIGHTED_CE_3090`: 2-model intervention check on RTX 3090 with
  group-based SNR-weighted cross-entropy (low=2.0, mid=1.0, high=0.7) on top
  of the EXTENDED_BUDGET schedule. Eligible only as a sensitivity /
  intervention paragraph in Section 7.8; never merged into Stage 5A main
  table or paired statistical tests.
- `FUSION_CLDNN_STFT_AUG_LS_3090`: 1-model proposed-approach evidence on
  RTX 3090. Stacks three interventions: CLDNN-style I/Q backbone in fusion,
  signal-domain augmentation (phase rotation + cyclic time shift, train-only),
  and label smoothing 0.1 in cross-entropy. Eligible as the project's
  positive-contribution Section 5.6, with Section 7-style caveats about
  hardware confound and combination-not-separated. Never merged into Stage 5A
  main table or paired statistical tests.
- `SMOKE TEST` / `DIAGNOSTIC`: engineering screening only; never main-table
  evidence and never merged into Stage 5A/5B aggregate outputs.

## Current Top Priority

The next recommended work item is artifact packaging/audit or a paper
outline/table inventory based on completed Stage 5A/5B evidence. Any later tiny
subset must remain `DIAGNOSTIC` and must include same-subset controls:
`iq_param_matched`, `cldnn`, and `resnet1d`.
