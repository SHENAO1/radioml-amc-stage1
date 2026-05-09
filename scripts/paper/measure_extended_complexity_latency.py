"""P1.2: extended complexity / latency table.

Fills the gaps in the Stage 5A controlled-latency evidence:
  - FLOPs and MACs for each of the 9 Stage 5A model rows (via `thop`).
  - CPU forward-pass latency (warmup 50, measured 200, batch sizes 1 and 256)
    using `torch.utils.benchmark.Timer`.

Stage 5A `complexity_latency_table.csv` already contains parameter counts and
controlled CUDA forward times. This script writes a *new* file
`extended_complexity_latency.csv` (and a markdown digest) so the original
Stage 5A artifact is not modified.

Outputs go to `results/paper_stage6/extended_complexity_latency/`.
"""
from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path
from typing import Any

import torch
import torch.utils.benchmark as bench
from thop import profile

REPO_ROOT = Path(__file__).resolve().parents[2]

import sys
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from radioml_amc.training.trainer import (  # noqa: E402
    build_model,
    feature_config_for_model,
    model_required_views,
)


MODELS = [
    "cnn1d",
    "resnet1d",
    "tfcnn_stft",
    "fusion_iq_stft",
    "cldnn",
    "mcldnn",
    "lwamcnet",
    "iq_param_matched",
    "gated_fusion_iq_stft",
]
NUM_CLASSES = 11
SIGNAL_LENGTH = 128
BATCH_SIZES = [1, 256]
WARMUP_ITERS = 50
MEASURED_ITERS = 200
DEFAULT_OUTPUT = REPO_ROOT / "results" / "paper_stage6" / "extended_complexity_latency"


def synthetic_input(views: list[str], batch_size: int) -> torch.Tensor | dict[str, torch.Tensor]:
    if views == ["iq"]:
        return torch.randn(batch_size, 2, SIGNAL_LENGTH)
    data: dict[str, torch.Tensor] = {}
    for v in views:
        if v in {"iq", "amp_phase"}:
            data[v] = torch.randn(batch_size, 2, SIGNAL_LENGTH)
        elif v == "stft":
            data[v] = torch.randn(batch_size, 1, 32, 7)
        elif v == "cwt":
            data[v] = torch.randn(batch_size, 1, 16, SIGNAL_LENGTH)
        else:
            raise ValueError(f"unsupported view: {v}")
    return data


def count_params(model: torch.nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def flops_macs_for(model_id: str) -> tuple[int, int]:
    """Run thop with a single sample. Returns (macs, params_from_thop)."""
    cfg = {"features": {"views": model_required_views(model_id)}}
    fc = feature_config_for_model(cfg, model_id)
    model = build_model(model_id, num_classes=NUM_CLASSES, feature_config=fc).eval()
    inp = synthetic_input(fc["views"], 1)
    if isinstance(inp, dict):
        macs, _ = profile(model, inputs=(inp,), verbose=False)
    else:
        macs, _ = profile(model, inputs=(inp,), verbose=False)
    return int(macs), count_params(model)


def cpu_forward_time(model_id: str, batch_size: int) -> dict[str, float]:
    """torch.utils.benchmark Timer with controlled warmup + measured iterations."""
    cfg = {"features": {"views": model_required_views(model_id)}}
    fc = feature_config_for_model(cfg, model_id)
    model = build_model(model_id, num_classes=NUM_CLASSES, feature_config=fc).eval()
    inp = synthetic_input(fc["views"], batch_size)

    # Warmup outside Timer for predictability.
    with torch.no_grad():
        for _ in range(WARMUP_ITERS):
            _ = model(inp)

    if isinstance(inp, dict):
        # Wrap the dict in a closure for benchmark.
        timer = bench.Timer(
            stmt="model(inp)",
            globals={"model": model, "inp": inp, "torch": torch},
            num_threads=1,
        )
    else:
        timer = bench.Timer(
            stmt="model(inp)",
            globals={"model": model, "inp": inp, "torch": torch},
            num_threads=1,
        )
    measurement = timer.timeit(MEASURED_ITERS)
    median_ms = measurement.median * 1000.0
    iqr_ms = measurement.iqr * 1000.0
    return {"median_ms": float(median_ms), "iqr_ms": float(iqr_ms)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device", default="cpu", choices=["cpu"], help="Force CPU; this script is for CPU latency only.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    if args.device != "cpu":
        raise SystemExit("This script measures CPU latency only.")
    torch.set_num_threads(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    started = time.time()
    for model_id in MODELS:
        print(f"  -> {model_id}: FLOPs ...", flush=True)
        macs, params = flops_macs_for(model_id)
        flops = macs * 2  # MAC -> FLOP convention used by thop docs
        cpu_times: dict[int, dict[str, float]] = {}
        for bs in BATCH_SIZES:
            print(f"     CPU latency batch={bs} ...", flush=True)
            cpu_times[bs] = cpu_forward_time(model_id, bs)
        rows.append({
            "model_id": model_id,
            "trainable_params": params,
            "macs_single_sample": macs,
            "flops_single_sample": flops,
            "cpu_forward_ms_bs1_median": cpu_times[1]["median_ms"],
            "cpu_forward_ms_bs1_iqr": cpu_times[1]["iqr_ms"],
            "cpu_forward_ms_bs256_median": cpu_times[256]["median_ms"],
            "cpu_forward_ms_bs256_iqr": cpu_times[256]["iqr_ms"],
        })
        print(f"     macs={macs:,}  bs1={cpu_times[1]['median_ms']:.3f} ms  bs256={cpu_times[256]['median_ms']:.3f} ms", flush=True)

    elapsed = time.time() - started

    # Persist CSV.
    import csv
    csv_path = output_dir / "extended_complexity_latency.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Persist JSON with metadata.
    meta = {
        "evidence_label": "CONTROLLED_LATENCY_EXTENDED",
        "host": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_built": torch.version.cuda,
        "thop": __import__("thop").__version__ if hasattr(__import__("thop"), "__version__") else "unknown",
        "device": "cpu",
        "warmup_iters": WARMUP_ITERS,
        "measured_iters": MEASURED_ITERS,
        "batch_sizes": BATCH_SIZES,
        "signal_length": SIGNAL_LENGTH,
        "num_threads": 1,
        "wall_time_seconds": elapsed,
        "rows": rows,
    }
    (output_dir / "extended_complexity_latency.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown digest.
    md = ["# Extended Complexity / Latency",
          "",
          f"Host: `{platform.node()}` ({platform.platform()})",
          f"PyTorch: `{torch.__version__}` (CUDA built: `{torch.version.cuda}`); thop: `{meta['thop']}`",
          f"Device: CPU; torch num_threads = 1; warmup = {WARMUP_ITERS}, measured = {MEASURED_ITERS}.",
          f"Evidence label: `CONTROLLED_LATENCY_EXTENDED`. This is a separate file from Stage 5A `complexity_latency_table.csv`; that file is not modified.",
          "",
          "| model | params | MACs (1 sample) | FLOPs (~2x MACs) | CPU bs=1 ms (median, IQR) | CPU bs=256 ms (median, IQR) |",
          "|---|---:|---:|---:|---:|---:|"]
    for row in rows:
        md.append(
            f"| {row['model_id']} | {row['trainable_params']:,} | {row['macs_single_sample']:,} | {row['flops_single_sample']:,} | "
            f"{row['cpu_forward_ms_bs1_median']:.3f} (IQR {row['cpu_forward_ms_bs1_iqr']:.3f}) | "
            f"{row['cpu_forward_ms_bs256_median']:.3f} (IQR {row['cpu_forward_ms_bs256_iqr']:.3f}) |"
        )
    (output_dir / "extended_complexity_latency.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\ndone in {elapsed:.1f}s. wrote:")
    for f in sorted(output_dir.iterdir()):
        print(f"  {f.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
