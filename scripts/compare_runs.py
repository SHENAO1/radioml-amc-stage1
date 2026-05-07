from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.reporting.compare_runs import collect_run_metrics, write_comparison


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare multiple RadioML run directories.")
    parser.add_argument("--run_dirs", nargs="+", required=True, help="Run directories to compare.")
    parser.add_argument("--output", required=True, help="Output directory for CSV and Markdown tables.")
    return parser.parse_args()


def _resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def main() -> int:
    args = parse_args()
    rows = [collect_run_metrics(_resolve(run_dir)) for run_dir in args.run_dirs]
    output_dir = _resolve(args.output)
    csv_path, md_path = write_comparison(rows, output_dir)

    print(f"Comparison CSV: {csv_path}")
    print(f"Comparison Markdown: {md_path}")
    print()
    print("| Model | Overall Acc | Low SNR | Mid SNR | High SNR | Params | Run Dir |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for row in rows:
        print(
            f"| {row['model']} | {row['overall_accuracy']} | {row['low_snr_accuracy']} | "
            f"{row['mid_snr_accuracy']} | {row['high_snr_accuracy']} | {row['num_parameters']} | {row['run_dir']} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
