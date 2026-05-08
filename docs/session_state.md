# Session State - 2026-05-08

Current goal: manuscript drafting under evidence-boundary guardrails.

Latest audit record:

- `docs/paper/EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`

Latest manuscript draft:

- `docs/paper/manuscript/section7_limitations.md`

Current status:

- No training was run.
- No tiny subset was run.
- No RadioML2018.01A run was started.
- No Stage 5A/5B artifacts were overwritten or modified.
- Stage 6B smoke/diagnostic data remains excluded from Stage 5A/5B main tables.
- Section 5.5 was drafted as retained MCLDNN negative evidence only; MCLDNN seeds `2025` and `3407` remain included.
- Section 6 Discussion was drafted as interpretation only; it does not add new results, conclusions, or diagnostic-as-result claims.
- Section 7 Limitations was drafted as limitations only; it records dataset/split, latency/complexity, fusion/gated, MCLDNN, artifact/environment, and diagnostic evidence boundaries.

Local sync summary:

- `paper_package/server_sync_20260508`: 269 files, 1,042,738 bytes.
- `paper_package/predictions_archive_20260508`: 27 prediction files, 635,907,848 bytes.
- `paper_package/statistical_tests_20260508`: 6 statistical-test files.
- `docs/paper/manuscript`: 8 manuscript draft files.
- Complete Stage 5A server `best_model.pt` weights are not synced locally.

Server environment:

- Repo: `/hy-tmp/radioml-amc-stage1`
- Python: 3.11.12
- PyTorch: 2.9.1+cu128
- GPU: NVIDIA GeForce RTX 4070
- CUDA available: true

Local environment:

- Python: 3.13.7
- PyTorch: 2.11.0+cpu
- CUDA available: false

Next safe step:

- If continuing experiments, first decide whether trained Stage 5A weights need to be archived locally. If yes, sync the 27 server `best_model.pt` files into a separate archive/package path and hash-check them. Do not overwrite local `results/` or Stage 5A/5B roots by default.
- New training or diagnostics should be run on the server only after an explicit protocol prompt authorizes the run and output root.
