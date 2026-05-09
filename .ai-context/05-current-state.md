# 05 · 当前状态

<!-- 动态文档。每次会话结束前都要更新。保持短小。 -->

**最近更新**: 2026-05-09

## Current Goal
**A 方案 completed and POSITIVE.** `fusion_cldnn_stft + augmentation + label smoothing 0.1` achieves overall mean accuracy 0.6264 (3 seeds, std 0.0005), beating Stage 5A CLDNN 0.6129 by +1.35 pp; all four SNR-aggregate metrics improve. Manuscript updated with Section 5.6 (positive contribution). Stage 5A main table remains frozen. Next decision: ablation experiments (separate the three interventions) or freeze the evidence package and finalise manuscript.

## Latest Evidence / Baton
- Latest training evidence: `docs/paper/PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md` and analysis `docs/paper/PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_ANALYSIS.md`.
- Latest manuscript draft: `docs/paper/manuscript/section7_8_low_snr_weighted_ce_outcome.md` (Section 7.8, separate evidence label `LOW_SNR_WEIGHTED_CE_3090`).
- Other Stage 6 evidence active in this session: `EXTENDED_BUDGET_3090` (P1.1), `CONTROLLED_LATENCY_EXTENDED` (P1.2), low-SNR confusion analysis (P1.3 post-processing).
- Latest audit record: `docs/paper/EXPERIMENT_ENVIRONMENT_AND_SYNC_STATUS_20260508.md`.
- Stage 6B smoke/diagnostic data remains excluded from Stage 5A/5B main tables.

## Done
- `.ai-context/` and thin entry files were initialized from `SHENAO1/ai-handoff-init`.
- Stage 5A/5B prediction archive is locally synced: `paper_package/predictions_archive_20260508`, 27 files, 9 models × 3 seeds.
- Statistical-test artifacts are locally synced: `paper_package/statistical_tests_20260508`, 6 files.
- Manuscript drafts: Section 4, 5.1-5.5, 6, 7, plus new Section 7.7 (extended-budget sensitivity).
- **2026-05-09 P1.1 extended-budget run completed on a new gpushare RTX 3090 instance.**
  - Server: new instance `i-1.gpushare.com:62244`, RTX 3090 24 GB (Ampere sm_86), driver 570.211.01, CUDA 12.8, PyTorch 2.9.1+cu128, Python 3.11.12.
  - Code path: `paper-sci-track` branch pushed to GitHub; uncommitted M + critical untracked files SFTP'd to server; dataset `RML2016.10a_dict.pkl` (612 MB, MD5 `61bf35ac7f0b7d8843613453447ea290`) uploaded.
  - Trainer was extended with optional `train.scheduler` (cosine + warmup); default behaviour unchanged for Stage 5A reproducibility.
  - 12/12 cells completed in 54.4 min, 0 failed: `cldnn`, `resnet1d`, `iq_param_matched`, `fusion_iq_stft` × seeds 42/2025/3407, epoch 50, cosine LR with 5-epoch warmup.
  - Output root `results/paper_stage6/extended_budget_3090/rml2016a/` (separated from Stage 5A/5B).
  - 12 `best_model.pt` files remain on server; not synced locally.

## P1.1 Headline Results (EXTENDED_BUDGET_3090)
- ΔOverall vs Stage 5A: cldnn +0.0015, resnet1d +0.0004, iq_param_matched +0.0067, fusion_iq_stft +0.0080. All within ±1 pp; ranking preserved.
- ΔLow-SNR vs Stage 5A: all four models negative (-0.0003 to -0.0089). Largest drop on `fusion_iq_stft`.
- best_epoch: resnet1d 15-20 (inside Stage 5A budget), cldnn 23-27, iq_param_matched 21-27, fusion_iq_stft 34-42.
- Interpretation: Stage 5A was not materially under-budgeted; budget extension does not save low-SNR; fusion's gap to CLDNN is not a budget issue.

## P1.2 Headline Results (CONTROLLED_LATENCY_EXTENDED)
- MCLDNN heaviest (49.1 M MACs, 573 ms CPU bs=256); CLDNN 8.7 M / 183 ms; ResNet1D 4.9 M / 91 ms; fusion_iq_stft 2.0 M / 83 ms; tfcnn_stft cheapest (0.42 M / 22 ms).
- `fusion_iq_stft` and `gated_fusion_iq_stft` are *cheaper* in MACs than ResNet1D, ruling out a "fusion underperforms because it does less compute" interpretation.
- `lwamcnet` has the smallest parameter count (20k) but slow CPU bs=1 (2.33 ms) due to depthwise/grouped conv kernels not paying off on single-thread CPU.

## P1.3 Headline Results (post-processed Stage 5A predictions)
- 7 of 9 stable models collapse to predicting AM-SSB at low SNR; row-fractions of digital-modulation-true-class -> AM-SSB are 0.63-0.81.
- AM-SSB low-SNR accuracy 0.87-0.95 across all stable models, AM-DSB 0.26-0.32, every other class < 0.34, most digital modulations < 0.10.
- Low-SNR fusion-vs-iq_param_matched gain decomposes: positive on QAM64 (+0.089), 8PSK (+0.022), PAM4 (+0.003); negative on QAM16 (-0.073).

## P2.5 Headline Results (LOW_SNR_WEIGHTED_CE_3090)
- ΔOverall vs Stage 5A: cldnn -0.0233, fusion_iq_stft -0.0067. Mid/high-SNR drops are larger than low-SNR gains.
- ΔLow-SNR vs Stage 5A: cldnn +0.0058, fusion_iq_stft +0.0042. Both positive but small.
- The collapse-to-AM-SSB pattern is not removed; deep low-SNR (-20 to -16 dB) remains at chance level.
- Interpretation: simple group-based SNR-weighted CE shifts the trade-off slightly toward low-SNR but at a larger total cost; not a sufficient remedy.

## A 方案 Headline Results (FUSION_CLDNN_STFT_AUG_LS_3090) — POSITIVE
- 3 seeds × 1 model `fusion_cldnn_stft` (CLDNN-style I/Q encoder + STFT 2D-CNN + fused MLP head). Stacked interventions: phase-rotation + cyclic-time-shift augmentation (train only), label smoothing 0.1, epoch 50 + cosine LR + warmup 5 (same as P1.1).
- Mean overall 0.6264 (std 0.0005); mean low-SNR 0.2258 (std 0.0008); mean mid-SNR 0.8606 (std 0.0009); mean high-SNR 0.9264 (std 0.0003).
- Δ vs Stage 5A CLDNN: overall +0.0135 / low-SNR +0.0034 / mid-SNR +0.0210 / high-SNR +0.0194. **All four positive.**
- Δ vs Stage 5A fusion_iq_stft: +0.0493 overall.
- Δ vs P1.1 fusion_iq_stft (matched schedule): +0.0413 overall.
- Best-epoch 31/42/31; well below 50-cap; schedule appropriate.
- Sits in the cluster of mid-2024 published multi-stream / complex-valued / attention models (CC-MSNet 0.6286, CCTL-Net 0.6297); 1-2 pp below LENet-M 0.6463 / SigFormer 0.6371.
- Deep low-SNR floor (-20 to -16 dB) still at chance level: this is a noise-information limit, not a model-capacity limit, consistent with P1.3 collapse-to-AM-SSB analysis.
- Combination is NOT ablated — three interventions are stacked and we do not yet know per-intervention contribution. Recorded as future-work item.

## In Progress
- A 方案 (`fusion_cldnn_stft + augmentation + label smoothing`) — code + smoke + 3-seed training on RTX 3090, then analysis docs.

## Stage 2 Literature Calibration (key takeaways)
- Real avg-across-SNR SOTA on RML2016.10A: ~0.63-0.65 (LENet-M 0.6463, SigFormer 0.6371, ICRNNA 0.6324, CC-MSNet 0.6286). Our CLDNN 0.6129 is 2-3 pp behind, gap is closeable.
- Architecture interventions consistently delivering +1-2 pp: complex-valued networks (CC-MSNet, CCTL-Net), Transformer/attention hybrids (SigFormer, dual-attention CNN-Transformer), stronger I/Q backbone in fusion.
- Signal-domain augmentation: phase rotation + cyclic time shift are label-preserving for AMC; image-style mixup on I/Q does NOT work (Huang et al. 2022); amplitude scaling and additive noise change effective SNR and conflict with our SNR-conditioned protocol.
- Hyperparameter: label smoothing 0.1 is a cheap +0.3-0.5 pp; LR 1e-3 + batch 256 with warmup + cosine is consistent with literature recipes.
- 95%+ headline figures in industry slides are at high-SNR-only points, not avg-across-SNR; not directly comparable.

## Next
- After A 方案 done: assemble Sections 5.1-5.5, 6, 7 + addendum/sensitivity subsections (5.2.A, 5.4.A, 7.7, 7.8) + new A-plan subsection. Freeze evidence package.
- If A succeeds: positive contribution narrative (fusion can match or beat CLDNN once IQ backbone is upgraded).
- If A fails: stronger triple-intervention negative result; consider complex-valued CLDNN as a further follow-up (`docs/paper/LITERATURE_REVIEW_STAGE2_SOTA_HYPERPARAMS_20260509.md` keeps it as future work).
- All new training must register a new evidence label + new output root before launch; do not modify Stage 5A/5B, P1.1, P2.5, P1.2, P1.3 artefacts.

## Blocked / Needs Explicit Authorization
- Any RadioML2018.01A run, Stage 5A/5B artifact rewrite, or new full-protocol baseline.
- Merging `EXTENDED_BUDGET_3090`, `LOW_SNR_WEIGHTED_CE_3090`, or `CONTROLLED_LATENCY_EXTENDED` rows into the Stage 5A main table or paired-statistical-tests JSON.
- Treating Stage 6B diagnostic outputs as main-table evidence.

## Environment Snapshot
- Local: Windows, Python 3.13.7, PyTorch 2.11.0+cpu, CUDA unavailable.
- Server (active): `/hy-tmp/radioml-amc-stage1` on `i-1.gpushare.com:62244`, Python 3.11.12, PyTorch 2.9.1+cu128, RTX 3090 24 GB, CUDA 12.8 available.
- Server (Stage 5A historical): same software stack on RTX 4070 12 GB; that instance is no longer the active workspace.
