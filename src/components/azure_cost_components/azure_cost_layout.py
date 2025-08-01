from dash import html, dcc
import dash_bootstrap_components as dbc

from src.components.azure_cost_components.filters import get_filters_layout
from src.components.azure_cost_components.azure_spending_trends import azure_spending_trends_layout
from src.components.azure_cost_components.azure_cost_breakdown import azure_cost_breakdown_layout
from src.components.azure_cost_components.azure_cost_drivers import azure_cost_drivers_layout
from src.components.azure_cost_components.azure_spending_heatmap import azure_spending_heatmap_layout
from src.components.azure_cost_components.azure_cost_data_table_view import azure_cost_data_table_view_layout

def create_azure_cost_layout():
    return dbc.Container([
        dcc.Store(id="azure-cost-filtered-query-store"),
        dcc.Store(id="azure-cost-filter-data-store"),
        dcc.Store(id="azure-cost-table-data-store"),
        dbc.Row([
            dbc.Col(html.H2("Azure Cost Analysis Dashboard"), width=8),
            dbc.Col(html.Img(src="https://images.plot.ly/logo/new-branding/plotly-logomark.png", height="40px"), width=4, style={"textAlign": "right"})
        ], align="center", className="my-2"),  
        html.Hr(),
        dbc.Row([
            dbc.Col(
                dbc.Button("Clear All Filters", id="azure-cost-clear-filters-btn", color="secondary", outline=True, className="mb-2"),
                width="auto"
            )
        ]),
        dcc.Loading(
            id="azure-cost-loading-filters",
            type="cube",  # or "circle", "dot", "default"
            children=html.Div(get_filters_layout(), id="azure-cost-filters-container")
        ),    
        html.Br(),
        dcc.Loading(
            id="azure-cost-loading-summary-cards",
            type="default",  # or "circle", "dot", "cube"
            children=html.Div(id="azure-cost-summary-cards-container")
        ),
        html.Br(),
        dbc.Row([
            dbc.Col(
            dcc.Loading(
                id="loading-weekly-trends",
                type="dot",  # or "circle", "default", "cube"
                children=html.Div(azure_spending_trends_layout(),id="azure-spending-trends-container")
            ),
            width=12)     
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(
            dcc.Loading(
                id="loading-cost-drivers",
                type="dot",  # or "circle", "default", "cube"
                children=html.Div(azure_cost_drivers_layout(), id="azure-cost-drivers-container")
            ),
            width=12)     
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(
            dcc.Loading(
                id="loading-app-usage-by-office",
                type="dot",  # or "circle", "default", "cube"
                children=html.Div(azure_cost_breakdown_layout(), id="azure-cost-breakdown-container")
            ),
            width=6),               
            dbc.Col(
            dcc.Loading(
                id="loading-spending-heatmap",
                type="dot",  # or "circle", "default", "cube"
                children=html.Div(azure_spending_heatmap_layout(), id="azure-spending-heatmap-container")
            ),
            width=6)     
        ]),
        dcc.Loading(
            id="loading-data-table-view",
            type="circle",  # or "dot", "default", "cube"
            children=html.Div(azure_cost_data_table_view_layout(), id="data-table-view-container")
        ),           
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.Button("Close", id="close-chart-modal", className="ml-auto")),
                dbc.ModalBody(html.Div(id="modal-chart-content"))
            ],
            id="chart-modal",
            size="xl",
            is_open=False,
            centered=True,
            scrollable=True,
            backdrop="static",
            style={"padding": "0"}
        )                                        
    ], fluid=True)    
