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
