from __future__ import annotations

from collections.abc import Mapping

import torch
from torch import nn

from radioml_amc.models.multiview import IQBranch1D, TimeFrequencyBranch2D


TensorInput = torch.Tensor | Mapping[str, torch.Tensor]


def _select_view(x: TensorInput, view: str) -> torch.Tensor:
    if isinstance(x, Mapping):
        if view not in x:
            raise KeyError(f"Missing required input view: {view}")
        return x[view]
    if view != "iq":
        raise KeyError(f"Tensor input can only satisfy the iq view, requested: {view}")
    return x


class ScalarGatedIQSTFTFusionNet(nn.Module):
    """Minimal SNR-free scalar gated I/Q + STFT fusion prototype.

    The gate is intentionally small and receives no explicit SNR input. It is a
    hypothesis-test module, not evidence that fusion is broadly superior.
    """

    def __init__(
        self,
        num_classes: int,
        fusion_dim: int = 128,
        gate_hidden_dim: int = 64,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.views = ["iq", "stft"]
        self.iq_branch = IQBranch1D(in_channels=2, embedding_dim=128)
        self.stft_branch = TimeFrequencyBranch2D(in_channels=1, embedding_dim=64)
        self.proj_iq = nn.Linear(128, fusion_dim)
        self.proj_stft = nn.Linear(64, fusion_dim)
        gate_input_dim = fusion_dim * 4
        self.gate = nn.Sequential(
            nn.Linear(gate_input_dim, gate_hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(gate_hidden_dim, 1),
            nn.Sigmoid(),
        )
        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim, fusion_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(fusion_dim, num_classes),
        )

    def encode(self, x: TensorInput) -> tuple[torch.Tensor, torch.Tensor]:
        iq = _select_view(x, "iq")
        stft = _select_view(x, "stft")
        z_iq = self.proj_iq(self.iq_branch(iq))
        z_stft = self.proj_stft(self.stft_branch(stft))
        return z_iq, z_stft

    def fuse(self, z_iq: torch.Tensor, z_stft: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        gate_input = torch.cat([z_iq, z_stft, torch.abs(z_iq - z_stft), z_iq * z_stft], dim=1)
        gate_scalar = self.gate(gate_input)
        fused = (1.0 - gate_scalar) * z_iq + gate_scalar * z_stft
        return fused, gate_scalar

    def forward_with_aux(self, x: TensorInput) -> dict[str, torch.Tensor]:
        z_iq, z_stft = self.encode(x)
        fused, gate_scalar = self.fuse(z_iq, z_stft)
        logits = self.classifier(fused)
        return {
            "logits": logits,
            "gate_scalar": gate_scalar,
            "gate_iq_mean": 1.0 - gate_scalar,
            "gate_tf_mean": gate_scalar,
        }

    def forward(self, x: TensorInput) -> torch.Tensor:
        return self.forward_with_aux(x)["logits"]


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
