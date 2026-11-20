"""
src/up_tree.py
UP-Tree (Utility Pattern Tree) and UPNode data structures
for High Utility Itemset Mining (UP-Growth / IHUP-TWU).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple


class UPNode:
    """
    Node in a UP-Tree.
    Stores item identifier, frequency count, accumulated node utility,
    pointers to parent and children, and horizontal node-link for header traversal.
    """
    __slots__ = ("item_id", "count", "node_utility", "parent", "children", "node_link")

    def __init__(
        self,
        item_id: Optional[int],
        count: int = 0,
        node_utility: float = 0.0,
        parent: Optional[UPNode] = None,
    ):
        self.item_id: Optional[int] = item_id
        self.count: int = count
        self.node_utility: float = node_utility
        self.parent: Optional[UPNode] = parent
        self.children: Dict[int, UPNode] = {}
        self.node_link: Optional[UPNode] = None

    def __repr__(self) -> str:
        return f"UPNode(item={self.item_id}, count={self.count}, nu={self.node_utility:.1f})"


class HeaderEntry:
    """
    Entry in the HeaderTable representing an item, its cumulative TWU/utility,
    and pointers to the head and tail of the node-link chain.
    """
    __slots__ = ("item_id", "twu", "head", "tail")

    def __init__(self, item_id: int, twu: float = 0.0):
        self.item_id: int = item_id
        self.twu: float = twu
        self.head: Optional[UPNode] = None
        self.tail: Optional[UPNode] = None

    def append_node(self, node: UPNode) -> None:
        """Appends a new node to the horizontal node-link list in O(1)."""
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.node_link = node
            self.tail = node


class UPTree:
    """
    Utility Pattern Tree (UP-Tree).
    Maintains the hierarchical tree structure and a header table for bottom-up DFS mining.
    """

    def __init__(self, rank_map: Optional[Dict[int, int]] = None):
        self.root: UPNode = UPNode(item_id=None)
        self.header_table: Dict[int, HeaderEntry] = {}
        # rank_map determines the topological ordering of items in paths (descending TWU)
        self.rank_map: Dict[int, int] = rank_map or {}

    def insert(self, items: List[int], utility: float, count: int = 1) -> None:
        """
        Inserts a transaction path into the UP-Tree.
        items must already be sorted according to self.rank_map.
        """
        curr = self.root
        for item in items:
            if item in curr.children:
                child = curr.children[item]
                child.count += count
                child.node_utility += utility
            else:
                child = UPNode(
                    item_id=item,
                    count=count,
                    node_utility=utility,
                    parent=curr,
                )
                curr.children[item] = child

                # Ensure item exists in header table and link node
                if item not in self.header_table:
                    self.header_table[item] = HeaderEntry(item_id=item)
                self.header_table[item].append_node(child)

            curr = child

    def get_prefix_paths(
        self, item_id: int
    ) -> Tuple[float, List[Tuple[List[int], float, int]]]:
        """
        Extracts the conditional pattern base for item_id:
        Returns:
            total_utility: Total accumulated node utility across all nodes of item_id.
            prefix_paths: List of (path_ancestors, path_utility, path_count).
        """
        entry = self.header_table.get(item_id)
        if not entry or entry.head is None:
            return 0.0, []

        total_utility = 0.0
        prefix_paths: List[Tuple[List[int], float, int]] = []
        curr: Optional[UPNode] = entry.head

        while curr is not None:
            total_utility += curr.node_utility
            # Walk up to root to collect prefix ancestors
            path: List[int] = []
            p = curr.parent
            while p is not None and p.item_id is not None:
                path.append(p.item_id)
                p = p.parent

            if path:
                path.reverse()  # from highest rank to lowest rank
                prefix_paths.append((path, curr.node_utility, curr.count))

            curr = curr.node_link

        return total_utility, prefix_paths
