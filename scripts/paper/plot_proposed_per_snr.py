"""Generate per-SNR accuracy curve comparing 4 model variants.

Lines:
  - Stage 5A CLDNN (computed from archived predictions)
  - Stage 5A fusion_iq_stft (computed from archived predictions)
  - P1.1 fusion_iq_stft (extended budget, same schedule as A 方案 except no aug, no LS, weak backbone)
  - A 方案 fusion_cldnn_stft + aug + LS

Output:
  docs/paper/course_report/figures/fig17_proposed_per_snr_comparison.{pdf,png}
"""
from __future__ import annotations

import csv
import glob
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]


def stage5a_per_snr(model: str) -> dict[int, float]:
    """Compute per-SNR mean accuracy aggregated over 3 Stage 5A seeds from archived predictions."""
    accs: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for seed in (42, 2025, 3407):
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
    """Average per-SNR accuracy across seeds from metrics_per_snr.csv files."""
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


def main() -> int:
    series = {
        "Stage 5A CLDNN": stage5a_per_snr("cldnn"),
        "Stage 5A fusion_iq_stft": stage5a_per_snr("fusion_iq_stft"),
        "P1.1 fusion_iq_stft (matched schedule)": stage6_per_snr(
            "results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft/seed_*/metrics_per_snr.csv"
        ),
        "Proposed fusion_cldnn_stft + aug": stage6_per_snr(
            "results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a/arch_aug/fusion_cldnn_stft/seed_*/metrics_per_snr.csv"
        ),
    }
    snrs = sorted(set(snr for d in series.values() for snr in d))

    styles = {
        "Stage 5A CLDNN": {"linestyle": "-", "marker": "o", "color": "tab:blue"},
        "Stage 5A fusion_iq_stft": {"linestyle": "--", "marker": "s", "color": "tab:gray"},
        "P1.1 fusion_iq_stft (matched schedule)": {"linestyle": ":", "marker": "^", "color": "tab:orange"},
        "Proposed fusion_cldnn_stft + aug": {"linestyle": "-", "marker": "D", "color": "tab:red", "linewidth": 2.4},
    }

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    for label, d in series.items():
        xs = sorted(d)
        ys = [d[x] for x in xs]
        kw = styles[label]
        ax.plot(xs, ys, label=label, **kw)
    ax.axvspan(-20, -6, alpha=0.06, color="gray")
    ax.axvspan(8, 18, alpha=0.06, color="green")
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Test accuracy (3-seed mean)")
    ax.set_title("Per-SNR accuracy: Stage 5A baselines, P1.1, and proposed model")
    ax.set_xticks(snrs[::2])
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=9)
    fig.tight_layout()

    out_dir = REPO_ROOT / "docs/paper/course_report/figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "fig17_proposed_per_snr_comparison.pdf"
    png_path = out_dir / "fig17_proposed_per_snr_comparison.png"
    fig.savefig(pdf_path, dpi=200, bbox_inches="tight")
    fig.savefig(png_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {pdf_path}")
    print(f"wrote {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
