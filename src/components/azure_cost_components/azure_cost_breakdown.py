from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

def azure_cost_breakdown_layout():
    return dbc.Card([
        dbc.CardHeader("Total Cloud Spending Breakdown"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Grouping Level: ")
                ], width=2),                 
                dbc.Col([
                    dcc.Dropdown(
                        id="total-spending-breakdown-dropdown",
                        options=[
                            {"label": "Service Only", "value": "ServiceName"},
                            {"label": "Service and ResourceGroup", "value": "ServiceName,ResourceGroup"},
                            {"label": "Service and Provider", "value": "ServiceName,Provider"}
                        ],
                        value="ServiceName",
                        clearable=False,
                    )
                ], width=4),            
            ]),
            dcc.Graph(id="azure-total-spending-breakdown-graph", style={"height": "800px"})
        ], style={"minHeight": "600px"})
    ])

def get_azure_cost_breakdown_figure(df, group_by):
    
    if 'ServiceName' in df.columns:
        df['ServiceName'] = df['ServiceName'].fillna('Unknown').replace('', 'Unknown')
    if 'ResourceGroup' in df.columns:
        df['ResourceGroup'] = df['ResourceGroup'].fillna('Unknown').replace('', 'Unknown')   
    if 'Provider' in df.columns:
        df['Provider'] = df['Provider'].fillna('Unknown').replace('', 'Unknown')                

    if df is not None and (not df.empty) and f"TotalCost" in df.columns: 

        fig = px.treemap(
            df,
            path=group_by.split(","),
            values='TotalCost',
            color='TotalCost',
            color_continuous_scale="Earth",
            hover_data={"TotalCost": ":.2f"},
            title= f"Azure Cost Breakdown by {', '.join(group_by.split(','))}"
        )        
    else:
        fig = px.treemap(title= f"Azure Cost Breakdown by {', '.join(group_by.split(','))}")           
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Cost: $%{value:,.2f}<br>Percentage: %{percentParent:,.2f}<extra></extra>"
    )   
    fig.update_layout(
        margin={"t": 30, "l": 0, "r": 0, "b": 0},
        font=dict(size=14, family="Arial"),
        title_font=dict(size=20, family="Arial", color="darkblue"),
        coloraxis_colorbar=dict(
            title="Total Cost (USD)",
            tickformat=".2f"
        )
    )    
    return fig        
