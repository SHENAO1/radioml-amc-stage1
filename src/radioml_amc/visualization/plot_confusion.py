from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def plot_confusion_matrix(
    confusion: list[list[int]] | np.ndarray,
    class_names: list[str],
    output_path: str | Path,
    normalize: bool = True,
) -> str:
    cm = np.asarray(confusion, dtype=np.float32)
    if normalize:
        denom = cm.sum(axis=1, keepdims=True)
        cm_plot = np.divide(cm, np.maximum(denom, 1.0))
    else:
        cm_plot = cm

    fig, ax = plt.subplots(figsize=(max(6, 0.55 * len(class_names)), max(5, 0.5 * len(class_names))))
    im = ax.imshow(cm_plot, interpolation="nearest", cmap="Blues", vmin=0)
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_xticks(np.arange(len(class_names)), labels=class_names, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(class_names)), labels=class_names)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    threshold = float(cm_plot.max()) / 2.0 if cm_plot.size else 0.0
    for i in range(cm_plot.shape[0]):
        for j in range(cm_plot.shape[1]):
            text = f"{cm_plot[i, j]:.2f}" if normalize else str(int(cm_plot[i, j]))
            ax.text(j, i, text, ha="center", va="center", color="white" if cm_plot[i, j] > threshold else "black", fontsize=8)

    fig.tight_layout()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return str(path)

