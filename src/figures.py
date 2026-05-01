"""Plotly figure construction for NBA passing network visualizations."""
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
from nba_api.stats.static import players
from src.graph import WeightedDirectedGraph
from src.tree import PossessionTree
from src.algorithms import (
    weighted_centrality, average_path_length, aggregate_possession_stats,
    get_hub_players, cluster_filtering, find_clusters
)

COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00',
          '#a65628', '#f781bf', '#999999', '#ffff33', '#a6cee3']


def get_player_name(player_id: str) -> str:
    """Return the full name of the player with the given player ID.

    If no matching player is found, return the given player ID as a string.
    """
    player = players.find_player_by_id(int(player_id))
    return player['full_name'] if player else str(player_id)


def get_node_positions(graph: WeightedDirectedGraph) -> dict:
    """Return a dictionary mapping each player ID to an (x, y) position."""
    nx_graph = graph.to_networkx()
    return nx.spring_layout(nx_graph, k=10, seed=42)


def build_edge_traces(graph: WeightedDirectedGraph, positions: dict, widths: dict) -> list:
    """Return a list of Plotly traces representing the directed edges in graph."""
    graph_nx = graph.to_networkx()
    traces = []
    for u, v in graph_nx.edges():
        x0, y0 = positions[u]
        x1, y1 = positions[v]
        weight = widths.get((u, v), 1)
        trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=max(0.5, weight / 50)),
            hoverinfo='none'
        )
        traces.append(trace)
    return traces


def build_node_traces(graph: WeightedDirectedGraph, positions: dict, scores: dict, player_cluster: dict) -> list:
    """Return a list of Plotly traces representing the nodes in graph."""
    graph_nx = graph.to_networkx()
    traces = []
    for node in graph_nx.nodes():
        x, y = positions[node]
        c = scores.get(node, 0)
        color = COLORS[player_cluster.get(node, 0) % len(COLORS)]
        trace = go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            text=get_player_name(node),
            textposition='middle center',
            textfont=dict(size=10, color='black'),
            hoverinfo='text',
            hovertext=f'Player: {get_player_name(node)}<br>Centrality: {c:.3f}',
            marker=dict(size=20 + 40 * c, color=color)
        )
        traces.append(trace)
    return traces


def build_figure(graph: WeightedDirectedGraph, trees: list[PossessionTree], df: pd.DataFrame) -> go.Figure:
    """Return a Plotly figure visualizing the passing network for graph."""
    positions = get_node_positions(graph)
    scores = weighted_centrality(graph)
    weighted_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['weight'] for _, row in df.iterrows()}
    raw_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['PASS'] for _, row in df.iterrows()}
    edge_traces_weighted = build_edge_traces(graph, positions, weighted_widths)
    edge_traces_raw = build_edge_traces(graph, positions, raw_widths)
    filtered_graph = cluster_filtering(graph, threshold=200)
    clusters = find_clusters(filtered_graph)
    player_cluster = {}
    for i, cluster in enumerate(clusters):
        for player in cluster:
            player_cluster[player] = i
    node_traces = build_node_traces(graph, positions, scores, player_cluster)
    avg_path_length = average_path_length(graph)
    avg_pass_depth, avg_branching = aggregate_possession_stats(trees)
    hub_players = get_hub_players(scores, 3)
    hub_names = "<br>• " + "<br>• ".join([get_player_name(p) for p in hub_players])
    for trace in edge_traces_raw:
        trace['visible'] = False

    figure = go.Figure(data=edge_traces_weighted + edge_traces_raw + node_traces)
    figure.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=220, t=20, b=20),
        shapes=[dict(
            type='rect', xref='paper', yref='paper',
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color='black', width=2)
        )],
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(label="Quality-Adjusted", method="update",
                     args=[{"visible": [True] * len(edge_traces_weighted) + [False] * len(edge_traces_raw) + [True] * len(node_traces)}]),
                dict(label="Raw Pass Count", method="update",
                     args=[{"visible": [False] * len(edge_traces_weighted) + [True] * len(edge_traces_raw) + [True] * len(node_traces)}])
            ]
        )],
        annotations=[
            dict(x=1.02, y=0.9, xref="paper", yref="paper", text=f"Avg Path Length: {avg_path_length:.2f}", showarrow=False, align="left", xanchor="left"),
            dict(x=1.02, y=0.8, xref="paper", yref="paper", text=f"Avg Pass Depth: {avg_pass_depth:.2f}", showarrow=False, align="left", xanchor="left"),
            dict(x=1.02, y=0.7, xref="paper", yref="paper", text=f"Avg Branching Factor: {avg_branching:.2f}", showarrow=False, align="left", xanchor="left"),
            dict(x=1.02, y=0.6, xref="paper", yref="paper", text=f"Hub Players: {hub_names}", showarrow=False, align="left", xanchor="left")
        ]
    )
    return figure