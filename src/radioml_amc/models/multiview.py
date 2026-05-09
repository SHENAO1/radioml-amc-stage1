from __future__ import annotations

from collections.abc import Mapping

import torch
from torch import nn


TensorInput = torch.Tensor | Mapping[str, torch.Tensor]


def _select_view(x: TensorInput, view: str) -> torch.Tensor:
    if isinstance(x, Mapping):
        if view not in x:
            raise KeyError(f"Missing required input view: {view}")
        return x[view]
    return x


class IQBranch1D(nn.Module):
    def __init__(self, in_channels: int = 2, embedding_dim: int = 128):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(in_channels, 32, kernel_size=7, padding=3, bias=False),
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(32, 64, kernel_size=5, padding=2, bias=False),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(64, embedding_dim, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm1d(embedding_dim),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool1d(1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return torch.flatten(x, start_dim=1)


class TimeFrequencyBranch2D(nn.Module):
    def __init__(self, in_channels: int = 1, embedding_dim: int = 64):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2),
            nn.Conv2d(32, embedding_dim, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(embedding_dim),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        return torch.flatten(x, start_dim=1)


class TimeFrequencyCNN(nn.Module):
    def __init__(self, num_classes: int, view: str = "stft", in_channels: int = 1):
        super().__init__()
        self.view = view
        self.branch = TimeFrequencyBranch2D(in_channels=in_channels, embedding_dim=64)
        self.classifier = nn.Linear(64, num_classes)

    def forward(self, x: TensorInput) -> torch.Tensor:
        view_tensor = _select_view(x, self.view)
        embedding = self.branch(view_tensor)
        return self.classifier(embedding)


class MultiViewFusionNet(nn.Module):
    def __init__(self, num_classes: int, views: list[str] | tuple[str, ...]):
        super().__init__()
        if not views:
            raise ValueError("At least one input view is required for fusion.")
        self.views = list(views)
        branches: dict[str, nn.Module] = {}
        dims: dict[str, int] = {}
        for view in self.views:
            if view in {"iq", "amp_phase"}:
                branches[view] = IQBranch1D(embedding_dim=128)
                dims[view] = 128
            elif view in {"stft", "cwt"}:
                branches[view] = TimeFrequencyBranch2D(in_channels=1, embedding_dim=64)
                dims[view] = 64
            else:
                raise ValueError(f"Unsupported fusion view: {view}")

        self.branches = nn.ModuleDict(branches)
        total_dim = sum(dims[view] for view in self.views)
        hidden_dim = min(256, max(96, total_dim))
        self.classifier = nn.Sequential(
            nn.Linear(total_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: TensorInput) -> torch.Tensor:
        embeddings = []
        for view in self.views:
            view_tensor = _select_view(x, view)
            embeddings.append(self.branches[view](view_tensor))
        fused = torch.cat(embeddings, dim=1)
        return self.classifier(fused)


class CLDNNIQBranch(nn.Module):
    """CLDNN-style I/Q encoder used as a branch inside multi-view fusion.

    This is the CLDNN feature stack (3 Conv1d + BN + ReLU + 2 MaxPool) followed
    by an LSTM whose final hidden state is the branch embedding. It mirrors
    `radioml_amc.models.baselines.CLDNN` minus the classification head, so
    `FusionCldnnStftNet` can stack a fusion classifier on top.

    Output shape: ``[B, embedding_dim]`` with ``embedding_dim = 128``.
    """

    def __init__(self, embedding_dim: int = 128) -> None:
        super().__init__()
        self.embedding_dim = embedding_dim
        self.features = nn.Sequential(
            nn.Conv1d(2, 64, kernel_size=7, padding=3, bias=False),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(64, 128, kernel_size=5, padding=2, bias=False),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(128, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
        )
        self.temporal = nn.LSTM(
            input_size=128,
            hidden_size=embedding_dim,
            num_layers=1,
            batch_first=True,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 3 or x.shape[1] != 2:
            raise ValueError(f"CLDNNIQBranch expects [B, 2, L], got {tuple(x.shape)}")
        feats = self.features(x).transpose(1, 2)  # -> [B, T, 128]
        _, (hidden, _) = self.temporal(feats)
        return hidden[-1]  # [B, embedding_dim]


class FusionCldnnStftNet(nn.Module):
    """I/Q + STFT static fusion with a CLDNN-style I/Q encoder.

    Replaces the lightweight `IQBranch1D` used by `MultiViewFusionNet` with a
    CNN+LSTM I/Q backbone (`CLDNNIQBranch`), keeping the same STFT 2D-CNN
    branch (`TimeFrequencyBranch2D`) and the same fused-MLP head.

    The motivation comes from project evidence (P1.2): the existing fusion
    model has a *lighter* I/Q backbone than ResNet1D and is therefore
    backbone-capacity-limited rather than compute-limited. Putting CLDNN's
    capacity directly into the fusion path tests whether a stronger I/Q
    encoder closes the fusion-vs-CLDNN overall-accuracy gap.
    """

    def __init__(self, num_classes: int) -> None:
        super().__init__()
        self.views = ["iq", "stft"]
        self.iq_branch = CLDNNIQBranch(embedding_dim=128)
        self.stft_branch = TimeFrequencyBranch2D(in_channels=1, embedding_dim=64)
        total_dim = 128 + 64
        hidden_dim = max(96, min(256, total_dim))
        self.classifier = nn.Sequential(
            nn.Linear(total_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.1),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, x: TensorInput) -> torch.Tensor:
        iq = _select_view(x, "iq")
        stft = _select_view(x, "stft")
        iq_emb = self.iq_branch(iq)
        stft_emb = self.stft_branch(stft)
        fused = torch.cat([iq_emb, stft_emb], dim=1)
        return self.classifier(fused)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
