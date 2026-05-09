from __future__ import annotations

import platform
import statistics
import time
from collections.abc import Callable, Mapping
from typing import Any

import torch
from torch import nn


TensorInput = torch.Tensor | Mapping[str, torch.Tensor]


def _move_to_device(value: TensorInput, device: torch.device) -> TensorInput:
    if torch.is_tensor(value):
        return value.to(device)
    return {key: tensor.to(device) for key, tensor in value.items()}


def _input_shapes(sample_input: TensorInput) -> dict[str, list[int]]:
    if torch.is_tensor(sample_input):
        return {"iq": list(sample_input.shape)}
    return {key: list(value.shape) for key, value in sample_input.items()}


def summarize_model_complexity(
    model: nn.Module,
    sample_input: TensorInput,
    model_id: str,
    dataset: str | None = None,
    feature_preprocess: dict[str, Any] | None = None,
) -> dict[str, Any]:
    params_total = sum(p.numel() for p in model.parameters())
    params_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {
        "dataset": dataset,
        "model_id": model_id,
        "input_shapes": _input_shapes(sample_input),
        "params_trainable": int(params_trainable),
        "params_total": int(params_total),
        "macs": None,
        "flops": None,
        "feature_preprocess": dict(feature_preprocess or {}),
        "software": {
            "python": platform.python_version(),
            "pytorch": torch.__version__,
            "cuda": torch.version.cuda,
        },
        "hardware": {
            "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cpu": platform.processor(),
            "platform": platform.platform(),
        },
    }


def _sync(device: torch.device) -> None:
    if device.type == "cuda":
        torch.cuda.synchronize(device)


def _latency_stats(values_ms: list[float]) -> dict[str, float | None]:
    if not values_ms:
        return {"mean": None, "median": None, "p95": None, "std": None}
    ordered = sorted(values_ms)
    p95_index = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
    return {
        "mean": float(statistics.fmean(values_ms)),
        "median": float(statistics.median(values_ms)),
        "p95": float(ordered[p95_index]),
        "std": float(statistics.pstdev(values_ms)) if len(values_ms) > 1 else 0.0,
    }


def _empty_latency_stats() -> dict[str, float | None]:
    return {"mean": None, "median": None, "p95": None, "std": None}


def empty_latency_report(
    model_id: str,
    batch_sizes: list[int] | None = None,
    warmup_iters: int = 0,
    measured_iters: int = 0,
    peak_inference_memory_mb: float | None = None,
    status: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    batch_sizes = list(batch_sizes or [1, 256])
    empty_batches = {f"batch_{int(batch)}": _empty_latency_stats() for batch in batch_sizes}
    payload: dict[str, Any] = {
        "model_id": model_id,
        "batch_sizes": batch_sizes,
        "warmup_iters": int(warmup_iters),
        "measured_iters": int(measured_iters),
        "gpu_forward_excluding_preprocess_ms": dict(empty_batches),
        "gpu_including_preprocess_ms": dict(empty_batches),
        "cpu_including_preprocess_ms": dict(empty_batches),
        "stft_preprocess_ms": dict(empty_batches),
        "peak_inference_memory_mb": peak_inference_memory_mb,
    }
    if status is not None:
        payload["status"] = status
    if note is not None:
        payload["note"] = note
    return payload


def measure_latency(
    model: nn.Module,
    sample_input: TensorInput,
    model_id: str,
    device: str | torch.device = "cpu",
    warmup_iters: int = 10,
    measured_iters: int = 25,
    preprocess_fn: Callable[[], TensorInput] | None = None,
) -> dict[str, Any]:
    target_device = torch.device(device)
    model = model.to(target_device)
    model.eval()
    prepared_input = _move_to_device(sample_input, target_device)

    if target_device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(target_device)

    with torch.no_grad():
        for _ in range(int(warmup_iters)):
            if preprocess_fn is None:
                batch = prepared_input
            else:
                batch = _move_to_device(preprocess_fn(), target_device)
            _ = model(batch)
        _sync(target_device)

        forward_ms: list[float] = []
        full_ms: list[float] = []
        preprocess_ms: list[float] = []
        for _ in range(int(measured_iters)):
            if preprocess_fn is None:
                _sync(target_device)
                start = time.perf_counter()
                _ = model(prepared_input)
                _sync(target_device)
                elapsed = (time.perf_counter() - start) * 1000.0
                forward_ms.append(elapsed)
                full_ms.append(elapsed)
            else:
                pre_start = time.perf_counter()
                batch = preprocess_fn()
                pre_elapsed = (time.perf_counter() - pre_start) * 1000.0
                preprocess_ms.append(pre_elapsed)
                batch = _move_to_device(batch, target_device)
                _sync(target_device)
                start = time.perf_counter()
                _ = model(batch)
                _sync(target_device)
                forward_elapsed = (time.perf_counter() - start) * 1000.0
                forward_ms.append(forward_elapsed)
                full_ms.append(pre_elapsed + forward_elapsed)

    peak_memory_mb = None
    if target_device.type == "cuda":
        peak_memory_mb = float(torch.cuda.max_memory_allocated(target_device) / (1024**2))

    batch_size = None
    first_tensor = prepared_input if torch.is_tensor(prepared_input) else next(iter(prepared_input.values()))
    if torch.is_tensor(first_tensor) and first_tensor.ndim > 0:
        batch_size = int(first_tensor.shape[0])

    batch_key = f"batch_{batch_size}" if batch_size is not None else "batch_unknown"
    forward_stats = _latency_stats(forward_ms)
    full_stats = _latency_stats(full_ms)
    pre_stats = _latency_stats(preprocess_ms)
    null_stats = _empty_latency_stats()

    return {
        "model_id": model_id,
        "device": str(target_device),
        "batch_size": batch_size,
        "batch_sizes": [batch_size] if batch_size is not None else [],
        "warmup_iters": int(warmup_iters),
        "measured_iters": int(measured_iters),
        "gpu_forward_excluding_preprocess_ms": {
            batch_key: forward_stats if target_device.type == "cuda" else null_stats,
        },
        "gpu_including_preprocess_ms": {
            batch_key: full_stats if target_device.type == "cuda" else null_stats,
        },
        "cpu_including_preprocess_ms": {
            batch_key: full_stats if target_device.type == "cpu" else null_stats,
        },
        "stft_preprocess_ms": {batch_key: pre_stats},
        "peak_inference_memory_mb": peak_memory_mb,
        "forward_excluding_preprocess_ms": forward_stats,
        "including_preprocess_ms": full_stats,
        "preprocess_ms": pre_stats,
    }
