from dash import html
import dash_bootstrap_components as dbc

def get_summary_cards_layout(filtered_df):
    # Aggregations
    total_logins = int(filtered_df['LoginCount'].sum()) if 'LoginCount' in filtered_df.columns else 0
    unique_users = filtered_df['UserId'].nunique() if 'UserId' in filtered_df.columns else 0
    avg_logins_per_user = int(round(total_logins / unique_users, 0)) if unique_users > 0 else 0

    # Most used app
    most_used_app = (
        filtered_df.groupby('App')['LoginCount'].sum().sort_values(ascending=False).index[0]
        if 'App' in filtered_df.columns and not filtered_df.empty else "N/A"
    )

    # Top office
    top_office = (
        filtered_df.groupby('OfficeName')['LoginCount'].sum().sort_values(ascending=False).index[0]
        if 'OfficeName' in filtered_df.columns and not filtered_df.empty else "N/A"
    )

    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{total_logins:,}", className="card-title"),
                html.P("Total Logins", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{unique_users:,}", className="card-title"),
                html.P("Unique Users", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(f"{avg_logins_per_user}", className="card-title"),
                html.P("Avg Logins per User", className="card-text")
            ])
        ]), width=2),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(str(most_used_app), className="card-title"),
                html.P("Most Used App", className="card-text")
            ])
        ]), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(str(top_office), className="card-title"),
                html.P("Top Office", className="card-text")
            ])
        ]), width=3)
    ])

# summary_cards_layout = dbc.Row([
#     dbc.Col(dbc.Card([
#         dbc.CardBody([
#             html.H4("2,703,1...", className="card-title"),
#             html.P("Total Logins", className="card-text")
#         ])
#     ]), width=2),
#     dbc.Col(dbc.Card([
#         dbc.CardBody([
#             html.H4("75,631", className="card-title"),
#             html.P("Unique Users", className="card-text")
#         ])
#     ]), width=2),
#     dbc.Col(dbc.Card([
#         dbc.CardBody([
#             html.H4("35.7", className="card-title"),
#             html.P("Avg Logins per User", className="card-text")
#         ])
#     ]), width=2),
#     dbc.Col(dbc.Card([
#         dbc.CardBody([
#             html.H4("CRMLS Matrix", className="card-title"),
#             html.P("Most Used App", className="card-text")
#         ])
#     ]), width=2),
#     dbc.Col(dbc.Card([
#         dbc.CardBody([
#             html.H4("Coldwell Banker R...", className="card-title"),
#             html.P("Top Office", className="card-text")
#         ])
#     ]), width=2)
# ])