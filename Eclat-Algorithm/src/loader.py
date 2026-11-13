"""Dataset loader for Association Rule Mining.

Supports automatic format detection:
1. Format A (Long/Transactional): e.g., Member_number, Date, itemDescription.
2. Format B (Horizontal Basket): One transaction per row, comma-separated.

Converts transaction baskets into the Vertical Data Format (item -> set of TIDs).
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class TransactionData:
    """Encapsulates transactional data in both vertical and horizontal formats."""

    tid_lists: dict[str, set[int]]
    total_transactions: int
    items: list[str]
    transactions: list[set[str]]
    format_detected: str


def _get_text_stream(source: Any) -> io.StringIO:
    """Convert various file sources (path, bytes, UploadedFile) into a StringIO."""
    if isinstance(source, (str, Path)):
        with open(source, mode="r", encoding="utf-8-sig", errors="replace") as f:
            return io.StringIO(f.read())
    elif hasattr(source, "getvalue"):
        # Streamlit UploadedFile or BytesIO
        raw = source.getvalue()
        if isinstance(raw, bytes):
            return io.StringIO(raw.decode("utf-8-sig", errors="replace"))
        return io.StringIO(str(raw))
    elif hasattr(source, "read"):
        pos = getattr(source, "tell", lambda: None)()
        raw = source.read()
        if pos is not None and hasattr(source, "seek"):
            source.seek(pos)
        if isinstance(raw, bytes):
            return io.StringIO(raw.decode("utf-8-sig", errors="replace"))
        return io.StringIO(str(raw))
    else:
        raise ValueError(f"Unsupported data source type: {type(source)}")


def load_dataset(source: Any) -> TransactionData:
    """Load a dataset from a file path or file-like object and convert to Vertical Data Format.

    Parameters
    ----------
    source : str, Path, or file-like object
        Path to CSV file or file buffer (e.g. Streamlit UploadedFile).

    Returns
    -------
    TransactionData
        Data container containing vertical tid_lists, total count, items, and transactions.
    """
    stream = _get_text_stream(source)
    content = stream.getvalue()

    if not content.strip():
        return TransactionData(
            tid_lists={},
            total_transactions=0,
            items=[],
            transactions=[],
            format_detected="Empty Dataset",
        )

    # 1. Try to detect Format A (Long/Transactional format)
    # Check header
    first_line = content.splitlines()[0] if content.splitlines() else ""
    header_cols = [c.strip().strip('"').strip("'").lower() for c in first_line.split(",")]

    is_long_format = False
    member_col = None
    date_col = None
    item_col = None

    for col in header_cols:
        col_clean = col.replace("_", "").replace(" ", "").replace("-", "")
        if "member" in col_clean or "cust" in col_clean or "user" in col_clean:
            member_col = col
        elif "date" in col_clean or "time" in col_clean or "day" in col_clean:
            date_col = col
        elif "item" in col_clean or "prod" in col_clean or "article" in col_clean or "desc" in col_clean:
            item_col = col

    # Check specifically for standard Groceries dataset column names
    if "member_number" in header_cols and "date" in header_cols and "itemdescription" in header_cols:
        is_long_format = True
        member_col = "member_number"
        date_col = "date"
        item_col = "itemdescription"
    elif member_col and date_col and item_col:
        is_long_format = True

    transactions: list[set[str]] = []
    format_name = "Horizontal Basket"

    if is_long_format:
        format_name = "Long / Transactional (Member + Date)"
        df = pd.read_csv(io.StringIO(content))
        # Find exact case column names matching detected lower-case names
        col_map = {c.strip().lower(): c for c in df.columns}
        actual_member = col_map.get(member_col, df.columns[0])
        actual_date = col_map.get(date_col, df.columns[1])
        actual_item = col_map.get(item_col, df.columns[2])

        df = df.dropna(subset=[actual_item])
        # Clean item strings
        df[actual_item] = df[actual_item].astype(str).str.strip()
        df = df[df[actual_item] != ""]

        # Group by (Member, Date) to form baskets
        grouped = df.groupby([actual_member, actual_date])[actual_item].apply(lambda s: set(s.dropna()))
        for basket in grouped:
            if basket:
                transactions.append(basket)
    else:
        # Format B: Horizontal Basket Format (each line is a transaction)
        reader = csv.reader(io.StringIO(content))
        # Check if first line is a generic header like Item 1, Item 2, etc.
        lines = list(reader)
        if not lines:
            return TransactionData({}, 0, [], [], "Empty Dataset")

        start_idx = 0
        first_row_lower = [str(x).strip().lower() for x in lines[0]]
        # If row contains words like 'item 1' or 'item1', treat as header
        if any(w.startswith("item") or w.startswith("product") for w in first_row_lower):
            start_idx = 1

        for row in lines[start_idx:]:
            basket = set()
            for cell in row:
                item = str(cell).strip()
                if item and item.lower() not in {"nan", "null", "none", "na", ""}:
                    basket.add(item)
            if basket:
                transactions.append(basket)

    total_transactions = len(transactions)

    # Build Vertical Data Representation: item -> set of TIDs
    tid_lists: dict[str, set[int]] = {}
    for tid, basket in enumerate(transactions):
        for item in basket:
            if item not in tid_lists:
                tid_lists[item] = set()
            tid_lists[item].add(tid)

    # Sorted list of unique items
    items = sorted(tid_lists.keys())

    return TransactionData(
        tid_lists=tid_lists,
        total_transactions=total_transactions,
        items=items,
        transactions=transactions,
        format_detected=format_name,
    )
