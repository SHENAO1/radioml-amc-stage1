from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _bootstrap import PROJECT_ROOT

from radioml_amc.config import load_config
from radioml_amc.training.trainer import build_model, feature_config_for_model, get_device, model_required_views
from radioml_amc.profiling import measure_latency, summarize_model_complexity


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure model complexity and latency on synthetic inputs.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--model", help="Model id. Defaults to train.model from config.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--device", default="cpu", help="Measurement device, e.g. cpu, cuda, auto.")
    parser.add_argument("--batch-size", type=int, default=1, help="Synthetic batch size.")
    parser.add_argument("--signal-length", type=int, default=128, help="I/Q signal length.")
    parser.add_argument("--num-classes", type=int, default=11, help="Number of classes for synthetic model construction.")
    parser.add_argument("--warmup-iters", type=int, default=10, help="Warmup iterations.")
    parser.add_argument("--measured-iters", type=int, default=25, help="Measured iterations.")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def _synthetic_input(views: list[str], batch_size: int, signal_length: int) -> torch.Tensor | dict[str, torch.Tensor]:
    if views == ["iq"]:
        return torch.randn(batch_size, 2, signal_length)
    data: dict[str, torch.Tensor] = {}
    for view in views:
        if view in {"iq", "amp_phase"}:
            data[view] = torch.randn(batch_size, 2, signal_length)
        elif view == "stft":
            data[view] = torch.randn(batch_size, 1, 32, 7)
        elif view == "cwt":
            data[view] = torch.randn(batch_size, 1, 16, signal_length)
        else:
            raise ValueError(f"Unsupported synthetic view: {view}")
    return data


def main() -> int:
    args = parse_args()
    config = load_config(_resolve(args.config))
    model_id = args.model or str(config.get("train", {}).get("model", "cnn1d"))
    config.setdefault("features", {})["views"] = model_required_views(model_id)
    feature_config = feature_config_for_model(config, model_id)
    sample_input = _synthetic_input(feature_config["views"], args.batch_size, args.signal_length)
    model = build_model(model_id, num_classes=args.num_classes, feature_config=feature_config)
    device = get_device(args.device)
    complexity = summarize_model_complexity(
        model,
        sample_input,
        model_id=model_id,
        dataset=str(config.get("data", {}).get("dataset", "unknown")),
        feature_preprocess={
            "uses_stft": "stft" in feature_config["views"],
            "uses_cwt": "cwt" in feature_config["views"],
            "cached": False,
        },
    )
    latency = measure_latency(
        model,
        sample_input,
        model_id=model_id,
        device=device,
        warmup_iters=args.warmup_iters,
        measured_iters=args.measured_iters,
    )
    payload = {"complexity": complexity, "latency": latency}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output = _resolve(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Wrote complexity/latency report: {output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
