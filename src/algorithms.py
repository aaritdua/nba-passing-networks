from graph import WeightedDirectedGraph

def weighted_centrality(graph: WeightedDirectedGraph) -> dict:
    """
    Return a dictionary mapping each player to their normalized centrality score.

    The centrality score is computed as the sum of all incoming and outgoing edge
    weights for each player, normalized so that the highest scoring player has a
    score of 1.0. A higher score indicates a player who is more central to their
    team's offensive flow.
    """
    
    scores = {}
    for player in graph._vertices:
        vertex = graph._vertices[player]
        out_score = sum(vertex.neighbours.values())
        in_score = 0
        for other_vertex in graph._vertices.values():
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
    for player in graph._vertices:
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
    for player in graph._vertices:
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
    for player in graph._vertices:
        distances = graph.bfs(player)
        for distance in distances.values():
            if distance > 0:
                total += distance
                count += 1
    return total / count if count > 0 else 0.0

