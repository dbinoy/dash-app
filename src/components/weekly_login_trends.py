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
                    dcc.RangeSlider(
                        id="trend-top-n-slider",
                        min=1,
                        max=20,
                        step=1,
                        value=[1, 3],
                        marks={i: str(i) for i in range(1, 21)},
                        tooltip={"placement": "bottom", "always_visible": False},
                        updatemode="mouseup",
                        allowCross=False,
                    )
                ])
            ]),
            dcc.Graph(id="weekly-login-trends-graph")
        ])
    ])

def get_weekly_login_trends_figure(df, breakdown_dim="None", top_n_range=None):
    if df is None or df.empty :
        fig = px.line(title="Weekly Login Trends")
        fig.update_layout(
            xaxis_title="Week Starting",
            yaxis_title="Login Count",
            template="plotly_white"
        )
        return fig

    if "LoginCount" in df.columns and "StartOfWeek" in df.columns:
        df["StartOfWeek"] = pd.to_datetime(df["StartOfWeek"], errors="coerce")

        if breakdown_dim == "None":
            fig = px.line(
                df,
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
            # Use the range from the slider to select top entities
            if not top_n_range or len(top_n_range) != 2:
                top_n_range = [1, 3]
            n_min, n_max = top_n_range
            all_entities = (
                df.groupby(breakdown_dim)["LoginCount"].sum().sort_values(ascending=False)
            )
            top_entities = all_entities.iloc[n_min-1:n_max].index
            # print(f"Top entities for {breakdown_dim} in range {n_min}-{n_max}: {top_entities}")
            filtered = df[df[breakdown_dim].isin(top_entities)]

            fig = px.line(
                filtered,
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