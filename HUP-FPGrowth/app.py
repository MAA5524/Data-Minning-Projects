"""
app.py
FastAPI backend for HUP-FPGrowth (High Utility Pattern Mining).
Serves static UI, provides dataset metadata, and exposes high-performance
two-phase UP-Growth / IHUP-TWU mining API endpoints.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import io
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.analytics import compute_analytics_summary
from src.huim_fpgrowth import mine_high_utility_patterns
from src.loader import UtilityDatabase, load_spmf_txt, load_utility_csv

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
RAW_DIR = BASE_DIR / "datasets" / "raw"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to initialize data on startup."""
    initialize_standard_datasets()
    yield


app = FastAPI(
    title="HUP-FPGrowth • High Utility Pattern Mining",
    description="Two-Phase Tree-Based High Utility Itemset Mining (UP-Growth / IHUP-TWU)",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database cache for instantaneous mining runs
DATABASE_CACHE: Dict[str, UtilityDatabase] = {}
DATASET_METADATA: Dict[str, Dict[str, Any]] = {}


class MineRequest(BaseModel):
    dataset_id: str
    min_utility: float = Field(..., gt=0, description="Minimum utility threshold value")
    threshold_mode: str = Field(
        default="percentage",
        description="'percentage' (% of total DB utility) or 'absolute' (raw utility value)",
    )
    max_len: Optional[int] = Field(
        default=4,
        description="Maximum pattern length (None or 0 for unlimited)",
    )


def get_or_load_dataset(dataset_id: str) -> UtilityDatabase:
    """Retrieves dataset from in-memory cache or loads it from disk."""
    if dataset_id in DATABASE_CACHE:
        return DATABASE_CACHE[dataset_id]

    # Standard pre-processed datasets
    csv_path = PROCESSED_DIR / f"{dataset_id}.csv"
    if csv_path.exists():
        db = load_utility_csv(csv_path)
        DATABASE_CACHE[dataset_id] = db
        return db

    raise HTTPException(
        status_code=404,
        detail=f"Dataset '{dataset_id}' not found. Available: {list(DATABASE_CACHE.keys())}",
    )


def initialize_standard_datasets() -> None:
    """Preloads standard datasets and initializes metadata on startup."""
    standard_configs = [
        {
            "id": "ecommerce_utility",
            "name": "E-Commerce Online Retail (Named Items)",
            "file": "ecommerce_utility.csv",
            "suggested_pct": 0.35,
            "description": "UK Online Retail transactions with human-readable product names and profit margins.",
        },
        {
            "id": "foodmart_utility",
            "name": "Foodmart Grocery Transactions",
            "file": "foodmart_utility.csv",
            "suggested_pct": 0.12,
            "description": "Retail supermarket dataset with transaction utilities and product IDs.",
        },
    ]

    for cfg in standard_configs:
        file_path = PROCESSED_DIR / cfg["file"]
        if file_path.exists():
            db = load_utility_csv(file_path)
            DATABASE_CACHE[cfg["id"]] = db

            sug_pct = cfg["suggested_pct"]
            sug_abs = round(db.total_utility * (sug_pct / 100.0), 2)

            DATASET_METADATA[cfg["id"]] = {
                "dataset_id": cfg["id"],
                "name": cfg["name"],
                "filename": cfg["file"],
                "description": cfg["description"],
                "total_transactions": db.num_transactions,
                "unique_items": db.num_items,
                "total_utility": round(db.total_utility, 2),
                "suggested_min_utility_pct": sug_pct,
                "suggested_min_utility_abs": sug_abs,
                "is_custom": False,
            }





@app.get("/")
def serve_index():
    """Serves the single-page application dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(
        status_code=404,
        content={"message": "Frontend index.html not found"},
    )


@app.get("/api/datasets")
def list_datasets():
    """Returns metadata for all available datasets."""
    # Ensure standard datasets are loaded if cache was empty
    if not DATASET_METADATA:
        initialize_standard_datasets()

    return {
        "datasets": list(DATASET_METADATA.values()),
    }


@app.post("/api/mine")
def mine_patterns(req: MineRequest):
    """
    Executes UP-Growth / IHUP-TWU two-phase mining on the requested dataset.
    """
    db = get_or_load_dataset(req.dataset_id)

    # Calculate absolute min_utility threshold
    if req.threshold_mode == "percentage":
        threshold_input = req.min_utility
        abs_min_utility = (req.min_utility / 100.0) * db.total_utility
    else:
        threshold_input = req.min_utility
        abs_min_utility = req.min_utility

    if abs_min_utility <= 0:
        raise HTTPException(
            status_code=400,
            detail="Minimum utility threshold must be strictly positive.",
        )

    # Normalize max_len
    max_len = req.max_len if (req.max_len and req.max_len > 0) else None

    # Execute mining algorithm
    result = mine_high_utility_patterns(
        database=db,
        min_utility=abs_min_utility,
        max_len=max_len,
        threshold_mode=req.threshold_mode,
        threshold_input_value=threshold_input,
    )

    # Compute comprehensive analytics and chart representations
    analytics = compute_analytics_summary(database=db, mining_result=result)

    meta = DATASET_METADATA.get(req.dataset_id, {})

    return {
        "success": True,
        "dataset_id": req.dataset_id,
        "dataset_name": meta.get("name", req.dataset_id),
        "total_transactions": db.num_transactions,
        "total_items": db.num_items,
        "total_utility": round(db.total_utility, 2),
        "threshold_mode": req.threshold_mode,
        "threshold_value": threshold_input,
        "effective_min_utility": round(abs_min_utility, 2),
        "max_len": max_len,
        "diagnostics": result.diagnostics.to_dict(),
        "kpis": analytics["kpis"],
        "patterns": [hui.to_dict() for hui in result.huis],
        "top_patterns_chart": analytics["top_patterns_chart"],
        "scatter_data": analytics["scatter_data"],
        "k_distribution": analytics["k_distribution"],
        "pruning_funnel": analytics["pruning_funnel"],
        "hidden_gems": analytics["hidden_gems"],
    }


@app.post("/api/upload")
async def upload_custom_dataset(file: UploadFile = File(...)):
    """
    Accepts a custom .csv (unified schema) or .txt (SPMF format) file.
    Parses and registers it as an in-memory dataset ready for mining.
    """
    filename = file.filename or "uploaded_dataset"
    content_bytes = await file.read()

    try:
        content_str = content_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode uploaded file: {str(e)}")

    dataset_id = f"custom_{int(time.time())}_{Path(filename).stem}"
    file_io = io.StringIO(content_str)

    try:
        if filename.endswith(".txt") or ":" in content_str[:500]:
            # Treat as SPMF format
            db = load_spmf_txt(file_io)
        else:
            # Treat as CSV format
            db = load_utility_csv(file_io)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not parse uploaded dataset. Check formatting: {str(e)}",
        )

    if db.num_transactions == 0:
        raise HTTPException(status_code=400, detail="Uploaded dataset contains 0 transactions.")

    # Cache dataset
    DATABASE_CACHE[dataset_id] = db

    # Suggest reasonable default (0.5% or top TWU fraction)
    twus = db.compute_twus()
    max_twu = max(twus.values()) if twus else db.total_utility
    top_pct = (max_twu / db.total_utility * 100.0) if db.total_utility > 0 else 1.0
    suggested_pct = max(0.1, round(top_pct * 0.25, 2))
    suggested_abs = round(db.total_utility * (suggested_pct / 100.0), 2)

    meta = {
        "dataset_id": dataset_id,
        "name": f"Custom: {filename}",
        "filename": filename,
        "description": f"Uploaded custom dataset ({db.num_transactions:,} transactions, {db.num_items:,} unique items)",
        "total_transactions": db.num_transactions,
        "unique_items": db.num_items,
        "total_utility": round(db.total_utility, 2),
        "suggested_min_utility_pct": suggested_pct,
        "suggested_min_utility_abs": suggested_abs,
        "is_custom": True,
    }
    DATASET_METADATA[dataset_id] = meta

    return {
        "success": True,
        "message": f"Successfully loaded {filename} ({db.num_transactions:,} transactions)",
        "dataset": meta,
    }


# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
