from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def azure_spending_trends_layout():
    return dbc.Card([
        dbc.CardHeader("Cloud Spending Trends Over Time"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Time Aggregation: "),
                    dcc.Dropdown(
                        id="spending-trend-time-aggregation-dropdown",
                        options=[
                            {"label": "Daily", "value": "daily"},
                            {"label": "Weekly", "value": "weekly"},
                            {"label": "Monthly", "value": "monthly"}
                        ],
                        value="monthly",
                        clearable=False,
                    )
                ], width=6),
                dbc.Col([
                    html.Label("Group By: "),
                    dcc.Dropdown(
                        id="spending-trend-group-by-dropdown",
                        options=[
                            {"label": "Subscription", "value": "subscriptionname"},
                            {"label": "Resource Group", "value": "resourcegroup"},
                            {"label": "Service Name", "value": "servicename"}
                        ],
                        value="subscriptionname",
                        clearable=False,
                    )
                ], width=6)                
            ]),
            dcc.Graph(id="azure-spending-trends-graph")
        ])
    ])

def get_azure_spending_trends_figure(df, time_aggregation, group_by):

    match time_aggregation:
        case "daily":
            xaxis_title = "Usage Day"
        case "weekly":
            xaxis_title = "Week Starting"
        case "monthly":
            xaxis_title = "Billing Month"
        case _:
            xaxis_title = "Time Period"

    match group_by:
        case "subscriptionname":
            group_by = "SubscriptionName"
        case "resourcegroup":
            group_by = "ResourceGroup"       
        case "servicename":
            group_by = "ServiceName"

            
    if df is not None and (not df.empty) and f"{time_aggregation.capitalize()}Cost" in df.columns: 
        if "UsageDay" in df.columns:
            df["UsageDay"] = pd.to_datetime(df["UsageDay"], errors="coerce")
            fig = px.line(
                df,
                x="UsageDay",
                y=f"{time_aggregation.capitalize()}Cost",
                color=group_by,
                title=f"{time_aggregation.capitalize()} Cost Trends"
            )
        elif "WeekStartDate" in df.columns:
            df["WeekStartDate"] = pd.to_datetime(df["WeekStartDate"], errors="coerce")
            fig = px.line(
                df,
                x="WeekStartDate",
                y=f"{time_aggregation.capitalize()}Cost",
                color=group_by,
                title=f"{time_aggregation.capitalize()} Cost Trends",
                markers=True
            )
        elif "BillingMonth" in df.columns:
            df["BillingMonth"] = pd.to_datetime(df["BillingMonth"], errors="coerce")
            fig = px.line(
                df,
                x="BillingMonth",
                y=f"{time_aggregation.capitalize()}Cost",
                color=group_by,
                title=f"{time_aggregation.capitalize()} Cost Trends",
                markers=True
            )            
        else:
            fig = px.line(title=f"{time_aggregation.capitaliza()} Cost Trends")
    else:
        fig = px.line(title=f"{time_aggregation.capitaliza()} Cost Trends")
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title="Cost (USD)",
        template="plotly_white",
        legend_title=group_by,
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
        # else:
        #     # Use the range from the slider to select top entities
        #     if not top_n_range or len(top_n_range) != 2:
        #         top_n_range = [1, 3]
        #     n_min, n_max = top_n_range
        #     all_entities = (
        #         df.groupby(breakdown_dim)["LoginCount"].sum().sort_values(ascending=False)
        #     )
        #     top_entities = all_entities.iloc[n_min-1:n_max].index
        #     # print(f"Top entities for {breakdown_dim} in range {n_min}-{n_max}: {top_entities}")
        #     filtered = df[df[breakdown_dim].isin(top_entities)]

        #     fig = px.line(
        #         filtered,
        #         x="StartOfWeek",
        #         y="LoginCount",
        #         color=breakdown_dim,
        #         title=f"Weekly Login Trends by {breakdown_dim}",
        #         markers=True
        #     )
        #     fig.update_layout(
        #         xaxis_title="Week Starting",
        #         yaxis_title="Login Count",
        #         template="plotly_white",
        #         legend_title=breakdown_dim,
        #         legend=dict(
        #             orientation="h",
        #             yanchor="bottom",
        #             y=-1,
        #             xanchor="center",
        #             x=0.5,
        #             bgcolor='rgba(255,255,255,0.5)',  # semi-transparent white
        #             bordercolor='rgba(0,0,0,0)',
        #             borderwidth=0,
        #             font=dict(size=12)
        #         )                
        #     )
        #     return fig            