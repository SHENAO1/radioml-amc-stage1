"""Re-evaluate best_model.pt checkpoints to recover lost metric artifacts.

Walks results/paper_stage6/{experiment}/rml2016a/{model}/seed_{seed}/
directories, loads best_model.pt, and regenerates all metric files
(metrics_test.json, confusion CSVs, per-SNR/per-class CSVs, predictions,
training_summary.json, etc.) that were lost during a git stash mishap.

Does NOT retrain — only forward pass on the test set.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml
from torch import nn

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _bootstrap import PROJECT_ROOT  # noqa: E402

from radioml_amc.config import load_config  # noqa: E402
from radioml_amc.data.dataset import DataBundle, SignalDataset, load_data_bundle  # noqa: E402
from radioml_amc.data.split import load_split_artifact, load_split_summary  # noqa: E402
from radioml_amc.profiling import measure_latency  # noqa: E402
from radioml_amc.reporting.paper_outputs import (  # noqa: E402
    write_paper_metric_artifacts,
)
from radioml_amc.training.metrics import evaluate_predictions  # noqa: E402
from radioml_amc.training.trainer import (  # noqa: E402
    _loop,
    _move_to_device,
    _save_json,
    build_model,
    count_model_parameters,
    empty_latency_report,
    feature_config_for_model,
    get_device,
    model_required_views,
    summarize_model_complexity,
    write_paper_json,
)
from radioml_amc.visualization.plot_confusion import plot_confusion_matrix  # noqa: E402
from radioml_amc.visualization.plot_snr_curve import plot_accuracy_vs_snr  # noqa: E402
from radioml_amc.visualization.plot_class_accuracy import plot_per_class_accuracy  # noqa: E402

SPLIT_NPZ = PROJECT_ROOT / "data/splits/rml2016a/stratified_by_mod_snr_seed42.npz"
SPLIT_SUMMARY_JSON = PROJECT_ROOT / "data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json"
SPLIT_ID = "stratified_by_mod_snr_seed42"

EXPERIMENTS = {
    "extended_budget_3090": {
        "config": "configs/paper/rml2016a_extended_budget_3090.yaml",
        "evidence_label": "EXTENDED_BUDGET_3090",
        "models": ["cldnn", "resnet1d", "iq_param_matched", "fusion_iq_stft"],
    },
    "fusion_cldnn_stft_aug_ls_3090": {
        "config": "configs/paper/rml2016a_fusion_cldnn_stft_aug_ls_3090.yaml",
        "evidence_label": "FUSION_CLDNN_STFT_AUG_LS_3090",
        "models": ["fusion_cldnn_stft"],
    },
    "low_snr_weighted_ce_3090": {
        "config": "configs/paper/rml2016a_low_snr_weighted_ce_3090.yaml",
        "evidence_label": "LOW_SNR_WEIGHTED_CE_3090",
        "models": ["cldnn", "fusion_iq_stft"],
    },
}

SEEDS = [42, 2025, 3407]


def load_data_and_splits():
    """Load dataset and fixed splits once (shared across all evals)."""
    config = {
        "data": {"mode": "real", "dataset": "RML2016.10A", "raw_path": "auto"},
        "project": {"seed": 42},
    }
    bundle = load_data_bundle(config, project_root=str(PROJECT_ROOT))
    splits = load_split_artifact(str(SPLIT_NPZ))
    split_summary = load_split_summary(str(SPLIT_SUMMARY_JSON))
    split_summary["split_source"] = "artifact"
    split_summary["split_artifact_npz"] = str(SPLIT_NPZ)
    return bundle, splits, split_summary


def make_test_loader(bundle: DataBundle, splits, feature_config, batch_size=256, num_workers=4):
    """Build test dataloader."""
    test_indices = splits["test"]
    test_dataset = SignalDataset(
        x=bundle.x[test_indices],
        y=bundle.y[test_indices],
        snr=bundle.snr[test_indices],
        feature_config=feature_config,
    )
    return torch.utils.data.DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=False,
    )


def recover_run(run_dir: Path, model_id: str, seed: int, bundle, splits, split_summary, device):
    """Recover all metric artifacts for a single run."""
    ckpt_path = run_dir / "best_model.pt"
    if not ckpt_path.exists():
        print(f"  SKIP (no checkpoint): {run_dir}")
        return False

    already_complete = (run_dir / "metrics_test.json").exists() and (run_dir / "training_summary.json").exists()
    if already_complete:
        print(f"  SKIP (already complete): {run_dir}")
        return True

    print(f"  RECOVERING: {model_id} seed={seed} ...")

    checkpoint = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    feature_config = checkpoint.get("feature_config")
    if not isinstance(feature_config, dict):
        feature_config = {"views": model_required_views(model_id)}
    if "views" not in feature_config:
        feature_config["views"] = model_required_views(model_id)

    model = build_model(model_id, num_classes=len(bundle.mod_names), feature_config=feature_config).to(device)
    state_dict = checkpoint.get("model_state_dict", checkpoint)
    model.load_state_dict(state_dict)

    test_loader = make_test_loader(bundle, splits, feature_config)

    # Complexity
    sample_x, _, _ = next(iter(test_loader))
    sample_input = _move_to_device(sample_x, device)
    complexity = summarize_model_complexity(
        model, sample_input, model_id=model_id,
        dataset="RadioML2016.10A",
        feature_preprocess={
            "uses_stft": "stft" in feature_config["views"],
            "uses_cwt": "cwt" in feature_config["views"],
            "cached": False,
        },
    )
    _save_json(complexity, run_dir / "complexity.json")

    # Latency
    write_paper_json(
        empty_latency_report(model_id=model_id, status="recovered_eval", note="Latency not re-measured during recovery."),
        run_dir / "latency.json",
    )

    # Evaluate
    criterion = nn.CrossEntropyLoss()
    t0 = time.perf_counter()
    test_loss, test_acc, y_pred, y_true, snr_true, test_logits = _loop(
        model, test_loader, criterion, device, collect_logits=True,
    )
    inference_time = time.perf_counter() - t0

    eval_metrics = evaluate_predictions(y_true, y_pred, snr_true, bundle.mod_names)
    eval_metrics["loss"] = float(test_loss)
    eval_metrics["loader_accuracy"] = float(test_acc)

    # Write metrics_test.json
    metrics = {
        "model": model_id,
        "model_name": model_id,
        "dataset": "RadioML2016.10A",
        "data_mode": "real",
        "run_dir": str(run_dir),
        "device": str(device),
        "checkpoint": str(ckpt_path),
        "feature_views": feature_config["views"],
        "feature_config": feature_config,
        "split_id": SPLIT_ID,
        "train_seed": seed,
        "num_parameters": count_model_parameters(model, model_id),
        "train_time_seconds": None,
        "inference_time_seconds": float(inference_time),
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
        "split_summary": dict(split_summary),
    }
    _save_json(metrics, run_dir / "metrics_test.json")

    # Write paper-format artifacts (per_snr.csv, per_class.csv, predictions.csv, confusion CSVs)
    write_paper_metric_artifacts(
        run_dir,
        logits=test_logits,
        y_true=y_true,
        snr=snr_true,
        sample_ids=splits["test"],
        class_names=bundle.mod_names,
        dataset="RadioML2016.10A",
        split_id=SPLIT_ID,
        model_id=model_id,
        train_seed=seed,
    )

    # Split summary
    ss = dict(split_summary)
    ss["train_seed"] = seed
    _save_json(ss, run_dir / "split_summary.json")

    # Training summary
    write_paper_json(
        {
            "model_id": model_id,
            "dataset": "RadioML2016.10A",
            "split_id": SPLIT_ID,
            "train_seed": seed,
            "checkpoint": str(ckpt_path),
            "train_time_seconds": None,
            "inference_time_seconds": float(inference_time),
            "best_epoch": checkpoint.get("epoch"),
        },
        run_dir / "training_summary.json",
    )

    # Config resolved
    config_resolved = {
        "data": {
            "dataset": "RadioML2016.10A",
            "split_source": "artifact",
            "split_id": SPLIT_ID,
            "split_artifact_npz": str(SPLIT_NPZ),
        },
        "features": feature_config,
        "train": {"model": model_id},
        "project": {"seed": seed},
        "recovered": True,
    }
    with open(run_dir / "config_resolved.yaml", "w") as f:
        yaml.dump(config_resolved, f, default_flow_style=False)

    # Plots
    plots_dir = run_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    try:
        plot_confusion_matrix(eval_metrics["confusion_matrix"], bundle.mod_names, plots_dir / "confusion_matrix.png", normalize=False)
        plot_confusion_matrix(eval_metrics["confusion_matrix"], bundle.mod_names, plots_dir / "normalized_confusion_matrix.png", normalize=True)
        plot_accuracy_vs_snr(eval_metrics["per_snr_accuracy"], plots_dir / "accuracy_vs_snr.png")
        plot_per_class_accuracy(eval_metrics["per_class_accuracy"], plots_dir / "per_class_accuracy.png")
    except Exception as e:
        print(f"    Warning: plot generation failed: {e}")

    # Label mapping
    _save_json({name: i for i, name in enumerate(bundle.mod_names)}, run_dir / "label_mapping.json")

    # Data summary
    _save_json({
        "mode": "real",
        "dataset": "RadioML2016.10A",
        "num_samples": len(bundle.x),
        "num_classes": len(bundle.mod_names),
        "class_names": bundle.mod_names,
    }, run_dir / "data_summary.json")
    _save_json({
        "mode": "real",
        "dataset": "RadioML2016.10A",
        "num_samples": len(bundle.x),
        "num_classes": len(bundle.mod_names),
        "class_names": bundle.mod_names,
    }, run_dir / "dataset_summary.json")

    print(f"    OK: acc={eval_metrics['overall_accuracy']:.4f}")
    return True


def main():
    device = get_device("auto")
    print(f"Device: {device}")
    print("Loading dataset and splits...")
    bundle, splits, split_summary = load_data_and_splits()
    print(f"Dataset loaded: {len(bundle.x)} samples, {len(bundle.mod_names)} classes")

    total = 0
    recovered = 0
    skipped = 0
    failed = 0

    for exp_name, exp_info in EXPERIMENTS.items():
        exp_root = PROJECT_ROOT / "results" / "paper_stage6" / exp_name / "rml2016a"
        print(f"\n=== {exp_name} ({exp_info['evidence_label']}) ===")
        for model_id in exp_info["models"]:
            for seed in SEEDS:
                run_dir = exp_root / model_id / f"seed_{seed}"
                total += 1
                if not run_dir.exists():
                    print(f"  SKIP (dir missing): {run_dir}")
                    skipped += 1
                    continue
                try:
                    ok = recover_run(run_dir, model_id, seed, bundle, splits, split_summary, device)
                    if ok:
                        recovered += 1
                    else:
                        skipped += 1
                except Exception as e:
                    print(f"  FAILED: {model_id} seed={seed}: {e}")
                    failed += 1

    print(f"\n=== Summary ===")
    print(f"Total: {total}, Recovered: {recovered}, Skipped: {skipped}, Failed: {failed}")


if __name__ == "__main__":
    main()
