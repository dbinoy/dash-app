from dash import html, dcc
import dash_bootstrap_components as dbc

import plotly.express as px
import pandas as pd

def weekly_app_popularity_layout():
    return dbc.Card([
        dbc.CardHeader("Weekly App Popularity"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(dcc.RadioItems(
                    id="popularity-display-type",
                    options=[
                        {"label": "Absolute Count", "value": "count"},
                        {"label": "Percentage", "value": "percentage"}
                    ],
                    value="count",
                    inline=True
                ), width=4),
                dbc.Col(dcc.Checklist(
                    id="popularity-apps-checklist",
                    options=[],  # Fill with app options
                    value=[],
                    inline=True
                ), width=8)
            ]),
            dcc.Graph(id="weekly-app-popularity-graph"),
            html.Small("Shows the popularity of apps over time based on login counts")
        ])
    ])

def get_weekly_app_popularity_figure(filtered_df, selected_apps, display_type="count"):
    if filtered_df is None or filtered_df.empty or not selected_apps:
        fig = px.area(title="Weekly App Popularity")
        fig.update_layout(
            xaxis_title="Week Starting",
            yaxis_title="Login Count",
            template="plotly_white"
        )
        return fig

    df = filtered_df.copy()
    df["StartOfWeek"] = pd.to_datetime(df["StartOfWeek"], errors="coerce")
    # Filter for selected apps
    df = df[df["App"].isin(selected_apps)]

    # Group by StartOfWeek and App, sum LoginCount
    grouped = df.groupby(["StartOfWeek", "App"])["LoginCount"].sum().reset_index()

    if display_type == "percentage":
        # Calculate percentage for each week
        total_per_week = grouped.groupby("StartOfWeek")["LoginCount"].transform("sum")
        grouped["LoginCount"] = (grouped["LoginCount"] / total_per_week) * 100
        yaxis_title = "Login Count (%)"
    else:
        yaxis_title = "Login Count"

    fig = px.area(
        grouped,
        x="StartOfWeek",
        y="LoginCount",
        color="App",
        line_group="App",
        title="Weekly App Popularity",
        labels={"LoginCount": yaxis_title, "StartOfWeek": "Week Starting"},
    )
    fig.update_layout(
        xaxis_title="Week Starting",
        yaxis_title=yaxis_title,
        template="plotly_white",
        legend_title="App",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='rgba(0,0,0,0)',
            borderwidth=0,
            font=dict(size=12)
        )
    )
    return fig