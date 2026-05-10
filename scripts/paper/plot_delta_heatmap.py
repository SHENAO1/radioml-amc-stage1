"""Generate fig22: delta heatmap — proposed model vs 9 Stage 5A baselines.

Each cell = proposed_mean - baseline_mean (in percentage points × 100).
Color scale: red (negative) / green (positive), saturates at ±5 pp.
The row for 'cldnn' is highlighted with a bold border.

Data sources:
  Stage 5A baselines:
    paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate/
        main_table_metrics.csv
  Proposed (3-seed mean):
    results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/
        fusion_cldnn_stft/seed_*/metrics_test.json

Output:
  docs/paper/course_report/figures/fig22_proposed_vs_stage5a_delta_heatmap.{pdf,png}
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs/paper/course_report/figures"

STAGE5A_CSV = (
    REPO_ROOT
    / "paper_package/server_sync_20260508/results/paper_stage2/rml2016a/aggregate"
    / "main_table_metrics.csv"
)

PROPOSED_ROOT = (
    REPO_ROOT
    / "results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft"
)

SEEDS = (42, 2025, 3407)

METRIC_KEYS_CSV = [
    "overall_acc_mean",
    "low_snr_acc_mean",
    "mid_snr_acc_mean",
    "high_snr_acc_mean",
]
METRIC_KEYS_JSON = [
    "overall_accuracy",
    "low_snr_accuracy",
    "mid_snr_accuracy",
    "high_snr_accuracy",
]
COL_LABELS = ["Overall", "Low SNR", "Mid SNR", "High SNR"]

# Row display order (9 models)
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

MODEL_DISPLAY = {
    "cnn1d": "cnn1d",
    "resnet1d": "resnet1d",
    "tfcnn_stft": "tfcnn\\_stft",
    "fusion_iq_stft": "fusion\\_iq\\_stft",
    "cldnn": "cldnn ★",
    "mcldnn": "mcldnn",
    "lwamcnet": "lwamcnet",
    "iq_param_matched": "iq\\_param\\_matched",
    "gated_fusion_iq_stft": "gated\\_fusion\\_iq\\_stft",
}

HIGHLIGHT_ROW = "cldnn"


def load_stage5a() -> dict[str, list[float]]:
    """Return {model_id: [overall_mean, low_mean, mid_mean, high_mean]} from CSV."""
    result: dict[str, list[float]] = {}
    if not STAGE5A_CSV.exists():
        raise FileNotFoundError(f"Missing: {STAGE5A_CSV}")
    with open(STAGE5A_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row["model_id"]
            result[model] = [float(row[k]) for k in METRIC_KEYS_CSV]
    return result


def load_proposed_mean() -> list[float]:
    """Return [overall, low, mid, high] mean across 3 seeds from metrics_test.json."""
    per_metric: list[list[float]] = [[] for _ in METRIC_KEYS_JSON]
    for seed in SEEDS:
        fp = PROPOSED_ROOT / f"seed_{seed}" / "metrics_test.json"
        if not fp.exists():
            raise FileNotFoundError(f"Missing: {fp}")
        with open(fp) as f:
            d = json.load(f)
        for i, k in enumerate(METRIC_KEYS_JSON):
            per_metric[i].append(float(d[k]))
    return [float(np.mean(vals)) for vals in per_metric]


def main() -> int:
    stage5a = load_stage5a()
    proposed = load_proposed_mean()

    n_rows = len(MODEL_ORDER)
    n_cols = len(COL_LABELS)
    delta_matrix = np.zeros((n_rows, n_cols))

    for ri, model in enumerate(MODEL_ORDER):
        if model not in stage5a:
            raise KeyError(f"Model not found in Stage 5A CSV: {model}")
        baseline = stage5a[model]
        for ci in range(n_cols):
            delta_matrix[ri, ci] = (proposed[ci] - baseline[ci]) * 100.0  # percentage points

    # Build diverging colormap: red for negative, green for positive
    from matplotlib.colors import TwoSlopeNorm

    vmax = max(5.0, float(np.abs(delta_matrix).max()) * 1.05)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cmap = plt.cm.RdYlGn

    fig, ax = plt.subplots(figsize=(8, 5.5))
    im = ax.imshow(delta_matrix, cmap=cmap, norm=norm, aspect="auto")

    # Axis labels
    ax.set_xticks(np.arange(n_cols))
    ax.set_xticklabels(COL_LABELS, fontsize=10)
    ax.set_yticks(np.arange(n_rows))
    ax.set_yticklabels(
        [MODEL_DISPLAY[m] for m in MODEL_ORDER],
        fontsize=9,
    )

    # Cell text
    for ri in range(n_rows):
        for ci in range(n_cols):
            val = delta_matrix[ri, ci]
            text_color = "black" if abs(val) < vmax * 0.6 else "white"
            sign = "+" if val >= 0 else ""
            ax.text(
                ci,
                ri,
                f"{sign}{val:.2f}",
                ha="center",
                va="center",
                fontsize=9,
                color=text_color,
                fontweight="bold" if MODEL_ORDER[ri] == HIGHLIGHT_ROW else "normal",
            )

    # Bold border around cldnn row
    highlight_ri = MODEL_ORDER.index(HIGHLIGHT_ROW)
    rect = mpatches.FancyBboxPatch(
        (-0.5, highlight_ri - 0.5),
        n_cols,
        1.0,
        boxstyle="square,pad=0",
        linewidth=2.5,
        edgecolor="black",
        facecolor="none",
    )
    ax.add_patch(rect)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Δ Accuracy (pp) = proposed − baseline", fontsize=9)

    ax.set_title(
        "Proposed Model vs Stage 5A Baselines: Δ Accuracy (percentage points)\n"
        "Data: proposed 3-seed mean (metrics_test.json) vs Stage 5A main_table_metrics.csv",
        fontsize=9,
    )
    ax.set_xlabel("SNR Group", fontsize=10)
    ax.set_ylabel("Stage 5A Baseline Model", fontsize=10)

    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURES_DIR / "fig22_proposed_vs_stage5a_delta_heatmap.pdf"
    png_path = FIGURES_DIR / "fig22_proposed_vs_stage5a_delta_heatmap.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
