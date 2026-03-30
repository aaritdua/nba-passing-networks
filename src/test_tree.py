from data_loader import load_play_by_play
from tree import build_possession_tree
tree = build_possession_tree(load_play_by_play("0022200001"))
tree.print_sequences_from("ROOT")
print(tree.average_branching_factor())