# Literature Review Plan

## Goal

Build a literature table that determines whether the proposed SCI-track idea has
real publication space and what experiments must be added before writing a paper.

## Search Keywords

- automatic modulation classification
- RadioML2016.10A
- RadioML2018.01A
- low SNR modulation classification
- time-frequency modulation recognition
- multi-view fusion AMC
- SNR-aware deep learning
- lightweight AMC
- complex neural network AMC
- attention AMC

## Suggested Search Sources

- IEEE Xplore
- Elsevier ScienceDirect
- SpringerLink
- MDPI Sensors and Electronics
- arXiv
- Google Scholar
- Web of Science or Scopus if available

## Literature Table Fields

| Field | Description |
|---|---|
| paper title | Exact title |
| year | Publication year |
| dataset | RadioML2016.10A, RadioML2018.01A, synthetic, OTA, or other |
| input representation | I/Q, STFT, CWT, constellation, amplitude-phase, multi-view |
| model | CNN, ResNet, LSTM, complex network, attention, Transformer, fusion |
| low-SNR experiment | Whether low-SNR conditions are explicitly evaluated |
| per-SNR result | Whether per-SNR accuracy curves or tables are reported |
| complexity report | Params, FLOPs, latency, memory, training cost |
| ablation | Branch, loss, sampler, augmentation, gate, architecture |
| limitation | Weaknesses, missing evidence, unrealistic assumptions |
| relevance to this project | Why it supports or challenges the planned paper direction |

## Review Questions

- Which papers report per-SNR accuracy rather than only overall accuracy?
- Which papers focus on low-SNR robustness?
- Which papers combine raw I/Q with time-frequency features?
- Which fusion methods are static and which are adaptive?
- Do existing methods use true SNR labels during training or inference?
- Are complexity and inference latency reported fairly?
- Are results multi-seed or single-seed?
- Is RadioML2018.01A used as a stronger validation dataset?

## Expected Output of Paper-Stage 1

- A completed literature table.
- A verified gap statement.
- A list of required experiments for publishable claims.
- A Related Work outline with subsections and paper clusters.
- A decision on whether the current method direction is strong enough to pursue.
