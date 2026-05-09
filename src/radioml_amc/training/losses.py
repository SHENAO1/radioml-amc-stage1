"""Loss factory for training with optional SNR-aware reweighting.

Default behaviour (no `train.loss` config or `train.loss.name == "ce"`) returns
a plain `nn.CrossEntropyLoss`, identical to Stage 5A. Setting
`train.loss.name == "snr_weighted_ce"` returns an `SnrWeightedCrossEntropy`
module whose forward signature is `forward(logits, y, snr_db)` and which
applies a per-sample weight derived from `snr_db`.

Two weighting schemes are supported:

  - `group`: piecewise-constant weights indexed by SNR group
    (`low`, `mid`, `high`), with explicit dB boundaries.
  - `continuous`: `w(snr) = exp(-alpha * snr_db / 10)`, clamped to
    [`min_weight`, `max_weight`]. Larger alpha means more emphasis on low SNR.

Trainer-level adapter `compute_loss(criterion, logits, y, snr_db)` calls
the SNR-aware path when applicable and falls back to plain CE otherwise.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass(frozen=True)
class SnrGroupBoundaries:
    low_max: float = -6.0
    mid_min: float = -4.0
    mid_max: float = 6.0
    high_min: float = 8.0


class SnrWeightedCrossEntropy(nn.Module):
    """Cross-entropy with a per-sample weight that depends on SNR.

    Sample loss is reduced as `(per_sample_loss * weight).sum() / weight.sum()`
    (a weighted mean). This keeps the loss magnitude comparable to plain CE
    while giving low-SNR samples a larger share of the gradient.
    """

    def __init__(
        self,
        scheme: str,
        group_weights: dict[str, float] | None = None,
        boundaries: SnrGroupBoundaries | None = None,
        alpha: float = 1.0,
        min_weight: float = 0.1,
        max_weight: float = 10.0,
    ) -> None:
        super().__init__()
        scheme = scheme.lower()
        if scheme not in {"group", "continuous"}:
            raise ValueError(f"unsupported scheme: {scheme!r}")
        self.scheme = scheme
        self.group_weights = dict(group_weights or {"low": 2.0, "mid": 1.0, "high": 0.7})
        self.boundaries = boundaries or SnrGroupBoundaries()
        self.alpha = float(alpha)
        self.min_weight = float(min_weight)
        self.max_weight = float(max_weight)

    def _weights_group(self, snr_db: torch.Tensor) -> torch.Tensor:
        w_low = float(self.group_weights.get("low", 1.0))
        w_mid = float(self.group_weights.get("mid", 1.0))
        w_high = float(self.group_weights.get("high", 1.0))
        b = self.boundaries
        out = torch.full_like(snr_db, w_mid, dtype=torch.float32)
        out = torch.where(snr_db <= b.low_max, torch.full_like(out, w_low), out)
        out = torch.where(snr_db >= b.high_min, torch.full_like(out, w_high), out)
        # Samples between low_max and mid_min, or between mid_max and high_min,
        # are transitional; treat them as mid by default.
        return out

    def _weights_continuous(self, snr_db: torch.Tensor) -> torch.Tensor:
        w = torch.exp(-self.alpha * snr_db.float() / 10.0)
        return torch.clamp(w, min=self.min_weight, max=self.max_weight)

    def forward(self, logits: torch.Tensor, y: torch.Tensor, snr_db: torch.Tensor) -> torch.Tensor:
        per_sample = F.cross_entropy(logits, y, reduction="none")
        snr_db = snr_db.to(logits.device).float()
        if self.scheme == "group":
            weights = self._weights_group(snr_db)
        else:
            weights = self._weights_continuous(snr_db)
        weights = weights.to(logits.device)
        denom = weights.sum().clamp(min=1.0)
        return (per_sample * weights).sum() / denom


def build_criterion(loss_cfg: dict[str, Any] | str | None) -> nn.Module:
    """Build a loss module from a config block.

    Returns a plain `nn.CrossEntropyLoss` if `loss_cfg` is None, an empty dict,
    a string `'ce'` / `'cross_entropy'`, or `{'name': 'ce'}`.
    Returns an `SnrWeightedCrossEntropy` if `name == 'snr_weighted_ce'`.
    """
    if loss_cfg is None or loss_cfg == {}:
        return nn.CrossEntropyLoss()
    if isinstance(loss_cfg, str):
        name = loss_cfg.lower()
        cfg: dict[str, Any] = {}
    else:
        cfg = dict(loss_cfg)
        name = str(cfg.get("name", "ce")).lower()

    if name in {"ce", "cross_entropy", "cross-entropy"}:
        label_smoothing = float(cfg.get("label_smoothing", 0.0))
        return nn.CrossEntropyLoss(label_smoothing=label_smoothing)
    if name in {"snr_weighted_ce", "snr_aware_ce"}:
        scheme = str(cfg.get("scheme", "group")).lower()
        group_weights = cfg.get("snr_group_weights")
        boundaries_cfg = cfg.get("boundary") or {}
        boundaries = SnrGroupBoundaries(
            low_max=float(boundaries_cfg.get("low_max", -6.0)),
            mid_min=float(boundaries_cfg.get("mid_min", -4.0)),
            mid_max=float(boundaries_cfg.get("mid_max", 6.0)),
            high_min=float(boundaries_cfg.get("high_min", 8.0)),
        )
        return SnrWeightedCrossEntropy(
            scheme=scheme,
            group_weights=group_weights,
            boundaries=boundaries,
            alpha=float(cfg.get("alpha", 1.0)),
            min_weight=float(cfg.get("min_weight", 0.1)),
            max_weight=float(cfg.get("max_weight", 10.0)),
        )
    raise ValueError(f"unsupported loss name: {name!r}")


def compute_loss(criterion: nn.Module, logits: torch.Tensor, y: torch.Tensor, snr_db: torch.Tensor) -> torch.Tensor:
    """Trainer adapter: call the SNR-aware path when applicable, else plain CE."""
    if isinstance(criterion, SnrWeightedCrossEntropy):
        return criterion(logits, y, snr_db)
    return criterion(logits, y)
