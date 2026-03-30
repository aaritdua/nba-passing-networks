import dash
from dash import dcc, html, Input, Output
from nba_api.stats.static import teams, players
import networkx as nx
import plotly.graph_objects as go
from graph import WeightedDirectedGraph, build_passing_graph
from tree import PossessionTree as PossessionTree
from algorithms import weighted_centrality, average_path_length, aggregate_possession_stats
import pandas as pd
from data_loader import load_passing_data
import time

def get_player_name(player_id) -> str:
    """Return the full name for a given player ID, or the ID as string if not found."""
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
    return nx.spring_layout(nx_graph)

def build_edge_traces(graph: WeightedDirectedGraph, positions: dict, widths: dict) -> list:
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

def build_node_traces(graph: WeightedDirectedGraph, positions: dict, scores: dict) -> list:
    graph_nx = graph.to_networkx()
    traces = []
    for node in graph_nx.nodes():
        x, y = positions[node]
        c = scores.get(node, 0)
        trace = go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            text=get_player_name(node),
            textposition='top center',
            hoverinfo='text',
            hovertext=f'Player: {get_player_name(node)}<br>Centrality: {c:.3f}',
            marker=dict(size=20 + 40 * c)
        )
        traces.append(trace)
    return traces

def build_figure(graph: WeightedDirectedGraph, trees: list[PossessionTree], df: pd.DataFrame) -> go.Figure:
    positions = get_node_positions(graph)
    scores = weighted_centrality(graph)
    weighted_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['weight'] for _, row in df.iterrows()}
    raw_widths = {(row['PLAYER_ID'], row['PASS_TEAMMATE_PLAYER_ID']): row['PASS'] for _, row in df.iterrows()}
    edge_traces_weighted = build_edge_traces(graph, positions, weighted_widths)
    edge_traces_raw = build_edge_traces(graph, positions, raw_widths,)
    node_traces = build_node_traces(graph, positions, scores)
    avg_path_length = average_path_length(graph)
    avg_pass_depth, avg_branching = aggregate_possession_stats(trees)
    for trace in edge_traces_raw:
        trace['visible'] = False

    figure = go.Figure(data=edge_traces_weighted + edge_traces_raw + node_traces)
    
    figure.update_layout(
        showlegend=False,
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

app = dash.Dash(__name__)

all_teams = teams.get_teams()
team_options = [{'label': t['full_name'], 'value': t['id']} for t in all_teams]
season_options = [
    {'label': '2022-23', 'value': '2022-23'},
    {'label': '2023-24', 'value': '2023-24'},
    {'label': '2024-25', 'value': '2024-25'}
]

app.layout = html.Div([
    dcc.Dropdown(id='team-dropdown', options=team_options, value=1610612747),
    dcc.Dropdown(id='season-dropdown', options=season_options, value='2023-24'),
    dcc.Graph(id='passing-graph')
])

@app.callback(
    Output('passing-graph', 'figure'),
    Input('team-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_graph(team_id, season):
    if team_id is None or season is None:
        return go.Figure()
    time.sleep(0.5)
    try:
        df = load_passing_data(team_id, season)
        graph = build_passing_graph(df)
        trees = []
        return build_figure(graph, trees, df)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise

def run_visualization() -> None:
    """Launch the interactive passing network visualization."""
    app.run(debug=True)
    
    
    
if __name__ == '__main__':
    run_visualization()