"""
tests/test_huim.py
Comprehensive test suite for HUP-FPGrowth:
- Textbook 5-transaction ground truth verification
- TU and TWU calculation
- UP-Tree construction & Phase 1 candidate mining
- Phase 2 exact utility verification
- CSV and SPMF loaders
- Analytics & Hidden Gems
- FastAPI REST API endpoints
"""

import io
import sys
from pathlib import Path

# Ensure HUP-FPGrowth root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from app import app
from src.analytics import compute_analytics_summary, identify_hidden_gems
from src.huim_fpgrowth import mine_high_utility_patterns
from src.loader import UtilityDatabase, load_spmf_txt, load_utility_csv
from src.up_tree import HeaderEntry, UPTree


@pytest.fixture
def textbook_database() -> UtilityDatabase:
    """
    Standard textbook 5-transaction utility database.
    T1: A:5, B:10, C:1 -> TU=16
    T2: A:5, C:6       -> TU=11
    T3: B:8, D:6       -> TU=14
    T4: A:10, B:4, D:2 -> TU=16
    T5: B:2, C:2, E:1  -> TU=5
    Total Utility = 62
    """
    txs = [
        {1: 5.0, 2: 10.0, 3: 1.0},        # T0
        {1: 5.0, 3: 6.0},                 # T1
        {2: 8.0, 4: 6.0},                 # T2
        {1: 10.0, 2: 4.0, 4: 2.0},        # T3
        {2: 2.0, 3: 2.0, 5: 1.0},         # T4
    ]
    names = {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    tus = [sum(t.values()) for t in txs]
    total_u = sum(tus)

    inv: dict[int, set[int]] = {i: set() for i in names}
    for tid, t in enumerate(txs):
        for i in t:
            inv[i].add(tid)

    return UtilityDatabase(
        transactions=txs,
        transaction_utilities=tus,
        total_utility=total_u,
        item_names=names,
        inverted_index=inv,
    )


def test_textbook_tu_and_twu(textbook_database: UtilityDatabase):
    """Verifies Transaction Utilities and Transaction-Weighted Utilities."""
    db = textbook_database
    assert db.transaction_utilities == [16.0, 11.0, 14.0, 16.0, 5.0]
    assert db.total_utility == 62.0

    twus = db.compute_twus()
    assert twus[1] == 16.0 + 11.0 + 16.0  # A appears in T0, T1, T3 -> 43.0
    assert twus[2] == 16.0 + 14.0 + 16.0 + 5.0  # B in T0, T2, T3, T4 -> 51.0
    assert twus[3] == 16.0 + 11.0 + 5.0  # C in T0, T1, T4 -> 32.0
    assert twus[4] == 14.0 + 16.0  # D in T2, T3 -> 30.0
    assert twus[5] == 5.0  # E in T4 -> 5.0


def test_textbook_mining_min_utility_20(textbook_database: UtilityDatabase):
    """
    Verifies Phase 1 candidates and Phase 2 verified HUIs with min_utility = 20.0.
    At min_utility = 20:
    Ground Truth HUIs:
    - {A}: utility = 20.0, support = 3
    - {B}: utility = 24.0, support = 4
    - {A, B}: utility = 29.0, support = 2
    - {B, D}: utility = 20.0, support = 2
    """
    res = mine_high_utility_patterns(textbook_database, min_utility=20.0, max_len=4)

    verified_patterns = {tuple(sorted(h.pattern_names)): h.exact_utility for h in res.huis}
    assert ("A",) in verified_patterns and verified_patterns[("A",)] == 20.0
    assert ("B",) in verified_patterns and verified_patterns[("B",)] == 24.0
    assert ("A", "B") in verified_patterns and verified_patterns[("A", "B")] == 29.0
    assert ("B", "D") in verified_patterns and verified_patterns[("B", "D")] == 20.0

    assert len(res.huis) == 4
    # Pruning efficiency: Phase 1 candidates > Phase 2 verified
    assert res.diagnostics.phase1_candidates_count >= 4
    assert res.diagnostics.phase2_verified_count == 4
    assert res.diagnostics.pruning_efficiency_pct > 0


def test_textbook_mining_min_utility_25(textbook_database: UtilityDatabase):
    """
    At min_utility = 25.0:
    Only {A, B} has exact utility >= 25 (utility = 29.0).
    """
    res = mine_high_utility_patterns(textbook_database, min_utility=25.0, max_len=4)
    assert len(res.huis) == 1
    assert tuple(sorted(res.huis[0].pattern_names)) == ("A", "B")
    assert res.huis[0].exact_utility == 29.0
    assert res.huis[0].support_count == 2


def test_max_len_constraint(textbook_database: UtilityDatabase):
    """Verifies that max_len constraint is respected."""
    # max_len=1: only 1-itemsets
    res_len1 = mine_high_utility_patterns(textbook_database, min_utility=20.0, max_len=1)
    for h in res_len1.huis:
        assert h.length == 1
    assert len(res_len1.huis) == 2  # {A} and {B}


def test_csv_loader():
    """Verifies loading from CSV formatted text."""
    csv_text = (
        "transaction_id,item_id,item_name,utility\n"
        "1,101,Widget A,15.5\n"
        "1,102,Widget B,20.0\n"
        "2,101,Widget A,10.0\n"
    )
    db = load_utility_csv(io.StringIO(csv_text))
    assert db.num_transactions == 2
    assert db.num_items == 2
    assert db.total_utility == 45.5
    assert db.get_item_name(101) == "Widget A"
    assert db.inverted_index[101] == {0, 1}


def test_spmf_txt_loader():
    """Verifies parsing of SPMF format."""
    spmf_text = (
        "@ITEM=1=Alpha\n"
        "@ITEM=2=Beta\n"
        "1 2:30:10 20\n"
        "1:15:15\n"
    )
    db = load_spmf_txt(io.StringIO(spmf_text))
    assert db.num_transactions == 2
    assert db.total_utility == 45.0
    assert db.get_item_name(1) == "Alpha"
    assert db.get_item_name(2) == "Beta"


def test_analytics_and_hidden_gems(textbook_database: UtilityDatabase):
    """Verifies analytics computation and hidden gem detection."""
    res = mine_high_utility_patterns(textbook_database, min_utility=20.0)
    summary = compute_analytics_summary(textbook_database, res)

    assert "kpis" in summary
    assert summary["kpis"]["total_transactions"] == 5
    assert summary["kpis"]["phase2_verified"] == 4
    assert len(summary["scatter_data"]) == 4
    assert len(summary["k_distribution"]["counts"]) >= 1

    gems = summary["hidden_gems"]
    assert isinstance(gems, list)
    assert len(gems) > 0


def test_api_list_datasets():
    """Verifies GET /api/datasets."""
    client = TestClient(app)
    response = client.get("/api/datasets")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert len(data["datasets"]) >= 2
    ids = [d["dataset_id"] for d in data["datasets"]]
    assert "ecommerce_utility" in ids
    assert "foodmart_utility" in ids


def test_api_mine_endpoint():
    """Verifies POST /api/mine."""
    client = TestClient(app)
    payload = {
        "dataset_id": "foodmart_utility",
        "min_utility": 15000.0,
        "threshold_mode": "absolute",
        "max_len": 3,
    }
    response = client.post("/api/mine", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "patterns" in data
    assert "kpis" in data
    assert "top_patterns_chart" in data
    assert data["diagnostics"]["phase2_verified_count"] == len(data["patterns"])


def test_api_upload_csv_endpoint():
    """Verifies POST /api/upload with CSV data."""
    client = TestClient(app)
    csv_content = (
        "transaction_id,item_id,item_name,utility\n"
        "1,1,Apple,5\n"
        "1,2,Banana,10\n"
        "2,1,Apple,5\n"
        "2,3,Cherry,15\n"
    )
    files = {"file": ("test_shop.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    dataset_id = data["dataset"]["dataset_id"]

    # Now mine on the uploaded dataset
    mine_payload = {
        "dataset_id": dataset_id,
        "min_utility": 10.0,
        "threshold_mode": "absolute",
        "max_len": 2,
    }
    mine_resp = client.post("/api/mine", json=mine_payload)
    assert mine_resp.status_code == 200
    mine_data = mine_resp.json()
    assert mine_data["success"] is True
    assert len(mine_data["patterns"]) > 0


def test_api_serve_index_and_static():
    """Verifies that GET / serves the frontend index.html."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "HUP-FPGrowth" in response.text
    assert "text/html" in response.headers.get("content-type", "")
