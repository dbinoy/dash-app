from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def azure_cost_drivers_layout():
    return dbc.Card([
        dbc.CardHeader("Top Cloud Cost Drivers"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("By: "),
                    dcc.Dropdown(
                        id="azure-cost-driver-by-dropdown",
                        options=[
                            {"label": "Subscriptions", "value": "SubscriptionName"},
                            {"label": "Resource Groups", "value": "ResourceGroup"},
                            {"label": "Providers", "value": "Provider"},
                            {"label": "Services", "value": "ServiceName"},
                            {"label": "Resource Types", "value": "ResourceType"}
                        ],
                        value="SubscriptionName",
                        clearable=False,
                    )
                ], width=3),  
                dbc.Col([
                    html.Label("Top: "),
                    dcc.Slider(
                        id="azure-cost-driver-top-n-slider",
                        min=1,
                        max=20,
                        step=1,
                        value=10,
                        marks={i: str(i) for i in range(1, 21)}
                    )
                ], width=9),                            
            ]),
            dcc.Graph(id="azure-top-cost-drivers-graph")
        ])
    ])

def get_top_cost_driver_figure(df, by):
    
    match by:
        case "SubscriptionName":
            x_title = "Subscription"
            df['SubscriptionName'] = df['SubscriptionName'].fillna('Unknown').replace('', 'Unknown')
        case "ResourceGroup":
            x_title = "Resource Group"
            df['ResourceGroup'] = df['ResourceGroup'].fillna('Unknown').replace('', 'Unknown')
        case "Provider":
            x_title = "Provider"
            df['Provider'] = df['Provider'].fillna('Unknown').replace('', 'Unknown')
        case "ServiceName":
            x_title = "Service"
            df['ServiceName'] = df['ServiceName'].fillna('Unknown').replace('', 'Unknown')
        case "ResourceType":
            x_title = "Resource Type"
            df['ResourceType'] = df['ResourceType'].fillna('Unknown').replace('', 'Unknown')
        case _:
            x_title = "Unknown"               

    if df is not None and (not df.empty) and f"TotalCost" in df.columns: 
        fig = px.bar(
            df,
            x=by,
            y='TotalCost',
            title=f"Azure Cost Breakdown By {x_title}",
            labels={
                'TotalCost': 'Total Cost (USD)',
                by: x_title
            }
        )
    else:
        fig = px.bar(title="Azure Cost Breakdown")        
    fig.update_layout(
        xaxis_title=x_title,
        yaxis_title="Total Cost (USD)",
        xaxis={'categoryorder': 'total descending'},
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=150)
    )        
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>" +
                        "Cost: $%{y:,.2f}<br>" +
                        "<extra></extra>"
    )        
    return fig        
