from dash import html, dcc
import dash_bootstrap_components as dbc
from src.components.filters import get_filters_layout
from src.components.summary_cards import get_summary_cards_layout
from src.components.weekly_login_trends import weekly_login_trends_layout
from src.components.app_usage_by_office import app_usage_by_office_layout
from src.components.user_activity_distribution import user_activity_distribution_layout
from src.components.weekly_app_popularity import weekly_app_popularity_layout
from src.components.data_table_view import data_table_view_layout

def create_layout():
    return dbc.Container([
    dcc.Store(id="filtered-query-store"),
    dcc.Store(id="filter-data-store"),
    dbc.Row([
        dbc.Col(html.H2("User Login Telemetry Dashboard"), width=8),
        dbc.Col(html.Img(src="https://images.plot.ly/logo/new-branding/plotly-logomark.png", height="40px"), width=4, style={"textAlign": "right"})
    ], align="center", className="my-2"),
    html.Hr(),
    dbc.Row([
        dbc.Col(
            dbc.Button("Clear All Filters", id="clear-filters-btn", color="secondary", outline=True, className="mb-2"),
            width="auto"
        )
    ]),    
    dcc.Loading(
        id="loading-filters",
        type="cube",  # or "circle", "dot", "default"
        children=html.Div(get_filters_layout(), id="filters-container")
    ),    
    html.Br(),
    dcc.Loading(
        id="loading-summary-cards",
        type="default",  # or "circle", "dot", "cube"
        children=html.Div(id="summary-cards-container")
    ),
    html.Br(),
    dbc.Row([
        dbc.Col(
        dcc.Loading(
            id="loading-weekly-trends",
            type="dot",  # or "circle", "default", "cube"
            children=html.Div(weekly_login_trends_layout(), id="weekly-trends-container")
        ),
        width=6),
        dbc.Col(
        dcc.Loading(
            id="loading-app-usage-by-office",
            type="dot",  # or "circle", "default", "cube"
            children=html.Div(app_usage_by_office_layout(), id="app-usage-by-office-container")
        ),
        width=6)        
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
        dcc.Loading(
            id="loading-user-activity-distribution",
            type="dot",  # or "circle", "default", "cube"
            children=html.Div(user_activity_distribution_layout(), id="user-activity-distribution-container")
        ),
        width=6),
        dbc.Col(
        dcc.Loading(
            id="loading-weekly-app-popularity",
            type="dot",  # or "circle", "default", "cube"
            children=html.Div(weekly_app_popularity_layout(), id="weekly-app-popularity-container")
        ),
        width=6)        
    ]),    
    html.Br(),
    dcc.Loading(
        id="loading-data-table-view",
        type="circle",  # or "dot", "default", "cube"
        children=html.Div(data_table_view_layout(), id="data-table-view-container")
    )     
], fluid=True)
