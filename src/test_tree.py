from data_loader import load_play_by_play
import pandas as pd
from tree import Tree, build_possession_tree, build_random_possession_sequences
tree_data = build_random_possession_sequences(load_play_by_play("0022200001"))
tree = build_possession_tree(tree_data)
print(tree.average_branching_factor())
print(tree.average_depth())
tree.print_sequences_from('Harden')

'''def build_possession_tree2(df: pd.DataFrame) -> Tree:
    """Return a possession tree for the given game.

    The tree is constructed by parsing play-by-play data and extracting
    pass sequences that end in either a Shot or Turnover.

    Each possession is added as a path to the tree. Player nodes are merged
    along shared prefixes, while repeated terminal events are preserved.

    >>> df = load_play_by_play("0022300061")
    >>> tree = build_possession_tree(df)
    >>> isinstance(tree, PossessionTree)
    True
    >>> tree._root is not None
    True
    >>> len(tree._subtrees) > 0
    True
    >>> len(tree.find_all("Shot")) >= 0
    True
    >>> len(tree.find_all("Turnover")) >= 0
    True
    """
    tree = Tree("ROOT")
    current_path = []

    for _, row in df.iterrows():
        event = row.get("actionType")
        player = row.get("playerName")

        if not isinstance(player, str) or player.strip() == "":
            continue

        if not current_path:
            current_path = ["ROOT", player]
        elif current_path[-1] != player:
            current_path.append(player)

        if event in {"2pt", "3pt", "freethrow"}:
            current_path.append("Shot")
            try:
                tree.add_path(current_path)
            except ValueError:
                pass
            current_path = []

        elif event == "turnover":
            current_path.append("Turnover")
            try:
                tree.add_path(current_path)
            except ValueError:
                pass
            current_path = []

        elif event in {"rebound", "jumpball"}:
            current_path = []

    return tree

tree = build_possession_tree2(load_play_by_play("0022200001"))
tree.print_sequences_from('ROOT')
print(tree.average_branching_factor())'''