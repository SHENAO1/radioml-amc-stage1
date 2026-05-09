from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.data.dataset import load_data_bundle
from radioml_amc.data.rml2016a_loader import RadioML2016AMissingError
from radioml_amc.data.split import create_split_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a fixed Paper-Stage split artifact.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--output-dir", default="data/splits/rml2016a", help="Output directory for NPZ and summary JSON.")
    parser.add_argument("--dataset", default="rml2016a", help="Dataset id written to summary metadata.")
    parser.add_argument("--strategy", default="stratified_by_mod_snr", help="Split strategy.")
    parser.add_argument("--seed", type=int, default=42, help="Split seed.")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio.")
    parser.add_argument("--val-size", type=float, default=0.1, help="Validation split ratio.")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def main() -> int:
    args = parse_args()
    config = load_config(_resolve(args.config))
    try:
        bundle = load_data_bundle(config, project_root=str(PROJECT_ROOT))
    except RadioML2016AMissingError as exc:
        print(str(exc))
        return 0

    _, npz_path, summary_path = create_split_artifact(
        y=bundle.y,
        snr=bundle.snr,
        class_names=bundle.mod_names,
        output_dir=_resolve(args.output_dir),
        test_size=args.test_size,
        val_size=args.val_size,
        strategy=args.strategy,
        seed=args.seed,
        dataset_name=args.dataset,
        metadata=bundle.metadata,
    )
    print(f"Split artifact: {npz_path}")
    print(f"Split summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
