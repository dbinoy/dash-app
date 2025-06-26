from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def weekly_login_trends_layout():
    return dbc.Card([
        dbc.CardHeader("Weekly Login Trends"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Aggregate by: "),
                    dcc.Dropdown(
                        id="trend-breakdown-dropdown",
                        options=[
                            {"label": "None", "value": "None"},
                            {"label": "App", "value": "App"},
                            {"label": "Office", "value": "OfficeName"},
                            {"label": "User", "value": "UserId"},
                        ],
                        value="None",
                        clearable=False,
                    )
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Top N"),
                    dcc.Slider(
                        id="trend-top-n-slider",
                        min=3,
                        max=20,
                        step=1,
                        value=3,
                        marks={i: str(i) for i in [3, 5, 7, 10, 15, 20]},
                        tooltip={"placement": "bottom", "always_visible": False},
                        updatemode="mouseup",
                        included=False,
                    )
                ])
            ]),
            dcc.Graph(id="weekly-login-trends-graph")
        ])
    ])

def get_weekly_login_trends_figure(filtered_df, breakdown_dim="None", top_n=3):
    if filtered_df is None or filtered_df.empty :
        fig = px.line(title="Weekly Login Trends")
        fig.update_layout(
            xaxis_title="Week Starting",
            yaxis_title="Login Count",
            template="plotly_white"
        )
        return fig

    # Group by Week and sum LoginCount
    df = filtered_df.copy()
    if "Week" in df.columns and "LoginCount" in df.columns and "StartOfWeek" in df.columns:
        df["StartOfWeek"] = pd.to_datetime(df["StartOfWeek"], errors="coerce")

        if breakdown_dim == "None":
            weekly = df.groupby("StartOfWeek")["LoginCount"].sum().reset_index()
            fig = px.line(
                weekly,
                x="StartOfWeek",
                y="LoginCount",
                title="Weekly Login Trends"
            )
            fig.update_layout(
                xaxis_title="Week Starting",
                yaxis_title="Login Count",
                template="plotly_white"
            )
            return fig
        else:
            # Aggregate by Week and breakdown_dim
            grouped = df.groupby(["StartOfWeek", breakdown_dim])["LoginCount"].sum().reset_index()

            # Get top N entities by total LoginCount
            top_entities = (
                grouped.groupby(breakdown_dim)["LoginCount"].sum()
                .sort_values(ascending=False)
                .head(top_n)
                .index
            )
            filtered_grouped = grouped[grouped[breakdown_dim].isin(top_entities)]

            fig = px.line(
                filtered_grouped,
                x="StartOfWeek",
                y="LoginCount",
                color=breakdown_dim,
                title=f"Weekly Login Trends by {breakdown_dim}",
                markers=True
            )
            fig.update_layout(
                xaxis_title="Week Starting",
                yaxis_title="Login Count",
                template="plotly_white",
                legend_title=breakdown_dim,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-1,
                    xanchor="center",
                    x=0.5,
                    bgcolor='rgba(255,255,255,0.5)',  # semi-transparent white
                    bordercolor='rgba(0,0,0,0)',
                    borderwidth=0,
                    font=dict(size=12)
                )                
            )
            return fig            
    else:
        fig = px.line(title="Weekly Login Trends")
        fig.update_layout(
            xaxis_title="Week",
            yaxis_title="Login Count",
            template="plotly_white"
        )
        return fig