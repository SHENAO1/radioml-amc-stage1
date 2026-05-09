from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, recall_score


def snr_group_name(snr_value: int) -> str:
    value = int(snr_value)
    if value <= -6:
        return "low"
    if -4 <= value <= 6:
        return "mid"
    if value >= 8:
        return "high"
    return "other"


def snr_group_masks(snr: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "low": snr <= -6,
        "mid": (snr >= -4) & (snr <= 6),
        "high": snr >= 8,
    }


def normalize_confusion_matrix(confusion: np.ndarray) -> np.ndarray:
    cm = confusion.astype(np.float32)
    denom = cm.sum(axis=1, keepdims=True)
    return np.divide(cm, np.maximum(denom, 1.0))


def safe_column_name(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value).strip("_").lower()


def softmax_numpy(logits: np.ndarray) -> np.ndarray:
    if logits.ndim != 2:
        raise ValueError(f"Expected logits with shape [N, C], got {logits.shape}")
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / np.maximum(exp.sum(axis=1, keepdims=True), 1e-12)


def write_json(payload: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_prediction_csv(
    path: str | Path,
    logits: np.ndarray,
    y_true: np.ndarray,
    snr: np.ndarray,
    sample_ids: np.ndarray,
    class_names: list[str],
    dataset: str,
    split_id: str,
    model_id: str,
    train_seed: int,
    split: str = "test",
    extra_columns: dict[str, np.ndarray] | None = None,
) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    logits = np.asarray(logits, dtype=np.float64)
    y_true = np.asarray(y_true, dtype=np.int64)
    snr = np.asarray(snr, dtype=np.int64)
    sample_ids = np.asarray(sample_ids, dtype=np.int64)
    y_pred = logits.argmax(axis=1).astype(np.int64)
    probs = softmax_numpy(logits)
    if not (len(y_true) == len(snr) == len(sample_ids) == logits.shape[0]):
        raise ValueError("Prediction arrays must have matching first dimension.")

    class_columns = [safe_column_name(name) for name in class_names]
    fieldnames = [
        "sample_id",
        "dataset",
        "split_id",
        "split",
        "model_id",
        "train_seed",
        "snr_db",
        "snr_group",
        "modulation",
        "y_true",
        "y_pred",
        "correct",
    ]
    fieldnames.extend(f"logit_{name}" for name in class_columns)
    fieldnames.extend(f"prob_{name}" for name in class_columns)
    extras = dict(extra_columns or {})
    fieldnames.extend(extras.keys())

    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx in range(logits.shape[0]):
            true_idx = int(y_true[idx])
            pred_idx = int(y_pred[idx])
            row: dict[str, Any] = {
                "sample_id": int(sample_ids[idx]),
                "dataset": dataset,
                "split_id": split_id,
                "split": split,
                "model_id": model_id,
                "train_seed": int(train_seed),
                "snr_db": int(snr[idx]),
                "snr_group": snr_group_name(int(snr[idx])),
                "modulation": class_names[true_idx],
                "y_true": true_idx,
                "y_pred": pred_idx,
                "correct": int(true_idx == pred_idx),
            }
            for class_idx, class_col in enumerate(class_columns):
                row[f"logit_{class_col}"] = float(logits[idx, class_idx])
                row[f"prob_{class_col}"] = float(probs[idx, class_idx])
            for key, values in extras.items():
                row[key] = values[idx].item() if hasattr(values[idx], "item") else values[idx]
            writer.writerow(row)
    return output


def per_snr_metric_rows(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
    dataset: str,
    split_id: str,
    model_id: str,
    train_seed: int,
) -> list[dict[str, Any]]:
    labels = list(range(len(class_names)))
    rows: list[dict[str, Any]] = []
    for snr_value in sorted(np.unique(snr).tolist()):
        mask = snr == snr_value
        yt = y_true[mask]
        yp = y_pred[mask]
        rows.append(
            {
                "dataset": dataset,
                "model_id": model_id,
                "split_id": split_id,
                "train_seed": int(train_seed),
                "snr_db": int(snr_value),
                "num_samples": int(mask.sum()),
                "accuracy": float(np.mean(yp == yt)) if yt.size else None,
                "macro_f1": float(f1_score(yt, yp, labels=labels, average="macro", zero_division=0)) if yt.size else None,
                "balanced_accuracy": float(recall_score(yt, yp, labels=labels, average="macro", zero_division=0))
                if yt.size
                else None,
            }
        )
    return rows


def per_class_metric_rows(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
    dataset: str,
    split_id: str,
    model_id: str,
    train_seed: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for class_idx, class_name in enumerate(class_names):
        mask = y_true == class_idx
        rows.append(
            {
                "dataset": dataset,
                "model_id": model_id,
                "split_id": split_id,
                "train_seed": int(train_seed),
                "class_id": int(class_idx),
                "modulation": class_name,
                "num_samples": int(mask.sum()),
                "accuracy": float(np.mean(y_pred[mask] == y_true[mask])) if np.any(mask) else None,
            }
        )
    return rows


def write_rows_csv(path: str | Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output


def write_confusion_csv(
    path: str | Path,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list[str],
    normalize: bool = False,
) -> Path:
    labels = list(range(len(class_names)))
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    values = normalize_confusion_matrix(matrix) if normalize else matrix
    rows: list[dict[str, Any]] = []
    for row_idx, class_name in enumerate(class_names):
        row: dict[str, Any] = {"true_modulation": class_name}
        for col_idx, pred_name in enumerate(class_names):
            row[f"pred_{safe_column_name(pred_name)}"] = float(values[row_idx, col_idx]) if normalize else int(values[row_idx, col_idx])
        rows.append(row)
    return write_rows_csv(path, rows)


def build_metrics_summary(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    snr: np.ndarray,
    class_names: list[str],
) -> dict[str, Any]:
    labels = list(range(len(class_names)))
    masks = snr_group_masks(snr)
    summary: dict[str, Any] = {
        "overall_accuracy": float(np.mean(y_pred == y_true)) if y_true.size else None,
        "macro_f1": float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)) if y_true.size else None,
        "balanced_accuracy": float(recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
        if y_true.size
        else None,
    }
    for group, mask in masks.items():
        yt = y_true[mask]
        yp = y_pred[mask]
        summary[f"{group}_snr_accuracy"] = float(np.mean(yp == yt)) if yt.size else None
        summary[f"{group}_snr_macro_f1"] = (
            float(f1_score(yt, yp, labels=labels, average="macro", zero_division=0)) if yt.size else None
        )
    return summary


def write_paper_metric_artifacts(
    output_dir: str | Path,
    logits: np.ndarray,
    y_true: np.ndarray,
    snr: np.ndarray,
    sample_ids: np.ndarray,
    class_names: list[str],
    dataset: str,
    split_id: str,
    model_id: str,
    train_seed: int,
    extra_prediction_columns: dict[str, np.ndarray] | None = None,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    logits = np.asarray(logits)
    y_true = np.asarray(y_true, dtype=np.int64)
    snr = np.asarray(snr, dtype=np.int64)
    y_pred = logits.argmax(axis=1).astype(np.int64)

    paths = {
        "predictions": write_prediction_csv(
            output / "predictions_test.csv",
            logits=logits,
            y_true=y_true,
            snr=snr,
            sample_ids=sample_ids,
            class_names=class_names,
            dataset=dataset,
            split_id=split_id,
            model_id=model_id,
            train_seed=train_seed,
            extra_columns=extra_prediction_columns,
        ),
        "per_snr": write_rows_csv(
            output / "metrics_per_snr.csv",
            per_snr_metric_rows(y_true, y_pred, snr, class_names, dataset, split_id, model_id, train_seed),
        ),
        "per_class": write_rows_csv(
            output / "metrics_per_class.csv",
            per_class_metric_rows(y_true, y_pred, class_names, dataset, split_id, model_id, train_seed),
        ),
        "confusion_overall": write_confusion_csv(output / "confusion_overall.csv", y_true, y_pred, class_names),
    }
    low_mask = snr <= -6
    paths["confusion_low_snr"] = write_confusion_csv(
        output / "confusion_low_snr.csv",
        y_true[low_mask],
        y_pred[low_mask],
        class_names,
    )
    write_json(
        build_metrics_summary(y_true, y_pred, snr, class_names)
        | {"dataset": dataset, "split_id": split_id, "model_id": model_id, "train_seed": int(train_seed)},
        output / "metrics_test.json",
    )
    paths["metrics_test"] = output / "metrics_test.json"
    return paths


def aggregate_mean_std(
    rows: list[dict[str, Any]],
    group_keys: list[str],
    value_keys: list[str],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(tuple(row[key] for key in group_keys), []).append(row)

    output: list[dict[str, Any]] = []
    for key, group_rows in sorted(grouped.items()):
        result = {name: value for name, value in zip(group_keys, key)}
        result["num_seeds"] = len(group_rows)
        for value_key in value_keys:
            values = [float(row[value_key]) for row in group_rows if row.get(value_key) is not None]
            result[f"{value_key}_mean"] = float(np.mean(values)) if values else None
            result[f"{value_key}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0 if values else None
        output.append(result)
    return output
