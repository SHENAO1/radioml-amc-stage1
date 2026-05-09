# Paper-Stage 6 fusion_cldnn_stft + Aug + LabelSmoothing (RTX 3090) Training Report

Date: 2026-05-09T14:58:26
Server repo: `/hy-tmp/radioml-amc-stage1`
Dataset: RadioML2016.10A only
Split: `stratified_by_mod_snr_seed42` from `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
Evidence label: `FUSION_CLDNN_STFT_AUG_LS_3090`
Architecture: CLDNN-style I/Q encoder + STFT 2D-CNN branch + fused MLP head.
Augmentation (train only): phase rotation theta~U(-pi,pi) prob 0.5; cyclic time shift k~U(-8,+8) prob 0.5.
Loss: nn.CrossEntropyLoss(label_smoothing=0.1).
Hardware: RTX 3090 (Ampere sm_86), CUDA 12.8, PyTorch 2.9.1+cu128.
Conclusion: GO

## Completion

- Completed cells: 3/3
- Failed or incomplete cells: 0

| Model | Seed | Status | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Best Epoch | Run Dir |
|---|---:|---|---:|---:|---:|---:|---:|---|
| fusion_cldnn_stft | 42 | completed | 0.6269545454545454 | 0.22613636363636364 | 0.8615909090909091 | 0.9267424242424243 | 31 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_42` |
| fusion_cldnn_stft | 2025 | completed | 0.6263863636363637 | 0.22642045454545454 | 0.86 | 0.926060606060606 | 42 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_2025` |
| fusion_cldnn_stft | 3407 | completed | 0.6259772727272728 | 0.225 | 0.8603030303030303 | 0.9262878787878788 | 31 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft/seed_3407` |

## Failures

- None.
