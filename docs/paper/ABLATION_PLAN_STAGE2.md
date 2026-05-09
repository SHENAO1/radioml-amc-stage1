# Ablation Plan for Paper-Stage 2

Date: 2026-05-07

Purpose: define ablations required to determine whether SNR-aware lightweight
multi-view fusion is a real contribution or only a parameter/preprocessing
artifact.

## Ablation Priorities

| Priority | Meaning |
|---|---|
| A0 | Required before implementing gated fusion full runs |
| A1 | Required for main paper claims |
| A2 | Strongly recommended for appendix or rebuttal |
| A3 | Optional future work |

## Required Ablation Matrix

| Ablation | Priority | Main or appendix | Purpose | Comparison target | Expected cost | Decision criterion |
|---|---:|---|---|---|---|---|
| I/Q only | A0 | Main | Anchor raw-signal behavior | ResNet1D and parameter-matched I/Q model | low | Must remain strongest simple reference |
| STFT only | A0 | Main/appx | Isolate time-frequency branch value | TF-CNN STFT versus I/Q | medium | Shows whether STFT alone has low-SNR utility |
| Static I/Q + STFT fusion | A0 | Main | Reproduce current trade-off | `fusion_iq_stft` | medium | Must be beaten by any gate |
| Parameter-matched I/Q baseline | A0 | Main | Control extra parameter count | proposed gate | low to medium | If it matches gate, multi-view claim weakens |
| Gated fusion without SNR input | A1 | Main | Test reliability gating without explicit SNR labels | static fusion and I/Q baselines | medium | Preferred deployable variant if stable |
| Gated fusion with true SNR input | A1 | Main/appx | Upper-bound SNR-aware gating with oracle SNR | SNR-free gate | medium | Useful but deployment claim must be limited |
| Gated fusion with noisy/estimated SNR | A1 | Main/appx | Test realism when SNR is imperfect | true-SNR gate | medium | Robustness to SNR error required for practical claim |
| Low-SNR weighted loss | A1 | Main/appx | Test whether gains come from training objective rather than gate | standard CE | medium | Include only if it improves low-SNR without large overall loss |
| SNR-balanced sampler | A1 | Main/appx | Stabilize per-SNR learning | random sampler | medium | Helps if low-SNR variance decreases |
| Gate regularization | A1 | Appendix | Avoid gate collapse and improve interpretability | unregularized gate | low | Gate should not collapse unless collapse improves accuracy |
| Branch dropout | A2 | Appendix | Prevent over-reliance on one branch | no branch dropout | medium | Keep only if improves seed stability |
| Cached STFT vs on-the-fly STFT | A1 | Complexity table | Separate model accuracy from preprocessing cost | same model, different feature path | measurement cost | Required for lightweight claim |
| Low-SNR boundary sensitivity | A2 | Appendix | Test whether claim depends on arbitrary group boundary | `snr <= -8`, `snr <= -6`, `snr <= -4` | low after predictions exist | Claim is stronger if robust to boundary |
| Gate scalar vs vector gate | A2 | Appendix | Determine whether per-feature gating is needed | scalar gate | medium | Prefer scalar if similar accuracy and lower cost |
| STFT hyperparameter sensitivity | A2 | Appendix | Test representation dependence | different `nperseg/noverlap` | medium | Avoid overclaiming one transform setting |
| Late-logit ensemble | A2 | Appendix | Separate gate value from generic ensembling | I/Q plus STFT ensemble | low if models exist | Gate should beat or simplify ensemble |

## Stage Ordering

### Stage 2A: Infrastructure Ablations

Do before gated-fusion full runs:

1. fixed split artifact;
2. sample-level prediction logging;
3. main metric aggregation;
4. complexity and latency measurement;
5. current CNN1D, ResNet1D, TF-CNN STFT, and static fusion through the V2
   reporting path.

Promotion criterion:

- Existing current results can be reproduced within expected seed variance and
  saved with the new schemas.

### Stage 2B: Baseline Completion

Do before strong method claims:

1. CLDNN or CNN-LSTM;
2. MCLDNN;
3. LWAMCNet or MCNet;
4. parameter-matched I/Q-only model.

Promotion criterion:

- Proposed method must be compared against at least ResNet1D, MCLDNN, static
  fusion, and parameter-matched I/Q-only.

### Stage 2C: Gated Fusion Mechanism

Run in this order:

1. SNR-free scalar gate.
2. SNR-free vector gate only if scalar gate underfits.
3. True-SNR gate as an upper-bound/reference.
4. Noisy/estimated-SNR gate if true-SNR gate looks promising.
5. Gate regularization and branch dropout only if collapse or instability is
   observed.

Promotion criterion:

- The gate must improve low-SNR mean accuracy over static fusion and strong I/Q
  baselines while controlling mid/high-SNR degradation.

### Stage 2D: Robustness and Rebuttal Ablations

Run after the primary mechanism survives:

1. low-SNR boundary sensitivity;
2. STFT hyperparameter sensitivity;
3. late-logit ensemble;
4. denoising/shrinkage baseline;
5. lightweight complex-valued baseline.

## Reporting Template

Each ablation row should report:

- overall accuracy mean/std;
- low/mid/high-SNR accuracy mean/std;
- low-SNR macro-F1 mean/std;
- parameters;
- FLOPs/MACs;
- GPU latency including and excluding preprocessing;
- CPU latency including preprocessing;
- gate statistics if applicable;
- reviewer interpretation.

## Failure Interpretation

If the gate improves low SNR but reduces overall accuracy:

- report the result as an operating-region trade-off;
- avoid claiming universal superiority;
- consider an SNR-triggered deployment policy;
- compare directly to static fusion to show whether the gate at least improves
  the trade-off.

If parameter-matched I/Q matches the gate:

- the multi-view contribution is not established;
- reframe around architecture efficiency only if complexity is favorable;
- otherwise stop the method direction.

If STFT-only is weak and fusion is weak:

- STFT may not be the right auxiliary view;
- consider amplitude/phase or learned spectral filters before adding CWT;
- do not add CWT full runs until preprocessing cost is controlled.

## Evidence Classification

Project-supported:

- Static fusion currently shows a low-SNR/overall trade-off on one seed.

Literature-supported:

- Stronger baselines, time-frequency views, attention, lightweight networks, and
  SNR-aware learning are known comparison families.

Hypotheses:

- Any gate, loss, sampler, or branch regularizer will improve the trade-off.

