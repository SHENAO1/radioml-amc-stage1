# Experiment Environment and Local Sync Status - 2026-05-08

Status: audit record

Scope: local sync inspection and experiment environment capture only. No training, no tiny subset run, no RadioML2018.01A run, no Stage 5A/5B artifact rewrite, and no Stage 6B diagnostic data merge into Stage 5A/5B tables.

## Baton Files

- `docs/session_state.md`: missing at startup; created during this audit as a concise baton pointing to this environment record.
- `docs/progress.md`: missing.
- No project-local `AGENTS.md` was found under `radioml-amc-stage1`.
- The outer workspace instructions remain active: rebuild context from durable baton files when present and check dirty files before edits.

## Git State

Outer workspace:

- Path: `E:\ML_HomeWork\ML_Final_Assignment\T2_Custom_Topic`
- Status: no commits yet on `master`.
- `radioml-amc-stage1/` is still an untracked directory at the outer repository level.

Inner project repository:

- Path: `E:\ML_HomeWork\ML_Final_Assignment\T2_Custom_Topic\radioml-amc-stage1`
- Branch: `paper-sci-track`.
- Dirty state: modified source/config/documentation files and many untracked configs, docs, package artifacts, results, scripts, tests, and manuscript drafts.
- No revert was performed.

Server repository:

- Path: `/hy-tmp/radioml-amc-stage1`
- Branch: `main`
- Head: `296428d`
- Dirty state: modified source/config files and many untracked docs/results/scripts/tests.
- No revert was performed.

## Local Sync Status

Paper package:

- Path: `paper_package/server_sync_20260508`
- Files: 269
- Bytes: 1,042,738
- Manifest: `docs/paper/ARTIFACT_MANIFEST_PAPER_PACKAGE_20260508.csv`
- Manifest rows: 299
- Hash status:
  - `package_hash_match`: 269
  - `server_hash_recorded_not_copied`: 27
  - `missing_on_server`: 3
- Sync policy:
  - `synced_to_paper_package`: 249
  - `synced_diagnostic_only`: 18
  - `synced_package_only_local_split_hash_mismatch`: 2
  - `hash_only_separate_archive_candidate`: 27
  - `missing_on_server_protocol_expected`: 3

Prediction archive:

- Path: `paper_package/predictions_archive_20260508`
- Files: 27
- Bytes: 635,907,848
- Manifest: `docs/paper/ARTIFACT_MANIFEST_PREDICTIONS_ARCHIVE_20260508.csv`
- Coverage: 9 models x 3 seeds.
- Models: `cldnn`, `cnn1d`, `fusion_iq_stft`, `gated_fusion_iq_stft`, `iq_param_matched`, `lwamcnet`, `mcldnn`, `resnet1d`, `tfcnn_stft`.
- Seeds: `42`, `2025`, `3407`.
- Evidence label: `PROJECT_SUPPORTED`.
- Stage 6B smoke/diagnostic predictions are not included.

Statistical tests:

- Path: `paper_package/statistical_tests_20260508`
- Files: 6
- Bytes: 50,187
- Files:
  - `paired_bootstrap_accuracy_deltas.csv`
  - `mcnemar_tests.csv`
  - `significance_tests.json`
  - `statistical_tests_summary.md`
  - `ARTIFACT_MANIFEST_STATISTICAL_TESTS_20260508.csv`
  - `ARTIFACT_MANIFEST_STATISTICAL_TESTS_20260508.json`
- These artifacts were generated from archived Stage 5A predictions and remain outside `results/paper_stage2/rml2016a/aggregate/`.

Manuscript drafts:

- Path: `docs/paper/manuscript`
- Files: 5
- Bytes: 19,950
- Drafts present:
  - `section4_experimental_protocol.md`
  - `section5_1_overall_fixed_split_results.md`
  - `section5_2_low_snr_fusion_tradeoff.md`
  - `section5_3_gated_fusion_outcome.md`
  - `section5_4_latency_complexity_caveat.md`

## Model Weight Sync Status

Stage 5A server weights:

- Server path pattern: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/*/seed_*/best_model.pt`
- Server count: 27
- Server bytes: 14,945,559
- Status: present on server.

Local Stage 5A weights:

- Local path checked: `results/paper_stage2/rml2016a/**/best_model.pt`
- Local count: 0
- Status: not synced into the local Stage 5A result tree.

Local paper package weights:

- Path checked: `paper_package/**/best_model.pt`
- Local count: 0
- Status: not included in the paper package.

Local development run weights:

- Path checked: `runs/**/best_model.pt`
- Local count: 19
- Local bytes: 6,215,471
- Interpretation: these are local run artifacts and should not be treated as the complete Stage 5A server weight matrix.

Verdict: prediction files, aggregate evidence, diagnostic smoke metadata, and statistical-test artifacts are synced locally. The complete Stage 5A trained model weights are still on the server and have not been fully downloaded into the local package or local Stage 5A result tree.

## Missing Or Partial Items

- Protocol-expected aggregate files missing on the server-side aggregate path:
  - `main_table_mean_std.csv`
  - `per_snr_mean_std.csv`
  - `significance_tests.json`
- A separate `paper_package/statistical_tests_20260508/significance_tests.json` exists, but it has not been copied into or used to rewrite the Stage 5B aggregate directory.
- Complete Stage 5A model weights are not locally synced.
- CPU latency, FLOPs/MACs, and preprocessing-inclusive latency remain unsupported.

## Local Environment

- OS/platform: Windows 11, `Windows-11-10.0.26200-SP0`
- Git: `git version 2.53.0.windows.2`
- Python executable: `E:\Python\Python313_7\python.exe`
- Python: `3.13.7`
- PyTorch: `2.11.0+cpu`
- NumPy: `2.4.4`
- pandas: not available in the checked global Python environment.
- scikit-learn: `1.8.0`
- SciPy: `1.17.1`
- CUDA availability from local PyTorch: `False`
- Local role: paper writing, packaging, manifest checks, statistical artifact review, and lightweight CPU-only inspection. Do not use this environment for GPU training.

## Server Environment

- SSH: key authentication worked with `ssh -p 39211 root@i-2.gpushare.com`; no password was used or recorded.
- Repo path: `/hy-tmp/radioml-amc-stage1`
- Hostname: `I2880f974c100501b7d`
- Kernel: `Linux 5.15.0-164-generic #174-Ubuntu SMP Fri Nov 14 20:25:16 UTC 2025 x86_64`
- Server timestamp during audit: `2026-05-08T13:55:28+08:00`
- Python executable: `/usr/local/bin/python`
- Python: `3.11.12`
- PyTorch: `2.9.1+cu128`
- CUDA reported by PyTorch: `12.8`
- CUDA available: `True`
- GPU count: 1
- GPU: `NVIDIA GeForce RTX 4070`
- NVIDIA driver: `570.211.01`
- GPU memory: 12,282 MiB
- `/hy-tmp` disk: 50G total, 1.8G used, 49G available, 4% used.
- Server role: GPU experiment execution, if a future protocol explicitly authorizes new runs.

## Evidence Boundary For Future Work

- `PROJECT_SUPPORTED`: Stage 5A/5B full RadioML2016.10A fixed-split evidence, predictions archive, and paired statistical artifacts derived from Stage 5A predictions.
- `CONTROLLED_LATENCY`: controlled CUDA forward-pass latency only. It does not support CPU latency, FLOPs/MACs, or preprocessing-inclusive deployment claims.
- `SMOKE TEST` / `DIAGNOSTIC`: Stage 6B smoke or diagnostic outputs. These must remain outside Stage 5A/5B main tables and statistical tests.

## Future Experiment Guardrails

Before any future experiment:

1. Check dirty files locally and on the server.
2. Record current git branch, head, dirty state, Python/PyTorch/CUDA versions, GPU name, driver, and disk availability.
3. Use a new output root for new experiments. Do not write into existing Stage 5A/5B artifact roots unless explicitly authorized.
4. Preserve MCLDNN seed `2025` and `3407` chance-level evidence in the Stage 5A/5B record.
5. Do not run RadioML2018.01A unless a new protocol explicitly authorizes it.
6. If Stage 6B tiny subset diagnostics are authorized later, label them as `DIAGNOSTIC`, keep them out of main tables, and include same-subset controls: `iq_param_matched`, `cldnn`, and `resnet1d`.
7. If trained weights are needed locally for inference, resume, or archival completeness, sync the 27 server `best_model.pt` files into a separate package/archive path first, then hash-check them. Do not overwrite local `results/` or Stage 5A/5B roots by default.
