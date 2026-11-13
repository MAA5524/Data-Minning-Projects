"""Association rule generator for frequent itemsets.

Extracts candidate rules X -> Y from frequent itemsets of length >= 2,
calculates support, confidence, and antecedent/consequent marginals,
and filters by minimum confidence threshold.
"""

from __future__ import annotations

import itertools
from typing import Any


def generate_association_rules(
    frequent_itemsets: dict[frozenset[str], int],
    total_transactions: int,
    minconf: float,
) -> list[dict[str, Any]]:
    """Generate association rules from frequent itemsets.

    Parameters
    ----------
    frequent_itemsets : dict[frozenset[str], int]
        Mapping from frequent itemsets to their absolute support counts.
    total_transactions : int
        Total number of transactions in dataset (N).
    minconf : float
        Minimum confidence threshold. Supports both 0 < minconf <= 1 and
        percentage 1 < minconf <= 100.

    Returns
    -------
    list[dict[str, Any]]
        List of generated valid rules meeting the minconf threshold.
    """
    if total_transactions <= 0 or not frequent_itemsets:
        return []

    # Normalize percentage threshold to [0.0, 1.0]
    if minconf > 1.0:
        minconf = minconf / 100.0

    if minconf < 0:
        minconf = 0.0

    rules: list[dict[str, Any]] = []

    for itemset, sup_count_XY in frequent_itemsets.items():
        k = len(itemset)
        if k < 2:
            continue

        item_list = sorted(list(itemset))
        s_XY = sup_count_XY / total_transactions

        # Generate all non-empty proper subsets X
        for r in range(1, k):
            for subset in itertools.combinations(item_list, r):
                X = frozenset(subset)
                Y = itemset - X

                sup_count_X = frequent_itemsets.get(X)
                sup_count_Y = frequent_itemsets.get(Y)

                # Skip if support of antecedent is missing or zero
                if not sup_count_X:
                    continue

                confidence = sup_count_XY / sup_count_X

                if confidence >= minconf:
                    s_X = sup_count_X / total_transactions
                    s_Y = (sup_count_Y / total_transactions) if sup_count_Y else 0.0

                    antecedent_str = ", ".join(sorted(X))
                    consequent_str = ", ".join(sorted(Y))
                    rule_str = f"{{{antecedent_str}}} ➔ {{{consequent_str}}}"

                    rules.append(
                        {
                            "antecedent": X,
                            "consequent": Y,
                            "antecedent_str": antecedent_str,
                            "consequent_str": consequent_str,
                            "rule_str": rule_str,
                            "support_count": sup_count_XY,
                            "support": s_XY,
                            "confidence": confidence,
                            "sup_X": sup_count_X,
                            "sup_Y": sup_count_Y or 0,
                            "s_X": s_X,
                            "s_Y": s_Y,
                        }
                    )

    return rules
