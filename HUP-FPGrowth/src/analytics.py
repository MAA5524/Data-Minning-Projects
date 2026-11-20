"""
src/analytics.py
Analytics, KPIs, chart data generation, and 'Hidden Gems' detection
for High Utility Itemset Mining (HUIM).
"""

from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional

from src.huim_fpgrowth import HighUtilityItemset, MiningResult
from src.loader import UtilityDatabase


def compute_analytics_summary(
    database: UtilityDatabase,
    mining_result: MiningResult,
) -> Dict[str, Any]:
    """
    Produces complete dashboard analytics, chart data, and hidden gems.
    """
    huis = mining_result.huis
    diag = mining_result.diagnostics

    # 1. Top Patterns Chart (Top 15 by exact utility)
    top_15 = huis[:15]
    top_patterns_chart = {
        "labels": [
            " + ".join(h.pattern_names) if len(h.pattern_names) <= 3
            else f"{h.pattern_names[0]} + {len(h.pattern_names)-1} items"
            for h in top_15
        ],
        "full_names": [" + ".join(h.pattern_names) for h in top_15],
        "utilities": [h.exact_utility for h in top_15],
        "supports": [h.support_count for h in top_15],
        "support_pcts": [h.support_pct for h in top_15],
    }

    # 2. Scatter Plot Data: Frequency (Support Count / Pct) vs. Exact Utility
    scatter_data = [
        {
            "x": round(h.support_pct, 3),
            "y": round(h.exact_utility, 2),
            "label": " + ".join(h.pattern_names),
            "length": h.length,
            "support_count": h.support_count,
            "avg_utility": round(h.avg_utility_per_tx, 2),
            "utility_share": round(h.utility_share_pct, 3),
        }
        for h in huis
    ]

    # 3. Pattern Length (k) Distribution
    length_counts: Dict[int, int] = {}
    length_utilities: Dict[int, float] = {}
    for h in huis:
        length_counts[h.length] = length_counts.get(h.length, 0) + 1
        length_utilities[h.length] = length_utilities.get(h.length, 0.0) + h.exact_utility

    all_k = sorted(length_counts.keys())
    k_distribution = {
        "labels": [f"k = {k}" for k in all_k],
        "counts": [length_counts[k] for k in all_k],
        "utilities": [round(length_utilities[k], 2) for k in all_k],
    }

    # 4. Pruning Funnel Stats
    pruning_funnel = {
        "total_items": diag.total_items_count,
        "promising_items": diag.promising_items_count,
        "twu_pruned_items": diag.total_items_count - diag.promising_items_count,
        "phase1_candidates": diag.phase1_candidates_count,
        "phase2_verified": diag.phase2_verified_count,
        "false_positive_pruned": diag.phase1_candidates_count - diag.phase2_verified_count,
        "pruning_efficiency_pct": diag.pruning_efficiency_pct,
    }

    # 5. Identify "Hidden High-Utility Gems"
    hidden_gems = identify_hidden_gems(huis, top_n=5)

    # 6. Overall KPI Summary
    top_pattern_utility = huis[0].exact_utility if huis else 0.0
    top_pattern_name = " + ".join(huis[0].pattern_names) if huis else "None"

    kpis = {
        "total_transactions": database.num_transactions,
        "total_items": database.num_items,
        "promising_items": diag.promising_items_count,
        "total_database_utility": round(database.total_utility, 2),
        "min_utility": round(diag.min_utility, 2),
        "phase1_candidates": diag.phase1_candidates_count,
        "phase2_verified": diag.phase2_verified_count,
        "pruning_efficiency_pct": round(diag.pruning_efficiency_pct, 1),
        "top_pattern_utility": round(top_pattern_utility, 2),
        "top_pattern_name": top_pattern_name,
        "phase1_ms": round(diag.phase1_ms, 2),
        "phase2_ms": round(diag.phase2_ms, 2),
        "total_ms": round(diag.total_ms, 2),
    }

    return {
        "kpis": kpis,
        "top_patterns_chart": top_patterns_chart,
        "scatter_data": scatter_data,
        "k_distribution": k_distribution,
        "pruning_funnel": pruning_funnel,
        "hidden_gems": hidden_gems,
    }


def identify_hidden_gems(
    huis: List[HighUtilityItemset],
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Identifies patterns with relatively low frequency (support %)
    but high exact utility and average utility per transaction.
    These showcase why HUIM discovers critical business value that
    standard frequency-based FP-Growth completely misses.
    """
    if not huis:
        return []

    if len(huis) <= 2:
        return [
            {
                "pattern": h.pattern,
                "pattern_names": h.pattern_names,
                "pattern_str": " + ".join(h.pattern_names),
                "support_count": h.support_count,
                "support_pct": round(h.support_pct, 2),
                "exact_utility": round(h.exact_utility, 2),
                "avg_utility_per_tx": round(h.avg_utility_per_tx, 2),
                "gem_ratio": round(h.avg_utility_per_tx, 2),
                "insight": f"High value pattern generating {h.exact_utility:,.2f} utility across {h.support_count} orders.",
            }
            for h in huis
        ]

    max_util = max(h.exact_utility for h in huis) or 1.0
    max_sup_pct = max(h.support_pct for h in huis) or 1.0
    median_sup_pct = statistics.median(h.support_pct for h in huis)

    gem_candidates = []
    for h in huis:
        # Normalized metrics
        norm_util = h.exact_utility / max_util
        norm_sup = h.support_pct / max_sup_pct

        # Gem score prioritizes high utility with low frequency (high utility density)
        # Ratio of normalized utility to normalized support
        gem_ratio = norm_util / (norm_sup + 0.05)

        # Bonus if support is below median
        if h.support_pct <= median_sup_pct:
            gem_ratio *= 1.3

        gem_candidates.append((gem_ratio, h))

    # Sort by gem score descending
    gem_candidates.sort(key=lambda x: -x[0])

    top_gems = []
    for ratio, h in gem_candidates[:top_n]:
        insight = (
            f"Low occurrence rate ({h.support_pct:.2f}% of transactions), "
            f"yet accounts for {h.exact_utility:,.2f} in utility "
            f"({h.avg_utility_per_tx:,.2f} avg/tx). Standard FP-Growth would drop this as infrequent!"
        )
        top_gems.append({
            "pattern": h.pattern,
            "pattern_names": h.pattern_names,
            "pattern_str": " + ".join(h.pattern_names),
            "support_count": h.support_count,
            "support_pct": round(h.support_pct, 2),
            "exact_utility": round(h.exact_utility, 2),
            "avg_utility_per_tx": round(h.avg_utility_per_tx, 2),
            "gem_ratio": round(ratio, 2),
            "insight": insight,
        })

    return top_gems
