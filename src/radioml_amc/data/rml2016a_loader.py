from __future__ import annotations

import bz2
import pickle
from pathlib import Path
from typing import Any

import numpy as np

from radioml_amc.paths import resolve_project_path


class RadioML2016AMissingError(FileNotFoundError):
    """Raised when RadioML2016.10A is not present locally."""


DEFAULT_RML2016A_CANDIDATES = (
    "data/raw/RML2016.10a_dict.pkl",
    "data/raw/RML2016.10a_dict.pkl.bz2",
    "data/raw/radioml2016/RML2016.10a_dict.pkl",
    "data/raw/radioml2016/RML2016.10a_dict.pkl.bz2",
)


def _normalize_mod_name(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _load_pickle(path: Path) -> dict[Any, Any]:
    opener = bz2.BZ2File if path.suffix == ".bz2" else open
    with opener(path, "rb") as f:
        return pickle.load(f, encoding="latin1")


def _candidate_paths(
    raw_path: str | Path | None = "auto",
    raw_bz2_path: str | Path | None = None,
    project_root: str | Path | None = None,
) -> list[Path]:
    candidates: list[str | Path] = []
    raw_path_text = str(raw_path) if raw_path is not None else "auto"
    if raw_path_text.lower() == "auto":
        candidates.extend(DEFAULT_RML2016A_CANDIDATES)
    else:
        candidates.append(raw_path_text)

    if raw_bz2_path:
        candidates.append(raw_bz2_path)

    resolved: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        path = resolve_project_path(candidate, project_root)
        key = str(path.resolve()) if path.exists() else str(path)
        if key not in seen:
            resolved.append(path)
            seen.add(key)
    return resolved


def find_rml2016a_file(
    raw_path: str | Path | None = "auto",
    raw_bz2_path: str | Path | None = None,
    project_root: str | Path | None = None,
) -> Path:
    candidates = _candidate_paths(raw_path, raw_bz2_path, project_root)
    for path in candidates:
        if path.exists():
            return path

    candidate_lines = "\n".join(f"  - {path}" for path in candidates)
    raise RadioML2016AMissingError(
        "RadioML2016.10A 文件不存在。请手动放置到以下任一路径，或在 config 中显式设置 data.raw_path：\n"
        f"{candidate_lines}\n"
        "本项目不会自动下载大数据集。"
    )


def load_rml2016a(
    raw_path: str | Path | None = "auto",
    raw_bz2_path: str | Path | None = None,
    project_root: str | Path | None = None,
    subset_mode: bool = False,
    subset_mods: list[str] | None = None,
    subset_snrs: list[int] | None = None,
    max_samples_per_group: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str], list[int], dict[str, Any]]:
    path = find_rml2016a_file(raw_path, raw_bz2_path, project_root)
    raw = _load_pickle(path)
    if not isinstance(raw, dict):
        raise ValueError(f"Expected RadioML2016.10A dict, got {type(raw)!r}")

    subset_mod_set = set(subset_mods or [])
    subset_snr_set = {int(v) for v in (subset_snrs or [])}

    normalized_items: list[tuple[str, int, np.ndarray]] = []
    for key, value in raw.items():
        if not isinstance(key, tuple) or len(key) != 2:
            continue
        mod_name = _normalize_mod_name(key[0])
        snr_value = int(key[1])
        if subset_mode and subset_mod_set and mod_name not in subset_mod_set:
            continue
        if subset_mode and subset_snr_set and snr_value not in subset_snr_set:
            continue

        arr = np.asarray(value, dtype=np.float32)
        if arr.ndim != 3 or arr.shape[1] != 2:
            raise ValueError(f"Unexpected sample shape for key {key!r}: {arr.shape}")
        if arr.shape[2] != 128:
            raise ValueError(f"RadioML2016.10A stage 1 expects length 128, got {arr.shape[2]}")
        if subset_mode and max_samples_per_group is not None:
            arr = arr[: int(max_samples_per_group)]
        normalized_items.append((mod_name, snr_value, arr))

    if not normalized_items:
        raise ValueError("No samples matched the requested RadioML2016.10A subset filters.")

    mod_names = sorted({item[0] for item in normalized_items})
    snr_values = sorted({item[1] for item in normalized_items})
    mod_to_idx = {name: idx for idx, name in enumerate(mod_names)}

    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    snrs: list[np.ndarray] = []
    group_counts: dict[str, int] = {}

    for mod_name, snr_value, arr in normalized_items:
        xs.append(arr.astype(np.float32, copy=False))
        ys.append(np.full((arr.shape[0],), mod_to_idx[mod_name], dtype=np.int64))
        snrs.append(np.full((arr.shape[0],), snr_value, dtype=np.int64))
        group_counts[f"{mod_name}@{snr_value}"] = int(arr.shape[0])

    x = np.concatenate(xs, axis=0).astype(np.float32, copy=False)
    y = np.concatenate(ys, axis=0)
    snr = np.concatenate(snrs, axis=0)
    class_counts = {
        mod_name: int(sum(count for key, count in group_counts.items() if key.startswith(f"{mod_name}@")))
        for mod_name in mod_names
    }
    snr_counts = {
        str(snr_value): int(sum(count for key, count in group_counts.items() if key.endswith(f"@{snr_value}")))
        for snr_value in snr_values
    }

    metadata = {
        "source_path": str(path),
        "candidate_paths": [str(p) for p in _candidate_paths(raw_path, raw_bz2_path, project_root)],
        "subset_mode": bool(subset_mode),
        "subset_mods": list(subset_mods) if subset_mods is not None else None,
        "subset_snrs": [int(v) for v in subset_snrs] if subset_snrs is not None else None,
        "max_samples_per_group": int(max_samples_per_group) if max_samples_per_group is not None else None,
        "group_counts": group_counts,
        "class_counts": class_counts,
        "snr_counts": snr_counts,
        "num_samples": int(x.shape[0]),
        "num_classes": int(len(mod_names)),
        "num_snrs": int(len(snr_values)),
        "x_shape": list(x.shape),
        "x_dtype": str(x.dtype),
        "has_nan": bool(np.isnan(x).any()),
        "has_inf": bool(np.isinf(x).any()),
    }
    return x, y, snr, mod_names, snr_values, metadata
