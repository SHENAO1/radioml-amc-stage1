from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset

from radioml_amc.data.mock_dataset import generate_mock_radioml
from radioml_amc.data.rml2016a_loader import load_rml2016a


@dataclass
class DataBundle:
    x: np.ndarray
    y: np.ndarray
    snr: np.ndarray
    mod_names: list[str]
    snr_values: list[int]
    mode: str
    metadata: dict[str, Any] = field(default_factory=dict)


class SignalDataset(Dataset):
    def __init__(self, x: np.ndarray, y: np.ndarray, snr: np.ndarray):
        self.x = torch.as_tensor(x, dtype=torch.float32)
        self.y = torch.as_tensor(y, dtype=torch.long)
        self.snr = torch.as_tensor(snr, dtype=torch.long)

    def __len__(self) -> int:
        return int(self.x.shape[0])

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.x[index], self.y[index], self.snr[index]


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
            raw_path=data_cfg.get("raw_path", "data/raw/RML2016.10a_dict.pkl"),
            raw_bz2_path=data_cfg.get("raw_bz2_path", "data/raw/RML2016.10a_dict.pkl.bz2"),
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
    return {
        "mode": bundle.mode,
        "num_samples": int(bundle.x.shape[0]),
        "shape": list(bundle.x.shape),
        "dtype": str(bundle.x.dtype),
        "num_classes": len(bundle.mod_names),
        "mod_names": bundle.mod_names,
        "snr_values": [int(v) for v in bundle.snr_values],
        "class_counts": class_counts,
        "snr_counts": snr_counts,
        "metadata": bundle.metadata,
    }

