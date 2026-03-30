"""CSC111 Winter 2026 Project 2: Mapping the Flow

Created by: Aarit Dua, Vedant Kansara, Lucas Hui

Title: tree
Description: This file contains the implementation of a possession tree used to
represent and analyze pass sequences from NBA play-by-play data, along with
functions for building possession trees from game data.

Copyright and Usage Information
===============================

This file is provided for educational and personal use only. You may view, download, and modify the code for your own
non-commercial purposes, provided that proper credit is given to the original author.
You may not redistribute, publish, or use this project or any modified version of it for commercial purposes without
explicit written permission from the author.
This project may include third-party libraries, data, or tools that are subject to their own licenses and terms of use.
Users are responsible for reviewing and complying with those licenses.
"""
from __future__ import annotations
import random
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


def build_random_possession_sequences(df: pd.DataFrame) -> list[list[str]]:
    """Extract possessions and generate approximate pass sequences from play-by-play data.

    Since PlayByPlayV3 does not record pass receivers, pass sequences within each
    possession are approximated by shuffling the players involved. This allows
    tree construction and computation as a proof of concept.
    """
    df = df.sort_values(by=["period", "clock"])
    possessions = []
    current_team = None
    current_players = []

    for _, row in df.iterrows():
        team = row.get("teamId")
        player = row.get("playerName")
        action = row.get("actionType")

        if not isinstance(player, str) or player.strip() == "":
            continue

        if team != current_team:
            if current_players:
                possessions.append(current_players)
            current_players = [player]
            current_team = team
        else:
            current_players.append(player)

        if action in ["turnover", "2pt", "3pt"]:
            if current_players:
                possessions.append(current_players)
            current_players = []

    sequences = []
    for players in possessions:
        unique_players = list(set(players))
        if not unique_players:
            continue
        random.shuffle(unique_players)
        outcome = random.choice(["Shot", "Turnover"])
        sequences.append(unique_players + [outcome])

    return sequences


def build_possession_tree(df: pd.DataFrame) -> PossessionTree:
    """Return a possession tree built from play-by-play data.

    >>> df1 = load_play_by_play("0022300061")
    >>> tree1 = build_possession_tree(df1)
    >>> isinstance(tree1, PossessionTree)
    True
    >>> tree1._root is not None
    True
    >>> len(tree1._subtrees) > 0
    True
    """
    sequences = build_random_possession_sequences(df)
    tree = PossessionTree("ROOT")

    for seq in sequences:
        path = ["ROOT"] + seq
        try:
            tree.add_path(path)
        except ValueError:
            pass

    return tree


if __name__ == '__main__':
    import doctest

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['csv', 'networkx', 'random', 'time', 'pandas', 'os'],
        'allowed-io': ['load_review_graph', 'load_passing_data', 'load_play_by_play', 'load_game_ids'],
        'max-nested-blocks': 4
    })
