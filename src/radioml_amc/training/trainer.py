from __future__ import annotations

import csv
import json
import logging
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Subset

from radioml_amc.config import save_config
from radioml_amc.data.dataset import (
    DataBundle,
    SignalDataset,
    load_data_bundle,
    normalize_feature_config,
    summarize_data_bundle,
)
from radioml_amc.data.split import load_split_artifact, load_split_summary, make_split_id, make_splits, summarize_splits
from radioml_amc.logger import setup_logger
from radioml_amc.models.baselines import CLDNN, LWAMCNet, MCLDNN, ParameterMatchedIQOnlyNet
from radioml_amc.models.cnn1d import CNN1D
from radioml_amc.models.gated_fusion import ScalarGatedIQSTFTFusionNet
from radioml_amc.models.multiview import MultiViewFusionNet, TimeFrequencyCNN
from radioml_amc.models.resnet1d import ResNet1D
from radioml_amc.paths import create_run_dir, resolve_project_path
from radioml_amc.profiling import empty_latency_report, summarize_model_complexity
from radioml_amc.reporting import make_stage1_5_report, make_stage1_report
from radioml_amc.reporting.paper_outputs import write_json as write_paper_json
from radioml_amc.reporting.paper_outputs import write_paper_metric_artifacts
from radioml_amc.seed import set_seed
from radioml_amc.training.metrics import evaluate_predictions
from radioml_amc.visualization.plot_confusion import plot_confusion_matrix
from radioml_amc.visualization.plot_class_accuracy import plot_per_class_accuracy
from radioml_amc.visualization.plot_signals import save_signal_example_plots
from radioml_amc.visualization.plot_snr_curve import plot_accuracy_vs_snr
from radioml_amc.visualization.plot_training import plot_training_curve


DIAGNOSTIC_EVIDENCE_TAGS = {"DIAGNOSTIC", "SMOKE TEST"}
PROTECTED_OUTPUT_ROOTS = ("results/paper_stage2/rml2016a",)


def get_device(requested: str = "auto") -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(requested)


def model_required_views(model_name: str) -> list[str]:
    normalized = model_name.lower()
    mapping = {
        "cnn1d": ["iq"],
        "cnn1d_iq": ["iq"],
        "resnet1d": ["iq"],
        "resnet1d_iq": ["iq"],
        "residualcnn1d": ["iq"],
        "cldnn": ["iq"],
        "cldnn_iq": ["iq"],
        "cnn_lstm": ["iq"],
        "cnn_lstm_iq": ["iq"],
        "iq_cldnn": ["iq"],
        "mcldnn": ["iq"],
        "mcldnn_iq": ["iq"],
        "lwamcnet": ["iq"],
        "lwamcnet_iq": ["iq"],
        "lw_amc_net": ["iq"],
        "lightweight_amc": ["iq"],
        "iq_param_matched": ["iq"],
        "parameter_matched_iq": ["iq"],
        "param_matched_iq": ["iq"],
        "tfcnn_stft": ["stft"],
        "stft_cnn2d": ["stft"],
        "tfcnn_cwt": ["cwt"],
        "cwt_cnn2d": ["cwt"],
        "fusion_iq_stft": ["iq", "stft"],
        "fusion_iq_amp_phase": ["iq", "amp_phase"],
        "fusion_iq_cwt": ["iq", "cwt"],
        "fusion_iq_stft_cwt": ["iq", "stft", "cwt"],
        "fusion_cldnn_stft": ["iq", "stft"],
        "gated_fusion_iq_stft": ["iq", "stft"],
        "scalar_gated_iq_stft": ["iq", "stft"],
    }
    if normalized not in mapping:
        raise ValueError(f"Unsupported model: {model_name}")
    return list(mapping[normalized])


def feature_config_for_model(config: dict[str, Any], model_name: str) -> dict[str, Any]:
    raw = dict(config.get("features", {}))
    if "views" not in raw:
        raw["views"] = model_required_views(model_name)
    if "amp_phase" not in raw:
        raw["amp_phase"] = {}
    if "stft" not in raw:
        raw["stft"] = dict(config.get("stft", {}))
    if "cwt" not in raw:
        raw["cwt"] = dict(config.get("cwt", {}))
    return normalize_feature_config(raw)


def build_model(model_name: str, num_classes: int, feature_config: dict[str, Any] | None = None) -> nn.Module:
    normalized = model_name.lower()
    if normalized in {"cnn1d", "cnn1d_iq"}:
        return CNN1D(num_classes=num_classes)
    if normalized in {"resnet1d", "resnet1d_iq", "residualcnn1d"}:
        return ResNet1D(num_classes=num_classes)
    if normalized in {"cldnn", "cldnn_iq", "cnn_lstm", "cnn_lstm_iq", "iq_cldnn"}:
        return CLDNN(num_classes=num_classes)
    if normalized in {"mcldnn", "mcldnn_iq"}:
        return MCLDNN(num_classes=num_classes)
    if normalized in {"lwamcnet", "lwamcnet_iq", "lw_amc_net", "lightweight_amc"}:
        return LWAMCNet(num_classes=num_classes)
    if normalized in {"iq_param_matched", "parameter_matched_iq", "param_matched_iq"}:
        return ParameterMatchedIQOnlyNet(num_classes=num_classes)
    if normalized in {"tfcnn_stft", "stft_cnn2d"}:
        return TimeFrequencyCNN(num_classes=num_classes, view="stft")
    if normalized in {"tfcnn_cwt", "cwt_cnn2d"}:
        return TimeFrequencyCNN(num_classes=num_classes, view="cwt")
    if normalized == "fusion_cldnn_stft":
        from radioml_amc.models.multiview import FusionCldnnStftNet
        return FusionCldnnStftNet(num_classes=num_classes)
    if normalized.startswith("fusion_"):
        views = list((feature_config or {}).get("views", model_required_views(model_name)))
        return MultiViewFusionNet(num_classes=num_classes, views=views)
    if normalized in {"gated_fusion_iq_stft", "scalar_gated_iq_stft"}:
        return ScalarGatedIQSTFTFusionNet(num_classes=num_classes)
    raise ValueError(f"Unsupported model: {model_name}")


def count_model_parameters(model: nn.Module, model_name: str) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def _make_loaders(
    bundle: DataBundle,
    splits: dict[str, np.ndarray],
    batch_size: int,
    num_workers: int,
    device: torch.device,
    feature_config: dict[str, Any] | None = None,
    augment_config: dict[str, Any] | None = None,
) -> dict[str, DataLoader]:
    from radioml_amc.data.augmentation import build_augmenter

    augmenter = build_augmenter(augment_config)
    eval_dataset = SignalDataset(bundle.x, bundle.y, bundle.snr, feature_config=feature_config)
    if augmenter is not None:
        train_dataset = SignalDataset(
            bundle.x, bundle.y, bundle.snr,
            feature_config=feature_config,
            augmenter=augmenter,
        )
    else:
        train_dataset = eval_dataset
    pin_memory = device.type == "cuda"
    loaders: dict[str, DataLoader] = {}
    for name, indices in splits.items():
        ds = train_dataset if name == "train" else eval_dataset
        loaders[name] = DataLoader(
            Subset(ds, indices.tolist()),
            batch_size=batch_size,
            shuffle=(name == "train"),
            num_workers=num_workers,
            pin_memory=pin_memory,
        )
    return loaders


def _move_to_device(batch: Any, device: torch.device) -> Any:
    if torch.is_tensor(batch):
        return batch.to(device)
    if isinstance(batch, dict):
        return {key: _move_to_device(value, device) for key, value in batch.items()}
    return batch


def _loop(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
    collect_logits: bool = False,
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    is_train = optimizer is not None
    model.train(is_train)
    total_loss = 0.0
    total_correct = 0
    total = 0
    all_preds: list[np.ndarray] = []
    all_targets: list[np.ndarray] = []
    all_snrs: list[np.ndarray] = []
    all_logits: list[np.ndarray] = []

    from radioml_amc.training.losses import compute_loss

    for x, y, snr in loader:
        x = _move_to_device(x, device)
        y = y.to(device)
        snr_dev = snr.to(device)
        if is_train:
            optimizer.zero_grad(set_to_none=True)

        with torch.set_grad_enabled(is_train):
            logits = model(x)
            loss = compute_loss(criterion, logits, y, snr_dev)
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
        if collect_logits:
            all_logits.append(logits.detach().cpu().numpy())

    avg_loss = total_loss / max(1, total)
    avg_acc = total_correct / max(1, total)
    return (
        avg_loss,
        avg_acc,
        np.concatenate(all_preds) if all_preds else np.asarray([], dtype=np.int64),
        np.concatenate(all_targets) if all_targets else np.asarray([], dtype=np.int64),
        np.concatenate(all_snrs) if all_snrs else np.asarray([], dtype=np.int64),
        np.concatenate(all_logits) if all_logits else np.asarray([], dtype=np.float32).reshape(0, 0),
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
        "snr_to_idx": {str(int(value)): idx for idx, value in enumerate(bundle.snr_values)},
        "idx_to_snr": {str(idx): int(value) for idx, value in enumerate(bundle.snr_values)},
        "metadata": bundle.metadata,
    }
    _save_json(payload, run_dir / "label_mapping.json")


def _normalize_evidence_tag(value: Any) -> str:
    return str(value).strip().upper().replace("_", " ")


def _resolve_evidence_tag(config: dict[str, Any], bundle: DataBundle) -> str:
    evidence_cfg = config.get("evidence", {})
    outputs_cfg = config.get("outputs", {})
    tag = (
        evidence_cfg.get("tag")
        or evidence_cfg.get("evidence_tag")
        or outputs_cfg.get("evidence_tag")
        or bundle.metadata.get("evidence_tag")
    )
    if tag:
        return _normalize_evidence_tag(tag)
    if bundle.mode == "mock":
        return "SMOKE TEST"
    if bool(config.get("data", {}).get("subset_mode", False)):
        return "DIAGNOSTIC"
    return "PROJECT_SUPPORTED"


def _path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_output_root_policy(
    config: dict[str, Any],
    run_root: str | Path,
    project_root: str | Path | None,
    evidence_tag: str | None,
) -> None:
    outputs_cfg = config.get("outputs", {})
    if bool(outputs_cfg.get("allow_protected_output_root", False)):
        return

    protected_roots = outputs_cfg.get("protected_roots", PROTECTED_OUTPUT_ROOTS)
    if not protected_roots:
        return

    normalized_tag = _normalize_evidence_tag(evidence_tag or "")
    stage_name = str(config.get("project", {}).get("stage", "")).lower()
    run_root_path = resolve_project_path(run_root, project_root).resolve(strict=False)
    root_text = str(run_root_path).lower()
    is_diagnostic_scope = (
        normalized_tag in DIAGNOSTIC_EVIDENCE_TAGS
        or "stage6b" in stage_name
        or "diagnostic" in root_text
        or "smoke" in root_text
        or "subset" in root_text
    )
    if not is_diagnostic_scope:
        return

    for protected_root in protected_roots:
        protected_path = resolve_project_path(protected_root, project_root).resolve(strict=False)
        if run_root_path == protected_path or _path_is_relative_to(run_root_path, protected_path):
            raise ValueError(
                "Refusing to write diagnostic/smoke/subset output under protected result root "
                f"{protected_path}. Use results/paper_stage6/diagnostic or set "
                "outputs.allow_protected_output_root only in an explicitly approved full-run script."
            )


def _prepare_run(
    config: dict[str, Any],
    model_name: str,
    project_root: str | Path | None,
    evidence_tag: str | None = None,
) -> tuple[Path, logging.Logger]:
    run_root = config.get("outputs", {}).get("run_root", "runs")
    _validate_output_root_policy(config, run_root, project_root, evidence_tag)
    run_dir = create_run_dir(run_root, model_name, project_root=project_root)
    save_config(config, run_dir / "config.yaml")
    save_config(config, run_dir / "config_resolved.yaml")
    logger = setup_logger("radioml_amc", run_dir / "logs.txt")
    return run_dir, logger


def _log_data_summary(logger: logging.Logger, summary: dict[str, Any]) -> None:
    logger.info("Data mode: %s", summary["mode"])
    logger.info("Data shape: %s, dtype=%s", summary["shape"], summary["dtype"])
    logger.info("Modulations: %s", ", ".join(summary["mod_names"]))
    logger.info("SNR values: %s", summary["snr_values"])
    logger.info("Class counts: %s", summary["class_counts"])
    logger.info("SNR counts: %s", summary["snr_counts"])


def _validate_split_indices(splits: dict[str, np.ndarray], num_samples: int) -> None:
    required = {"train", "val", "test"}
    missing = sorted(required.difference(splits))
    if missing:
        raise ValueError(f"Split artifact is missing required splits: {missing}")
    for name in sorted(required):
        indices = np.asarray(splits[name], dtype=np.int64)
        if indices.ndim != 1:
            raise ValueError(f"Split '{name}' must be a 1D index array, got shape {indices.shape}")
        if indices.size and (int(indices.min()) < 0 or int(indices.max()) >= num_samples):
            raise ValueError(f"Split '{name}' has indices outside dataset length {num_samples}")


def _split_summary_path_for_artifact(split_artifact_path: Path) -> Path:
    return split_artifact_path.with_name(f"{split_artifact_path.stem}_summary.json")


def resolve_experiment_splits(
    config: dict[str, Any],
    bundle: DataBundle,
    project_root: str | Path | None,
    train_seed: int,
) -> tuple[dict[str, np.ndarray], dict[str, Any], str]:
    data_cfg = config.get("data", {})
    split_artifact = data_cfg.get("split_artifact_npz") or data_cfg.get("split_artifact")
    if split_artifact:
        split_path = resolve_project_path(split_artifact, project_root)
        splits = load_split_artifact(split_path)
        _validate_split_indices(splits, int(bundle.y.shape[0]))

        configured_summary = data_cfg.get("split_summary_json")
        summary_path = resolve_project_path(configured_summary, project_root) if configured_summary else _split_summary_path_for_artifact(split_path)
        if summary_path.exists():
            split_summary = load_split_summary(summary_path)
        else:
            strategy = str(data_cfg.get("split_strategy", "stratified_by_mod_snr"))
            split_seed = int(data_cfg.get("split_seed", data_cfg.get("seed", 42)))
            split_summary = summarize_splits(
                splits=splits,
                y=bundle.y,
                snr=bundle.snr,
                class_names=bundle.mod_names,
                strategy=strategy,
                seed=split_seed,
            )
            split_summary["split_id"] = make_split_id(strategy, split_seed)

        split_id = str(split_summary.get("split_id", split_path.stem))
        split_summary = dict(split_summary)
        split_summary["split_source"] = "artifact"
        split_summary["split_artifact_npz"] = str(split_path)
        split_summary["split_summary_json"] = str(summary_path) if summary_path.exists() else None
        split_summary["train_seed"] = int(train_seed)
        return splits, split_summary, split_id

    strategy = str(data_cfg.get("split_strategy", "stratified"))
    split_seed = int(data_cfg.get("split_seed", train_seed))
    splits = make_splits(
        y=bundle.y,
        snr=bundle.snr,
        test_size=float(data_cfg.get("test_size", 0.2)),
        val_size=float(data_cfg.get("val_size", 0.1)),
        strategy=strategy,
        seed=split_seed,
    )
    split_summary = summarize_splits(
        splits=splits,
        y=bundle.y,
        snr=bundle.snr,
        class_names=bundle.mod_names,
        strategy=strategy,
        seed=split_seed,
    )
    split_id = make_split_id(strategy, split_seed)
    split_summary["split_id"] = split_id
    split_summary["split_source"] = "generated"
    split_summary["train_seed"] = int(train_seed)
    return splits, split_summary, split_id


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
    feature_config = feature_config_for_model(config, model_name)
    config["features"] = feature_config
    evidence_tag = _resolve_evidence_tag(config, bundle)
    config.setdefault("evidence", {})["tag"] = evidence_tag
    splits, split_summary, split_id = resolve_experiment_splits(config, bundle, project_root, seed)
    config.setdefault("data", {})["split_id"] = split_id
    config["data"]["split_source"] = split_summary.get("split_source")
    run_dir, logger = _prepare_run(config, model_name, project_root, evidence_tag=evidence_tag)

    summary = summarize_data_bundle(bundle)
    dataset_name = str(config.get("data", {}).get("dataset", bundle.mode))
    _save_json(summary, run_dir / "dataset_summary.json")
    _save_json(summary, run_dir / "data_summary.json")
    _save_label_mapping(bundle, run_dir)
    _log_data_summary(logger, summary)
    if bundle.mode == "mock":
        logger.info("Mock data is for engineering smoke tests only; do not use it as research evidence.")

    _save_json(split_summary, run_dir / "split_summary.json")
    logger.info("Split sizes: train=%d, val=%d, test=%d", len(splits["train"]), len(splits["val"]), len(splits["test"]))

    train_cfg = config.get("train", {})
    device = get_device(str(train_cfg.get("device", "auto")))
    loaders = _make_loaders(
        bundle,
        splits,
        batch_size=int(train_cfg.get("batch_size", 32)),
        num_workers=int(train_cfg.get("num_workers", 0)),
        device=device,
        feature_config=feature_config,
        augment_config=train_cfg.get("augmentation"),
    )

    model = build_model(model_name, num_classes=len(bundle.mod_names), feature_config=feature_config).to(device)
    num_parameters = count_model_parameters(model, model_name)
    logger.info("Model: %s, views=%s, parameters=%d, device=%s", model_name, feature_config["views"], num_parameters, device)
    sample_x, _, _ = next(iter(loaders["test"]))
    sample_input = _move_to_device(sample_x, device)
    complexity_payload = summarize_model_complexity(
        model,
        sample_input,
        model_id=model_name,
        dataset=dataset_name,
        feature_preprocess={
            "uses_stft": "stft" in feature_config["views"],
            "uses_cwt": "cwt" in feature_config["views"],
            "cached": False,
        },
    )
    _save_json(complexity_payload, run_dir / "complexity.json")
    write_paper_json(
        empty_latency_report(
            model_id=model_name,
            status="not_measured_in_training_loop",
            note="Use scripts/paper/measure_complexity_latency.py for controlled latency measurement.",
        ),
        run_dir / "latency.json",
    )

    from radioml_amc.training.losses import build_criterion

    criterion = build_criterion(train_cfg.get("loss"))
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(train_cfg.get("learning_rate", 1e-3)),
        weight_decay=float(train_cfg.get("weight_decay", 1e-4)),
    )

    epochs = int(train_cfg.get("epochs", 2))
    patience = int(train_cfg.get("early_stopping_patience", epochs))

    scheduler = None
    scheduler_cfg = train_cfg.get("scheduler")
    if scheduler_cfg:
        if isinstance(scheduler_cfg, str):
            scheduler_name = scheduler_cfg
            warmup_epochs = 0
        else:
            scheduler_name = str(scheduler_cfg.get("name", "cosine")).lower()
            warmup_epochs = int(scheduler_cfg.get("warmup_epochs", 0))
        if scheduler_name == "cosine":
            import math as _math

            def _lr_lambda(epoch_idx: int) -> float:
                if warmup_epochs > 0 and epoch_idx < warmup_epochs:
                    return float(epoch_idx + 1) / float(warmup_epochs)
                denom = max(1, epochs - warmup_epochs)
                progress = float(epoch_idx - warmup_epochs) / denom
                return 0.5 * (1.0 + _math.cos(_math.pi * progress))

            scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=_lr_lambda)
        else:
            raise ValueError(f"Unsupported scheduler.name={scheduler_name!r}; only 'cosine' is supported.")

    save_checkpoint = bool(config.get("outputs", {}).get("save_checkpoint", True))
    save_plots = bool(config.get("outputs", {}).get("save_plots", True))
    history: list[dict[str, Any]] = []
    best_val_acc = -1.0
    best_epoch = 0
    stale_epochs = 0

    train_start = time.perf_counter()
    for epoch in range(1, epochs + 1):
        train_loss, train_acc, _, _, _, _ = _loop(model, loaders["train"], criterion, device, optimizer)
        val_loss, val_acc, _, _, _, _ = _loop(model, loaders["val"], criterion, device)
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
                        "feature_config": feature_config,
                        "feature_views": feature_config["views"],
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

        if scheduler is not None:
            scheduler.step()
    train_time_seconds = time.perf_counter() - train_start

    if save_checkpoint and (run_dir / "best_model.pt").exists():
        checkpoint = torch.load(run_dir / "best_model.pt", map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])

    inference_start = time.perf_counter()
    test_loss, test_acc, y_pred, y_true, snr_true, test_logits = _loop(
        model,
        loaders["test"],
        criterion,
        device,
        collect_logits=True,
    )
    inference_time_seconds = time.perf_counter() - inference_start
    test_metrics = evaluate_predictions(y_true, y_pred, snr_true, bundle.mod_names)
    test_metrics["loss"] = float(test_loss)
    test_metrics["loader_accuracy"] = float(test_acc)
    logger.info("Test loss %.4f, overall accuracy %.4f", test_loss, test_metrics["overall_accuracy"])
    logger.info("Per-class accuracy: %s", test_metrics["per_class_accuracy"])
    logger.info("Per-SNR accuracy: %s", test_metrics["per_snr_accuracy"])

    metrics = {
        "model": model_name,
        "model_name": model_name,
        "dataset": dataset_name,
        "data_mode": bundle.mode,
        "run_dir": str(run_dir),
        "device": str(device),
        "evidence_tag": evidence_tag,
        "feature_views": feature_config["views"],
        "feature_config": feature_config,
        "split_id": split_id,
        "train_seed": seed,
        "num_parameters": num_parameters,
        "model_complexity": {
            "num_parameters": num_parameters,
            "trainable_parameters": num_parameters,
            "input_views": feature_config["views"],
        },
        "train_time_seconds": float(train_time_seconds),
        "inference_time_seconds": float(inference_time_seconds),
        "best_epoch": best_epoch,
        "best_val_acc": best_val_acc,
        "overall_accuracy": test_metrics["overall_accuracy"],
        "low_snr_accuracy": test_metrics["low_snr_accuracy"],
        "mid_snr_accuracy": test_metrics["mid_snr_accuracy"],
        "high_snr_accuracy": test_metrics["high_snr_accuracy"],
        "per_snr_accuracy": test_metrics["per_snr_accuracy"],
        "per_class_accuracy": test_metrics["per_class_accuracy"],
        "confusion_matrix": test_metrics["confusion_matrix"],
        "normalized_confusion_matrix": test_metrics["normalized_confusion_matrix"],
        "history": history,
        "test": test_metrics,
        "data_summary": summary,
        "dataset_summary": summary,
        "split_summary": split_summary,
    }
    _save_json(metrics, run_dir / "metrics.json")
    _save_history_csv(history, run_dir / "metrics.csv")
    write_paper_metric_artifacts(
        run_dir,
        logits=test_logits,
        y_true=y_true,
        snr=snr_true,
        sample_ids=splits["test"],
        class_names=bundle.mod_names,
        dataset=dataset_name,
        split_id=split_id,
        model_id=model_name,
        train_seed=seed,
    )
    write_paper_json(
        {
            "model_id": model_name,
            "dataset": dataset_name,
            "split_id": split_id,
            "train_seed": seed,
            "epochs_requested": epochs,
            "best_epoch": best_epoch,
            "train_time_seconds": float(train_time_seconds),
            "train_time_sec_per_epoch": float(train_time_seconds / max(1, len(history))),
            "inference_time_seconds": float(inference_time_seconds),
            "evidence_tag": evidence_tag,
        },
        run_dir / "training_summary.json",
    )

    if save_plots:
        plot_training_curve(history, run_dir / "plots" / "training_curve.png")
        plot_confusion_matrix(
            test_metrics["confusion_matrix"],
            bundle.mod_names,
            run_dir / "plots" / "confusion_matrix.png",
            normalize=False,
        )
        plot_confusion_matrix(
            test_metrics["confusion_matrix"],
            bundle.mod_names,
            run_dir / "plots" / "normalized_confusion_matrix.png",
            normalize=True,
        )
        plot_accuracy_vs_snr(test_metrics["per_snr_accuracy"], run_dir / "plots" / "accuracy_vs_snr.png")
        plot_per_class_accuracy(test_metrics["per_class_accuracy"], run_dir / "plots" / "per_class_accuracy.png")
        save_signal_example_plots(bundle, run_dir / "plots", config.get("stft", {}), seed=seed)

    if bool(config.get("outputs", {}).get("save_report", True)):
        make_stage1_report(run_dir)
        make_stage1_5_report(run_dir)

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
    config.setdefault("train", {})["model"] = model_name
    checkpoint_feature_config = checkpoint.get("feature_config")
    if isinstance(checkpoint_feature_config, dict):
        feature_config = normalize_feature_config(checkpoint_feature_config)
    else:
        feature_config = feature_config_for_model(config, model_name)
    config["features"] = feature_config
    evidence_tag = _resolve_evidence_tag(config, bundle)
    config.setdefault("evidence", {})["tag"] = evidence_tag
    splits, split_summary, split_id = resolve_experiment_splits(config, bundle, project_root, seed)
    config.setdefault("data", {})["split_id"] = split_id
    config["data"]["split_source"] = split_summary.get("split_source")
    run_dir, logger = _prepare_run(config, f"eval_{model_name}", project_root, evidence_tag=evidence_tag)
    _save_label_mapping(bundle, run_dir)
    summary = summarize_data_bundle(bundle)
    _save_json(summary, run_dir / "dataset_summary.json")
    _save_json(summary, run_dir / "data_summary.json")
    _log_data_summary(logger, summary)

    _save_json(split_summary, run_dir / "split_summary.json")
    train_cfg = config.get("train", {})
    device = get_device(str(train_cfg.get("device", "auto")))
    loaders = _make_loaders(
        bundle,
        splits,
        batch_size=int(train_cfg.get("batch_size", 32)),
        num_workers=int(train_cfg.get("num_workers", 0)),
        device=device,
        feature_config=feature_config,
    )

    model = build_model(model_name, num_classes=len(bundle.mod_names), feature_config=feature_config).to(device)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)
    sample_x, _, _ = next(iter(loaders["test"]))
    sample_input = _move_to_device(sample_x, device)
    _save_json(
        summarize_model_complexity(
            model,
            sample_input,
            model_id=model_name,
            dataset=str(config.get("data", {}).get("dataset", bundle.mode)),
            feature_preprocess={
                "uses_stft": "stft" in feature_config["views"],
                "uses_cwt": "cwt" in feature_config["views"],
                "cached": False,
            },
        ),
        run_dir / "complexity.json",
    )
    write_paper_json(
        empty_latency_report(
            model_id=model_name,
            status="not_measured_in_evaluation_loop",
            note="Use scripts/paper/measure_complexity_latency.py for controlled latency measurement.",
        ),
        run_dir / "latency.json",
    )
    criterion = nn.CrossEntropyLoss()
    inference_start = time.perf_counter()
    test_loss, test_acc, y_pred, y_true, snr_true, test_logits = _loop(
        model,
        loaders["test"],
        criterion,
        device,
        collect_logits=True,
    )
    inference_time_seconds = time.perf_counter() - inference_start
    eval_metrics = evaluate_predictions(y_true, y_pred, snr_true, bundle.mod_names)
    eval_metrics["loss"] = float(test_loss)
    eval_metrics["loader_accuracy"] = float(test_acc)
    logger.info("Evaluation checkpoint: %s", checkpoint_file)
    logger.info("Test loss %.4f, overall accuracy %.4f", test_loss, eval_metrics["overall_accuracy"])

    metrics = {
        "model": model_name,
        "model_name": model_name,
        "dataset": str(config.get("data", {}).get("dataset", bundle.mode)),
        "data_mode": bundle.mode,
        "run_dir": str(run_dir),
        "device": str(device),
        "evidence_tag": evidence_tag,
        "checkpoint": str(checkpoint_file),
        "feature_views": feature_config["views"],
        "feature_config": feature_config,
        "split_id": split_id,
        "train_seed": seed,
        "num_parameters": count_model_parameters(model, model_name),
        "model_complexity": {
            "num_parameters": count_model_parameters(model, model_name),
            "trainable_parameters": count_model_parameters(model, model_name),
            "input_views": feature_config["views"],
        },
        "train_time_seconds": None,
        "inference_time_seconds": float(inference_time_seconds),
        "best_epoch": checkpoint.get("epoch"),
        "overall_accuracy": eval_metrics["overall_accuracy"],
        "low_snr_accuracy": eval_metrics["low_snr_accuracy"],
        "mid_snr_accuracy": eval_metrics["mid_snr_accuracy"],
        "high_snr_accuracy": eval_metrics["high_snr_accuracy"],
        "per_snr_accuracy": eval_metrics["per_snr_accuracy"],
        "per_class_accuracy": eval_metrics["per_class_accuracy"],
        "confusion_matrix": eval_metrics["confusion_matrix"],
        "normalized_confusion_matrix": eval_metrics["normalized_confusion_matrix"],
        "evaluation": eval_metrics,
        "test": eval_metrics,
        "data_summary": summary,
        "dataset_summary": summary,
        "split_summary": split_summary,
    }
    _save_json(metrics, run_dir / "metrics.json")
    dataset_name = str(config.get("data", {}).get("dataset", bundle.mode))
    write_paper_metric_artifacts(
        run_dir,
        logits=test_logits,
        y_true=y_true,
        snr=snr_true,
        sample_ids=splits["test"],
        class_names=bundle.mod_names,
        dataset=dataset_name,
        split_id=split_id,
        model_id=model_name,
        train_seed=seed,
    )
    write_paper_json(
        {
            "model_id": model_name,
            "dataset": dataset_name,
            "split_id": split_id,
            "train_seed": seed,
            "checkpoint": str(checkpoint_file),
            "train_time_seconds": None,
            "inference_time_seconds": float(inference_time_seconds),
            "evidence_tag": evidence_tag,
        },
        run_dir / "training_summary.json",
    )
    plot_confusion_matrix(eval_metrics["confusion_matrix"], bundle.mod_names, run_dir / "plots" / "confusion_matrix.png", normalize=False)
    plot_confusion_matrix(
        eval_metrics["confusion_matrix"],
        bundle.mod_names,
        run_dir / "plots" / "normalized_confusion_matrix.png",
        normalize=True,
    )
    plot_accuracy_vs_snr(eval_metrics["per_snr_accuracy"], run_dir / "plots" / "accuracy_vs_snr.png")
    plot_per_class_accuracy(eval_metrics["per_class_accuracy"], run_dir / "plots" / "per_class_accuracy.png")
    save_signal_example_plots(bundle, run_dir / "plots", config.get("stft", {}), seed=seed)
    make_stage1_report(run_dir)
    make_stage1_5_report(run_dir)
    return run_dir
