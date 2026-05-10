"""Ablation: CLDNN (I/Q only) + signal-domain augmentation + label smoothing.

Trains the CLDNN baseline with the SAME augmentation and label-smoothing
hyperparameters used in the proposed model (fusion_cldnn_stft + aug + LS),
to test whether the accuracy gain from augmentation requires the fusion
architecture or transfers equally to a simpler single-stream model.

Same fixed split, 3 seeds, extended-budget schedule as all Stage 6 experiments.
"""
from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import torch
import yaml

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _bootstrap import PROJECT_ROOT  # noqa: E402

from radioml_amc.config import load_config  # noqa: E402
from radioml_amc.profiling import measure_latency  # noqa: E402
from radioml_amc.training import trainer  # noqa: E402
from radioml_amc.training.trainer import (  # noqa: E402
    build_model,
    feature_config_for_model,
    get_device,
    model_required_views,
)


ALLOWED_MODELS = ["cldnn"]
ALLOWED_SEEDS = [42, 2025, 3407]
SPLIT_ID = "stratified_by_mod_snr_seed42"
SPLIT_NPZ = "data/splits/rml2016a/stratified_by_mod_snr_seed42.npz"
SPLIT_SUMMARY = "data/splits/rml2016a/stratified_by_mod_snr_seed42_summary.json"
RESULT_ROOT = Path("results/paper_stage6/cldnn_aug_ablation_3090/rml2016a")
STATUS_PATH = PROJECT_ROOT / RESULT_ROOT / "status.json"
REPORT_PATH = PROJECT_ROOT / "docs/paper/PAPER_STAGE6_CLDNN_AUG_ABLATION_3090_REPORT.md"
EVIDENCE_LABEL = "CLDNN_AUG_ABLATION_3090"
REQUIRED_ARTIFACTS = [
    "config_resolved.yaml",
    "metrics_test.json",
    "metrics_per_snr.csv",
    "metrics_per_class.csv",
    "predictions_test.csv",
    "confusion_overall.csv",
    "confusion_low_snr.csv",
    "complexity.json",
    "latency.json",
    "training_summary.json",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ablation: CLDNN + aug + label smoothing.")
    p.add_argument("--config", default="configs/paper/rml2016a_cldnn_aug_ablation_3090.yaml")
    p.add_argument("--single", action="store_true")
    p.add_argument("--model", choices=ALLOWED_MODELS)
    p.add_argument("--seed", type=int, choices=ALLOWED_SEEDS)
    p.add_argument("--resume", action="store_true")
    p.add_argument("--latency-device", default="cuda")
    p.add_argument("--latency-warmup-iters", type=int, default=50)
    p.add_argument("--latency-measured-iters", type=int, default=200)
    return p.parse_args()


def resolve(path: str | Path) -> Path:
    cand = Path(path)
    return cand if cand.is_absolute() else PROJECT_ROOT / cand


def load_status() -> dict[str, Any]:
    if STATUS_PATH.exists():
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    return {
        "stage": "Paper-Stage 6 CLDNN + Aug + LS Ablation (RTX 3090)",
        "evidence_label": EVIDENCE_LABEL,
        "dataset": "RadioML2016.10A",
        "split_id": SPLIT_ID,
        "models": ALLOWED_MODELS,
        "train_seeds": ALLOWED_SEEDS,
        "runs": {},
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_status(status: dict[str, Any]) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    status["updated_at"] = datetime.now().isoformat(timespec="seconds")
    STATUS_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def cell_key(model_id: str, seed: int) -> str:
    return f"{model_id}/seed_{seed}"


def run_dir_for(model_id: str, seed: int) -> Path:
    return PROJECT_ROOT / RESULT_ROOT / model_id / f"seed_{seed}"


def is_complete_run(run_dir: Path) -> bool:
    if not run_dir.exists():
        return False
    if any(not (run_dir / a).exists() for a in REQUIRED_ARTIFACTS):
        return False
    try:
        ts = json.loads((run_dir / "training_summary.json").read_text(encoding="utf-8"))
        m = json.loads((run_dir / "metrics_test.json").read_text(encoding="utf-8"))
        ss = json.loads((run_dir / "split_summary.json").read_text(encoding="utf-8"))
        rc = yaml.safe_load((run_dir / "config_resolved.yaml").read_text(encoding="utf-8"))
    except Exception:
        return False
    return (
        ts.get("split_id") == SPLIT_ID
        and m.get("split_id") == SPLIT_ID
        and ss.get("split_source") == "artifact"
        and rc.get("data", {}).get("split_source") == "artifact"
        and rc.get("data", {}).get("split_id") == SPLIT_ID
    )


def archive_incomplete(run_dir: Path) -> None:
    if not run_dir.exists() or is_complete_run(run_dir):
        return
    archive = run_dir.with_name(f"{run_dir.name}_incomplete_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.move(str(run_dir), str(archive))


def prepare_config(base_config: dict[str, Any], model_id: str, seed: int) -> dict[str, Any]:
    config = copy.deepcopy(base_config)
    config.setdefault("project", {})["seed"] = int(seed)
    config.setdefault("data", {})["mode"] = "real"
    config["data"]["dataset"] = "RML2016.10A"
    config["data"]["raw_path"] = "auto"
    config["data"]["subset_mode"] = False
    config["data"]["subset_mods"] = None
    config["data"]["subset_snrs"] = None
    config["data"]["max_samples_per_group"] = None
    config["data"]["split_strategy"] = "stratified_by_mod_snr"
    config["data"]["split_artifact_npz"] = SPLIT_NPZ
    config["data"]["split_summary_json"] = SPLIT_SUMMARY
    config.setdefault("features", {})["views"] = model_required_views(model_id)
    config.setdefault("train", {})["model"] = model_id
    config["train"]["device"] = "auto"
    config["train"]["epochs"] = int(config["train"].get("epochs", 50))
    config["train"]["batch_size"] = int(config["train"].get("batch_size", 256))
    config["train"]["num_workers"] = int(config["train"].get("num_workers", 4))
    config.setdefault("outputs", {})["run_root"] = str((RESULT_ROOT / model_id).as_posix())
    config["outputs"]["save_checkpoint"] = True
    config["outputs"]["save_plots"] = True
    config["outputs"]["save_report"] = True
    return config


def synthetic_input(views: list[str], batch_size: int, signal_length: int = 128) -> torch.Tensor | dict[str, torch.Tensor]:
    if views == ["iq"]:
        return torch.randn(batch_size, 2, signal_length)
    data: dict[str, torch.Tensor] = {}
    for v in views:
        if v in {"iq", "amp_phase"}:
            data[v] = torch.randn(batch_size, 2, signal_length)
        elif v == "stft":
            data[v] = torch.randn(batch_size, 1, 32, 7)
        elif v == "cwt":
            data[v] = torch.randn(batch_size, 1, 16, signal_length)
        else:
            raise ValueError(f"Unsupported synthetic view: {v}")
    return data


def merge_latency_reports(reports: list[dict[str, Any]], model_id: str, device: str, warmup: int, measured: int) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model_id": model_id,
        "device": device,
        "batch_sizes": [],
        "warmup_iters": int(warmup),
        "measured_iters": int(measured),
        "gpu_forward_excluding_preprocess_ms": {},
        "gpu_including_preprocess_ms": {},
        "cpu_including_preprocess_ms": {},
        "stft_preprocess_ms": {},
        "peak_inference_memory_mb": None,
        "evidence_tag": EVIDENCE_LABEL,
    }
    for r in reports:
        for bs in r.get("batch_sizes", []):
            if bs not in payload["batch_sizes"]:
                payload["batch_sizes"].append(bs)
        for k in [
            "gpu_forward_excluding_preprocess_ms",
            "gpu_including_preprocess_ms",
            "cpu_including_preprocess_ms",
            "stft_preprocess_ms",
        ]:
            payload[k].update(r.get(k, {}))
        peak = r.get("peak_inference_memory_mb")
        if peak is not None:
            payload["peak_inference_memory_mb"] = max(float(peak), float(payload["peak_inference_memory_mb"] or 0.0))
    payload["batch_sizes"] = sorted(payload["batch_sizes"])
    return payload


def write_controlled_latency(run_dir: Path, config: dict[str, Any], model_id: str, device_name: str, warmup: int, measured: int) -> None:
    fc = feature_config_for_model(config, model_id)
    model = build_model(model_id, num_classes=11, feature_config=fc)
    device = get_device(device_name)
    reports = []
    for bs in [1, 256]:
        reports.append(
            measure_latency(
                model,
                synthetic_input(fc["views"], bs),
                model_id=model_id,
                device=device,
                warmup_iters=warmup,
                measured_iters=measured,
            )
        )
    latency = merge_latency_reports(reports, model_id=model_id, device=str(device), warmup=warmup, measured=measured)
    (run_dir / "latency.json").write_text(json.dumps(latency, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_completed_run(run_dir: Path, model_id: str, seed: int) -> dict[str, Any]:
    missing = [a for a in REQUIRED_ARTIFACTS if not (run_dir / a).exists()]
    if missing:
        raise RuntimeError(f"Missing required artifacts for {model_id} seed {seed}: {missing}")
    ts = json.loads((run_dir / "training_summary.json").read_text(encoding="utf-8"))
    m = json.loads((run_dir / "metrics_test.json").read_text(encoding="utf-8"))
    ss = json.loads((run_dir / "split_summary.json").read_text(encoding="utf-8"))
    rc = yaml.safe_load((run_dir / "config_resolved.yaml").read_text(encoding="utf-8"))
    if ts.get("split_id") != SPLIT_ID or m.get("split_id") != SPLIT_ID:
        raise RuntimeError(f"Unexpected split id for {model_id} seed {seed}")
    if ss.get("split_source") != "artifact" or rc.get("data", {}).get("split_source") != "artifact":
        raise RuntimeError(f"Run did not use fixed split artifact for {model_id} seed {seed}")
    if ts.get("train_seed") != seed or m.get("train_seed") != seed:
        raise RuntimeError(f"Unexpected train seed for {model_id} seed {seed}")
    return {
        "status": "completed",
        "model_id": model_id,
        "train_seed": seed,
        "split_id": SPLIT_ID,
        "split_source": "artifact",
        "evidence_label": EVIDENCE_LABEL,
        "run_dir": str(run_dir),
        "overall_accuracy": m.get("overall_accuracy"),
        "low_snr_accuracy": m.get("low_snr_accuracy"),
        "mid_snr_accuracy": m.get("mid_snr_accuracy"),
        "high_snr_accuracy": m.get("high_snr_accuracy"),
        "macro_f1": m.get("test", {}).get("macro_f1"),
        "balanced_accuracy": m.get("test", {}).get("balanced_accuracy"),
        "best_epoch": ts.get("best_epoch"),
        "train_time_seconds": ts.get("train_time_seconds"),
        "artifacts": {n: str(run_dir / n) for n in REQUIRED_ARTIFACTS},
    }


def run_single(args: argparse.Namespace) -> int:
    if args.model is None or args.seed is None:
        raise SystemExit("--single requires --model and --seed")
    model_id = args.model
    seed = int(args.seed)
    run_dir = run_dir_for(model_id, seed)
    if is_complete_run(run_dir):
        print(f"SKIP_COMPLETE {model_id} seed={seed} run_dir={run_dir}", flush=True)
        return 0
    if args.resume:
        archive_incomplete(run_dir)
    elif run_dir.exists():
        raise FileExistsError(f"Refusing to overwrite existing incomplete run directory: {run_dir}")

    base_config = load_config(resolve(args.config))
    config = prepare_config(base_config, model_id, seed)

    def create_fixed_run_dir(run_root: str | Path, model_name: str, project_root: str | Path | None = None) -> Path:
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "plots").mkdir(parents=True, exist_ok=True)
        return run_dir

    trainer.create_run_dir = create_fixed_run_dir
    started = time.perf_counter()
    print(f"RUN_START model={model_id} seed={seed} run_dir={run_dir}", flush=True)
    trainer.run_training(config, model_name_override=model_id, project_root=PROJECT_ROOT)
    write_controlled_latency(
        run_dir,
        config=config,
        model_id=model_id,
        device_name=args.latency_device,
        warmup=args.latency_warmup_iters,
        measured=args.latency_measured_iters,
    )
    summary = validate_completed_run(run_dir, model_id, seed)
    summary["wall_time_seconds"] = float(time.perf_counter() - started)
    (run_dir / "cldnn_aug_ablation_run_status.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"RUN_DONE model={model_id} seed={seed} acc={summary['overall_accuracy']} run_dir={run_dir}", flush=True)
    return 0


def build_report(status: dict[str, Any]) -> str:
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for model_id in ALLOWED_MODELS:
        for seed in ALLOWED_SEEDS:
            entry = status.get("runs", {}).get(cell_key(model_id, seed), {})
            if entry.get("status") == "completed":
                rows.append(entry)
            else:
                failures.append({"model_id": model_id, "train_seed": seed, **entry})
    completed = len(rows)
    expected = len(ALLOWED_MODELS) * len(ALLOWED_SEEDS)
    conclusion = "GO" if completed == expected and not failures else "NO-GO"
    lines = [
        "# Paper-Stage 6 CLDNN + Aug + LS Ablation (RTX 3090) Training Report",
        "",
        f"Date: {datetime.now().isoformat(timespec='seconds')}",
        f"Server repo: `{PROJECT_ROOT}`",
        f"Dataset: RadioML2016.10A only",
        f"Split: `{SPLIT_ID}` from `{SPLIT_NPZ}`",
        f"Evidence label: `{EVIDENCE_LABEL}`",
        f"Architecture: CLDNN (I/Q only, no fusion).",
        f"Augmentation (train only): phase rotation theta~U(-pi,pi) prob 0.5; cyclic time shift k~U(-8,+8) prob 0.5.",
        f"Loss: nn.CrossEntropyLoss(label_smoothing=0.1).",
        f"Hardware: RTX 3090 (Ampere sm_86), CUDA 12.8, PyTorch 2.9.1+cu128.",
        f"Conclusion: {conclusion}",
        "",
        "## Purpose",
        "",
        "Isolate whether the accuracy gain from signal-domain augmentation requires",
        "the fusion architecture or transfers equally to the simpler CLDNN baseline.",
        "",
        "## Comparison targets",
        "",
        "| Condition | Evidence label | Aug | LS | Architecture |",
        "|---|---|---|---|---|",
        "| CLDNN baseline (no aug) | EXTENDED_BUDGET_3090 | No | No | CLDNN |",
        "| **This experiment** | CLDNN_AUG_ABLATION_3090 | Yes | Yes | CLDNN |",
        "| Proposed model | FUSION_CLDNN_STFT_AUG_LS_3090 | Yes | Yes | fusion_cldnn_stft |",
        "",
        "## Results",
        "",
        "| Model | Seed | Status | Overall Acc | Low SNR Acc | Mid SNR Acc | High SNR Acc | Best Epoch |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for model_id in ALLOWED_MODELS:
        for seed in ALLOWED_SEEDS:
            entry = status.get("runs", {}).get(cell_key(model_id, seed), {})
            lines.append(
                "| {model} | {seed} | {status} | {overall} | {low} | {mid} | {high} | {best} |".format(
                    model=model_id,
                    seed=seed,
                    status=entry.get("status", "missing"),
                    overall=entry.get("overall_accuracy"),
                    low=entry.get("low_snr_accuracy"),
                    mid=entry.get("mid_snr_accuracy"),
                    high=entry.get("high_snr_accuracy"),
                    best=entry.get("best_epoch"),
                )
            )
    lines.extend(["", "## Failures", ""])
    if failures:
        for failure in failures:
            lines.append(
                f"- {failure.get('model_id')} seed {failure.get('train_seed')}: {failure.get('status', 'missing')} "
                f"{failure.get('error', '')}"
            )
    else:
        lines.append("- None.")
    return "\n".join(lines).rstrip() + "\n"


def orchestrate(args: argparse.Namespace) -> int:
    status = load_status()
    save_status(status)
    for model_id in ALLOWED_MODELS:
        for seed in ALLOWED_SEEDS:
            key = cell_key(model_id, seed)
            run_dir = run_dir_for(model_id, seed)
            if is_complete_run(run_dir):
                status.setdefault("runs", {})[key] = validate_completed_run(run_dir, model_id, seed)
                save_status(status)
                print(f"ORCH_SKIP_COMPLETE {key}", flush=True)
                continue
            cmd = [
                sys.executable,
                str(Path(__file__).resolve()),
                "--single",
                "--config", args.config,
                "--model", model_id,
                "--seed", str(seed),
                "--latency-device", args.latency_device,
                "--latency-warmup-iters", str(args.latency_warmup_iters),
                "--latency-measured-iters", str(args.latency_measured_iters),
            ]
            if args.resume:
                cmd.append("--resume")
            status.setdefault("runs", {})[key] = {
                "status": "running",
                "model_id": model_id,
                "train_seed": seed,
                "run_dir": str(run_dir),
                "started_at": datetime.now().isoformat(timespec="seconds"),
            }
            save_status(status)
            print(f"ORCH_RUN {key}", flush=True)
            result = subprocess.run(cmd, cwd=PROJECT_ROOT, text=True)
            if result.returncode != 0:
                status["runs"][key] = {
                    "status": "failed",
                    "model_id": model_id,
                    "train_seed": seed,
                    "run_dir": str(run_dir),
                    "returncode": result.returncode,
                    "failed_at": datetime.now().isoformat(timespec="seconds"),
                }
                save_status(status)
                REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
                REPORT_PATH.write_text(build_report(status), encoding="utf-8")
                return result.returncode
            status["runs"][key] = validate_completed_run(run_dir, model_id, seed)
            status["runs"][key]["completed_at"] = datetime.now().isoformat(timespec="seconds")
            save_status(status)
            REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
            REPORT_PATH.write_text(build_report(status), encoding="utf-8")
    status["completed_at"] = datetime.now().isoformat(timespec="seconds")
    save_status(status)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(status), encoding="utf-8")
    print(f"REPORT {REPORT_PATH}", flush=True)
    return 0


def main() -> int:
    args = parse_args()
    if args.single:
        return run_single(args)
    return orchestrate(args)


if __name__ == "__main__":
    raise SystemExit(main())
