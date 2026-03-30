from __future__ import annotations
import pandas as pd

'''def build_possession_tree(play_by_play_data: pd.DataFrame) -> Tree:
    """Build a possession tree from play-by-play data."""
    root = Tree("Possession")
    current = root

    for _, row in play_by_play_data.iterrows():
        event_type = row["EVENT_TYPE"]
        player_name = row["PLAYER_NAME"]

        if event_type == "PASS":
            current.add_player(player_name)
        elif event_type == "SHOT":
            current.add_shot()
        elif event_type == "TURNOVER":
            current.add_turnover()

    return root'''


class Tree:
    """A recursive tree representing one possession tree in a game.

    Each internal node stores a player name. Leaf nodes may also store the
    special values ``"Shot"`` or ``"Turnover"`` to represent how a sequence
    ended.

    Repeated ending events are preserved as separate leaves, so a player may
    have subtrees like ``["Shot", "Shot", "Turnover", "Kyrie"]``.
    """

    _root: str
    _subtrees: list[Tree]

    def __init__(self, root: str, subtrees: list[Tree] | None = None) -> None:
        """Initialize a new tree with the given root value and subtrees."""
        self._root = root
        self._subtrees = subtrees.copy() if subtrees is not None else []

    def add_player(self, player: str) -> None:
        """Add a player node as a child of this tree."""
        self._subtrees.append(Tree(player))

    def add_shot(self) -> None:
        """Add a shot leaf as a child of this tree."""
        self._subtrees.append(Tree("Shot"))

    def add_turnover(self) -> None:
        """Add a turnover leaf as a child of this tree."""
        self._subtrees.append(Tree("Turnover"))

    def find_all(self, target: str) -> list[Tree]:
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
                current._subtrees.append(Tree(item))
                return

            found = current._find_child_player(item)
            if found is None:
                found = Tree(item)
                current._subtrees.append(found)
            current = found

    def _find_child_player(self, player: str) -> Tree | None:
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


def build_possession_tree(df: pd.DataFrame) -> Tree:
    """Return a possession tree built from PlayByPlayV3 data."""

    tree = Tree("ROOT")

    # ✅ FIXED column names
    df = df.sort_values(by=["period", "clock"])

    current_possession = None
    current_path = []

    for _, row in df.iterrows():
        event_type = row.get("eventType")
        player = row.get("playerName")
        pass_to = row.get("passTo")
        possession = row.get("possession")

        # Skip invalid rows
        if not isinstance(player, str) or player.strip() == "":
            continue

        # --- NEW POSSESSION ---
        if possession != current_possession:
            current_possession = possession
            current_path = ["ROOT", player]

        # --- PASS ---
        if event_type == "pass" and isinstance(pass_to, str) and pass_to.strip() != "":
            if current_path[-1] != pass_to:
                current_path.append(pass_to)

        # --- SHOT ---
        elif event_type in {"shot", "miss"}:
            current_path.append("Shot")
            try:
                tree.add_path(current_path)
            except ValueError:
                pass
            current_path = []

        # --- TURNOVER ---
        elif event_type == "turnover":
            current_path.append("Turnover")
            try:
                tree.add_path(current_path)
            except ValueError:
                pass
            current_path = []

    return tree

'''tree = build_possession_tree(load_play_by_play("0022200001"))
print(tree._get_all_paths())'''
