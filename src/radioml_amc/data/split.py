from __future__ import annotations

import json
from pathlib import Path
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


def make_split_id(strategy: str, seed: int) -> str:
    return f"{strategy}_seed{int(seed)}"


def save_split_artifact(
    splits: dict[str, np.ndarray],
    y: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
    output_dir: str | Path,
    strategy: str,
    seed: int,
    dataset_name: str = "rml2016a",
    split_ratios: dict[str, float] | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    split_id = make_split_id(strategy, seed)
    npz_path = output / f"{split_id}.npz"
    summary_path = output / f"{split_id}_summary.json"

    np.savez_compressed(
        npz_path,
        train_idx=np.asarray(splits["train"], dtype=np.int64),
        val_idx=np.asarray(splits["val"], dtype=np.int64),
        test_idx=np.asarray(splits["test"], dtype=np.int64),
    )

    summary = summarize_splits(
        splits=splits,
        y=y,
        snr=snr,
        class_names=class_names,
        strategy=strategy,
        seed=seed,
    )
    summary.update(
        {
            "dataset": dataset_name,
            "split_id": split_id,
            "split_ratios": split_ratios or {},
            "class_mapping": {name: idx for idx, name in enumerate(class_names)},
            "snr_values": [int(value) for value in sorted(np.unique(snr).tolist())],
            "metadata": dict(metadata or {}),
            "artifact_npz": str(npz_path),
        }
    )
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return npz_path, summary_path


def load_split_artifact(path: str | Path) -> dict[str, np.ndarray]:
    artifact = Path(path)
    with np.load(artifact) as data:
        return {
            "train": np.asarray(data["train_idx"], dtype=np.int64),
            "val": np.asarray(data["val_idx"], dtype=np.int64),
            "test": np.asarray(data["test_idx"], dtype=np.int64),
        }


def load_split_summary(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"Split summary must be a JSON object: {path}")
    return payload


def create_split_artifact(
    y: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
    output_dir: str | Path,
    test_size: float = 0.2,
    val_size: float = 0.1,
    strategy: str = "stratified_by_mod_snr",
    seed: int = 42,
    dataset_name: str = "rml2016a",
    metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, np.ndarray], Path, Path]:
    splits = make_splits(
        y=y,
        snr=snr,
        test_size=test_size,
        val_size=val_size,
        strategy=strategy,
        seed=seed,
    )
    npz_path, summary_path = save_split_artifact(
        splits=splits,
        y=y,
        snr=snr,
        class_names=class_names,
        output_dir=output_dir,
        strategy=strategy,
        seed=seed,
        dataset_name=dataset_name,
        split_ratios={"train": 1.0 - test_size - val_size, "val": val_size, "test": test_size},
        metadata=metadata,
    )
    return splits, npz_path, summary_path
