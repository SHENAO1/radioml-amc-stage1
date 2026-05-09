# Baseline Matrix for Paper-Stage 2

Date: 2026-05-07

Purpose: define which baselines are necessary before any SCI-level claim about
SNR-aware lightweight multi-view fusion. This is a planning document only.

## Priority Levels

| Priority | Meaning |
|---|---|
| P0 | Already present or required to reproduce current evidence |
| P1 | Must be added for a credible main-table comparison |
| P2 | Strongly recommended if compute and implementation time permit |
| P3 | Appendix or future validation |

## Baseline Matrix

| Baseline | Priority | Main or appendix | Why it is needed | Input representation | Expected cost | New model code? | Fit current compute? | Review risk if omitted |
|---|---:|---|---|---|---|---|---|---|
| CNN1D | P0 | Main | Lightweight raw I/Q reference and current project baseline | raw I/Q `[2, L]` | low | no | yes | Low, if ResNet1D is included; still useful for continuity |
| ResNet1D | P0 | Main | Current best overall model and strongest local reference | raw I/Q `[2, L]` | low to medium | no | yes | Severe, because all proposed claims must beat or bound against it |
| TF-CNN STFT | P0 | Main or appendix | Isolates STFT-only value from fusion value | STFT image `[1, F, T]` | medium due to preprocessing | no or minor config | yes if STFT cached/measured | Medium; without it branch contribution is ambiguous |
| `fusion_iq_stft` static fusion | P0 | Main | Current static fusion reference and observed low-SNR/overall trade-off | raw I/Q plus STFT | medium | no | yes if STFT cost controlled | Severe; gated fusion must beat static fusion |
| CLDNN or CNN-LSTM | P1 | Main | Standard AMC temporal baseline; addresses reviewer expectation beyond CNN/ResNet | raw I/Q, optional amplitude/phase | medium | yes | yes on RML2016A | High; reviewers know recurrent/hybrid AMC baselines |
| MCLDNN | P1 | Main | Widely used multi-channel AMC baseline using I, Q, and I/Q streams | I stream, Q stream, I/Q stream | medium | yes | yes on RML2016A | Severe; a low-SNR fusion claim is weak without it |
| LWAMCNet | P1 | Main | Lightweight CNN baseline with deployment-aware prior art | raw I/Q | low | yes | yes | High for a lightweight paper |
| Parameter-matched I/Q-only model | P1 | Main | Controls whether gains come from extra parameters instead of multi-view information | raw I/Q | matched to fusion | yes or config variant | yes | Severe; otherwise fusion gain may be parameter-count artifact |
| Late-logit ensemble | P1 | Appendix, promote if strong | Separates learned gate benefit from generic ensembling | separate I/Q and STFT logits | medium to high | minor wrapper | yes if both models exist | Medium; useful to show gate is not just ensembling |
| HFECNET-CA | P2 | Main if implemented, otherwise appendix/referenced | Lightweight attention competitor from recent literature | raw I/Q | low to medium | yes | yes | Medium to high for attention-aware reviewers |
| SE-MSFN simplified | P2 | Appendix or main if stable | Multi-scale SE attention baseline for RadioML2018.01A-style literature | raw I/Q | medium | yes | likely | Medium; omission acceptable if HFECNET-CA included |
| Lightweight complex-valued baseline | P2 | Appendix | Tests whether complex-valued I/Q modeling explains low-SNR gains better than STFT | complex I/Q | medium, implementation risk | yes | maybe | Medium; relevant but may distract from Stage 2 |
| Denoising/shrinkage baseline | P2 | Appendix | Low-SNR robustness competitor without multi-view fusion | raw I/Q plus denoising block | medium | yes | maybe | Medium; important if low-SNR claim is central |
| MCNet | P3 | Appendix/future | Alternative lightweight AMC baseline if LWAMCNet is not chosen | raw I/Q | low to medium | yes | yes | Low if LWAMCNet is implemented |
| RadioML2018.01A ResNet/CNN baseline | P3 | Stage 3 main | External validity and harder dataset validation | raw I/Q `[2, 1024]` likely | high | config/data loader likely | uncertain | Severe for final paper, not required for Stage 2 protocol |

## Minimum Main Table

The smallest defensible Stage 2 main table is:

1. CNN1D.
2. ResNet1D.
3. TF-CNN STFT.
4. `fusion_iq_stft` static fusion.
5. CLDNN or CNN-LSTM.
6. MCLDNN.
7. LWAMCNet.
8. Parameter-matched I/Q-only model.
9. Proposed gated fusion variants, after implementation.

## Baseline Implementation Order

Implementation order should control risk:

1. Freeze split and prediction logging.
2. Re-run existing CNN1D, ResNet1D, TF-CNN STFT, and `fusion_iq_stft` through
   the V2 logging path.
3. Add CLDNN or CNN-LSTM.
4. Add MCLDNN.
5. Add LWAMCNet.
6. Add parameter-matched I/Q-only baseline.
7. Add gated fusion only after the comparison harness is stable.
8. Add P2 baselines if the gated method survives initial tests.

## Main-Table Readiness Checklist

Each baseline must have:

- fixed full split evaluation;
- 3 training seeds;
- per-SNR accuracy;
- low/mid/high grouped accuracy;
- macro-F1 and low-SNR macro-F1;
- sample-level predictions;
- parameters;
- FLOPs/MACs;
- latency excluding preprocessing;
- latency including preprocessing where applicable;
- peak memory;
- training time per epoch.

## Reviewer Notes

Supported by current project:

- CNN1D, ResNet1D, and static `fusion_iq_stft` are already part of the local
  evidence base.

Supported by literature:

- CLDNN/CNN-LSTM, MCLDNN, lightweight CNN, attention, complex-valued, and
  low-SNR robust baselines are established AMC comparison families.

Still hypotheses:

- A gated I/Q plus STFT model will beat these baselines in low-SNR robustness
  without damaging mid/high-SNR performance.

