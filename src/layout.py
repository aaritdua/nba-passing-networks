"""Dash app instance and layout for the NBA passing network visualizer."""
import dash
from dash import dcc, html
from nba_api.stats.static import teams

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