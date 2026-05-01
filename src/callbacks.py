"""Dash callbacks for the NBA passing network visualizer."""
import time
import traceback
import plotly.graph_objects as go
from dash import Input, Output
from src.layout import app
from src.figures import build_figure
from src.graph import build_passing_graph
from src.tree import build_possession_tree
from src.data_loader import load_passing_data, load_game_ids, load_play_by_play


@app.callback(
    Output('passing-graph', 'figure'),
    Input('team-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_graph(team_id, season) -> go.Figure:
    """Return an updated passing-network figure for the selected team and season."""
    if team_id is None or season is None:
        return go.Figure()
    time.sleep(0.5)
    try:
        df = load_passing_data(team_id, season)
        graph = build_passing_graph(df)
        game_ids = load_game_ids(team_id, season)[:5]
        trees = []
        for game_id in game_ids:
            play_df = load_play_by_play(str(game_id).zfill(10))
            trees.append(build_possession_tree(play_df))
        return build_figure(graph, trees, df)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        raise