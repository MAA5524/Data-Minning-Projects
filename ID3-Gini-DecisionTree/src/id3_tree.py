"""Recursive ID3-Gini Decision Tree Classifier, Prediction & Rule Extraction."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from .gini import best_gini_split, gini_impurity


def _majority_label(labels: Sequence[str]) -> str:
    """Return the most frequent class label with deterministic alphabetical tie-breaking."""
    counts = Counter(labels)
    return min(counts.items(), key=lambda item: (-item[1], item[0]))[0]


@dataclass
class TreeNode:
    """Node in the multiway ID3-Gini decision tree."""

    node_id: int
    is_leaf: bool
    majority_class: str
    prediction: str
    gini: float
    samples: int
    class_distribution: dict[str, int]
    depth: int
    attribute: Optional[str] = None
    weighted_gini: Optional[float] = None
    delta_gini: float = 0.0
    children: dict[str, TreeNode] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Export subtree to a JSON-serializable nested dictionary."""
        return {
            "node_id": self.node_id,
            "is_leaf": self.is_leaf,
            "attribute": self.attribute,
            "prediction": self.prediction,
            "majority_class": self.majority_class,
            "gini": round(self.gini, 6),
            "weighted_gini": round(self.weighted_gini, 6) if self.weighted_gini is not None else None,
            "delta_gini": round(self.delta_gini, 6),
            "samples": self.samples,
            "class_distribution": dict(sorted(self.class_distribution.items())),
            "depth": self.depth,
            "children": {
                branch_val: child.to_dict() for branch_val, child in self.children.items()
            },
        }


class ID3GiniClassifier:
    """Top-down recursive ID3 Decision Tree using the Gini Index split criterion."""

    def __init__(
        self,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
    ) -> None:
        if max_depth is not None and max_depth < 0:
            raise ValueError("max_depth must be non-negative or None.")
        if min_samples_split < 2:
            raise ValueError("min_samples_split must be at least 2.")
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split

        self.root: Optional[TreeNode] = None
        self.target_column: str = ""
        self.feature_columns: list[str] = []
        self.attribute_domains: dict[str, list[str]] = {}
        self._next_node_id: int = 0

    def _allocate_id(self) -> int:
        node_id = self._next_node_id
        self._next_node_id += 1
        return node_id

    def fit(
        self,
        rows: Sequence[Mapping[str, str]],
        target_column: str,
        feature_columns: Optional[Sequence[str]] = None,
        attribute_domains: Optional[Mapping[str, Sequence[str]]] = None,
    ) -> ID3GiniClassifier:
        """Induce an ID3-Gini decision tree from training rows."""
        if not rows:
            raise ValueError("Cannot fit ID3GiniClassifier on empty training data.")
        if target_column not in rows[0]:
            raise ValueError(f"Target column '{target_column}' not present in training data.")

        self.target_column = target_column
        if feature_columns is None:
            self.feature_columns = [col for col in rows[0].keys() if col != target_column]
        else:
            self.feature_columns = [col for col in feature_columns if col != target_column]

        if not self.feature_columns:
            raise ValueError("At least one feature column is required to train the tree.")

        # Collect discrete domain values for each feature column from training data
        # (merged with optional full-dataset domain if supplied).
        self.attribute_domains = {}
        for attr in self.feature_columns:
            vals = {str(row[attr]) for row in rows}
            if attribute_domains and attr in attribute_domains:
                vals.update(str(v) for v in attribute_domains[attr])
            self.attribute_domains[attr] = sorted(vals)

        self._next_node_id = 0
        normalized_rows = [{k: str(v) for k, v in row.items()} for row in rows]
        self.root = self._generate_decision_tree(
            rows=normalized_rows,
            candidate_attributes=list(self.feature_columns),
            depth=0,
        )
        return self

    def _make_leaf(
        self,
        label: str,
        gini: float,
        samples: int,
        class_distribution: dict[str, int],
        depth: int,
    ) -> TreeNode:
        return TreeNode(
            node_id=self._allocate_id(),
            is_leaf=True,
            majority_class=label,
            prediction=label,
            gini=gini,
            samples=samples,
            class_distribution=class_distribution,
            depth=depth,
        )

    def _generate_decision_tree(
        self,
        rows: list[dict[str, str]],
        candidate_attributes: list[str],
        depth: int,
    ) -> TreeNode:
        labels = [row[self.target_column] for row in rows]
        counts = dict(sorted(Counter(labels).items()))
        majority = _majority_label(labels)
        node_gini = gini_impurity(labels)
        n_samples = len(rows)

        # Stopping criterion 1: All samples belong to the same class C
        if len(counts) == 1:
            return self._make_leaf(
                label=majority,
                gini=node_gini,
                samples=n_samples,
                class_distribution=counts,
                depth=depth,
            )

        # Stopping criterion 2 & 3: No attributes left, max_depth reached, or too few samples
        if (
            not candidate_attributes
            or (self.max_depth is not None and depth >= self.max_depth)
            or n_samples < self.min_samples_split
        ):
            return self._make_leaf(
                label=majority,
                gini=node_gini,
                samples=n_samples,
                class_distribution=counts,
                depth=depth,
            )

        split_result = best_gini_split(rows, candidate_attributes, self.target_column)
        best_attr: str = split_result["best_attribute"]
        partitions: dict[str, list[dict[str, str]]] = split_result["partitions"]

        node = TreeNode(
            node_id=self._allocate_id(),
            is_leaf=False,
            majority_class=majority,
            prediction=majority,
            gini=split_result["parent_gini"],
            weighted_gini=split_result["best_gini_a"],
            delta_gini=split_result["best_delta_gini"],
            samples=n_samples,
            class_distribution=counts,
            depth=depth,
            attribute=best_attr,
            children={},
        )

        remaining_attributes = [attr for attr in candidate_attributes if attr != best_attr]
        domain_values = self.attribute_domains.get(best_attr) or sorted(partitions.keys())

        for val in domain_values:
            sub_rows = partitions.get(val, [])
            # Stopping criterion 4: Partition D_v is empty -> attach leaf with parent majority class
            if not sub_rows:
                node.children[val] = self._make_leaf(
                    label=majority,
                    gini=0.0,
                    samples=0,
                    class_distribution={},
                    depth=depth + 1,
                )
            else:
                node.children[val] = self._generate_decision_tree(
                    rows=sub_rows,
                    candidate_attributes=remaining_attributes,
                    depth=depth + 1,
                )

        return node

    def predict_with_trace(self, sample: Mapping[str, Any]) -> dict[str, Any]:
        """Predict class for a single sample and return the root-to-leaf decision path."""
        if self.root is None:
            raise RuntimeError("Model has not been trained yet. Call fit() first.")

        node = self.root
        path: list[dict[str, Any]] = []
        path_node_ids: list[int] = [node.node_id]
        unseen_fallback = False

        while not node.is_leaf:
            assert node.attribute is not None
            raw_val = sample.get(node.attribute, "")
            val = str(raw_val).strip()

            if val in node.children:
                child = node.children[val]
                path.append(
                    {
                        "node_id": node.node_id,
                        "attribute": node.attribute,
                        "value": val,
                        "next_node_id": child.node_id,
                        "gini": round(node.gini, 6),
                        "samples": node.samples,
                        "majority_class": node.majority_class,
                        "is_fallback": False,
                    }
                )
                node = child
                path_node_ids.append(node.node_id)
            else:
                # Graceful fallback to node's majority_class when encountering an unseen value
                unseen_fallback = True
                path.append(
                    {
                        "node_id": node.node_id,
                        "attribute": node.attribute,
                        "value": val if val != "" else "<MISSING>",
                        "next_node_id": None,
                        "gini": round(node.gini, 6),
                        "samples": node.samples,
                        "majority_class": node.majority_class,
                        "is_fallback": True,
                    }
                )
                return {
                    "prediction": node.majority_class,
                    "path": path,
                    "path_node_ids": path_node_ids,
                    "unseen_fallback": unseen_fallback,
                }

        return {
            "prediction": node.prediction,
            "path": path,
            "path_node_ids": path_node_ids,
            "unseen_fallback": unseen_fallback,
        }

    def predict_one(self, sample: Mapping[str, Any]) -> str:
        """Predict the class label for a single sample."""
        return self.predict_with_trace(sample)["prediction"]

    def predict(self, samples: Sequence[Mapping[str, Any]]) -> list[str]:
        """Predict class labels for a batch of samples."""
        return [self.predict_one(sample) for sample in samples]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the fitted tree to a nested dictionary."""
        if self.root is None:
            raise RuntimeError("Model has not been trained yet. Call fit() first.")
        return self.root.to_dict()

    def extract_rules(self, include_empty_branches: bool = False) -> list[dict[str, Any]]:
        """Traverse root-to-leaf paths and extract human-readable IF-THEN rules."""
        if self.root is None:
            raise RuntimeError("Model has not been trained yet. Call fit() first.")

        rules: list[dict[str, Any]] = []

        def _dfs(node: TreeNode, conditions: list[dict[str, str]]) -> None:
            if node.is_leaf:
                if node.samples == 0 and not include_empty_branches:
                    return
                correct_count = node.class_distribution.get(node.prediction, 0)
                purity = (correct_count / node.samples) if node.samples > 0 else 1.0
                if conditions:
                    cond_str = " AND ".join(
                        f"{cond['attribute']} = {cond['value']}" for cond in conditions
                    )
                else:
                    cond_str = "TRUE"
                rule_text = (
                    f"IF {cond_str} THEN {self.target_column} = {node.prediction} "
                    f"(samples={node.samples}, purity={purity * 100:.1f}%)"
                )
                rules.append(
                    {
                        "rule_id": len(rules) + 1,
                        "conditions": list(conditions),
                        "prediction": node.prediction,
                        "samples": node.samples,
                        "correct_count": correct_count,
                        "purity": round(purity, 6),
                        "text": rule_text,
                    }
                )
                return

            assert node.attribute is not None
            for branch_val, child in node.children.items():
                conditions.append({"attribute": node.attribute, "value": branch_val})
                _dfs(child, conditions)
                conditions.pop()

        _dfs(self.root, [])
        return rules

    def tree_stats(self) -> dict[str, int]:
        """Return structural counts: tree_depth, total_nodes, leaf_nodes, internal_nodes."""
        if self.root is None:
            raise RuntimeError("Model has not been trained yet. Call fit() first.")

        total_nodes = 0
        leaf_nodes = 0
        max_depth = 0

        def _walk(node: TreeNode) -> None:
            nonlocal total_nodes, leaf_nodes, max_depth
            total_nodes += 1
            max_depth = max(max_depth, node.depth)
            if node.is_leaf:
                leaf_nodes += 1
            else:
                for child in node.children.values():
                    _walk(child)

        _walk(self.root)
        return {
            "tree_depth": max_depth,
            "total_nodes": total_nodes,
            "leaf_nodes": leaf_nodes,
            "internal_nodes": total_nodes - leaf_nodes,
        }
