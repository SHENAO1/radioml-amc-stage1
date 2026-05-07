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


def snr_group_accuracy(y_true: np.ndarray, y_pred: np.ndarray, snr: np.ndarray) -> dict[str, float | None]:
    groups = {
        "low_snr_accuracy": snr <= -6,
        "mid_snr_accuracy": (snr >= -4) & (snr <= 6),
        "high_snr_accuracy": snr >= 8,
    }
    result: dict[str, float | None] = {}
    for name, mask in groups.items():
        result[name] = float(np.mean(y_pred[mask] == y_true[mask])) if np.any(mask) else None
    return result


def normalize_confusion_matrix(confusion: np.ndarray) -> np.ndarray:
    cm = confusion.astype(np.float32)
    denom = cm.sum(axis=1, keepdims=True)
    return np.divide(cm, np.maximum(denom, 1.0))


def evaluate_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
) -> dict[str, Any]:
    labels = list(range(len(class_names)))
    overall = float(np.mean(y_pred == y_true))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    snr_groups = snr_group_accuracy(y_true, y_pred, snr)
    return {
        "overall_accuracy": overall,
        "low_snr_accuracy": snr_groups["low_snr_accuracy"],
        "mid_snr_accuracy": snr_groups["mid_snr_accuracy"],
        "high_snr_accuracy": snr_groups["high_snr_accuracy"],
        "per_class_accuracy": per_class_accuracy(y_true, y_pred, class_names),
        "per_snr_accuracy": per_snr_accuracy(y_true, y_pred, snr),
        "confusion_matrix": cm.astype(int).tolist(),
        "normalized_confusion_matrix": normalize_confusion_matrix(cm).tolist(),
    }
