from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def plot_per_class_accuracy(per_class_accuracy: dict[str, float | None], output_path: str | Path) -> str:
    names = list(per_class_accuracy.keys())
    values = [0.0 if per_class_accuracy[name] is None else float(per_class_accuracy[name]) for name in names]

    fig, ax = plt.subplots(figsize=(max(7.0, 0.55 * len(names)), 4.8))
    ax.bar(names, values, color="#4c78a8")
    ax.set_title("Per-Class Accuracy")
    ax.set_xlabel("Modulation")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0.0, 1.02)
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=45)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    fig.tight_layout()

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return str(path)
