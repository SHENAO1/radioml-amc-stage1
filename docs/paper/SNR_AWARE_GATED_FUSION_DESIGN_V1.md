# SNR-Aware Gated Fusion Design V1

Date: 2026-05-07

Purpose: define the smallest scientifically testable gated-fusion design. This
is not an implementation request and does not change model code.

## Design Goal

The method should test one narrow hypothesis:

> A lightweight gate can selectively use a time-frequency view under low-SNR
> conditions while preserving the stronger raw-I/Q behavior at mid/high SNR.

It should not be positioned as generic fusion superiority.

## Minimal Architecture

Inputs:

- `x_iq`: raw I/Q tensor `[batch, 2, length]`;
- `x_stft`: STFT tensor `[batch, 1, freq_bins, time_frames]`;
- optional `snr_db` or `snr_group` during training and selected experiments.

Encoders:

- I/Q encoder: reuse the current ResNet1D-style or lightweight I/Q backbone for
  the reference path.
- STFT encoder: use a compact 2D CNN branch.
- Feature dimensions should be projected to a shared dimension before gating.

Projection:

```text
z_iq = proj_iq(h_iq)
z_tf = proj_tf(h_stft)
```

Scalar gate:

```text
g = sigmoid(MLP([z_iq, z_tf, abs(z_iq - z_tf), z_iq * z_tf, optional_snr]))
h = (1 - g) * z_iq + g * z_tf
logits = classifier(h)
```

Vector gate:

```text
g_vec = sigmoid(MLP([...]))
h = (1 - g_vec) * z_iq + g_vec * z_tf
```

Start with scalar gate. Use vector gate only if scalar gate cannot model the
trade-off.

## Variants to Test

| Variant | SNR at train | SNR at inference | Purpose | Claim strength |
|---|---|---|---|---|
| SNR-free reliability gate | no | no | deployable main candidate | strongest practical claim if successful |
| True-SNR gate | yes | yes | oracle/reference upper bound | limited deployment claim |
| Noisy-SNR gate | yes | noisy estimate | realism check | useful if true-SNR gate works |
| SNR auxiliary head | SNR label as auxiliary target | no SNR input | learns SNR-aware representation without requiring SNR at inference | good compromise |
| Static fusion | no | no | baseline | not proposed method |

## Losses

Base loss:

```text
L = L_cls
```

Optional auxiliary SNR loss:

```text
L = L_cls + lambda_snr * L_snr
```

Optional gate regularization:

```text
L = L_cls + lambda_entropy * L_gate_entropy + lambda_balance * L_gate_balance
```

Rules:

- Keep `lambda_snr`, `lambda_entropy`, and `lambda_balance` in a small grid.
- Do not tune on the test set.
- Report whether the gate collapses to I/Q or STFT.

## Gate Logging

Required gate analysis:

- mean gate value by SNR;
- standard deviation of gate value by SNR;
- mean gate value by modulation class;
- mean gate value by correctness;
- gate distribution for low/mid/high SNR;
- correlation between gate value and model confidence;
- correlation between gate value and SNR.

Expected behavior if the hypothesis is true:

- low-SNR samples should use more STFT information than high-SNR samples;
- high-SNR samples should retain strong I/Q behavior;
- gate values should vary by sample, not collapse to a constant.

Do not force this behavior in the claim. Treat it as evidence to be observed.

## Complexity Constraints

For a lightweight claim:

- parameter count target: no more than `1.5x` ResNet1D;
- full inference latency target: no more than `2x` ResNet1D including STFT;
- STFT cache size must be reported if cached;
- on-the-fly STFT must be reported as part of end-to-end latency.

If the method misses these targets:

- remove "lightweight" from the central claim or reframe as a robustness-cost
  trade-off.

## Go Criteria

Continue to full Stage 2 runs only if subset/full pilot evidence shows:

- low-SNR accuracy exceeds ResNet1D and static fusion;
- low-SNR accuracy is competitive with or better than MCLDNN-style baseline;
- mid-SNR and high-SNR degradation versus ResNet1D are each within `0.01`
  absolute accuracy, or the method is explicitly framed as low-SNR-only;
- overall accuracy is at least ResNet1D minus `0.005`;
- the gate beats the parameter-matched I/Q-only baseline;
- gate behavior is nontrivial and analyzable;
- complexity remains within the lightweight budget.

## No-Go Criteria

Stop or reframe if:

- low-SNR gain is smaller than seed variance;
- static fusion is as good as gated fusion;
- a parameter-matched I/Q-only baseline is as good as gated fusion;
- gate values collapse and cannot be interpreted;
- STFT preprocessing cost dominates deployment latency;
- the method improves only a narrow SNR slice and hurts most other regions.

## Paper Framing After Results

If all go criteria pass:

- Frame as lightweight reliability-aware multi-view fusion for low-SNR robust
  AMC with bounded complexity.

If low SNR improves but overall drops:

- Frame as low-SNR operating-mode adaptation.
- State explicitly that the method trades overall accuracy for low-SNR
  robustness.
- Do not claim broad superiority.

If the gate fails but static fusion still shows low-SNR value:

- Reframe as an empirical analysis paper only if evidence is strong and
  literature positioning remains valid.

If no multi-seed low-SNR gain remains:

- Stop the SNR-aware fusion paper direction and keep the result as negative
  evidence for the project report.

## Implementation Readiness

Do not implement full gated fusion until:

- fixed split artifacts exist;
- V2 prediction logging exists;
- existing baselines can write the V2 metric schema;
- STFT preprocessing latency can be measured;
- at least one stronger baseline is planned in the same harness.

Recommended next implementation sequence:

1. result schema and split artifact tooling;
2. complexity/latency measurement tooling;
3. reproduce existing baselines through the V2 harness;
4. add CLDNN/MCLDNN/LWAMCNet or one strong baseline;
5. implement scalar SNR-free gate;
6. add true-SNR and noisy-SNR variants only if the scalar gate has a signal.

