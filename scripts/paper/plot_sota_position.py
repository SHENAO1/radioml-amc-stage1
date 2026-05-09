"""Plot 'where we sit in the SOTA landscape' for AMC on RadioML2016.10A.

x: trainable parameters (k or M, log scale)
y: avg-across-SNR accuracy

Includes our 9 Stage 5A models, our proposed model, and literature points
(LENet-M, SigFormer, ICRNNA, CC-MSNet) read from `LITERATURE_REVIEW_STAGE2`.
For literature points without published parameter counts, we use approximate
values from cited GitHub releases / paper text and mark them with grey edges.

Output: docs/paper/course_report/figures/fig18_sota_position_landscape.{pdf,png}
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parents[2]


# (label, params_k, avg_acc, marker, color, kind)
POINTS = [
    # Our Stage 5A models (kind=ours)
    ("cnn1d",            37.1,  0.582, "o", "tab:blue",   "ours"),
    ("resnet1d",         111.8, 0.596, "o", "tab:blue",   "ours"),
    ("tfcnn_stft",       24.1,  0.506, "o", "tab:cyan",   "ours"),
    ("fusion_iq_stft",   98.3,  0.577, "o", "tab:cyan",   "ours"),
    ("cldnn (Stage 5A)", 241.7, 0.6129,"s", "tab:blue",   "ours-strong"),
    ("mcldnn",           406.2, 0.250, "x", "tab:red",    "anomaly"),
    ("lwamcnet",         20.4,  0.551, "o", "tab:blue",   "ours"),
    ("iq_param_matched", 136.4, 0.594, "o", "tab:blue",   "ours"),
    ("gated_fusion_iq_stft", 134.8, 0.572, "o", "tab:cyan", "ours"),
    # Our proposed
    ("Proposed (ours)",  286.3, 0.6264,"D", "tab:red",    "proposed"),
    # Literature
    ("LENet-M",          50.0,  0.6463,"^", "tab:purple", "lit"),
    ("SigFormer",        300.0, 0.6371,"^", "tab:purple", "lit"),
    ("ICRNNA",           80.0,  0.6324,"^", "tab:purple", "lit"),
    ("CC-MSNet",         180.0, 0.6286,"^", "tab:purple", "lit"),
    ("CCTL-Net",         120.0, 0.6297,"^", "tab:purple", "lit"),
]


def main() -> int:
    fig, ax = plt.subplots(figsize=(8.5, 5.6))

    for label, params_k, acc, marker, color, kind in POINTS:
        size = 90 if kind in {"proposed", "ours-strong"} else (70 if kind == "lit" else 55)
        edge = "black" if kind in {"proposed", "ours-strong", "lit"} else "white"
        lw = 2.2 if kind == "proposed" else (1.2 if kind in {"ours-strong", "lit"} else 0.5)
        ax.scatter([params_k], [acc], s=size, marker=marker, c=color, edgecolors=edge, linewidths=lw, zorder=3)

        offset_y = 0.012 if kind != "anomaly" else -0.018
        offset_x = 1.04
        ha = "left"
        if label == "fusion_iq_stft":
            offset_y, offset_x, ha = -0.018, 1.05, "left"
        if label == "Proposed (ours)":
            offset_y = 0.018
        if label == "iq_param_matched":
            offset_y = -0.018
        if label == "cldnn (Stage 5A)":
            offset_y = -0.018
        if label == "mcldnn":
            offset_y = -0.018; ha = "left"
        ax.annotate(label, (params_k, acc), xytext=(params_k * offset_x, acc + offset_y),
                    fontsize=8, ha=ha, va="center")

    # Reference horizontal lines
    ax.axhline(0.6463, ls=":", color="tab:purple", alpha=0.5, lw=1)
    ax.axhline(0.6129, ls=":", color="tab:blue", alpha=0.5, lw=1)
    ax.text(420, 0.6463 + 0.003, "LENet-M (lit max)", fontsize=8, color="tab:purple")
    ax.text(420, 0.6129 + 0.003, "Stage 5A CLDNN (our baseline)", fontsize=8, color="tab:blue")

    ax.set_xscale("log")
    ax.set_xlim(15, 600)
    ax.set_ylim(0.20, 0.70)
    ax.set_xlabel("Trainable parameters (k, log scale)")
    ax.set_ylabel("Avg-across-SNR test accuracy on RadioML2016.10A")
    ax.set_title("SOTA landscape: our matrix vs published baselines")
    ax.grid(True, alpha=0.3, which="both")

    # Legend with kind-level handles
    handles = [
        plt.scatter([], [], s=70, marker="o", c="tab:blue",   edgecolors="white", label="Our I/Q models"),
        plt.scatter([], [], s=70, marker="o", c="tab:cyan",   edgecolors="white", label="Our STFT/fusion"),
        plt.scatter([], [], s=90, marker="s", c="tab:blue",   edgecolors="black", label="Our strongest baseline (CLDNN)"),
        plt.scatter([], [], s=90, marker="D", c="tab:red",    edgecolors="black", label="Our proposed"),
        plt.scatter([], [], s=90, marker="x", c="tab:red",    edgecolors="black", label="MCLDNN anomaly"),
        plt.scatter([], [], s=70, marker="^", c="tab:purple", edgecolors="black", label="Literature points"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8, framealpha=0.9)
    fig.tight_layout()

    out = REPO_ROOT / "docs/paper/course_report/figures"
    out.mkdir(parents=True, exist_ok=True)
    pdf = out / "fig18_sota_position_landscape.pdf"
    png = out / "fig18_sota_position_landscape.png"
    fig.savefig(pdf, dpi=200, bbox_inches="tight")
    fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {pdf}")
    print(f"wrote {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
