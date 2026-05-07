# Method Design: SNR-Aware Gated Multi-View Fusion Network

## Method Name

SNR-Aware Gated Multi-View Fusion Network.

## Design Status

This is a method draft only. Paper-Stage 0 does not implement model code or run
large-scale training.

## Core Modules

- I/Q raw branch.
- STFT branch.
- Reliability gate.
- Optional SNR auxiliary head.
- Fusion classifier.

## Structure

The model receives raw I/Q samples and an on-the-fly STFT view. The I/Q branch
extracts time-domain features. The STFT branch extracts time-frequency features.
A reliability gate estimates how much each branch should contribute. The fused
feature is passed to the final classifier.

## Data Flow

1. Input raw sample: `x_iq` with shape `[batch, 2, length]`.
2. STFT feature extraction creates `x_stft`.
3. I/Q encoder produces feature `h_iq`.
4. STFT encoder produces feature `h_stft`.
5. Gate module produces branch weight `g`.
6. Fusion combines branch features.
7. Classifier predicts modulation class.
8. Optional auxiliary head predicts SNR group or SNR value during training.

## Inputs and Outputs

Inputs:

- Raw I/Q signal.
- STFT representation.
- Optional SNR label during training for the supervised-gate version.

Outputs:

- Modulation logits.
- Optional SNR logits or SNR regression output.
- Optional gate values for analysis.

## Mathematical Expression

Let:

- `h_iq = f_iq(x_iq)`
- `h_stft = f_stft(x_stft)`
- `g = sigmoid(phi([h_iq, h_stft]))`

The fused feature can be:

```text
h_fused = g * h_stft + (1 - g) * h_iq
y_hat = classifier(h_fused)
```

For vector gates, `g` can have the same feature dimension as `h_iq` and
`h_stft`. For scalar gates, `g` is one value per sample.

## Version 1: SNR-Supervised Gate

The gate receives training supervision from known SNR labels or SNR groups.

Possible design:

- Predict SNR group: low, mid, high.
- Use auxiliary loss `L_snr`.
- Total loss:

```text
L = L_cls + lambda_snr * L_snr
```

Expected behavior:

- Increase STFT contribution in low-SNR regions if evidence supports it.
- Preserve I/Q dominance in high-SNR regions.

Risk:

- The model may overfit to dataset-specific SNR annotations.
- Real deployments may not have accurate SNR labels.

## Version 2: SNR-Free Reliability Gate

The gate learns branch reliability without SNR labels.

Possible design:

- Gate input is `[h_iq, h_stft, |h_iq - h_stft|, h_iq * h_stft]`.
- Train only with classification loss.
- Analyze gate values by SNR after training.

Expected behavior:

- Learn sample-level branch confidence without requiring SNR at inference.
- Avoid depending on explicit SNR labels.

Risk:

- The learned gate may collapse to one branch.
- Additional regularization or entropy constraints may be needed.

## Why This May Address the Current Trade-Off

The current `fusion_iq_stft` model improves low-SNR accuracy slightly but reduces
overall, mid-SNR, and high-SNR accuracy. This suggests that STFT information may
be useful only in selected conditions. A reliability gate can reduce harmful STFT
contribution when raw I/Q features are already sufficient and increase it when
low-SNR samples need complementary structure.

## Suggested Future Implementation Files

- `src/radioml_amc/models/gated_fusion.py`
- `src/radioml_amc/models/fusion_blocks.py`
- `scripts/train_gated_fusion.py`
- `scripts/run_paper_ablations.py`
- `configs/paper/rml2016a_gated_fusion_subset.yaml`
- `configs/paper/rml2016a_gated_fusion_full.yaml`

## Risks

- Low-SNR gains may remain too small for publication.
- Gate learning may be unstable under single-seed training.
- Added complexity may not justify the accuracy gain.
- On-the-fly STFT may dominate inference latency.
- SNR-supervised variants may be less realistic for deployment.
