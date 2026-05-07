from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def plot_accuracy_vs_snr(per_snr_accuracy: dict[str, float], output_path: str | Path) -> str:
    pairs = sorted((int(k), float(v)) for k, v in per_snr_accuracy.items())
    snrs = [p[0] for p in pairs]
    accs = [p[1] for p in pairs]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(snrs, accs, marker="o", linewidth=1.8)
    ax.set_title("Accuracy vs SNR")
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.0, 1.02)
    ax.grid(alpha=0.3)
    fig.tight_layout()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return str(path)

