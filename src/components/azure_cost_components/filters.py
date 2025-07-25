from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

def get_filters_layout():
    filters_layout = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label("Date Range"),
                        dcc.DatePickerRange(
                            id="azure-cost-date-range-picker",
                            start_date_placeholder_text="",
                            end_date_placeholder_text="",
                            disabled=False
                        )
                    ], className="d-grid gap-1")
                ], width=3),                
                dbc.Col([
                    html.Div([
                        html.Label("Tenant"),
                        dcc.Dropdown(
                            id="tenant-dropdown", 
                            options=[],
                            placeholder="Select Tenant",
                            multi=True,
                            disabled=False
                        )
                    ], className="d-grid gap-1")
                ], width=2),   
                dbc.Col([
                    html.Div([
                        html.Label("Subscription"),
                        dcc.Dropdown(
                            id="subscription-dropdown", 
                            options=[],
                            placeholder="Select Subscription",
                            multi=True,
                            disabled=False
                        )
                    ], className="d-grid gap-1")
                ], width=2), 
                dbc.Col([
                    html.Div([
                        html.Label("ResourceGroup"),
                        dcc.Dropdown(
                            id="resourcegroup-dropdown", 
                            options=[],
                            placeholder="Select ResourceGroup",
                            multi=True,
                            disabled=False
                        )
                    ], className="d-grid gap-1")
                ], width=5),                 
            ], className="mb-2")
        ]),
        className="mb-3"
    )    
    return filters_layout