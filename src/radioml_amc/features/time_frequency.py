from __future__ import annotations

import numpy as np
import torch
from torch.nn import functional as F
from scipy.signal import stft


def iq_to_complex(sample: np.ndarray) -> np.ndarray:
    if sample.shape[0] != 2:
        raise ValueError(f"Expected sample shape [2, L], got {sample.shape}")
    return sample[0].astype(np.float32) + 1j * sample[1].astype(np.float32)


def compute_amplitude_phase(sample: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    complex_signal = iq_to_complex(sample)
    amplitude = np.abs(complex_signal)
    phase = np.unwrap(np.angle(complex_signal))
    return amplitude.astype(np.float32), phase.astype(np.float32)


def compute_stft_power(
    sample: np.ndarray,
    nperseg: int = 32,
    noverlap: int = 16,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    complex_signal = iq_to_complex(sample)
    freqs, times, zxx = stft(
        complex_signal,
        nperseg=nperseg,
        noverlap=noverlap,
        return_onesided=False,
        boundary=None,
    )
    power_db = 20.0 * np.log10(np.abs(zxx) + 1e-8)
    order = np.argsort(freqs)
    freqs = freqs[order]
    power_db = power_db[order, :]
    return freqs, times, power_db.astype(np.float32)


def _as_iq_tensor(sample: torch.Tensor | np.ndarray) -> torch.Tensor:
    tensor = sample if torch.is_tensor(sample) else torch.as_tensor(sample)
    tensor = tensor.to(dtype=torch.float32)
    if tensor.ndim != 2 or int(tensor.shape[0]) != 2:
        raise ValueError(f"Expected I/Q tensor shape [2, L], got {tuple(tensor.shape)}")
    return tensor


def _normalize_image(image: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    mean = image.mean()
    std = image.std(unbiased=False)
    return (image - mean) / torch.clamp(std, min=eps)


def compute_stft_tensor(
    sample: torch.Tensor | np.ndarray,
    nperseg: int = 32,
    noverlap: int = 16,
    log_scale: bool = True,
    normalize: bool = True,
) -> torch.Tensor:
    """Compute a single-sample STFT view on demand.

    Returns a float tensor with shape [1, frequency_bins, time_frames].
    """
    iq = _as_iq_tensor(sample)
    nperseg = int(nperseg)
    noverlap = int(noverlap)
    if nperseg <= 0:
        raise ValueError("nperseg must be positive")
    if noverlap < 0 or noverlap >= nperseg:
        raise ValueError("noverlap must satisfy 0 <= noverlap < nperseg")

    hop_length = max(1, nperseg - noverlap)
    complex_signal = torch.complex(iq[0], iq[1])
    window = torch.hann_window(nperseg, dtype=iq.dtype, device=iq.device)
    spec = torch.stft(
        complex_signal,
        n_fft=nperseg,
        hop_length=hop_length,
        win_length=nperseg,
        window=window,
        center=False,
        onesided=False,
        return_complex=True,
    )
    magnitude = torch.fft.fftshift(spec.abs(), dim=0)
    if log_scale:
        magnitude = torch.log1p(magnitude)
    image = magnitude.unsqueeze(0).to(dtype=torch.float32)
    return _normalize_image(image) if normalize else image


def _ricker_wavelet(scale: float, dtype: torch.dtype, device: torch.device) -> torch.Tensor:
    radius = max(1, int(round(4.0 * float(scale))))
    t = torch.arange(-radius, radius + 1, dtype=dtype, device=device)
    scaled = t / float(scale)
    coeff = 2.0 / (np.sqrt(3.0 * float(scale)) * np.pi ** 0.25)
    wavelet = coeff * (1.0 - scaled.square()) * torch.exp(-0.5 * scaled.square())
    wavelet = wavelet - wavelet.mean()
    denom = torch.linalg.vector_norm(wavelet)
    return wavelet / torch.clamp(denom, min=1e-6)


def compute_cwt_tensor(
    sample: torch.Tensor | np.ndarray,
    num_scales: int = 16,
    min_scale: float = 1.0,
    max_scale: float = 32.0,
    log_scale: bool = True,
    normalize: bool = True,
) -> torch.Tensor:
    """Compute a lightweight Ricker CWT magnitude view on demand.

    Returns a float tensor with shape [1, num_scales, signal_length].
    """
    iq = _as_iq_tensor(sample)
    num_scales = int(num_scales)
    min_scale = float(min_scale)
    max_scale = float(max_scale)
    if num_scales <= 0:
        raise ValueError("num_scales must be positive")
    if min_scale <= 0 or max_scale < min_scale:
        raise ValueError("CWT scales must satisfy 0 < min_scale <= max_scale")

    real = iq[0].view(1, 1, -1)
    imag = iq[1].view(1, 1, -1)
    target_length = int(iq.shape[-1])
    scale_values = torch.linspace(min_scale, max_scale, steps=num_scales, dtype=iq.dtype, device=iq.device)
    rows: list[torch.Tensor] = []
    for scale in scale_values.tolist():
        wavelet = _ricker_wavelet(float(scale), dtype=iq.dtype, device=iq.device).view(1, 1, -1)
        padding = int(wavelet.shape[-1] // 2)
        real_conv = F.conv1d(real, wavelet, padding=padding)
        imag_conv = F.conv1d(imag, wavelet, padding=padding)
        coeff = torch.sqrt(real_conv.square() + imag_conv.square() + 1e-12).view(-1)
        if int(coeff.shape[0]) > target_length:
            start = (int(coeff.shape[0]) - target_length) // 2
            coeff = coeff[start : start + target_length]
        elif int(coeff.shape[0]) < target_length:
            coeff = F.pad(coeff, (0, target_length - int(coeff.shape[0])))
        rows.append(coeff)

    image = torch.stack(rows, dim=0)
    if log_scale:
        image = torch.log1p(image)
    image = image.unsqueeze(0).to(dtype=torch.float32)
    return _normalize_image(image) if normalize else image
