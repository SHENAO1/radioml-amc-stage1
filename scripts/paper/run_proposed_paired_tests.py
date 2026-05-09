"""Paired bootstrap + McNemar tests for the proposed model evaluation.

Compares (per the audit register) on RTX 3090, same fixed split, same 3 seeds:
  - proposed (fusion_cldnn_stft + aug + LS)  vs  P1.1 fusion_iq_stft (matched schedule, weak backbone)
  - proposed                                  vs  ablation arch_only
  - proposed                                  vs  ablation arch_aug
  - proposed                                  vs  ablation arch_ls

Predictions are paired by (split_id, train_seed, sample_id). For each pair we
report:
  - paired-bootstrap accuracy delta with 95% CI (10000 resamples, seed 42)
  - McNemar test (with continuity correction), discordant counts (b, c) and p-value

Output: results/paper_stage6/proposed_paired_tests/
  paired_bootstrap.csv
  mcnemar.csv
  summary.md
"""
from __future__ import annotations

import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_predictions(model_root: Path, seeds: Iterable[int]) -> pd.DataFrame:
    """Load predictions across seeds from <model_root>/seed_<seed>/predictions_test.csv."""
    parts = []
    for s in seeds:
        p = model_root / f"seed_{s}" / "predictions_test.csv"
        if not p.exists():
            raise FileNotFoundError(p)
        df = pd.read_csv(p, usecols=["sample_id", "split_id", "train_seed", "snr_db", "y_true", "y_pred", "correct"])
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


def paired_bootstrap_delta(correct_a: np.ndarray, correct_b: np.ndarray,
                           n_resamples: int = 10000, seed: int = 42) -> tuple[float, float, float, bool]:
    """Return (delta_mean, ci_low, ci_high, crosses_zero)."""
    rng = np.random.default_rng(seed)
    n = len(correct_a)
    idx_block = rng.integers(0, n, size=(n_resamples, n))
    a_means = correct_a[idx_block].mean(axis=1)
    b_means = correct_b[idx_block].mean(axis=1)
    deltas = a_means - b_means
    delta_mean = float(correct_a.mean() - correct_b.mean())
    ci_low, ci_high = float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))
    crosses_zero = ci_low <= 0.0 <= ci_high
    return delta_mean, ci_low, ci_high, crosses_zero


def mcnemar_with_correction(correct_a: np.ndarray, correct_b: np.ndarray) -> tuple[int, int, float]:
    """McNemar with chi-squared continuity correction. Returns (b, c, p_value)."""
    a_correct = correct_a.astype(bool)
    b_correct = correct_b.astype(bool)
    b = int(np.sum(a_correct & ~b_correct))
    c = int(np.sum(~a_correct & b_correct))
    if b + c == 0:
        return 0, 0, 1.0
    chi2 = (abs(b - c) - 1.0) ** 2 / (b + c)
    # 1-cdf chi2 with df=1 = exp(-chi2/2)
    p = math.exp(-chi2 / 2.0)
    return b, c, float(p)


def pair_predictions(df_a: pd.DataFrame, df_b: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Inner join on (split_id, train_seed, sample_id). Returns (correct_a, correct_b, joined_df)."""
    keys = ["split_id", "train_seed", "sample_id"]
    a = df_a[keys + ["correct", "snr_db"]].rename(columns={"correct": "correct_a"})
    b = df_b[keys + ["correct"]].rename(columns={"correct": "correct_b"})
    j = a.merge(b, on=keys, how="inner")
    if len(j) != len(df_a) or len(j) != len(df_b):
        print(f"!! warning: join size {len(j)} differs from a={len(df_a)} b={len(df_b)}", file=sys.stderr)
    return j["correct_a"].to_numpy(), j["correct_b"].to_numpy(), j


def compare_pair(label_a: str, df_a: pd.DataFrame, label_b: str, df_b: pd.DataFrame, scope: str = "overall") -> dict:
    if scope == "overall":
        a = df_a; b = df_b
    elif scope == "low_snr":
        a = df_a[df_a["snr_db"] <= -6]
        b = df_b[df_b["snr_db"] <= -6]
    else:
        raise ValueError(scope)
    ca, cb, _ = pair_predictions(a, b)
    delta, lo, hi, cz = paired_bootstrap_delta(ca, cb)
    bn, cn, pv = mcnemar_with_correction(ca, cb)
    return {
        "model_a": label_a, "model_b": label_b, "scope": scope,
        "n_pairs": len(ca),
        "delta_mean": delta, "ci_low": lo, "ci_high": hi, "crosses_zero": cz,
        "mcnemar_b": bn, "mcnemar_c": cn, "mcnemar_p": pv,
    }


def main() -> int:
    seeds = (42, 2025, 3407)
    proposed_root = REPO_ROOT / "results/paper_stage6/fusion_cldnn_stft_aug_ls_3090/rml2016a/fusion_cldnn_stft"
    p11_fusion_root = REPO_ROOT / "results/paper_stage6/extended_budget_3090/rml2016a/fusion_iq_stft"
    ablation_base = REPO_ROOT / "results/paper_stage6/fusion_cldnn_stft_ablation_3090/rml2016a"

    pairs = []
    print("loading proposed predictions ...", flush=True)
    proposed = load_predictions(proposed_root, seeds)
    print(f"  {len(proposed):,} rows", flush=True)

    print("loading P1.1 fusion_iq_stft predictions ...", flush=True)
    p11 = load_predictions(p11_fusion_root, seeds)
    print(f"  {len(p11):,} rows", flush=True)
    pairs.append(("proposed", proposed, "p11_fusion_iq_stft", p11))

    for variant in ("arch_only", "arch_aug", "arch_ls"):
        ab_root = ablation_base / variant / "fusion_cldnn_stft"
        if not (ab_root / "seed_42").exists():
            print(f"  variant {variant} not yet trained; skipping", flush=True)
            continue
        print(f"loading ablation variant {variant} ...", flush=True)
        ab = load_predictions(ab_root, seeds)
        print(f"  {len(ab):,} rows", flush=True)
        pairs.append(("proposed", proposed, f"ablation_{variant}", ab))

    rows: list[dict] = []
    for label_a, df_a, label_b, df_b in pairs:
        for scope in ("overall", "low_snr"):
            print(f"  pairing {label_a} vs {label_b} / {scope} ...", flush=True)
            rows.append(compare_pair(label_a, df_a, label_b, df_b, scope=scope))

    out_dir = REPO_ROOT / "results/paper_stage6/proposed_paired_tests"
    out_dir.mkdir(parents=True, exist_ok=True)

    bootstrap_csv = out_dir / "paired_bootstrap.csv"
    mcnemar_csv = out_dir / "mcnemar.csv"
    with open(bootstrap_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["model_a", "model_b", "scope", "n_pairs",
                                          "delta_mean", "ci_low", "ci_high", "crosses_zero"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})
    with open(mcnemar_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["model_a", "model_b", "scope", "n_pairs",
                                          "mcnemar_b", "mcnemar_c", "mcnemar_p"])
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    md_lines = [
        "# Proposed model paired statistical tests",
        "",
        "Same fixed split (`stratified_by_mod_snr_seed42`), same 3 train seeds (42/2025/3407),",
        "same RTX 3090 hardware. Predictions paired by (split_id, train_seed, sample_id).",
        "Bootstrap: 10000 resamples, seed=42. McNemar: chi-squared continuity correction.",
        "",
        "## Paired bootstrap accuracy delta (model_a − model_b)",
        "",
        "| model_a | model_b | scope | n | delta | 95% CI | crosses 0 |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for r in rows:
        md_lines.append(
            f"| {r['model_a']} | {r['model_b']} | {r['scope']} | {r['n_pairs']:,} | "
            f"{r['delta_mean']:+.4f} | [{r['ci_low']:+.4f}, {r['ci_high']:+.4f}] | "
            f"{'yes' if r['crosses_zero'] else '**no**'} |"
        )
    md_lines.extend([
        "",
        "## McNemar test (continuity-corrected, df=1)",
        "",
        "| model_a | model_b | scope | b (a✓ b✗) | c (a✗ b✓) | p |",
        "|---|---|---|---:|---:|---:|",
    ])
    for r in rows:
        md_lines.append(
            f"| {r['model_a']} | {r['model_b']} | {r['scope']} | {r['mcnemar_b']} | "
            f"{r['mcnemar_c']} | {r['mcnemar_p']:.3e} |"
        )
    (out_dir / "summary.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"wrote {bootstrap_csv}")
    print(f"wrote {mcnemar_csv}")
    print(f"wrote {out_dir / 'summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
