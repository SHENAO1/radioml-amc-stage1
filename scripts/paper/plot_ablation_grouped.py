"""Generate fig19: grouped bar chart for ablation variants across SNR groups.

4 variants: arch_only / arch_aug / arch_ls / full
4 SNR groups: Overall / Low / Mid / High
Error bars = mean ± std across 3 seeds (42, 2025, 3407).
Best value in each group column is shown in bold (handled via annotation).
Horizontal dashed line marks Stage 5A CLDNN overall baseline (0.6129).

Data sources:
  - Ablation variants:
    results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/<variant>/
        fusion_cldnn_stft/seed_*/metrics_test.json
  - Full (proposed):
    results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/
        fusion_cldnn_stft/seed_*/metrics_test.json

Output:
  docs/paper/course_report/figures/fig19_ablation_grouped_bars.{pdf,png}
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs/paper/course_report/figures"

SEEDS = (42, 2025, 3407)
STAGE5A_CLDNN_OVERALL = 0.6129  # Stage 5A CLDNN baseline (Table 4.1)

VARIANT_LABELS = {
    "arch_only": "arch\\_only",
    "arch_aug": "arch\\_aug",
    "arch_ls": "arch\\_ls",
    "full": "full",
}

SNR_GROUPS = ["Overall", "Low", "Mid", "High"]
METRIC_KEYS = [
    "overall_accuracy",
    "low_snr_accuracy",
    "mid_snr_accuracy",
    "high_snr_accuracy",
]

ABLATION_ROOT = (
    REPO_ROOT / "results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a"
)
FULL_ROOT = (
    REPO_ROOT / "results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a"
        / "fusion_cldnn_stft"
)


def load_variant_metrics(variant: str) -> dict[str, tuple[float, float]]:
    """Return {metric_key: (mean, std)} for a given ablation variant."""
    if variant == "full":
        root = FULL_ROOT
        seed_dirs = [root / f"seed_{s}" for s in SEEDS]
    else:
        root = ABLATION_ROOT / variant / "fusion_cldnn_stft"
        seed_dirs = [root / f"seed_{s}" for s in SEEDS]

    per_seed: dict[str, list[float]] = {k: [] for k in METRIC_KEYS}
    for sd in seed_dirs:
        fp = sd / "metrics_test.json"
        if not fp.exists():
            raise FileNotFoundError(f"Missing: {fp}")
        with open(fp) as f:
            d = json.load(f)
        for k in METRIC_KEYS:
            per_seed[k].append(float(d[k]))

    return {
        k: (float(np.mean(v)), float(np.std(v, ddof=1))) for k, v in per_seed.items()
    }


def main() -> int:
    variants = ["arch_only", "arch_aug", "arch_ls", "full"]
    data: dict[str, dict[str, tuple[float, float]]] = {}
    for v in variants:
        data[v] = load_variant_metrics(v)

    n_groups = len(SNR_GROUPS)
    n_variants = len(variants)
    bar_width = 0.18
    group_gap = 0.05
    group_width = n_variants * bar_width + group_gap
    group_centers = np.arange(n_groups) * group_width
    offsets = np.linspace(
        -(n_variants - 1) * bar_width / 2,
        (n_variants - 1) * bar_width / 2,
        n_variants,
    )

    colors = ["#5B8DB8", "#F28B30", "#6BAD6B", "#D95F5F"]

    fig, ax = plt.subplots(figsize=(9, 5))

    for vi, (variant, color) in enumerate(zip(variants, colors)):
        means = [data[variant][k][0] for k in METRIC_KEYS]
        stds = [data[variant][k][1] for k in METRIC_KEYS]
        xs = group_centers + offsets[vi]
        bars = ax.bar(
            xs,
            means,
            width=bar_width,
            color=color,
            alpha=0.85,
            label=VARIANT_LABELS[variant],
            yerr=stds,
            capsize=3,
            error_kw={"elinewidth": 1.0, "ecolor": "black", "capthick": 1.0},
        )
        # Annotate best bar in each group (highest mean)
        for gi, (x, mean, std) in enumerate(zip(xs, means, stds)):
            # Determine if this variant has the best mean in this group
            group_means = [data[v][METRIC_KEYS[gi]][0] for v in variants]
            if abs(mean - max(group_means)) < 1e-9:
                ax.text(
                    x,
                    mean + std + 0.002,
                    f"{mean:.4f}",
                    ha="center",
                    va="bottom",
                    fontsize=6.5,
                    fontweight="bold",
                    color="black",
                )

    # Stage 5A CLDNN baseline dashed line (overall only — drawn across full width)
    ax.axhline(
        STAGE5A_CLDNN_OVERALL,
        color="gray",
        linestyle="--",
        linewidth=1.2,
        label=f"Stage 5A CLDNN overall ({STAGE5A_CLDNN_OVERALL:.4f})",
    )

    ax.set_xticks(group_centers)
    ax.set_xticklabels(SNR_GROUPS, fontsize=11)
    ax.set_ylabel("Accuracy", fontsize=11)
    ax.set_ylim(0.18, 0.98)
    ax.set_title(
        "Ablation Variants: Accuracy by SNR Group\n"
        "(mean ± std, 3 seeds; bold = best in group)",
        fontsize=11,
    )
    ax.legend(fontsize=9, loc="upper left", ncol=2)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)

    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURES_DIR / "fig19_ablation_grouped_bars.pdf"
    png_path = FIGURES_DIR / "fig19_ablation_grouped_bars.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
