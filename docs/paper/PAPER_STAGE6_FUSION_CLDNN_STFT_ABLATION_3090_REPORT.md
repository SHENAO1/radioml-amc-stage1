# Paper-Stage 6 fusion_cldnn_stft Ablation (RTX 3090) Training Report

Date: 2026-05-09T21:07:46
Server repo: `/hy-tmp/radioml-amc-stage1`
Dataset: RadioML2016.10A only
Split: `stratified_by_mod_snr_seed42` from `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
Evidence label: `FUSION_CLDNN_STFT_ABLATION_3090`
Variants: arch_only, arch_aug, arch_ls; same fixed split + 3 seeds + RTX 3090 hardware as A 方案.

| Variant | Seed | Status | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Best Epoch | Run Dir |
|---|---:|---|---:|---:|---:|---:|---:|---|
| arch_only | 42 | completed | 0.6102727272727273 | 0.21278409090909092 | 0.8406818181818182 | 0.9098484848484848 | 22 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_only/fusion_cldnn_stft/seed_42` |
| arch_only | 2025 | completed | 0.6146363636363636 | 0.221875 | 0.8417424242424243 | 0.9112121212121213 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_only/fusion_cldnn_stft/seed_2025` |
| arch_only | 3407 | completed | 0.609840909090909 | 0.2172159090909091 | 0.8374242424242424 | 0.9057575757575758 | 22 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_only/fusion_cldnn_stft/seed_3407` |
| arch_aug | 42 | completed | 0.6272727272727273 | 0.22573863636363636 | 0.8639393939393939 | 0.9259848484848485 | 36 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_aug/fusion_cldnn_stft/seed_42` |
| arch_aug | 2025 | completed | 0.6280454545454546 | 0.22363636363636363 | 0.8686363636363637 | 0.9266666666666666 | 43 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_aug/fusion_cldnn_stft/seed_2025` |
| arch_aug | 3407 | completed | 0.6298181818181818 | 0.22676136363636365 | 0.868030303030303 | 0.9290151515151515 | 45 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_aug/fusion_cldnn_stft/seed_3407` |
| arch_ls | 42 | completed | 0.6117045454545454 | 0.21880681818181819 | 0.8428787878787879 | 0.9043939393939394 | 16 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_ls/fusion_cldnn_stft/seed_42` |
| arch_ls | 2025 | completed | 0.6093636363636363 | 0.21272727272727274 | 0.8437878787878788 | 0.9037878787878788 | 21 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_ls/fusion_cldnn_stft/seed_2025` |
| arch_ls | 3407 | completed | 0.6112045454545455 | 0.21420454545454545 | 0.8438636363636364 | 0.9078787878787878 | 16 | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_ls/fusion_cldnn_stft/seed_3407` |
