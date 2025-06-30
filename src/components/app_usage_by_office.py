from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def app_usage_by_office_layout():
    return dbc.Card([
        dbc.CardHeader("App Usage by Office"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Office:"),
                    dcc.Dropdown(
                        id="office-filter-dropdown",
                        options=[],  # Populated by callback
                        placeholder="Select Office(s)",
                        multi=True,
                        style={"marginBottom": "8px"}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("App:"),
                    dcc.Dropdown(
                        id="app-filter-dropdown",
                        options=[],  # Populated by callback
                        placeholder="Select App(s)",
                        multi=True,
                        style={"marginBottom": "8px"}
                    ),
                ], width=6),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col([
                    html.Label("Sort By:"),
                    dcc.Dropdown(
                        id="sortby-dropdown",
                        options=[
                            {"label": "Login Count (Ascending)", "value": "asc"},
                            {"label": "Login Count (Descending)", "value": "desc"}
                        ],
                        placeholder="Sort By",
                        value="desc",
                        clearable=False,
                        style={"marginBottom": "8px"}
                    ),
                ], width=6),
                dbc.Col([
                    html.Label("Show Top:"),
                    dcc.Dropdown(
                        id="showtop-dropdown",
                        options=[{"label": f"Top {n}", "value": n} for n in [5, 10, 15, 20, 25, 30, 50]],
                        placeholder="Show Top",
                        value=10,
                        clearable=False,
                        style={"marginBottom": "8px"}
                    ),
                ], width=6),
            ], className="mb-2"),
            dcc.Graph(id="app-usage-by-office-graph")
        ])
    ])

def get_app_usage_by_office_figure(df, selected_offices, selected_apps, sortby, showtop):

    ascending = sortby == "asc"
    df = df.sort_values("TotalLogins", ascending=ascending)
    # Show top N
    df = df.tail(showtop) if ascending else df.head(showtop)
    # Plot
    fig = px.bar(
        df,
        x="OfficeName",
        y="TotalLogins",
        title="Login Count by Office",
        labels={"TotalLogins": "Login Count", "OfficeName": "Office Name"},
    )
    fig.update_layout(
        xaxis_title="Office Name",
        yaxis_title="Login Count",
        template="plotly_white",
        margin=dict(l=40, r=20, t=60, b=120),
        xaxis_tickangle=-45
    )
    return fig