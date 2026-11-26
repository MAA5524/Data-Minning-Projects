"""Dynamic CSV Loader, Header Auto-Check, Target Detection, and Stratified Split."""

from __future__ import annotations

import csv
import io
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

CAR_EVALUATION_COLUMNS = [
    "buying",
    "maint",
    "doors",
    "persons",
    "lug_boot",
    "safety",
    "class",
]

_CAR_VALUE_SETS = [
    {"vhigh", "high", "med", "low"},
    {"vhigh", "high", "med", "low"},
    {"2", "3", "4", "5more"},
    {"2", "4", "more"},
    {"small", "med", "big"},
    {"low", "med", "high"},
    {"unacc", "acc", "good", "vgood"},
]

_TARGET_CANDIDATES = ("class", "target", "label", "outcome", "y")


@dataclass
class DatasetBundle:
    """In-memory representation of a parsed discrete CSV dataset."""

    dataset_id: str
    name: str
    source: str
    columns: list[str]
    rows: list[dict[str, str]]
    default_target: str
    unique_values_per_column: dict[str, list[str]]
    has_synthetic_header: bool = False

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def to_metadata(self, preview_rows: int = 5) -> dict[str, Any]:
        """Serialize dataset metadata for API responses."""
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "source": self.source,
            "columns": self.columns,
            "row_count": self.row_count,
            "default_target": self.default_target,
            "unique_values_per_column": self.unique_values_per_column,
            "has_synthetic_header": self.has_synthetic_header,
            "preview": self.rows[:preview_rows],
        }


def detect_default_target(columns: Sequence[str]) -> str:
    """Auto-detect target column by common names, else fall back to the last column."""
    if not columns:
        raise ValueError("Cannot detect target column from empty column list.")
    lowered = {col.strip().lower(): col for col in columns}
    for candidate in _TARGET_CANDIDATES:
        if candidate in lowered:
            return lowered[candidate]
    return columns[-1]


def _looks_like_car_evaluation_row(row: Sequence[str]) -> bool:
    if len(row) != len(CAR_EVALUATION_COLUMNS):
        return False
    return all(val in allowed for val, allowed in zip(row, _CAR_VALUE_SETS))


def _is_headerless(raw_rows: list[list[str]], dataset_hint: str = "") -> bool:
    """Detect whether the first row of a CSV is actually data rather than column headers."""
    if len(raw_rows) < 2:
        return False
    first = raw_rows[0]
    if _looks_like_car_evaluation_row(first):
        return True
    if "car_evaluation" in dataset_hint.lower() and len(first) == 7 and first != CAR_EVALUATION_COLUMNS:
        return True

    # Duplicate values in row 0 (e.g. "vhigh,vhigh,2,2") strongly indicate a data row.
    if len(set(first)) < len(first):
        return True

    # If every cell in row 0 looks like a pure numeric literal, treat as headerless.
    if all(re.fullmatch(r"-?\d+(\.\d+)?", cell) for cell in first if cell != ""):
        return True

    return False


def _assign_headers(raw_rows: list[list[str]], dataset_hint: str = "") -> tuple[list[str], list[list[str]], bool]:
    first = raw_rows[0]
    if _is_headerless(raw_rows, dataset_hint=dataset_hint):
        if len(first) == len(CAR_EVALUATION_COLUMNS) and (
            _looks_like_car_evaluation_row(first) or "car_evaluation" in dataset_hint.lower()
        ):
            return list(CAR_EVALUATION_COLUMNS), raw_rows, True
        headers = [f"feature_{idx + 1}" for idx in range(len(first) - 1)] + ["class"]
        return headers, raw_rows, True

    # Ensure unique, non-empty column names.
    seen: dict[str, int] = {}
    headers: list[str] = []
    for idx, raw_name in enumerate(first):
        name = raw_name.strip() or f"column_{idx + 1}"
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        headers.append(name)
    return headers, raw_rows[1:], False


def load_csv_from_text(
    text: str,
    dataset_id: str,
    name: str,
    source: str = "uploaded",
) -> DatasetBundle:
    """Parse CSV text into a DatasetBundle with stripped discrete string values."""
    cleaned_text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(cleaned_text))
    raw_rows = [
        [cell.strip() for cell in row]
        for row in reader
        if row and any(cell.strip() != "" for cell in row)
    ]

    if len(raw_rows) < 2:
        raise ValueError("CSV must contain at least 2 non-empty rows.")

    headers, data_rows, synthetic = _assign_headers(raw_rows, dataset_hint=name)
    if len(headers) < 2:
        raise ValueError("Dataset must have at least 2 columns (1 feature and 1 target).")

    expected_width = len(headers)
    dict_rows: list[dict[str, str]] = []
    unique_sets: dict[str, set[str]] = {col: set() for col in headers}

    for row_idx, raw_row in enumerate(data_rows, start=1):
        if len(raw_row) != expected_width:
            raise ValueError(
                f"Malformed CSV row {row_idx}: expected {expected_width} columns, got {len(raw_row)}."
            )
        record: dict[str, str] = {}
        for col, val in zip(headers, raw_row):
            normalized = val.strip() if val.strip() != "" else "<MISSING>"
            record[col] = normalized
            unique_sets[col].add(normalized)
        dict_rows.append(record)

    if not dict_rows:
        raise ValueError("CSV contains headers but zero data rows.")

    unique_values = {col: sorted(vals) for col, vals in unique_sets.items()}
    default_target = detect_default_target(headers)

    return DatasetBundle(
        dataset_id=dataset_id,
        name=name,
        source=source,
        columns=headers,
        rows=dict_rows,
        default_target=default_target,
        unique_values_per_column=unique_values,
        has_synthetic_header=synthetic,
    )


def load_csv_from_path(
    path: str | Path,
    dataset_id: str | None = None,
    name: str | None = None,
    source: str = "builtin",
) -> DatasetBundle:
    """Load a CSV file from disk into a DatasetBundle."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    text = file_path.read_text(encoding="utf-8", errors="replace")
    resolved_id = dataset_id or file_path.stem
    resolved_name = name or file_path.stem.replace("_", " ").title()
    return load_csv_from_text(text=text, dataset_id=resolved_id, name=resolved_name, source=source)


def list_builtin_datasets(datasets_dir: str | Path) -> dict[str, DatasetBundle]:
    """Scan a directory for *.csv datasets and load them keyed by dataset_id."""
    root = Path(datasets_dir)
    bundles: dict[str, DatasetBundle] = {}
    if not root.is_dir():
        return bundles
    for csv_path in sorted(root.glob("*.csv")):
        bundle = load_csv_from_path(csv_path, dataset_id=csv_path.stem, source="builtin")
        bundles[bundle.dataset_id] = bundle
    return bundles


def stratified_train_test_split(
    rows: Sequence[dict[str, str]],
    target_column: str,
    test_size: float = 0.2,
    random_seed: int = 42,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Pure-Python stratified train/test split preserving class proportions."""
    if not rows:
        raise ValueError("Cannot split an empty dataset.")
    if not 0.0 <= test_size < 1.0:
        raise ValueError("test_size must be in [0.0, 1.0).")
    if target_column not in rows[0]:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")

    if test_size == 0.0:
        return [dict(r) for r in rows], []

    by_class: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_class.setdefault(row[target_column], []).append(dict(row))

    rng = random.Random(random_seed)
    train_rows: list[dict[str, str]] = []
    test_rows: list[dict[str, str]] = []

    for label in sorted(by_class):
        group = by_class[label]
        rng.shuffle(group)
        if len(group) == 1:
            train_rows.extend(group)
            continue
        n_test = round(len(group) * test_size)
        n_test = max(1, min(len(group) - 1, n_test))
        test_rows.extend(group[:n_test])
        train_rows.extend(group[n_test:])

    rng.shuffle(train_rows)
    rng.shuffle(test_rows)
    return train_rows, test_rows
