"""Dash app instance and layout for the NBA passing network visualizer."""
import dash
from dash import dcc, html
from nba_api.stats.static import teams

app = dash.Dash(__name__)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>{%metas%}<title>Passing Network</title>{%favicon%}{%css%}</head>
    <body style="margin:0;padding:0;background:#0f0f0f;overflow:hidden;">{%app_entry%}{%config%}{%scripts%}{%renderer%}</body>
</html>
'''

all_teams = teams.get_teams()
team_options = [{'label': t['full_name'], 'value': t['id']} for t in all_teams]
season_options = [
    {'label': '2022-23', 'value': '2022-23'},
    {'label': '2023-24', 'value': '2023-24'},
    {'label': '2024-25', 'value': '2024-25'}
]

ORANGE = '#f97316'
BG_DARK = '#0f0f0f'
BG_SIDEBAR = '#161616'
BORDER = '#2a2a2a'
TEXT_PRIMARY = '#ffffff'
TEXT_MUTED = '#666666'

app.layout = html.Div(
    style={'display': 'flex', 'height': '100vh', 'background': BG_DARK, 'fontFamily': 'sans-serif'},
    children=[
        html.Div(
            style={
                'width': '220px', 'minWidth': '220px', 'background': BG_SIDEBAR,
                'borderRight': f'0.5px solid {BORDER}', 'padding': '24px 20px',
                'display': 'flex', 'flexDirection': 'column', 'gap': '20px'
            },
            children=[
                html.Div([
                    html.Div('Passing Network', style={'fontSize': '18px', 'fontWeight': '500', 'color': TEXT_PRIMARY}),
                    html.Div('NBA Offense Analysis', style={'fontSize': '11px', 'color': TEXT_MUTED, 'marginTop': '4px'}),
                ]),

                html.Div([
                    html.Div('Team', style={'fontSize': '11px', 'color': TEXT_MUTED, 'textTransform': 'uppercase', 'letterSpacing': '0.06em', 'marginBottom': '6px'}),
                    dcc.Dropdown(
                        id='team-dropdown',
                        options=team_options,
                        value=1610612747,
                        searchable=False,
                        style={'width': '100%'}
                    ),
                ]),

                html.Div([
                    html.Div('Season', style={'fontSize': '11px', 'color': TEXT_MUTED, 'textTransform': 'uppercase', 'letterSpacing': '0.06em', 'marginBottom': '6px'}),
                    dcc.Dropdown(
                        id='season-dropdown',
                        options=season_options,
                        value='2023-24',
                        searchable=False,
                        style={'width': '100%'}
                    ),
                ]),

                html.Div(style={'borderTop': f'0.5px solid {BORDER}'}),

                html.Div([
                    html.Div('Network Stats', style={'fontSize': '11px', 'color': TEXT_MUTED, 'textTransform': 'uppercase', 'letterSpacing': '0.06em', 'marginBottom': '14px'}),
                    html.Div(id='stat-path-length', children=[
                        html.Div('Avg Path Length', style={'fontSize': '11px', 'color': TEXT_MUTED, 'marginBottom': '2px'}),
                        html.Div('—', style={'fontSize': '22px', 'fontWeight': '500', 'color': ORANGE}),
                    ], style={'marginBottom': '14px'}),
                    html.Div(id='stat-pass-depth', children=[
                        html.Div('Avg Pass Depth', style={'fontSize': '11px', 'color': TEXT_MUTED, 'marginBottom': '2px'}),
                        html.Div('—', style={'fontSize': '22px', 'fontWeight': '500', 'color': ORANGE}),
                    ], style={'marginBottom': '14px'}),
                    html.Div(id='stat-branching', children=[
                        html.Div('Branching Factor', style={'fontSize': '11px', 'color': TEXT_MUTED, 'marginBottom': '2px'}),
                        html.Div('—', style={'fontSize': '22px', 'fontWeight': '500', 'color': ORANGE}),
                    ], style={'marginBottom': '14px'}),
                    html.Div([
                        html.Div('Hub Players', style={'fontSize': '11px', 'color': TEXT_MUTED, 'marginBottom': '8px'}),
                        html.Div(id='stat-hub-players', children='—', style={'fontSize': '13px', 'color': TEXT_PRIMARY}),
                    ]),
                ]),
            ]
        ),

        html.Div(
            style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'background': BG_DARK, 'position': 'relative'},
            children=[
                dcc.Loading(
                    id='loading',
                    type='circle',
                    color=ORANGE,
                    overlay_style={"visibility": "visible", "filter": "blur(2px)"},
                    custom_spinner=html.Div([
                        html.Div(style={
                            'width': '40px', 'height': '40px', 'border': f'3px solid #2a2a2a',
                            'borderTop': f'3px solid {ORANGE}', 'borderRadius': '50%',
                            'animation': 'spin 0.8s linear infinite', 'margin': '0 auto 16px'
                        }),
                        html.Div('Loading passing data...', style={'color': '#ffffff', 'fontSize': '14px', 'marginBottom': '6px'}),
                        html.Div('First load may take up to 30 seconds', style={'color': '#666666', 'fontSize': '12px'}),
                    ], style={'textAlign': 'center'}),
                    children=dcc.Graph(
                        id='passing-graph',
                        style={'height': '100vh'},
                        config={'displayModeBar': False, 'displaylogo': False}
                    )
                )
            ]
        )
    ]
)