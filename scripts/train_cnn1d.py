from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError
from radioml_amc.training import run_training


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train CNN1D baseline.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    config = load_config(config_path)
    try:
        run_dir = run_training(config, model_name_override="cnn1d", project_root=PROJECT_ROOT)
    except RadioML2016AMissingError as exc:
        print(str(exc))
        return 0
    print(f"Training finished. Run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

