from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config, save_config
from radioml_amc.data.dataset import load_data_bundle, summarize_data_bundle
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError
from radioml_amc.paths import create_run_dir
from radioml_amc.visualization.plot_signals import save_signal_example_plots


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visualize I/Q examples, constellation, amplitude/phase and STFT.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--num_examples", type=int, default=4, help="Number of examples to draw.")
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

    run_dir = create_run_dir(config.get("outputs", {}).get("run_root", "runs"), "visualize_examples", PROJECT_ROOT)
    save_config(config, run_dir / "config.yaml")
    mapping = {
        "mode": bundle.mode,
        "mod_names": bundle.mod_names,
        "class_to_idx": {name: idx for idx, name in enumerate(bundle.mod_names)},
        "snr_values": [int(v) for v in bundle.snr_values],
    }
    (run_dir / "label_mapping.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(summarize_data_bundle(bundle), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    saved = save_signal_example_plots(
        bundle,
        run_dir / "plots",
        stft_config=config.get("stft", {}),
        num_examples=args.num_examples,
        seed=int(config.get("project", {}).get("seed", 42)),
    )
    print(f"Saved visualization run: {run_dir}")
    for name, path in saved.items():
        print(f"- {name}: {path}")
    if bundle.mode == "mock":
        print("提示：当前图片来自 mock/synthetic 数据，只用于工程 smoke test。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
