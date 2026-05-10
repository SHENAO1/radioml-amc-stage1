"""Generate fig21: 2x2 training curve comparison for ablation variants.

Sub-plots:
  (a) full  — train/val accuracy vs epoch
  (b) arch_only — train/val accuracy vs epoch
  (c) arch_aug  — train/val accuracy vs epoch
  (d) 4 variants val accuracy overlaid

Seed: 42 only (to avoid smoothing artifacts from seed averaging).
X axis: 0–50 epoch, Y axis: 0–1.0 accuracy.
I train=solid, val=dashed, color per variant.

Data source:
  results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/<variant>/
      fusion_cldnn_stft/seed_42/metrics.csv   (cols: epoch,train_loss,train_acc,val_loss,val_acc)
  results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/
      fusion_cldnn_stft/seed_42/metrics.csv   (full variant)

Output:
  docs/paper/course_report/figures/fig21_proposed_ablation_training_curves.{pdf,png}
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs/paper/course_report/figures"

ABLATION_ROOT = (
    REPO_ROOT / "results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a"
)
FULL_CSV = (
    REPO_ROOT
    / "results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a"
    / "fusion_cldnn_stft/seed_42/metrics.csv"
)

VARIANT_CSV_PATHS = {
    "full": FULL_CSV,
    "arch_only": ABLATION_ROOT / "arch_only/fusion_cldnn_stft/seed_42/metrics.csv",
    "arch_aug": ABLATION_ROOT / "arch_aug/fusion_cldnn_stft/seed_42/metrics.csv",
    "arch_ls": ABLATION_ROOT / "arch_ls/fusion_cldnn_stft/seed_42/metrics.csv",
}

COLORS = {
    "full": "#D95F5F",
    "arch_only": "#5B8DB8",
    "arch_aug": "#F28B30",
    "arch_ls": "#6BAD6B",
}
DISPLAY_NAMES = {
    "full": "full",
    "arch_only": "arch_only",
    "arch_aug": "arch_aug",
    "arch_ls": "arch_ls",
}


def load_metrics(path: Path) -> tuple[list[int], list[float], list[float]]:
    """Return (epochs, train_acc, val_acc) from metrics.csv."""
    epochs, train_acc, val_acc = [], [], []
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            epochs.append(int(row["epoch"]))
            train_acc.append(float(row["train_acc"]))
            val_acc.append(float(row["val_acc"]))
    return epochs, train_acc, val_acc


def plot_single(ax: plt.Axes, variant: str) -> None:
    epochs, train_acc, val_acc = load_metrics(VARIANT_CSV_PATHS[variant])
    color = COLORS[variant]
    name = DISPLAY_NAMES[variant]
    ax.plot(epochs, train_acc, color=color, linestyle="-", linewidth=1.5, label=f"train")
    ax.plot(epochs, val_acc, color=color, linestyle="--", linewidth=1.5, label=f"val")
    ax.set_xlim(0, 50)
    ax.set_ylim(0.0, 1.0)
    ax.set_title(f"({chr(ord('a') + list(VARIANT_CSV_PATHS.keys()).index(variant))}) {name}", fontsize=10)
    ax.set_xlabel("Epoch", fontsize=9)
    ax.set_ylabel("Accuracy", fontsize=9)
    ax.legend(fontsize=8)
    ax.xaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)


def main() -> int:
    variants_subplots = ["full", "arch_only", "arch_aug"]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    fig.suptitle(
        "Training Curves by Ablation Variant (seed 42; solid=train, dashed=val)",
        fontsize=11,
    )

    # Sub-plots (a)(b)(c): individual variants
    subplot_variants = ["full", "arch_only", "arch_aug"]
    subplot_order = [(0, 0), (0, 1), (1, 0)]
    letters = ["a", "b", "c"]
    for (r, c), variant, letter in zip(subplot_order, subplot_variants, letters):
        ax = axes[r][c]
        epochs, train_acc, val_acc = load_metrics(VARIANT_CSV_PATHS[variant])
        color = COLORS[variant]
        ax.plot(epochs, train_acc, color=color, linestyle="-", linewidth=1.5, label="train")
        ax.plot(epochs, val_acc, color=color, linestyle="--", linewidth=1.5, label="val")
        ax.set_xlim(0, 50)
        ax.set_ylim(0.0, 1.0)
        ax.set_title(f"({letter}) {DISPLAY_NAMES[variant]}", fontsize=10)
        ax.set_xlabel("Epoch", fontsize=9)
        ax.set_ylabel("Accuracy", fontsize=9)
        ax.legend(fontsize=8)
        ax.xaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
        ax.yaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)

    # Sub-plot (d): val accuracy all 4 variants overlaid
    ax_d = axes[1][1]
    for variant in ["full", "arch_only", "arch_aug", "arch_ls"]:
        epochs, _, val_acc = load_metrics(VARIANT_CSV_PATHS[variant])
        ax_d.plot(
            epochs,
            val_acc,
            color=COLORS[variant],
            linestyle="-",
            linewidth=1.5,
            label=DISPLAY_NAMES[variant],
        )
    ax_d.set_xlim(0, 50)
    ax_d.set_ylim(0.0, 1.0)
    ax_d.set_title("(d) val accuracy — all variants", fontsize=10)
    ax_d.set_xlabel("Epoch", fontsize=9)
    ax_d.set_ylabel("Val Accuracy", fontsize=9)
    ax_d.legend(fontsize=8)
    ax_d.xaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax_d.yaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)

    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURES_DIR / "fig21_proposed_ablation_training_curves.pdf"
    png_path = FIGURES_DIR / "fig21_proposed_ablation_training_curves.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
