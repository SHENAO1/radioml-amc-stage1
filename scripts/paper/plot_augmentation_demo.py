"""Generate fig23: augmentation visualization demo.

One QPSK sample at +6 dB SNR from RML2016.10a_dict.pkl is shown under 4 conditions:
  (a) Original I/Q waveform
  (b) Phase rotation θ = π/3
  (c) Cyclic time shift k = +8
  (d) Both applied (phase rotation then cyclic shift)

I channel: blue solid line; Q channel: orange dashed line.
X axis: sample index 0–127; Y axis: amplitude.

Data source:
  data/raw/radioml2016/RML2016.10a_dict.pkl

Output:
  docs/paper/course_report/figures/fig23_augmentation_visualization.{pdf,png}
"""
from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "docs/paper/course_report/figures"
PKL_PATH = REPO_ROOT / "data/raw/radioml2016/RML2016.10a_dict.pkl"

TARGET_MOD = "QPSK"
TARGET_SNR = 6  # dB
SAMPLE_INDEX = 0  # first sample in that bin

THETA = np.pi / 3  # phase rotation angle
CYCLIC_SHIFT = 8   # samples to shift right


def load_sample() -> np.ndarray:
    """Load a [2, 128] QPSK @ +6 dB sample from the dataset."""
    if not PKL_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {PKL_PATH}")
    with open(PKL_PATH, "rb") as f:
        dataset = pickle.load(f, encoding="latin1")

    # Try common key formats: ('QPSK', 6) or b'QPSK'
    key = (TARGET_MOD, TARGET_SNR)
    if key not in dataset:
        # Try finding any key with matching mod & snr
        for k in dataset:
            if isinstance(k, (list, tuple)) and len(k) == 2:
                if str(k[0]) == TARGET_MOD and int(k[1]) == TARGET_SNR:
                    key = k
                    break
        else:
            raise KeyError(
                f"Key ({TARGET_MOD}, {TARGET_SNR}) not found. Available: {list(dataset.keys())[:10]}"
            )

    samples = dataset[key]  # shape: [N, 2, 128] or similar
    arr = np.array(samples[SAMPLE_INDEX])  # [2, 128]
    if arr.shape[0] != 2 or arr.shape[1] != 128:
        raise ValueError(f"Unexpected sample shape: {arr.shape}, expected [2, 128]")
    return arr.astype(np.float32)


def apply_phase_rotation(x: np.ndarray, theta: float) -> np.ndarray:
    """Apply phase rotation θ to [2, 128] I/Q signal.
    x[0]=I, x[1]=Q. Rotation: [cosθ, -sinθ; sinθ, cosθ] * [I; Q].
    """
    rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    return (rot @ x).astype(np.float32)  # [2, 128]


def apply_cyclic_shift(x: np.ndarray, k: int) -> np.ndarray:
    """Apply cyclic time shift by k samples along time axis."""
    return np.roll(x, k, axis=1).astype(np.float32)


def plot_iq(ax: plt.Axes, x: np.ndarray, title: str) -> None:
    t = np.arange(x.shape[1])
    ax.plot(t, x[0], color="#2171B5", linestyle="-", linewidth=1.2, label="I")
    ax.plot(t, x[1], color="#F16913", linestyle="--", linewidth=1.2, label="Q")
    ax.set_xlim(0, 127)
    ax.set_xlabel("Sample index", fontsize=9)
    ax.set_ylabel("Amplitude", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.xaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)
    ax.yaxis.grid(True, linestyle=":", linewidth=0.5, alpha=0.6)


def main() -> int:
    x = load_sample()

    x_rot = apply_phase_rotation(x, THETA)
    x_shift = apply_cyclic_shift(x, CYCLIC_SHIFT)
    x_both = apply_cyclic_shift(apply_phase_rotation(x, THETA), CYCLIC_SHIFT)

    fig, axes = plt.subplots(2, 2, figsize=(11, 6))
    fig.suptitle(
        f"Augmentation Visualization: QPSK @ +{TARGET_SNR} dB (sample index {SAMPLE_INDEX})\n"
        f"Blue=I (solid), Orange=Q (dashed)",
        fontsize=11,
    )

    plot_iq(axes[0][0], x, "(a) Original")
    plot_iq(axes[0][1], x_rot, rf"(b) Phase rotation $\theta=\pi/3$")
    plot_iq(axes[1][0], x_shift, f"(c) Cyclic shift k=+{CYCLIC_SHIFT}")
    plot_iq(axes[1][1], x_both, rf"(d) Both: $\theta=\pi/3$ + shift k=+{CYCLIC_SHIFT}")

    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = FIGURES_DIR / "fig23_augmentation_visualization.pdf"
    png_path = FIGURES_DIR / "fig23_augmentation_visualization.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
