# Paper-Stage 6 SNR-Aware Weighted CE (RTX 3090) Training Report

Date: 2026-05-09T13:56:53
Server repo: `/hy-tmp/radioml-amc-stage1`
Dataset: RadioML2016.10A only
Split: `stratified_by_mod_snr_seed42` from `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
Evidence label: `LOW_SNR_WEIGHTED_CE_3090`
Loss: SnrWeightedCrossEntropy(scheme=group, low=2.0, mid=1.0, high=0.7).
Hardware: RTX 3090 (Ampere sm_86), CUDA 12.8, PyTorch 2.9.1+cu128.
Conclusion: GO

## Completion

- Completed cells: 6/6
- Failed or incomplete cells: 0

| Model | Seed | Status | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Best Epoch | Run Dir |
|---|---:|---|---:|---:|---:|---:|---:|---|
| cldnn | 42 | completed | 0.5970227272727273 | 0.22477272727272726 | 0.8075757575757576 | 0.8828030303030303 | 23 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/cldnn/seed_42` |
| cldnn | 2025 | completed | 0.5707272727272727 | 0.2318181818181818 | 0.7673484848484848 | 0.8259848484848484 | 15 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/cldnn/seed_2025` |
| cldnn | 3407 | completed | 0.6009545454545454 | 0.2277840909090909 | 0.8125757575757576 | 0.8868939393939393 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/cldnn/seed_3407` |
| fusion_iq_stft | 42 | completed | 0.5708863636363637 | 0.22767045454545454 | 0.7680303030303031 | 0.8313636363636364 | 13 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/fusion_iq_stft/seed_42` |
| fusion_iq_stft | 2025 | completed | 0.5695 | 0.2240909090909091 | 0.7649242424242424 | 0.8346212121212121 | 12 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/fusion_iq_stft/seed_2025` |
| fusion_iq_stft | 3407 | completed | 0.5709772727272727 | 0.22460227272727273 | 0.7706060606060606 | 0.8331818181818181 | 13 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/fusion_iq_stft/seed_3407` |

## Failures

- None.
