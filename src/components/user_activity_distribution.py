from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def user_activity_distribution_layout():
    return dbc.Card([
        dbc.CardHeader("User Activity Distribution"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("App:"),
                    dcc.Dropdown(id="activity-app-dropdown", options=[], placeholder="Select App(s)", multi=True)                
                ], width=6),
                dbc.Col([
                    html.Label("Max Login Count:"),
                    dcc.Dropdown(id="max-login-count-dropdown", options=[], placeholder="Login Count")                
                ], width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Number of Bins:"),
                    dcc.Slider(id="activity-bins-slider", min=1, max=20, step=1, value=10, marks={i: str(i) for i in range(1, 21)})
                ], width=12)
            ]),
            dcc.Graph(id="user-activity-distribution-graph"),
            html.Small("Distribution of login counts across users, filterable by app")
        ])
    ])

def get_user_activity_distribution_figure(filtered_df, max_count, selected_apps=None, num_bins=10):
    df = filtered_df.copy()
    # Filter by selected apps if provided
    if selected_apps and "All" not in selected_apps:
        df = df[df["App"].isin(selected_apps)]
    # Aggregate: total logins per user
    if "UserId" not in df.columns or "LoginCount" not in df.columns:
        fig = px.histogram(title="User Activity Distribution")
        fig.update_layout(
            xaxis_title="Login Count",
            yaxis_title="Number of Users",
            template="plotly_white"
        )
        return fig

    user_login_counts = df.groupby("UserId")["LoginCount"].sum().reset_index()
    # Set bin range from 1 to max login count for a user
    # min_count = 1
    # max_count = int(user_login_counts["LoginCount"].max()) if not user_login_counts.empty else 1
    if max_count is not None:
        user_login_counts = user_login_counts[user_login_counts["LoginCount"] <= max_count]
        
    fig = px.histogram(
        user_login_counts,
        x="LoginCount",
        nbins=num_bins,
        title="User Activity Distribution",
        labels={"LoginCount": "Login Count", "count": "Number of Users"},
        opacity=0.85,
    )
    fig.update_layout(
        xaxis_title="Login Count",
        yaxis_title="Number of Users",
        template="plotly_white",
        bargap=0.05,
        margin=dict(l=40, r=20, t=60, b=60)
    )
    fig.update_traces(marker_color="#3b82f6")
    return fig