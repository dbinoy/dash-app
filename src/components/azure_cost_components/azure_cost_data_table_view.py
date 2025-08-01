from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd

def azure_cost_data_table_view_layout():
    return dbc.Card([
        dbc.CardHeader("Data Table View"),
        dbc.CardBody([
            dash_table.DataTable(
                id="azure-cost-data-table",
                columns=[
                    {"name": "UsageDay", "id": "UsageDay"},
                    {"name": "SubscriptionName", "id": "SubscriptionName"},
                    {"name": "ResourceGroup", "id": "ResourceGroup"},
                    {"name": "Provider", "id": "userProviderd"},
                    {"name": "ServiceName", "id": "ServiceName"},
                    {"name": "ResourceType", "id": "ResourceType"},
                    {"name": "TotalCost", "id": "TotalCost"}                    
                ],
                page_size=50,
                filter_action="native",
                sort_action="native",
                page_action="native"
            ),
            html.Div("Showing 10000 rows", style={"color": "red", "fontSize": "12px"}),
            html.Small("Full data table view with filtering, sorting, and pagination capabilities. Limited to a maximum of 10000 rows.")            
        ])
    ])

def get_data_table_data(df, max_rows=10000):
    df = df.head(max_rows)

    return df.to_dict("records")