"""Generate course-report figures and table snippets from archived evidence.

This script is read-only with respect to Stage 5A/5B evidence. It consumes
synced CSV/JSON artifacts and writes derived figures/tables under
docs/paper/course_report/.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "docs" / "paper" / "course_report"
FIG_DIR = REPORT_DIR / "figures"
TABLE_DIR = REPORT_DIR / "tables"
AGG_DIR = ROOT / "paper_package" / "server_sync_20260508" / "results" / "paper_stage2" / "rml2016a" / "aggregate"
RUN_DIR = ROOT / "paper_package" / "server_sync_20260508" / "results" / "paper_stage2" / "rml2016a"
STAT_DIR = ROOT / "paper_package" / "statistical_tests_20260508"
PRED_DIR = ROOT / "paper_package" / "predictions_archive_20260508" / "results" / "paper_stage2" / "rml2016a"

SEEDS = [42, 2025, 3407]
KEY_RESULT_MODELS = ["cldnn", "fusion_iq_stft", "iq_param_matched", "resnet1d", "gated_fusion_iq_stft"]


MODEL_ORDER = [
    "cnn1d",
    "resnet1d",
    "tfcnn_stft",
    "fusion_iq_stft",
    "cldnn",
    "mcldnn",
    "lwamcnet",
    "iq_param_matched",
    "gated_fusion_iq_stft",
]

MODEL_LABELS = {
    "cnn1d": "CNN1D",
    "resnet1d": "ResNet1D",
    "tfcnn_stft": "TFCNN-STFT",
    "fusion_iq_stft": "Fusion",
    "cldnn": "CLDNN",
    "mcldnn": "MCLDNN",
    "lwamcnet": "LWAMCNet",
    "iq_param_matched": "IQ matched",
    "gated_fusion_iq_stft": "Gated fusion",
}

COLORS = {
    "iq": "#4C78A8",
    "stft": "#72B7B2",
    "fusion": "#F58518",
    "gated": "#7B4FA1",
    "cldnn": "#2F6B3F",
    "mcldnn": "#9A9A9A",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str, default: float = math.nan) -> float:
    value = row.get(key, "")
    if value == "" or value is None:
        return default
    return float(value)


def pct(value: float) -> str:
    return f"{100 * value:.2f}"


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def tex_path_list(text: str) -> str:
    parts = [part.strip() for part in text.split(";")]
    rendered = []
    for part in parts:
        if any(ch in part for ch in "/_.") and " " not in part:
            rendered.append(rf"\path{{{part}}}")
        else:
            rendered.append(tex_escape(part))
    return "; ".join(rendered)


def tex_evidence_label(label: str) -> str:
    if "_" in label:
        return rf"\path{{{label}}}"
    return tex_escape(label)


def model_color(model_id: str) -> str:
    if model_id == "cldnn":
        return COLORS["cldnn"]
    if model_id == "mcldnn":
        return COLORS["mcldnn"]
    if model_id == "gated_fusion_iq_stft":
        return COLORS["gated"]
    if model_id == "fusion_iq_stft":
        return COLORS["fusion"]
    if model_id == "tfcnn_stft":
        return COLORS["stft"]
    return COLORS["iq"]


def save_fig(fig: plt.Figure, stem: str) -> None:
    for suffix, kwargs in [
        (".pdf", {}),
        (".png", {"dpi": 240}),
    ]:
        fig.savefig(FIG_DIR / f"{stem}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def plot_grouped_accuracy(main_rows: list[dict[str, str]]) -> None:
    rows = {row["model_id"]: row for row in main_rows}
    metrics = [
        ("overall_acc", "Overall"),
        ("low_snr_acc", "Low SNR"),
        ("mid_snr_acc", "Mid SNR"),
        ("high_snr_acc", "High SNR"),
    ]
    x = np.arange(len(MODEL_ORDER))
    width = 0.18
    fig, ax = plt.subplots(figsize=(12, 6.2))
    palette = ["#4C78A8", "#F58518", "#54A24B", "#B279A2"]
    for i, (prefix, label) in enumerate(metrics):
        vals = [f(rows[m], f"{prefix}_mean") for m in MODEL_ORDER]
        errs = [f(rows[m], f"{prefix}_std", 0.0) for m in MODEL_ORDER]
        ax.bar(x + (i - 1.5) * width, vals, width, yerr=errs, capsize=2.5, label=label, color=palette[i], alpha=0.88)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("Accuracy")
    ax.set_xticks(x)
    ax.set_xticklabels([MODEL_LABELS[m] for m in MODEL_ORDER], rotation=35, ha="right")
    ax.set_title("Stage 5A/5B fixed-split accuracy by SNR group")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.12), frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.01, -0.26, "Data source: main_table_metrics.csv; values are mean +/- std across seeds 42, 2025, 3407.",
            transform=ax.transAxes, fontsize=9)
    save_fig(fig, "fig04_accuracy_by_snr_group")


def plot_low_snr_curve(low_rows: list[dict[str, str]]) -> None:
    rows = {row["model_id"]: row for row in low_rows}
    selected = ["cldnn", "fusion_iq_stft", "iq_param_matched", "resnet1d", "gated_fusion_iq_stft"]
    snrs = [-20, -18, -16, -14, -12, -10, -8, -6]
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    for model_id in selected:
        vals = [f(rows[model_id], f"snr_m{abs(s)}_acc_mean") for s in snrs]
        ax.plot(snrs, vals, marker="o", linewidth=2.0, label=MODEL_LABELS[model_id], color=model_color(model_id))
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.06, 0.58)
    ax.set_xticks(snrs)
    ax.set_title("Low-SNR per-SNR accuracy")
    ax.grid(alpha=0.28)
    ax.legend(frameon=False, ncol=2)
    ax.text(0.0, -0.2, "Data source: low_snr_table.csv; low-SNR scope is snr_db <= -6.",
            transform=ax.transAxes, fontsize=9)
    save_fig(fig, "fig05_low_snr_per_snr_curve")


def plot_bootstrap_forest(test_rows: list[dict[str, str]]) -> None:
    scopes = ["overall", "low_snr"]
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6), sharex=True)
    for ax, scope in zip(axes, scopes):
        scoped = [row for row in test_rows if row["scope"] == scope]
        labels = [f"{MODEL_LABELS[row['model_a']]} - {MODEL_LABELS[row['model_b']]}" for row in scoped]
        means = np.array([f(row, "mean_delta") for row in scoped])
        lows = np.array([f(row, "ci95_lower") for row in scoped])
        highs = np.array([f(row, "ci95_upper") for row in scoped])
        y = np.arange(len(scoped))
        colors = ["#9A9A9A" if row["crosses_zero"] == "True" else "#4C78A8" for row in scoped]
        ax.axvline(0.0, color="black", linewidth=1.0)
        ax.errorbar(means, y, xerr=[means - lows, highs - means], fmt="none", ecolor="#333333", capsize=3, linewidth=1)
        ax.scatter(means, y, s=45, color=colors, zorder=3)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.invert_yaxis()
        ax.grid(axis="x", alpha=0.24)
        ax.set_title("Overall" if scope == "overall" else "Low SNR")
        ax.set_xlabel("Accuracy delta")
    fig.suptitle("Paired bootstrap accuracy deltas with 95% CI", y=1.02)
    fig.text(0.06, -0.02, "Data source: paired_bootstrap_accuracy_deltas.csv; delta = acc(model_a) - acc(model_b).",
             fontsize=9)
    save_fig(fig, "fig06_bootstrap_delta_forest")


def plot_accuracy_latency_bubble(main_rows: list[dict[str, str]], complexity_rows: list[dict[str, str]]) -> None:
    main = {row["model_id"]: row for row in main_rows}
    complexity = {row["model_id"]: row for row in complexity_rows}
    fig, ax = plt.subplots(figsize=(8.8, 5.8))
    for model_id in MODEL_ORDER:
        x = f(complexity[model_id], "gpu_forward_excl_pre_batch_1_mean_mean_across_seeds")
        y = f(main[model_id], "overall_acc_mean")
        params = f(main[model_id], "params_trainable")
        size = 80 + params / 1800
        ax.scatter(x, y, s=size, color=model_color(model_id), edgecolor="white", linewidth=0.8, alpha=0.85)
        dx = 0.025
        dy = 0.006 if model_id != "mcldnn" else -0.025
        ax.text(x + dx, y + dy, MODEL_LABELS[model_id], fontsize=8)
    ax.set_xlabel("Batch-1 CUDA forward latency (ms)")
    ax.set_ylabel("Overall accuracy")
    ax.set_title("Accuracy-latency-parameter trade-off")
    ax.grid(alpha=0.25)
    ax.text(0.02, -0.22, "Data sources: main_table_metrics.csv and complexity_latency_table.csv. "
            "CONTROLLED_LATENCY only; STFT preprocessing excluded.",
            transform=ax.transAxes, fontsize=9)
    save_fig(fig, "fig07_accuracy_latency_params_bubble")


def read_confusion(model_id: str, filename: str = "confusion_low_snr.csv") -> tuple[list[str], np.ndarray]:
    total = None
    labels = None
    for seed in SEEDS:
        path = RUN_DIR / model_id / f"seed_{seed}" / filename
        rows = read_csv(path)
        current_labels = [row["true_modulation"] for row in rows]
        pred_cols = [c for c in rows[0] if c.startswith("pred_")]
        matrix = np.array([[float(row[c]) for c in pred_cols] for row in rows], dtype=float)
        if total is None:
            total = matrix
            labels = current_labels
        else:
            total += matrix
    assert total is not None and labels is not None
    row_sums = total.sum(axis=1, keepdims=True)
    normalized = np.divide(total, row_sums, out=np.zeros_like(total), where=row_sums != 0)
    return labels, normalized


def plot_confusion_panels() -> None:
    selected = ["cldnn", "fusion_iq_stft", "iq_param_matched", "gated_fusion_iq_stft"]
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 9.4))
    labels = []
    im = None
    for ax, model_id in zip(axes.flat, selected):
        labels, matrix = read_confusion(model_id)
        im = ax.imshow(matrix, cmap="Blues", vmin=0.0, vmax=1.0)
        ax.set_title(MODEL_LABELS[model_id])
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.85)
    cbar.set_label("Row-normalized share")
    fig.suptitle("Low-SNR normalized confusion matrices (aggregated across seeds)", y=0.98)
    fig.text(0.08, 0.02, "Data source: confusion_low_snr.csv for seeds 42, 2025, and 3407.",
             fontsize=9)
    save_fig(fig, "fig08_low_snr_confusion_panels")


def plot_mcldnn_anomaly() -> None:
    overall = []
    macro = []
    for seed in SEEDS:
        with (RUN_DIR / "mcldnn" / f"seed_{seed}" / "metrics_test.json").open(encoding="utf-8") as fobj:
            data = json.load(fobj)
        overall.append(data["overall_accuracy"])
        macro.append(data["macro_f1"])
    x = np.arange(len(SEEDS))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ax.bar(x - width / 2, overall, width, label="Overall accuracy", color="#4C78A8")
    ax.bar(x + width / 2, macro, width, label="Macro-F1", color="#F58518")
    ax.axhline(1 / 11, color="#777777", linestyle="--", linewidth=1.2, label="Chance level (1/11)")
    ax.set_xticks(x)
    ax.set_xticklabels([str(seed) for seed in SEEDS])
    ax.set_ylim(0, 0.65)
    ax.set_xlabel("Training seed")
    ax.set_ylabel("Metric")
    ax.set_title("MCLDNN retained seed-level anomaly")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.25)
    ax.text(0.0, -0.24, "Data source: mcldnn/seed_*/metrics_test.json. Seeds 2025 and 3407 are retained negative evidence.",
            transform=ax.transAxes, fontsize=9)
    save_fig(fig, "fig09_mcldnn_seed_anomaly")


def aggregate_metric_per_snr(model_id: str) -> tuple[np.ndarray, dict[str, np.ndarray], dict[str, np.ndarray]]:
    values: dict[int, dict[str, list[float]]] = {}
    for seed in SEEDS:
        rows = read_csv(RUN_DIR / model_id / f"seed_{seed}" / "metrics_per_snr.csv")
        for row in rows:
            snr = int(float(row["snr_db"]))
            values.setdefault(snr, {"accuracy": [], "macro_f1": []})
            values[snr]["accuracy"].append(float(row["accuracy"]))
            values[snr]["macro_f1"].append(float(row["macro_f1"]))
    snrs = np.array(sorted(values), dtype=int)
    means = {
        metric: np.array([np.mean(values[int(snr)][metric]) for snr in snrs])
        for metric in ["accuracy", "macro_f1"]
    }
    stds = {
        metric: np.array([np.std(values[int(snr)][metric], ddof=0) for snr in snrs])
        for metric in ["accuracy", "macro_f1"]
    }
    return snrs, means, stds


def plot_full_snr_metric_curves() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.4), sharex=True, sharey=True)
    for model_id in KEY_RESULT_MODELS:
        snrs, means, stds = aggregate_metric_per_snr(model_id)
        color = model_color(model_id)
        for ax, metric, title in zip(axes, ["accuracy", "macro_f1"], ["Accuracy", "Macro-F1"]):
            y = means[metric]
            err = stds[metric]
            ax.plot(snrs, y, marker="o", linewidth=2.0, markersize=4, color=color, label=MODEL_LABELS[model_id])
            ax.fill_between(snrs, np.maximum(0, y - err), np.minimum(1, y + err), color=color, alpha=0.12, linewidth=0)
            ax.set_title(title)
            ax.set_xlabel("SNR (dB)")
            ax.grid(alpha=0.25)
    axes[0].set_ylabel("Metric value")
    for ax in axes:
        ax.set_ylim(0.0, 1.0)
        ax.set_xticks(snrs)
        ax.tick_params(axis="x", labelrotation=45)
    axes[1].legend(frameon=False, fontsize=8, loc="lower right")
    fig.suptitle("Per-SNR performance across the full RadioML2016.10A test range", y=1.02)
    fig.text(0.06, -0.02, "Data source: metrics_per_snr.csv for seeds 42, 2025, and 3407; bands show across-seed std.",
             fontsize=9)
    save_fig(fig, "fig11_full_snr_accuracy_macro_f1")


def plot_model_class_accuracy_heatmap() -> None:
    first_rows = read_csv(RUN_DIR / MODEL_ORDER[0] / "seed_42" / "metrics_per_class.csv")
    class_labels = [row["modulation"] for row in first_rows]
    matrix = []
    for model_id in MODEL_ORDER:
        by_class = {label: [] for label in class_labels}
        for seed in SEEDS:
            rows = read_csv(RUN_DIR / model_id / f"seed_{seed}" / "metrics_per_class.csv")
            for row in rows:
                by_class[row["modulation"]].append(float(row["accuracy"]))
        matrix.append([np.mean(by_class[label]) for label in class_labels])
    data = np.array(matrix)
    fig, ax = plt.subplots(figsize=(10.8, 5.8))
    im = ax.imshow(data, cmap="YlGnBu", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(np.arange(len(class_labels)))
    ax.set_yticks(np.arange(len(MODEL_ORDER)))
    ax.set_xticklabels(class_labels, rotation=45, ha="right")
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODEL_ORDER])
    ax.set_title("Overall class accuracy by model")
    cbar = fig.colorbar(im, ax=ax, shrink=0.88)
    cbar.set_label("Accuracy")
    ax.text(0.0, -0.24, "Data source: metrics_per_class.csv for seeds 42, 2025, and 3407.",
            transform=ax.transAxes, fontsize=9)
    save_fig(fig, "fig12_model_class_accuracy_heatmap")


def plot_low_snr_class_delta() -> None:
    labels, fusion = read_confusion("fusion_iq_stft", "confusion_low_snr.csv")
    _, iq_matched = read_confusion("iq_param_matched", "confusion_low_snr.csv")
    _, cldnn = read_confusion("cldnn", "confusion_low_snr.csv")
    deltas = np.vstack([
        np.diag(fusion) - np.diag(iq_matched),
        np.diag(fusion) - np.diag(cldnn),
    ])
    max_abs = max(0.02, float(np.max(np.abs(deltas))))
    fig, ax = plt.subplots(figsize=(11.4, 2.8))
    im = ax.imshow(deltas, cmap="RdBu_r", vmin=-max_abs, vmax=max_abs, aspect="auto")
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(["Fusion - IQ matched", "Fusion - CLDNN"])
    ax.set_title("Low-SNR per-class recall deltas")
    for y in range(deltas.shape[0]):
        for x in range(deltas.shape[1]):
            ax.text(x, y, f"{100 * deltas[y, x]:+.1f}", ha="center", va="center", fontsize=7)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Recall delta")
    ax.text(0.0, -0.48, "Data source: confusion_low_snr.csv aggregated across seeds 42, 2025, and 3407.",
            transform=ax.transAxes, fontsize=9)
    save_fig(fig, "fig13_low_snr_class_recall_delta")


def read_prediction_correctness(model_id: str, seed: int) -> dict[str, tuple[int, bool]]:
    rows = read_csv(PRED_DIR / model_id / f"seed_{seed}" / "predictions_test.csv")
    return {
        row["sample_id"]: (int(float(row["snr_db"])), row["correct"] in {"1", "True", "true"})
        for row in rows
    }


def paired_disagreement_by_snr(model_a: str, model_b: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    counts: dict[int, dict[str, int]] = {}
    for seed in SEEDS:
        pred_a = read_prediction_correctness(model_a, seed)
        pred_b = read_prediction_correctness(model_b, seed)
        common_ids = pred_a.keys() & pred_b.keys()
        for sample_id in common_ids:
            snr, correct_a = pred_a[sample_id]
            snr_b, correct_b = pred_b[sample_id]
            if snr != snr_b:
                raise ValueError(f"SNR mismatch for {model_a}/{model_b} seed {seed} sample {sample_id}")
            item = counts.setdefault(snr, {"n": 0, "a_only": 0, "b_only": 0})
            item["n"] += 1
            if correct_a and not correct_b:
                item["a_only"] += 1
            elif correct_b and not correct_a:
                item["b_only"] += 1
    snrs = np.array(sorted(counts), dtype=int)
    a_only = np.array([counts[int(s)]["a_only"] / counts[int(s)]["n"] for s in snrs])
    b_only = np.array([counts[int(s)]["b_only"] / counts[int(s)]["n"] for s in snrs])
    return snrs, a_only, b_only


def plot_paired_disagreement_by_snr() -> None:
    pairs = [
        ("fusion_iq_stft", "cldnn"),
        ("fusion_iq_stft", "iq_param_matched"),
        ("gated_fusion_iq_stft", "fusion_iq_stft"),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(11.2, 8.4), sharex=True)
    for ax, (model_a, model_b) in zip(axes, pairs):
        snrs, a_only, b_only = paired_disagreement_by_snr(model_a, model_b)
        width = 1.2
        ax.axhline(0.0, color="#333333", linewidth=0.8)
        ax.bar(snrs - width / 4, a_only, width=width / 2, color=model_color(model_a), alpha=0.85,
               label=f"{MODEL_LABELS[model_a]} correct only")
        ax.bar(snrs + width / 4, -b_only, width=width / 2, color=model_color(model_b), alpha=0.85,
               label=f"{MODEL_LABELS[model_b]} correct only")
        ax.set_ylabel("Share")
        ax.set_title(f"{MODEL_LABELS[model_a]} vs {MODEL_LABELS[model_b]}")
        ax.grid(axis="y", alpha=0.22)
        ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper left")
    axes[-1].set_xticks(snrs)
    axes[-1].tick_params(axis="x", labelrotation=45)
    axes[-1].set_xlabel("SNR (dB)")
    fig.suptitle("Paired correctness disagreements by SNR", y=0.995)
    fig.text(0.06, -0.01, "Data source: predictions_test.csv in predictions_archive_20260508; positive bars favor the first model in each panel.",
             fontsize=9)
    save_fig(fig, "fig14_paired_disagreement_by_snr")


def plot_seed_stability_all_models() -> None:
    metrics = [("overall_accuracy", "Overall accuracy"), ("low_snr_accuracy", "Low-SNR accuracy")]
    fig, axes = plt.subplots(2, 1, figsize=(11.4, 7.2), sharex=True, sharey=True)
    x = np.arange(len(MODEL_ORDER))
    jitter = {42: -0.18, 2025: 0.0, 3407: 0.18}
    for ax, (metric, title) in zip(axes, metrics):
        for idx, model_id in enumerate(MODEL_ORDER):
            vals = []
            for seed in SEEDS:
                with (RUN_DIR / model_id / f"seed_{seed}" / "metrics_test.json").open(encoding="utf-8") as fobj:
                    data = json.load(fobj)
                vals.append(float(data[metric]))
                ax.scatter(idx + jitter[seed], data[metric], s=42, color=model_color(model_id),
                           edgecolor="white", linewidth=0.6, zorder=3)
            ax.vlines(idx, min(vals), max(vals), color=model_color(model_id), alpha=0.45, linewidth=2)
        ax.axhline(1 / 11, color="#777777", linestyle="--", linewidth=1.0)
        ax.set_ylabel(title)
        ax.grid(axis="y", alpha=0.24)
        ax.set_ylim(0.0, 0.95)
    axes[0].set_title("Seed-level stability across all model rows")
    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels([MODEL_LABELS[m] for m in MODEL_ORDER], rotation=35, ha="right")
    axes[-1].set_xlabel("Model row")
    fig.text(0.06, -0.01, "Data source: seed-level metrics_test.json for seeds 42, 2025, and 3407; dashed line is chance level (1/11).",
             fontsize=9)
    save_fig(fig, "fig15_seed_stability_all_models")


def plot_overall_confusion_panels() -> None:
    selected = ["cldnn", "fusion_iq_stft", "iq_param_matched", "gated_fusion_iq_stft"]
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 9.4))
    labels = []
    im = None
    for ax, model_id in zip(axes.flat, selected):
        labels, matrix = read_confusion(model_id, "confusion_overall.csv")
        im = ax.imshow(matrix, cmap="Blues", vmin=0.0, vmax=1.0)
        ax.set_title(MODEL_LABELS[model_id])
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=7)
        ax.set_yticklabels(labels, fontsize=7)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
    cbar = fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.85)
    cbar.set_label("Row-normalized share")
    fig.suptitle("Overall normalized confusion matrices (aggregated across seeds)", y=0.98)
    fig.text(0.08, 0.02, "Data source: confusion_overall.csv for seeds 42, 2025, and 3407.",
             fontsize=9)
    save_fig(fig, "fig16_overall_confusion_panels")


def write_literature_table() -> None:
    rows = [
        ("O'Shea 2016", "https://arxiv.org/abs/1602.04105", "Y", "Y", "-", "-", "-", "RadioML/CNN baseline and SNR curves"),
        ("Deep architectures 2017", "https://arxiv.org/abs/1712.00443", "Y", "Y", "Y", "Y", "Y", "Baseline families and experiment tables"),
        ("Polar features 2018", "https://arxiv.org/abs/1810.02027", "Y", "Y", "-", "-", "Y", "Alternative I/Q-derived views"),
        ("Fast DL AMC 2019", "https://arxiv.org/abs/1901.05850", "Y", "Y", "-", "-", "Y", "Efficiency-aware reporting"),
        ("SCRNN 2019", "https://arxiv.org/abs/1909.03050", "Y", "Y", "-", "-", "Y", "CNN/RNN model comparison"),
        ("Data augmentation 2019", "https://arxiv.org/abs/1912.03026", "-", "Y", "-", "Y", "Y", "Ablation and robustness framing"),
        ("Constellation CNN 2020", "https://arxiv.org/abs/2009.02026", "Y", "Y", "Y", "-", "-", "Non-I/Q visual representation"),
        ("Complex CNN 2020", "https://arxiv.org/abs/2010.10717", "Y", "Y", "-", "-", "Y", "Complex-valued model framing"),
        ("Multi-scale networks 2021", "https://arxiv.org/abs/2105.15037", "Y", "Y", "-", "Y", "Y", "Multi-scale architecture figure"),
        ("Involution ResNet 2021", "https://arxiv.org/abs/2108.10001", "Y", "Y", "-", "-", "Y", "Residual baseline variant"),
        ("Time-frequency attention 2021", "https://arxiv.org/abs/2111.03258", "Y", "Y", "-", "Y", "Y", "Time-frequency attention evidence"),
        ("Adaptive fusion 2022", "https://arxiv.org/abs/2203.03140", "Y", "Y", "-", "Y", "Y", "Fusion architecture and ablation"),
        ("Ultra Lite CNN 2022", "https://arxiv.org/abs/2208.04659", "Y", "Y", "-", "Y", "Y", "Lightweight complexity table"),
        ("SE-MSFN 2022", "https://arxiv.org/abs/2209.03764", "Y", "Y", "-", "Y", "Y", "Attention/multi-scale result curves"),
        ("Harper 2023", "https://arxiv.org/abs/2301.11773", "Y", "Y", "Y", "Y", "Y", "Systematic benchmark style"),
        ("AMC-Net 2023", "https://arxiv.org/abs/2304.00445", "Y", "Y", "-", "Y", "Y", "Dedicated AMC network comparison"),
        ("MAMCA 2024", "https://arxiv.org/abs/2405.11263", "Y", "Y", "-", "Y", "Y", "Accuracy/efficiency trade-off"),
        ("UQ-AMC 2025", "https://arxiv.org/abs/2503.04142", "Y", "Y", "-", "-", "Y", "Reliability and uncertainty framing"),
        ("G-AMC 2026", "https://arxiv.org/abs/2604.06402", "Y", "Y", "-", "Y", "Y", "Green/lightweight framing"),
        ("HFECNET-CA/IDAF", "https://www.mdpi.com/2079-9292/12/17/3661", "Y", "Y", "Y", "Y", "Y", "Open-access module and figure exemplars"),
    ]
    lines = [
        r"\begingroup",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\begin{longtable}{p{0.18\textwidth}>{\centering\arraybackslash}p{0.07\textwidth}>{\centering\arraybackslash}p{0.07\textwidth}>{\centering\arraybackslash}p{0.08\textwidth}>{\centering\arraybackslash}p{0.06\textwidth}>{\centering\arraybackslash}p{0.07\textwidth}p{0.27\textwidth}}",
        r"\caption{开放 AMC 论文中的常见图表模式与本文图表设计对应关系}\label{tab:literature-figure-patterns}\\",
        r"\toprule",
        r"文献线索 & 结构图 & SNR 曲线 & 混淆矩阵 & 消融 & 复杂度 & 对本文图表设计的作用 \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"文献线索 & 结构图 & SNR 曲线 & 混淆矩阵 & 消融 & 复杂度 & 对本文图表设计的作用 \\",
        r"\midrule",
        r"\endhead",
    ]
    for name, url, arch, snr, conf, abl, complexity, role in rows:
        lines.append(
            rf"\href{{{url}}}{{{tex_escape(name)}}} & {arch} & {snr} & {conf} & {abl} & {complexity} & {tex_escape(role)} \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup"])
    (TABLE_DIR / "literature_figure_patterns.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure_evidence_table() -> None:
    rows = [
        ("Fig. 1", "fig01_protocol_pipeline.tex", "Protocol docs, manifest, statistical package", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 2", "fig02_model_taxonomy.tex", "main_table_metrics.csv; code registry", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 3", "fig03_fusion_architecture.tex", "src/radioml_amc/models", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 4", "fig04_accuracy_by_snr_group.pdf", "main_table_metrics.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 5", "fig05_low_snr_per_snr_curve.pdf", "low_snr_table.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 6", "fig06_bootstrap_delta_forest.pdf", "paired_bootstrap_accuracy_deltas.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 7", "fig07_accuracy_latency_params_bubble.pdf", "main_table_metrics.csv; complexity_latency_table.csv", "CONTROLLED_LATENCY", "正文"),
        ("Fig. 8", "fig08_low_snr_confusion_panels.pdf", "confusion_low_snr.csv", "PROJECT_SUPPORTED", "附录"),
        ("Fig. 9", "fig09_mcldnn_seed_anomaly.pdf", "mcldnn/seed_*/metrics_test.json", "PROJECT_SUPPORTED", "附录"),
        ("Fig. 10", "fig10_evidence_boundary.tex", "REPORT_EVIDENCE_MAP.md; environment audit", "Mixed labels", "附录"),
        ("Fig. 11", "fig11_full_snr_accuracy_macro_f1.pdf", "metrics_per_snr.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 12", "fig12_model_class_accuracy_heatmap.pdf", "metrics_per_class.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 13", "fig13_low_snr_class_recall_delta.pdf", "confusion_low_snr.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 14", "fig14_paired_disagreement_by_snr.pdf", "predictions_test.csv", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 15", "fig15_seed_stability_all_models.pdf", "metrics_test.json", "PROJECT_SUPPORTED", "正文"),
        ("Fig. 16", "fig16_overall_confusion_panels.pdf", "confusion_overall.csv", "PROJECT_SUPPORTED", "附录"),
    ]
    lines = [
        r"\begingroup",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\begin{longtable}{p{0.08\textwidth}p{0.25\textwidth}p{0.28\textwidth}p{0.20\textwidth}p{0.07\textwidth}}",
        r"\caption{模型与图表证据源映射表}\label{tab:figure-evidence-map}\\",
        r"\toprule",
        r"图号 & 文件 & 主要数据源 & 证据标签 & 使用位置 \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"图号 & 文件 & 主要数据源 & 证据标签 & 使用位置 \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        fig_no, filename, source, label, location = row
        lines.append(
            rf"{tex_escape(fig_no)} & \path{{{filename}}} & {tex_path_list(source)} & "
            rf"{tex_evidence_label(label)} & {tex_escape(location)} \\"
        )
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup"])
    (TABLE_DIR / "figure_evidence_sources.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_low_snr_comparison_table(low_rows: list[dict[str, str]], bootstrap_rows: list[dict[str, str]], mcnemar_rows: list[dict[str, str]]) -> None:
    low = {row["model_id"]: row for row in low_rows}
    boot = {(row["model_a"], row["model_b"], row["scope"]): row for row in bootstrap_rows}
    mc = {(row["model_a"], row["model_b"], row["scope"]): row for row in mcnemar_rows}
    comparisons = [
        ("cldnn", "iq_param_matched", "CLDNN vs IQ matched"),
        ("fusion_iq_stft", "cldnn", "Fusion vs CLDNN"),
        ("fusion_iq_stft", "iq_param_matched", "Fusion vs IQ matched"),
        ("gated_fusion_iq_stft", "fusion_iq_stft", "Gated vs Fusion"),
    ]
    lines = [
        r"\begin{table}[htbp]",
        r"  \centering",
        r"  \caption{低信噪比关键比较与配对检验摘要}",
        r"  \label{tab:low-snr-key-comparisons}",
        r"  \resizebox{\textwidth}{!}{%",
        r"  \begin{tabular}{lcccl}",
        r"    \toprule",
        r"    比较 & Low-SNR Acc. & $\Delta$ 与 95\% CI & McNemar $p$ & 解释边界 \\",
        r"    \midrule",
    ]
    for model_a, model_b, label in comparisons:
        brow = boot[(model_a, model_b, "low_snr")]
        mrow = mc[(model_a, model_b, "low_snr")]
        acc_a = f(low[model_a], "low_snr_acc_mean")
        acc_b = f(low[model_b], "low_snr_acc_mean")
        delta = f(brow, "mean_delta")
        lo = f(brow, "ci95_lower")
        hi = f(brow, "ci95_upper")
        pvalue = f(mrow, "p_value")
        boundary = "CI 跨 0，不能声称优势。" if brow["crosses_zero"] == "True" else "方向由当前 paired test 支持。"
        lines.append(
            rf"    {tex_escape(label)} & {pct(acc_a)}\% vs. {pct(acc_b)}\% & "
            rf"${delta:+.6f}$ $[{lo:+.6f},{hi:+.6f}]$ & ${pvalue:.3g}$ & {boundary} \\"
        )
    lines.extend([
        r"    \bottomrule",
        r"  \end{tabular}%",
        r"  }",
        r"\end{table}",
    ])
    (TABLE_DIR / "low_snr_key_comparisons.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_figure_inventory() -> None:
    rows = [
        ("fig01_protocol_pipeline.tex", "Protocol/manifests/statistical package", "PROJECT_SUPPORTED", "第 1 章"),
        ("fig02_model_taxonomy.tex", "main_table_metrics.csv", "PROJECT_SUPPORTED", "第 3 章"),
        ("fig03_fusion_architecture.tex", "model source files", "PROJECT_SUPPORTED", "第 3 章"),
        ("fig04_accuracy_by_snr_group.pdf/png", "main_table_metrics.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig05_low_snr_per_snr_curve.pdf/png", "low_snr_table.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig06_bootstrap_delta_forest.pdf/png", "paired_bootstrap_accuracy_deltas.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig07_accuracy_latency_params_bubble.pdf/png", "main_table_metrics.csv; complexity_latency_table.csv", "CONTROLLED_LATENCY", "第 4 章"),
        ("fig08_low_snr_confusion_panels.pdf/png", "confusion_low_snr.csv", "PROJECT_SUPPORTED", "附录 A"),
        ("fig09_mcldnn_seed_anomaly.pdf/png", "mcldnn metrics_test.json", "PROJECT_SUPPORTED", "附录 A"),
        ("fig10_evidence_boundary.tex", "REPORT_EVIDENCE_MAP.md", "Mixed labels", "附录 A"),
        ("fig11_full_snr_accuracy_macro_f1.pdf/png", "metrics_per_snr.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig12_model_class_accuracy_heatmap.pdf/png", "metrics_per_class.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig13_low_snr_class_recall_delta.pdf/png", "confusion_low_snr.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig14_paired_disagreement_by_snr.pdf/png", "predictions_test.csv", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig15_seed_stability_all_models.pdf/png", "metrics_test.json", "PROJECT_SUPPORTED", "第 4 章"),
        ("fig16_overall_confusion_panels.pdf/png", "confusion_overall.csv", "PROJECT_SUPPORTED", "附录 A"),
    ]
    lines = [
        r"\begingroup",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{2.5pt}",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\begin{longtable}{p{0.30\textwidth}p{0.30\textwidth}p{0.20\textwidth}p{0.08\textwidth}}",
        r"\caption{新增图表清单、证据源与正文引用位置}\label{tab:figure-inventory}\\",
        r"\toprule",
        r"文件 & 主要证据源 & 证据标签 & 引用位置 \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"文件 & 主要证据源 & 证据标签 & 引用位置 \\",
        r"\midrule",
        r"\endhead",
    ]
    for filename, source, label, location in rows:
        lines.append(rf"\path{{{filename}}} & {tex_path_list(source)} & {tex_evidence_label(label)} & {tex_escape(location)} \\")
    lines.extend([r"\bottomrule", r"\end{longtable}", r"\endgroup"])
    (TABLE_DIR / "figure_inventory.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    main_rows = read_csv(AGG_DIR / "main_table_metrics.csv")
    low_rows = read_csv(AGG_DIR / "low_snr_table.csv")
    complexity_rows = read_csv(AGG_DIR / "complexity_latency_table.csv")
    bootstrap_rows = read_csv(STAT_DIR / "paired_bootstrap_accuracy_deltas.csv")
    mcnemar_rows = read_csv(STAT_DIR / "mcnemar_tests.csv")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    plot_grouped_accuracy(main_rows)
    plot_low_snr_curve(low_rows)
    plot_bootstrap_forest(bootstrap_rows)
    plot_accuracy_latency_bubble(main_rows, complexity_rows)
    plot_confusion_panels()
    plot_mcldnn_anomaly()
    plot_full_snr_metric_curves()
    plot_model_class_accuracy_heatmap()
    plot_low_snr_class_delta()
    plot_paired_disagreement_by_snr()
    plot_seed_stability_all_models()
    plot_overall_confusion_panels()
    write_literature_table()
    write_figure_evidence_table()
    write_low_snr_comparison_table(low_rows, bootstrap_rows, mcnemar_rows)
    write_figure_inventory()


if __name__ == "__main__":
    main()
