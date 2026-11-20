"""
src/huim_fpgrowth.py
High Utility Itemset Mining (HUIM) algorithm using UP-Growth / IHUP-TWU.
Pure Python two-phase implementation with tree-based candidate generation
and inverted-index exact utility verification.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from src.loader import UtilityDatabase
from src.up_tree import HeaderEntry, UPTree


@dataclass
class HighUtilityItemset:
    """Represents a verified High Utility Itemset (HUI)."""
    pattern: List[int]
    pattern_names: List[str]
    length: int
    support_count: int
    support_pct: float
    exact_utility: float
    utility_share_pct: float
    avg_utility_per_tx: float

    def to_dict(self) -> dict:
        return {
            "pattern": self.pattern,
            "pattern_names": self.pattern_names,
            "length": self.length,
            "support_count": self.support_count,
            "support_pct": round(self.support_pct, 4),
            "exact_utility": round(self.exact_utility, 2),
            "utility_share_pct": round(self.utility_share_pct, 4),
            "avg_utility_per_tx": round(self.avg_utility_per_tx, 2),
        }


@dataclass
class MiningDiagnostics:
    """Performance metrics and pruning statistics for a mining execution."""
    phase1_candidates_count: int
    phase2_verified_count: int
    pruning_efficiency_pct: float
    phase1_ms: float
    phase2_ms: float
    total_ms: float
    promising_items_count: int
    total_items_count: int
    min_utility: float
    threshold_mode: str
    threshold_value: float

    def to_dict(self) -> dict:
        return {
            "phase1_candidates_count": self.phase1_candidates_count,
            "phase2_verified_count": self.phase2_verified_count,
            "pruning_efficiency_pct": round(self.pruning_efficiency_pct, 2),
            "phase1_ms": round(self.phase1_ms, 2),
            "phase2_ms": round(self.phase2_ms, 2),
            "total_ms": round(self.total_ms, 2),
            "promising_items_count": self.promising_items_count,
            "total_items_count": self.total_items_count,
            "min_utility": round(self.min_utility, 2),
            "threshold_mode": self.threshold_mode,
            "threshold_value": self.threshold_value,
        }


@dataclass
class MiningResult:
    """Overall result of a HUIM execution."""
    huis: List[HighUtilityItemset]
    diagnostics: MiningDiagnostics


def mine_high_utility_patterns(
    database: UtilityDatabase,
    min_utility: float,
    max_len: Optional[int] = 4,
    threshold_mode: str = "absolute",
    threshold_input_value: Optional[float] = None,
) -> MiningResult:
    """
    Executes the two-phase UP-Growth / IHUP-TWU algorithm on the utility database.

    Phase 1:
        1. Compute TWU for all items.
        2. Prune unpromising items (TWU < min_utility) via TWU Downward Closure.
        3. Sort promising items descending by TWU.
        4. Reorganize transactions and construct UP-Tree.
        5. Recursive conditional UP-Tree mining to yield Potential High Utility Itemsets (PHUIs).

    Phase 2:
        Exact utility verification using inverted index TID intersections.
    """
    total_start = time.perf_counter()

    # ---------------------------------------------------------
    # Step 1: TWU Calculation & Pruning
    # ---------------------------------------------------------
    twus = database.compute_twus()
    total_items_count = len(database.item_names)

    promising_items = [
        item_id for item_id, twu in twus.items() if twu >= min_utility
    ]
    # Sort promising items in descending order of TWU, breaking ties consistently
    promising_items.sort(key=lambda item_id: (-twus[item_id], item_id))
    rank_map: Dict[int, int] = {
        item_id: rank for rank, item_id in enumerate(promising_items)
    }
    promising_set = set(promising_items)

    # ---------------------------------------------------------
    # Step 2: UP-Tree Construction
    # ---------------------------------------------------------
    tree = UPTree(rank_map=rank_map)
    for item_id in promising_items:
        tree.header_table[item_id] = HeaderEntry(item_id=item_id, twu=twus[item_id])

    for tx in database.transactions:
        # Reorganize transaction: keep promising items sorted by TWU rank
        reorganized = [i for i in tx if i in promising_set]
        if not reorganized:
            continue
        reorganized.sort(key=lambda i: rank_map[i])

        # RTU: sum of utilities of the remaining promising items in transaction
        rtu = sum(tx[i] for i in reorganized)
        tree.insert(reorganized, utility=rtu, count=1)

    # ---------------------------------------------------------
    # Step 3: Phase 1 - Recursive Conditional UP-Tree Mining
    # ---------------------------------------------------------
    phase1_start = time.perf_counter()
    phuis: Set[Tuple[int, ...]] = set()

    _mine_conditional_up_tree(
        tree=tree,
        prefix=[],
        min_utility=min_utility,
        max_len=max_len,
        phuis=phuis,
    )
    phase1_end = time.perf_counter()
    phase1_ms = (phase1_end - phase1_start) * 1000.0

    # ---------------------------------------------------------
    # Step 4: Phase 2 - Exact Utility Verification
    # ---------------------------------------------------------
    phase2_start = time.perf_counter()
    verified_huis: List[HighUtilityItemset] = []

    total_tx_count = database.num_transactions
    total_db_utility = database.total_utility if database.total_utility > 0 else 1.0

    for phui in phuis:
        # Collect TID sets
        tid_sets = [
            database.inverted_index[iid]
            for iid in phui
            if iid in database.inverted_index
        ]
        if len(tid_sets) < len(phui):
            continue

        # Intersect smallest sets first for speed
        tid_sets.sort(key=len)
        common_tids = set.intersection(*tid_sets)
        if not common_tids:
            continue

        support_count = len(common_tids)
        exact_utility = sum(
            sum(database.transactions[tid][iid] for iid in phui)
            for tid in common_tids
        )

        if exact_utility >= min_utility:
            support_pct = (support_count / total_tx_count) * 100.0 if total_tx_count > 0 else 0.0
            utility_share_pct = (exact_utility / total_db_utility) * 100.0
            avg_utility_per_tx = exact_utility / support_count if support_count > 0 else 0.0

            verified_huis.append(
                HighUtilityItemset(
                    pattern=list(phui),
                    pattern_names=[database.get_item_name(iid) for iid in phui],
                    length=len(phui),
                    support_count=support_count,
                    support_pct=support_pct,
                    exact_utility=exact_utility,
                    utility_share_pct=utility_share_pct,
                    avg_utility_per_tx=avg_utility_per_tx,
                )
            )

    # Sort verified HUIs by exact utility descending
    verified_huis.sort(key=lambda hui: (-hui.exact_utility, -hui.support_count))

    phase2_end = time.perf_counter()
    phase2_ms = (phase2_end - phase2_start) * 1000.0
    total_ms = (phase2_end - total_start) * 1000.0

    candidates_count = len(phuis)
    verified_count = len(verified_huis)
    pruning_efficiency = (
        ((candidates_count - verified_count) / candidates_count * 100.0)
        if candidates_count > 0
        else 0.0
    )

    diagnostics = MiningDiagnostics(
        phase1_candidates_count=candidates_count,
        phase2_verified_count=verified_count,
        pruning_efficiency_pct=pruning_efficiency,
        phase1_ms=phase1_ms,
        phase2_ms=phase2_ms,
        total_ms=total_ms,
        promising_items_count=len(promising_items),
        total_items_count=total_items_count,
        min_utility=min_utility,
        threshold_mode=threshold_mode,
        threshold_value=threshold_input_value if threshold_input_value is not None else min_utility,
    )

    return MiningResult(huis=verified_huis, diagnostics=diagnostics)


def _mine_conditional_up_tree(
    tree: UPTree,
    prefix: List[int],
    min_utility: float,
    max_len: Optional[int],
    phuis: Set[Tuple[int, ...]],
) -> None:
    """
    Bottom-up traversal of the HeaderTable to recursively discover PHUIs.
    """
    # Sort items bottom-up (reverse rank order: lowest TWU to highest TWU)
    items_bottom_up = sorted(
        tree.header_table.keys(),
        key=lambda item_id: tree.rank_map.get(item_id, 0),
        reverse=True,
    )

    for item in items_bottom_up:
        total_utility, prefix_paths = tree.get_prefix_paths(item)
        candidate = prefix + [item]

        if total_utility >= min_utility:
            phuis.add(tuple(sorted(candidate)))

        # Prune search space if maximum length reached
        if max_len is not None and len(candidate) >= max_len:
            continue

        if not prefix_paths:
            continue

        # Accumulate path utilities for each ancestor item in prefix paths
        cond_item_utils: Dict[int, float] = defaultdict(float)
        for path, util, count in prefix_paths:
            for anc in path:
                cond_item_utils[anc] += util

        # Promising ancestors satisfying min_utility
        promising_ancestors = {
            anc for anc, u in cond_item_utils.items() if u >= min_utility
        }
        if not promising_ancestors:
            continue

        # Construct conditional UP-Tree
        cond_tree = UPTree(rank_map=tree.rank_map)
        for anc in promising_ancestors:
            cond_tree.header_table[anc] = HeaderEntry(
                item_id=anc, twu=cond_item_utils[anc]
            )

        for path, util, count in prefix_paths:
            filtered_path = [anc for anc in path if anc in promising_ancestors]
            if filtered_path:
                cond_tree.insert(filtered_path, utility=util, count=count)

        # Recurse with extended prefix
        _mine_conditional_up_tree(
            tree=cond_tree,
            prefix=candidate,
            min_utility=min_utility,
            max_len=max_len,
            phuis=phuis,
        )
