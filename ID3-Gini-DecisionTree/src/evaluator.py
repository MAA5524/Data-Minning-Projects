"""Pure-Python Model Evaluator: Accuracy, Precision/Recall/F1, Confusion Matrix, Tree Stats."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .id3_tree import ID3GiniClassifier


def compute_accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    """Compute exact classification accuracy in [0.0, 1.0]."""
    if not y_true:
        return 0.0
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    return correct / len(y_true)


def compute_confusion_matrix(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str],
) -> list[list[int]]:
    """Build confusion matrix[true_idx][pred_idx] ordered by `labels`."""
    index_map = {label: idx for idx, label in enumerate(labels)}
    size = len(labels)
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    for t, p in zip(y_true, y_pred):
        if t in index_map and p in index_map:
            matrix[index_map[t]][index_map[p]] += 1
    return matrix


def compute_classification_metrics(
    matrix: Sequence[Sequence[int]],
    labels: Sequence[str],
) -> tuple[list[dict[str, Any]], float, float, float]:
    """Compute per-class and macro-averaged Precision, Recall, and F1-Score."""
    per_class: list[dict[str, Any]] = []
    n = len(labels)

    for idx, label in enumerate(labels):
        tp = matrix[idx][idx]
        fp = sum(matrix[r][idx] for r in range(n) if r != idx)
        fn = sum(matrix[idx][c] for c in range(n) if c != idx)
        support = sum(matrix[idx])

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            (2.0 * precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        per_class.append(
            {
                "label": label,
                "precision": round(precision, 6),
                "recall": round(recall, 6),
                "f1_score": round(f1, 6),
                "support": support,
            }
        )

    if not per_class:
        return [], 0.0, 0.0, 0.0

    macro_precision = sum(item["precision"] for item in per_class) / len(per_class)
    macro_recall = sum(item["recall"] for item in per_class) / len(per_class)
    macro_f1 = sum(item["f1_score"] for item in per_class) / len(per_class)
    return (
        per_class,
        round(macro_precision, 6),
        round(macro_recall, 6),
        round(macro_f1, 6),
    )


def evaluate_model(
    model: ID3GiniClassifier,
    train_rows: Sequence[Mapping[str, str]],
    test_rows: Sequence[Mapping[str, str]],
    target_column: str,
    training_time_ms: float,
    all_labels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Evaluate a fitted ID3GiniClassifier on train and test partitions."""
    train_true = [row[target_column] for row in train_rows]
    train_pred = model.predict(train_rows)
    train_accuracy = compute_accuracy(train_true, train_pred)

    eval_rows = test_rows if test_rows else train_rows
    test_true = [row[target_column] for row in eval_rows]
    test_pred = model.predict(eval_rows)
    test_accuracy = compute_accuracy(test_true, test_pred)

    label_set = set(train_true) | set(test_true) | set(test_pred)
    if all_labels:
        label_set.update(all_labels)
    labels = sorted(label_set)

    matrix = compute_confusion_matrix(test_true, test_pred, labels)
    per_class, macro_precision, macro_recall, macro_f1 = compute_classification_metrics(
        matrix, labels
    )
    stats = model.tree_stats()

    return {
        "train_accuracy": round(train_accuracy, 6),
        "test_accuracy": round(test_accuracy, 6),
        "labels": labels,
        "confusion_matrix": matrix,
        "per_class_metrics": per_class,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "tree_depth": stats["tree_depth"],
        "total_nodes": stats["total_nodes"],
        "leaf_nodes": stats["leaf_nodes"],
        "internal_nodes": stats["internal_nodes"],
        "training_time_ms": round(training_time_ms, 3),
        "train_samples": len(train_rows),
        "test_samples": len(test_rows),
    }
