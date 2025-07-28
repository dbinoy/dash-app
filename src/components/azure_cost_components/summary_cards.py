from dash import html
import dash_bootstrap_components as dbc

def get_summary_cards_layout(filtered_data):
    # Aggregations
    total_cost = filtered_data['TotalCost']
    avg_daily_cost = filtered_data['AvgDailyCost']
    max_daily_cost = filtered_data['MaxDailyCost']
    unique_resources = filtered_data['UniqueResources']
    cost_variance = filtered_data['CostVariance']
    most_expensive_subscription = filtered_data['MostExpensiveSubscription']

    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{total_cost}", className="card-title"),
                html.P("Total Cost (USD)", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{avg_daily_cost}", className="card-title"),
                html.P("Avg Daily Cost(USD)", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{max_daily_cost}", className="card-title"),
                html.P("Max Daily Cost(USD)", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{most_expensive_subscription}", className="card-title"),
                html.P("Most Expensive", className="card-text")
            ])
        ]), width=2),         
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{unique_resources}", className="card-title"),
                html.P("Unique Resources", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{cost_variance}", className="card-title"),
                html.P("Cost Variance", className="card-text")
            ])
        ]), width=2)       
    ])