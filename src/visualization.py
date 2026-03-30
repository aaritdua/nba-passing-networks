import networkx as nx
import plotly.graph_objects as go
from graph import WeightedDirectedGraph
from tree import PossessionTree
from algorithms import weighted_centrality, average_path_length, aggregate_possession_stats
import pandas as pd

def get_node_positions(graph: WeightedDirectedGraph) -> dict:
    """
    Return a dictionary mapping each player ID to an (x, y) position. 
    
    >>> g = WeightedDirectedGraph()
    >>> g.add_vertex(1)
    >>> g.add_vertex(2)
    >>> g.add_directed_edge(1, 2, 5.0)
    >>> positions = get_node_positions(g)
    >>> set(positions.keys()) == {1, 2}
    True
    >>> len(positions[1]) == 2
    True
    """
    
    nx_graph = graph.to_networkx()
    return nx.spring_layout(nx_graph)

def build_figure(graph: WeightedDirectedGraph, trees: list[PossessionTree], df: pd.DataFrame) -> go.Figure:
    positions = get_node_positions(graph)
    scores = weighted_centrality(graph)
    weighted_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['weight'] for _, row in df.iterrows()}
    raw_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['PASS'] for _, row in df.iterrows()}
    edge_traces_weighted = build_edge_traces(graph, positions, weighted_widths)
    edge_traces_raw = build_edge_traces(graph, positions, raw_widths)
    node_traces = build_node_traces(graph, positions, scores)
    avg_path_length = average_path_length(graph)
    avg_pass_depth, avg_branching = aggregate_possession_stats(trees)
    for trace in edge_traces_raw:
        trace.visible = False

    figure = go.Figure(data=edge_traces_weighted + edge_traces_raw + node_traces)
    
    figure.update_layout(
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(label="Quality-Adjusted", method="update",
                    args=[{"visible": [True] * len(edge_traces_weighted) + [False] * len(edge_traces_raw) + [True] * len(node_traces)}]),
                dict(label="Raw Pass Count", method="update",
                    args=[{"visible": [False] * len(edge_traces_weighted) + [True] * len(edge_traces_raw) + [True] * len(node_traces)}])
            ]
        )]
        
        annotations=[
            dict(
                x=1.02,  # just outside the right edge of the graph
                y=0.9,
                xref="paper",
                yref="paper",
                text=f"Avg Path Length: {avg_path_length:.2f}",
                showarrow=False,
                align="left"
            ),
            dict(
                x=1.02,
                y=0.8,
                xref="paper",
                yref="paper",
                text=f"Avg Pass Depth: {avg_pass_depth:.2f}",
                showarrow=False,
                align="left"
            ),
            dict(
                x=1.02,
                y=0.7,
                xref="paper",
                yref="paper",
                text=f"Avg Branching Factor: {avg_branching:.2f}",
                showarrow=False,
                align="left"
            )
        ]
    )
    
    return figure