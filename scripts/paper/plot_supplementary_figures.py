"""Generate updated figures reflecting supplementary experiments.

Updates:
  fig17: Add CLDNN+aug line to per-SNR comparison
  fig19: Add CLDNN+aug bar to ablation grouped chart
  fig20: Rebuild forest plot with all 5 paired comparisons from all_paired_tests.json
  fig24 (NEW): Gate diagnostic - g vs SNR + histogram

Data sources:
  - cldnn_aug_ablation_3090: CLDNN + aug + LS control experiment
  - gated_fusion_diagnostic_3090: gate weight diagnostic
  - paired_statistical_tests: 5-group McNemar + bootstrap
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.rcParams["font.family"] = "DejaVu Sans"

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs" / "paper" / "course_report" / "figures"
RESULTS_ROOT = REPO_ROOT / "results" / "paper_stage6"
SEEDS = (42, 2025, 3407)


# --------------- helpers ---------------

def stage5a_per_snr(model: str) -> dict[int, float]:
    accs: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for seed in SEEDS:
        p = REPO_ROOT / f"paper_package/predictions_archive_20260508/results/paper_stage2/rml2016a/{model}/seed_{seed}/predictions_test.csv"
        if not p.exists():
            raise FileNotFoundError(p)
        with open(p) as f:
            r = csv.DictReader(f)
            for row in r:
                snr = int(row["snr_db"])
                accs[snr][0] += int(row["correct"])
                accs[snr][1] += 1
    return {k: v[0] / v[1] for k, v in sorted(accs.items())}


def stage6_per_snr(per_snr_glob: str) -> dict[int, float]:
    by_snr: dict[int, list[float]] = defaultdict(list)
    files = sorted(REPO_ROOT.glob(per_snr_glob))
    if not files:
        raise FileNotFoundError(f"no files matched: {per_snr_glob}")
    for fp in files:
        with open(fp) as f:
            r = csv.DictReader(f)
            for row in r:
                try:
                    snr = int(row["snr_db"])
                except (TypeError, ValueError):
                    continue
                by_snr[snr].append(float(row["accuracy"]))
    return {k: float(np.mean(v)) for k, v in sorted(by_snr.items())}


def load_metrics_test(root: Path, model_dir: str = "") -> dict[str, tuple[float, float]]:
    """Load metrics_test.json for all seeds, return {key: (mean, std)}."""
    keys = ["overall_accuracy", "low_snr_accuracy", "mid_snr_accuracy", "high_snr_accuracy"]
    per_seed: dict[str, list[float]] = {k: [] for k in keys}
    for seed in SEEDS:
        if model_dir:
            fp = root / model_dir / f"seed_{seed}" / "metrics_test.json"
        else:
            fp = root / f"seed_{seed}" / "metrics_test.json"
        if not fp.exists():
            raise FileNotFoundError(fp)
        with open(fp) as f:
            d = json.load(f)
        for k in keys:
            per_seed[k].append(float(d[k]))
    return {k: (float(np.mean(v)), float(np.std(v, ddof=1))) for k, v in per_seed.items()}


# --------------- fig17: per-SNR with CLDNN+aug ---------------

def plot_fig17():
    print("Generating fig17 (per-SNR with CLDNN+aug)...")

    cldnn_aug_glob = "results/paper_stage6/cldnn_aug_ablation_3090/rml2016a/cldnn/seed_*/metrics_per_snr.csv"
    # Try nested path if non-nested doesn't work
    try:
        cldnn_aug_snr = stage6_per_snr(cldnn_aug_glob)
    except FileNotFoundError:
        cldnn_aug_glob = "results/paper_stage6/cldnn_aug_ablation_3090/cldnn_aug_ablation_3090/rml2016a/cldnn/seed_*/metrics_per_snr.csv"
        cldnn_aug_snr = stage6_per_snr(cldnn_aug_glob)

    series = {
        "Stage 5A CLDNN": stage5a_per_snr("cldnn"),
        "Stage 5A fusion_iq_stft": stage5a_per_snr("fusion_iq_stft"),
        "P1.1 fusion_iq_stft (matched schedule)": stage6_per_snr(
            "results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft/seed_*/metrics_per_snr.csv"
        ),
        "CLDNN + aug + LS (control)": cldnn_aug_snr,
        "Proposed fusion_cldnn_stft + aug": stage6_per_snr(
            "results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_aug/fusion_cldnn_stft/seed_*/metrics_per_snr.csv"
        ),
    }
    snrs = sorted(set(snr for d in series.values() for snr in d))

    styles = {
        "Stage 5A CLDNN": {"linestyle": "-", "marker": "o", "color": "tab:blue"},
        "Stage 5A fusion_iq_stft": {"linestyle": "--", "marker": "s", "color": "tab:gray"},
        "P1.1 fusion_iq_stft (matched schedule)": {"linestyle": ":", "marker": "^", "color": "tab:orange"},
        "CLDNN + aug + LS (control)": {"linestyle": "-", "marker": "v", "color": "tab:green", "linewidth": 2.0},
        "Proposed fusion_cldnn_stft + aug": {"linestyle": "-", "marker": "D", "color": "tab:red", "linewidth": 2.4},
    }

    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for label, d in series.items():
        xs = sorted(d)
        ys = [d[x] for x in xs]
        kw = styles[label]
        ax.plot(xs, ys, label=label, **kw)
    ax.axvspan(-20, -6, alpha=0.06, color="gray")
    ax.axvspan(8, 18, alpha=0.06, color="green")
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Test accuracy (3-seed mean)")
    ax.set_title("Per-SNR accuracy: baselines, CLDNN+aug control, and proposed model")
    ax.set_xticks(snrs[::2])
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        out = FIGURES_DIR / f"fig17_proposed_per_snr_comparison.{ext}"
        fig.savefig(out, dpi=200, bbox_inches="tight")
        print(f"  wrote {out}")
    plt.close(fig)


# --------------- fig19: ablation grouped bars + CLDNN+aug ---------------

def plot_fig19():
    print("Generating fig19 (ablation grouped bars with CLDNN+aug)...")

    METRIC_KEYS = ["overall_accuracy", "low_snr_accuracy", "mid_snr_accuracy", "high_snr_accuracy"]
    SNR_GROUPS = ["Overall", "Low", "Mid", "High"]
    STAGE5A_CLDNN_OVERALL = 0.6129

    # Load ablation variants
    abl_root = RESULTS_ROOT / "fusion_cldnn_stft_ablation_3090" / "rml2016a"
    full_root = RESULTS_ROOT / "fusion_cldnn_stft_aug_ls_3090" / "rml2016a" / "fusion_cldnn_stft"

    def load_variant(variant):
        if variant == "full":
            return load_metrics_test(full_root)
        elif variant == "cldnn_aug":
            # Try non-nested first, then nested
            root = RESULTS_ROOT / "cldnn_aug_ablation_3090" / "rml2016a" / "cldnn"
            try:
                return load_metrics_test(root)
            except FileNotFoundError:
                root = RESULTS_ROOT / "cldnn_aug_ablation_3090" / "cldnn_aug_ablation_3090" / "rml2016a" / "cldnn"
                return load_metrics_test(root)
        else:
            root = abl_root / variant / "fusion_cldnn_stft"
            return load_metrics_test(root)

    variants = ["arch_only", "arch_aug", "arch_ls", "full", "cldnn_aug"]
    labels = {
        "arch_only": "arch\\_only",
        "arch_aug": "arch\\_aug",
        "arch_ls": "arch\\_ls",
        "full": "full (arch+aug+LS)",
        "cldnn_aug": "CLDNN+aug+LS",
    }

    data = {}
    for v in variants:
        data[v] = load_variant(v)

    n_groups = len(SNR_GROUPS)
    n_variants = len(variants)
    bar_width = 0.15
    group_gap = 0.05
    group_width = n_variants * bar_width + group_gap
    group_centers = np.arange(n_groups) * group_width
    offsets = np.linspace(
        -(n_variants - 1) * bar_width / 2,
        (n_variants - 1) * bar_width / 2,
        n_variants,
    )

    colors = ["#5B8DB8", "#F28B30", "#6BAD6B", "#D95F5F", "#9B59B6"]

    fig, ax = plt.subplots(figsize=(10, 5))

    for vi, (variant, color) in enumerate(zip(variants, colors)):
        means = [data[variant][k][0] for k in METRIC_KEYS]
        stds = [data[variant][k][1] for k in METRIC_KEYS]
        xs = group_centers + offsets[vi]
        ax.bar(
            xs, means, width=bar_width, color=color, alpha=0.85,
            label=labels[variant], yerr=stds, capsize=3,
            error_kw={"elinewidth": 1.0, "ecolor": "black", "capthick": 1.0},
        )
        for gi, (x, mean, std) in enumerate(zip(xs, means, stds)):
            group_means = [data[v][METRIC_KEYS[gi]][0] for v in variants]
            if abs(mean - max(group_means)) < 1e-6:
                ax.text(x, mean + std + 0.002, f"{mean:.4f}",
                        ha="center", va="bottom", fontsize=6, fontweight="bold")

    ax.axhline(STAGE5A_CLDNN_OVERALL, color="gray", linestyle="--", linewidth=1.2,
               label=f"Stage 5A CLDNN ({STAGE5A_CLDNN_OVERALL:.4f})")
    ax.set_xticks(group_centers)
    ax.set_xticklabels(SNR_GROUPS, fontsize=11)
    ax.set_ylabel("Accuracy", fontsize=11)
    ax.set_ylim(0.18, 0.98)
    ax.set_title("Ablation + CLDNN+aug Control: Accuracy by SNR Group\n"
                 "(mean ± std, 3 seeds; bold = best in group)", fontsize=11)
    ax.legend(fontsize=8, loc="upper left", ncol=3)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout()

    for ext in ("pdf", "png"):
        out = FIGURES_DIR / f"fig19_ablation_grouped_bars.{ext}"
        fig.savefig(out, dpi=150, bbox_inches="tight")
        print(f"  wrote {out}")
    plt.close(fig)


# --------------- fig20: paired forest from all_paired_tests.json ---------------

def plot_fig20():
    print("Generating fig20 (paired forest from all_paired_tests.json)...")

    # Load data
    json_path = RESULTS_ROOT / "paired_statistical_tests" / "all_paired_tests.json"
    if not json_path.exists():
        json_path = RESULTS_ROOT / "paired_statistical_tests" / "paired_statistical_tests" / "all_paired_tests.json"
    with open(json_path) as f:
        comparisons = json.load(f)

    # Build rows: for each comparison, aggregate across seeds
    rows = []
    for comp in comparisons:
        name = comp["name"]
        seeds_data = comp["seeds"]
        if not seeds_data:
            continue
        # Overall: aggregate bootstrap from all seeds
        deltas = [s["delta_pp"] / 100 for s in seeds_data]
        ci_lows = [s["bootstrap"]["ci_2.5"] for s in seeds_data]
        ci_highs = [s["bootstrap"]["ci_97.5"] for s in seeds_data]
        mean_delta = float(np.mean(deltas))
        mean_ci_low = float(np.mean(ci_lows))
        mean_ci_high = float(np.mean(ci_highs))
        crosses_zero = (mean_ci_low <= 0 <= mean_ci_high)
        all_sig = comp.get("all_seeds_significant", False)
        rows.append({
            "label": name,
            "delta": mean_delta,
            "ci_low": mean_ci_low,
            "ci_high": mean_ci_high,
            "crosses_zero": crosses_zero,
            "all_sig": all_sig,
        })

    colors_list = ["#F28B30", "#D95F5F", "#9B59B6", "#5B8DB8", "#6BAD6B"]

    n_rows = len(rows)
    fig, ax = plt.subplots(figsize=(9, 4.5))

    for i, row in enumerate(rows):
        color = colors_list[i % len(colors_list)]
        ci_lo, ci_hi = row["ci_low"], row["ci_high"]
        delta = row["delta"]
        crosses = row["crosses_zero"]

        ax.plot([ci_lo, ci_hi], [i, i], color=color, linewidth=2.0, zorder=2)
        face = color if not crosses else "white"
        ax.plot(delta, i, marker="o", markersize=9, color=color,
                markerfacecolor=face, markeredgewidth=1.5, zorder=3)
        # Annotate delta value
        sig_txt = "***" if row["all_sig"] else "ns"
        ax.text(ci_hi + 0.001, i, f"  Δ={delta*100:+.2f}pp {sig_txt}",
                va="center", fontsize=8, color=color)

    ax.axvline(0.0, color="black", linewidth=1.0, linestyle="-", zorder=1)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels([r["label"] for r in rows], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Paired Bootstrap Δ Accuracy (A − B, 3-seed mean)", fontsize=10)
    ax.set_title("Same-Hardware Paired Statistical Tests\n"
                 "(● CI excludes 0; ○ CI crosses 0; *** all seeds p<0.05)", fontsize=10)
    ax.xaxis.grid(True, linestyle=":", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout()

    for ext in ("pdf", "png"):
        out = FIGURES_DIR / f"fig20_proposed_paired_forest.{ext}"
        fig.savefig(out, dpi=150, bbox_inches="tight")
        print(f"  wrote {out}")
    plt.close(fig)


# --------------- fig24 (NEW): gate diagnostic ---------------

def plot_fig24():
    print("Generating fig24 (gate diagnostic: g vs SNR + histogram)...")

    gate_data = {}
    for seed in SEEDS:
        fp = RESULTS_ROOT / "gated_fusion_diagnostic_3090" / "rml2016a" / "gated_fusion_iq_stft" / f"seed_{seed}" / "gate_diagnostic.json"
        if not fp.exists():
            fp = RESULTS_ROOT / "gated_fusion_diagnostic_3090" / "gated_fusion_diagnostic_3090" / "rml2016a" / "gated_fusion_iq_stft" / f"seed_{seed}" / "gate_diagnostic.json"
        with open(fp) as f:
            gate_data[seed] = json.load(f)

    snrs = sorted([int(k) for k in gate_data[42]["per_snr_gate_mean"].keys()])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [2, 1]})

    # Left: g vs SNR for each seed
    seed_colors = {42: "tab:blue", 2025: "tab:orange", 3407: "tab:green"}
    for seed in SEEDS:
        d = gate_data[seed]
        means = [d["per_snr_gate_mean"][str(s)] for s in snrs]
        stds = [d["per_snr_gate_std"][str(s)] for s in snrs]
        ax1.errorbar(snrs, means, yerr=stds, marker="o", markersize=4,
                     label=f"seed {seed} (g̅={d['gate_mean']:.3f})",
                     color=seed_colors[seed], linewidth=1.5, capsize=2, alpha=0.8)

    ax1.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
    ax1.axvspan(-20, -6, alpha=0.06, color="gray")
    ax1.set_xlabel("SNR (dB)", fontsize=11)
    ax1.set_ylabel("Gate weight g (0=I/Q, 1=STFT)", fontsize=11)
    ax1.set_title("Gate Weight vs SNR (per seed)", fontsize=11)
    ax1.set_xticks(snrs[::2])
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9, loc="upper right")
    ax1.text(-19, 0.85, "STFT\npreferred", fontsize=8, color="gray", style="italic")
    ax1.text(-19, 0.10, "I/Q\npreferred", fontsize=8, color="gray", style="italic")

    # Right: global gate distribution histogram (seed 42 as representative)
    # We show overall gate mean and std as text annotations
    for seed in SEEDS:
        d = gate_data[seed]
        g_mean = d["gate_mean"]
        g_std = d["gate_std"]
        color = seed_colors[seed]
        # Simulate distribution from mean/std (approximate with beta or just show stats)
        ax2.barh(f"seed {seed}", g_mean, xerr=g_std, height=0.5,
                 color=color, alpha=0.7, capsize=5)
        ax2.text(g_mean + g_std + 0.02, f"seed {seed}",
                 f"μ={g_mean:.3f}\nσ={g_std:.3f}",
                 va="center", fontsize=9, color=color)

    ax2.set_xlabel("Gate weight g", fontsize=11)
    ax2.set_title("Global Gate Statistics", fontsize=11)
    ax2.set_xlim(0, 1.0)
    ax2.axvline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
    ax2.grid(True, alpha=0.3, axis="x")

    fig.suptitle("Gated Fusion Diagnostic: Scalar Gate Weight g Analysis\n"
                 "(GATED_FUSION_DIAGNOSTIC_3090, 3 seeds × gated_fusion_iq_stft)",
                 fontsize=12, y=1.02)
    fig.tight_layout()

    for ext in ("pdf", "png"):
        out = FIGURES_DIR / f"fig24_gate_diagnostic.{ext}"
        fig.savefig(out, dpi=200, bbox_inches="tight")
        print(f"  wrote {out}")
    plt.close(fig)


# --------------- main ---------------

def main():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_fig17()
    plot_fig19()
    plot_fig20()
    plot_fig24()
    print("\nAll supplementary figures generated.")


if __name__ == "__main__":
    main()
