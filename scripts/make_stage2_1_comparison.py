from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import yaml

from _bootstrap import PROJECT_ROOT


FIELDS = [
    "model_name",
    "input_view",
    "run_dir",
    "epochs",
    "seed",
    "overall_acc",
    "low_snr_acc",
    "mid_snr_acc",
    "high_snr_acc",
    "num_params",
    "train_time",
    "inference_time",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Stage 2.1 real-subset ablation comparison bundle.")
    parser.add_argument("--run_dirs", nargs="+", required=True, help="Run directories to include.")
    parser.add_argument("--output", required=True, help="Output directory for Stage 2.1 comparison files.")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)
    return payload if isinstance(payload, dict) else {}


def _metric(metrics: dict[str, Any], key: str) -> Any:
    if key in metrics:
        return metrics[key]
    test = metrics.get("test", metrics.get("evaluation", {}))
    if isinstance(test, dict):
        return test.get(key)
    return None


def _input_view(metrics: dict[str, Any], model_name: str) -> str:
    views = metrics.get("feature_views")
    if isinstance(views, list) and views:
        return "+".join(str(view) for view in views)
    lowered = model_name.lower()
    if lowered in {"cnn1d", "cnn1d_iq", "resnet1d", "resnet1d_iq", "residualcnn1d"}:
        return "iq"
    return "N/A"


def _format(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _notes(metrics: dict[str, Any], config: dict[str, Any]) -> str:
    notes: list[str] = []
    data = metrics.get("dataset_summary", metrics.get("data_summary", {}))
    if isinstance(data, dict):
        metadata = data.get("metadata", {})
        if isinstance(metadata, dict) and metadata.get("subset_mode") is True:
            notes.append("real subset")
        snr_values = data.get("snr_values", [])
        if isinstance(snr_values, list) and not any(int(v) <= -6 for v in snr_values):
            notes.append("low SNR N/A: subset excludes SNR <= -6")
    if metrics.get("data_mode") == "mock":
        notes.append("mock smoke only")
    model_name = str(metrics.get("model", metrics.get("model_name", ""))).lower()
    if model_name in {"cnn1d", "resnet1d", "cnn1d_iq", "resnet1d_iq"}:
        notes.append("Stage 1.6 I/Q baseline")
    if config.get("project", {}).get("seed") is not None:
        notes.append("single seed")
    return "; ".join(notes)


def collect_row(run_dir: Path) -> dict[str, Any]:
    metrics = _load_json(run_dir / "metrics.json")
    config = _load_yaml(run_dir / "config.yaml")
    model_name = str(metrics.get("model", metrics.get("model_name", "unknown")))
    train_cfg = config.get("train", {}) if isinstance(config.get("train", {}), dict) else {}
    project_cfg = config.get("project", {}) if isinstance(config.get("project", {}), dict) else {}
    return {
        "model_name": model_name,
        "input_view": _input_view(metrics, model_name),
        "run_dir": str(run_dir),
        "epochs": train_cfg.get("epochs", len(metrics.get("history", []))),
        "seed": project_cfg.get("seed"),
        "overall_acc": _metric(metrics, "overall_accuracy"),
        "low_snr_acc": _metric(metrics, "low_snr_accuracy"),
        "mid_snr_acc": _metric(metrics, "mid_snr_accuracy"),
        "high_snr_acc": _metric(metrics, "high_snr_accuracy"),
        "num_params": metrics.get("num_parameters"),
        "train_time": metrics.get("train_time_seconds"),
        "inference_time": metrics.get("inference_time_seconds"),
        "notes": _notes(metrics, config),
        "per_snr_accuracy": metrics.get("per_snr_accuracy", metrics.get("test", {}).get("per_snr_accuracy")),
        "per_class_accuracy": metrics.get("per_class_accuracy", metrics.get("test", {}).get("per_class_accuracy")),
        "best_epoch": metrics.get("best_epoch"),
        "best_val_acc": metrics.get("best_val_acc"),
    }


def write_outputs(rows: list[dict[str, Any]], output_dir: Path) -> tuple[Path, Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "stage2_1_ablation_comparison.csv"
    md_path = output_dir / "stage2_1_ablation_comparison.md"
    summary_path = output_dir / "stage2_1_ablation_summary.json"
    notes_path = output_dir / "stage2_1_ablation_notes.md"

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in FIELDS})

    lines = [
        "# Stage 2.1 Real Subset Ablation Comparison",
        "",
        "| Model | Input View | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Params | Epochs | Seed | Train Time (s) | Inference Time (s) | Notes | Run Dir |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _format(row.get("model_name")),
                    _format(row.get("input_view")),
                    _format(row.get("overall_acc")),
                    _format(row.get("low_snr_acc")),
                    _format(row.get("mid_snr_acc")),
                    _format(row.get("high_snr_acc")),
                    _format(row.get("num_params")),
                    _format(row.get("epochs")),
                    _format(row.get("seed")),
                    _format(row.get("train_time")),
                    _format(row.get("inference_time")),
                    _format(row.get("notes")),
                    _format(row.get("run_dir")),
                ]
            )
            + " |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    best = max(rows, key=lambda row: float(row["overall_acc"]) if row.get("overall_acc") is not None else -1.0)
    summary = {
        "stage": "Stage 2.1",
        "dataset_scope": "RadioML2016.10A real subset",
        "single_seed": True,
        "low_snr_available": False,
        "best_model_by_overall_acc": best.get("model_name"),
        "best_overall_acc": best.get("overall_acc"),
        "rows": rows,
    }
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    notes = [
        "# Stage 2.1 Ablation Notes",
        "",
        "- All rows use the real RadioML2016.10A subset unless marked otherwise.",
        "- The subset contains SNR values -2, 0, 2, 4, 6, 8, 10, 12, so low SNR accuracy is N/A and must not be inferred.",
        "- These are single-seed subset results with seed 42.",
        "- Stage 1.6 CNN1D and ResNet1D baseline runs are included as I/Q-only controls.",
        "- `runs/` and checkpoints remain experiment artifacts and are not Git-tracked.",
    ]
    notes_path.write_text("\n".join(notes) + "\n", encoding="utf-8")
    return csv_path, md_path, summary_path, notes_path


def main() -> int:
    args = parse_args()
    rows = [collect_row(_resolve(run_dir)) for run_dir in args.run_dirs]
    output_dir = _resolve(args.output)
    paths = write_outputs(rows, output_dir)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
