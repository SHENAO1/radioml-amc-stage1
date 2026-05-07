# Paper Track Overview

## Project Background

The project studies automatic modulation classification (AMC) with RadioML2016.10A
and later RadioML2018.01A. The course-project track has already built a complete
engineering loop for data loading, training, evaluation, visualization, reports,
I/Q baselines, time-frequency branches, and initial multi-view fusion.

## Current Experiment Basis

The current stable evidence comes from RadioML2016.10A full experiments:

- CNN1D and ResNet1D I/Q baselines.
- STFT-based time-frequency feature extraction.
- I/Q + STFT fusion through `fusion_iq_stft`.
- Low/mid/high-SNR grouped evaluation.
- Complexity observations for STFT and CWT.

Stage 2.2 shows that ResNet1D is the best overall model, while `fusion_iq_stft`
has a small low-SNR advantage but worse mid/high-SNR and overall accuracy.

## Why Use a Separate SCI-Track Branch

The SCI-track branch protects the completed course-project artifacts while
allowing the paper direction to evolve through stricter protocols, additional
literature review, more seeds, more ablations, and possible RadioML2018.01A
validation.

This branch should not rewrite the meaning of the completed course stages. It
records the existing results as evidence and prepares new paper-level questions.

## SCI-Track vs Course-Report Track

| Aspect | Course-report track | SCI-track |
|---|---|---|
| Goal | Complete a reliable course project | Explore publishable research direction |
| Dataset | RadioML2016.10A mainly | RadioML2016.10A, later RadioML2018.01A |
| Evidence level | Single-seed engineering experiments acceptable with caveats | Multi-seed, full-set, complexity-aware evidence |
| Model scope | Baselines and practical fusion | SNR-aware low-SNR robust fusion |
| Claim style | Conservative course-report conclusions | Literature-grounded, statistically supported claims |
| Risk tolerance | Avoid disrupting stable workflow | Add protocols before adding new methods |

## Recommended Paper Direction

The recommended direction is:

**SNR-aware lightweight multi-view fusion for robust AMC under low-SNR
conditions.**

This direction is consistent with the current observation: simple I/Q + STFT
fusion does not improve overall accuracy, but may provide complementary
information at low SNR. The paper track should therefore focus on adaptive
fusion and low-SNR robustness rather than claiming generic fusion superiority.

## Short-Term Goals

- Freeze the current Stage 2.2 full-result snapshot.
- Build a literature review table and validate the research gap.
- Upgrade the experiment protocol to paper level.
- Define SNR-aware gated fusion without implementing it prematurely.

## Medium-Term Goals

- Implement a lightweight gated fusion prototype.
- Run subset smoke tests before full training.
- Add low-SNR weighted loss and SNR-balanced sampling ablations.
- Run at least three seeds on the main RadioML2016.10A experiments.

## Long-Term Goals

- Extend validation to RadioML2018.01A.
- Compare accuracy, per-SNR robustness, complexity, and inference cost.
- Prepare a paper draft with bounded claims and reproducible experiment tables.
