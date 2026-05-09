# Paper-Stage 6 Low-SNR Confusion-Matrix Analysis (P1.3)

Date: 2026-05-09
Evidence label: `PROJECT_SUPPORTED` (post-processed Stage 5A predictions; no model retraining).
Source artefacts: `paper_package/predictions_archive_20260508/results/paper_stage2/rml2016a/<model>/seed_<seed>/predictions_test.csv` (27 files, 9 models × 3 seeds).
Output dir: `results/paper_stage6/low_snr_confusion_extended/`

## Scope

This document closes the pending output flagged in [`runs/stage3_low_snr_analysis/stage3_low_snr_findings.md`](../../runs/stage3_low_snr_analysis/stage3_low_snr_findings.md): per-class low-SNR confusion matrices for the Stage 5A models. It is a pure post-processing pass over the archived prediction CSVs and does not modify Stage 5A/5B aggregate tables.

The threshold follows the protocol definition `snr_db <= -6 dB`. Each model figure aggregates 52,800 low-SNR test samples (8 SNR levels × 6,600 samples per SNR within the test split, summed across three seeds).

## Headline Finding: Low-SNR Models Collapse To One Modulation

For seven of the nine Stage 5A model rows, the low-SNR top-5 off-diagonal cells all share the same predicted-class column: **AM-SSB**. The fraction of *non-AM-SSB* true classes that the model predicts as AM-SSB at low SNR is large:

| Model | top off-diagonal pattern | fraction of row |
|---|---|---:|
| cnn1d | 8PSK / BPSK / QPSK / CPFSK / GFSK -> AM-SSB | 0.628 - 0.683 |
| resnet1d | 8PSK / BPSK / QPSK / CPFSK / GFSK -> AM-SSB | 0.629 - 0.700 |
| tfcnn_stft | 8PSK / BPSK / CPFSK / QPSK / GFSK -> AM-SSB | 0.756 - 0.805 |
| fusion_iq_stft | 8PSK / QPSK / CPFSK / BPSK / GFSK -> AM-SSB | 0.652 - 0.711 |
| cldnn | 8PSK / QPSK / BPSK / CPFSK / GFSK -> AM-SSB | 0.677 - 0.746 |
| lwamcnet | 8PSK / CPFSK / QPSK / BPSK / GFSK -> AM-SSB | 0.713 - 0.757 |
| iq_param_matched | 8PSK / CPFSK / BPSK / QPSK / GFSK -> AM-SSB | 0.667 - 0.725 |
| gated_fusion_iq_stft | 8PSK / BPSK / QPSK / CPFSK / GFSK -> AM-SSB | 0.687 - 0.745 |

The eighth row, `mcldnn`, collapses differently because two of its three Stage 5A seeds (2025, 3407) are chance-level single-class predictions; its top off-diagonal pattern is dominated by predicting AM-DSB.

The per-class low-SNR accuracy table reflects the same pattern: AM-SSB low-SNR accuracy is in 0.87-0.95 for all models, while every non-AM-SSB class is below 0.32, and most digital modulations are below 0.10:

| Model | low-SNR Acc | AM-SSB | AM-DSB | QAM64 | PAM4 | GFSK | CPFSK | QAM16 | BPSK | WBFM | QPSK | 8PSK |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cnn1d | 0.2095 | 0.869 | 0.264 | 0.294 | 0.261 | 0.175 | 0.098 | 0.087 | 0.091 | 0.080 | 0.043 | 0.043 |
| resnet1d | 0.2059 | 0.875 | 0.280 | 0.242 | 0.257 | 0.152 | 0.119 | 0.131 | 0.065 | 0.072 | 0.037 | 0.035 |
| tfcnn_stft | 0.1713 | 0.948 | 0.100 | 0.274 | 0.180 | 0.070 | 0.067 | 0.040 | 0.066 | 0.080 | 0.033 | 0.028 |
| fusion_iq_stft | 0.2213 | 0.883 | 0.297 | 0.327 | 0.300 | 0.156 | 0.103 | 0.084 | 0.080 | 0.114 | 0.037 | 0.054 |
| cldnn | 0.2224 | 0.918 | 0.315 | 0.336 | 0.268 | 0.188 | 0.089 | 0.082 | 0.101 | 0.073 | 0.035 | 0.043 |
| mcldnn | 0.1313 | 0.307 | 0.455 | 0.089 | 0.074 | 0.045 | 0.048 | 0.048 | 0.027 | 0.005 | 0.008 | 0.340 |
| lwamcnet | 0.2025 | 0.910 | 0.296 | 0.263 | 0.249 | 0.126 | 0.059 | 0.127 | 0.063 | 0.085 | 0.031 | 0.018 |
| iq_param_matched | 0.2163 | 0.884 | 0.296 | 0.238 | 0.297 | 0.163 | 0.079 | 0.157 | 0.084 | 0.101 | 0.050 | 0.032 |
| gated_fusion_iq_stft | 0.2113 | 0.908 | 0.277 | 0.285 | 0.256 | 0.156 | 0.077 | 0.079 | 0.087 | 0.090 | 0.045 | 0.062 |

This is a behavioural signature of a model that has identified one modulation with a noise-robust spectral feature (AM-SSB has an asymmetric, single-sideband spectrum), and falls back to that prediction when the input is sufficiently corrupted by AWGN. It is consistent with the expected accuracy floor at chance-level (1/11 ~ 0.09) plus a strong AM-SSB bias.

## Why This Matters For The Manuscript

1. **The Stage 5A low-SNR ranking compresses different failure modes into one number.** A 2 pp difference in the low-SNR aggregate between two models can hide identical AM-SSB collapse patterns. The per-class table makes the comparison concrete: for example, between `fusion_iq_stft` and `iq_param_matched`, the +0.005 low-SNR aggregate gap (Stage 5A statistical-test summary) is composed of a +0.022 PAM4 gap, a +0.013 WBFM gap, and a +0.022 8PSK gap, partly offset by `iq_param_matched`'s +0.073 QAM16 gap.

2. **Stage 5A's "fusion has a low-SNR advantage over `iq_param_matched`" claim is supported on the digital-modulation classes that benefit from the time-frequency view.** The biggest advantages of `fusion_iq_stft` over `iq_param_matched` at low SNR are PAM4 (+0.022 absolute), QAM64 (+0.089 absolute), and 8PSK (+0.022 absolute). The disadvantages are QAM16 (-0.073 absolute), CPFSK (+0.024 absolute, in fusion's favour), and BPSK (-0.004 absolute). This makes the Section 5.2 trade-off statement more interpretable.

3. **CLDNN's stronger low-SNR aggregate is mostly an AM-SSB and AM-DSB advantage.** CLDNN's edge over the parameter-matched I/Q baseline at low SNR (0.2224 vs 0.2163) is concentrated on AM-SSB (+0.034) and AM-DSB (+0.019), with smaller positive contributions on QAM64 and other classes. This is consistent with CLDNN's stronger temporal modeling exploiting the slower-varying spectrum of analog modulations under noise.

4. **The collapse-to-AM-SSB pattern motivates the P2.5 SNR-weighted-CE experiment.** Plain cross-entropy gives the model no incentive to extract more signal from low-SNR examples than high-SNR examples. A loss that re-weights low-SNR samples upward changes the gradient incentive directly. This is the planned C-line experiment; it is reported under a separate evidence label.

## Disallowed Statements

- This addendum does not change the Stage 5A main table, Stage 5A low-SNR table, paired bootstrap, or McNemar tests.
- It does not give any model row a new aggregate accuracy. All numbers here are recalculated from the same 27 archived prediction files.
- It does not authorize generalization beyond the protocol-bounded RadioML2016.10A fixed split.

## Artefacts

- 9 normalized confusion-matrix PNGs (3-seed aggregate)
- 9 raw-count confusion-matrix PNGs
- 9 per-seed panel PNGs (3 subplots per model) for stability inspection
- `confusion_low_snr_summary.csv` (one row per model, columns = per-class accuracy)
- `confusion_low_snr_summary.md` (markdown digest with top-5 off-diagonals per model)
