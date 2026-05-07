from __future__ import annotations

import argparse
import copy
from datetime import datetime
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError
from radioml_amc.reporting.compare_runs import collect_run_metrics, write_comparison
from radioml_amc.training import run_training


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage 1.5 CNN1D and ResNet1D baselines.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def main() -> int:
    args = parse_args()
    config = load_config(_resolve(args.config))
    run_dirs: list[Path] = []

    for model_name in ("cnn1d", "resnet1d"):
        model_config = copy.deepcopy(config)
        model_config.setdefault("train", {})["model"] = model_name
        try:
            run_dir = run_training(model_config, model_name_override=model_name, project_root=PROJECT_ROOT)
        except RadioML2016AMissingError as exc:
            print(str(exc))
            print("真实数据缺失，Stage 1.5 baseline 批量训练未执行。")
            return 0
        run_dirs.append(run_dir)
        print(f"{model_name} finished: {run_dir}")

    rows = [collect_run_metrics(run_dir) for run_dir in run_dirs]
    output_dir = PROJECT_ROOT / "runs" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_stage1_5_comparison"
    csv_path, md_path = write_comparison(rows, output_dir)

    print(f"Baseline comparison CSV: {csv_path}")
    print(f"Baseline comparison Markdown: {md_path}")
    print()
    print("| Model | Overall Acc | Low SNR | Mid SNR | High SNR | Params | Run Dir |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for row in rows:
        print(
            f"| {row['model']} | {row['overall_accuracy']} | {row['low_snr_accuracy']} | "
            f"{row['mid_snr_accuracy']} | {row['high_snr_accuracy']} | {row['num_parameters']} | {row['run_dir']} |"
        )
    print()
    print("如需固化到 docs/EXPERIMENT_LOG.md，请记录上表的关键摘要和 run_dir。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
