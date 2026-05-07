from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset

from radioml_amc.data.mock_dataset import generate_mock_radioml
from radioml_amc.data.rml2016a_loader import load_rml2016a
from radioml_amc.features.time_frequency import compute_amplitude_phase_tensor, compute_cwt_tensor, compute_stft_tensor


@dataclass
class DataBundle:
    x: np.ndarray
    y: np.ndarray
    snr: np.ndarray
    mod_names: list[str]
    snr_values: list[int]
    mode: str
    metadata: dict[str, Any] = field(default_factory=dict)


VIEW_ORDER = ("iq", "amp_phase", "stft", "cwt")


def normalize_feature_config(feature_config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = dict(feature_config or {})
    raw_views = config.get("views", ["iq"])
    if raw_views is None:
        raw_views = ["iq"]
    if isinstance(raw_views, str):
        raw_views = [part.strip() for part in raw_views.split(",")]

    views: list[str] = []
    for value in raw_views:
        view = str(value).strip().lower()
        if not view:
            continue
        if view not in VIEW_ORDER:
            raise ValueError(f"Unsupported feature view: {view}")
        if view not in views:
            views.append(view)
    if not views:
        views = ["iq"]

    return {
        "views": views,
        "amp_phase": dict(config.get("amp_phase", {})),
        "stft": dict(config.get("stft", {})),
        "cwt": dict(config.get("cwt", {})),
    }


class SignalDataset(Dataset):
    def __init__(
        self,
        x: np.ndarray,
        y: np.ndarray,
        snr: np.ndarray,
        feature_config: dict[str, Any] | None = None,
    ):
        self.x = torch.as_tensor(x, dtype=torch.float32)
        self.y = torch.as_tensor(y, dtype=torch.long)
        self.snr = torch.as_tensor(snr, dtype=torch.long)
        self.feature_config = normalize_feature_config(feature_config)
        self.views = list(self.feature_config["views"])

    def __len__(self) -> int:
        return int(self.x.shape[0])

    def __getitem__(
        self,
        index: int,
    ) -> tuple[torch.Tensor | dict[str, torch.Tensor], torch.Tensor, torch.Tensor]:
        iq = self.x[index]
        if self.views == ["iq"]:
            return iq, self.y[index], self.snr[index]

        features: dict[str, torch.Tensor] = {}
        if "iq" in self.views:
            features["iq"] = iq
        if "amp_phase" in self.views:
            amp_phase_cfg = self.feature_config["amp_phase"]
            features["amp_phase"] = compute_amplitude_phase_tensor(
                iq,
                normalize=bool(amp_phase_cfg.get("normalize", True)),
            )
        if "stft" in self.views:
            stft_cfg = self.feature_config["stft"]
            features["stft"] = compute_stft_tensor(
                iq,
                nperseg=int(stft_cfg.get("nperseg", stft_cfg.get("n_fft", 32))),
                noverlap=int(stft_cfg.get("noverlap", 16)),
                log_scale=bool(stft_cfg.get("log_scale", True)),
                normalize=bool(stft_cfg.get("normalize", True)),
            )
        if "cwt" in self.views:
            cwt_cfg = self.feature_config["cwt"]
            features["cwt"] = compute_cwt_tensor(
                iq,
                num_scales=int(cwt_cfg.get("num_scales", 16)),
                min_scale=float(cwt_cfg.get("min_scale", 1.0)),
                max_scale=float(cwt_cfg.get("max_scale", 32.0)),
                log_scale=bool(cwt_cfg.get("log_scale", True)),
                normalize=bool(cwt_cfg.get("normalize", True)),
            )
        return features, self.y[index], self.snr[index]


def load_data_bundle(config: dict[str, Any], project_root: str | None = None) -> DataBundle:
    data_cfg = config.get("data", {})
    project_cfg = config.get("project", {})
    seed = int(project_cfg.get("seed", 42))
    mode = str(data_cfg.get("mode", "mock")).lower()

    if mode == "mock":
        x, y, snr, mod_names, snr_values = generate_mock_radioml(
            num_samples=int(data_cfg.get("num_samples", 512)),
            num_classes=int(data_cfg.get("num_classes", 4)),
            snr_values=data_cfg.get("snr_values", [-6, 0, 6, 12]),
            signal_length=int(data_cfg.get("signal_length", 128)),
            seed=seed,
        )
        return DataBundle(
            x=x,
            y=y,
            snr=snr,
            mod_names=mod_names,
            snr_values=snr_values,
            mode="mock",
            metadata={"note": "Synthetic smoke-test data only; not valid for research conclusions."},
        )

    if mode == "real":
        x, y, snr, mod_names, snr_values, metadata = load_rml2016a(
            raw_path=data_cfg.get("raw_path", "auto"),
            raw_bz2_path=data_cfg.get("raw_bz2_path"),
            project_root=project_root,
            subset_mode=bool(data_cfg.get("subset_mode", False)),
            subset_mods=data_cfg.get("subset_mods"),
            subset_snrs=data_cfg.get("subset_snrs"),
            max_samples_per_group=data_cfg.get("max_samples_per_group"),
        )
        return DataBundle(x=x, y=y, snr=snr, mod_names=mod_names, snr_values=snr_values, mode="real", metadata=metadata)

    raise ValueError(f"Unsupported data mode: {mode}")


def summarize_data_bundle(bundle: DataBundle) -> dict[str, Any]:
    class_counts = {
        bundle.mod_names[int(label)]: int(count)
        for label, count in zip(*np.unique(bundle.y, return_counts=True))
    }
    snr_counts = {
        str(int(snr_value)): int(count)
        for snr_value, count in zip(*np.unique(bundle.snr, return_counts=True))
    }
    modulation_snr_counts: dict[str, int] = {}
    for class_idx, snr_value in zip(bundle.y, bundle.snr):
        key = f"{bundle.mod_names[int(class_idx)]}@{int(snr_value)}"
        modulation_snr_counts[key] = modulation_snr_counts.get(key, 0) + 1

    return {
        "mode": bundle.mode,
        "num_samples": int(bundle.x.shape[0]),
        "shape": list(bundle.x.shape),
        "dtype": str(bundle.x.dtype),
        "has_nan": bool(np.isnan(bundle.x).any()),
        "has_inf": bool(np.isinf(bundle.x).any()),
        "num_classes": len(bundle.mod_names),
        "num_snrs": len(bundle.snr_values),
        "mod_names": bundle.mod_names,
        "snr_values": [int(v) for v in bundle.snr_values],
        "class_counts": class_counts,
        "snr_counts": snr_counts,
        "modulation_snr_counts": dict(sorted(modulation_snr_counts.items())),
        "source_path": bundle.metadata.get("source_path"),
        "metadata": bundle.metadata,
    }
