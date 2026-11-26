"""Pure-Python Gini Index Impurity Engine (Han, Pei, Tong - Chapter 6)."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence


def gini_impurity(labels: Sequence[str]) -> float:
    """Compute Gini(D) = 1 - sum(p_j^2) for a sequence of class labels."""
    total = len(labels)
    if total == 0:
        return 0.0
    counts = Counter(labels)
    sum_sq = sum((count / total) ** 2 for count in counts.values())
    return max(0.0, 1.0 - sum_sq)


def weighted_gini_split(
    partitions: Mapping[Any, Sequence[str]] | Iterable[Sequence[str]],
) -> float:
    """Compute Gini_A(D) = sum((|D_v| / |D|) * Gini(D_v)) across partitions."""
    groups = list(partitions.values()) if isinstance(partitions, Mapping) else list(partitions)
    total = sum(len(group) for group in groups)
    if total == 0:
        return 0.0
    return sum((len(group) / total) * gini_impurity(group) for group in groups if group)


def delta_gini(
    rows: Sequence[Mapping[str, str]],
    attribute: str,
    target_column: str,
) -> tuple[float, float, float]:
    """Return (Gini(D), Gini_A(D), DeltaGini(A)) for a candidate discrete attribute."""
    if not rows:
        return 0.0, 0.0, 0.0

    parent_labels = [row[target_column] for row in rows]
    parent_gini = gini_impurity(parent_labels)

    label_partitions: dict[str, list[str]] = {}
    for row in rows:
        val = row[attribute]
        label_partitions.setdefault(val, []).append(row[target_column])

    gini_a = weighted_gini_split(label_partitions)
    reduction = max(0.0, parent_gini - gini_a)
    return parent_gini, gini_a, reduction


def best_gini_split(
    rows: Sequence[Mapping[str, str]],
    attributes: Sequence[str],
    target_column: str,
) -> dict[str, Any]:
    """Select the attribute minimizing Gini_A(D) (maximizing DeltaGini(A))."""
    if not rows or not attributes:
        raise ValueError("Cannot evaluate Gini split on empty rows or empty attribute list.")

    parent_gini = gini_impurity([row[target_column] for row in rows])
    best_attr: str | None = None
    best_gini_a = float("inf")
    best_delta = -1.0
    best_partitions: dict[str, list[dict[str, str]]] = {}
    attribute_scores: dict[str, dict[str, float]] = {}

    for attr in attributes:
        row_partitions: dict[str, list[dict[str, str]]] = {}
        label_partitions: dict[str, list[str]] = {}
        for row in rows:
            val = row[attr]
            row_partitions.setdefault(val, []).append(dict(row))
            label_partitions.setdefault(val, []).append(row[target_column])

        gini_a = weighted_gini_split(label_partitions)
        reduction = max(0.0, parent_gini - gini_a)
        attribute_scores[attr] = {
            "gini_a": gini_a,
            "delta_gini": reduction,
        }

        if gini_a < best_gini_a - 1e-12:
            best_gini_a = gini_a
            best_delta = reduction
            best_attr = attr
            best_partitions = row_partitions

    assert best_attr is not None
    return {
        "best_attribute": best_attr,
        "parent_gini": parent_gini,
        "best_gini_a": best_gini_a,
        "best_delta_gini": max(0.0, best_delta),
        "partitions": best_partitions,
        "scores": attribute_scores,
    }
