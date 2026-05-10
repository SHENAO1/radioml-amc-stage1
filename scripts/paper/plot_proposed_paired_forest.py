"""Generate fig20: forest plot of proposed model paired bootstrap deltas.

Rows (8 total): 5 comparisons × mixed scopes
  proposed vs p11_fusion_iq_stft  |  overall
  proposed vs p11_fusion_iq_stft  |  low_snr
  proposed vs ablation_arch_only  |  overall
  proposed vs ablation_arch_only  |  low_snr
  proposed vs ablation_arch_aug   |  overall
  proposed vs ablation_arch_aug   |  low_snr
  proposed vs ablation_arch_ls    |  overall
  proposed vs ablation_arch_ls    |  low_snr

Horizontal axis: paired bootstrap delta (accuracy difference) with 95% CI.
Vertical zero line marks no difference.
Filled circle (●) if CI does not cross 0; open circle (○) if CI crosses 0.

Data source:
  results/paper_stage6/proposed_paired_tests/paired_bootstrap.csv

Output:
  docs/paper/course_report/figures/fig20_proposed_paired_forest.{pdf,png}
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
CSV_PATH = REPO_ROOT / "results/paper_stage6/proposed_paired_tests/paired_bootstrap.csv"

# Display order and labels
ROW_ORDER = [
    ("p11_fusion_iq_stft", "overall"),
    ("p11_fusion_iq_stft", "low_snr"),
    ("ablation_arch_only", "overall"),
    ("ablation_arch_only", "low_snr"),
    ("ablation_arch_aug", "overall"),
    ("ablation_arch_aug", "low_snr"),
    ("ablation_arch_ls", "overall"),
    ("ablation_arch_ls", "low_snr"),
]

ROW_LABELS = [
    "vs P1.1 fusion\\_iq\\_stft (overall)",
    "vs P1.1 fusion\\_iq\\_stft (low SNR)",
    "vs arch\\_only (overall)",
    "vs arch\\_only (low SNR)",
    "vs arch\\_aug (overall)",
    "vs arch\\_aug (low SNR)",
    "vs arch\\_ls (overall)",
    "vs arch\\_ls (low SNR)",
]

GROUP_COLORS = {
    "p11_fusion_iq_stft": "#5B8DB8",
    "ablation_arch_only": "#6BAD6B",
    "ablation_arch_aug": "#F28B30",
    "ablation_arch_ls": "#D95F5F",
}


def load_csv() -> dict[tuple[str, str], dict]:
    """Load paired_bootstrap.csv into nested dict keyed by (model_b, scope)."""
    data: dict[tuple[str, str], dict] = {}
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Missing: {CSV_PATH}")
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row["model_b"], row["scope"])
            data[key] = {
                "delta": float(row["delta_mean"]),
                "ci_low": float(row["ci_low"]),
                "ci_high": float(row["ci_high"]),
                "crosses_zero": row["crosses_zero"].strip().lower() == "true",
            }
    return data


def main() -> int:
    data = load_csv()

    n_rows = len(ROW_ORDER)
    y_pos = np.arange(n_rows)

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, (key, label) in enumerate(zip(ROW_ORDER, ROW_LABELS)):
        model_b, scope = key
        if key not in data:
            raise KeyError(f"Row not found in CSV: {key}")
        row = data[key]
        delta = row["delta"]
        ci_lo = row["ci_low"]
        ci_hi = row["ci_high"]
        crosses = row["crosses_zero"]
        color = GROUP_COLORS[model_b]

        # Error bar (CI)
        ax.plot([ci_lo, ci_hi], [i, i], color=color, linewidth=1.8, zorder=2)

        # Marker: filled if CI doesn't cross 0, open if it does
        marker = "o"
        face = color if not crosses else "white"
        ax.plot(
            delta,
            i,
            marker=marker,
            markersize=8,
            color=color,
            markerfacecolor=face,
            markeredgewidth=1.5,
            zorder=3,
        )

    ax.axvline(0.0, color="black", linewidth=1.0, linestyle="-", zorder=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(ROW_LABELS, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Paired Bootstrap Δ Accuracy (proposed − baseline)", fontsize=10)
    ax.set_title(
        "Proposed Model: Paired Bootstrap Deltas with 95% CI\n"
        "(● CI excludes 0; ○ CI crosses 0)",
        fontsize=10,
    )
    ax.xaxis.grid(True, linestyle=":", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)

    # Color legend by comparison group
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color="#5B8DB8", linewidth=2, label="vs P1.1 fusion\\_iq\\_stft"),
        Line2D([0], [0], color="#6BAD6B", linewidth=2, label="vs arch\\_only"),
        Line2D([0], [0], color="#F28B30", linewidth=2, label="vs arch\\_aug"),
        Line2D([0], [0], color="#D95F5F", linewidth=2, label="vs arch\\_ls"),
    ]
    ax.legend(handles=legend_elements, fontsize=8, loc="lower right")

    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURES_DIR / "fig20_proposed_paired_forest.pdf"
    png_path = FIGURES_DIR / "fig20_proposed_paired_forest.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
