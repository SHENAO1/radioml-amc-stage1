# Paper-Stage 5A Full RadioML2016.10A Training Report

Date: 2026-05-08T02:18:09
Server repo: `/hy-tmp/radioml-amc-stage1`
Dataset: RadioML2016.10A only
Fixed split: `stratified_by_mod_snr_seed42`
Split NPZ: `data/splits/rml2016a/stratified_by_mod_snr_seed42.npz`
Split summary: `data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json`
Conclusion: GO

## Protocol Guardrails

- RadioML2018.01A was not run.
- Train seeds were restricted to `42`, `2025`, and `3407`.
- Every completed run was validated with `split_source=artifact` and `split_id=stratified_by_mod_snr_seed42`.
- Every completed run contains `config_resolved.yaml`, `metrics_test.json`, per-SNR/per-class metrics, predictions, confusion CSVs, `complexity.json`, `latency.json`, and `training_summary.json`.
- `latency.json` was overwritten after training with controlled CUDA latency schema using warmup `50`, measured `200`, and batch sizes `1` and `256`.
- Results below are full RadioML2016.10A training evidence for completed cells only.
- No claim is made that fusion is comprehensively better than baselines.

## Completion

- Completed cells: 27/27
- Failed or incomplete cells: 0

| Model | Seed | Status | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Best Epoch | Run Dir |
|---|---:|---|---:|---:|---:|---:|---:|---|
| cnn1d | 42 | completed | 0.580977 | 0.208523 | 0.796667 | 0.861894 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42` |
| cnn1d | 2025 | completed | 0.578068 | 0.204602 | 0.793561 | 0.860530 | 18 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025` |
| cnn1d | 3407 | completed | 0.586932 | 0.215398 | 0.796591 | 0.872652 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407` |
| resnet1d | 42 | completed | 0.596273 | 0.203011 | 0.824015 | 0.892879 | 13 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42` |
| resnet1d | 2025 | completed | 0.596068 | 0.207784 | 0.819394 | 0.890455 | 8 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025` |
| resnet1d | 3407 | completed | 0.595409 | 0.206818 | 0.815758 | 0.893182 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407` |
| tfcnn_stft | 42 | completed | 0.505136 | 0.175568 | 0.683788 | 0.765909 | 19 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42` |
| tfcnn_stft | 2025 | completed | 0.508318 | 0.170341 | 0.694242 | 0.773030 | 19 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025` |
| tfcnn_stft | 3407 | completed | 0.505455 | 0.168011 | 0.691894 | 0.768939 | 16 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407` |
| fusion_iq_stft | 42 | completed | 0.575182 | 0.225682 | 0.778939 | 0.837424 | 17 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42` |
| fusion_iq_stft | 2025 | completed | 0.577636 | 0.214318 | 0.790833 | 0.848864 | 12 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025` |
| fusion_iq_stft | 3407 | completed | 0.578477 | 0.223977 | 0.787652 | 0.841970 | 19 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407` |
| cldnn | 42 | completed | 0.612500 | 0.216477 | 0.842500 | 0.910530 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42` |
| cldnn | 2025 | completed | 0.613545 | 0.226420 | 0.839545 | 0.903712 | 17 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025` |
| cldnn | 3407 | completed | 0.612750 | 0.224261 | 0.836742 | 0.906742 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407` |
| mcldnn | 42 | completed | 0.568432 | 0.212102 | 0.772879 | 0.839091 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42` |
| mcldnn | 2025 | completed | 0.090909 | 0.090909 | 0.090909 | 0.090909 | 1 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025` |
| mcldnn | 3407 | completed | 0.090909 | 0.090909 | 0.090909 | 0.090909 | 1 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407` |
| lwamcnet | 42 | completed | 0.549523 | 0.193295 | 0.755152 | 0.818864 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42` |
| lwamcnet | 2025 | completed | 0.553114 | 0.204261 | 0.754470 | 0.816894 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025` |
| lwamcnet | 3407 | completed | 0.550636 | 0.210057 | 0.743258 | 0.812121 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407` |
| iq_param_matched | 42 | completed | 0.594818 | 0.208409 | 0.820227 | 0.884621 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42` |
| iq_param_matched | 2025 | completed | 0.593932 | 0.221932 | 0.806136 | 0.877727 | 20 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025` |
| iq_param_matched | 3407 | completed | 0.594636 | 0.218693 | 0.810076 | 0.880455 | 17 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407` |
| gated_fusion_iq_stft | 42 | completed | 0.571841 | 0.214716 | 0.782652 | 0.837197 | 17 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42` |
| gated_fusion_iq_stft | 2025 | completed | 0.569977 | 0.203580 | 0.789394 | 0.839091 | 16 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025` |
| gated_fusion_iq_stft | 3407 | completed | 0.574023 | 0.215625 | 0.780000 | 0.845909 | 12 | `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407` |

## Aggregate Across Seeds

| Model | Seeds | Overall Mean | Overall Std | Low Mean | Low Std | Mid Mean | Mid Std | High Mean | High Std |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cnn1d | 3 | 0.581992 | 0.004518 | 0.209508 | 0.005465 | 0.795606 | 0.001772 | 0.865025 | 0.006640 |
| resnet1d | 3 | 0.595917 | 0.000451 | 0.205871 | 0.002523 | 0.819722 | 0.004139 | 0.892172 | 0.001495 |
| tfcnn_stft | 3 | 0.506303 | 0.001752 | 0.171307 | 0.003870 | 0.689975 | 0.005485 | 0.769293 | 0.003574 |
| fusion_iq_stft | 3 | 0.577098 | 0.001712 | 0.221326 | 0.006128 | 0.785808 | 0.006158 | 0.842753 | 0.005760 |
| cldnn | 3 | 0.612932 | 0.000546 | 0.222386 | 0.005230 | 0.839596 | 0.002879 | 0.906995 | 0.003416 |
| mcldnn | 3 | 0.250083 | 0.275698 | 0.131307 | 0.069971 | 0.318232 | 0.393735 | 0.340303 | 0.431963 |
| lwamcnet | 3 | 0.551091 | 0.001838 | 0.202538 | 0.008513 | 0.750960 | 0.006679 | 0.815960 | 0.003467 |
| iq_param_matched | 3 | 0.594462 | 0.000468 | 0.216345 | 0.007061 | 0.812146 | 0.007270 | 0.880934 | 0.003472 |
| gated_fusion_iq_stft | 3 | 0.571947 | 0.002025 | 0.211307 | 0.006707 | 0.784015 | 0.004843 | 0.840732 | 0.004582 |

## Failures

- None.

## Anomalies And Review Notes

- mcldnn seed 2025 completed at chance-level overall_accuracy=0.090909; keep as protocol evidence and flag for diagnosis, not selective rerun.
- mcldnn seed 3407 completed at chance-level overall_accuracy=0.090909; keep as protocol evidence and flag for diagnosis, not selective rerun.

## Required Artifact Paths

### cnn1d seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_42/training_summary.json`

### cnn1d seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_2025/training_summary.json`

### cnn1d seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cnn1d/seed_3407/training_summary.json`

### resnet1d seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_42/training_summary.json`

### resnet1d seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_2025/training_summary.json`

### resnet1d seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/resnet1d/seed_3407/training_summary.json`

### tfcnn_stft seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_42/training_summary.json`

### tfcnn_stft seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_2025/training_summary.json`

### tfcnn_stft seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/tfcnn_stft/seed_3407/training_summary.json`

### fusion_iq_stft seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_42/training_summary.json`

### fusion_iq_stft seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_2025/training_summary.json`

### fusion_iq_stft seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/fusion_iq_stft/seed_3407/training_summary.json`

### cldnn seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_42/training_summary.json`

### cldnn seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_2025/training_summary.json`

### cldnn seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/cldnn/seed_3407/training_summary.json`

### mcldnn seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_42/training_summary.json`

### mcldnn seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_2025/training_summary.json`

### mcldnn seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/mcldnn/seed_3407/training_summary.json`

### lwamcnet seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_42/training_summary.json`

### lwamcnet seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_2025/training_summary.json`

### lwamcnet seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/lwamcnet/seed_3407/training_summary.json`

### iq_param_matched seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_42/training_summary.json`

### iq_param_matched seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_2025/training_summary.json`

### iq_param_matched seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/iq_param_matched/seed_3407/training_summary.json`

### gated_fusion_iq_stft seed 42
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_42/training_summary.json`

### gated_fusion_iq_stft seed 2025
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_2025/training_summary.json`

### gated_fusion_iq_stft seed 3407
- `config_resolved.yaml`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/config_resolved.yaml`
- `metrics_test.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/metrics_test.json`
- `metrics_per_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/metrics_per_snr.csv`
- `metrics_per_class.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/metrics_per_class.csv`
- `predictions_test.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/predictions_test.csv`
- `confusion_overall.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/confusion_overall.csv`
- `confusion_low_snr.csv`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/confusion_low_snr.csv`
- `complexity.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/complexity.json`
- `latency.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/latency.json`
- `training_summary.json`: `/hy-tmp/radioml-amc-stage1/results/paper_stage2/rml2016a/gated_fusion_iq_stft/seed_3407/training_summary.json`
