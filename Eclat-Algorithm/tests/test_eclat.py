"""Comprehensive automated unit tests for Eclat Pattern Mining Suite.

Validates:
1. Loader (Long/Transactional & Horizontal formats)
2. Eclat vertical DFS engine (prefix equivalence classes & set intersections)
3. Rule generation (subsets, confidence filtering)
4. Metrics (Lift vs. Null-Invariant Kulczynski)
5. Edge cases (empty data, thresholds)
"""

from __future__ import annotations

import io
import math
import pytest

from src.eclat import eclat
from src.loader import load_dataset
from src.metrics import evaluate_rules, kulczynski, lift
from src.rules import generate_association_rules


# -----------------------------------------------------------------------------
# 1. Loader Tests
# -----------------------------------------------------------------------------
def test_loader_horizontal_basket():
    csv_content = """
    Water,Nuts,Diaper
    Water,Coffee,Diaper
    Water,Diaper,Eggs
    Nuts,Eggs,Milk
    Nuts,Coffee,Diaper,Eggs,Milk
    """
    stream = io.StringIO(csv_content.strip())
    data = load_dataset(stream)

    assert data.total_transactions == 5
    assert len(data.items) == 6
    assert data.tid_lists["Water"] == {0, 1, 2}
    assert data.tid_lists["Diaper"] == {0, 1, 2, 4}
    assert data.tid_lists["Nuts"] == {0, 3, 4}
    assert data.tid_lists["Eggs"] == {2, 3, 4}
    assert data.tid_lists["Coffee"] == {1, 4}
    assert data.tid_lists["Milk"] == {3, 4}


def test_loader_long_transactional():
    csv_content = """Member_number,Date,itemDescription
1001,2025-01-01,milk
1001,2025-01-01,bread
1002,2025-01-01,butter
1001,2025-01-02,milk
"""
    stream = io.StringIO(csv_content.strip())
    data = load_dataset(stream)

    # 1001 on 2025-01-01 -> {milk, bread}
    # 1002 on 2025-01-01 -> {butter}
    # 1001 on 2025-01-02 -> {milk}
    assert data.total_transactions == 3
    assert "milk" in data.tid_lists
    assert len(data.tid_lists["milk"]) == 2


def test_loader_empty():
    stream = io.StringIO("")
    data = load_dataset(stream)
    assert data.total_transactions == 0
    assert len(data.items) == 0


# -----------------------------------------------------------------------------
# 2. Eclat Algorithm Tests
# -----------------------------------------------------------------------------
def test_eclat_textbook_sample():
    """Verify Eclat with textbook dataset:
    TID 0: Water, Nuts, Diaper
    TID 1: Water, Coffee, Diaper
    TID 2: Water, Diaper, Eggs
    TID 3: Nuts, Eggs, Milk
    TID 4: Nuts, Coffee, Diaper, Eggs, Milk

    minsup = 50% -> ceil(0.5 * 5) = 3
    """
    tid_lists = {
        "Water": {0, 1, 2},
        "Nuts": {0, 3, 4},
        "Diaper": {0, 1, 2, 4},
        "Eggs": {2, 3, 4},
        "Coffee": {1, 4},
        "Milk": {3, 4},
    }
    freq = eclat(tid_lists, total_transactions=5, minsup=0.5)

    # Coffee and Milk have count 2 < 3, so pruned
    assert frozenset(["Coffee"]) not in freq
    assert frozenset(["Milk"]) not in freq

    # Frequent 1-itemsets
    assert freq[frozenset(["Diaper"])] == 4
    assert freq[frozenset(["Water"])] == 3
    assert freq[frozenset(["Nuts"])] == 3
    assert freq[frozenset(["Eggs"])] == 3

    # Frequent 2-itemsets: {Water, Diaper} has intersection {0, 1, 2} & {0, 1, 2, 4} = {0, 1, 2} (count 3)
    assert freq[frozenset(["Water", "Diaper"])] == 3

    # Other pairs have count 2 < 3, so pruned:
    assert frozenset(["Water", "Nuts"]) not in freq  # intersection {0} -> 1
    assert frozenset(["Water", "Eggs"]) not in freq  # intersection {2} -> 1
    assert frozenset(["Nuts", "Diaper"]) not in freq  # intersection {0, 4} -> 2
    assert frozenset(["Eggs", "Diaper"]) not in freq  # intersection {2, 4} -> 2


def test_eclat_absolute_minsup():
    tid_lists = {
        "A": {0, 1, 2},
        "B": {0, 1},
        "C": {0, 1, 2, 3},
    }
    freq = eclat(tid_lists, total_transactions=4, minsup=2)
    assert freq[frozenset(["C"])] == 4
    assert freq[frozenset(["A"])] == 3
    assert freq[frozenset(["B"])] == 2
    assert freq[frozenset(["A", "C"])] == 3
    assert freq[frozenset(["A", "B"])] == 2
    assert freq[frozenset(["B", "C"])] == 2
    assert freq[frozenset(["A", "B", "C"])] == 2


def test_eclat_max_len():
    tid_lists = {
        "A": {0, 1, 2},
        "B": {0, 1, 2},
        "C": {0, 1, 2},
    }
    freq_len1 = eclat(tid_lists, total_transactions=3, minsup=1, max_len=1)
    assert all(len(k) == 1 for k in freq_len1.keys())

    freq_len2 = eclat(tid_lists, total_transactions=3, minsup=1, max_len=2)
    assert all(len(k) <= 2 for k in freq_len2.keys())
    assert frozenset(["A", "B", "C"]) not in freq_len2


# -----------------------------------------------------------------------------
# 3. Association Rules & Metrics Tests
# -----------------------------------------------------------------------------
def test_rules_and_metrics():
    # Textbook sample:
    # sup(Water) = 3/5 = 0.6
    # sup(Diaper) = 4/5 = 0.8
    # sup(Water, Diaper) = 3/5 = 0.6
    freq = {
        frozenset(["Water"]): 3,
        frozenset(["Diaper"]): 4,
        frozenset(["Water", "Diaper"]): 3,
    }

    rules = generate_association_rules(freq, total_transactions=5, minconf=0.5)
    assert len(rules) == 2

    df = evaluate_rules(rules)
    assert len(df) == 2

    # Rule: Water -> Diaper
    r_water_diaper = df[df["antecedent_str"] == "Water"].iloc[0]
    assert r_water_diaper["confidence"] == 1.0  # 3/3
    assert math.isclose(r_water_diaper["lift"], 1.25)  # 0.6 / (0.6 * 0.8) = 1 / 0.8 = 1.25
    assert math.isclose(r_water_diaper["kulczynski"], 0.875)  # 0.5 * (3/3 + 3/4) = 0.5 * 1.75 = 0.875

    # Rule: Diaper -> Water
    r_diaper_water = df[df["antecedent_str"] == "Diaper"].iloc[0]
    assert r_diaper_water["confidence"] == 0.75  # 3/4
    assert math.isclose(r_diaper_water["lift"], 1.25)
    assert math.isclose(r_diaper_water["kulczynski"], 0.875)


def test_null_invariance_demonstration():
    """Demonstrate why Kulczynski is Null-Invariant and Lift is NOT.
    Adding 10,000 null-transactions alters Lift drastically, but leaves Kulczynski unchanged!
    """
    s_XY_1 = 3 / 10
    s_X_1 = 5 / 10
    s_Y_1 = 5 / 10

    lift_1 = lift(s_XY_1, s_X_1, s_Y_1)
    kulc_1 = kulczynski(s_XY_1, s_X_1, s_Y_1)

    # Add 10,000 null-transactions (transactions containing neither X nor Y)
    # Total transactions becomes 10,010
    N_new = 10010
    s_XY_2 = 3 / N_new
    s_X_2 = 5 / N_new
    s_Y_2 = 5 / N_new

    lift_2 = lift(s_XY_2, s_X_2, s_Y_2)
    kulc_2 = kulczynski(s_XY_2, s_X_2, s_Y_2)

    # Kulczynski remains IDENTICAL (null-invariant)
    assert math.isclose(kulc_1, kulc_2, rel_tol=1e-9)

    # Lift changes by orders of magnitude (NOT null-invariant)
    assert not math.isclose(lift_1, lift_2)
    assert lift_2 > lift_1 * 500  # Artificially sky-rockets!


def test_edge_cases():
    # Empty rules
    empty_df = evaluate_rules([])
    assert empty_df.empty

    # Division by zero protection
    assert lift(0, 0, 0) == 0.0
    assert kulczynski(0, 0, 0) == 0.0


def test_market_basket_optimisation_file():
    from pathlib import Path
    data_path = Path("data/Market_Basket_Optimisation.csv")
    if data_path.exists():
        data = load_dataset(data_path)
        assert data.format_detected == "Horizontal Basket"
        assert data.total_transactions == 7501
        assert len(data.items) == 119
        freq = eclat(data.tid_lists, data.total_transactions, minsup=0.03)
        assert len(freq) > 0

