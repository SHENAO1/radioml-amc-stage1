# Paper-Stage 6 Low-SNR Weighted-CE Analysis (P2.5)

Date: 2026-05-09
Evidence label: `LOW_SNR_WEIGHTED_CE_3090`
Auto-generated report: [`PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md`](PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md)
Status JSON: `results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/status.json`
Wall time: 22.8 minutes (6 cells)

## Scope

This addendum tests whether replacing plain cross-entropy with an SNR-group-weighted cross-entropy (low / mid / high weights = 2.0 / 1.0 / 0.7) shifts the overall-vs-low-SNR trade-off documented in Section 5.2. All other training hyperparameters match the P1.1 extended-budget run (epoch 50, 5-epoch warmup, cosine LR, early-stop patience 15, AdamW). Output goes to a new evidence label and a new output root so neither Stage 5A/5B nor P1.1 artefacts are modified.

Only the two models whose low-SNR behaviour is explicitly discussed in the manuscript are evaluated: `cldnn` (strongest stable baseline) and `fusion_iq_stft` (multi-view candidate). The remaining seven Stage 5A model rows are not retrained under this loss; their main-table behaviour continues to come from Stage 5A/5B.

## Aggregate Comparison (mean across 3 seeds)

| Model | Branch | Overall | Low-SNR | Mid-SNR | High-SNR |
|---|---|---:|---:|---:|---:|
| cldnn | Stage 5A (CE, ep20, 4070) | 0.6129 | 0.2224 | 0.8396 | 0.9070 |
| cldnn | P1.1 (CE, ep50 cosine, 3090) | 0.6145 | 0.2220 | 0.8437 | 0.9085 |
| **cldnn** | **P2.5 (weighted CE, ep50 cosine, 3090)** | **0.5896** | **0.2281** | **0.7958** | **0.8652** |
| Δ vs Stage 5A |  | -0.0233 | +0.0058 | -0.0438 | -0.0418 |
| Δ vs P1.1 |  | -0.0249 | +0.0061 | -0.0479 | -0.0432 |
| fusion_iq_stft | Stage 5A (CE, ep20, 4070) | 0.5771 | 0.2213 | 0.7858 | 0.8428 |
| fusion_iq_stft | P1.1 (CE, ep50 cosine, 3090) | 0.5851 | 0.2124 | 0.8025 | 0.8646 |
| **fusion_iq_stft** | **P2.5 (weighted CE, ep50 cosine, 3090)** | **0.5704** | **0.2255** | **0.7679** | **0.8331** |
| Δ vs Stage 5A |  | -0.0067 | +0.0042 | -0.0179 | -0.0097 |
| Δ vs P1.1 |  | -0.0147 | +0.0131 | -0.0346 | -0.0315 |

P2.5 best-epoch distributions: cldnn 23 / 15 / 20; fusion_iq_stft 13 / 12 / 13. The fusion-side best epochs are notably earlier than under plain CE (P1.1: 34 / 42 / 36), which suggests the weighted loss makes the model fit its hardest examples sooner and then plateau.

## Findings

1. **The intended low-SNR shift is real but small.** For both models, the low-SNR aggregate moves up by ~0.6 pp (cldnn) and ~0.4 pp (fusion vs Stage 5A) / ~1.3 pp (fusion vs P1.1). The direction is consistent across all three seeds for both models, supporting the claim that low-SNR-weighted gradient does shift the model toward harder examples.

2. **The cost in mid- and high-SNR is much larger than the gain.** cldnn loses 4.4 pp at mid-SNR and 4.2 pp at high-SNR; fusion loses 1.8 pp and 1.0 pp. Net overall accuracy drops 2.3 pp for cldnn and 0.7 pp for fusion. Within this matrix, the cost-benefit of group-based weighted CE is unfavourable.

3. **The collapse-to-AM-SSB pattern is not removed.** A look at the per-SNR accuracy curve for cldnn seed 42 shows that gains concentrate in the SNR transition zone (-8 dB → 0.395 vs typical 0.30, -6 dB → 0.519 vs typical 0.43). The deep low-SNR floor (snr_db ∈ {-20, -18, -16}) remains at chance level (~0.09–0.11). Re-weighting by 2x is therefore not enough to extract additional signal from samples where the noise is already overwhelming.

4. **Fusion benefits more in low-SNR than CLDNN does, but both lose in mid/high.** Fusion's low-SNR gain over its own P1.1 baseline is +1.31 pp (vs CLDNN's +0.61 pp), and its overall loss is smaller (-1.47 pp vs CLDNN's -2.49 pp). This is consistent with the static fusion model already being closer to low-SNR-optimal under plain CE, leaving more headroom for re-weighting on harder digital-modulation examples.

5. **Best-epoch shifts earlier for fusion.** Under plain CE (P1.1) fusion's best epoch was 34 / 42 / 36; under weighted CE (P2.5) it dropped to 13 / 12 / 13. The weighted loss accelerates fitting the harder examples but the model then begins to overfit them and validation accuracy stalls. This suggests that combining weighted CE with a longer schedule does not buy further gains; the shift happens early and stops.

## Interpretation For The Research Question

The headline claim from this experiment is **negative for the simple-loss-reweighting intervention as a path to bridge the low-SNR / overall trade-off**. Specifically:

- Under group-based weighted CE with weights (low=2, mid=1, high=0.7), neither cldnn nor fusion_iq_stft beats Stage 5A overall accuracy.
- Both models gain low-SNR aggregate accuracy by less than 1.5 pp on top of Stage 5A.
- The low-SNR collapse-to-AM-SSB pattern (P1.3 evidence) is not removed; only the SNR transition zone shifts.

This evidence does **not** rule out future SNR-aware techniques (per-class weighted CE, SNR-aware Focal loss, complex-valued models, denoising augmentation, or curriculum sampling). It does rule out the simplest version of the idea — uniform 2x weight on low-SNR samples — under the registered protocol.

For the manuscript, this experiment can be reported as a single sensitivity / intervention check in Section 7, alongside the P1.1 budget-extension check. It strengthens the limitations narrative because the project tested both natural extensions of the Stage 5A protocol (longer training; SNR-weighted loss) and confirmed that neither intervention recovers the low-SNR collapse.

## Allowed Statements

- Under matched extended-budget conditions on RTX 3090, group-based SNR-weighted CE moves the low-SNR aggregate up by a small amount (~0.4 to 1.3 pp) for `cldnn` and `fusion_iq_stft`, but at a larger overall and mid/high-SNR cost.
- The improvement is concentrated in the SNR transition zone (-8 to -4 dB); the deep-low-SNR floor remains at chance level.
- Best-epoch shifts earlier for `fusion_iq_stft` under the weighted loss, indicating faster convergence on the up-weighted samples.

## Disallowed Statements

- This evidence does not let us claim that *any* SNR-aware loss is ineffective; only that the registered group-based variant with weights (2.0, 1.0, 0.7) is. Different weights, different boundaries, focal-style scaling, or sample-level SNR weighting are not tested.
- This evidence does not justify replacing or recomputing the Stage 5A main table or low-SNR table.
- The hardware change (4070 → 3090) prevents direct paired statistical comparison against Stage 5A predictions.

## Future Work (If Pursued)

- **More aggressive low-SNR weight** (e.g., 3 / 1 / 0.5) to confirm the cost curve is not just a local minimum.
- **Continuous SNR weight** `w(snr) = exp(-alpha * snr_db / 10)`, which the loss factory already supports via `scheme: continuous`.
- **Per-(class, SNR) weighting**, biased toward digital modulations that suffer the most at low SNR (8PSK, BPSK, QPSK, CPFSK, GFSK).
- **SNR-balanced sampler** (oversample low-SNR examples) instead of loss reweighting; preserves loss magnitude.
- **Combine with augmentation** (phase rotation, time shift) to target low-SNR distortion robustness.

These remain in the queue but are not authorized by the current protocol.

## Artefact Paths

- Server runs: `/hy-tmp/radioml-amc-stage1/results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/<model_id>/seed_<train_seed>/`
- Per-cell required artifacts: same as Stage 5A protocol, plus `low_snr_weighted_ce_run_status.json`.
- Aggregate status: `results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/status.json`
- Auto-generated report: [`PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md`](PAPER_STAGE6_LOW_SNR_WEIGHTED_CE_3090_REPORT.md).

## Required Local Sync If Future Work Needs Weights

The 6 P2.5 `best_model.pt` files remain on the server (`results/paper_stage6/low_snr_weighted_ce_3090/rml2016a/<model_id>/seed_<train_seed>/best_model.pt`). They have not been pulled to local. Same archival policy applies as Stage 5A and P1.1: pull into a separate archive path with hash check; do not overwrite `results/`.
