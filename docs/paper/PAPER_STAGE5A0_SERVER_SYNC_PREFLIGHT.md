# Paper-Stage 5A-0 Server Sync Preflight

Date: 2026-05-08 Asia/Shanghai
Server repo: `/hy-tmp/radioml-amc-stage1`
Scope: server sync, fixed split artifact generation/verification, unit tests, model construction, and CPU complexity/latency schema smoke only. No RadioML2016.10A full training was started. RadioML2018.01A was not run.

## Conclusion

1. Server synced to Stage 4F: GO.
   - Stage 4E/4F source, docs, configs, scripts, profiling/reporting modules, fixed split schema tests, and direct dependencies were synced to the server repo.
   - Server preflight pytest result: `38 passed, 1 skipped`.

2. Fixed split artifact exists: GO.
   - NPZ: `/hy-tmp/radioml-amc-stage1/data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
   - Summary: `/hy-tmp/radioml-amc-stage1/data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json`
   - Summary source path: `/hy-tmp/radioml-amc-stage1/data/raw/radioml2016/RML2016.10a_dict.pkl`
   - Verified dataset metadata: `220000` samples, `11` classes, `20` SNR values.
   - Verified split sizes: train `154000`, val `22000`, test `44000`.

3. Trainer uses the fixed split artifact for the Stage 5A config: GO.
   - `configs/stage2_rml2016a_real_full.yaml` contains `split_artifact_npz` and `split_summary_json`.
   - `src/radioml_amc/training/trainer.py` contains `resolve_experiment_splits`, `load_split_artifact`, `split_artifact_npz`, and `config_resolved.yaml` handling.
   - Dynamic server check with `train_seed=2025` resolved `split_id=stratified_by_mod_snr_seed42` and `split_source=artifact`.

4. Nine main-table models are constructible: GO.
   - Verified by CPU smoke construction/forward: `cnn1d`, `resnet1d`, `tfcnn_stft`, `fusion_iq_stft`, `cldnn`, `mcldnn`, `lwamcnet`, `iq_param_matched`, `gated_fusion_iq_stft`.

5. V2 complexity/latency schema smoke passed: GO.
   - Smoke command used `device=cpu`, `warmup_iters=1`, `measured_iters=2`.
   - All nine smoke JSON files under `/hy-tmp/radioml-amc-stage1/results/paper_stage5a0_preflight/complexity_latency_smoke/` contain top-level `complexity` and `latency`.
   - Required V2 complexity keys and latency keys were present for all nine models.
   - CPU latency values are SMOKE TEST only, not research evidence.

6. Permission to enter true Paper-Stage 5A full RadioML2016.10A 3-seed training: GO.
   - Allowed next step: Paper-Stage 5A full RadioML2016.10A 3-seed training only, using the fixed split artifact above.
   - Still prohibited: RadioML2018.01A and any claim that fusion is broadly superior to baselines without full evidence.
