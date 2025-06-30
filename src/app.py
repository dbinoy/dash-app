import os
import dash
import pyodbc
import pandas as pd
import concurrent.futures
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State
from flask_caching import Cache
from components.filters import get_filters_layout
from components.summary_cards import get_summary_cards_layout
from components.weekly_login_trends import weekly_login_trends_layout, get_weekly_login_trends_figure
from components.app_usage_by_office import app_usage_by_office_layout, get_app_usage_by_office_figure
from components.user_activity_distribution import user_activity_distribution_layout, get_user_activity_distribution_figure
from components.weekly_app_popularity import weekly_app_popularity_layout, get_weekly_app_popularity_figure
from components.data_table_view import data_table_view_layout, get_data_table_data

driver = 'ODBC Driver 18 for SQL Server'
workspace = 'lakehouse-dev-ws-ondemand'
username = 'synapseadmin'
password = 'Rec0reR0ck$'
database = 'recore_ldw'
conn_string = (
    f'DRIVER={{{driver}}};'
    f'SERVER=tcp:{workspace}.sql.azuresynapse.net,1433;'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "User Login Telemetry Dashboard"
server = app.server

app.layout = dbc.Container([
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

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',  # or 'simple' for in-memory, 'redis' for production
    'CACHE_DIR': 'cache',  # required for filesystem cache
    'CACHE_DEFAULT_TIMEOUT': 86400     # cache timeout in seconds
})


@cache.memoize()
def run_query(name_query_tuple):
    name, query = name_query_tuple
    conn = pyodbc.connect(conn_string)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return name, df

def get_unique(df, col):
    return sorted([v for v in df[col].unique() if pd.notnull(v)])

@app.callback(
    Output("filter-data-store", "data"),
    Input("filtered-query-store", "id"),  # This will trigger on page load; you can use any component that always exists
    prevent_initial_call=False
)
def load_filter_data(_):
    q_unique_members ='''
    SELECT DISTINCT [UserId], [MemberName]
    FROM [consumable].[vw_user_logins_by_day_user_app_office]
    WHERE [MemberName] IS NOT NULL
    ORDER BY [MemberName]
    '''
    q_unique_offices = '''
    SELECT DISTINCT [OfficeName]
    FROM [consumable].[vw_user_logins_by_day_user_app_office]
    WHERE [OfficeName] IS NOT NULL
    ORDER BY [OfficeName]
    '''
    q_unique_apps = '''
    SELECT DISTINCT [App]
    FROM [consumable].[vw_user_logins_by_day_user_app_office]
    WHERE [App] IS NOT NULL
    ORDER BY [App]
    '''

    q_unique_login_counts = '''
    SELECT DISTINCT [LoginCount]
    FROM [consumable].[vw_user_logins_by_day_user_app_office]
    WHERE [LoginCount] IS NOT NULL
    ORDER BY [LoginCount]
    '''

    q_earliest_and_latest_dates = '''
    SELECT MIN(CONVERT(DATE, CONCAT(Year, '-', Month, '-', Day))) AS EarliestDay,
        MAX(CONVERT(DATE, CONCAT(Year, '-', Month, '-', Day))) AS LatestDay
    FROM [consumable].[vw_user_logins_by_day_user_app_office]
    '''
    queries = {
        "unique_members": q_unique_members,
        "unique_offices": q_unique_offices,
        "unique_apps": q_unique_apps,
        "unique_login_counts": q_unique_login_counts,
        "earliest_and_latest_dates": q_earliest_and_latest_dates,
    }    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = dict(executor.map(run_query, queries.items()))
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


@app.callback(
    Output("summary-cards-container", "children"),
    Input("filtered-query-store", "data"),
)
def update_summary_cards(filtered_query):
    q_total_logins = 'SELECT SUM([LoginCount]) AS TotalLogins ' + filtered_query
    q_unique_users = 'SELECT COUNT(DISTINCT [UserId]) AS UniqueUsers '+ filtered_query
    q_avg_logins_per_user = 'SELECT AVG([LoginCount]) AS AvgLoginsPerUser '+ filtered_query
    q_most_used_app = 'SELECT TOP 10 [App], SUM([LoginCount]) AS TotalLogins '+ filtered_query + ' GROUP BY [App] ORDER BY TotalLogins DESC'
    q_top_office = 'SELECT TOP 10 [OfficeName], SUM([LoginCount]) AS TotalLogins ' + filtered_query + ' GROUP BY [OfficeName] ORDER BY TotalLogins DESC'
    queries = {
        "total_logins": q_total_logins,
        "unique_users": q_unique_users,
        "avg_logins_per_user": q_avg_logins_per_user,
        "most_used_app": q_most_used_app,
        "top_office": q_top_office
    }   
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = dict(executor.map(run_query, queries.items()))    
    filtered_data = {
        "TotalLogins": results["total_logins"].iloc[0]["TotalLogins"] if not results["total_logins"].empty else 0,
        "UniqueUsers": results["unique_users"].iloc[0]["UniqueUsers"] if not results["unique_users"].empty else 0,
        "AvgLoginsPerUser": int(round(results["avg_logins_per_user"].iloc[0]["AvgLoginsPerUser"], 0)) if not results["avg_logins_per_user"].empty else 0,
        "MostUsedApp": results["most_used_app"].iloc[0]["App"] if not results["most_used_app"].empty else "N/A",
        "TopOffice": results["top_office"].iloc[0]["OfficeName"] if not results["top_office"].empty else "N/A"
    }
    return get_summary_cards_layout(filtered_data)

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
    q_weekly_trend = "SELECT MIN(CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE)) AS StartOfWeek, "
    if breakdown_dim != "None":
        q_weekly_trend += f"[{breakdown_dim}], "
    q_weekly_trend += f"SUM([LoginCount]) AS LoginCount {filtered_query}"  
    if breakdown_dim != "None":
        q_weekly_trend += f" AND [{breakdown_dim}] IS NOT NULL AND [{breakdown_dim}] IN "
        q_weekly_trend += f"(SELECT TOP {20} [{breakdown_dim}] FROM [consumable].[vw_user_logins_by_day_user_app_office] WHERE [{breakdown_dim}] IS NOT NULL "
        if breakdown_dim == "App":
            if selected_apps and "All" not in selected_apps:
                q_weekly_trend += f"AND [App] IN ({', '.join(['\''+app+'\'' for app in selected_apps])}) "
        elif breakdown_dim == "OfficeName":
            if selected_offices and "All" not in selected_offices:
                q_weekly_trend += f"AND [OfficeName] IN ({', '.join(['\''+office+'\'' for office in selected_offices])}) "
        elif breakdown_dim == "UserId":
            if selected_users and "All" not in selected_users:
                q_weekly_trend += f"AND [UserId] IN ({', '.join(['\''+user+'\'' for user in selected_users])}) "
        q_weekly_trend += f"GROUP BY [{breakdown_dim}] ORDER BY SUM([LoginCount]) DESC) "
    q_weekly_trend += f"GROUP BY [Year], DATEPART(week, CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE)) "
    if breakdown_dim != "None":
        q_weekly_trend += f", [{breakdown_dim}] "
    q_weekly_trend += "ORDER BY [Year], StartOfWeek, LoginCount DESC"

    # print("Generated Trend Query:", q_weekly_trend)  # Debugging line to check the generated query

    queries = {
        "weekly_trend_data": q_weekly_trend
    }   
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))   

    filtered_df = results["weekly_trend_data"]
    return get_weekly_login_trends_figure(filtered_df, breakdown_dim, top_n)


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
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))        
    filtered_df = results["app_usage_by_office_data"]

    return get_app_usage_by_office_figure(filtered_df, selected_offices, selected_apps, sortby, int(showtop))


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
        app_options = [{"label": str(v), "value": v} for v in df_unique_apps["App"]]

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))    
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))    
    filtered_data = results["user_login_counts"]    

    return get_user_activity_distribution_figure(filtered_data, max_count, selected_apps, num_bins)




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
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))
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
    q_weekly_app_popularity = "SELECT MIN(CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE)) AS StartOfWeek, "
    q_weekly_app_popularity += f"[App], SUM([LoginCount]) AS LoginCount {filtered_query} AND [App] IS NOT NULL "  
    q_weekly_app_popularity += f"GROUP BY [Year], DATEPART(week, CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE)), [App] "
    q_weekly_app_popularity += "ORDER BY StartOfWeek, App" 

    # print("Generated Weekly App Popularity Query:", q_weekly_app_popularity)  # Debugging line to check the generated query
    queries = {
        "weekly_app_popularity_data": q_weekly_app_popularity
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))
    filtered_df = results["weekly_app_popularity_data"]
    return get_weekly_app_popularity_figure(filtered_df, selected_apps, display_type)


@app.callback(
    Output("data-table", "data"),
    Input("filtered-query-store", "data"),
)
def update_data_table(filtered_query):
    q_data_table = f'''
    SELECT
        [Year],
        MIN(CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE)) AS StartOfWeek,
        [App],
        [OfficeName],
        [UserId],
        SUM([LoginCount]) AS LoginCount
    {filtered_query}
    AND [App] IS NOT NULL
    AND [OfficeName] IS NOT NULL
    AND [UserId] IS NOT NULL
    GROUP BY
        [Year],
        DATEPART(week, CAST(CONCAT([Year], '-', RIGHT('0' + CAST([Month] AS VARCHAR(2)), 2), '-', RIGHT('0' + CAST([Day] AS VARCHAR(2)), 2)) AS DATE)),
        [App],
        [OfficeName],
        [UserId]    
    ORDER BY
        [Year], StartOfWeek, LoginCount DESC, [App], [OfficeName], [UserId]
    '''
    # print("Generated Data Table Query:", q_data_table)  # Debugging line to check the generated query
    queries = {
        "data_table_data": q_data_table
    }
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        results = dict(executor.map(run_query, queries.items()))
    filtered_df = results["data_table_data"]
    return get_data_table_data(filtered_df)

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=8050, debug=True)