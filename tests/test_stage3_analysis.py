import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path


def _write_metrics(run_dir: Path, model: str, overall: float, low: float, mid: float, high: float) -> None:
    run_dir.mkdir(parents=True)
    metrics = {
        "model": model,
        "dataset": "RML2016.10A",
        "data_mode": "real",
        "overall_accuracy": overall,
        "low_snr_accuracy": low,
        "mid_snr_accuracy": mid,
        "high_snr_accuracy": high,
        "num_parameters": 123,
        "train_time_seconds": 1.0,
        "inference_time_seconds": 0.1,
        "best_epoch": 1,
        "per_snr_accuracy": {"-20": low, "-6": low + 0.1, "0": mid, "18": high},
        "per_class_accuracy": {"BPSK": overall, "QPSK": overall - 0.1},
        "confusion_matrix": [[1, 0], [0, 1]],
        "normalized_confusion_matrix": [[1.0, 0.0], [0.0, 1.0]],
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")


def test_stage3_low_snr_analysis_script_generates_outputs():
    tmp_path = Path(".pytest_tmp") / f"stage3_analysis_{uuid.uuid4().hex}"
    comparison_dir = tmp_path / "comparison"
    comparison_dir.mkdir(parents=True)
    cnn = tmp_path / "cnn"
    resnet = tmp_path / "resnet"
    fusion = tmp_path / "fusion"
    output = tmp_path / "analysis"

    try:
        _write_metrics(cnn, "cnn1d", 0.50, 0.20, 0.70, 0.80)
        _write_metrics(resnet, "resnet1d", 0.60, 0.21, 0.80, 0.90)
        _write_metrics(fusion, "fusion_iq_stft", 0.58, 0.23, 0.78, 0.85)

        result = subprocess.run(
            [
                sys.executable,
                "scripts/analyze_stage3_low_snr.py",
                "--comparison-dir",
                str(comparison_dir),
                "--cnn1d-run-dir",
                str(cnn),
                "--resnet1d-run-dir",
                str(resnet),
                "--fusion-run-dir",
                str(fusion),
                "--output",
                str(output),
            ],
            check=True,
            text=True,
            capture_output=True,
        )

        assert "fusion_iq_stft - resnet1d low SNR delta: +0.0200" in result.stdout
        assert (output / "stage3_low_snr_summary.csv").exists()
        assert (output / "stage3_low_snr_summary.md").exists()
        assert (output / "stage3_low_snr_summary.json").exists()
        assert (output / "per_snr_accuracy_comparison.png").exists()
        assert (output / "stage3_low_snr_findings.md").exists()

        summary = json.loads((output / "stage3_low_snr_summary.json").read_text(encoding="utf-8"))
        assert summary["best_overall_model"] == "resnet1d"
        assert summary["best_low_snr_model"] == "fusion_iq_stft"
        assert summary["low_snr_confusion_matrix_status"].startswith("pending")
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)
