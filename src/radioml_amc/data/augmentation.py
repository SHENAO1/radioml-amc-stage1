"""Signal-domain augmentation for AMC training.

Implements label-preserving I/Q transforms used during training only:

  - Phase rotation: rotate the (I, Q) channel pair by a random angle
    ``theta ~ U(-pi, pi)``. AMC labels are rotation-invariant for the
    modulation-type classification task, so this is safe.
  - Cyclic time shift: roll the time axis by a random ``k ~ U(-max_shift, max_shift)``.
    Quasi-stationary signals retain their modulation type under small shifts.

Operations explicitly NOT applied here, and the reasons:

  - Amplitude scaling: changes effective SNR, which conflicts with the
    project's SNR-conditioned analysis pipeline (per-SNR accuracy curves and
    paired statistical tests grouped by snr_db).
  - Additive Gaussian noise: same SNR-conflict reason.
  - Image-style mixup: linear interpolation of I/Q + label interpolation
    produces non-physical signals (Huang et al. 2022, "Mixing Signals", arXiv:2204.03737).

The augmenter is applied inside `SignalDataset.__getitem__` *before* derived
views (STFT, CWT, amp/phase) are computed, so the derived views see the
augmented I/Q. This is the correct point to inject augmentation: deriving
features after augmentation guarantees consistency between the I/Q branch and
the time-frequency branch in fusion models.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import torch


@dataclass
class SignalAugmentConfig:
    enabled: bool = False
    phase_rotation_prob: float = 0.5
    time_shift_prob: float = 0.5
    time_shift_max: int = 8


class SignalAugmenter:
    """Apply label-preserving I/Q augmentation.

    Stateless aside from configuration; randomness comes from torch's global RNG
    (or a per-worker generator if the dataloader sets one).
    """

    def __init__(self, config: SignalAugmentConfig) -> None:
        self.config = config

    def __call__(self, iq: torch.Tensor) -> torch.Tensor:
        if not self.config.enabled:
            return iq
        if iq.ndim != 2 or iq.shape[0] != 2:
            raise ValueError(f"SignalAugmenter expects [2, L] I/Q tensor, got {tuple(iq.shape)}")

        out = iq
        if self.config.phase_rotation_prob > 0 and torch.rand(()) < self.config.phase_rotation_prob:
            theta = float((torch.rand(()) * 2.0 - 1.0) * math.pi)
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)
            i_chan, q_chan = out[0], out[1]
            new_i = i_chan * cos_t - q_chan * sin_t
            new_q = i_chan * sin_t + q_chan * cos_t
            out = torch.stack([new_i, new_q], dim=0)

        if self.config.time_shift_prob > 0 and self.config.time_shift_max > 0 and torch.rand(()) < self.config.time_shift_prob:
            max_k = int(self.config.time_shift_max)
            k = int(torch.randint(low=-max_k, high=max_k + 1, size=()).item())
            if k != 0:
                out = torch.roll(out, shifts=k, dims=1)

        return out


def build_augmenter(config: dict | None) -> SignalAugmenter | None:
    """Build a SignalAugmenter from a config block; return None if disabled."""
    if not config:
        return None
    cfg = SignalAugmentConfig(
        enabled=bool(config.get("enabled", False)),
        phase_rotation_prob=float(config.get("phase_rotation_prob", 0.0)),
        time_shift_prob=float(config.get("time_shift_prob", 0.0)),
        time_shift_max=int(config.get("time_shift_max", 0)),
    )
    if not cfg.enabled:
        return None
    return SignalAugmenter(cfg)
