"""Comprehensive paired statistical tests across all Stage 6 experiments.

Runs McNemar's test and bootstrap confidence intervals for key pairwise
comparisons, using sample-level predictions from the same test split.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _bootstrap import PROJECT_ROOT  # noqa: E402

RESULTS_ROOT = PROJECT_ROOT / "results" / "paper_stage6"
SEEDS = [42, 2025, 3407]
OUTPUT_DIR = PROJECT_ROOT / "results" / "paper_stage6" / "paired_statistical_tests"


def load_predictions(experiment: str, model: str, seed: int) -> pd.DataFrame | None:
    """Load predictions_test.csv for a given run."""
    path = RESULTS_ROOT / experiment / "rml2016a" / model / f"seed_{seed}" / "predictions_test.csv"
    if not path.exists():
        print(f"  WARNING: missing {path}")
        return None
    return pd.read_csv(path)


def mcnemar_test(correct_a: np.ndarray, correct_b: np.ndarray) -> dict[str, Any]:
    """McNemar's test comparing two classifiers on the same samples."""
    b_wrong_a_right = np.sum((correct_a == 1) & (correct_b == 0))
    b_right_a_wrong = np.sum((correct_a == 0) & (correct_b == 1))
    n = b_wrong_a_right + b_right_a_wrong
    if n == 0:
        return {"statistic": 0.0, "p_value": 1.0, "n_discordant": 0, "a_wins": 0, "b_wins": 0}
    chi2 = (abs(b_wrong_a_right - b_right_a_wrong) - 1) ** 2 / n
    p_value = 1 - stats.chi2.cdf(chi2, df=1)
    return {
        "statistic": float(chi2),
        "p_value": float(p_value),
        "n_discordant": int(n),
        "a_wins": int(b_wrong_a_right),
        "b_wins": int(b_right_a_wrong),
    }


def bootstrap_delta(acc_a: np.ndarray, acc_b: np.ndarray, n_boot: int = 10000, seed: int = 42) -> dict[str, Any]:
    """Bootstrap CI for accuracy difference (A - B)."""
    rng = np.random.default_rng(seed)
    n = len(acc_a)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas.append(np.mean(acc_a[idx]) - np.mean(acc_b[idx]))
    deltas = np.array(deltas)
    return {
        "mean_delta": float(np.mean(deltas)),
        "ci_2.5": float(np.percentile(deltas, 2.5)),
        "ci_97.5": float(np.percentile(deltas, 97.5)),
        "ci_contains_zero": bool(np.percentile(deltas, 2.5) <= 0 <= np.percentile(deltas, 97.5)),
        "p_value_bootstrap": float(np.mean(deltas <= 0) if np.mean(deltas) > 0 else np.mean(deltas >= 0)),
    }


def per_snr_bootstrap(pred_a: pd.DataFrame, pred_b: pd.DataFrame, n_boot: int = 5000) -> dict[str, Any]:
    """Bootstrap delta per SNR bin."""
    results = {}
    for snr_val in sorted(pred_a["snr_db"].unique()):
        mask_a = pred_a["snr_db"] == snr_val
        mask_b = pred_b["snr_db"] == snr_val
        correct_a = (pred_a.loc[mask_a, "y_pred"].values == pred_a.loc[mask_a, "y_true"].values).astype(float)
        correct_b = (pred_b.loc[mask_b, "y_pred"].values == pred_b.loc[mask_b, "y_true"].values).astype(float)
        if len(correct_a) > 0 and len(correct_b) > 0:
            bt = bootstrap_delta(correct_a, correct_b, n_boot=n_boot)
            results[str(int(snr_val))] = bt
    return results


def run_comparison(
    name: str,
    exp_a: str, model_a: str,
    exp_b: str, model_b: str,
) -> dict[str, Any]:
    """Run full paired comparison between two models across all seeds."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"  A: {exp_a}/{model_a}  vs  B: {exp_b}/{model_b}")
    print(f"{'='*60}")

    seed_results = []
    for seed in SEEDS:
        pred_a = load_predictions(exp_a, model_a, seed)
        pred_b = load_predictions(exp_b, model_b, seed)
        if pred_a is None or pred_b is None:
            continue

        correct_a = (pred_a["y_pred"].values == pred_a["y_true"].values).astype(int)
        correct_b = (pred_b["y_pred"].values == pred_b["y_true"].values).astype(int)

        acc_a = float(np.mean(correct_a))
        acc_b = float(np.mean(correct_b))

        mcn = mcnemar_test(correct_a, correct_b)
        bt = bootstrap_delta(correct_a.astype(float), correct_b.astype(float))
        per_snr = per_snr_bootstrap(pred_a, pred_b)

        result = {
            "seed": seed,
            "acc_a": acc_a,
            "acc_b": acc_b,
            "delta_pp": (acc_a - acc_b) * 100,
            "mcnemar": mcn,
            "bootstrap": bt,
            "per_snr_bootstrap": per_snr,
        }
        seed_results.append(result)

        sig = "***" if mcn["p_value"] < 0.001 else "**" if mcn["p_value"] < 0.01 else "*" if mcn["p_value"] < 0.05 else "ns"
        print(f"  seed {seed}: A={acc_a:.4f} B={acc_b:.4f} delta={result['delta_pp']:+.2f}pp McNemar p={mcn['p_value']:.4f} {sig}")
        print(f"    Bootstrap 95% CI: [{bt['ci_2.5']*100:+.2f}, {bt['ci_97.5']*100:+.2f}] pp, contains_zero={bt['ci_contains_zero']}")

    comparison = {
        "name": name,
        "model_a": f"{exp_a}/{model_a}",
        "model_b": f"{exp_b}/{model_b}",
        "seeds": seed_results,
    }

    if seed_results:
        mean_delta = np.mean([r["delta_pp"] for r in seed_results])
        all_sig = all(r["mcnemar"]["p_value"] < 0.05 for r in seed_results)
        print(f"\n  SUMMARY: mean delta = {mean_delta:+.2f} pp, all seeds significant = {all_sig}")
        comparison["mean_delta_pp"] = float(mean_delta)
        comparison["all_seeds_significant"] = all_sig

    return comparison


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    comparisons = []

    # 1. CLDNN baseline vs CLDNN + aug
    comparisons.append(run_comparison(
        "CLDNN+aug vs CLDNN baseline (augmentation effect)",
        "cldnn_aug_ablation_3090", "cldnn",
        "extended_budget_3090", "cldnn",
    ))

    # 2. Proposed vs CLDNN baseline
    comparisons.append(run_comparison(
        "Proposed (fusion_cldnn_stft+aug+LS) vs CLDNN baseline",
        "fusion_cldnn_stft_aug_ls_3090", "fusion_cldnn_stft",
        "extended_budget_3090", "cldnn",
    ))

    # 3. Proposed vs CLDNN + aug (fusion-specific gain)
    comparisons.append(run_comparison(
        "Proposed vs CLDNN+aug (fusion-specific gain)",
        "fusion_cldnn_stft_aug_ls_3090", "fusion_cldnn_stft",
        "cldnn_aug_ablation_3090", "cldnn",
    ))

    # 4. CLDNN vs ResNet1D
    comparisons.append(run_comparison(
        "CLDNN vs ResNet1D (baseline ranking)",
        "extended_budget_3090", "cldnn",
        "extended_budget_3090", "resnet1d",
    ))

    # 5. CLDNN vs fusion_iq_stft (naive fusion)
    comparisons.append(run_comparison(
        "CLDNN vs fusion_iq_stft (naive fusion underperformance)",
        "extended_budget_3090", "cldnn",
        "extended_budget_3090", "fusion_iq_stft",
    ))

    # Save all results
    output_path = OUTPUT_DIR / "all_paired_tests.json"
    output_path.write_text(json.dumps(comparisons, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nAll results saved to: {output_path}")

    # Print summary table
    print(f"\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}")
    print(f"{'Comparison':<55} {'Mean Δ':>8} {'All sig':>8}")
    print(f"{'-'*55} {'-'*8} {'-'*8}")
    for c in comparisons:
        md = c.get("mean_delta_pp", float("nan"))
        sig = c.get("all_seeds_significant", False)
        print(f"{c['name']:<55} {md:>+7.2f}pp {'YES' if sig else 'NO':>8}")


if __name__ == "__main__":
    main()
