from graph import WeightedDirectedGraph

def weighted_centrality(graph: WeightedDirectedGraph) -> dict:
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
    return sorted(scores, key=lambda x: scores[x], reverse=True)[:n]

def cluster_filtering(graph: WeightedDirectedGraph, threshold: float) -> WeightedDirectedGraph:
    edges = graph.get_edges()
    g = WeightedDirectedGraph()
    for player in graph._vertices:
        g.add_vertex(player)
    for edge in edges:
        if edge[2] > threshold:
            g.add_directed_edge(edge[0], edge[1], edge[2])
    return g

def find_clusters(graph: WeightedDirectedGraph) -> list[set]:
    clusters = []
    visited = set()
    for player in graph._vertices:
        if player not in visited:
            cluster = set(graph.bfs(player).keys())
            clusters.append(cluster)
            visited.update(cluster)
    return clusters
