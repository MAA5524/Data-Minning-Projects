"""Eclat Association Rule Mining & Pattern Evaluation Package.

Based on Chapter 4 of 'Data Mining: Concepts and Techniques' (Han, Pei, Tong).
"""

from src.eclat import eclat
from src.loader import TransactionData, load_dataset
from src.metrics import evaluate_rules, kulczynski, lift
from src.rules import generate_association_rules

__all__ = [
    "load_dataset",
    "TransactionData",
    "eclat",
    "generate_association_rules",
    "evaluate_rules",
    "lift",
    "kulczynski",
]
