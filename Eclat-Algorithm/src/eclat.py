"""Pure Eclat (Equivalence Class Transformation) Algorithm.

Uses Vertical Data Format (item -> TID set) and Depth-First Search (DFS)
over prefix-based equivalence classes.
"""

from __future__ import annotations

import math
from typing import Optional


def eclat(
    tid_lists: dict[str, set[int]],
    total_transactions: int,
    minsup: float | int,
    max_len: Optional[int] = None,
) -> dict[frozenset[str], int]:
    """Mine frequent itemsets using pure Eclat with vertical TID-set intersections.

    Parameters
    ----------
    tid_lists : dict[str, set[int]]
        Mapping from item to the set of Transaction IDs (TIDs) containing it.
    total_transactions : int
        Total number of transactions in the dataset (N).
    minsup : float | int
        Minimum support threshold. If 0 < minsup < 1.0, treated as relative support
        and converted to ceil(minsup * total_transactions). If minsup >= 1, treated
        as absolute support count.
    max_len : int, optional
        Maximum length of frequent itemsets to mine. Default is None (unconstrained).

    Returns
    -------
    dict[frozenset[str], int]
        Mapping from frequent itemset (frozenset of item names) to its absolute support count,
        sorted by support count descending, then itemset length, then item names.
    """
    if total_transactions <= 0 or not tid_lists:
        return {}

    # Calculate absolute minimum support count
    if 0 < minsup < 1.0:
        min_sup_count = math.ceil(minsup * total_transactions)
    elif minsup >= 1:
        min_sup_count = int(minsup)
    else:
        raise ValueError(f"minsup must be positive, got {minsup}")

    if min_sup_count > total_transactions:
        return {}

    # 1. Prune infrequent 1-itemsets
    frequent_1_items: list[tuple[str, set[int]]] = []
    frequent_itemsets: dict[frozenset[str], int] = {}

    for item, tids in tid_lists.items():
        if len(tids) >= min_sup_count:
            frequent_1_items.append((item, tids))
            frequent_itemsets[frozenset([item])] = len(tids)

    if not frequent_1_items or (max_len is not None and max_len < 1):
        return {}

    # Deterministic sorting: highest support first, then alphabetical
    frequent_1_items.sort(key=lambda x: (-len(x[1]), x[0]))

    # If max_len is 1, return 1-itemsets only
    if max_len == 1:
        return dict(
            sorted(
                frequent_itemsets.items(),
                key=lambda x: (-x[1], len(x[0]), sorted(x[0])),
            )
        )

    # 2. Depth-First Search (DFS) over Equivalence Classes
    def _dfs(
        prefix_items: list[tuple[str, set[int]]],
        current_prefix: tuple[str, ...],
    ) -> None:
        """Recursive DFS intersection of TID sets within the prefix equivalence class."""
        n_candidates = len(prefix_items)
        for i in range(n_candidates):
            item_i, tid_set_i = prefix_items[i]
            new_prefix = current_prefix + (item_i,)
            suffix_candidates: list[tuple[str, set[int]]] = []

            for j in range(i + 1, n_candidates):
                item_j, tid_set_j = prefix_items[j]

                # Core Eclat operation: Set Intersection of TIDs
                intersected_tids = tid_set_i & tid_set_j

                if len(intersected_tids) >= min_sup_count:
                    combined_itemset = frozenset(new_prefix + (item_j,))
                    frequent_itemsets[combined_itemset] = len(intersected_tids)

                    # Continue extending if max_len allows
                    if max_len is None or len(combined_itemset) < max_len:
                        suffix_candidates.append((item_j, intersected_tids))

            if suffix_candidates:
                _dfs(suffix_candidates, new_prefix)

    # Start DFS from 1-itemsets
    _dfs(frequent_1_items, ())

    # Return cleanly sorted dictionary
    return dict(
        sorted(
            frequent_itemsets.items(),
            key=lambda x: (-x[1], len(x[0]), sorted(x[0])),
        )
    )
