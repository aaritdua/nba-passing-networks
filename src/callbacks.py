# """Dash callbacks for the NBA passing network visualizer."""
# import time
# import traceback
# import plotly.graph_objects as go
# from dash import Input, Output
# from src.layout import app
# from src.figures import build_figure
# from src.graph import build_passing_graph
# from src.tree import build_possession_tree
# from src.data_loader import load_passing_data, load_game_ids, load_play_by_play


# @app.callback(
#     Output('passing-graph', 'figure'),
#     Input('team-dropdown', 'value'),
#     Input('season-dropdown', 'value')
# )
# def update_graph(team_id, season) -> go.Figure:
#     """Return an updated passing-network figure for the selected team and season."""
#     if team_id is None or season is None:
#         return go.Figure()
#     try:
#         df = load_passing_data(team_id, season)
#         graph = build_passing_graph(df)
#         game_ids = load_game_ids(team_id, season)[:5]
#         trees = []
#         for game_id in game_ids:
#             play_df = load_play_by_play(str(game_id).zfill(10))
#             trees.append(build_possession_tree(play_df))
#         return build_figure(graph, trees, df)
#     except Exception as e:
#         print(f"Error: {e}")
#         traceback.print_exc()
#         return go.Figure().update_layout(
#             annotations=[dict(
#                 text=f"Failed to load data. Please try again.",
#                 x=0.5, y=0.5,
#                 xref="paper", yref="paper",
#                 showarrow=False,
#                 font=dict(size=16, color="red")
#             )],
#             xaxis=dict(visible=False),
#             yaxis=dict(visible=False)
#         )

"""Dash callbacks for the NBA passing network visualizer."""
import traceback
import plotly.graph_objects as go
from dash import Input, Output, html
from src.layout import app
from src.figures import build_figure, get_player_name
from src.graph import build_passing_graph
from src.tree import build_possession_tree
from src.algorithms import weighted_centrality, average_path_length, aggregate_possession_stats, get_hub_players
from src.data_loader import load_passing_data, load_game_ids, load_play_by_play

ORANGE = '#f97316'
TEXT_MUTED = '#666666'
TEXT_PRIMARY = '#ffffff'


@app.callback(
    Output('passing-graph', 'figure'),
    Output('stat-path-length', 'children'),
    Output('stat-pass-depth', 'children'),
    Output('stat-branching', 'children'),
    Output('stat-hub-players', 'children'),
    Input('team-dropdown', 'value'),
    Input('season-dropdown', 'value')
)
def update_graph(team_id, season):
    empty_stats = (
        go.Figure(),
        stat_block('Avg Path Length', '—'),
        stat_block('Avg Pass Depth', '—'),
        stat_block('Branching Factor', '—'),
        '—'
    )

    if team_id is None or season is None:
        return empty_stats

    try:
        df = load_passing_data(team_id, season)
        graph = build_passing_graph(df)
        game_ids = load_game_ids(team_id, season)[:5]
        trees = []
        for game_id in game_ids:
            play_df = load_play_by_play(str(game_id).zfill(10))
            trees.append(build_possession_tree(play_df))

        from src.algorithms import weighted_centrality
        scores = weighted_centrality(graph)
        avg_pl = average_path_length(graph)
        avg_depth, avg_branching = aggregate_possession_stats(trees)
        hub_players = get_hub_players(scores, 3)
        hub_names = [html.Div(f'• {get_player_name(p)}', style={'marginBottom': '4px'}) for p in hub_players]

        return (
            build_figure(graph, trees, df),
            stat_block('Avg Path Length', f'{avg_pl:.2f}'),
            stat_block('Avg Pass Depth', str(avg_depth)),
            stat_block('Branching Factor', f'{avg_branching:.2f}'),
            hub_names
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return empty_stats


def stat_block(label, value):
    return [
        html.Div(label, style={'fontSize': '11px', 'color': TEXT_MUTED, 'marginBottom': '2px'}),
        html.Div(value, style={'fontSize': '22px', 'fontWeight': '500', 'color': ORANGE}),
    ]