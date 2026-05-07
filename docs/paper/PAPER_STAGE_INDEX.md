# Paper Stage Index

| Paper stage | Status | Goal | Main artifacts | Training needed | Server needed |
|---|---|---|---|---|---|
| Paper-Stage 0 | In progress | Create branch and paper documentation skeleton | `docs/paper/`, `configs/paper/`, `scripts/paper/`, `paper_experiments/` README files | No | No |
| Paper-Stage 1 | Pending | Literature review and gap consolidation | Literature table, gap statement, Related Work outline | No | No |
| Paper-Stage 2 | Pending | Upgrade paper-level experiment protocol | Final protocol, metric definitions, seed plan, result table templates | No | No |
| Paper-Stage 3 | Pending | SNR-aware gated fusion prototype | Model draft, subset configs, smoke tests, implementation notes | Subset only | Usually no |
| Paper-Stage 4 | Pending | Low-SNR training strategy ablation | Weighted loss, SNR-balanced sampler, augmentation ablations | Yes | Yes for full |
| Paper-Stage 5 | Pending | RadioML2018.01A extension validation | Dataset protocol, baseline transfer, main comparison | Yes | Yes |
| Paper-Stage 6 | Pending | Paper first draft | Abstract, Introduction, Related Work, Method, Experiments, Limitations | No new training unless gaps remain | No |

## Stage Notes

Paper-Stage 0 freezes existing evidence and creates the planning structure. It
must not change the stable course-project workflow.

Paper-Stage 1 decides whether the planned method has enough novelty and what
published baselines must be considered.

Paper-Stage 2 prevents uncontrolled experiment growth by fixing seeds, metrics,
splits, complexity reporting, and claim boundaries before implementation.

Paper-Stage 3 should implement only a minimal prototype after the literature gap
and protocol are clear.

Paper-Stage 4 should test whether training strategy improves low-SNR robustness
before adding heavier architectures.

Paper-Stage 5 should only begin after RadioML2016.10A evidence is stable.

Paper-Stage 6 should write bounded claims from completed evidence, not from
planned experiments.
