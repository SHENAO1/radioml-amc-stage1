from __future__ import annotations

import numpy as np
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
