from dash import html
import dash_bootstrap_components as dbc

def get_summary_cards_layout(filtered_data):
    # Aggregations
    total_cost = filtered_data['TotalCost']
    # unique_users = filtered_data['UniqueUsers']
    # avg_logins_per_user = filtered_data['AvgLoginsPerUser']
    # most_used_app = filtered_data['MostUsedApp']
    # top_office = filtered_data['TopOffice']

    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{total_cost}", className="card-title"),
                html.P("Total Cost (USD)", className="card-text")
            ])
        ]), width=2),
        # dbc.Col(dbc.Card([
        #     dbc.CardBody([
        #         html.H4(f"{unique_users}", className="card-title"),
        #         html.P("Unique Users", className="card-text")
        #     ])
        # ]), width=2),
        # dbc.Col(dbc.Card([
        #     dbc.CardBody([
        #         html.H4(f"{avg_logins_per_user}", className="card-title"),
        #         html.P("Avg Logins per User", className="card-text")
        #     ])
        # ]), width=2),
        # dbc.Col(dbc.Card([
        #     dbc.CardBody([
        #         html.H4(str(most_used_app), className="card-title"),
        #         html.P("Most Used App", className="card-text")
        #     ])
        # ]), width=3),
        # dbc.Col(dbc.Card([
        #     dbc.CardBody([
        #         html.H4(str(top_office), className="card-title"),
        #         html.P("Top Office", className="card-text")
        #     ])
        # ]), width=3)
    ])