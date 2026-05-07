# Current Experiment Snapshot

## Scope

This snapshot freezes the current Stage 2.2 RadioML2016.10A full baseline and
full ablation evidence for the SCI-track branch. It is evidence for planning, not
a final paper result.

## Stage 2.2 Full Results

| Model | Overall | Low SNR | Mid SNR | High SNR |
|---|---:|---:|---:|---:|
| CNN1D | 0.5855 | 0.2032 | 0.8017 | 0.8790 |
| ResNet1D | 0.5968 | 0.2091 | 0.8155 | 0.8950 |
| fusion_iq_stft | 0.5782 | 0.2222 | 0.7856 | 0.8455 |

## Key Observations

- The current best overall model is ResNet1D with overall accuracy 0.5968.
- `fusion_iq_stft` does not exceed ResNet1D or CNN1D in overall accuracy.
- `fusion_iq_stft` has a weak low-SNR advantage: 0.2222 versus ResNet1D 0.2091
  and CNN1D 0.2032.
- `fusion_iq_stft` is weaker than ResNet1D in mid-SNR and high-SNR groups.
- The current evidence cannot support the claim that the fusion model is
  generally or fully better than the baselines.
- The current evidence can support the weak hypothesis that time-frequency
  fusion may provide complementary value under low-SNR conditions.
- Full CWT training was temporarily skipped because the current on-the-fly CWT
  implementation is CPU-bound and too costly on the RTX 4070 12GB server setup.

## Claim Boundary

Allowed statement:

Time-frequency fusion may provide complementary information for low-SNR AMC, but
the current simple fusion design sacrifices mid/high-SNR and overall accuracy.

Not allowed statement:

The fusion model comprehensively outperforms I/Q baselines.

## Current Limitations

- Single-seed full results only.
- RadioML2016.10A only.
- No low-SNR-only confusion matrix with saved sample-level predictions yet.
- No RadioML2018.01A validation.
- No paper-level complexity table with FLOPs and latency across devices yet.
