from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.app_usage_components.app_usage_by_office import get_app_usage_by_office_figure

def register_callbacks(app):
    @app.callback(
        Output("office-filter-dropdown", "options"),
        Output("app-filter-dropdown", "options"),
        Input("filter-data-store", "data"),
        Input("app-dropdown", "value"),
        Input("office-dropdown", "value"),    
    )
    def update_app_usage_by_office_filters(filter_data, filtered_apps, filtered_offices):
        if not filter_data:
            # Return empty/defaults
            return [], []
        df_unique_offices = pd.DataFrame(filter_data["unique_offices"])
        df_unique_apps = pd.DataFrame(filter_data["unique_apps"])
        if filtered_apps and "All" not in filtered_apps:
            app_options = [{"label": str(v), "value": v} for v in filtered_apps]
        else:
            app_options = [{"label": str(v), "value": v} for v in df_unique_apps["App"] if pd.notnull(v)]
        if filtered_offices and "All" not in filtered_offices:
            office_options = [{"label": str(v), "value": v} for v in filtered_offices]
        else:
            office_options = [{"label": str(v), "value": v} for v in df_unique_offices["OfficeName"] if pd.notnull(v)]
        return office_options, app_options


    @app.callback(
        Output("app-usage-by-office-graph", "figure"),
        Input("filtered-query-store", "data"),
        Input("office-filter-dropdown", "value"),
        Input("app-filter-dropdown", "value"),
        Input("sortby-dropdown", "value"),
        Input("showtop-dropdown", "value"), 
    )
    def update_app_usage_by_office_graph(filtered_query, selected_offices, selected_apps, sortby, showtop):
        q_app_usage_by_office = "SELECT [OfficeName], SUM([LoginCount]) AS TotalLogins " + filtered_query

        if selected_offices and "All" not in selected_offices:
            q_app_usage_by_office += f" AND [OfficeName] IN ({', '.join(['\''+office+'\'' for office in selected_offices])})"
        if selected_apps and "All" not in selected_apps:
            q_app_usage_by_office += f" AND [App] IN ({', '.join(['\''+app+'\'' for app in selected_apps])})"
        q_app_usage_by_office += " GROUP BY [OfficeName]" 

        # print("Generated App Usage Query:", q_app_usage_by_office)  # Debugging line to check the generated query   
        queries = {
            "app_usage_by_office_data": q_app_usage_by_office
        }
        results = run_queries(queries, len(queries.keys()))        
        filtered_df = results["app_usage_by_office_data"]

        return get_app_usage_by_office_figure(filtered_df, selected_offices, selected_apps, sortby, int(showtop))
