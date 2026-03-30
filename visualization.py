"""CSC111 Winter 2026 Project 2: Mapping the Flow

Created by: Aarit Dua, Vedant Kansara, Lucas Hui

Title: visualization
Description: This file contains functions and a Dash app for visualizing NBA
passing networks and related possession statistics.

Copyright and Usage Information
===============================

This file is provided for educational and personal use only. You may view, download, and modify the code for your own
non-commercial purposes, provided that proper credit is given to the original author.
You may not redistribute, publish, or use this project or any modified version of it for commercial purposes without
explicit written permission from the author.
This project may include third-party libraries, data, or tools that are subject to their own licenses and terms of use.
Users are responsible for reviewing and complying with those licenses.
"""
import time
import traceback
import dash
from dash import dcc, html, Input, Output
from nba_api.stats.static import teams, players
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
from graph import WeightedDirectedGraph, build_passing_graph
from tree import PossessionTree, build_possession_tree
from algorithms import weighted_centrality, average_path_length, aggregate_possession_stats, get_hub_players, \
    cluster_filtering, find_clusters
from data_loader import load_passing_data, load_game_ids, load_play_by_play


def get_player_name(player_id: str) -> str:
    """Return the full name of the player with the given player ID.

        If no matching player is found, return the given player ID as a string.
    """
    player = players.find_player_by_id(int(player_id))
    return player['full_name'] if player else str(player_id)


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
    return nx.spring_layout(nx_graph, k=10, seed=42)


def build_edge_traces(graph: WeightedDirectedGraph, positions: dict, widths: dict) -> list:
    """Return a list of Plotly traces representing the directed edges in graph.

       Each edge is drawn as a line between the positions of its two endpoint nodes.
       The displayed line width is based on the corresponding edge weight stored in
       widths.
    """
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


def build_node_traces(graph: WeightedDirectedGraph, positions: dict, scores: dict, player_cluster, colors) -> list:
    """Return a list of Plotly traces representing the nodes in graph.

    Each node is displayed with its player name, centrality-based size, and
    cluster-based color.
    """
    graph_nx = graph.to_networkx()
    traces = []
    for node in graph_nx.nodes():
        x, y = positions[node]
        c = scores.get(node, 0)
        color = colors[player_cluster.get(node, 0) % len(colors)]
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
    """Return a Plotly figure visualizing the passing network for graph.

    The figure includes:
        - directed edges with toggleable weighted and raw pass-count views
        - player nodes sized by centrality score
        - cluster-based node coloring
        - annotations for average path length, average pass depth,
          average branching factor, and hub players
    """
    positions = get_node_positions(graph)
    scores = weighted_centrality(graph)
    weighted_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['weight'] for _, row in df.iterrows()}
    raw_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['PASS'] for _, row in df.iterrows()}
    edge_traces_weighted = build_edge_traces(graph, positions, weighted_widths)
    edge_traces_raw = build_edge_traces(graph, positions, raw_widths, )
    filtered_graph = cluster_filtering(graph, threshold=200)
    clusters = find_clusters(filtered_graph)
    player_cluster = {}
    for i, cluster in enumerate(clusters):
        for player in cluster:
            player_cluster[player] = i
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#a65628', '#f781bf', '#999999', '#ffff33',
              '#a6cee3']
    node_traces = build_node_traces(graph, positions, scores, player_cluster, colors)
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
            type='rect',
            xref='paper',
            yref='paper',
            x0=0, y0=0,
            x1=1, y1=1,
            line=dict(color='black', width=2)
        )],
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(label="Quality-Adjusted", method="update",
                     args=[{"visible": [True] * len(edge_traces_weighted) + [False] * len(edge_traces_raw) + [
                         True] * len(node_traces)}]),
                dict(label="Raw Pass Count", method="update",
                     args=[{"visible": [False] * len(edge_traces_weighted) + [True] * len(edge_traces_raw) + [
                         True] * len(node_traces)}])
            ]
        )],

        annotations=[
            dict(
                x=1.02,  # just outside the right edge of the graph
                y=0.9,
                xref="paper",
                yref="paper",
                text=f"Avg Path Length: {avg_path_length:.2f}",
                showarrow=False,
                align="left",
                xanchor="left"
            ),
            dict(
                x=1.02,
                y=0.8,
                xref="paper",
                yref="paper",
                text=f"Avg Pass Depth: {avg_pass_depth:.2f}",
                showarrow=False,
                align="left",
                xanchor="left"
            ),
            dict(
                x=1.02,
                y=0.7,
                xref="paper",
                yref="paper",
                text=f"Avg Branching Factor: {avg_branching:.2f}",
                showarrow=False,
                align="left",
                xanchor="left"
            ),
            dict(
                x=1.02,
                y=0.6,
                xref="paper",
                yref="paper",
                text=f"Hub Players: {hub_names}",
                showarrow=False,
                align="left",
                xanchor="left"
            )
        ]
    )

    return figure


app = dash.Dash(__name__)

all_teams = teams.get_teams()
team_options = [{'label': t['full_name'], 'value': t['id']} for t in all_teams]
season_options = [
    {'label': '2022-23', 'value': '2022-23'},
    {'label': '2023-24', 'value': '2023-24'},
    {'label': '2024-25', 'value': '2024-25'}
]

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(id='team-dropdown', options=team_options, value=1610612747,
                     searchable=False, style={'width': '350px'}),
        dcc.Dropdown(id='season-dropdown', options=season_options, value='2023-24',
                     style={'width': '150px', 'marginLeft': '10px'}),
    ], style={'display': 'flex', 'marginTop': '10px', 'marginLeft': '10px', 'marginBottom': '10px'}),
    dcc.Graph(id='passing-graph', style={'height': '85vh'})
])


@app.callback(
    Output('passing-graph', 'figure'),
    Input('team-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_graph(team_id, season) -> go.Figure:
    """Return an updated passing-network figure for the selected team and season.

        This callback loads passing data, builds the passing graph, constructs a small
        collection of possession trees from recent games, and returns the completed
        visualization figure.

        If team_id or season is missing, return an empty figure.

        Preconditions:
        - team_id is a valid NBA team ID or None
        - season is a valid NBA season string in the format 'YYYY-YY' or None
        """
    if team_id is None or season is None:
        return go.Figure()
    time.sleep(0.5)
    try:
        df = load_passing_data(team_id, season)
        graph = build_passing_graph(df)
        game_ids = load_game_ids(team_id, season)[:5]  # first 5 games only
        trees = []
        for game_id in game_ids:
            play_df = load_play_by_play(str(game_id).zfill(10))
            trees.append(build_possession_tree(play_df))
        return build_figure(graph, trees, df)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        raise


def run_visualization() -> None:
    """Launch the interactive passing network visualization."""
    app.run(debug=True)


if __name__ == '__main__':
    import doctest

    import python_ta
    
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['static_type_checker'],
        'extra-imports': ['csv', 'networkx', 'random', 'time', 'pandas', 'os', 'traceback', 'dash', 'nba_api.stats.static', 'plotly.graph_objects'],
        'allowed-io': ['load_review_graph', 'load_passing_data', 'load_play_by_play', 'load_game_ids'],
        'max-nested-blocks': 4
    })

    run_visualization()