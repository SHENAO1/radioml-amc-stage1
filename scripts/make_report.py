from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.reporting import make_stage1_5_report, make_stage1_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate stage1_report.md from a run directory.")
    parser.add_argument("--run_dir", required=True, help="Run directory under runs/ or absolute path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = PROJECT_ROOT / run_dir
    report = make_stage1_report(run_dir)
    stage1_5_report = make_stage1_5_report(run_dir)
    print(f"Report written: {report}")
    print(f"Stage 1.5 report written: {stage1_5_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
