"""Pure-Python ID3 Decision Tree Classifier using the Gini Index."""

from .evaluator import evaluate_model
from .gini import best_gini_split, delta_gini, gini_impurity, weighted_gini_split
from .id3_tree import ID3GiniClassifier, TreeNode
from .loader import (
    DatasetBundle,
    detect_default_target,
    list_builtin_datasets,
    load_csv_from_path,
    load_csv_from_text,
    stratified_train_test_split,
)

__all__ = [
    "DatasetBundle",
    "ID3GiniClassifier",
    "TreeNode",
    "best_gini_split",
    "delta_gini",
    "detect_default_target",
    "evaluate_model",
    "gini_impurity",
    "list_builtin_datasets",
    "load_csv_from_path",
    "load_csv_from_text",
    "stratified_train_test_split",
    "weighted_gini_split",
]
