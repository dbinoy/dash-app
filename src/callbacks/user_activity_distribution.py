from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.user_activity_distribution import get_user_activity_distribution_figure

def register_callbacks(app):
    @app.callback(
        Output("activity-app-dropdown", "options"),
        Output("max-login-count-dropdown", "options"),
        Input("filtered-query-store", "data"),
        Input("filter-data-store", "data"),
        Input("app-dropdown", "value"),    
        Input("activity-app-dropdown", "value"),
    )
    def update_user_activity_distribution_filters(filtered_query, filter_data, filtered_apps, selected_apps):
        if not filter_data:
            # Return empty/defaults
            return [], []
        df_unique_apps = pd.DataFrame(filter_data["unique_apps"])
        if filtered_apps and "All" not in filtered_apps:
            app_options = [{"label": str(v), "value": v} for v in filtered_apps]
        else:
            app_options = [{"label": str(v), "value": v} for v in df_unique_apps["App"] if pd.notnull(v)]

        q_user_login_counts = "SELECT [UserId], SUM([LoginCount]) AS LoginCount " + filtered_query
        if filtered_apps and "All" not in filtered_apps:
            q_user_login_counts += f" AND [App] IN ({', '.join(['\''+app+'\'' for app in filtered_apps])})"
        if selected_apps and "All" not in selected_apps:
            q_user_login_counts += f" AND [App] IN ({', '.join(['\''+app+'\'' for app in selected_apps])})"        
        q_user_login_counts += " GROUP BY [UserId] ORDER BY LoginCount DESC"

        # print("Generated User Login Counts Query:", q_user_login_counts)  # Debugging line to check the generated query
        queries = {
            "user_login_counts": q_user_login_counts
        }
        results = run_queries(queries, len(queries.keys()))      
        filtered_data = results["user_login_counts"]    
        # Get max login count from the results
        max_login_count = int(filtered_data["LoginCount"].max()) if not filtered_data.empty else 1
        # Create options for max login count dropdown
        if max_login_count < 100:
            count_options = [{"label": i, "value": i} for i in range(10, max_login_count + 20, 10)]  
        else:
            count_options = [{"label": i, "value": i} for i in range(100, max_login_count + 200, 100)]  
        return app_options, count_options


    @app.callback(
        Output("user-activity-distribution-graph", "figure"),
        Input("filtered-query-store", "data"),
        Input("activity-app-dropdown", "value"),
        Input("max-login-count-dropdown", "value"),
        Input("activity-bins-slider", "value"),
        Input("app-dropdown", "value"),        
    )
    def update_user_activity_distribution_graph(filtered_query, selected_apps, max_count, num_bins, filtered_apps):

        q_user_login_counts = "SELECT [UserId], SUM([LoginCount]) AS LoginCount " + filtered_query
        if filtered_apps and "All" not in filtered_apps:
            q_user_login_counts += f" AND [App] IN ({', '.join(['\''+app+'\'' for app in filtered_apps])})"
        if selected_apps and "All" not in selected_apps:
            q_user_login_counts += f" AND [App] IN ({', '.join(['\''+app+'\'' for app in selected_apps])})"        
        q_user_login_counts += " GROUP BY [UserId] ORDER BY LoginCount DESC"

        # print("Generated User Login Counts Query:", q_user_login_counts)  # Debugging line to check the generated query
        queries = {
            "user_login_counts": q_user_login_counts
        }
        results = run_queries(queries, len(queries.keys()))    
        filtered_data = results["user_login_counts"]    

        return get_user_activity_distribution_figure(filtered_data, max_count, selected_apps, num_bins)
