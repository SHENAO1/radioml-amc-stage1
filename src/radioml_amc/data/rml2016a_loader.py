from __future__ import annotations

import bz2
import pickle
from pathlib import Path
from typing import Any

import numpy as np

from radioml_amc.paths import resolve_project_path


class RadioML2016AMissingError(FileNotFoundError):
    """Raised when RadioML2016.10A is not present locally."""


def _normalize_mod_name(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _load_pickle(path: Path) -> dict[Any, Any]:
    opener = bz2.BZ2File if path.suffix == ".bz2" else open
    with opener(path, "rb") as f:
        return pickle.load(f, encoding="latin1")


def find_rml2016a_file(
    raw_path: str | Path,
    raw_bz2_path: str | Path,
    project_root: str | Path | None = None,
) -> Path:
    pkl_path = resolve_project_path(raw_path, project_root)
    bz2_path = resolve_project_path(raw_bz2_path, project_root)
    if pkl_path.exists():
        return pkl_path
    if bz2_path.exists():
        return bz2_path
    raise RadioML2016AMissingError(
        "RadioML2016.10A 文件不存在。请手动放置到以下任一路径：\n"
        f"  - {pkl_path}\n"
        f"  - {bz2_path}\n"
        "本项目不会自动下载大数据集。"
    )


def load_rml2016a(
    raw_path: str | Path,
    raw_bz2_path: str | Path,
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

    metadata = {
        "source_path": str(path),
        "subset_mode": bool(subset_mode),
        "group_counts": group_counts,
    }
    return x, y, snr, mod_names, snr_values, metadata

