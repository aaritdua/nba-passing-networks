from __future__ import annotations
from typing import Any, Optional

class Tree:
    """A recursive tree data structure representing a passing network for a single nba game. 

    Each node of this tree represents a player involved in the game, with the root being the player who initiated the play.

    Child nodes represent the players that have received a pass from this Tree's player and Leaf nodes represent either a shot attempt or turnover.

    Representation Invariants:
        - self._root is not None or self._subtrees == []
    """
    # Private Instance Attributes:
    #   - _root:
    #       The name of the NBA player represented by this Tree, or "Shot"/"Turnover" in the event of a leaf node.
    #   - _subtrees:
    #       The list of subtrees of this tree. Each subtree represents either a player, turnover or shot attempt.
    _root: str 
    _subtrees: list[Tree]


    def __init__(self, root: Any, subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def add_player(self, player: str) -> None:
        """Add a player, turnover or shot attempt as a node."""
        self._subtrees.append(Tree(player, []))

    def add_shot(self) -> None:
        """Add a shot attempt as a leaf node."""
        self._subtrees.append(Tree("Shot", []))

    def add_turnover(self) -> None:
        """Add a turnover as a leaf node."""
        self._subtrees.append(Tree("Turnover", []))

    def find_all(self, target: str) -> list[Tree]:
        """Return ALL subtrees whose root is target."""
        matches = []

        if self._root == target:
            matches.append(self)

        for child in self._subtrees:
            matches.extend(child.find_all(target))

        return matches

    def _get_all_paths(self) -> list[list[str]]:
        """Return all paths from this node to leaves."""
        if not self._subtrees:
            return [[self._root]]

        paths = []
        for child in self._subtrees:
            for subpath in child._get_all_paths():
                paths.append([self._root] + subpath)
        return paths
    
    def print_sequences_from(self, player: str) -> None:
        """Print ALL pass sequences starting from every occurrence of player."""
        nodes = self.find_all(player)

        if not nodes:
            print(f"Player '{player}' not found in tree.")
            return

        for node in nodes:
            paths = node._get_all_paths()
            for path in paths:
                print(" -> ".join(path))

    def add_path(self, path: list[str]) -> None:
        """Add a pass sequence to the tree.

        Preconditions:
            - path[0] == self.value
        """
        current = self

        for i in range(1, len(path)):
            player = path[i]
            # Check if child already exists
            found = None
            for node in current._subtrees:
                if node._root == player:
                    found = node
                    break

            if found is None:
                new_node = Tree(player, [])
                current._subtrees.append(new_node)
                current = new_node
            else:
                current = found

    def max_depth(self) -> int:
        """Return the maximum depth of the tree."""
        if not self._subtrees:
            return 1

        return 1 + max(child.max_depth() for child in self._subtrees)

    def _leaf_depths(self, depth: int) -> list[int]:
        """Return depths of all leaves."""
        if not self._subtrees:
            return [depth]

        depths = []
        for child in self._subtrees:
            depths.extend(child._leaf_depths(depth + 1))
        return depths

    def average_depth(self) -> float:
        """Return average depth of all leaves (possession endings)."""
        depths = self._leaf_depths(1)
        return sum(depths) / len(depths)
    
    def _node_degrees(self) -> list[int]:
        """Return number of children for all nodes."""
        degrees = [len(self._subtrees)]

        for child in self._subtrees:
            degrees.extend(child._node_degrees())

        return degrees

    def average_branching_factor(self) -> float:
        """Return average number of children per node."""
        degrees = self._node_degrees()
        return sum(degrees) / len(degrees)
    
    def dfs(self) -> list[str]:
        """Return a DFS traversal of the tree."""
        nodes = [self._root]

        for child in self._subtrees:
            if child._root in ["Shot", "Turnover"]:
                nodes += child.dfs()
                nodes += ["END OF POSSESSION"]
            else:
                nodes += child.dfs()

        return nodes