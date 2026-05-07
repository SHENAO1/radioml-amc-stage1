from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError
from radioml_amc.training import evaluate_checkpoint


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a saved baseline checkpoint.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--checkpoint", required=True, help="Path to best_model.pt.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    config = load_config(config_path)
    try:
        run_dir = evaluate_checkpoint(config, args.checkpoint, project_root=PROJECT_ROOT)
    except RadioML2016AMissingError as exc:
        print(str(exc))
        return 0
    print(f"Evaluation finished. Run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

