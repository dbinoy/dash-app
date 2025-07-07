from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.weekly_login_trends import get_weekly_login_trends_figure

def register_callbacks(app):
    @app.callback(
        Output("weekly-login-trends-graph", "figure"),
        Input("filtered-query-store", "data"),
        Input("trend-breakdown-dropdown", "value"),
        Input("trend-top-n-slider", "value"),
        Input("app-dropdown", "value"),
        Input("office-dropdown", "value"),       
        Input("user-dropdown", "value"),     
    )
    def update_weekly_login_trends(filtered_query, breakdown_dim, top_n, selected_apps, selected_offices, selected_users):
        q_weekly_trend = "SELECT MIN([Date]) AS StartOfWeek, "
        if breakdown_dim != "None":
            q_weekly_trend += f"[{breakdown_dim}], "
        q_weekly_trend += f"SUM([LoginCount]) AS LoginCount {filtered_query}"  
        if breakdown_dim != "None":
            q_weekly_trend += f" AND [{breakdown_dim}] IS NOT NULL AND [{breakdown_dim}] IN "
            q_weekly_trend += f"(SELECT TOP {20} [{breakdown_dim}] {filtered_query} AND [{breakdown_dim}] IS NOT NULL "
            if breakdown_dim == "App":
                if selected_apps and "All" not in selected_apps:
                    q_weekly_trend += f"AND [App] IN ({', '.join(['\''+app+'\'' for app in selected_apps])}) "
            elif breakdown_dim == "OfficeName":
                if selected_offices and "All" not in selected_offices:
                    q_weekly_trend += f"AND [OfficeName] IN ({', '.join(['\''+office+'\'' for office in selected_offices])}) "
            elif breakdown_dim == "UserId":
                if selected_users and "All" not in selected_users:
                    q_weekly_trend += f"AND [UserId] IN ({', '.join(['\''+user+'\'' for user in selected_users])}) "
            q_weekly_trend += f" GROUP BY [{breakdown_dim}] ORDER BY SUM([LoginCount]) DESC) "
        q_weekly_trend += f" GROUP BY DATEPART(week, [Date]) "
        if breakdown_dim != "None":
            q_weekly_trend += f", [{breakdown_dim}] "
        q_weekly_trend += "ORDER BY StartOfWeek, LoginCount DESC"

        # print("Generated Trend Query:", q_weekly_trend)  # Debugging line to check the generated query

        queries = {
            "weekly_trend_data": q_weekly_trend
        }   

        results = run_queries(queries, len(queries.keys()))    

        filtered_df = results["weekly_trend_data"]
        return get_weekly_login_trends_figure(filtered_df, breakdown_dim, top_n)


