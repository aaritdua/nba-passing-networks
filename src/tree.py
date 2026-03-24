from __future__ import annotations
from typing import Any

class Tree:
    """A recursive tree data structure representing a passing network for a single offensive possession. 

    Each node of this tree represents a player involved in the possession, with the root being the player who initiated the pass.

    Child nodes represent 

    Representation Invariants:
        - self._root is not None or self._subtrees == []
    """
    # Private Instance Attributes:
    #   - _root:
    #       The name of the NBA player represented by this Tree.
    #   - _subtrees:
    #       The list of subtrees of this tree. Each subtree represents all the player 
    _root: Any
    _subtrees: list[Tree]

    def __init__(self, root: Optional[Any], subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        If root is None, the tree is empty.

        Preconditions:
            - root is not none or subtrees == []
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.
        """
        return self._root is None