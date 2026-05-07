from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset

from radioml_amc.config import save_config
from radioml_amc.data.dataset import DataBundle, SignalDataset, load_data_bundle, summarize_data_bundle
from radioml_amc.data.split import make_splits
from radioml_amc.logger import setup_logger
from radioml_amc.models.cnn1d import CNN1D, count_parameters as count_cnn_parameters
from radioml_amc.models.resnet1d import ResNet1D, count_parameters as count_resnet_parameters
from radioml_amc.paths import create_run_dir, resolve_project_path
from radioml_amc.reporting import make_stage1_report
from radioml_amc.seed import set_seed
from radioml_amc.training.metrics import evaluate_predictions
from radioml_amc.visualization.plot_confusion import plot_confusion_matrix
from radioml_amc.visualization.plot_signals import save_signal_example_plots
from radioml_amc.visualization.plot_snr_curve import plot_accuracy_vs_snr
from radioml_amc.visualization.plot_training import plot_training_curve


def get_device(requested: str = "auto") -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def build_model(model_name: str, num_classes: int) -> nn.Module:
    normalized = model_name.lower()
    if normalized == "cnn1d":
        return CNN1D(num_classes=num_classes)
    if normalized in {"resnet1d", "residualcnn1d"}:
        return ResNet1D(num_classes=num_classes)
    raise ValueError(f"Unsupported model: {model_name}")


def count_model_parameters(model: nn.Module, model_name: str) -> int:
    if model_name.lower() == "cnn1d":
        return count_cnn_parameters(model)
    return count_resnet_parameters(model)


def _make_loaders(
    bundle: DataBundle,
    splits: dict[str, np.ndarray],
    batch_size: int,
    num_workers: int,
    device: torch.device,
) -> dict[str, DataLoader]:
    dataset = SignalDataset(bundle.x, bundle.y, bundle.snr)
    pin_memory = device.type == "cuda"
    return {
        name: DataLoader(
            Subset(dataset, indices.tolist()),
            batch_size=batch_size,
            shuffle=(name == "train"),
            num_workers=num_workers,
            pin_memory=pin_memory,
        )
        for name, indices in splits.items()
    }


def _loop(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray]:
    is_train = optimizer is not None
    model.train(is_train)
    total_loss = 0.0
    total_correct = 0
    total = 0
    all_preds: list[np.ndarray] = []
    all_targets: list[np.ndarray] = []
    all_snrs: list[np.ndarray] = []

    for x, y, snr in loader:
        x = x.to(device)
        y = y.to(device)
        if is_train:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(is_train):
            logits = model(x)
            loss = criterion(logits, y)
            if is_train:
                loss.backward()
                optimizer.step()

        preds = logits.argmax(dim=1)
        batch_size = int(y.shape[0])
        total_loss += float(loss.item()) * batch_size
        total_correct += int((preds == y).sum().item())
        total += batch_size
        all_preds.append(preds.detach().cpu().numpy())
        all_targets.append(y.detach().cpu().numpy())
        all_snrs.append(snr.detach().cpu().numpy())

    avg_loss = total_loss / max(1, total)
    avg_acc = total_correct / max(1, total)
    return (
        avg_loss,
        avg_acc,
        np.concatenate(all_preds) if all_preds else np.asarray([], dtype=np.int64),
        np.concatenate(all_targets) if all_targets else np.asarray([], dtype=np.int64),
        np.concatenate(all_snrs) if all_snrs else np.asarray([], dtype=np.int64),
    )


def _save_json(payload: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def _save_history_csv(history: list[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not history:
        return
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(history[0].keys()))
        writer.writeheader()
        writer.writerows(history)


def _save_label_mapping(bundle: DataBundle, run_dir: Path) -> None:
    payload = {
        "mode": bundle.mode,
        "mod_names": bundle.mod_names,
        "class_to_idx": {name: idx for idx, name in enumerate(bundle.mod_names)},
        "idx_to_class": {str(idx): name for idx, name in enumerate(bundle.mod_names)},
        "snr_values": [int(v) for v in bundle.snr_values],
        "metadata": bundle.metadata,
    }
    _save_json(payload, run_dir / "label_mapping.json")


def _prepare_run(
    config: dict[str, Any],
    model_name: str,
    project_root: str | Path | None,
) -> tuple[Path, logging.Logger]:
    run_root = config.get("outputs", {}).get("run_root", "runs")
    run_dir = create_run_dir(run_root, model_name, project_root=project_root)
    save_config(config, run_dir / "config.yaml")
    logger = setup_logger("radioml_amc", run_dir / "logs.txt")
    return run_dir, logger


def _log_data_summary(logger: logging.Logger, summary: dict[str, Any]) -> None:
    logger.info("Data mode: %s", summary["mode"])
    logger.info("Data shape: %s, dtype=%s", summary["shape"], summary["dtype"])
    logger.info("Modulations: %s", ", ".join(summary["mod_names"]))
    logger.info("SNR values: %s", summary["snr_values"])
    logger.info("Class counts: %s", summary["class_counts"])
    logger.info("SNR counts: %s", summary["snr_counts"])


def run_training(
    config: dict[str, Any],
    model_name_override: str | None = None,
    project_root: str | Path | None = None,
) -> Path:
    seed = int(config.get("project", {}).get("seed", 42))
    set_seed(seed)

    bundle = load_data_bundle(config, project_root=str(project_root) if project_root else None)
    model_name = model_name_override or str(config.get("train", {}).get("model", "cnn1d"))
    config.setdefault("train", {})["model"] = model_name
    run_dir, logger = _prepare_run(config, model_name, project_root)

    summary = summarize_data_bundle(bundle)
    _save_json(summary, run_dir / "data_summary.json")
    _save_label_mapping(bundle, run_dir)
    _log_data_summary(logger, summary)
    if bundle.mode == "mock":
        logger.info("Mock data is for engineering smoke tests only; do not use it as research evidence.")

    data_cfg = config.get("data", {})
    splits = make_splits(
        y=bundle.y,
        snr=bundle.snr,
        test_size=float(data_cfg.get("test_size", 0.2)),
        val_size=float(data_cfg.get("val_size", 0.1)),
        strategy=str(data_cfg.get("split_strategy", "stratified")),
        seed=seed,
    )
    logger.info("Split sizes: train=%d, val=%d, test=%d", len(splits["train"]), len(splits["val"]), len(splits["test"]))

    train_cfg = config.get("train", {})
    device = get_device(str(train_cfg.get("device", "auto")))
    loaders = _make_loaders(
        bundle,
        splits,
        batch_size=int(train_cfg.get("batch_size", 32)),
        num_workers=int(train_cfg.get("num_workers", 0)),
        device=device,
    )

    model = build_model(model_name, num_classes=len(bundle.mod_names)).to(device)
    num_parameters = count_model_parameters(model, model_name)
    logger.info("Model: %s, parameters=%d, device=%s", model_name, num_parameters, device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(train_cfg.get("learning_rate", 1e-3)),
        weight_decay=float(train_cfg.get("weight_decay", 1e-4)),
    )

    epochs = int(train_cfg.get("epochs", 2))
    patience = int(train_cfg.get("early_stopping_patience", epochs))
    save_checkpoint = bool(config.get("outputs", {}).get("save_checkpoint", True))
    save_plots = bool(config.get("outputs", {}).get("save_plots", True))
    history: list[dict[str, Any]] = []
    best_val_acc = -1.0
    best_epoch = 0
    stale_epochs = 0

    for epoch in range(1, epochs + 1):
        train_loss, train_acc, _, _, _ = _loop(model, loaders["train"], criterion, device, optimizer)
        val_loss, val_acc, _, _, _ = _loop(model, loaders["val"], criterion, device)
        row = {
            "epoch": epoch,
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
        }
        history.append(row)
        logger.info(
            "Epoch %d/%d | train loss %.4f acc %.4f | val loss %.4f acc %.4f",
            epoch,
            epochs,
            train_loss,
            train_acc,
            val_loss,
            val_acc,
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            stale_epochs = 0
            if save_checkpoint:
                torch.save(
                    {
                        "model_state_dict": model.state_dict(),
                        "model_name": model_name,
                        "num_classes": len(bundle.mod_names),
                        "mod_names": bundle.mod_names,
                        "epoch": epoch,
                        "best_val_acc": best_val_acc,
                    },
                    run_dir / "best_model.pt",
                )
        else:
            stale_epochs += 1
            if stale_epochs >= patience:
                logger.info("Early stopping at epoch %d", epoch)
                break

    if save_checkpoint and (run_dir / "best_model.pt").exists():
        checkpoint = torch.load(run_dir / "best_model.pt", map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])

    test_loss, test_acc, y_pred, y_true, snr_true = _loop(model, loaders["test"], criterion, device)
    test_metrics = evaluate_predictions(y_true, y_pred, snr_true, bundle.mod_names)
    test_metrics["loss"] = float(test_loss)
    test_metrics["loader_accuracy"] = float(test_acc)
    logger.info("Test loss %.4f, overall accuracy %.4f", test_loss, test_metrics["overall_accuracy"])
    logger.info("Per-class accuracy: %s", test_metrics["per_class_accuracy"])
    logger.info("Per-SNR accuracy: %s", test_metrics["per_snr_accuracy"])

    metrics = {
        "model_name": model_name,
        "device": str(device),
        "num_parameters": num_parameters,
        "best_epoch": best_epoch,
        "best_val_acc": best_val_acc,
        "history": history,
        "test": test_metrics,
        "data_summary": summary,
    }
    _save_json(metrics, run_dir / "metrics.json")
    _save_history_csv(history, run_dir / "metrics.csv")

    if save_plots:
        plot_training_curve(history, run_dir / "plots" / "training_curve.png")
        plot_confusion_matrix(test_metrics["confusion_matrix"], bundle.mod_names, run_dir / "plots" / "confusion_matrix.png")
        plot_accuracy_vs_snr(test_metrics["per_snr_accuracy"], run_dir / "plots" / "accuracy_vs_snr.png")
        save_signal_example_plots(bundle, run_dir / "plots", config.get("stft", {}), seed=seed)

    if bool(config.get("outputs", {}).get("save_report", True)):
        make_stage1_report(run_dir)

    return run_dir


def evaluate_checkpoint(
    config: dict[str, Any],
    checkpoint_path: str | Path,
    project_root: str | Path | None = None,
) -> Path:
    seed = int(config.get("project", {}).get("seed", 42))
    set_seed(seed)
    bundle = load_data_bundle(config, project_root=str(project_root) if project_root else None)
    checkpoint_file = resolve_project_path(checkpoint_path, project_root)
    if not checkpoint_file.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_file}")

    checkpoint = torch.load(checkpoint_file, map_location="cpu")
    model_name = str(checkpoint.get("model_name", config.get("train", {}).get("model", "cnn1d")))
    run_dir, logger = _prepare_run(config, f"eval_{model_name}", project_root)
    _save_label_mapping(bundle, run_dir)
    summary = summarize_data_bundle(bundle)
    _save_json(summary, run_dir / "data_summary.json")
    _log_data_summary(logger, summary)

    data_cfg = config.get("data", {})
    splits = make_splits(
        y=bundle.y,
        snr=bundle.snr,
        test_size=float(data_cfg.get("test_size", 0.2)),
        val_size=float(data_cfg.get("val_size", 0.1)),
        strategy=str(data_cfg.get("split_strategy", "stratified")),
        seed=seed,
    )
    train_cfg = config.get("train", {})
    device = get_device(str(train_cfg.get("device", "auto")))
    loaders = _make_loaders(
        bundle,
        splits,
        batch_size=int(train_cfg.get("batch_size", 32)),
        num_workers=int(train_cfg.get("num_workers", 0)),
        device=device,
    )

    model = build_model(model_name, num_classes=len(bundle.mod_names)).to(device)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    criterion = nn.CrossEntropyLoss()
    test_loss, test_acc, y_pred, y_true, snr_true = _loop(model, loaders["test"], criterion, device)
    eval_metrics = evaluate_predictions(y_true, y_pred, snr_true, bundle.mod_names)
    eval_metrics["loss"] = float(test_loss)
    eval_metrics["loader_accuracy"] = float(test_acc)
    logger.info("Evaluation checkpoint: %s", checkpoint_file)
    logger.info("Test loss %.4f, overall accuracy %.4f", test_loss, eval_metrics["overall_accuracy"])

    metrics = {
        "model_name": model_name,
        "device": str(device),
        "checkpoint": str(checkpoint_file),
        "evaluation": eval_metrics,
        "test": eval_metrics,
        "data_summary": summary,
    }
    _save_json(metrics, run_dir / "metrics.json")
    plot_confusion_matrix(eval_metrics["confusion_matrix"], bundle.mod_names, run_dir / "plots" / "confusion_matrix.png")
    plot_accuracy_vs_snr(eval_metrics["per_snr_accuracy"], run_dir / "plots" / "accuracy_vs_snr.png")
    save_signal_example_plots(bundle, run_dir / "plots", config.get("stft", {}), seed=seed)
    make_stage1_report(run_dir)
    return run_dir

