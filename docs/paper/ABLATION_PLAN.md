# Ablation Plan

## Purpose

This file defines planned SCI-track ablations. Do not run these experiments in
Paper-Stage 0.

## Baseline Experiments

| Experiment | Purpose | Expected cost | Subset first | Full server needed | Acceptance metric |
|---|---|---:|---|---|---|
| CNN1D | Lightweight I/Q baseline | Low | Yes | Yes | Reproduce known full baseline within expected seed variance |
| ResNet1D | Strong I/Q baseline | Low to medium | Yes | Yes | Maintain best or near-best overall baseline |
| TF-CNN STFT | Isolate STFT-only value | Medium | Yes | Yes | Determine whether STFT alone helps low SNR |
| fusion_iq_stft | Static fusion reference | Medium | Yes | Yes | Reproduce current low-SNR/overall trade-off |

## Proposed Experiments

| Experiment | Purpose | Expected cost | Subset first | Full server needed | Acceptance metric |
|---|---|---:|---|---|---|
| gated_fusion_iq_stft | Test adaptive fusion | Medium | Yes | Yes | Improve low-SNR accuracy without overall drop versus `fusion_iq_stft` |
| gated_fusion_iq_stft + low_snr_weighted_loss | Emphasize noisy samples | Medium | Yes | Yes | Improve low-SNR mean accuracy with bounded overall loss |
| gated_fusion_iq_stft + snr_balanced_sampler | Reduce SNR imbalance effects | Medium | Yes | Yes | Improve per-SNR stability and low-SNR group accuracy |
| gated_fusion_iq_stft + augmentation | Improve robustness | Medium to high | Yes | Yes | Improve multi-seed robustness and reduce overfitting |

## Mechanism Ablations

| Ablation | Purpose | Expected cost | Subset first | Full server needed | Acceptance metric |
|---|---|---:|---|---|---|
| no gate | Confirm static fusion baseline | Medium | Yes | Yes | Match `fusion_iq_stft` behavior |
| fixed gate | Test hand-designed branch weighting | Medium | Yes | Optional | Identify whether simple SNR-based weights are enough |
| learned gate | Test adaptive branch weighting | Medium | Yes | Yes | Better low-SNR/overall trade-off than no gate |
| SNR-supervised gate | Use known SNR labels during training | Medium | Yes | Yes | Gate values align with SNR groups and improve low-SNR results |
| SNR-free gate | Avoid SNR labels at inference | Medium | Yes | Yes | Comparable gain without SNR supervision |
| without STFT branch | Verify branch contribution | Low | Yes | Yes | Reduce to I/Q behavior and expose STFT contribution |
| without weighted loss | Isolate loss effect | Medium | Yes | Yes | Quantify weighted-loss contribution |
| without sampler | Isolate sampler effect | Medium | Yes | Yes | Quantify SNR-balanced sampler contribution |

## Reporting Rules

- Run subset experiments only for screening and debugging.
- Promote only promising and stable designs to full runs.
- Keep per-seed raw results.
- Report mean and standard deviation for main tables.
- Include complexity and latency for each proposed variant.
- Do not treat small single-seed gains as final conclusions.
