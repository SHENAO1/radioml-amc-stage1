from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


COMPARISON_FIELDS = [
    "model",
    "dataset",
    "data_mode",
    "run_dir",
    "overall_accuracy",
    "low_snr_accuracy",
    "mid_snr_accuracy",
    "high_snr_accuracy",
    "num_parameters",
    "train_time_seconds",
    "inference_time_seconds",
    "best_epoch",
]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def _metric(metrics: dict[str, Any], key: str) -> Any:
    if key in metrics:
        return metrics[key]
    test = metrics.get("test", metrics.get("evaluation", {}))
    if isinstance(test, dict) and key in test:
        return test[key]
    return None


def collect_run_metrics(run_dir: str | Path) -> dict[str, Any]:
    run = Path(run_dir)
    metrics_path = run / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"metrics.json not found: {metrics_path}")
    metrics = _load_json(metrics_path)
    data_summary = metrics.get("dataset_summary", metrics.get("data_summary", {}))
    if not isinstance(data_summary, dict):
        data_summary = {}

    row = {
        "model": metrics.get("model", metrics.get("model_name", "unknown")),
        "dataset": metrics.get("dataset", data_summary.get("metadata", {}).get("dataset", "N/A")),
        "data_mode": metrics.get("data_mode", data_summary.get("mode", "N/A")),
        "run_dir": str(run),
        "overall_accuracy": _metric(metrics, "overall_accuracy"),
        "low_snr_accuracy": _metric(metrics, "low_snr_accuracy"),
        "mid_snr_accuracy": _metric(metrics, "mid_snr_accuracy"),
        "high_snr_accuracy": _metric(metrics, "high_snr_accuracy"),
        "num_parameters": metrics.get("num_parameters"),
        "train_time_seconds": metrics.get("train_time_seconds"),
        "inference_time_seconds": metrics.get("inference_time_seconds"),
        "best_epoch": metrics.get("best_epoch"),
    }
    return row


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_comparison(rows: list[dict[str, Any]], output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / "baseline_comparison.csv"
    md_path = output / "baseline_comparison.md"

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMPARISON_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in COMPARISON_FIELDS})

    lines = [
        "# Baseline Comparison",
        "",
        "| Model | Dataset | Mode | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | Train Time (s) | Inference Time (s) | Run Dir |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row.get("model")),
                    _fmt(row.get("dataset")),
                    _fmt(row.get("data_mode")),
                    _fmt(row.get("overall_accuracy")),
                    _fmt(row.get("low_snr_accuracy")),
                    _fmt(row.get("mid_snr_accuracy")),
                    _fmt(row.get("high_snr_accuracy")),
                    _fmt(row.get("num_parameters")),
                    _fmt(row.get("train_time_seconds")),
                    _fmt(row.get("inference_time_seconds")),
                    _fmt(row.get("run_dir")),
                ]
            )
            + " |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path
