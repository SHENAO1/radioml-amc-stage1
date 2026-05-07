from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.model_selection import train_test_split


def _can_stratify(labels: np.ndarray, holdout_size: float) -> bool:
    unique, counts = np.unique(labels, return_counts=True)
    if len(unique) < 2 or np.min(counts) < 2:
        return False
    n = labels.shape[0]
    n_holdout = int(np.ceil(n * holdout_size)) if holdout_size < 1 else int(holdout_size)
    n_train = n - n_holdout
    return n_holdout >= len(unique) and n_train >= len(unique)


def _stratify_labels(y: np.ndarray, snr: np.ndarray, strategy: str) -> np.ndarray | None:
    if strategy == "stratified":
        return y
    if strategy == "stratified_by_mod_snr":
        return np.asarray([f"{int(label)}_{int(snr_value)}" for label, snr_value in zip(y, snr)])
    return None


def make_splits(
    y: np.ndarray,
    snr: np.ndarray,
    test_size: float = 0.2,
    val_size: float = 0.1,
    strategy: str = "stratified",
    seed: int = 42,
) -> dict[str, np.ndarray]:
    indices = np.arange(y.shape[0])
    labels = _stratify_labels(y, snr, strategy)
    first_stratify = labels if labels is not None and _can_stratify(labels, test_size) else None

    trainval_idx, test_idx = train_test_split(
        indices,
        test_size=test_size,
        random_state=seed,
        shuffle=True,
        stratify=first_stratify,
    )

    val_fraction_of_trainval = val_size / max(1e-8, 1.0 - test_size)
    labels_trainval = labels[trainval_idx] if labels is not None else None
    second_stratify = (
        labels_trainval
        if labels_trainval is not None and _can_stratify(labels_trainval, val_fraction_of_trainval)
        else None
    )
    train_idx, val_idx = train_test_split(
        trainval_idx,
        test_size=val_fraction_of_trainval,
        random_state=seed,
        shuffle=True,
        stratify=second_stratify,
    )
    return {
        "train": np.asarray(train_idx, dtype=np.int64),
        "val": np.asarray(val_idx, dtype=np.int64),
        "test": np.asarray(test_idx, dtype=np.int64),
    }


def summarize_splits(
    splits: dict[str, np.ndarray],
    y: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
    strategy: str,
    seed: int,
) -> dict[str, Any]:
    total = int(y.shape[0])
    summary: dict[str, Any] = {
        "strategy": strategy,
        "seed": int(seed),
        "total_samples": total,
        "splits": {},
    }
    for name, indices in splits.items():
        split_y = y[indices]
        split_snr = snr[indices]
        class_counts = {
            class_names[int(label)]: int(count)
            for label, count in zip(*np.unique(split_y, return_counts=True))
        }
        snr_counts = {
            str(int(snr_value)): int(count)
            for snr_value, count in zip(*np.unique(split_snr, return_counts=True))
        }
        group_counts: dict[str, int] = {}
        for class_idx, snr_value in zip(split_y, split_snr):
            key = f"{class_names[int(class_idx)]}@{int(snr_value)}"
            group_counts[key] = group_counts.get(key, 0) + 1
        summary["splits"][name] = {
            "num_samples": int(indices.shape[0]),
            "ratio": float(indices.shape[0] / total) if total else 0.0,
            "class_counts": class_counts,
            "snr_counts": snr_counts,
            "modulation_snr_counts": dict(sorted(group_counts.items())),
        }
    return summary
