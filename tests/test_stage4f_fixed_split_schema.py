import json

import numpy as np
import torch

from radioml_amc.data.dataset import DataBundle
from radioml_amc.data.mock_dataset import generate_mock_radioml
from radioml_amc.data.split import create_split_artifact
from radioml_amc.models.cnn1d import CNN1D
from radioml_amc.profiling import empty_latency_report, measure_latency, summarize_model_complexity
from radioml_amc.training.trainer import _prepare_run, resolve_experiment_splits


def _mock_bundle(num_samples=160, seed=7):
    x, y, snr, mod_names, snr_values = generate_mock_radioml(
        num_samples=num_samples,
        num_classes=4,
        snr_values=[-6, 0, 6, 12],
        seed=seed,
    )
    return DataBundle(
        x=x,
        y=y,
        snr=snr,
        mod_names=mod_names,
        snr_values=snr_values,
        mode="mock",
        metadata={"evidence_tag": "SMOKE TEST"},
    )


def test_fixed_split_artifact_is_independent_of_train_seed(tmp_path):
    bundle = _mock_bundle()
    artifact_splits, npz_path, summary_path = create_split_artifact(
        y=bundle.y,
        snr=bundle.snr,
        class_names=bundle.mod_names,
        output_dir=tmp_path / "splits",
        strategy="stratified_by_mod_snr",
        seed=42,
        dataset_name="mock_rml",
    )
    config = {
        "data": {
            "split_artifact_npz": str(npz_path),
            "split_summary_json": str(summary_path),
            "split_strategy": "stratified_by_mod_snr",
        }
    }

    splits_a, summary_a, split_id_a = resolve_experiment_splits(config, bundle, tmp_path, train_seed=2025)
    splits_b, summary_b, split_id_b = resolve_experiment_splits(config, bundle, tmp_path, train_seed=3407)

    assert split_id_a == "stratified_by_mod_snr_seed42"
    assert split_id_b == "stratified_by_mod_snr_seed42"
    assert summary_a["seed"] == 42
    assert summary_a["train_seed"] == 2025
    assert summary_b["train_seed"] == 3407
    assert summary_a["split_source"] == "artifact"
    assert np.array_equal(splits_a["test"], artifact_splits["test"])
    assert np.array_equal(splits_a["test"], splits_b["test"])


def test_split_seed_can_be_explicit_without_artifact(tmp_path):
    bundle = _mock_bundle()
    config = {
        "data": {
            "split_strategy": "stratified_by_mod_snr",
            "split_seed": 42,
            "test_size": 0.2,
            "val_size": 0.1,
        }
    }

    splits_a, summary_a, split_id_a = resolve_experiment_splits(config, bundle, tmp_path, train_seed=2025)
    splits_b, summary_b, split_id_b = resolve_experiment_splits(config, bundle, tmp_path, train_seed=3407)

    assert split_id_a == split_id_b == "stratified_by_mod_snr_seed42"
    assert summary_a["seed"] == summary_b["seed"] == 42
    assert np.array_equal(splits_a["test"], splits_b["test"])


def test_prepare_run_writes_resolved_config(tmp_path):
    config = {"outputs": {"run_root": str(tmp_path / "runs")}, "train": {"model": "cnn1d"}}
    run_dir, _ = _prepare_run(config, "cnn1d", project_root=None)

    assert (run_dir / "config.yaml").exists()
    resolved_path = run_dir / "config_resolved.yaml"
    assert resolved_path.exists()
    assert "cnn1d" in resolved_path.read_text(encoding="utf-8")


def test_complexity_and_latency_use_v2_schema_keys():
    model = CNN1D(num_classes=4)
    sample = torch.randn(1, 2, 128)

    complexity = summarize_model_complexity(model, sample, model_id="cnn1d", dataset="mock_rml")
    latency = measure_latency(model, sample, model_id="cnn1d", device="cpu", warmup_iters=1, measured_iters=2)
    placeholder = empty_latency_report("cnn1d", status="not_measured")

    assert complexity["dataset"] == "mock_rml"
    assert {"params_trainable", "params_total", "macs", "flops"}.issubset(complexity)
    assert latency["batch_sizes"] == [1]
    assert latency["cpu_including_preprocess_ms"]["batch_1"]["mean"] is not None
    assert "gpu_forward_excluding_preprocess_ms" in latency
    assert "stft_preprocess_ms" in latency
    assert placeholder["batch_sizes"] == [1, 256]
    assert placeholder["cpu_including_preprocess_ms"]["batch_1"]["mean"] is None


def test_latency_schema_is_json_serializable():
    payload = empty_latency_report("demo", status="not_measured", note="schema only")
    encoded = json.dumps(payload)
    assert "gpu_forward_excluding_preprocess_ms" in encoded
