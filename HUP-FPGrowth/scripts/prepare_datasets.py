#!/usr/bin/env python3
"""
scripts/prepare_datasets.py
Converts raw SPMF-format dataset files in datasets/raw/ into unified,
clean, human-readable CSV files in datasets/processed/.

Schema:
transaction_id,item_id,item_name,utility
"""

import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "datasets" / "raw"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"


def parse_spmf_line(line: str):
    """
    Parses a single line of an SPMF utility dataset.
    Format: item1 item2 ... :TU:utility1 utility2 ...
    Returns (item_ids, utilities) as lists of ints/floats.
    """
    line = line.strip()
    if not line or line.startswith(("#", "@")):
        return None, None

    parts = line.split(":")
    if len(parts) < 3:
        return None, None

    item_ids = [int(x) for x in parts[0].strip().split()]
    utilities = [float(x) for x in parts[2].strip().split()]

    if len(item_ids) != len(utilities):
        raise ValueError(f"Mismatch in item count ({len(item_ids)}) vs utility count ({len(utilities)}): {line}")

    return item_ids, utilities


def load_item_names(names_file: Path) -> dict[int, str]:
    """
    Loads item id -> item name mappings from SPMF metadata file.
    Format: @ITEM=<item_id>=<item_name>
    """
    names = {}
    if not names_file.exists():
        return names

    with open(names_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("@ITEM="):
                parts = line[len("@ITEM="):].split("=", 1)
                if len(parts) == 2:
                    try:
                        item_id = int(parts[0].strip())
                        item_name = parts[1].strip()
                        names[item_id] = item_name
                    except ValueError:
                        continue
    return names


def convert_dataset(
    raw_spmf_file: Path,
    output_csv_file: Path,
    item_names: dict[int, str] | None = None,
    default_name_prefix: str = "Product #",
) -> tuple[int, int]:
    """
    Converts a raw SPMF dataset into unified CSV format.
    Returns (total_transactions, total_records).
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if item_names is None:
        item_names = {}

    total_transactions = 0
    total_records = 0

    with open(raw_spmf_file, "r", encoding="utf-8", errors="replace") as in_f, \
         open(output_csv_file, "w", newline="", encoding="utf-8") as out_f:

        writer = csv.writer(out_f)
        writer.writerow(["transaction_id", "item_id", "item_name", "utility"])

        for line in in_f:
            item_ids, utilities = parse_spmf_line(line)
            if item_ids is None:
                continue

            total_transactions += 1
            tid = total_transactions

            for item_id, utility in zip(item_ids, utilities):
                # Format utility as int if it's an integer value, else float
                util_val = int(utility) if utility.is_integer() else utility
                name = item_names.get(item_id, f"{default_name_prefix}{item_id}")
                writer.writerow([tid, item_id, name, util_val])
                total_records += 1

    return total_transactions, total_records


def main():
    print(f"Preparing datasets from: {RAW_DIR}")
    print(f"Target directory: {PROCESSED_DIR}")

    # 1. E-Commerce Dataset
    ecom_raw = RAW_DIR / "ecommerce_utility.txt"
    ecom_names_file = RAW_DIR / "ecommerce_item_names.txt"
    ecom_out = PROCESSED_DIR / "ecommerce_utility.csv"

    if ecom_raw.exists():
        print(f"Loading names from {ecom_names_file.name}...")
        ecom_names = load_item_names(ecom_names_file)
        print(f"Loaded {len(ecom_names)} item names.")

        print(f"Converting {ecom_raw.name} -> {ecom_out.name}...")
        tx_count, rec_count = convert_dataset(
            raw_spmf_file=ecom_raw,
            output_csv_file=ecom_out,
            item_names=ecom_names,
            default_name_prefix="Product #"
        )
        print(f"Done: {tx_count:,} transactions, {rec_count:,} item records written to {ecom_out.name}.")
    else:
        print(f"Warning: {ecom_raw} not found!", file=sys.stderr)

    # 2. Foodmart Dataset
    foodmart_raw = RAW_DIR / "foodmart_utility.txt"
    foodmart_out = PROCESSED_DIR / "foodmart_utility.csv"

    if foodmart_raw.exists():
        print(f"Converting {foodmart_raw.name} -> {foodmart_out.name}...")
        tx_count, rec_count = convert_dataset(
            raw_spmf_file=foodmart_raw,
            output_csv_file=foodmart_out,
            item_names=None,
            default_name_prefix="Product #"
        )
        print(f"Done: {tx_count:,} transactions, {rec_count:,} item records written to {foodmart_out.name}.")
    else:
        print(f"Warning: {foodmart_raw} not found!", file=sys.stderr)

    print("\nDataset preparation successfully completed!")


if __name__ == "__main__":
    main()
