"""Pattern evaluation metrics for association rules.

Implements two key measures taught in Chapter 4 of 'Data Mining: Concepts and Techniques'
(Han, Pei, Tong):
1. Lift (Traditional Non-Null-Invariant)
2. Kulczynski (Modern Null-Invariant)
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def lift(s_XY: float, s_X: float, s_Y: float) -> float:
    """Calculate Lift (Non-Null-Invariant).

    Formula: s(X ∪ Y) / (s(X) * s(Y))
    Baseline: 1.0 (independence)
    Range: [0, ∞)
    """
    denom = s_X * s_Y
    if denom <= 0:
        return 0.0
    return s_XY / denom


def kulczynski(s_XY: float, s_X: float, s_Y: float) -> float:
    """Calculate Kulczynski (Null-Invariant).

    Formula: 0.5 * (s(X ∪ Y) / s(X) + s(X ∪ Y) / s(Y))
             = 0.5 * (c(X -> Y) + c(Y -> X))
    Baseline: 0.5 (independence)
    Range: [0, 1]
    """
    if s_X <= 0 or s_Y <= 0:
        return 0.0
    return 0.5 * ((s_XY / s_X) + (s_XY / s_Y))


METRIC_METADATA = {
    "Lift": {
        "name": "Lift",
        "symbol": "Lift(X, Y)",
        "null_invariant": False,
        "range": "[0, ∞)",
        "baseline": 1.0,
        "formula_latex": r"\text{Lift}(X, Y) = \frac{s(X \cup Y)}{s(X) \times s(Y)}",
        "description": (
            "Measures how much more often X and Y occur together than expected under independence. "
            "Values > 1.0 imply positive correlation; values < 1.0 imply negative correlation; "
            "value = 1.0 implies statistical independence. "
            "WARNING: Not null-invariant; heavily influenced by the number of null-transactions."
        ),
    },
    "Kulczynski": {
        "name": "Kulczynski",
        "symbol": "Kulc(X, Y)",
        "null_invariant": True,
        "range": "[0, 1]",
        "baseline": 0.5,
        "formula_latex": r"\text{Kulc}(X, Y) = \frac{1}{2} \left( \frac{s(X \cup Y)}{s(X)} + \frac{s(X \cup Y)}{s(Y)} \right)",
        "description": (
            "Arithmetic mean of the two conditional probabilities P(Y|X) and P(X|Y). "
            "Values > 0.5 imply positive correlation; values < 0.5 imply negative correlation; "
            "value = 0.5 implies neutral/independence. "
            "PRO: Null-invariant; unaffected by transactions that contain neither X nor Y."
        ),
    },
}


def evaluate_rules(rules: list[dict[str, Any]]) -> pd.DataFrame:
    """Augment generated rules with Lift and Kulczynski metrics.

    Parameters
    ----------
    rules : list[dict[str, Any]]
        List of rule dictionaries produced by `generate_association_rules`.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        ['rule_str', 'antecedent_str', 'consequent_str', 'support', 'support_count',
         'confidence', 'lift', 'kulczynski', 'antecedent', 'consequent']
    """
    if not rules:
        return pd.DataFrame(
            columns=[
                "rule_str",
                "antecedent_str",
                "consequent_str",
                "support",
                "support_count",
                "confidence",
                "lift",
                "kulczynski",
                "antecedent",
                "consequent",
            ]
        )

    records: list[dict[str, Any]] = []
    for r in rules:
        s_XY = r["support"]
        s_X = r["s_X"]
        s_Y = r["s_Y"]

        rule_lift = lift(s_XY, s_X, s_Y)
        rule_kulc = kulczynski(s_XY, s_X, s_Y)

        records.append(
            {
                "rule_str": r["rule_str"],
                "antecedent_str": r["antecedent_str"],
                "consequent_str": r["consequent_str"],
                "support": s_XY,
                "support_count": r["support_count"],
                "confidence": r["confidence"],
                "lift": rule_lift,
                "kulczynski": rule_kulc,
                "antecedent": r["antecedent"],
                "consequent": r["consequent"],
                "s_X": s_X,
                "s_Y": s_Y,
            }
        )

    df = pd.DataFrame(records)
    # Sort by confidence descending, then lift descending
    df = df.sort_values(by=["confidence", "lift", "support"], ascending=[False, False, False]).reset_index(drop=True)
    return df
