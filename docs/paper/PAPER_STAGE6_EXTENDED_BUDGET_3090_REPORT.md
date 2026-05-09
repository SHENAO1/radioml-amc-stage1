# Paper-Stage 6 Extended Budget RTX 3090 Training Report

Date: 2026-05-09T12:44:57
Server repo: `/hy-tmp/radioml-amc-stage1`
Dataset: RadioML2016.10A only
Split: `stratified_by_mod_snr_seed42` from `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
Evidence label: `EXTENDED_BUDGET_3090`
Hardware: RTX 3090 24GB (Ampere sm_86), CUDA 12.8, PyTorch 2.9.1+cu128
Conclusion: GO

## Protocol

- Same fixed split as Stage 5A; train seeds restricted to `42`, `2025`, `3407`.
- Epochs lifted from 20 to 50; cosine LR with 5-epoch linear warmup; early-stop patience 15.
- This evidence is separated from Stage 5A/5B (different RESULT_ROOT, REPORT_PATH).
- Hardware changed from RTX 4070 (Ada) to RTX 3090 (Ampere); annotate in any paper claim.

## Completion

- Completed cells: 12/12
- Failed or incomplete cells: 0

| Model | Seed | Status | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Best Epoch | Run Dir |
|---|---:|---|---:|---:|---:|---:|---:|---|
| cldnn | 42 | completed | 0.6132727272727273 | 0.22113636363636363 | 0.8437121212121212 | 0.9056818181818181 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/cldnn/seed_42` |
| cldnn | 2025 | completed | 0.6163863636363637 | 0.22357954545454545 | 0.845 | 0.9115151515151515 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/cldnn/seed_2025` |
| cldnn | 3407 | completed | 0.6137727272727272 | 0.22142045454545456 | 0.8424242424242424 | 0.9082575757575757 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/cldnn/seed_3407` |
| resnet1d | 42 | completed | 0.5978863636363636 | 0.210625 | 0.8190909090909091 | 0.8930303030303031 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/resnet1d/seed_42` |
| resnet1d | 2025 | completed | 0.59575 | 0.2044318181818182 | 0.8233333333333334 | 0.8899242424242424 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/resnet1d/seed_2025` |
| resnet1d | 3407 | completed | 0.5953636363636363 | 0.20113636363636364 | 0.8234090909090909 | 0.8929545454545454 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/resnet1d/seed_3407` |
| iq_param_matched | 42 | completed | 0.5989545454545454 | 0.21693181818181817 | 0.8177272727272727 | 0.8895454545454545 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/iq_param_matched/seed_42` |
| iq_param_matched | 2025 | completed | 0.6029545454545454 | 0.2149431818181818 | 0.8278787878787879 | 0.8953787878787879 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/iq_param_matched/seed_2025` |
| iq_param_matched | 3407 | completed | 0.6014318181818182 | 0.21085227272727272 | 0.8278030303030303 | 0.8958333333333334 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/iq_param_matched/seed_3407` |
| fusion_iq_stft | 42 | completed | 0.5843863636363636 | 0.21556818181818183 | 0.7987121212121212 | 0.8618181818181818 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft/seed_42` |
| fusion_iq_stft | 2025 | completed | 0.5877954545454546 | 0.20897727272727273 | 0.8097727272727273 | 0.8709090909090909 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft/seed_2025` |
| fusion_iq_stft | 3407 | completed | 0.5831136363636363 | 0.21267045454545455 | 0.798939393939394 | 0.8612121212121212 | None | `/hy-tmp/radioml-amc-stage1/results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft/seed_3407` |

## Failures

- None.
