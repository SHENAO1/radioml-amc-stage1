from __future__ import annotations

import argparse
import copy
import json
from datetime import datetime
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError
from radioml_amc.reporting.compare_runs import collect_run_metrics, write_comparison
from radioml_amc.training import run_training
from radioml_amc.training.trainer import model_required_views


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage 2 time-frequency and multiview ablations.")
    parser.add_argument("--config", required=True, help="Path to a Stage 2 YAML config.")
    parser.add_argument("--models", nargs="*", help="Optional model list overriding ablation.models.")
    parser.add_argument("--output", help="Optional comparison output directory.")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def _models_from_config(config: dict) -> list[str]:
    models = config.get("ablation", {}).get("models")
    if not models:
        models = [config.get("train", {}).get("model", "fusion_iq_stft")]
    return [str(model) for model in models]


def _configure_model(base_config: dict, model_name: str) -> dict:
    config = copy.deepcopy(base_config)
    config.setdefault("train", {})["model"] = model_name
    features = dict(config.get("features", {}))
    features["views"] = model_required_views(model_name)
    config["features"] = features
    return config


def main() -> int:
    args = parse_args()
    config_path = _resolve(args.config)
    config = load_config(config_path)
    model_names = [str(model) for model in args.models] if args.models else _models_from_config(config)
    run_dirs: list[Path] = []

    for model_name in model_names:
        model_config = _configure_model(config, model_name)
        try:
            run_dir = run_training(model_config, model_name_override=model_name, project_root=PROJECT_ROOT)
        except RadioML2016AMissingError as exc:
            print(str(exc))
            print("真实数据缺失，Stage 2 ablation 未执行。")
            return 0
        run_dirs.append(run_dir)
        print(f"{model_name} finished: {run_dir}")

    rows = [collect_run_metrics(run_dir) for run_dir in run_dirs]
    if args.output:
        output_dir = _resolve(args.output)
    else:
        configured_output = config.get("ablation", {}).get("output_dir")
        if configured_output:
            output_dir = _resolve(configured_output)
        else:
            output_dir = PROJECT_ROOT / "runs" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_stage2_ablation_comparison"

    csv_path, md_path = write_comparison(rows, output_dir)
    manifest = {
        "stage": "Stage 2",
        "config": str(config_path),
        "models": model_names,
        "run_dirs": [str(path) for path in run_dirs],
        "comparison_csv": str(csv_path),
        "comparison_markdown": str(md_path),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "stage2_ablation_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Stage 2 comparison CSV: {csv_path}")
    print(f"Stage 2 comparison Markdown: {md_path}")
    print()
    print("| Model | Overall Acc | Low SNR | Mid SNR | High SNR | Params | Run Dir |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for row in rows:
        print(
            f"| {row['model']} | {row['overall_accuracy']} | {row['low_snr_accuracy']} | "
            f"{row['mid_snr_accuracy']} | {row['high_snr_accuracy']} | {row['num_parameters']} | {row['run_dir']} |"
        )
    print()
    print("提醒：mock ablation 只验证工程链路；真实结果请记录到 docs/EXPERIMENT_LOG.md。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
