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
    #       The name of the NBA player represented by this Tree.
    #   - _subtrees:
    #       The list of subtrees of this tree. Each subtree represents a player, turnover or shot attempt.
    _root: str 
    _subtrees: Optional[list[Tree]]


    def __init__(self, root: Any, subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees
    
    def add_node(self, node: Tree) -> None:
        """Add a player, turnover or shot attempt as a node."""
        self._subtrees.append(node)

    def find(self, target: str) -> Tree | None:
        """Return the subtree whose root is target, else None."""
        if self._root == target:
            return self

        for node in self._subtrees:
            result = node.find(target)
            if result is not None:
                return result

        return None
    
    def print_path(self, path: list[str]) -> bool:
        """Print the given pass sequence if it exists."""
        if self._path_exists(path):
            print(" -> ".join(path))
            return True
        else:
            print("Path not found.")
            return False


    def _path_exists(self, path: list[str]) -> bool:
        """Return whether the path exists in the tree."""
        if not path or self._root != path[0]:
            return False

        if len(path) == 1:
            return True

        for child in self._subtrees:
            if child._root == path[1]:
                return child._path_exists(path[1:])

        return False
        
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
            nodes.extend(child.dfs())

        return nodes
    

# Root player starts possession
lebron = Tree("LeBron", [])

lebron.add_path(["LeBron", "AD", "Reaves", "Shot"])
lebron.add_path(["LeBron", "DLo", "AD", "Shot"])

lebron.print_path(["LeBron", "AD", "Reaves", "Shot"])
# Output:
# LeBron -> AD -> Reaves -> Shot

lebron.print_path(["LeBron", "AD", "Turnover"])
# Output:
# Path not found.

print(lebron.max_depth())  # e.g. 4
print(lebron.average_depth())
print(lebron.average_branching_factor())
