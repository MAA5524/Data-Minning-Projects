"""Comprehensive unit and integration tests for ID3-Gini Decision Tree & FastAPI API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app
from src.evaluator import evaluate_model
from src.gini import best_gini_split, delta_gini, gini_impurity, weighted_gini_split
from src.id3_tree import ID3GiniClassifier
from src.loader import (
    CAR_EVALUATION_COLUMNS,
    load_csv_from_path,
    load_csv_from_text,
    stratified_train_test_split,
)


def test_gini_impurity_exact_math() -> None:
    assert gini_impurity([]) == 0.0
    assert gini_impurity(["yes", "yes", "yes"]) == pytest.approx(0.0, abs=1e-9)
    assert gini_impurity(["yes", "no"]) == pytest.approx(0.5, abs=1e-9)
    # 9 yes, 5 no (Han, Pei, Tong classic AllElectronics target counts)
    labels = ["yes"] * 9 + ["no"] * 5
    expected = 1.0 - (9 / 14) ** 2 - (5 / 14) ** 2
    assert gini_impurity(labels) == pytest.approx(expected, abs=1e-9)


def test_weighted_and_delta_gini_exact_math() -> None:
    rows = [
        {"outlook": "sunny", "play": "no"},
        {"outlook": "sunny", "play": "no"},
        {"outlook": "sunny", "play": "yes"},
        {"outlook": "overcast", "play": "yes"},
        {"outlook": "overcast", "play": "yes"},
        {"outlook": "rain", "play": "yes"},
        {"outlook": "rain", "play": "no"},
    ]
    # Parent: 4 yes, 3 no => Gini(D) = 1 - (16/49 + 9/49) = 24/49
    expected_parent = 1.0 - (4 / 7) ** 2 - (3 / 7) ** 2
    # sunny (3): 1 yes, 2 no => 1 - (1/9 + 4/9) = 4/9
    # overcast (2): 2 yes => 0
    # rain (2): 1 yes, 1 no => 0.5
    expected_gini_a = (3 / 7) * (4 / 9) + (2 / 7) * 0.0 + (2 / 7) * 0.5
    expected_delta = expected_parent - expected_gini_a

    p_gini, g_a, d_gini = delta_gini(rows, "outlook", "play")
    assert p_gini == pytest.approx(expected_parent, abs=1e-9)
    assert g_a == pytest.approx(expected_gini_a, abs=1e-9)
    assert d_gini == pytest.approx(expected_delta, abs=1e-9)

    assert weighted_gini_split({"a": ["x", "x"], "b": ["y", "x"]}) == pytest.approx(
        0.5 * 0.0 + 0.5 * 0.5, abs=1e-9
    )


def test_best_gini_split_selects_lowest_weighted_gini() -> None:
    rows = [
        {"useless": "a", "perfect": "p", "y": "1"},
        {"useless": "a", "perfect": "p", "y": "1"},
        {"useless": "a", "perfect": "n", "y": "0"},
        {"useless": "b", "perfect": "n", "y": "0"},
    ]
    res = best_gini_split(rows, ["useless", "perfect"], "y")
    assert res["best_attribute"] == "perfect"
    assert res["best_gini_a"] == pytest.approx(0.0, abs=1e-9)
    assert res["best_delta_gini"] == pytest.approx(0.5, abs=1e-9)


def test_arbitrary_column_counts_2_6_22() -> None:
    # 1) 2-feature synthetic CSV
    csv_2 = "f1,f2,label\na,x,yes\na,y,yes\nb,x,no\nb,y,no\n"
    b2 = load_csv_from_text(csv_2, "two_feat", "Two Features")
    assert b2.default_target == "label"
    clf2 = ID3GiniClassifier().fit(b2.rows, target_column="label")
    assert clf2.predict([{"f1": "a", "f2": "x"}, {"f1": "b", "f2": "y"}]) == ["yes", "no"]

    # 2) 6-feature headerless car_evaluation.csv
    car_bundle = load_csv_from_path(PROJECT_ROOT / "datasets" / "car_evaluation.csv")
    assert car_bundle.columns == CAR_EVALUATION_COLUMNS
    assert car_bundle.has_synthetic_header is True
    assert car_bundle.default_target == "class"
    car_train, car_test = stratified_train_test_split(car_bundle.rows, "class", test_size=0.2, random_seed=42)
    clf6 = ID3GiniClassifier().fit(car_train, target_column="class", attribute_domains=car_bundle.unique_values_per_column)
    eval6 = evaluate_model(clf6, car_train, car_test, "class", training_time_ms=1.0)
    assert eval6["test_accuracy"] > 0.85

    # 3) 22-feature mushrooms.csv (target in column 0)
    mush_bundle = load_csv_from_path(PROJECT_ROOT / "datasets" / "mushrooms.csv")
    assert len(mush_bundle.columns) == 23
    assert mush_bundle.default_target == "class"
    m_train, m_test = stratified_train_test_split(mush_bundle.rows, "class", test_size=0.2, random_seed=42)
    clf22 = ID3GiniClassifier().fit(m_train, target_column="class", attribute_domains=mush_bundle.unique_values_per_column)
    eval22 = evaluate_model(clf22, m_train, m_test, "class", training_time_ms=1.0)
    assert eval22["test_accuracy"] > 0.99


def test_unseen_value_fallback_and_stopping_criteria() -> None:
    rows = [
        {"color": "red", "size": "s", "cls": "A"},
        {"color": "red", "size": "m", "cls": "A"},
        {"color": "red", "size": "l", "cls": "A"},
        {"color": "blue", "size": "s", "cls": "B"},
        {"color": "blue", "size": "m", "cls": "A"},
    ]
    clf = ID3GiniClassifier(max_depth=1, min_samples_split=2).fit(rows, target_column="cls")
    assert clf.tree_stats()["tree_depth"] <= 1

    trace = clf.predict_with_trace({"color": "purple_unseen", "size": "s"})
    assert trace["unseen_fallback"] is True
    assert trace["prediction"] == "A"
    assert trace["path"][0]["is_fallback"] is True

    tree_json = clf.to_dict()
    assert {"attribute", "gini", "delta_gini", "samples", "class_distribution", "majority_class", "is_leaf", "children"}.issubset(
        tree_json.keys()
    )
    rules = clf.extract_rules()
    assert len(rules) >= 1
    assert all("IF " in r["text"] and " THEN cls = " in r["text"] for r in rules)


def test_fastapi_endpoints_end_to_end() -> None:
    client = TestClient(app)

    home_resp = client.get("/")
    assert home_resp.status_code == 200
    assert "ID3-Gini" in home_resp.text

    ds_resp = client.get("/api/datasets")
    assert ds_resp.status_code == 200
    ds_ids = {d["dataset_id"] for d in ds_resp.json()["datasets"]}
    assert {"car_evaluation", "mushrooms"}.issubset(ds_ids)

    train_resp = client.post(
        "/api/train",
        json={
            "dataset_id": "car_evaluation",
            "target_column": "class",
            "test_size": 0.2,
            "random_seed": 42,
            "max_depth": None,
            "min_samples_split": 2,
        },
    )
    assert train_resp.status_code == 200
    train_data = train_resp.json()
    assert train_data["metrics"]["test_accuracy"] > 0.85
    assert len(train_data["rules"]) > 0
    assert train_data["tree"]["attribute"] is not None

    pred_resp = client.post(
        "/api/predict",
        json={
            "buying": "vhigh",
            "maint": "vhigh",
            "doors": "2",
            "persons": "2",
            "lug_boot": "small",
            "safety": "low",
        },
    )
    assert pred_resp.status_code == 200
    pred_data = pred_resp.json()
    assert pred_data["prediction"] == "unacc"
    assert len(pred_data["path"]) >= 1

    # Upload custom CSV with arbitrary columns and override target column
    custom_csv = "weather,temp,wind,decision\nsunny,hot,weak,no\nsunny,mild,strong,no\novercast,hot,weak,yes\nrain,cool,weak,yes\nrain,cool,strong,no\n"
    upload_resp = client.post(
        "/api/upload",
        files={"file": ("play_custom.csv", custom_csv.encode("utf-8"), "text/csv")},
    )
    assert upload_resp.status_code == 200
    uploaded_id = upload_resp.json()["dataset"]["dataset_id"]

    custom_train = client.post(
        "/api/train",
        json={
            "dataset_id": uploaded_id,
            "target_column": "decision",
            "test_size": 0.2,
            "random_seed": 7,
        },
    )
    assert custom_train.status_code == 200
    assert custom_train.json()["target_column"] == "decision"
