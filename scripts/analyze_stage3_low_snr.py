from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _bootstrap import PROJECT_ROOT


DEFAULT_RUNS = {
    "cnn1d": "runs/20260507_192755_cnn1d",
    "resnet1d": "runs/20260507_193019_resnet1d",
    "fusion_iq_stft": "runs/20260507_193548_fusion_iq_stft",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze Stage 3 low-SNR behavior from completed full runs.")
    parser.add_argument(
        "--comparison-dir",
        default="runs/stage2_2_full_ablation_comparison",
        help="Stage 2.2 comparison directory.",
    )
    parser.add_argument("--cnn1d-run-dir", default=DEFAULT_RUNS["cnn1d"], help="Full CNN1D run directory.")
    parser.add_argument("--resnet1d-run-dir", default=DEFAULT_RUNS["resnet1d"], help="Full ResNet1D run directory.")
    parser.add_argument(
        "--fusion-run-dir",
        default=DEFAULT_RUNS["fusion_iq_stft"],
        help="Full fusion_iq_stft run directory.",
    )
    parser.add_argument("--output", default="runs/stage3_low_snr_analysis", help="Output analysis directory.")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def _metrics(run_dir: Path) -> dict[str, Any]:
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError(f"metrics.json not found: {metrics_path}")
    metrics = _load_json(metrics_path)
    metrics["_run_dir"] = str(run_dir)
    return metrics


def _float(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    return float(value) if value is not None else None


def _fmt(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _model_name(metrics: dict[str, Any]) -> str:
    return str(metrics.get("model", metrics.get("model_name", "unknown")))


def _snr_items(metrics: dict[str, Any]) -> list[tuple[int, float]]:
    per_snr = metrics.get("per_snr_accuracy", {})
    if not isinstance(per_snr, dict):
        return []
    return sorted((int(k), float(v)) for k, v in per_snr.items())


def _class_items(metrics: dict[str, Any]) -> list[tuple[str, float]]:
    per_class = metrics.get("per_class_accuracy", {})
    if not isinstance(per_class, dict):
        return []
    return sorted((str(k), float(v)) for k, v in per_class.items())


def _has_predictions(run_dir: Path) -> bool:
    names = {
        "predictions.csv",
        "predictions.json",
        "predictions.npz",
        "test_predictions.csv",
        "test_predictions.json",
        "test_predictions.npz",
    }
    return any((run_dir / name).exists() for name in names)


def build_rows(named_metrics: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for display_name, metrics in named_metrics.items():
        rows.append(
            {
                "model_name": display_name,
                "reported_model": _model_name(metrics),
                "input_view": "I/Q + STFT" if display_name == "fusion_iq_stft" else "I/Q",
                "run_dir": metrics["_run_dir"],
                "overall_acc": _float(metrics, "overall_accuracy"),
                "low_snr_acc": _float(metrics, "low_snr_accuracy"),
                "mid_snr_acc": _float(metrics, "mid_snr_accuracy"),
                "high_snr_acc": _float(metrics, "high_snr_accuracy"),
                "num_params": metrics.get("num_parameters"),
                "train_time_seconds": _float(metrics, "train_time_seconds"),
                "inference_time_seconds": _float(metrics, "inference_time_seconds"),
                "best_epoch": metrics.get("best_epoch"),
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "stage3_low_snr_summary.csv"
    fields = [
        "model_name",
        "input_view",
        "run_dir",
        "overall_acc",
        "low_snr_acc",
        "mid_snr_acc",
        "high_snr_acc",
        "num_params",
        "train_time_seconds",
        "inference_time_seconds",
        "best_epoch",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})
    return path


def plot_per_snr(named_metrics: dict[str, dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "per_snr_accuracy_comparison.png"
    plt.figure(figsize=(9, 5))
    for name, metrics in named_metrics.items():
        items = _snr_items(metrics)
        plt.plot([snr for snr, _ in items], [acc for _, acc in items], marker="o", linewidth=2, label=name)
    plt.axvline(-6, color="#777777", linestyle="--", linewidth=1, label="low SNR boundary")
    plt.xlabel("SNR (dB)")
    plt.ylabel("Accuracy")
    plt.title("Per-SNR Accuracy Comparison")
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()
    return path


def plot_low_mid_high(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "low_mid_high_accuracy_bar.png"
    labels = [str(row["model_name"]) for row in rows]
    groups = ["low_snr_acc", "mid_snr_acc", "high_snr_acc"]
    group_labels = ["Low SNR", "Mid SNR", "High SNR"]
    x = range(len(labels))
    width = 0.24
    plt.figure(figsize=(9, 5))
    for idx, key in enumerate(groups):
        values = [float(row[key]) for row in rows]
        offsets = [pos + (idx - 1) * width for pos in x]
        plt.bar(offsets, values, width=width, label=group_labels[idx])
    plt.xticks(list(x), labels, rotation=10)
    plt.ylim(0, 1.0)
    plt.ylabel("Accuracy")
    plt.title("Low/Mid/High SNR Accuracy")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()
    return path


def plot_tradeoff(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "overall_vs_low_snr_tradeoff.png"
    plt.figure(figsize=(7, 5))
    for row in rows:
        overall = float(row["overall_acc"])
        low = float(row["low_snr_acc"])
        params = float(row.get("num_params") or 1)
        size = max(80.0, min(500.0, params / 300.0))
        plt.scatter(overall, low, s=size, alpha=0.75)
        plt.text(overall + 0.001, low + 0.001, str(row["model_name"]), fontsize=9)
    plt.xlabel("Overall Accuracy")
    plt.ylabel("Low SNR Accuracy")
    plt.title("Overall vs Low-SNR Trade-off")
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()
    return path


def plot_per_class(named_metrics: dict[str, dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "per_class_accuracy_comparison.png"
    classes = [name for name, _ in _class_items(next(iter(named_metrics.values())))]
    model_names = list(named_metrics)
    x = range(len(classes))
    width = 0.24
    plt.figure(figsize=(12, 5.5))
    for idx, model_name in enumerate(model_names):
        per_class = dict(_class_items(named_metrics[model_name]))
        values = [float(per_class.get(cls, 0.0)) for cls in classes]
        offsets = [pos + (idx - 1) * width for pos in x]
        plt.bar(offsets, values, width=width, label=model_name)
    plt.xticks(list(x), classes, rotation=30, ha="right")
    plt.ylim(0, 1.0)
    plt.ylabel("Accuracy")
    plt.title("Per-Class Accuracy Comparison")
    plt.grid(axis="y", linestyle="--", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()
    return path


def _best(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    return max(rows, key=lambda row: float(row[key]))


def _top_snr_gains(
    fusion_metrics: dict[str, Any],
    baseline_metrics: dict[str, Any],
    *,
    limit: int = 5,
) -> list[dict[str, float]]:
    fusion = dict(_snr_items(fusion_metrics))
    baseline = dict(_snr_items(baseline_metrics))
    deltas = [
        {"snr": float(snr), "fusion_minus_resnet": fusion[snr] - baseline[snr]}
        for snr in sorted(set(fusion) & set(baseline))
    ]
    return sorted(deltas, key=lambda item: item["fusion_minus_resnet"], reverse=True)[:limit]


def _class_deltas(fusion_metrics: dict[str, Any], baseline_metrics: dict[str, Any]) -> list[dict[str, Any]]:
    fusion = dict(_class_items(fusion_metrics))
    baseline = dict(_class_items(baseline_metrics))
    return sorted(
        [
            {
                "class_name": class_name,
                "fusion_accuracy": fusion[class_name],
                "resnet_accuracy": baseline[class_name],
                "fusion_minus_resnet": fusion[class_name] - baseline[class_name],
            }
            for class_name in sorted(set(fusion) & set(baseline))
        ],
        key=lambda item: item["fusion_minus_resnet"],
        reverse=True,
    )


def write_markdown(
    rows: list[dict[str, Any]],
    named_metrics: dict[str, dict[str, Any]],
    artifacts: dict[str, str],
    output_dir: Path,
) -> Path:
    path = output_dir / "stage3_low_snr_summary.md"
    best_overall = _best(rows, "overall_acc")
    best_low = _best(rows, "low_snr_acc")
    fusion = next(row for row in rows if row["model_name"] == "fusion_iq_stft")
    resnet = next(row for row in rows if row["model_name"] == "resnet1d")
    low_delta = float(fusion["low_snr_acc"]) - float(resnet["low_snr_acc"])
    overall_delta = float(fusion["overall_acc"]) - float(resnet["overall_acc"])
    mid_delta = float(fusion["mid_snr_acc"]) - float(resnet["mid_snr_acc"])
    high_delta = float(fusion["high_snr_acc"]) - float(resnet["high_snr_acc"])
    top_snr = _top_snr_gains(named_metrics["fusion_iq_stft"], named_metrics["resnet1d"])
    class_deltas = _class_deltas(named_metrics["fusion_iq_stft"], named_metrics["resnet1d"])
    positive_classes = [item for item in class_deltas if item["fusion_minus_resnet"] > 0]

    lines = [
        "# Stage 3 Low-SNR Analysis Summary",
        "",
        "## Metric Table",
        "",
        "| Model | Input View | Overall | Low SNR | Mid SNR | High SNR | Params | Train Time (s) | Inference Time (s) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model_name']} | {row['input_view']} | {_fmt(row['overall_acc'])} | {_fmt(row['low_snr_acc'])} | "
            f"{_fmt(row['mid_snr_acc'])} | {_fmt(row['high_snr_acc'])} | {_fmt(row['num_params'])} | "
            f"{_fmt(row['train_time_seconds'])} | {_fmt(row['inference_time_seconds'])} |"
        )

    lines.extend(
        [
            "",
            "## Direct Answers",
            "",
            f"- Best overall model: `{best_overall['model_name']}` with overall accuracy {_fmt(best_overall['overall_acc'])}.",
            f"- Best low-SNR model: `{best_low['model_name']}` with low-SNR accuracy {_fmt(best_low['low_snr_acc'])}.",
            f"- `fusion_iq_stft` vs ResNet1D low-SNR delta: {low_delta:+.4f} ({low_delta * 100:+.2f} percentage points).",
            f"- `fusion_iq_stft` vs ResNet1D overall delta: {overall_delta:+.4f} ({overall_delta * 100:+.2f} percentage points).",
            f"- Mid-SNR delta: {mid_delta:+.4f}; high-SNR delta: {high_delta:+.4f}. This indicates the low-SNR gain comes with lower mid/high-SNR accuracy in the current training setup.",
            "",
            "## Per-SNR Gain Concentration",
            "",
            "| SNR | fusion_iq_stft - ResNet1D |",
            "|---:|---:|",
        ]
    )
    for item in top_snr:
        lines.append(f"| {int(item['snr'])} | {item['fusion_minus_resnet']:+.4f} |")

    lines.extend(
        [
            "",
            "The strongest fusion gains over ResNet1D occur in the low-to-transition SNR region, especially around -10 dB, -4 dB, and -6 dB. This supports a weak, carefully worded conclusion that STFT features may provide complementary information under noisy conditions.",
            "",
            "## Per-Class Sensitivity",
            "",
            "| Class | fusion_iq_stft | ResNet1D | Delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for item in class_deltas:
        lines.append(
            f"| {item['class_name']} | {item['fusion_accuracy']:.4f} | {item['resnet_accuracy']:.4f} | {item['fusion_minus_resnet']:+.4f} |"
        )
    if positive_classes:
        classes = ", ".join(f"`{item['class_name']}`" for item in positive_classes)
        lines.append("")
        lines.append(f"Classes where STFT fusion is higher than ResNet1D overall: {classes}.")
    else:
        lines.append("")
        lines.append("No class shows higher overall per-class accuracy for STFT fusion than ResNet1D.")

    lines.extend(
        [
            "",
            "## Low-SNR Confusion Matrix Status",
            "",
            "Prediction-level test outputs were not saved in the Stage 2.2 run directories, so low-SNR-only confusion matrices cannot be reconstructed without re-evaluating checkpoints and saving predictions. Existing confusion matrices are full-test-set matrices, not low-SNR-only matrices.",
            "",
            "Pending outputs:",
            "",
            "- `low_snr_confusion_matrix_cnn1d.png`",
            "- `low_snr_confusion_matrix_resnet1d.png`",
            "- `low_snr_confusion_matrix_fusion_iq_stft.png`",
            "",
            "## Artifact Paths",
            "",
        ]
    )
    for name, artifact in artifacts.items():
        lines.append(f"- `{name}`: `{artifact}`")

    lines.extend(
        [
            "",
            "## Report-Safe Conclusion",
            "",
            "On RadioML2016.10A full, ResNet1D remains the strongest overall baseline. The I/Q + STFT fusion model does not improve overall accuracy, but it shows a small low-SNR advantage over both I/Q baselines. This is enough to motivate further low-SNR-focused experiments, but not enough to claim that fusion is generally superior.",
            "",
            "## Over-Strong Conclusions To Avoid",
            "",
            "- Do not claim the fusion model is globally better than CNN1D or ResNet1D.",
            "- Do not claim CWT full ablation is complete.",
            "- Do not claim RadioML2018.01A has been evaluated.",
            "- Do not claim SOTA or paper-level generality from a single-seed course experiment.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_findings(
    rows: list[dict[str, Any]],
    named_metrics: dict[str, dict[str, Any]],
    output_dir: Path,
    *,
    predictions_available: dict[str, bool],
) -> Path:
    path = output_dir / "stage3_low_snr_findings.md"
    fusion = next(row for row in rows if row["model_name"] == "fusion_iq_stft")
    resnet = next(row for row in rows if row["model_name"] == "resnet1d")
    cnn = next(row for row in rows if row["model_name"] == "cnn1d")
    low_delta_resnet = float(fusion["low_snr_acc"]) - float(resnet["low_snr_acc"])
    low_delta_cnn = float(fusion["low_snr_acc"]) - float(cnn["low_snr_acc"])
    overall_delta_resnet = float(fusion["overall_acc"]) - float(resnet["overall_acc"])
    class_deltas = _class_deltas(named_metrics["fusion_iq_stft"], named_metrics["resnet1d"])
    top_positive = [item for item in class_deltas if item["fusion_minus_resnet"] > 0][:5]
    top_negative = list(reversed(class_deltas[-5:]))

    lines = [
        "# Stage 3 Low-SNR Findings",
        "",
        "## Findings",
        "",
        f"1. ResNet1D is the best overall model at {_fmt(resnet['overall_acc'])}.",
        f"2. `fusion_iq_stft` is the best low-SNR model at {_fmt(fusion['low_snr_acc'])}.",
        f"3. `fusion_iq_stft` improves low-SNR accuracy over ResNet1D by {low_delta_resnet:+.4f} ({low_delta_resnet * 100:+.2f} pp) and over CNN1D by {low_delta_cnn:+.4f} ({low_delta_cnn * 100:+.2f} pp).",
        f"4. `fusion_iq_stft` loses overall accuracy against ResNet1D by {overall_delta_resnet:+.4f} ({overall_delta_resnet * 100:+.2f} pp).",
        "5. The current evidence suggests a trade-off: STFT fusion helps the low-SNR segment slightly, but hurts mid/high-SNR accuracy and overall accuracy.",
        "",
        "## Classes More Favorable To STFT Fusion",
        "",
    ]
    if top_positive:
        for item in top_positive:
            lines.append(f"- `{item['class_name']}`: {item['fusion_minus_resnet']:+.4f}")
    else:
        lines.append("- None in overall per-class accuracy.")

    lines.extend(["", "## Classes Less Favorable To STFT Fusion", ""])
    for item in top_negative:
        lines.append(f"- `{item['class_name']}`: {item['fusion_minus_resnet']:+.4f}")

    lines.extend(
        [
            "",
            "## Confusion Matrix Availability",
            "",
            f"- Prediction files available: {predictions_available}",
            "- Low-SNR-only confusion matrices remain pending because Stage 2.2 did not save sample-level predictions.",
            "",
            "## CWT Decision",
            "",
            "CWT full training is not included in the main full table because the current on-the-fly implementation was CPU-bound on RTX 4070 12GB, produced a large NNPACK warning log, and did not reach epoch 1 in a reasonable time. Keeping it optional is methodologically cleaner than reporting an incomplete or unstable run.",
            "",
            "## Recommended Next Step",
            "",
            "For Stage 3.1, prioritize data/training strategy over architecture: use low-SNR weighting or an SNR-balanced sampler on the existing ResNet1D and fusion_iq_stft pipelines before adding more model complexity.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_json(
    rows: list[dict[str, Any]],
    named_metrics: dict[str, dict[str, Any]],
    artifacts: dict[str, str],
    output_dir: Path,
    comparison_dir: Path,
    predictions_available: dict[str, bool],
) -> Path:
    fusion_row = next(row for row in rows if row["model_name"] == "fusion_iq_stft")
    resnet_row = next(row for row in rows if row["model_name"] == "resnet1d")
    summary = {
        "stage": "Stage 3",
        "task": "low_snr_analysis",
        "comparison_dir": str(comparison_dir),
        "rows": rows,
        "best_overall_model": _best(rows, "overall_acc")["model_name"],
        "best_low_snr_model": _best(rows, "low_snr_acc")["model_name"],
        "fusion_minus_resnet_low_snr": float(fusion_row["low_snr_acc"]) - float(resnet_row["low_snr_acc"]),
        "fusion_minus_resnet_overall": float(fusion_row["overall_acc"]) - float(resnet_row["overall_acc"]),
        "fusion_minus_resnet_mid_snr": float(fusion_row["mid_snr_acc"]) - float(resnet_row["mid_snr_acc"]),
        "fusion_minus_resnet_high_snr": float(fusion_row["high_snr_acc"]) - float(resnet_row["high_snr_acc"]),
        "top_snr_gains_vs_resnet": _top_snr_gains(named_metrics["fusion_iq_stft"], named_metrics["resnet1d"]),
        "per_class_deltas_vs_resnet": _class_deltas(named_metrics["fusion_iq_stft"], named_metrics["resnet1d"]),
        "prediction_files_available": predictions_available,
        "low_snr_confusion_matrix_status": "pending: prediction-level test outputs were not saved",
        "artifacts": artifacts,
        "safe_conclusion": (
            "ResNet1D remains the best overall full-data model, while fusion_iq_stft shows a small low-SNR "
            "advantage that motivates further low-SNR-focused experiments."
        ),
    }
    path = output_dir / "stage3_low_snr_summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    comparison_dir = _resolve(args.comparison_dir)
    output_dir = _resolve(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    run_dirs = {
        "cnn1d": _resolve(args.cnn1d_run_dir),
        "resnet1d": _resolve(args.resnet1d_run_dir),
        "fusion_iq_stft": _resolve(args.fusion_run_dir),
    }
    named_metrics = {name: _metrics(path) for name, path in run_dirs.items()}
    rows = build_rows(named_metrics)
    predictions_available = {name: _has_predictions(path) for name, path in run_dirs.items()}

    artifacts = {
        "stage3_low_snr_summary.csv": str(write_csv(rows, output_dir)),
        "per_snr_accuracy_comparison.png": str(plot_per_snr(named_metrics, output_dir)),
        "low_mid_high_accuracy_bar.png": str(plot_low_mid_high(rows, output_dir)),
        "overall_vs_low_snr_tradeoff.png": str(plot_tradeoff(rows, output_dir)),
        "per_class_accuracy_comparison.png": str(plot_per_class(named_metrics, output_dir)),
    }
    artifacts["stage3_low_snr_summary.md"] = str(write_markdown(rows, named_metrics, artifacts, output_dir))
    artifacts["stage3_low_snr_findings.md"] = str(
        write_findings(rows, named_metrics, output_dir, predictions_available=predictions_available)
    )
    artifacts["stage3_low_snr_summary.json"] = str(
        write_json(rows, named_metrics, artifacts, output_dir, comparison_dir, predictions_available)
    )

    print(f"Stage 3 analysis output: {output_dir}")
    print()
    print("| Model | Overall | Low SNR | Mid SNR | High SNR |")
    print("|---|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['model_name']} | {_fmt(row['overall_acc'])} | {_fmt(row['low_snr_acc'])} | "
            f"{_fmt(row['mid_snr_acc'])} | {_fmt(row['high_snr_acc'])} |"
        )
    fusion = next(row for row in rows if row["model_name"] == "fusion_iq_stft")
    resnet = next(row for row in rows if row["model_name"] == "resnet1d")
    print()
    print(
        "fusion_iq_stft - resnet1d low SNR delta: "
        f"{float(fusion['low_snr_acc']) - float(resnet['low_snr_acc']):+.4f}"
    )
    print(
        "fusion_iq_stft - resnet1d overall delta: "
        f"{float(fusion['overall_acc']) - float(resnet['overall_acc']):+.4f}"
    )
    print("Low-SNR confusion matrices: pending unless prediction-level files are generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
