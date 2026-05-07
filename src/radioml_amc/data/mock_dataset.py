from __future__ import annotations

from dataclasses import dataclass

import numpy as np


DEFAULT_MOD_NAMES = ["BPSK", "QPSK", "8PSK", "QAM16", "QAM64", "CPFSK", "GFSK", "PAM4"]


@dataclass(frozen=True)
class MockSignalConfig:
    num_samples: int = 512
    num_classes: int = 4
    snr_values: tuple[int, ...] = (-6, 0, 6, 12)
    signal_length: int = 128
    seed: int = 42


def _symbol_stream(mod_name: str, length: int, rng: np.random.Generator) -> np.ndarray:
    if mod_name == "BPSK":
        symbols = rng.choice([-1.0, 1.0], size=length) + 0j
    elif mod_name == "QPSK":
        base = rng.choice([1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j], size=length)
        symbols = base / np.sqrt(2.0)
    elif mod_name == "8PSK":
        phases = rng.integers(0, 8, size=length) * (2 * np.pi / 8)
        symbols = np.exp(1j * phases)
    elif mod_name == "QAM16":
        vals = np.array([-3, -1, 1, 3], dtype=np.float32)
        i = rng.choice(vals, size=length)
        q = rng.choice(vals, size=length)
        symbols = (i + 1j * q) / np.sqrt(10.0)
    else:
        phases = rng.uniform(-np.pi, np.pi, size=length)
        envelope = 0.8 + 0.4 * rng.random(size=length)
        symbols = envelope * np.exp(1j * phases)
    return symbols.astype(np.complex64)


def generate_mock_radioml(
    num_samples: int = 512,
    num_classes: int = 4,
    snr_values: list[int] | tuple[int, ...] = (-6, 0, 6, 12),
    signal_length: int = 128,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str], list[int]]:
    """Generate small synthetic I/Q data for engineering smoke tests only."""
    rng = np.random.default_rng(seed)
    mod_names = DEFAULT_MOD_NAMES[:num_classes]
    snr_values = [int(v) for v in snr_values]

    x = np.empty((num_samples, 2, signal_length), dtype=np.float32)
    y = np.empty((num_samples,), dtype=np.int64)
    snr = np.empty((num_samples,), dtype=np.int64)

    t = np.arange(signal_length, dtype=np.float32)
    for idx in range(num_samples):
        class_idx = idx % num_classes
        snr_value = snr_values[(idx // num_classes) % len(snr_values)]
        mod_name = mod_names[class_idx]

        symbols = _symbol_stream(mod_name, signal_length, rng)
        freq_offset = rng.uniform(-0.04, 0.04)
        phase_offset = rng.uniform(-np.pi, np.pi)
        faded = symbols * np.exp(1j * (2 * np.pi * freq_offset * t + phase_offset))

        signal_power = float(np.mean(np.abs(faded) ** 2))
        noise_power = signal_power / (10 ** (snr_value / 10.0))
        noise = np.sqrt(noise_power / 2.0) * (
            rng.standard_normal(signal_length) + 1j * rng.standard_normal(signal_length)
        )
        sample = faded + noise

        x[idx, 0, :] = sample.real.astype(np.float32)
        x[idx, 1, :] = sample.imag.astype(np.float32)
        y[idx] = class_idx
        snr[idx] = snr_value

    order = rng.permutation(num_samples)
    return x[order], y[order], snr[order], mod_names, snr_values

