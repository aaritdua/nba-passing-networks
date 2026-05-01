"""Graph and tree algorithms for analyzing NBA passing networks.

Includes player centrality scoring, hub detection, cluster filtering,
average path length, and aggregate possession statistics.
"""
from nba_passing_networks.core.graph import WeightedDirectedGraph
from nba_passing_networks.core.tree import PossessionTree


def weighted_centrality(graph: WeightedDirectedGraph) -> dict:
    """
    Return a dictionary mapping each player to their normalized centrality score.

    The centrality score is computed as the sum of all incoming and outgoing edge
    weights for each player, normalized so that the highest scoring player has a
    score of 1.0. A higher score indicates a player who is more central to their
    team's offensive flow.
    """

    scores = {}
    graph_vertices = graph.get_vertices()
    for player in graph_vertices:
        vertex = graph_vertices[player]
        out_score = sum(vertex.neighbours.values())
        in_score = 0
        for other_vertex in graph_vertices.values():
            if vertex in other_vertex.neighbours:
                in_score += other_vertex.neighbours[vertex]
        scores[player] = out_score + in_score
    max_score = max(scores.values())
    for player in scores:
        scores[player] = scores[player] / max_score
    return scores


def get_hub_players(scores: dict, n: int) -> list:
    """
    Return the top n players by centrality score as a list of player IDs.

    Players are sorted in descending order of centrality score. The scores
    argument should be a dictionary as returned by weighted_centrality.
    """

    return sorted(scores, key=lambda x: scores[x], reverse=True)[:n]


def cluster_filtering(graph: WeightedDirectedGraph, threshold: float) -> WeightedDirectedGraph:
    """
    Return a new WeightedDirectedGraph containing only the edges from graph
    whose weight is strictly above the given threshold.

    All vertices from the original graph are preserved in the filtered graph,
    even if they have no edges above the threshold. This ensures isolated players
    appear as their own cluster in find_clusters.
    """

    edges = graph.get_edges()
    g = WeightedDirectedGraph()
    graph_vertices = graph.get_vertices()
    for player in graph_vertices:
        g.add_vertex(player)
    for edge in edges:
        if edge[2] > threshold:
            g.add_directed_edge(edge[0], edge[1], edge[2])
    return g


def find_clusters(graph: WeightedDirectedGraph) -> list[set]:
    """
    Return a list of clusters, where each cluster is a set of player IDs
    that are reachable from each other in the graph.

    Uses BFS to discover connected components. Each call to BFS from an
    unvisited player discovers one cluster. A player with no edges will
    appear as a singleton cluster.
    """

    clusters = []
    visited = set()
    graph_vertices = graph.get_vertices()
    for player in graph_vertices:
        if player not in visited:
            cluster = set(graph.bfs(player).keys())
            clusters.append(cluster)
            visited.update(cluster)
    return clusters


def average_path_length(graph: WeightedDirectedGraph) -> float:
    """
    Return the average shortest path length between all pairs of reachable
    vertices in the graph, measured in number of directed edges.

    A lower value indicates a more well-connected offense where the ball
    can reach any player quickly.
    """
    total = 0
    count = 0
    graph_vertices = graph.get_vertices()
    for player in graph_vertices:
        distances = graph.bfs(player)
        for distance in distances.values():
            if distance > 0:
                total += distance
                count += 1
    return total / count if count > 0 else 0.0


def aggregate_possession_stats(trees: list[PossessionTree]) -> tuple[int, float]:
    """Return the average pass depth and average branching factor across all pass-sequence trees"""
    if not trees:
        return 0, 0.0
    else:
        return _average_pass_depth_trees(trees), average_branching_factor_trees(trees)


def average_branching_factor_trees(trees: list[PossessionTree]) -> float:
    """Return the mean of average branching factor across all pass-sequence trees .

        This is computed by taking each tree's average branching factor and then
        returning the mean of those values.
    """
    avg_branching_factor = 0
    for tree in trees:
        avg_branching_factor += tree.average_branching_factor()
    return avg_branching_factor / len(trees)


def _average_pass_depth_trees(trees: list[PossessionTree]) -> int:
    """Return the mean of average pass depth acroos all pass-sequence trees .

        This is computed by taking each tree's average pass depth and then returning the mean of those values
    """
    avg_pass_depth = 0
    for tree in trees:
        avg_pass_depth += tree.average_depth()
    return int(avg_pass_depth / len(trees))
