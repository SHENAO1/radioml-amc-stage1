"""P1.3: build low-SNR-only confusion matrices from Stage 5A archived predictions.

Reads the 27 archived `predictions_test.csv` (9 models x 3 seeds) under
`paper_package/predictions_archive_20260508/`, filters `snr_db <= -6`, and
produces:

  - per-model 3-seed-aggregated normalized confusion-matrix PNG
  - per-model 3-seed-aggregated raw-count confusion-matrix PNG
  - per-model per-seed normalized panel (3x1 figure) for stability inspection
  - `confusion_low_snr_summary.csv`: compact per-class accuracy table
  - `confusion_low_snr_summary.md`: markdown digest with the largest off-diagonal
    confusions for each model

Outputs go to `results/paper_stage6/low_snr_confusion_extended/` to keep them
out of Stage 5A/5B aggregate directories. Stage 5A artifacts are not modified.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = REPO_ROOT / "paper_package" / "predictions_archive_20260508" / "results" / "paper_stage2" / "rml2016a"
OUTPUT_DIR = REPO_ROOT / "results" / "paper_stage6" / "low_snr_confusion_extended"

MODELS = [
    "cnn1d",
    "resnet1d",
    "tfcnn_stft",
    "fusion_iq_stft",
    "cldnn",
    "mcldnn",
    "lwamcnet",
    "iq_param_matched",
    "gated_fusion_iq_stft",
]
SEEDS = [42, 2025, 3407]
LOW_SNR_THRESHOLD_DB = -6
CLASSES = [
    "8PSK", "AM-DSB", "AM-SSB", "BPSK", "CPFSK",
    "GFSK", "PAM4", "QAM16", "QAM64", "QPSK", "WBFM",
]
LABEL_TO_NAME = dict(enumerate(CLASSES))


def load_low_snr(model: str, seed: int) -> pd.DataFrame:
    csv = ARCHIVE / model / f"seed_{seed}" / "predictions_test.csv"
    df = pd.read_csv(csv, usecols=["sample_id", "snr_db", "modulation", "y_true", "y_pred"])
    return df[df["snr_db"] <= LOW_SNR_THRESHOLD_DB].copy()


def confusion_counts(df: pd.DataFrame) -> np.ndarray:
    n = len(CLASSES)
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(df["y_true"].to_numpy(), df["y_pred"].to_numpy()):
        cm[int(t), int(p)] += 1
    return cm


def plot_confusion(cm: np.ndarray, title: str, out_png: Path, normalize: bool, vmin: float | None = None, vmax: float | None = None) -> None:
    n = cm.shape[0]
    if normalize:
        row_sum = cm.sum(axis=1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            data = np.where(row_sum > 0, cm / np.maximum(row_sum, 1), 0.0)
        fmt = ".2f"
        cmap = "Blues"
    else:
        data = cm.astype(float)
        fmt = "d"
        cmap = "Blues"

    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    im = ax.imshow(data, cmap=cmap, vmin=vmin if vmin is not None else 0.0, vmax=vmax if vmax is not None else (data.max() if data.size else 1.0))
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(CLASSES, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(CLASSES, fontsize=9)
    ax.set_xlabel("Predicted", fontsize=10)
    ax.set_ylabel("True", fontsize=10)
    ax.set_title(title, fontsize=11)
    threshold = data.max() / 2.0 if data.size else 0.5
    for i in range(n):
        for j in range(n):
            value = data[i, j]
            if normalize:
                text = f"{value:.2f}" if value >= 0.01 else ""
            else:
                text = f"{int(value)}" if value > 0 else ""
            if text:
                color = "white" if value > threshold else "black"
                ax.text(j, i, text, ha="center", va="center", color=color, fontsize=7)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)


def per_seed_panel(cms: dict[int, np.ndarray], model: str, out_png: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))
    for ax, seed in zip(axes, SEEDS):
        cm = cms[seed]
        row_sum = cm.sum(axis=1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            data = np.where(row_sum > 0, cm / np.maximum(row_sum, 1), 0.0)
        im = ax.imshow(data, cmap="Blues", vmin=0.0, vmax=1.0)
        ax.set_xticks(range(len(CLASSES)))
        ax.set_yticks(range(len(CLASSES)))
        ax.set_xticklabels(CLASSES, rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(CLASSES, fontsize=8)
        ax.set_title(f"{model} seed {seed} (low-SNR <= {LOW_SNR_THRESHOLD_DB} dB)", fontsize=10)
        ax.set_xlabel("Predicted", fontsize=9)
        ax.set_ylabel("True", fontsize=9)
    fig.colorbar(im, ax=axes, fraction=0.02, pad=0.02)
    fig.suptitle(f"{model} per-seed low-SNR confusion (row-normalized)", fontsize=12)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)


def per_class_accuracy(cm: np.ndarray) -> np.ndarray:
    diag = np.diag(cm).astype(float)
    row_sum = cm.sum(axis=1).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(row_sum > 0, diag / row_sum, np.nan)


def biggest_offdiagonals(cm: np.ndarray, top_k: int = 5) -> list[tuple[str, str, int, float]]:
    """Return the top-k largest off-diagonal cells as (true, predicted, count, fraction-of-row)."""
    row_sum = cm.sum(axis=1)
    items: list[tuple[str, str, int, float]] = []
    n = cm.shape[0]
    for i in range(n):
        if row_sum[i] == 0:
            continue
        for j in range(n):
            if i == j:
                continue
            count = int(cm[i, j])
            if count == 0:
                continue
            frac = count / row_sum[i]
            items.append((CLASSES[i], CLASSES[j], count, frac))
    items.sort(key=lambda t: -t[3])
    return items[:top_k]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, float | str | int]] = []
    digest_lines: list[str] = ["# Low-SNR (snr_db <= -6 dB) Confusion Matrix Summary",
                                "",
                                f"Source: `paper_package/predictions_archive_20260508/` (Stage 5A predictions, 9 models x 3 seeds).",
                                f"Threshold: snr_db <= {LOW_SNR_THRESHOLD_DB} dB.",
                                f"Output dir: `{output_dir.relative_to(REPO_ROOT).as_posix()}/`",
                                "",
                                "Stage 5A predictions are read-only inputs; this artifact set is reported under the same `PROJECT_SUPPORTED` evidence label as its parent predictions but is stored outside the Stage 5A/5B aggregate roots to avoid implying any rewrite.",
                                "",
                                "## Per-model low-SNR per-class accuracy",
                                "",
                                "Aggregated over the three Stage 5A seeds.",
                                "",
                                "| Model | low_n | overall low-SNR acc |"
                                + "".join([f" {c} |" for c in CLASSES]),
                                "|---|---:|---:|" + "---:|" * len(CLASSES)]

    for model in MODELS:
        cms_per_seed: dict[int, np.ndarray] = {}
        agg = np.zeros((len(CLASSES), len(CLASSES)), dtype=np.int64)
        total_n = 0
        for seed in SEEDS:
            df = load_low_snr(model, seed)
            cm = confusion_counts(df)
            cms_per_seed[seed] = cm
            agg += cm
            total_n += len(df)

        plot_confusion(
            agg,
            title=f"{model} low-SNR confusion (snr_db <= {LOW_SNR_THRESHOLD_DB} dB, 3 seeds aggregated)",
            out_png=output_dir / f"confusion_low_snr_{model}_normalized.png",
            normalize=True,
            vmin=0.0,
            vmax=1.0,
        )
        plot_confusion(
            agg,
            title=f"{model} low-SNR confusion (raw counts, 3 seeds aggregated)",
            out_png=output_dir / f"confusion_low_snr_{model}_counts.png",
            normalize=False,
        )
        per_seed_panel(cms_per_seed, model, output_dir / f"confusion_low_snr_{model}_per_seed.png")

        per_class = per_class_accuracy(agg)
        diag_total = float(np.diag(agg).sum())
        overall_total = float(agg.sum())
        overall_acc = (diag_total / overall_total) if overall_total > 0 else float("nan")

        row = {
            "model": model,
            "low_snr_samples": int(overall_total),
            "low_snr_overall_acc": overall_acc,
        }
        for c, v in zip(CLASSES, per_class):
            row[c] = v
        summary_rows.append(row)

        cells = [
            f"| {model} | {int(overall_total)} | {overall_acc:.4f} |",
        ]
        for v in per_class:
            cells.append(f" {'NaN' if np.isnan(v) else f'{v:.3f}'} |")
        digest_lines.append("".join(cells))

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(output_dir / "confusion_low_snr_summary.csv", index=False)

    digest_lines.extend(["", "## Largest off-diagonal patterns per model (top-5 fraction-of-row)", ""])
    for row, model in zip(summary_rows, MODELS):
        digest_lines.append(f"### {model}")
        digest_lines.append("")
        digest_lines.append("| true | predicted | count | fraction-of-row |")
        digest_lines.append("|---|---|---:|---:|")
        agg = np.zeros((len(CLASSES), len(CLASSES)), dtype=np.int64)
        for seed in SEEDS:
            df = load_low_snr(model, seed)
            agg += confusion_counts(df)
        for true_c, pred_c, cnt, frac in biggest_offdiagonals(agg, top_k=5):
            digest_lines.append(f"| {true_c} | {pred_c} | {cnt} | {frac:.3f} |")
        digest_lines.append("")

    (output_dir / "confusion_low_snr_summary.md").write_text("\n".join(digest_lines), encoding="utf-8")

    print("done. outputs:")
    for f in sorted(output_dir.iterdir()):
        size_kb = f.stat().st_size / 1024
        print(f"  {f.relative_to(REPO_ROOT).as_posix()}  ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
