# Paper Configs

This directory is reserved for SCI-track configuration files.

Paper-Stage 0 intentionally does not add executable training configs. Future
configs should be added only after the literature gap and experiment protocol are
fixed.

Expected future configs:

- `rml2016a_gated_fusion_subset.yaml`
- `rml2016a_gated_fusion_full.yaml`
- `rml2016a_low_snr_weighted_loss.yaml`
- `rml2016a_snr_balanced_sampler.yaml`
- RadioML2018.01A validation configs after the dataset protocol is ready.

Rules:

- Keep subset and full configs clearly separated.
- Record seeds explicitly.
- Do not reference private absolute data paths in committed configs.
- Do not commit credentials or tokens.
