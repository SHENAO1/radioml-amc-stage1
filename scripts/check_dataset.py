from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.data.dataset import load_data_bundle, summarize_data_bundle
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check RadioML dataset configuration and statistics.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path
    config = load_config(config_path)
    try:
        bundle = load_data_bundle(config, project_root=PROJECT_ROOT)
    except RadioML2016AMissingError as exc:
        print(str(exc))
        return 0

    summary = summarize_data_bundle(bundle)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if bundle.mode == "mock":
        print("\n提示：当前为 mock/synthetic 数据，只用于工程 smoke test，不能作为正式实验结果。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

