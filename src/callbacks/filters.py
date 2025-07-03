from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries

def register_callbacks(app):
    @app.callback(
        Output("filter-data-store", "data"),
        Input("filtered-query-store", "id"),  # This will trigger on page load; you can use any component that always exists
        prevent_initial_call=False
    )
    def load_filter_data(_):
        q_unique_members ='SELECT [UserId], [MemberName]  FROM [consumable].[unique_members] order by [TotalLogins] desc'
        q_unique_offices = 'SELECT [OfficeName]  FROM [consumable].[unique_offices] order by [TotalLogins] desc'
        q_unique_apps = 'SELECT [App]  FROM [consumable].[unique_apps] order by [TotalLogins] desc'
        q_unique_login_counts = 'SELECT [LoginCount]  FROM [consumable].[unique_login_counts] order by [LoginCount]'
        q_earliest_and_latest_dates = 'SELECT [EarliestDay], [LatestDay]  FROM [consumable].[earliest_and_latest_dates]'
        
        queries = {
            "unique_members": q_unique_members,
            "unique_offices": q_unique_offices,
            "unique_apps": q_unique_apps,
            "unique_login_counts": q_unique_login_counts,
            "earliest_and_latest_dates": q_earliest_and_latest_dates,
        }    
        results = run_queries(queries, len(queries.keys()))
        # Convert DataFrames to dict for storage in dcc.Store
        return {
            "unique_members": results["unique_members"].to_dict("records"),
            "unique_offices": results["unique_offices"].to_dict("records"),
            "unique_apps": results["unique_apps"].to_dict("records"),
            "unique_login_counts": results["unique_login_counts"].to_dict("records"),
            "earliest_and_latest_dates": results["earliest_and_latest_dates"].to_dict("records"),
        }

    @app.callback(
        Output("app-dropdown", "options"),
        Output("office-dropdown", "options"),
        Output("user-dropdown", "options"),
        Output("member-dropdown", "options"),
        Output("login-count-slider", "min"),
        Output("login-count-slider", "max"),
        Output("login-count-slider", "marks"),
        Output("date-range-picker", "start_date_placeholder_text"),
        Output("date-range-picker", "end_date_placeholder_text"),
        Input("filter-data-store", "data"),
    )
    def populate_filters(filter_data):
        if not filter_data:
            # Return empty/defaults
            return [], [], [], [], 0, 0, {}, "", ""
        df_unique_members = pd.DataFrame(filter_data["unique_members"])
        df_unique_offices = pd.DataFrame(filter_data["unique_offices"])
        df_unique_apps = pd.DataFrame(filter_data["unique_apps"])
        df_unique_login_counts = pd.DataFrame(filter_data["unique_login_counts"])
        df_earliest_and_latest_dates = pd.DataFrame(filter_data["earliest_and_latest_dates"])

        app_options = [{"label": str(v), "value": v} for v in df_unique_apps["App"] if pd.notnull(v)]
        office_options = [{"label": str(v), "value": v} for v in df_unique_offices["OfficeName"] if pd.notnull(v)]
        user_options = [{"label": str(v), "value": v} for v in df_unique_members["UserId"] if pd.notnull(v)]
        member_options = [{"label": str(v), "value": v} for v in df_unique_members["MemberName"] if pd.notnull(v)]

        min_login = int(df_unique_login_counts["LoginCount"].min())
        max_login = int(df_unique_login_counts["LoginCount"].max())
        marks = {str(count): str(count) for count in range(min_login, max_login + 1, 45)}

        start_placeholder = df_earliest_and_latest_dates["EarliestDay"][0]
        end_placeholder = df_earliest_and_latest_dates["LatestDay"][0]

        return app_options, office_options, user_options, member_options, min_login, max_login, marks, str(start_placeholder), str(end_placeholder)

    # --- Callback to clear all filters ---
    @app.callback(
        Output("app-dropdown", "value", allow_duplicate=True),
        Output("office-dropdown", "value", allow_duplicate=True),
        Output("user-dropdown", "value", allow_duplicate=True),
        Output("member-dropdown", "value", allow_duplicate=True),
        Output("login-count-slider", "value", allow_duplicate=True),
        Output("date-range-picker", "start_date", allow_duplicate=True),
        Output("date-range-picker", "end_date", allow_duplicate=True),
        Input("clear-filters-btn", "n_clicks"),
        Input("filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def clear_all_filters(n_clicks, filter_data):
        app_default = []
        office_default = []
        user_default = []
        member_default = []
        if not filter_data:
            login_count_default = [0, 0]
            date_start_default = ""
            date_end_default = ""
        else:
            df_unique_login_counts = pd.DataFrame(filter_data["unique_login_counts"])
            df_earliest_and_latest_dates = pd.DataFrame(filter_data["earliest_and_latest_dates"])        
            login_count_default = [int(df_unique_login_counts["LoginCount"].min()), int(df_unique_login_counts["LoginCount"].max())]
            date_start_default = df_earliest_and_latest_dates["EarliestDay"][0]
            date_end_default = df_earliest_and_latest_dates["LatestDay"][0]
        return app_default, office_default, user_default, member_default, login_count_default, date_start_default, date_end_default

    @app.callback(
        Output("app-dropdown", "value"),
        Output("select-all-apps", "value"),
        Input("select-all-apps", "value"),
        State("app-dropdown", "options"),
        prevent_initial_call=True
    )
    def select_all_apps(select_all, options):
        all_values = [opt["value"] for opt in options]
        if "all" in select_all:
            return all_values, ["all"]
        return [], []

    @app.callback(
        Output("filtered-query-store", "data"), 
        Input("app-dropdown", "value"),
        Input("office-dropdown", "value"),
        Input("user-dropdown", "value"),
        Input("member-dropdown", "value"),    
        Input("login-count-slider", "value"),
        Input("date-range-picker", "start_date"),
        Input("date-range-picker", "end_date"),    
    )
    def filter_data_query(selected_apps, selected_offices, selected_users, selected_members, login_count_range, start_date, end_date):
        query = "FROM [consumable].[vw_user_logins_by_day_user_app_office] "
        if start_date is not None and end_date is not None:
            query += f"WHERE CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE) BETWEEN CAST('{start_date}' AS DATE) AND CAST('{end_date}' AS DATE) "
        elif end_date is not None:
            query += f"WHERE CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE) <= CAST('{end_date}' AS DATE) "
        elif start_date is not None:
            query += f"WHERE CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE) >= CAST('{start_date}' AS DATE) "
        else:
            query += "WHERE 1=1 "    

        if selected_apps and "All" not in selected_apps:
            query += f" AND [App] IN ({', '.join(['\''+app+'\'' for app in selected_apps])})"

        if selected_offices and "All" not in selected_offices:
            query += f" AND [OfficeName] IN ({', '.join(['\''+office+'\'' for office in selected_offices])})"        

        if selected_users and "All" not in selected_users:
            query += f" AND [UserId] IN ({', '.join(['\''+user+'\'' for user in selected_users])})"        

        if selected_members and "All" not in selected_members:
            query += f" AND [MemberName] IN ({', '.join(['\''+member+'\'' for member in selected_members])})"                

        if login_count_range and isinstance(login_count_range, (list, tuple)) and len(login_count_range) == 2:
            query += f" AND [LoginCount] BETWEEN {login_count_range[0]} AND {login_count_range[1]}"
        
        # print("Generated Query:", query)  # Debugging line to check the generated query
        return query
