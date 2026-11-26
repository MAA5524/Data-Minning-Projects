"""FastAPI Backend for the ID3-Gini Decision Tree Classifier & Interactive Dashboard."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.evaluator import evaluate_model
from src.id3_tree import ID3GiniClassifier
from src.loader import (
    DatasetBundle,
    list_builtin_datasets,
    load_csv_from_text,
    stratified_train_test_split,
)

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="ID3-Gini Decision Tree API",
    description="Pure-Python ID3 Decision Tree Classifier using the Gini Index (Han, Pei, Tong Ch. 6).",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class TrainRequest(BaseModel):
    dataset_id: str = Field(..., description="Identifier of a built-in or uploaded dataset.")
    target_column: Optional[str] = Field(
        default=None,
        description="Target class column name. Defaults to dataset's detected target.",
    )
    test_size: float = Field(default=0.2, ge=0.0, lt=1.0)
    random_seed: int = Field(default=42)
    max_depth: Optional[int] = Field(default=None, ge=0)
    min_samples_split: int = Field(default=2, ge=2)


class AppState:
    """In-memory state holding loaded datasets and the active trained model."""

    def __init__(self) -> None:
        self.datasets: dict[str, DatasetBundle] = {}
        self.active_model: Optional[ID3GiniClassifier] = None
        self.active_dataset_id: Optional[str] = None
        self.active_target_column: Optional[str] = None
        self.active_test_rows: list[dict[str, str]] = []
        self.refresh_builtin_datasets()

    def refresh_builtin_datasets(self) -> None:
        builtins = list_builtin_datasets(DATASETS_DIR)
        for dataset_id, bundle in builtins.items():
            self.datasets[dataset_id] = bundle


state = AppState()


def _slugify_dataset_id(filename: str) -> str:
    stem = Path(filename or "custom_dataset").stem.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", stem).strip("_") or "custom_dataset"
    candidate = f"uploaded_{slug}"
    suffix = 2
    while candidate in state.datasets:
        candidate = f"uploaded_{slug}_{suffix}"
        suffix += 1
    return candidate


@app.get("/", include_in_schema=False)
async def serve_dashboard() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Dashboard index.html not found.")
    return FileResponse(str(index_path))


@app.get("/api/datasets")
async def get_datasets() -> dict[str, Any]:
    state.refresh_builtin_datasets()
    items = [bundle.to_metadata() for bundle in state.datasets.values()]
    return {"datasets": items, "count": len(items)}


@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid .csv file.")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    try:
        text = raw_bytes.decode("utf-8", errors="replace")
        dataset_id = _slugify_dataset_id(file.filename)
        display_name = Path(file.filename).stem.replace("_", " ").title()
        bundle = load_csv_from_text(
            text=text,
            dataset_id=dataset_id,
            name=display_name,
            source="uploaded",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    state.datasets[bundle.dataset_id] = bundle
    return {"message": "Dataset uploaded successfully.", "dataset": bundle.to_metadata()}


@app.post("/api/train")
async def train_model(payload: TrainRequest) -> dict[str, Any]:
    if payload.dataset_id not in state.datasets:
        state.refresh_builtin_datasets()
    bundle = state.datasets.get(payload.dataset_id)
    if bundle is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset '{payload.dataset_id}' not found.",
        )

    target_column = payload.target_column or bundle.default_target
    if target_column not in bundle.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Target column '{target_column}' does not exist in dataset '{bundle.dataset_id}'.",
        )

    feature_columns = [col for col in bundle.columns if col != target_column]
    if not feature_columns:
        raise HTTPException(
            status_code=400,
            detail="Dataset must contain at least one feature column besides the target.",
        )

    try:
        train_rows, test_rows = stratified_train_test_split(
            rows=bundle.rows,
            target_column=target_column,
            test_size=payload.test_size,
            random_seed=payload.random_seed,
        )
        classifier = ID3GiniClassifier(
            max_depth=payload.max_depth,
            min_samples_split=payload.min_samples_split,
        )
        start = time.perf_counter()
        classifier.fit(
            rows=train_rows,
            target_column=target_column,
            feature_columns=feature_columns,
            attribute_domains=bundle.unique_values_per_column,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    metrics = evaluate_model(
        model=classifier,
        train_rows=train_rows,
        test_rows=test_rows,
        target_column=target_column,
        training_time_ms=elapsed_ms,
        all_labels=bundle.unique_values_per_column.get(target_column),
    )
    rules = classifier.extract_rules()
    tree_dict = classifier.to_dict()

    state.active_model = classifier
    state.active_dataset_id = bundle.dataset_id
    state.active_target_column = target_column
    state.active_test_rows = test_rows[:25] if test_rows else train_rows[:25]

    feature_unique_values = {
        col: bundle.unique_values_per_column[col] for col in feature_columns
    }

    return {
        "dataset_id": bundle.dataset_id,
        "dataset_name": bundle.name,
        "target_column": target_column,
        "feature_columns": feature_columns,
        "unique_values_per_column": feature_unique_values,
        "split_info": {
            "test_size": payload.test_size,
            "random_seed": payload.random_seed,
            "max_depth": payload.max_depth,
            "min_samples_split": payload.min_samples_split,
            "train_samples": len(train_rows),
            "test_samples": len(test_rows),
        },
        "tree": tree_dict,
        "metrics": metrics,
        "rules": rules,
        "sample_rows": state.active_test_rows[:10],
    }


@app.post("/api/predict")
async def predict_sample(sample: dict[str, Any] = Body(...)) -> dict[str, Any]:
    if state.active_model is None:
        raise HTTPException(
            status_code=400,
            detail="No trained model is currently active. Call POST /api/train first.",
        )

    features = sample.get("features") if isinstance(sample.get("features"), dict) else sample
    if not isinstance(features, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object of feature values.")

    result = state.active_model.predict_with_trace(features)
    return {
        "target_column": state.active_target_column,
        "prediction": result["prediction"],
        "path": result["path"],
        "path_node_ids": result["path_node_ids"],
        "unseen_fallback": result["unseen_fallback"],
    }
