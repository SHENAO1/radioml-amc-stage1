# Paper Scripts

This directory is reserved for future SCI-track helper scripts.

Paper-Stage 0 intentionally does not add new executable scripts. Future scripts
should support reproducibility, paper-table generation, and controlled ablation
runs after the protocol is finalized.

Expected future scripts:

- Literature table formatting helpers.
- Paper experiment launch wrappers.
- Multi-seed aggregation.
- Complexity reporting.
- Low-SNR confusion-matrix generation from saved predictions.

Rules:

- Do not start large-scale training from this stage.
- Do not print secrets or private server paths.
- Do not write raw data, runs, checkpoints, or `.venv` contents into Git.
