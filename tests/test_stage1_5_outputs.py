import json
import shutil
import uuid
from pathlib import Path

import numpy as np

from radioml_amc.data.split import make_splits, summarize_splits
from radioml_amc.reporting.compare_runs import collect_run_metrics, write_comparison
from radioml_amc.training.metrics import evaluate_predictions


def _repo_tmp() -> Path:
    root = Path(__file__).resolve().parents[1]
    path = root / ".pytest_tmp" / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    return path


def test_split_summary_contains_counts_and_ratios():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    snr = np.array([-6, -6, 0, 0, -6, -6, 0, 0])
    splits = make_splits(y, snr, test_size=0.25, val_size=0.25, strategy="stratified_by_mod_snr", seed=42)
    summary = summarize_splits(splits, y, snr, ["BPSK", "QPSK"], "stratified_by_mod_snr", 42)

    assert summary["total_samples"] == 8
    assert set(summary["splits"]) == {"train", "val", "test"}
    assert sum(payload["num_samples"] for payload in summary["splits"].values()) == 8
    assert summary["splits"]["train"]["ratio"] > 0


def test_metrics_include_snr_groups_and_normalized_confusion():
    y_true = np.array([0, 0, 1, 1, 1])
    y_pred = np.array([0, 1, 1, 0, 1])
    snr = np.array([-8, -6, 0, 8, 10])
    metrics = evaluate_predictions(y_true, y_pred, snr, ["BPSK", "QPSK"])

    assert metrics["overall_accuracy"] == 0.6
    assert metrics["low_snr_accuracy"] == 0.5
    assert metrics["mid_snr_accuracy"] == 1.0
    assert metrics["high_snr_accuracy"] == 0.5
    assert "normalized_confusion_matrix" in metrics


def test_compare_runs_writes_markdown_and_csv():
    tmp_path = _repo_tmp()
    try:
        run_dir = tmp_path / "20260507_000000_cnn1d"
        run_dir.mkdir()
        metrics = {
            "model": "cnn1d",
            "dataset": "mock_radioml",
            "data_mode": "mock",
            "overall_accuracy": 0.25,
            "low_snr_accuracy": None,
            "mid_snr_accuracy": 0.25,
            "high_snr_accuracy": 0.25,
            "num_parameters": 123,
            "train_time_seconds": 1.2,
            "inference_time_seconds": 0.1,
            "best_epoch": 1,
        }
        (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")

        row = collect_run_metrics(run_dir)
        csv_path, md_path = write_comparison([row], tmp_path / "comparison")

        assert row["model"] == "cnn1d"
        assert csv_path.exists()
        assert md_path.exists()
        assert "Baseline Comparison" in md_path.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_docs_files_exist():
    root = Path(__file__).resolve().parents[1]
    required = [
        root / "docs" / "STAGE_INDEX.md",
        root / "docs" / "PROGRESS_LOG.md",
        root / "docs" / "EXPERIMENT_LOG.md",
        root / "docs" / "NEXT_STAGE_PROMPTS.md",
        root / "docs" / "stages" / "STAGE_TEMPLATE.md",
        root / "docs" / "stages" / "STAGE_01_LOCAL_MOCK_ENGINEERING.md",
        root / "docs" / "stages" / "STAGE_015_RML2016A_BASELINE.md",
    ]
    for path in required:
        assert path.exists(), path
