from dash import html, dcc
import dash_bootstrap_components as dbc

from src.components.azure_cost_components.filters import get_filters_layout

def create_azure_cost_layout():
    return dbc.Container([
        dcc.Store(id="azure-cost-filtered-query-store"),
        dcc.Store(id="azure-cost-filter-data-store"),
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
        html.Br()                 
    ], fluid=True)    
    # return html.Div([
    #     dbc.Row([
    #         dbc.Col(html.H1("Azure Cost Analysis"), width=12)
    #     ]),
    #     dbc.Row([
    #         dbc.Col(html.P("This section provides insights into Azure costs."), width=12)
    #     ]),
    #     dbc.Row([
    #         dbc.Col(dbc.Button("View Costs", color="primary"), width={"size": 2, "offset": 5})
    #     ])
    # ])
