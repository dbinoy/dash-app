from dash import html
import dash_bootstrap_components as dbc

def create_azure_cost_layout():
    return html.Div([
        dbc.Row([
            dbc.Col(html.H1("Azure Cost Analysis"), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.P("This section provides insights into Azure costs."), width=12)
        ]),
        dbc.Row([
            dbc.Col(dbc.Button("View Costs", color="primary"), width={"size": 2, "offset": 5})
        ])
    ])