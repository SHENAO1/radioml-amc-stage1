from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

from radioml_amc.data.dataset import DataBundle
from radioml_amc.features.time_frequency import compute_amplitude_phase, compute_stft_power


def _choose_indices(num_samples: int, count: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    count = min(count, num_samples)
    return rng.choice(num_samples, size=count, replace=False)


def _title(bundle: DataBundle, idx: int) -> str:
    mod = bundle.mod_names[int(bundle.y[idx])]
    snr = int(bundle.snr[idx])
    return f"{mod}, SNR={snr} dB"


def save_signal_example_plots(
    bundle: DataBundle,
    output_dir: str | Path,
    stft_config: dict | None = None,
    num_examples: int = 4,
    seed: int = 42,
) -> dict[str, str]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    stft_config = stft_config or {}
    indices = _choose_indices(len(bundle.y), num_examples, seed)
    time_axis = np.arange(bundle.x.shape[-1])
    saved: dict[str, str] = {}

    fig, axes = plt.subplots(len(indices), 1, figsize=(10, 2.6 * len(indices)), squeeze=False)
    for row, idx in enumerate(indices):
        sample = bundle.x[idx]
        ax = axes[row, 0]
        ax.plot(time_axis, sample[0], label="I", linewidth=1.2)
        ax.plot(time_axis, sample[1], label="Q", linewidth=1.2)
        ax.set_title(_title(bundle, int(idx)))
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude")
        ax.grid(alpha=0.25)
        ax.legend(loc="upper right")
    fig.tight_layout()
    path = output / "iq_examples.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    saved["iq_examples"] = str(path)

    fig, axes = plt.subplots(1, len(indices), figsize=(3.4 * len(indices), 3.2), squeeze=False)
    for col, idx in enumerate(indices):
        sample = bundle.x[idx]
        ax = axes[0, col]
        ax.scatter(sample[0], sample[1], s=10, alpha=0.7)
        ax.set_title(_title(bundle, int(idx)))
        ax.set_xlabel("I")
        ax.set_ylabel("Q")
        ax.grid(alpha=0.25)
        ax.axis("equal")
    fig.tight_layout()
    path = output / "constellation_examples.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    saved["constellation_examples"] = str(path)

    fig, axes = plt.subplots(len(indices), 2, figsize=(11, 2.6 * len(indices)), squeeze=False)
    for row, idx in enumerate(indices):
        amplitude, phase = compute_amplitude_phase(bundle.x[idx])
        axes[row, 0].plot(time_axis, amplitude, linewidth=1.2)
        axes[row, 0].set_title(f"Amplitude: {_title(bundle, int(idx))}")
        axes[row, 0].set_xlabel("Sample")
        axes[row, 0].grid(alpha=0.25)
        axes[row, 1].plot(time_axis, phase, linewidth=1.2, color="tab:orange")
        axes[row, 1].set_title(f"Phase: {_title(bundle, int(idx))}")
        axes[row, 1].set_xlabel("Sample")
        axes[row, 1].grid(alpha=0.25)
    fig.tight_layout()
    path = output / "amplitude_phase_examples.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    saved["amplitude_phase_examples"] = str(path)

    fig, axes = plt.subplots(1, len(indices), figsize=(3.8 * len(indices), 3.3), squeeze=False)
    for col, idx in enumerate(indices):
        freqs, times, power_db = compute_stft_power(
            bundle.x[idx],
            nperseg=int(stft_config.get("nperseg", 32)),
            noverlap=int(stft_config.get("noverlap", 16)),
        )
        ax = axes[0, col]
        im = ax.pcolormesh(times, freqs, power_db, shading="auto", cmap="viridis")
        ax.set_title(_title(bundle, int(idx)))
        ax.set_xlabel("Time")
        ax.set_ylabel("Frequency")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    path = output / "stft_examples.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    saved["stft_examples"] = str(path)

    return saved

