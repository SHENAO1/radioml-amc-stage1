import csv
import json

import numpy as np
import torch

from radioml_amc.data.mock_dataset import generate_mock_radioml
from radioml_amc.data.split import create_split_artifact, load_split_artifact, load_split_summary
from radioml_amc.models.gated_fusion import ScalarGatedIQSTFTFusionNet, count_parameters
from radioml_amc.profiling import measure_latency, summarize_model_complexity
from radioml_amc.reporting.paper_outputs import aggregate_mean_std, write_paper_metric_artifacts


def test_fixed_split_artifact_round_trip(tmp_path):
    _, y, snr, class_names, _ = generate_mock_radioml(num_samples=96, num_classes=4, seed=5)
    splits, npz_path, summary_path = create_split_artifact(
        y=y,
        snr=snr,
        class_names=class_names,
        output_dir=tmp_path,
        strategy="stratified_by_mod_snr",
        seed=42,
        dataset_name="mock_rml",
    )

    loaded = load_split_artifact(npz_path)
    summary = load_split_summary(summary_path)

    assert set(loaded) == {"train", "val", "test"}
    assert np.array_equal(loaded["test"], splits["test"])
    assert summary["dataset"] == "mock_rml"
    assert summary["split_id"] == "stratified_by_mod_snr_seed42"
    assert "modulation_snr_counts" in summary["splits"]["train"]


def test_paper_prediction_and_metric_outputs(tmp_path):
    class_names = ["BPSK", "QPSK", "8PSK"]
    y_true = np.array([0, 1, 2, 1, 0, 2])
    snr = np.array([-8, -6, 0, 2, 8, 10])
    logits = np.array(
        [
            [3.0, 1.0, 0.0],
            [0.2, 2.0, 0.1],
            [0.1, 0.2, 2.0],
            [2.0, 0.1, 0.0],
            [2.0, 0.1, 0.0],
            [0.1, 0.1, 2.0],
        ],
        dtype=np.float32,
    )
    paths = write_paper_metric_artifacts(
        tmp_path,
        logits=logits,
        y_true=y_true,
        snr=snr,
        sample_ids=np.arange(y_true.shape[0]),
        class_names=class_names,
        dataset="mock",
        split_id="split_seed42",
        model_id="demo",
        train_seed=42,
    )

    assert paths["predictions"].exists()
    assert paths["per_snr"].exists()
    assert paths["confusion_low_snr"].exists()
    metrics = json.loads(paths["metrics_test"].read_text(encoding="utf-8"))
    assert metrics["low_snr_accuracy"] == 1.0
    with paths["predictions"].open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["sample_id"] == "0"
    assert "prob_bpsk" in rows[0]


def test_aggregate_mean_std():
    rows = [
        {"model_id": "a", "overall": 0.5, "low": 0.2},
        {"model_id": "a", "overall": 0.7, "low": 0.4},
        {"model_id": "b", "overall": 0.6, "low": 0.3},
    ]
    aggregated = aggregate_mean_std(rows, group_keys=["model_id"], value_keys=["overall", "low"])
    by_model = {row["model_id"]: row for row in aggregated}
    assert by_model["a"]["num_seeds"] == 2
    assert by_model["a"]["overall_mean"] == 0.6
    assert by_model["b"]["overall_std"] == 0.0


def test_scalar_gated_fusion_forward_and_aux():
    model = ScalarGatedIQSTFTFusionNet(num_classes=4)
    x = {
        "iq": torch.randn(3, 2, 128),
        "stft": torch.randn(3, 1, 32, 7),
    }
    output = model.forward_with_aux(x)
    assert output["logits"].shape == (3, 4)
    assert output["gate_scalar"].shape == (3, 1)
    assert torch.all(output["gate_scalar"] >= 0)
    assert torch.all(output["gate_scalar"] <= 1)
    assert count_parameters(model) > 0


def test_complexity_latency_helpers_smoke():
    model = ScalarGatedIQSTFTFusionNet(num_classes=4)
    sample = {
        "iq": torch.randn(1, 2, 128),
        "stft": torch.randn(1, 1, 32, 7),
    }
    complexity = summarize_model_complexity(model, sample, model_id="gated")
    latency = measure_latency(model, sample, model_id="gated", warmup_iters=1, measured_iters=2)
    assert complexity["params_trainable"] > 0
    assert latency["forward_excluding_preprocess_ms"]["mean"] is not None
