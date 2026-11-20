"""
src/loader.py
Fast loader for unified utility CSV files and raw SPMF datasets.
Constructs and returns structured UtilityDatabase dataclasses.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Union


@dataclass
class UtilityDatabase:
    """
    Structured in-memory representation of a utility database.
    """
    transactions: List[Dict[int, float]]
    transaction_utilities: List[float]
    total_utility: float
    item_names: Dict[int, str]
    inverted_index: Dict[int, Set[int]]

    @property
    def num_transactions(self) -> int:
        return len(self.transactions)

    @property
    def num_items(self) -> int:
        return len(self.item_names)

    def get_item_name(self, item_id: int) -> str:
        return self.item_names.get(item_id, f"Product #{item_id}")

    def compute_twus(self) -> Dict[int, float]:
        """
        Computes Transaction-Weighted Utility (TWU) for every item:
        TWU(i) = sum_{T containing i} TU(T)
        """
        twus: Dict[int, float] = {}
        for item_id, tids in self.inverted_index.items():
            twus[item_id] = sum(self.transaction_utilities[tid] for tid in tids)
        return twus


def load_utility_csv(
    file_source: Union[str, Path, io.StringIO, io.TextIOBase]
) -> UtilityDatabase:
    """
    Loads unified CSV data.
    Supported headers:
    1. transaction_id,item_id,item_name,utility
    2. transaction_id,item_name,utility (item_id assigned automatically)
    """
    if isinstance(file_source, (str, Path)):
        f = open(file_source, mode="r", encoding="utf-8", errors="replace")
        should_close = True
    else:
        f = file_source
        should_close = False

    try:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            raise ValueError("CSV file is empty")

        clean_header = [col.strip().lower() for col in header]
        col_map = {name: idx for idx, name in enumerate(clean_header)}

        has_tid = "transaction_id" in col_map
        has_item_id = "item_id" in col_map
        has_item_name = "item_name" in col_map
        has_utility = "utility" in col_map

        if not (has_tid and has_utility and (has_item_id or has_item_name)):
            raise ValueError(
                f"Invalid CSV header. Expected at least (transaction_id, [item_id and/or item_name], utility). "
                f"Got: {header}"
            )

        tid_idx = col_map["transaction_id"]
        util_idx = col_map["utility"]
        iid_idx = col_map.get("item_id")
        name_idx = col_map.get("item_name")

        tx_list: List[Dict[int, float]] = []
        tid_to_index: Dict[str, int] = {}
        item_names: Dict[int, str] = {}
        name_to_id: Dict[str, int] = {}
        next_auto_id = 1

        for row in reader:
            if not row or len(row) <= max(tid_idx, util_idx):
                continue

            raw_tid = row[tid_idx].strip()
            if not raw_tid:
                continue

            try:
                utility_val = float(row[util_idx].strip())
            except ValueError:
                continue

            # Determine item_id and item_name
            if iid_idx is not None and len(row) > iid_idx and row[iid_idx].strip():
                try:
                    item_id = int(row[iid_idx].strip())
                except ValueError:
                    # Non-integer ID, map to unique integer
                    item_str = row[iid_idx].strip()
                    if item_str not in name_to_id:
                        name_to_id[item_str] = next_auto_id
                        next_auto_id += 1
                    item_id = name_to_id[item_str]

                if name_idx is not None and len(row) > name_idx and row[name_idx].strip():
                    item_name = row[name_idx].strip()
                else:
                    item_name = f"Product #{item_id}"
            else:
                item_name = row[name_idx].strip() if (name_idx is not None and len(row) > name_idx) else "Unknown"
                if item_name not in name_to_id:
                    name_to_id[item_name] = next_auto_id
                    next_auto_id += 1
                item_id = name_to_id[item_name]

            if item_id not in item_names:
                item_names[item_id] = item_name

            if raw_tid not in tid_to_index:
                tid_to_index[raw_tid] = len(tx_list)
                tx_list.append({})

            internal_tid = tid_to_index[raw_tid]
            # Accumulate if item appears multiple times in transaction
            tx_list[internal_tid][item_id] = tx_list[internal_tid].get(item_id, 0.0) + utility_val

    finally:
        if should_close:
            f.close()

    return _build_utility_database(tx_list, item_names)


def load_spmf_txt(
    file_source: Union[str, Path, io.StringIO, io.TextIOBase]
) -> UtilityDatabase:
    """
    Loads raw SPMF utility dataset (.txt).
    Format per line: item1 item2 ... :TU:utility1 utility2 ...
    Metadata lines starting with @ITEM=<id>=<name> are parsed for names.
    """
    if isinstance(file_source, (str, Path)):
        f = open(file_source, mode="r", encoding="utf-8", errors="replace")
        should_close = True
    else:
        f = file_source
        should_close = False

    try:
        tx_list: List[Dict[int, float]] = []
        item_names: Dict[int, str] = {}

        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("@ITEM="):
                parts = line[6:].split("=", 1)
                if len(parts) == 2:
                    try:
                        iid = int(parts[0].strip())
                        item_names[iid] = parts[1].strip()
                    except ValueError:
                        pass
                continue

            if line.startswith("@"):
                continue

            parts = line.split(":")
            if len(parts) < 3:
                continue

            item_strs = parts[0].strip().split()
            util_strs = parts[2].strip().split()
            if len(item_strs) != len(util_strs):
                continue

            tx: Dict[int, float] = {}
            for i_str, u_str in zip(item_strs, util_strs):
                try:
                    iid = int(i_str)
                    u_val = float(u_str)
                    tx[iid] = tx.get(iid, 0.0) + u_val
                    if iid not in item_names:
                        item_names[iid] = f"Product #{iid}"
                except ValueError:
                    continue

            if tx:
                tx_list.append(tx)

    finally:
        if should_close:
            f.close()

    return _build_utility_database(tx_list, item_names)


def _build_utility_database(
    tx_list: List[Dict[int, float]], item_names: Dict[int, str]
) -> UtilityDatabase:
    """
    Builds transaction_utilities, total_utility, and inverted_index.
    """
    transaction_utilities: List[float] = []
    inverted_index: Dict[int, Set[int]] = {iid: set() for iid in item_names}
    total_utility = 0.0

    for tid, tx in enumerate(tx_list):
        tu = sum(tx.values())
        transaction_utilities.append(tu)
        total_utility += tu
        for item_id in tx:
            if item_id not in inverted_index:
                inverted_index[item_id] = set()
            inverted_index[item_id].add(tid)

    return UtilityDatabase(
        transactions=tx_list,
        transaction_utilities=transaction_utilities,
        total_utility=total_utility,
        item_names=item_names,
        inverted_index=inverted_index,
    )
