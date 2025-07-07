from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.weekly_app_popularity import get_weekly_app_popularity_figure

def register_callbacks(app):
    @app.callback(
        Output("popularity-apps-checklist", "options"),
        Output("popularity-apps-checklist", "value"),
        Input("filtered-query-store", "data"),
    )
    def update_popularity_apps_checklist(filtered_query):
        q_most_used_app = 'SELECT TOP 10 [App], SUM([LoginCount]) AS TotalLogins '+ filtered_query + ' AND [App] IS NOT NULL GROUP BY [App] ORDER BY TotalLogins DESC'
        # print("Generated Popularity Apps Query:", q_most_used_app)  # Debugging line to check the generated query
        queries = {
            "most_used_apps": q_most_used_app
        }
        results = run_queries(queries, len(queries.keys()))    
        filtered_data = results["most_used_apps"]
        # Ensure the DataFrame has the expected columns
        if filtered_data.empty:
            return [], []
        options = [{"label": app, "value": app} for app in filtered_data['App']]
        return options, filtered_data['App'].to_list()


    @app.callback(
        Output("weekly-app-popularity-graph", "figure"),
        Input("filtered-query-store", "data"),
        Input("popularity-apps-checklist", "value"),
        Input("popularity-display-type", "value"),
    )
    def update_weekly_app_popularity_graph(filtered_query, selected_apps, display_type):
        q_weekly_app_popularity = "SELECT MIN([Date]) AS StartOfWeek, "
        q_weekly_app_popularity += f"[App], SUM([LoginCount]) AS LoginCount {filtered_query} AND [App] IS NOT NULL "  
        q_weekly_app_popularity += f"GROUP BY DATEPART(week, [Date]), [App] "
        q_weekly_app_popularity += "ORDER BY StartOfWeek, App" 

        # print("Generated Weekly App Popularity Query:", q_weekly_app_popularity)  # Debugging line to check the generated query
        queries = {
            "weekly_app_popularity_data": q_weekly_app_popularity
        }
        results = run_queries(queries, len(queries.keys()))    
        filtered_df = results["weekly_app_popularity_data"]
        return get_weekly_app_popularity_figure(filtered_df, selected_apps, display_type)
