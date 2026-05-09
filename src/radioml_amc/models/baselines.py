from __future__ import annotations

from collections.abc import Mapping

import torch
import torch.nn.functional as F
from torch import nn


TensorInput = torch.Tensor | Mapping[str, torch.Tensor]


def _select_iq(x: TensorInput) -> torch.Tensor:
    if isinstance(x, Mapping):
        if "iq" not in x:
            raise KeyError("Missing required input view: iq")
        return x["iq"]
    return x


class _CausalConv1d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int):
        super().__init__()
        self.left_pad = kernel_size - 1
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(F.pad(x, (self.left_pad, 0)))


class _SamePadConv2d(nn.Module):
    def __init__(self, in_channels: int, out_channels: int, kernel_size: tuple[int, int]):
        super().__init__()
        kh, kw = kernel_size
        top = (kh - 1) // 2
        bottom = kh - 1 - top
        left = (kw - 1) // 2
        right = kw - 1 - left
        self.pad = (left, right, top, bottom)
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(F.pad(x, self.pad))


class MCLDNN(nn.Module):
    """PyTorch MCLDNN-style I/Q baseline for RadioML2016.10A length-128 inputs."""

    def __init__(self, num_classes: int, dropout: float = 0.5):
        super().__init__()
        self.views = ["iq"]
        self.iq_spatial = nn.Sequential(
            _SamePadConv2d(1, 50, kernel_size=(2, 8)),
            nn.ReLU(inplace=True),
        )
        self.i_stream = nn.Sequential(
            _CausalConv1d(1, 50, kernel_size=8),
            nn.ReLU(inplace=True),
        )
        self.q_stream = nn.Sequential(
            _CausalConv1d(1, 50, kernel_size=8),
            nn.ReLU(inplace=True),
        )
        self.independent_spatial = nn.Sequential(
            _SamePadConv2d(50, 50, kernel_size=(1, 8)),
            nn.ReLU(inplace=True),
        )
        self.fusion_conv = nn.Sequential(
            nn.Conv2d(100, 100, kernel_size=(2, 5)),
            nn.ReLU(inplace=True),
        )
        self.temporal = nn.LSTM(
            input_size=100,
            hidden_size=128,
            num_layers=2,
            batch_first=True,
            dropout=0.0,
        )
        self.classifier = nn.Sequential(
            nn.Linear(128, 128),
            nn.SELU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(128, 128),
            nn.SELU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: TensorInput) -> torch.Tensor:
        iq = _select_iq(x)
        if iq.ndim != 3 or iq.shape[1] != 2:
            raise ValueError(f"MCLDNN expects I/Q input with shape [B, 2, L], got {tuple(iq.shape)}")

        joint = self.iq_spatial(iq.unsqueeze(1))
        i_features = self.i_stream(iq[:, 0:1, :])
        q_features = self.q_stream(iq[:, 1:2, :])
        independent = torch.stack([i_features, q_features], dim=2)
        independent = self.independent_spatial(independent)
        features = torch.cat([joint, independent], dim=1)
        features = self.fusion_conv(features).squeeze(2).transpose(1, 2)
        _, (hidden, _) = self.temporal(features)
        return self.classifier(hidden[-1])


class CLDNN(nn.Module):
    """Raw I/Q convolutional-LSTM-DNN temporal baseline.

    The intent is a reviewer-standard CNN+LSTM comparison point with a simpler
    single-stream I/Q path than MCLDNN. It consumes `[B, 2, L]` I/Q tensors and
    returns logits for the shared V2 training and artifact path.
    """

    def __init__(self, num_classes: int, dropout: float = 0.5):
        super().__init__()
        self.views = ["iq"]
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
            hidden_size=128,
            num_layers=1,
            batch_first=True,
        )
        self.classifier = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: TensorInput) -> torch.Tensor:
        iq = _select_iq(x)
        if iq.ndim != 3 or iq.shape[1] != 2:
            raise ValueError(f"CLDNN expects I/Q input with shape [B, 2, L], got {tuple(iq.shape)}")

        x = self.features(iq).transpose(1, 2)
        _, (hidden, _) = self.temporal(x)
        return self.classifier(hidden[-1])


class _DepthwiseSeparableConv2d(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: tuple[int, int],
        padding: tuple[int, int],
        activation: bool,
    ):
        super().__init__()
        self.depthwise = nn.Conv2d(
            in_channels,
            in_channels,
            kernel_size=kernel_size,
            padding=padding,
            groups=in_channels,
            bias=False,
        )
        self.pointwise = nn.Conv2d(in_channels, out_channels, kernel_size=1)
        self.activation = nn.ReLU(inplace=True) if activation else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(self.pointwise(self.depthwise(x)))


class _DSCResidualUnit(nn.Module):
    def __init__(self, channels: int, kernel_size: tuple[int, int] = (1, 5)):
        super().__init__()
        padding = (kernel_size[0] // 2, kernel_size[1] // 2)
        self.conv_relu = _DepthwiseSeparableConv2d(
            channels,
            channels,
            kernel_size=kernel_size,
            padding=padding,
            activation=True,
        )
        self.conv_linear = _DepthwiseSeparableConv2d(
            channels,
            channels,
            kernel_size=kernel_size,
            padding=padding,
            activation=False,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.conv_linear(self.conv_relu(x))


class _DSCResidualStack(nn.Module):
    def __init__(self, in_channels: int, channels: int):
        super().__init__()
        self.channel_fusion = nn.Conv2d(in_channels, channels, kernel_size=1)
        self.units = nn.Sequential(
            _DSCResidualUnit(channels),
            _DSCResidualUnit(channels),
        )
        self.pool = nn.MaxPool2d(kernel_size=(1, 2))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.channel_fusion(x)
        x = self.units(x)
        return self.pool(x)


class LWAMCNet(nn.Module):
    """LWAMCNet-style lightweight I/Q CNN for RadioML2016.10A length-128 inputs.

    This follows the paper's 2016.10A-scale variant: a 2x5 first convolution,
    three DSC residual stacks, GDWConv reconstruction, and one classifier layer.
    """

    def __init__(
        self,
        num_classes: int,
        input_length: int = 128,
        stack_channels: int = 32,
    ):
        super().__init__()
        if input_length % 8 != 0:
            raise ValueError("LWAMCNet input_length must be divisible by 8 for three pooling stacks.")
        self.views = ["iq"]
        self.input_length = input_length
        self.feature_length = input_length // 8
        self.features = nn.Sequential(
            nn.Conv2d(1, 64, kernel_size=(2, 5), padding=(0, 2)),
            nn.ReLU(inplace=True),
            _DSCResidualStack(64, stack_channels),
            _DSCResidualStack(stack_channels, stack_channels),
            _DSCResidualStack(stack_channels, stack_channels),
        )
        self.gdwconv = nn.Sequential(
            nn.Conv2d(
                stack_channels,
                stack_channels,
                kernel_size=(1, self.feature_length),
                groups=stack_channels,
            ),
            nn.ReLU(inplace=True),
        )
        self.classifier = nn.Linear(stack_channels, num_classes)

    def forward(self, x: TensorInput) -> torch.Tensor:
        iq = _select_iq(x)
        if iq.ndim != 3 or iq.shape[1] != 2:
            raise ValueError(f"LWAMCNet expects I/Q input with shape [B, 2, L], got {tuple(iq.shape)}")
        if iq.shape[-1] != self.input_length:
            raise ValueError(f"LWAMCNet expects signal length {self.input_length}, got {iq.shape[-1]}")

        x = self.features(iq.unsqueeze(1))
        if x.shape[-1] != self.feature_length:
            raise ValueError(f"Unexpected LWAMCNet feature length {x.shape[-1]}, expected {self.feature_length}")
        x = self.gdwconv(x).flatten(start_dim=1)
        return self.classifier(x)


class ParameterMatchedIQOnlyNet(nn.Module):
    """I/Q-only CNN sized to track the scalar gated I/Q+STFT parameter budget."""

    def __init__(self, num_classes: int, dropout: float = 0.1):
        super().__init__()
        self.views = ["iq"]
        self.features = nn.Sequential(
            nn.Conv1d(2, 64, kernel_size=7, padding=3, bias=False),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(64, 96, kernel_size=5, padding=2, bias=False),
            nn.BatchNorm1d(96),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(96, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.Conv1d(128, 128, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool1d(1),
        )
        self.classifier = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: TensorInput) -> torch.Tensor:
        iq = _select_iq(x)
        x = self.features(iq)
        x = torch.flatten(x, start_dim=1)
        return self.classifier(x)


def count_parameters(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
