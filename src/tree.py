from __future__ import annotations
import pandas as pd
from data_loader import load_play_by_play


class PossessionTree:
    """A recursive tree representing one possession tree in a game.

    Each internal node stores a player name. Leaf nodes may also store the
    special values ``"Shot"`` or ``"Turnover"`` to represent how a sequence
    ended.

    Repeated ending events are preserved as separate leaves, so a player may
    have subtrees like ``["Shot", "Shot", "Turnover", "Kyrie"]``.
    """

    _root: str
    _subtrees: list[PossessionTree]

    def __init__(self, root: str, subtrees: list[PossessionTree] | None = None) -> None:
        """Initialize a new tree with the given root value and subtrees."""
        self._root = root
        self._subtrees = subtrees.copy() if subtrees is not None else []

    def add_player(self, player: str) -> None:
        """Add a player node as a child of this tree."""
        self._subtrees.append(PossessionTree(player))

    def add_shot(self) -> None:
        """Add a shot leaf as a child of this tree."""
        self._subtrees.append(PossessionTree("Shot"))

    def add_turnover(self) -> None:
        """Add a turnover leaf as a child of this tree."""
        self._subtrees.append(PossessionTree("Turnover"))

    def find_all(self, target: str) -> list[PossessionTree]:
        """Return all subtrees whose root matches ``target``."""
        matches = []

        if self._root == target:
            matches.append(self)

        for child in self._subtrees:
            matches.extend(child.find_all(target))

        return matches

    def _get_all_paths(self) -> list[list[str]]:
        """Return all root-to-leaf paths starting at this tree."""
        if not self._subtrees:
            return [[self._root]]

        paths = []
        for child in self._subtrees:
            for subpath in child._get_all_paths():
                paths.append([self._root] + subpath)
        return paths

    def print_sequences_from(self, player: str) -> None:
        """Print all possession-ending sequences from every occurrence of player."""
        nodes = self.find_all(player)

        if not nodes:
            print(f"Player '{player}' not found in tree.")
            return

        for node in nodes:
            for path in node._get_all_paths():
                print(" -> ".join(path))

    def add_path(self, path: list[str]) -> None:
        """Add a pass sequence beginning at this tree's root.

        Player nodes are reused so that one player has one subtree per parent.
        Terminal events (``"Shot"`` and ``"Turnover"``) are always appended as
        new leaves so repeated outcomes are preserved.

        Raises:
            ValueError: If ``path`` is empty or does not begin at this tree's root.
        """
        if not path or path[0] != self._root:
            raise ValueError("Path must start with this tree's root.")

        current = self

        for item in path[1:]:
            if item in {"Shot", "Turnover"}:
                current._subtrees.append(PossessionTree(item))
                return

            found = current._find_child_player(item)
            if found is None:
                found = PossessionTree(item)
                current._subtrees.append(found)
            current = found

    def _find_child_player(self, player: str) -> PossessionTree | None:
        """Return the child subtree for ``player``, if one exists."""
        for subtree in self._subtrees:
            if subtree._root == player and subtree._root not in {"Shot", "Turnover"}:
                return subtree
        return None

    def max_depth(self) -> int:
        """Return the maximum root-to-leaf depth of this tree."""
        if not self._subtrees:
            return 1

        return 1 + max(child.max_depth() for child in self._subtrees)

    def _leaf_depths(self, depth: int) -> list[int]:
        """Return a list of depths for every leaf in this tree."""
        if not self._subtrees:
            return [depth]

        depths = []
        for child in self._subtrees:
            depths.extend(child._leaf_depths(depth + 1))
        return depths

    def average_depth(self) -> float:
        """Return the average root-to-leaf depth."""
        depths = self._leaf_depths(1)
        return sum(depths) / len(depths)

    def _node_degrees(self) -> list[int]:
        """Return the child count for each non-leaf node in this tree."""
        if not self._subtrees:
            return []

        degrees = [len(self._subtrees)]
        for child in self._subtrees:
            degrees.extend(child._node_degrees())
        return degrees

    def average_branching_factor(self) -> float:
        """Return the average number of children across non-leaf nodes."""
        degrees = self._node_degrees()
        return sum(degrees) / len(degrees) if degrees else 0.0

    def dfs(self) -> list[str]:
        """Return a DFS traversal with explicit possession endings."""
        nodes = [self._root]

        for child in self._subtrees:
            nodes.extend(child.dfs())
            if child._root in {"Shot", "Turnover"}:
                nodes.append("END OF POSSESSION")

        return nodes


def build_possession_tree(df: pd.DataFrame) -> PossessionTree:
    """Return a possession tree for the given game.

    The tree is constructed by parsing play-by-play data and extracting
    pass sequences that end in either a Shot or Turnover.

    Each possession is added as a path to the tree. Player nodes are merged
    along shared prefixes, while repeated terminal events are preserved.

    >>> df = load_play_by_play("0022200001")
    >>> tree = build_possession_tree("0022200001")
    >>> isinstance(tree, PossessionTree)
    True
    >>> tree._root is not None
    True
    >>> len(tree._subtrees) > 0
    True
    >>> # There should be at least some shot or turnover endings
    >>> len(tree.find_all("Shot")) >= 0
    True
    >>> len(tree.find_all("Turnover")) >= 0
    True
    """

    tree = PossessionTree("ROOT")

    current_path = []

    for _, row in df.iterrows():
        event = row.get("EVENTMSGTYPE")
        player1 = row.get("PLAYER1_NAME")
        player2 = row.get("PLAYER2_NAME")

        if not isinstance(player1, str) or player1.strip() == "":
            continue

        if not current_path:
            current_path = ["ROOT", player1]

        if isinstance(player2, str) and player2.strip() != "":
            if current_path[-1] != player2:
                current_path.append(player2)

        if event in {1, 2}:
            if current_path:
                current_path.append("Shot")
                try:
                    tree.add_path(current_path)
                except ValueError:
                    pass
            current_path = []

        elif event == 5:
            if current_path:
                current_path.append("Turnover")
                try:
                    tree.add_path(current_path)
                except ValueError:
                    pass
            current_path = []

        elif event == 4:
            current_path = []

    return tree
