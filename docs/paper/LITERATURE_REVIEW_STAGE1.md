# Paper-Stage 1 Literature Review and Gap Assessment

Date: 2026-05-07

Branch: `paper-sci-track`

Scope: assess whether "SNR-aware lightweight multi-view fusion for low-SNR
robust AMC" has publishable space. This document freezes a literature-grounded
Stage 1 judgement only. It does not change model code and does not claim that
the current fusion model is generally better than I/Q baselines.

## Current Project Evidence

The current local evidence is the RadioML2016.10A full single-seed snapshot in
[`CURRENT_EXPERIMENT_SNAPSHOT.md`](CURRENT_EXPERIMENT_SNAPSHOT.md).

| Model | Overall | Low SNR | Mid SNR | High SNR |
|---|---:|---:|---:|---:|
| CNN1D | 0.5855 | 0.2032 | 0.8017 | 0.8790 |
| ResNet1D | 0.5968 | 0.2091 | 0.8155 | 0.8950 |
| fusion_iq_stft | 0.5782 | 0.2222 | 0.7856 | 0.8455 |

Allowed project-level conclusion:

- ResNet1D is currently the best overall model.
- `fusion_iq_stft` has only a weak low-SNR advantage.
- The current evidence supports only a hypothesis that a time-frequency view may
  provide complementary low-SNR information.

Forbidden claim:

- Do not claim that fusion comprehensively outperforms the I/Q baselines.

## Literature Table

Legend:

- "per-SNR" means the paper reports an accuracy-vs-SNR curve, table, or
  SNR-conditioned analysis.
- "complexity" includes parameters, FLOPs, latency, memory, training time, or
  implementation cost.
- "low-SNR" follows each paper's own definition where available.

| Paper title | Year | Venue | Dataset | Input representation | Model | Low-SNR experiment | Per-SNR result | Complexity report | Ablation | Limitation | Relevance to this project |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| [Radio Machine Learning Dataset Generation with GNU Radio](https://pubs.gnuradio.org/index.php/grcon/article/view/11) | 2016 | GNU Radio Conference | RadioML family, including 2016.10A generation context | synthetic I/Q | dataset generation pipeline | yes, SNR is a dataset axis | dataset supports per-SNR evaluation | not a model paper | no | dataset realism and leakage must be handled carefully | Primary dataset provenance for RadioML2016.10A-style experiments. |
| [Convolutional Radio Modulation Recognition Networks](https://arxiv.org/abs/1602.04105) | 2016 | EANN / arXiv | early RadioML datasets | raw I/Q | CNN / VTCNN-style classifier | yes, emphasizes low SNR viability | yes | limited by current standards | limited | early benchmark, smaller protocol than current SCI expectations | Establishes raw I/Q CNN baseline tradition. |
| [Over-the-Air Deep Learning Based Radio Signal Classification](https://arxiv.org/abs/1712.04578) | 2018 | IEEE Journal of Selected Topics in Signal Processing | RadioML2018.01A | raw I/Q, synthetic and OTA RF bursts | CNN / ResNet-style DL classifiers | yes, SNR is central | yes | partial architecture discussion, not full modern FLOPs/latency protocol | some architecture comparisons | RadioML2018.01A is harder and more realistic than 2016.10A; exact splits matter | Required Stage 2 validation reference if claiming SCI-level generality. |
| [Automatic Modulation Classification: A Deep Learning Enabled Approach](https://ieeexplore.ieee.org/document/8454504/) | 2018 | IEEE Transactions on Vehicular Technology | simulated digital modulation scenarios | long symbol-rate observations plus estimated SNR | CNN-AMC | yes, robust to SNR and estimation errors | yes | inference speed compared with ML-AMC | training strategy and transfer learning | not a RadioML2016.10A benchmark paper | Important prior art because SNR information is already used as model input. |
| [Spectrum Analysis and Convolutional Neural Network for Automatic Modulation Recognition](https://doi.org/10.1109/LWC.2019.2900247) | 2019 | IEEE Wireless Communications Letters | simulated radio signals | STFT spectrogram plus Gaussian filtering/statistical analysis | 2D CNN | yes | yes | compares computational complexity | limited | pure spectrogram pipeline may add preprocessing cost and may not preserve high-SNR I/Q behavior | Direct support that time-frequency images can help AMC. |
| [Automatic Modulation Classification Using CNN With Features Fusion of SPWVD and BJD](https://www.semanticscholar.org/paper/Automatic-Modulation-Classification-Using-Neural-of-Zhang-Wang/dc54adb7b80ff2d32682539461777d15118ed441) | 2019 | IEEE Transactions on Signal and Information Processing over Networks | simulated AMC data | handcrafted features, SPWVD images, BJD images | CNN feature extraction plus multimodal fusion | yes, reports strong result at -4 dB | yes | compares feature combinations | partial | feature extraction is heavy; not raw I/Q plus lightweight adaptive gate | Strong prior art for time-frequency fusion; weakens novelty of simple static fusion. |
| [A Spatiotemporal Multi-Channel Learning Framework for Automatic Modulation Recognition](https://doi.org/10.1109/LWC.2020.2999453) | 2020 | IEEE Wireless Communications Letters | RadioML2016.10A / 2016.10B | I, Q, and I/Q streams | MCLDNN, CNN plus LSTM | yes | yes | limited in letter format | limited | stronger baseline than simple CNN/ResNet for many AMC protocols | Must be included as a Stage 2 baseline or at least reimplemented/quoted carefully. |
| [Automatic Modulation Classification Using CNN-LSTM Based Dual-Stream Structure](https://doi.org/10.1109/TVT.2020.3030018) | 2020 | IEEE Transactions on Vehicular Technology | RadioML2016.10A / 2016.10B style benchmarks | I/Q and amplitude/phase | CNN-LSTM dual-stream fusion | yes | yes | architecture comparisons | yes | heavier temporal model; not explicitly lightweight SNR-gated STFT fusion | Relevant multi-representation baseline; static/architectural fusion already exists. |
| [Automatic Modulation Classification Based on Deep Residual Networks With Multimodal Information](https://www.semanticscholar.org/paper/Automatic-Modulation-Classification-Based-on-Deep-Qi-Zhou/1f815304fb950570a71878f324369ccaad6362d1) | 2021 | IEEE Transactions on Cognitive Communications and Networking | custom high-order modulation data | waveform and spectrum multimodal information | residual networks with waveform-spectrum fusion | yes | yes | likely representation comparisons | yes | not the same RadioML protocol; multimodal fusion itself is not novel | Key evidence that waveform-spectrum fusion is established prior art. |
| [A Lightweight CNN Architecture for Automatic Modulation Classification](https://www.mdpi.com/2079-9292/10/21/2679) | 2021 | Electronics | RadioML2018.01A and RadioML2016.10A | raw I/Q | LWAMCNet with depthwise separable convolution | limited low-SNR discussion | yes | parameters and CPU inference time | architecture depth comparison | average accuracy lower than high-capacity methods | Required lightweight baseline; shows complexity tables are expected. |
| [Deep Cascading Network Architecture for Robust AMC](https://www.sciencedirect.com/science/article/abs/pii/S0925231221007219) | 2021 | Neurocomputing | AMC datasets | SNR-conditioned sub-environments | SNR environment perception plus classifiers | yes | yes | likely model components | yes | uses SNR labels/environment split; may be heavier than this project's target | Direct SNR-aware prior art. Novelty must avoid claiming SNR-awareness alone. |
| [Automatic Modulation Classification: A Deep Architecture Survey](https://www.researchgate.net/publication/355663524_Automatic_Modulation_Classification_A_Deep_Architecture_Survey) | 2021 | IEEE Access | survey | I/Q, spectrum, constellation and other representations | survey of CNN/RNN/hybrid/advanced models | yes, identifies robustness as a challenge | survey-level | survey-level | not an experimental method | survey only | Supports the Related Work taxonomy and expected evidence standards. |
| [Robust Automatic Modulation Classification Using CNN Based on Scalogram Information](https://www.mdpi.com/2073-431X/11/11/162) | 2022 | Computers | AMC datasets | scalogram / wavelet time-frequency images | CNN | yes | yes | limited | likely limited | preprocessing cost and representation sensitivity | Supports CWT/scalogram relevance, but also justifies treating CWT as optional if compute is high. |
| [Deep Multi-Scale Representation Learning with Attention for AMC](https://arxiv.org/abs/2209.03764) | 2022 | IJCNN | RadioML2018.01A | raw I/Q | SE-MSFN, multi-scale convolution plus SE attention | yes, reports lower-SNR range 0 to 10 dB | yes | limited | ensemble and architecture variants | low-SNR range starts at 0 dB, not the hardest -20 to -2 dB region | Strong attention baseline; Stage 2 should not ignore attention-based AMC. |
| [A Spatiotemporal Multi-Stream Learning Framework Based on Attention Mechanism for AMR](https://doi.org/10.1016/j.dsp.2022.103703) | 2022 | Digital Signal Processing | four DeepSig datasets | amplitude, phase, frequency, raw data | multi-stream CNN/BiGRU plus CBAM/MHSA | yes | yes | likely attention/stream components | yes | multi-stream attention can be heavy; not necessarily lightweight | Narrows gap: multi-stream attention fusion already exists. |
| [Automatic Modulation Classification with Deep Neural Networks](https://www.mdpi.com/2079-9292/12/18/3962) | 2023 | Electronics | RadioML2018.01A | raw I/Q bursts | dilated CNN, statistics pooling, SE units | yes via SNR-conditioned RadioML2018.01A evaluation | yes | reports extensive architecture ablation | yes | not focused on multi-view STFT fusion | Useful protocol model: ablation, per-SNR, and RadioML2018.01A main evaluation. |
| [An Efficient and Lightweight Model for AMC: Hybrid Feature Extraction Network Combined with Attention](https://www.mdpi.com/2079-9292/12/17/3661) | 2023 | Electronics | RadioML2016.10A | raw I/Q | HFECNET-CA, hybrid features plus channel attention | yes | yes | parameters and test time | yes | single dataset focus | Strong lightweight plus attention baseline; must be compared in complexity terms. |
| [IDAF: Iterative Dual-Scale Attentional Fusion Network for AMR](https://www.mdpi.com/1424-8220/23/19/8134) | 2023 | Sensors | AMC benchmarks | multimodal/multi-channel signals | iterative dual-scale attentional fusion | yes | yes | not always complete latency/FLOPs | yes | attention fusion can be complex | Shows that attentional fusion is an active competing route. |
| [Automatic Modulation Recognition Based on Multimodal Information Processing](https://www.mdpi.com/2079-9292/13/22/4568) | 2024 | Electronics | RadioML2016.10A, 2016.10B, RadioML2018.01A-sample | multimodal signals | MPHNN with spatio-temporal attention | yes | yes | parameters, training time, prediction time, memory | statistical comparison | sample version of 2018.01A may not equal full 2018.01A | Shows reviewers can ask for memory/time, not only accuracy. |
| [A Complex-Valued Convolutional Fusion-Type Multi-Stream Spatiotemporal Network for AMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11436720/) | 2024 | Scientific Reports | RML2016.10A, 2016.10B, 2016.04C | I, Q, I/Q complex-valued streams | CC-MSNet, complex convolution plus LSTM/BiLSTM | yes, emphasizes below 0 dB | yes | parameters table and component experiments | yes | parameter count still larger than lightweight models; no RadioML2018.01A | Relevant complex and multi-stream baseline for low-SNR claims. |
| [Robust AMC Using Asymmetric Trilinear Attention Net with Noisy Activation](https://www.sciencedirect.com/science/article/abs/pii/S0952197624020207) | 2024 | Engineering Applications of Artificial Intelligence | practical and simulation AMC tasks | multi-channel received signals | Tri-Net with SE-style attention and noisy ReLU | yes | yes | likely component ablation | yes | abstract does not establish lightweight deployment | Low-SNR robust attention competitor. |
| [Phase Transformation and Deep Residual Shrinkage Network for AMR](https://www.mdpi.com/2079-9292/13/11/2141) | 2024 | Electronics | RML2016.10A | raw I/Q plus phase transformation | CNN, GRU, residual shrinkage | yes | yes | parameters compared with other models | likely | not multi-view STFT fusion | Denoising/shrinkage is a relevant low-SNR baseline family. |
| [A Lightweight Dual-Branch Complex-Valued Neural Network for AMC](https://www.mdpi.com/1424-8220/25/8/2489) | 2025 | Sensors | RML2016.10A and other datasets | complex I/Q | LDCVNN, complex dual branch with trainable fusion | yes | yes | parameters and efficiency focus | yes | not time-frequency fusion; complex operations can complicate deployment | Important lightweight complex baseline; sets a high bar for parameter efficiency. |
| [Improved AMR Using Deep Learning with Additive Attention](https://www.sciencedirect.com/science/article/pii/S2590123025008606) | 2025 | Results in Engineering | RadioML2016.10A and 2016.10B | raw I/Q | CNN-BiLSTM with additive attention | yes, reports 0 dB and low-SNR robustness | yes | 48.42 MFLOPs, 0.79M params | yes | heavier recurrent model than desired lightweight fusion | Good comparison point for accuracy/complexity trade-off. |
| [Wavelet CNN and Dual-Channel Feature Extraction for AMC](https://link.springer.com/article/10.1007/s44443-025-00382-y) | 2025 | Journal of King Saud University - Computer and Information Sciences | RadioML2016.10A, 2016.10B, RML22 | wavelet/time-frequency dual channel | WCNN-DFE | yes, reports -10, -6, -4, 0 dB type results | yes | parameters, FLOPs, memory, training time | yes | newer paper raises novelty bar for wavelet/STFT low-SNR claims | Strong evidence that time-frequency low-SNR AMC is active and must be compared. |
| [MCCSAN: Multiscale Complex Convolution and Spatiotemporal Attention Network](https://www.mdpi.com/2079-9292/14/16/3192) | 2025 | Electronics | RadioML2018.01A and RadioML2016.10A | I/Q, frequency and constellation visualization; complex conv input | multiscale complex convolution plus spatiotemporal attention | yes, -6 to 12 dB focus | yes | parameter count and module ablation | yes | heavier than ultra-light models; attention/complex modules may be difficult to deploy | Strong recent complex-attention baseline across 2016 and 2018. |
| [KADNet: Low SNR AMC via SNR Aware Deformable Convolution and KANs](https://www.sciencedirect.com/science/article/pii/S105120042600062X) | 2026 | Digital Signal Processing | AMC datasets | I/Q projected to FFT/frequency domain | SEM plus SNR-aware deformable convolution plus KAN | yes, primary focus | yes | abstract indicates SNR-aware module; full complexity must be checked | likely | very recent; may be heavy and uses a different architecture family | Critical novelty threat: SNR-aware low-SNR AMC exists. Our gap must be lightweight multi-view gate with reproducible complexity. |
| [CAIC-Net: Robust Radio Modulation Classification via Dynamic Cross-Attention and Cross-SNR Contrastive Learning](https://www.mdpi.com/1424-8220/26/3/756) | 2026 | Sensors | AMC benchmarks | multi-scale signal features | dynamic cross-attention plus cross-SNR contrastive learning | yes | yes | likely | yes | may rely on heavier contrastive/attention training | Shows cross-SNR learning is current; Stage 2 needs a narrower and cleaner claim. |

## Related Work Structure for the Paper

### 1. I/Q Deep Learning Baselines for AMC

Use O'Shea et al., O'Shea/Roy/Clancy, MCLDNN, CNN-LSTM dual-stream, ResNet,
CLDNN/LSTM/GRU families, Harper et al., and project CNN1D/ResNet1D. The key
message is that raw I/Q learning is the main reproducible baseline and often has
strong mid/high-SNR behavior with low preprocessing cost.

### 2. Time-Frequency Representation for AMC

Use STFT/spectrogram, SPWVD/BJD, scalogram/CWT, wavelet dual-channel, fractional
S-transform, and Fourier/spectrum analysis work. The key message is that
time-frequency images can expose local spectral-temporal structure and are
especially plausible under noisy or nonstationary conditions, but preprocessing
cost and representation sensitivity are nontrivial.

### 3. Multi-View Fusion for AMC

Use SPWVD/BJD feature fusion, waveform-spectrum multimodal residual networks,
CNN-LSTM dual-stream I/Q plus A/P, MCLDNN multi-channel I/Q streams, MPHNN,
IDAF, and CC-MSNet. The key message is that "fusion" itself is not novel. The
paper must focus on when and why a branch should be used.

### 4. Low-SNR Robust AMC

Use robust CNN, deep cascading SNR-aware architectures, denoising/shrinkage,
attention models, wavelet models, CC-MSNet, KADNet, and CAIC-Net. The key
message is that low-SNR robustness is a real and crowded target; per-SNR curves
and low-SNR subgroup tables are mandatory.

### 5. Lightweight and Complexity-Aware AMC

Use LWAMCNet, HFECNET-CA, LDCVNN, lightweight complex/attention models, and
deployment-oriented papers. The key message is that a SCI submission must report
parameters, FLOPs or MACs, preprocessing cost, latency, and memory. Accuracy
alone will not be persuasive.

### 6. SNR-Aware or Reliability-Aware Learning

Use CNN-AMC with estimated SNR, deep cascading SNR-environment perception,
KADNet, CAIC-Net, and reliability/attention fusion papers. The key message is
that the gap is not "using SNR"; the gap must be framed as lightweight
reliability-gated multi-view fusion that preserves high-SNR I/Q behavior while
selectively exploiting time-frequency views at low SNR.

## Reviewer-Style Gap Judgement

### Is There Publication Space?

Yes, but it is narrow. A publishable paper is plausible only if the work is
positioned as:

> Lightweight reliability/SNR-aware multi-view fusion that improves low-SNR AMC
> without sacrificing mid/high-SNR behavior or deployment cost.

It is not publishable as:

- "STFT fusion improves AMC."
- "Multi-view fusion is better than I/Q."
- "Attention/gating improves classification."
- "SNR-aware learning is new."

Those claims are already covered or strongly challenged by existing work.

### Is the Gap Real?

The broad gap is not real. Existing literature already covers:

- raw I/Q CNN/ResNet/CLDNN/MCLDNN baselines;
- spectrogram, wavelet, and other time-frequency representations;
- multimodal and multi-stream fusion;
- attention-based fusion;
- lightweight AMC;
- SNR-aware or cross-SNR learning.

The defensible gap is narrower:

- many fusion papers use static fusion or heavy attention/recurrent modules;
- many low-SNR papers improve a subset of SNRs but do not prove that high-SNR
  I/Q behavior is preserved;
- complexity reporting is inconsistent, especially when preprocessing
  transforms are included;
- fewer papers combine raw I/Q plus a time-frequency view with an explicitly
  lightweight gate whose gate behavior is analyzed by SNR and class.

### Weakest Current Evidence

The weakest evidence is not the size of the low-SNR gain alone. The bigger
problem is that the current result is single-seed, RadioML2016.10A-only, and the
fusion model loses mid/high-SNR and overall accuracy. A reviewer would likely
interpret the current result as a trade-off, not an improvement.

Specific weak points:

- no multi-seed mean/std or statistical test;
- no per-SNR table/curve in the paper-level format;
- no sample-level prediction files for McNemar/bootstrap or confusion analysis;
- no RadioML2018.01A validation;
- no strong baselines such as MCLDNN, MCNet/LWAMCNet/HFECNET-CA, SE-MSFN, or a
  modern attention/complex model;
- no complexity table including STFT preprocessing latency;
- no ablation isolating "time-frequency view" from "extra parameters".

### What Must Be Proven

For a credible SCI claim, Stage 2 must prove all of the following:

1. Low-SNR improvement is repeatable across at least 3 seeds.
2. Low-SNR gain remains when compared against stronger AMC baselines.
3. Mid/high-SNR degradation is eliminated or explicitly bounded.
4. The fusion/gate improves over a parameter-matched I/Q-only model.
5. The time-frequency branch is worth its preprocessing and inference cost.
6. Gate behavior is interpretable by SNR group, modulation class, and branch
   confidence.
7. Results transfer beyond RadioML2016.10A, preferably to RadioML2018.01A or at
   minimum RadioML2016.10B/RML22 if compute blocks 2018.01A.

## Evidence Taxonomy

### Supported by Current Project Experiments

- ResNet1D is currently best overall on RadioML2016.10A full single-seed.
- `fusion_iq_stft` is worse overall and worse at mid/high SNR.
- `fusion_iq_stft` has a weak low-SNR advantage over CNN1D and ResNet1D.
- CWT full training is currently optional/skipped because on-the-fly CWT is too
  costly in the current implementation.

### Supported by Literature

- Raw I/Q CNN/ResNet/RNN/hybrid networks are the standard baseline family.
- RadioML2016.10A and RadioML2018.01A are common public AMC benchmarks, with
  RadioML2018.01A being larger and more challenging.
- Time-frequency and spectrum representations are established AMC inputs.
- Multi-stream/multimodal fusion is established prior art.
- Low-SNR robustness is a recognized hard problem.
- Lightweight AMC papers often report parameters and latency; recent stronger
  papers increasingly report FLOPs, memory, training time, and ablations.
- SNR-aware or cross-SNR learning has prior art; novelty cannot rest on the
  mere use of SNR labels.

### Still Only Hypotheses

- STFT/time-frequency information provides complementary low-SNR information
  after controlling for parameter count and preprocessing cost.
- A lightweight gate can selectively use STFT at low SNR and preserve I/Q
  behavior at mid/high SNR.
- The current weak low-SNR gain will survive multi-seed evaluation.
- The same trend will appear on RadioML2018.01A.
- Gate weights will be interpretable and aligned with signal reliability rather
  than merely overfitting SNR labels.

## Paper-Stage 2 Recommendations

### Experiment Protocol Upgrade

- Use fixed train/validation/test splits saved to disk.
- Run at least 3 seeds for all main-table models.
- Save sample-level predictions with fields: sample id, SNR, modulation, y_true,
  y_pred, logits/probabilities, model name, seed.
- Report mean +/- std for overall, low-SNR, mid-SNR, high-SNR, and per-SNR
  accuracy.
- Define low/mid/high SNR before experiments and keep the definition fixed.
- Add paired significance tests for low-SNR improvements, such as bootstrap
  confidence intervals or McNemar tests on paired predictions.
- Include preprocessing cost in latency for STFT/CWT/frequency branches.

### Baselines That Should Be Added

Minimum baseline set:

- CNN1D and ResNet1D, already present.
- CLDNN or CNN-LSTM baseline.
- MCLDNN.
- MCNet or LWAMCNet as lightweight CNN baseline.
- HFECNET-CA or another lightweight attention baseline.
- A parameter-matched I/Q-only model with comparable parameter count to the
  fusion model.

Recommended stronger baseline set if time permits:

- SE-MSFN or a simplified SE/multi-scale attention model.
- LDCVNN or another lightweight complex-valued baseline.
- One denoising/shrinkage baseline, such as residual shrinkage or DAE-style
  low-SNR model.
- A static fusion baseline and a late-logit ensemble baseline to separate
  gating benefit from generic ensembling.

### Metrics for Main Tables

- overall accuracy;
- low/mid/high-SNR grouped accuracy;
- per-SNR accuracy table or curve;
- macro-F1 and balanced accuracy;
- low-SNR macro-F1;
- per-class confusion at representative SNRs, e.g. -6, 0, 10 dB;
- parameters;
- FLOPs or MACs;
- GPU latency excluding and including preprocessing;
- CPU latency including preprocessing;
- peak memory during inference;
- training time per epoch;
- preprocessing cache size if STFT/CWT is cached.

### Required Ablations

- I/Q only backbone;
- STFT only branch;
- static I/Q plus STFT fusion;
- gated fusion without explicit SNR input;
- gated fusion with true SNR input during training/inference;
- gated fusion with estimated/noisy SNR input;
- parameter-matched I/Q baseline;
- low-SNR weighted loss versus normal CE loss;
- SNR-balanced sampler versus random sampler;
- gate regularization/no regularization;
- branch dropout or reliability dropout;
- cached STFT versus on-the-fly STFT latency comparison;
- low-SNR group boundary sensitivity.

### Should We Continue Implementing SNR-Aware Gated Fusion?

Yes, but only as a Stage 2 hypothesis test, not as a guaranteed paper method.

The first implementation target should be deliberately small:

- keep ResNet1D or the current I/Q backbone as the reference path;
- add an STFT branch only if preprocessing is cached or latency is measured;
- add a scalar or channel-wise gate conditioned on SNR/reliability features;
- constrain the gate so the model can fall back to I/Q at mid/high SNR;
- log gate values by SNR and modulation class.

Go/no-go criteria after Stage 2:

- continue if low-SNR mean accuracy improves over ResNet1D and MCLDNN-style
  baselines with no statistically meaningful mid/high-SNR collapse;
- continue if the gated model beats static fusion and a parameter-matched I/Q
  baseline;
- stop or reframe if gains disappear across seeds or if the STFT cost dominates
  the deployment story.

## Working Claim Template

Conservative claim if Stage 2 succeeds:

> We do not find that time-frequency fusion uniformly improves AMC. Instead, our
> results show that a lightweight reliability/SNR-aware gate can selectively
> exploit a time-frequency view under low-SNR conditions while preserving the
> stronger raw-I/Q behavior at moderate and high SNRs, with explicit
> accuracy-complexity trade-off reporting.

Claim to avoid:

> The proposed fusion model comprehensively outperforms all baselines.

## Source Notes

This Stage 1 review used web-accessible metadata, abstracts, and open full text
where available. Before manuscript submission, verify all final numbers from the
publisher PDF or official arXiv/full-text version and store BibTeX entries in a
separate bibliography file.

