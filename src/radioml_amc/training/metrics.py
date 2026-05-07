from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import confusion_matrix


def accuracy_from_logits(logits, targets) -> float:
    preds = logits.argmax(dim=1)
    return float((preds == targets).float().mean().item())


def per_class_accuracy(y_true: np.ndarray, y_pred: np.ndarray, class_names: list[str]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for idx, name in enumerate(class_names):
        mask = y_true == idx
        if not np.any(mask):
            result[name] = None
        else:
            result[name] = float(np.mean(y_pred[mask] == y_true[mask]))
    return result


def per_snr_accuracy(y_true: np.ndarray, y_pred: np.ndarray, snr: np.ndarray) -> dict[str, float]:
    result: dict[str, float] = {}
    for snr_value in sorted(np.unique(snr).tolist()):
        mask = snr == snr_value
        result[str(int(snr_value))] = float(np.mean(y_pred[mask] == y_true[mask]))
    return result


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
) -> dict[str, Any]:
    labels = list(range(len(class_names)))
    overall = float(np.mean(y_pred == y_true))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return {
        "overall_accuracy": overall,
        "per_class_accuracy": per_class_accuracy(y_true, y_pred, class_names),
        "per_snr_accuracy": per_snr_accuracy(y_true, y_pred, snr),
        "confusion_matrix": cm.astype(int).tolist(),
    }

