# Paper-Stage 6A Optimization Literature Matrix and Experiment Plan

Date: 2026-05-08

Project: `radioml-amc-stage1`

Scope: post-Stage5 optimization literature matrix and experiment design for RadioML2016.10A AMC/AMR.

This document is a planning and protocol artifact only. It is not paper prose and it is not full-training evidence.

## Protocol Boundary

- RadioML2018.01A must not be run in this stage.
- No new full training is authorized by this document.
- Stage 5A / Stage 5B artifacts must not be overwritten, deleted, or selectively cleaned.
- Any mock, subset, diagnostic, or smoke result must be stored outside Stage 5A main-table paths and must be labelled `DIAGNOSTIC` or `SMOKE TEST`.
- MCLDNN seed 2025 and seed 3407 chance-level results remain retained as protocol evidence. They must not be removed from any audit trail.
- Stage 6A is allowed to perform literature scanning, experiment design, protocol planning, and code feasibility inspection only.

## Evidence Read Status

Readable local evidence:

- `docs/paper/PAPER_STAGE5A_FULL_RML2016A_TRAINING_REPORT.md`
- `results/paper_stage2/rml2016a/stage5a_status.json`
- current model and training code under `src/radioml_amc/`

Requested but not present in the current local checkout:

- `docs/paper/PAPER_STAGE5B_RESULT_AUDIT_AND_TABLES.md`
- `results/paper_stage2/rml2016a/aggregate/main_table_metrics.csv`
- `results/paper_stage2/rml2016a/aggregate/low_snr_table.csv`
- `results/paper_stage2/rml2016a/aggregate/complexity_latency_table.csv`

The Stage 6A gap analysis below therefore uses Stage 5A report/status evidence and treats Stage 5B aggregate files as a synchronization gap. Before any Stage 6 full-run decision, Stage 5B should be synced or regenerated into a new audit artifact without modifying completed Stage 5A run directories.

## Stage 5 Evidence Snapshot

Stage 5A completed 27/27 cells on RadioML2016.10A with fixed split `stratified_by_mod_snr_seed42` and seeds `42`, `2025`, `3407`.

| Model | Overall mean | Low-SNR mean | Mid-SNR mean | High-SNR mean | Main readout |
|---|---:|---:|---:|---:|---|
| cldnn | 0.6129 | 0.2224 | 0.8396 | 0.9070 | Best current stable full-run baseline |
| resnet1d | 0.5959 | 0.2059 | 0.8197 | 0.8922 | Very stable; strong reference for full-run gates |
| iq_param_matched | 0.5945 | 0.2163 | 0.8121 | 0.8809 | Important control: fusion must beat this, not only vanilla CNN |
| cnn1d | 0.5820 | 0.2095 | 0.7956 | 0.8650 | Simple baseline |
| fusion_iq_stft | 0.5771 | 0.2213 | 0.7858 | 0.8428 | Low-SNR competitive, but hurts mid/high and overall |
| gated_fusion_iq_stft | 0.5719 | 0.2113 | 0.7840 | 0.8407 | Current scalar gate did not beat static fusion or I/Q controls |
| lwamcnet | 0.5511 | 0.2025 | 0.7510 | 0.8160 | Lightweight, but current implementation underperforms accuracy baselines |
| tfcnn_stft | 0.5063 | 0.1713 | 0.6900 | 0.7693 | Standalone STFT view is weak |
| mcldnn | 0.2501 | 0.1313 | 0.3182 | 0.3403 | Protocol anomaly: seed 2025/3407 chance-level retained |

The current gap is not a missing exotic architecture. The more basic gap is that fusion does not yet beat parameter-matched I/Q, low-SNR gains are small relative to seed variance, and MCLDNN is unstable under the present PyTorch/training setup.

## Literature Candidate Matrix

Search date: 2026-05-08. Sources used include direct web search, OpenAlex DOI metadata, IEEE/MDPI/Nature/PMC/arXiv landing pages, and publisher pages. This is a screening matrix, not the final manuscript bibliography. Each candidate must still be rechecked before citation in paper prose.

| # | Direction | Candidate | Main value for Stage 6 | Stage 6 action |
|---:|---|---|---|---|
| 1 | CNN/RadioML root | [O'Shea et al., 2016, Convolutional Radio Modulation Recognition Networks](https://arxiv.org/abs/1602.04105) | Raw-I/Q CNN and RadioML-era baseline framing | Protocol background |
| 2 | Benchmark/protocol | [O'Shea and West, 2016, Radio Machine Learning Dataset Generation with GNU Radio](https://pubs.gnuradio.org/index.php/grcon/article/view/11) | Dataset-generation and benchmark rationale | Cite for split/dataset context |
| 3 | Representation | [O'Shea et al., 2016, Unsupervised Representation Learning of Structured Radio Communication Signals](https://arxiv.org/abs/1604.07078) | Early autoencoder representation learning | Background only |
| 4 | MCLDNN baseline | [Xu et al., 2020, A Spatiotemporal Multi-Channel Learning Framework for Automatic Modulation Recognition](https://doi.org/10.1109/LWC.2020.2999453) | Canonical MCLDNN-style three-stream CNN/LSTM | Diagnose and stabilize |
| 5 | CLDNN/LSTM/ResNet | [Fast Deep Learning for Automatic Modulation Classification](https://arxiv.org/abs/1901.05850) | Baseline trio: CLDNN, LSTM, ResNet | Compare protocol assumptions |
| 6 | CNN/distributed sensors | [Rajendran et al., 2018, Deep Learning Models for Wireless Signal Classification With Distributed Low-Cost Spectrum Sensors](https://doi.org/10.1109/tccn.2018.2835460) | Multi-sensor and CNN baseline context | Background |
| 7 | Protocol/training | [Wang et al., 2019, Data-Driven Deep Learning for Automatic Modulation Recognition in Cognitive Radios](https://doi.org/10.1109/tvt.2019.2900460) | Data-driven AMR training design | Training protocol check |
| 8 | Spectrum data CNN | [Kulin et al., 2018, End-to-End Learning From Spectrum Data](https://doi.org/10.1109/access.2018.2818794) | End-to-end spectrum/IQ learning | Background |
| 9 | Pruning | [Lin et al., 2020, Improved Neural Network Pruning Technology for AMC in Edge Devices](https://doi.org/10.1109/tvt.2020.2983143) | Compression without retraining from scratch | Stage 6C/6D only |
| 10 | Complex-valued | [Tu et al., 2020, Complex-Valued Networks for Automatic Modulation Classification](https://doi.org/10.1109/tvt.2020.3005707) | Core complex convolution/batchnorm/init paper | High-priority candidate |
| 11 | CNN-LSTM dual stream | [Zhang et al., 2020, Automatic Modulation Classification Using CNN-LSTM Based Dual-Stream Structure](https://doi.org/10.1109/tvt.2020.3030018) | I/Q dual-stream temporal hybrid | Candidate architecture |
| 12 | Augmentation | [Huang et al., 2019, Data Augmentation for Deep Learning-Based Radio Modulation Classification](https://doi.org/10.1109/access.2019.2960775) | Radio-specific augmentation evidence | Stage 6B screening |
| 13 | Multitask | [Chang et al., 2021, Multitask-Learning-Based DNN for AMC](https://doi.org/10.1109/jiot.2021.3091523) | Auxiliary objectives and shared representations | SNR auxiliary head design |
| 14 | Robust CNN | [Tekbiyik et al., 2020, Robust and Fast AMC with CNN under Multipath Fading Channels](https://doi.org/10.1109/vtc2020-spring48590.2020.9128408) | Channel-robust CNN baseline | Background/control |
| 15 | Transformer | [Zheng et al., 2022, Fine-Grained Modulation Classification Using Multi-Scale Radio Transformer](https://doi.org/10.1109/lcomm.2022.3145647) | Transformer with dual-channel representation | Stage 6C if cheap |
| 16 | Lightweight transformer | [Zheng et al., 2023, MobileRaT](https://doi.org/10.3390/drones7100596) | Lightweight radio transformer | Later candidate |
| 17 | Semi-supervised transformer | [Kong et al., 2023, Transformer-Based Contrastive Semi-Supervised Learning for AMR](https://doi.org/10.1109/tccn.2023.3264908) | Contrastive/SSL direction | Not first full run |
| 18 | Transformer | [Hamidi-Rad and Jain, 2021, MCformer](https://doi.org/10.1109/globecom46510.2021.9685815) | Early transformer AMC baseline | Stage 6B mock only |
| 19 | Preprocessing | [Zhang et al., 2020, Data Preprocessing Method for AMC Based on CNN](https://doi.org/10.1109/lcomm.2020.3044755) | Preprocessing can dominate gains | Test only if cheap |
| 20 | Complex lightweight | [Xiao et al., 2023, Complex-Valued Depthwise Separable CNN for AMC](https://doi.org/10.1109/tim.2023.3298657) | Complex + depthwise lightweight path | High-priority candidate |
| 21 | LSTM augmentation | [Chen et al., 2020, LSTM with Random Erasing and Attention](https://doi.org/10.1109/access.2020.3017641) | Temporal model with random erasing | Augmentation screening |
| 22 | CGDNN | [Chang et al., 2022, Hierarchical Classification Head Based Convolutional Gated DNN](https://doi.org/10.1109/twc.2022.3168884) | Hierarchical labels and gated CNN | Later candidate |
| 23 | 3D CNN/noise | [Khan et al., 2021, 3D CNNs Based AMC in Channel Noise](https://doi.org/10.1049/cmu2.12269) | 3D feature representation under noise | Low priority |
| 24 | Robust DL | [Kim et al., 2021, Deep Learning-Based Robust AMC for Cognitive Radio Networks](https://doi.org/10.1109/access.2021.3091421) | Robustness-oriented CNN protocol | Background |
| 25 | Ultralight CNN | [Guo et al., 2024, Ultralight CNN for AMC in Internet of UAVs](https://doi.org/10.1109/jiot.2024.3373497) | Very small model design | Lightweight screening |
| 26 | Low SNR | [Truong An and Lee, 2023, Robust AMC in Low Signal to Noise Ratio](https://doi.org/10.1109/access.2023.3238995) | Low-SNR-specific framing | Training strategy |
| 27 | Fading DNN | [Lee et al., 2017, Robust AMC Technique for Fading Channels via DNN](https://doi.org/10.3390/e19090454) | Early robust fading protocol | Background |
| 28 | GNN/Transformer | [Wang et al., 2023, AMC Based on CNN-Transformer Graph Neural Network](https://doi.org/10.3390/s23167281) | Graph + transformer hybrid | Stage 6D only |
| 29 | Complex BiLSTM | [Liu et al., 2021, AMR Based on a DCN-BiLSTM Network](https://doi.org/10.3390/s21051577) | Complex network plus BiLSTM | Candidate but costlier |
| 30 | Masked modeling | [Peng et al., 2023, Deep Residual NN with Masked Modeling](https://doi.org/10.3390/drones7060390) | Self-supervised masked signal modeling | Not first full run |
| 31 | Complex conv | [Krzyston et al., 2020, Complex-Valued Convolutions for Modulation Recognition](https://doi.org/10.1109/iccworkshops49005.2020.9145469) | Implementation-level complex conv reference | Candidate |
| 32 | Non-Gaussian noise | [Ma et al., 2019, AMC under Non-Gaussian Noise](https://doi.org/10.1109/icc.2019.8761426) | Noise robustness beyond AWGN | Background |
| 33 | Lightweight | [Kim et al., 2020, Lightweight DL Model for AMC in Cognitive Radio Networks](https://doi.org/10.1109/access.2020.3033989) | Compact architecture control | Lightweight screening |
| 34 | Scalogram | [Abdulkarem et al., 2022, Robust AMC Using Scalogram Information](https://doi.org/10.3390/computers11110162) | Time-frequency alternative to STFT | CWT/scalogram screening |
| 35 | Cepstrum | [Xing and Gao, 2019, Modulation Classification for Multipath Signals Based on Cepstrum](https://doi.org/10.1109/tim.2019.2955535) | Classical transform comparison | Background only |
| 36 | Autoencoder | [Shi et al., 2022, ConvLSTMAE](https://doi.org/10.1109/lcomm.2022.3179003) | Spatiotemporal autoencoder | Denoise/SSL candidate |
| 37 | Multimodal transformer | [Shao et al., 2024, IQFormer](https://doi.org/10.1109/tccn.2024.3485118) | Multi-modality fusion transformer | Later candidate |
| 38 | Residual attention | [Huynh-The et al., 2022, RanNet](https://doi.org/10.1109/lwc.2022.3162422) | Residual-attention CNN | Candidate if simple |
| 39 | Cross-model | [Ma et al., 2020, Cross Model Deep Learning Scheme for AMC](https://doi.org/10.1109/access.2020.2988727) | Cross-domain/model fusion idea | Low priority |
| 40 | Robust CNN | [Abd-Elaziz et al., 2023, Robust CNN Architecture for Cognitive Radio Networks](https://doi.org/10.3390/s23239467) | CNN baseline and robustness table | Background |
| 41 | GRU | [Utrilla et al., 2020, GRU Neural Networks for AMC with Resource-Constrained End-Devices](https://doi.org/10.1109/access.2020.3002770) | GRU-only temporal baseline | Stage 6B cheap |
| 42 | CNN-LSTM | [Wang et al., 2021, Multidimensional CNN-LSTM Network for AMC](https://doi.org/10.3390/electronics10141649) | Multi-feature CNN-LSTM | Candidate |
| 43 | Hierarchical CNN | [Huang et al., 2021, Hierarchical Digital Modulation Classification Using Cascaded CNN](https://doi.org/10.23919/jcin.2021.9387706) | Class hierarchy for confusing modulations | Later candidate |
| 44 | Gated GCN | [Ghasemzadeh et al., 2023, GGCNN](https://doi.org/10.1109/twc.2023.3239311) | Gated graph convolution | Stage 6D only |
| 45 | Polar features | [Teng et al., 2018, Polar Feature Based Deep Architectures](https://doi.org/10.1109/globalsip.2018.8646375) | Amplitude/phase input support | High-priority feature view |
| 46 | Complex transformer | [Li et al., 2024, Complex-Valued Transformer for AMR](https://doi.org/10.1109/jiot.2024.3379429) | Complex + attention | Later candidate |
| 47 | OFDM parameter estimation | [Park and Han, 2021, DL-Based AMC with Blind OFDM Parameter Estimation](https://doi.org/10.1109/access.2021.3102223) | Parameter-estimation branch idea | Background |
| 48 | Hierarchical RNN | [Zang and Ma, 2020, Hierarchical RNN with Grouped Auxiliary Memory](https://doi.org/10.1109/access.2020.3039543) | RNN memory design | Low priority |
| 49 | Attention CNN-LSTM | [Kumar et al., 2024, OFDM Bi-Stream and Attention-Based CNN-LSTM](https://doi.org/10.1109/lcomm.2023.3348512) | Bi-stream attention temporal model | Candidate pattern |
| 50 | DNN survey/example | [Harper et al., 2023, Automatic Modulation Classification with Deep Neural Networks](https://doi.org/10.3390/electronics12183962) | Recent reproducibility reference | Protocol comparison |
| 51 | Hybrid augmentation | [Wang et al., 2023, Hybrid Data Augmentation and Lightweight Neural Network](https://doi.org/10.3390/s23094187) | Augmentation plus lightweight | Stage 6B screen |
| 52 | Residual OFDM | [Kumar et al., 2023, AMC for Adaptive OFDM Systems Using CNNs with Residual Learning](https://doi.org/10.1109/access.2023.3286939) | Residual CNN transfer idea | Background |
| 53 | Survey | [Wang et al., 2022, Survey of DL in Radio Signal Modulation Recognition](https://doi.org/10.3390/app122312052) | Taxonomy of DL AMR | Literature anchor |
| 54 | CFO/SRO transformer | [Zeng et al., 2024, CNN Assisted Transformer under Large CFOs and SROs](https://doi.org/10.1109/lsp.2024.3372770) | Robust to offsets | Later candidate |
| 55 | Conv-aided transformer | [Hu et al., 2023, Feature Fusion Convolution-Aided Transformer](https://doi.org/10.1109/lcomm.2023.3298941) | Local CNN + global attention | Candidate if small |
| 56 | High-noise fusion | [Han et al., 2021, Deep Feature Fusion for High Noise Level and Large Dynamic Input](https://doi.org/10.3390/s21062117) | Feature fusion under high noise | Fusion design |
| 57 | Satellite CLDNN | [Jiang et al., 2021, Modulation Recognition Based on CLDNN](https://doi.org/10.1109/isie45552.2021.9576379) | CLDNN variant | Background |
| 58 | KD transformer | [Hou et al., 2024, ClST: Convolutional Transformer by Knowledge Distillation](https://doi.org/10.1109/twc.2023.3347537) | Distillation plus transformer | Stage 6D only |
| 59 | CNN approaches | [Hussein et al., 2023, Convolutional DL Neural Networks Approaches](https://doi.org/10.1109/access.2023.3313393) | CNN baseline variants | Background |
| 60 | Pyramid transformer | [He et al., 2022, Pyramid Signal Transformer](https://doi.org/10.1109/globecom48099.2022.10001593) | Efficient signal transformer | Stage 6C maybe |
| 61 | Blind AMR | [Benedetto et al., 2016, Automatic Blind Modulation Recognition](https://doi.org/10.1109/vtcfall.2016.7880915) | Pre-DL AMR baseline context | Background |
| 62 | Complex CRNN | [Ren et al., 2022, Complex-valued Parallel Convolutional Recurrent NNs](https://doi.org/10.1109/cscwd54268.2022.9776161) | Complex + recurrent | Candidate but costlier |
| 63 | Real-time SDR | [Chong et al., 2020, Real-Time Modulation Recognition with Multi-Skip ResNet](https://doi.org/10.1109/access.2020.3043588) | Deployment latency concern | Protocol |
| 64 | Lightweight SE | [Nisar et al., 2023, Lightweight Residual Learning and SE Blocks](https://doi.org/10.3390/app13085145) | SE residual low-cost model | Candidate |
| 65 | Representation techniques | [Liu et al., 2022, Wireless Signal Representation Techniques for AMC](https://doi.org/10.1109/access.2022.3197224) | Representation comparison | Feature selection |
| 66 | FPGA/FINN | [Jentzsch et al., 2022, RadioML Meets FINN](https://doi.org/10.1109/mm.2022.3202091) | Hardware-aware inference | Not Stage 6B |
| 67 | TF-GCN | [Tonchev et al., 2022, GCNs for Time-Frequency Representation](https://doi.org/10.1109/wpmc55625.2022.10014833) | Time-frequency graph design | Stage 6D only |
| 68 | LWAMCNet | [Wang et al., 2021, A Lightweight CNN Architecture for AMC](https://doi.org/10.3390/electronics10212679) | Current LWAMCNet reference | Diagnose current gap |
| 69 | GIGNet | [Ke et al., 2025, Graph-in-Graph Neural Network for AMR](https://doi.org/10.1109/tvt.2025.3542494) | New GNN family | Later only |
| 70 | Combinatorial DL | [El-Khatib et al., 2024, Radio Modulation Classification Optimization](https://doi.org/10.1109/access.2024.3357628) | Hyperparameter/model combination idea | Search-space input |
| 71 | GAN inpainting | [Lee et al., 2023, GAN-Based Signal Inpainting for AMC](https://doi.org/10.1109/access.2023.3279022) | Generative repair/augmentation | Later, not first |
| 72 | Spatial transformer | [Li et al., 2019, Low Parameter Estimation Dependence Based on Spatial Transformer Networks](https://doi.org/10.3390/app9051010) | Learnable alignment | Candidate if offsets dominate |
| 73 | Impulsive noise | [Bai et al., 2024, AMC in Impulsive Noise](https://doi.org/10.1109/tccn.2024.3375510) | Non-AWGN low-SNR robustness | Background |
| 74 | Hybrid GCN transfer | [Suetrong et al., 2024, Enhanced Modulation Recognition Through Deep Transfer Learning in Hybrid GCNs](https://doi.org/10.1109/access.2024.3388490) | Transfer + GCN | Stage 6D only |
| 75 | Unknown interference graph | [Zhang et al., 2024, AMR of Unknown Interference Signals Based on Graph Model](https://doi.org/10.1109/lwc.2024.3401720) | Graph under unknown interference | Later only |
| 76 | Multi-domain fusion | [Hou et al., 2023, Multi-domain-fusion Deep Learning for AMR](https://doi.org/10.1038/s41598-023-37165-2) | IQ/feature-domain fusion | Fusion design |
| 77 | SNR segmentation | [Duan et al., 2023, Multi-Modal Modulation Recognition with SNR Segmentation](https://doi.org/10.3390/electronics12143175) | Explicit SNR-segmented models | Low-SNR route |
| 78 | Domain adaptation | [Wang et al., 2022, AMC Based on CNN and Multiple Kernel MMD](https://doi.org/10.3390/electronics12010066) | Distribution alignment idea | Later |
| 79 | Self-attention | [Zhang et al., 2023, Channel and Spatial Self-Attention Mechanism](https://doi.org/10.1109/access.2023.3292408) | Attention module for CNN features | Candidate |
| 80 | Low-data augmentation | [Wei et al., 2023, Data Augmentation under Low-Data Imbalanced-Class Regime](https://doi.org/10.3390/app13053177) | Imbalance/low-data augmentation | Stage 6B screen |
| 81 | Low-SNR SDR | [Alzaq et al., 2022, Low-SNR Modulation Recognition on SDR](https://doi.org/10.1109/commnet56067.2022.9993934) | Practical low-SNR check | Background |
| 82 | Ultra lightweight | [Wang et al., 2024, Ultra Lightweight Neural Network](https://doi.org/10.1038/s41598-024-72867-1) | Lightweight architecture | Candidate |
| 83 | Complex hybrid | [Xu et al., 2023, Complex-Valued Hybrid Neural Network](https://doi.org/10.3390/electronics12204380) | Complex-valued hybrid model | Candidate |
| 84 | Underwater GCN | [Yao et al., 2023, Feature Fusion GCN for Modulation Classification](https://doi.org/10.3390/e25071096) | GCN fusion concept | Low priority |
| 85 | CVCNN semi-supervised | [Liu et al., 2023, Complex-Valued CNN and Semi-Supervised Learning](https://doi.org/10.1109/icct59356.2023.10419774) | CVCNN plus SSL | Later |
| 86 | Sparse RNN | [Zang et al., 2021, Deep Sparse Learning with RNNs](https://doi.org/10.3390/s21196410) | Sparsity for temporal models | Later |
| 87 | Hybrid transformer | [Ansari et al., 2025, Attention-Enhanced Hybrid AMC](https://doi.org/10.1109/access.2025.3580574) | Recent transformer hybrid | Candidate only after baselines |
| 88 | Complex multistream | [Wang et al., 2024, Complex-Valued Convolutional Fusion-Type Multi-Stream Spatiotemporal Network](https://doi.org/10.1038/s41598-024-73547-w) | Complex + multi-stream + temporal | Strong but costly candidate |
| 89 | Dual-attention transformer | [Yi et al., 2024, Efficient Convolutional Dual-Attention Transformer](https://doi.org/10.1007/s10489-024-06202-6) | Efficient attention design | Later |
| 90 | Mobile transformer | [Fei et al., 2024, MobileAmcT](https://doi.org/10.3390/drones8080357) | Mobile transformer control | Lightweight/attention |
| 91 | Diffusion augmentation | [Diffusion-Based Radio Signal Augmentation for AMC](https://doi.org/10.3390/electronics13112063) | Diffusion augmentation on RadioML2016.10A | Later, high risk |
| 92 | Mixup-style augmentation | [Mixing Signals: Data Augmentation Approach for Deep Learning Based Modulation Recognition](https://arxiv.org/abs/2204.03737) | Signal mixup idea | Stage 6B screen |
| 93 | Knowledge distillation | [MLD-Net: Multi-Level Knowledge Distillation Network for AMR](https://pmc.ncbi.nlm.nih.gov/articles/PMC12694331/) | Teacher-student compression | Stage 6D only |
| 94 | Complex CLDNN | [Research on Communication Signal Modulation Recognition Based on a CCLDNN](https://www.mdpi.com/2079-9292/13/9/1604) | Complex CLDNN variant | Candidate after MCLDNN fix |
| 95 | TCN-LSTM multitask | [CrossTLNet: TCN-LSTM Multitask AMC](https://doi.org/10.3390/electronics12224668) | TCN + LSTM + cross-attention + KD | Candidate |
| 96 | Attention hybrid parallel | [Novel AMC Method Using Attention Mechanism and Hybrid Parallel NN](https://doi.org/10.3390/app11031327) | Raw I/Q plus amplitude/phase and attention | Feature/fusion candidate |
| 97 | Dual-scale fusion | [IDAF: Iterative Dual-Scale Attentional Fusion Network](https://doi.org/10.3390/s23198134) | Fusion and attention across scales | Candidate if simple |
| 98 | TCN-GRU | [Robust AMC via a Lightweight Temporal Hybrid Neural Network](https://doi.org/10.3390/s24247908) | TCN-GRU low-cost temporal hybrid | High-priority candidate |
| 99 | Additive attention | [Improved AMR Using Deep Learning with Additive Attention](https://www.sciencedirect.com/science/article/pii/S2590123025008606) | Efficient attention; compares ResNet/MCLDNN | Candidate after baseline checks |
| 100 | Low-SNR SNR-aware | [KADNet: Low SNR AMC via SNR-Aware Deformable Convolution and KAN](https://www.sciencedirect.com/science/article/pii/S105120042600062X) | Explicit SNR-aware low-SNR design | Concept only for now |

## Literature Trends

The literature has moved from raw-I/Q CNN baselines to hybrid spatiotemporal models, then to complex-valued operators, attention/transformer blocks, multiview signal representations, and deployment-aware compression. The useful point for this project is not that every newer architecture should be implemented. The useful point is that many reported gains combine three factors: model architecture, feature representation, and training/split protocol. Stage 6 must separate those factors.

Complex-valued and amplitude/phase methods are the most directly relevant to RadioML2016.10A because the raw signal is naturally I/Q and phase-rich. They are also more plausible than standalone STFT, since Stage 5 shows STFT-only performance is weak and IQ-only controls are strong.

Temporal hybrids remain a practical sweet spot. CLDNN is already the best current model, and TCN/GRU/CNN-LSTM variants offer a lower-risk extension than full transformer or graph models. The current code can host new 1D temporal models with modest changes.

Transformer and graph methods are numerous, but they are not the first optimization target. They can be compute-heavy, sensitive to patching/tokenization choices, and frequently report under split protocols that are not directly comparable. They should enter only after stronger I/Q and temporal baselines are stable.

Low-SNR papers repeatedly use denoising, SNR-aware branches, SNR segmentation, auxiliary objectives, or sample reweighting. Stage 5 low-SNR accuracy is only around 0.22 for the best stable models, so this is a real gap. The risk is that low-SNR gains can trade away mid/high-SNR accuracy and look better only under cherry-picked SNR slices.

Augmentation papers support cheap Stage 6B screening. Random time shift, phase rotation, amplitude scaling, additive noise calibration, random erasing, and mixup-style signal interpolation are much cheaper than diffusion/GAN. Diffusion/GAN should not be first because generation quality is another experimental burden.

Lightweight papers are useful only if accuracy is not sacrificed beyond the paper's claim. Current LWAMCNet underperforms CLDNN/ResNet by a large margin in this harness, so any lightweight claim needs a strong accuracy-cost trade-off, not parameter count alone.

Benchmark fairness remains a major concern. Papers use different train/test ratios, SNR slices, random splits, and sometimes omit fixed split seeds. This project should keep the fixed stratified-by-modulation-and-SNR split and report multi-seed mean/std. Do not compare a single high-SNR maximum from literature to this project's all-SNR mean.

## Gap Analysis Against Stage 5

The current strongest full-run result is CLDNN, not fusion. That implies Stage 6 should improve or defend an I/Q temporal baseline before claiming multiview superiority.

The current fusion variants slightly help low-SNR in some cells, but static IQ+STFT and gated IQ+STFT both reduce overall, mid-SNR, and high-SNR performance relative to CLDNN, ResNet1D, and parameter-matched I/Q. The core fusion gap is not gate complexity. It is representation and optimization: STFT alone is weak, and the gate does not yet learn a reliable sample-dependent trade-off.

MCLDNN is scientifically important but implementation-unstable. Since seed 42 reaches 0.5684 while seeds 2025 and 3407 collapse to 0.0909, Stage 6 must treat MCLDNN as a diagnostic target, not as a result to clean. A stable-v2 variant can be proposed only with separate naming and separate diagnostic records.

The low-SNR gap is broad. CLDNN low-SNR mean is 0.2224, fusion_iq_stft is 0.2213, and iq_param_matched is 0.2163. Any proposed low-SNR method should target at least +0.01 absolute low-SNR mean over CLDNN and parameter-matched I/Q in subset screening before it deserves full-run consideration.

The lightweight gap is also broad. LWAMCNet is efficient but not competitive in the current harness. A lightweight claim is only credible if a compact model closes most of the CLDNN/ResNet gap or if the paper explicitly frames a Pareto trade-off.

## Code Feasibility Check

Already supported:

- fixed split artifacts and split-source logging;
- model registry for CNN1D, ResNet1D, CLDNN, MCLDNN, LWAMCNet, STFT CNN, static fusion, scalar gated fusion, and parameter-matched I/Q;
- feature views `iq`, `amp_phase`, `stft`, and `cwt` in `SignalDataset`;
- per-SNR/per-class metrics, predictions, confusion outputs, complexity, and controlled latency tooling;
- mock data mode and subset knobs suitable for smoke/diagnostic runs.

Not yet supported or only partially supported:

- true complex-valued convolution/batchnorm/activation modules;
- TCN, GRU, CNN-GRU, CNN-TCN, transformer, or graph models in the registry;
- explicit SNR input to models; the dataloader returns SNR, but the model interface currently receives only `x`;
- augmentation hooks in the training loop;
- distillation loss, teacher checkpoints, or multi-objective training;
- gate logging by SNR/class/correctness for the current scalar gated fusion model;
- Stage 5B aggregate CSVs in this local checkout.

This means Stage 6B should begin with mock forward tests and subset training for small, isolated changes. The fastest implementable candidates are feature-view fusion, low-SNR sampling/loss changes, TCN/GRU modules, and MCLDNN-stable-v2 diagnostics.

## Candidate Experiment Matrix

| Candidate | Expected benefit | Main risk | Code cost | Compute cost | Full-run decision |
|---|---|---|---|---|---|
| CLDNN training-protocol sweep | Improve current best stable baseline | Overfitting to validation seed | Low | Low-medium | Worth Stage 6B |
| ResNet1D large-kernel/SE/MSF variant | Stable I/Q CNN improvement | Marginal gain only | Low-medium | Medium | Worth Stage 6B |
| MCLDNN-stable-v2 | Recover canonical baseline without seed collapse | May still be unstable | Medium | Medium | Diagnostic first |
| IQ + amplitude/phase static fusion | Adds physically meaningful phase/amplitude view | Parameter-matched I/Q may still win | Low | Medium | Worth Stage 6B |
| IQ + amp/phase + scalar/vector gate | More plausible than IQ+STFT gate | Gate collapse | Medium | Medium | Worth after static fusion |
| Complex depthwise CNN | Better inductive bias for I/Q | Complex layers require careful implementation | Medium-high | Medium | Worth Stage 6B mock only first |
| TCN-GRU temporal hybrid | Temporal context with bounded cost | Might duplicate CLDNN | Medium | Medium | Worth Stage 6B |
| CNN-BiGRU / CNN-BiLSTM | Strong temporal baseline | Parameter/latency growth | Medium | Medium-high | Worth only if TCN-GRU promising |
| STFT/CWT-only stronger branch | Better time-frequency baseline | Stage 5 STFT result is weak | Medium | Medium-high | Low priority |
| IQ+STFT+CWT fusion | More complete multiview fusion | Preprocess cost and overfitting | Medium | High | No full run before static IQ+AP |
| Low-SNR reweighting/curriculum | Directly targets largest gap | Can hurt high-SNR | Low | Low | Worth Stage 6B |
| SNR auxiliary head | Learns SNR-aware representation without SNR at inference | Extra loss tuning | Medium | Medium | Worth Stage 6B if model hooks added |
| True-SNR gate | Oracle upper bound | Weak deployment claim | Medium | Medium | Diagnostic/reference only |
| Random shift/phase/amplitude/noise augmentation | Cheap robustness | Wrong augmentation can distort labels | Low-medium | Low | Worth Stage 6B |
| Mixup-style IQ augmentation | Regularization under low data/noise | Ambiguous labels for analog classes | Medium | Low | Screen carefully |
| Denoising autoencoder front-end | Low-SNR robustness | Adds pretraining and artifact complexity | High | High | Later only |
| Diffusion/GAN augmentation | Potential low-data benefit | High experimental burden | High | High | Not Stage 6B |
| Distillation/pruning | Better deployment trade-off | Needs teacher first | Medium-high | Medium | Stage 6D only |
| Transformer small | Global context | Tokenization and compute risk | Medium-high | High | Not before temporal hybrid |
| Graph/time-frequency GNN | Structured TF relation | Highest implementation risk | High | High | Not before Stage 6D |

## Hyperparameter Search Space

Stage 6B should use small grids, not broad AutoML.

Training protocol:

- optimizer: AdamW baseline; one Adam comparison for unstable MCLDNN only;
- learning rate: `1e-3`, `5e-4`, `1e-4`;
- weight decay: `0`, `1e-5`, `1e-4`;
- dropout: `0.1`, `0.3`, `0.5`;
- gradient clipping: none vs `1.0` for recurrent models;
- batch size: keep `256` for comparability unless memory forces otherwise;
- early stopping: keep existing patience for full pilots; do not tune on test.

Low-SNR strategy:

- SNR group weights: low/mid/high = `1/1/1`, `1.5/1/1`, `2/1/1`;
- curriculum: all-SNR from epoch 1 vs first epochs biased to `[-8, 2]` dB, then all SNR;
- loss: cross-entropy vs weighted cross-entropy; focal loss only if weighted CE fails;
- reporting: always all-SNR overall plus low/mid/high, never low-SNR only.

Feature/fusion:

- amp/phase normalization on/off;
- static concat vs scalar gate vs vector gate;
- shared projection dimension: `64`, `128`;
- gate regularization: none first; entropy/balance only if gate collapses;
- STFT/CWT variants only after IQ+amp_phase has been checked.

Architecture:

- TCN channels: `64`, `128`;
- TCN kernel size: `3`, `5`, `7`;
- dilation schedule: `[1,2,4]`, `[1,2,4,8]`;
- GRU hidden: `64`, `128`;
- bidirectional GRU only after unidirectional baseline.

## MCLDNN-Stable-v2 Diagnostic Route

The current MCLDNN implementation uses separate I/Q streams, a joint 2D path, a fusion convolution, a two-layer LSTM, and SELU/dropout classifier layers. The seed-specific collapse suggests an optimization or initialization instability rather than a pure capacity issue.

Diagnostic sequence:

1. Add a separate `mcldnn_stable_v2` model name; do not overwrite `mcldnn`.
2. Run forward-shape and parameter-count unit tests on mock tensors only.
3. Run one-batch overfit on mock data for 20-50 optimizer steps; tag `DIAGNOSTIC`.
4. Compare AdamW vs Adam, learning rates `1e-3`, `5e-4`, `1e-4`, and gradient clipping `1.0`.
5. Replace SELU + standard dropout with ReLU/GELU + dropout or use AlphaDropout if retaining SELU.
6. Add batch/layer normalization after fusion conv and before LSTM if gradients are unstable.
7. Log gradient norms, prediction class histogram, and loss for the first 3 epochs on tiny subset.
8. Only if all three seeds avoid chance-level behavior in subset screening may this variant be considered for a later full run.

The original Stage 5A MCLDNN rows remain untouched and remain in aggregate reporting.

## Stage 6B / 6C / 6D Plan

Stage 6B: mock/subset/smoke screening.

- Allowed: mock forward tests, synthetic smoke tests, tiny real subset runs, and code feasibility checks.
- Suggested limits: seed `42` first; at most 2-3 epochs for smoke; subset with a small number of samples per modulation/SNR group; separate output root such as `results/paper_stage6/diagnostic/...`.
- Required label: every output and report line must include `DIAGNOSTIC` or `SMOKE TEST`.
- No Stage 6B result may enter Stage 5A or Stage 5B main tables.
- Primary candidates: low-SNR weighted CE, IQ+amp_phase static fusion, TCN-GRU, MCLDNN-stable-v2 diagnostics, cheap augmentation.

Stage 6C: controlled subset/pilot protocol after Stage 6B.

- Still not a full run unless explicitly authorized.
- Freeze 3-5 candidates, fixed subset recipe, fixed split derivation, and fixed metric schema.
- Use at least seeds `42` and `2025` for pilot stability if compute allows.
- Add complexity/latency for any model claiming lightweight or deployable.
- Require comparison to CLDNN, ResNet1D, and parameter-matched I/Q in the same harness.

Stage 6D: full-run readiness gate.

- Requires Stage 5B aggregate sync or regeneration.
- Requires exact candidate configs, run roots, artifact list, and no-overwrite checks.
- Full RadioML2016.10A training may begin only after separate user authorization.
- Full-run table must be Stage 6-specific and must not rewrite Stage 5A run artifacts.

## Diagnostic / Smoke Result Exclusion Rules

A result is forbidden from main tables if any of the following is true:

- data mode is `mock`;
- dataset is subsetted, class-filtered, SNR-filtered, or capped by samples per group;
- epochs, seeds, split, artifact schema, latency protocol, or metric schema differ from the frozen full-run protocol;
- model has debug logging, gradient probes, overfit checks, or smoke-only code paths enabled;
- run root includes `diagnostic`, `smoke`, `mock`, `subset`, or `debug`;
- output lacks `split_source=artifact` and the approved full-run `split_id`;
- result was produced while diagnosing MCLDNN-stable-v2 or any unstable model.

Diagnostic results may be summarized qualitatively in Stage 6 planning notes, but they must not be mixed into Stage 5A/5B aggregates.

## Top 5 Recommended Experiments

1. Low-SNR weighted/curriculum training on CLDNN and ResNet1D.
   - Rationale: targets the clearest gap with minimal code change.
   - Full-run path: yes, if subset gains exceed low-SNR seed variance without high-SNR collapse.

2. IQ + amplitude/phase static fusion with parameter-matched I/Q control.
   - Rationale: literature supports polar features and current code already has `amp_phase`.
   - Full-run path: yes, if it beats `iq_param_matched` and CLDNN on low-SNR without mid/high damage.

3. TCN-GRU temporal hybrid.
   - Rationale: lower-risk temporal extension of the winning CLDNN family.
   - Full-run path: yes, if it matches CLDNN overall and improves low/mid SNR in subset.

4. MCLDNN-stable-v2 diagnostic and stabilization.
   - Rationale: MCLDNN is reviewer-recognizable, but current seed collapse blocks fair use.
   - Full-run path: only after diagnostic stability across all three seeds.

5. Complex depthwise or lightweight complex CNN.
   - Rationale: complex-valued inductive bias is strongly aligned with I/Q data and can be kept lightweight.
   - Full-run path: yes, but only after mock/unit validation of complex layers and a subset pilot.

Transformer, graph, diffusion/GAN, and distillation are not top-5 full-run candidates for the next step. They are valid literature directions but have worse cost/risk ratio for this project phase.

## Stage 6B Entry Decision

Stage 6B mock/subset/smoke screening is allowed under the current user constraints.

The allowed Stage 6B work is limited to:

- small mock or subset runs only;
- no RadioML2018.01A;
- no full RadioML2016.10A training;
- separate diagnostic output directories;
- explicit `DIAGNOSTIC` / `SMOKE TEST` labels;
- no changes to Stage 5A/5B artifacts;
- no inclusion of smoke/subset results in the Stage 5A main table.

The recommended Stage 6B first batch is:

| Priority | Candidate | Minimum pass criterion |
|---:|---|---|
| 1 | Low-SNR weighted CE on CLDNN/ResNet1D | no immediate train instability; subset low-SNR improves without high-SNR collapse |
| 2 | IQ+amp_phase static fusion | beats parameter-matched I/Q on subset low-SNR or is dropped |
| 3 | TCN-GRU | forward/overfit smoke passes; subset accuracy competitive with CLDNN |
| 4 | MCLDNN-stable-v2 | no chance-level collapse in tiny subset for seeds 42/2025/3407 |
| 5 | Cheap augmentation | improves subset robustness without label/pathology artifacts |

No candidate should enter a full run until Stage 6B evidence is reviewed and Stage 6C pilot protocol is frozen.
