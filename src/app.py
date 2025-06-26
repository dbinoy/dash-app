import os
import dash
import pandas as pd
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


# Load data once here
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/app_logins_by_user.csv')
df = pd.read_csv(DATA_PATH)
df = df.fillna('None')
df['StartOfWeek'] = pd.to_datetime(df['StartOfWeek'], format='%Y-%m-%d', errors='coerce')
df['EndOfWeek'] = pd.to_datetime(df['EndOfWeek'], format='%Y-%m-%d', errors='coerce')

# Pass df to components
from components.filters import get_filters_layout
from components.summary_cards import get_summary_cards_layout
# from components.weekly_login_trends import weekly_login_trends_layout, get_weekly_login_trends_figure
# from components.app_usage_by_office import app_usage_by_office_layout, get_app_usage_by_office_figure
# from components.user_activity_distribution import user_activity_distribution_layout, get_user_activity_distribution_figure
# from components.weekly_app_popularity import weekly_app_popularity_layout, get_weekly_app_popularity_figure
# from components.data_table_view import data_table_view_layout, get_data_table_data

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dcc.Store(id="filtered-data-store"),
    dbc.Row([
        dbc.Col(html.H2("User Login Telemetry Dashboard"), width=8),
        dbc.Col(html.Img(src="https://images.plot.ly/logo/new-branding/plotly-logomark.png", height="40px"), width=4, style={"textAlign": "right"})
    ], align="center", className="my-2"),
    # dbc.Row([
    #     dbc.Col(html.Div([
    #         html.Small("Data Updated: 2025-06-25"),
    #         html.Small(" | Created by: Binoy Das with help from Github Copilot"),
    #         html.Small(" | Data Source: User Login Telemetry Data from REcore CRIB database")
    #     ]))
    # ]),
    html.Hr(),
    dbc.Row([
        dbc.Col(
            dbc.Button("Clear All Filters", id="clear-filters-btn", color="secondary", outline=True, className="mb-2"),
            width="auto"
        )
    ]),    
    get_filters_layout(df),
    html.Br(),
    # get_summary_cards_layout(df),
    html.Div(id="summary-cards-container"),
    html.Br(),

    dbc.Row([
        # dbc.Col(weekly_login_trends_layout(), width=6),
        # dbc.Col(app_usage_by_office_layout(), width=6)
    ]),
    html.Br(),
    dbc.Row([
        # dbc.Col(user_activity_distribution_layout(), width=6),
        # dbc.Col((weekly_app_popularity_layout()), width=6)
    ]),
    html.Br(),
    # data_table_view_layout()
 
], fluid=True)

# --- Select All/Deselect All Callbacks for Filters ---

def get_unique(df, col):
    return sorted([v for v in df[col].unique() if pd.notnull(v)])

@app.callback(
    Output("week-dropdown", "value"),
    Output("select-all-weeks", "value"),
    Input("select-all-weeks", "value"),
    State("week-dropdown", "options"),
    prevent_initial_call=True
)
def select_all_weeks(select_all, options):
    all_values = [opt["value"] for opt in options]
    if "all" in select_all:
        return all_values, ["all"]
    return [], []

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

# @app.callback(
#     Output("office-dropdown", "value"),
#     Output("select-all-offices", "value"),
#     Input("select-all-offices", "value"),
#     State("office-dropdown", "options"),
#     prevent_initial_call=True
# )
# def select_all_offices(select_all, options):
#     all_values = [opt["value"] for opt in options]
#     if "all" in select_all:
#         return all_values, ["all"]
#     return [], []

# @app.callback(
#     Output("user-dropdown", "value"),
#     Output("select-all-users", "value"),
#     Input("select-all-users", "value"),
#     State("user-dropdown", "options"),
#     prevent_initial_call=True
# )
# def select_all_users(select_all, options):
#     all_values = [opt["value"] for opt in options]
#     if "all" in select_all:
#         return all_values, ["all"]
#     return [], []

# @app.callback(
#     Output("member-dropdown", "value"),
#     Output("select-all-members", "value"),
#     Input("select-all-members", "value"),
#     State("member-dropdown", "options"),
#     prevent_initial_call=True
# )
# def select_all_members(select_all, options):
#     all_values = [opt["value"] for opt in options]
#     if "all" in select_all:
#         return all_values, ["all"]
#     return [], []

@app.callback(
    Output("filtered-data-store", "data"),  # or Output for your target component
    Input("week-dropdown", "value"),
    Input("app-dropdown", "value"),
    Input("office-dropdown", "value"),
    Input("user-dropdown", "value"),
    Input("member-dropdown", "value"),    
    Input("login-count-slider", "value"),
    Input("date-range-picker", "start_date"),
    Input("date-range-picker", "end_date"),    
)
def filter_data(selected_weeks, selected_apps, selected_offices, selected_users, selected_members, login_count_range, start_date, end_date):
    filtered = df.copy()
    # Weeks
    if selected_weeks and "All" not in selected_weeks:
        filtered = filtered[filtered["Week"].isin(selected_weeks)]

    # Apps
    if selected_apps and "All" not in selected_apps:
        filtered = filtered[filtered["App"].isin(selected_apps)]

    # Offices
    if selected_offices and "All" not in selected_offices:
        filtered = filtered[filtered["OfficeName"].isin(selected_offices)]

    # Users
    if selected_users and "All" not in selected_users:
        filtered = filtered[filtered["UserId"].isin(selected_users)]

    # Members
    if selected_members and "All" not in selected_members:
        filtered = filtered[filtered["MemberFullName"].isin(selected_members)]

    # Login Count Range
    if login_count_range and isinstance(login_count_range, (list, tuple)) and len(login_count_range) == 2:
        filtered = filtered[
            (filtered["LoginCount"] >= login_count_range[0]) &
            (filtered["LoginCount"] <= login_count_range[1])
        ]

    # Date Range
    if start_date:
        filtered = filtered[filtered["StartOfWeek"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["EndOfWeek"] <= pd.to_datetime(end_date)]

    return filtered.to_dict("records")

@app.callback(
    Output("summary-cards-container", "children"),
    Input("filtered-data-store", "data"),
)
def update_summary_cards(filtered_data):
    import pandas as pd
    if filtered_data is None or len(filtered_data) == 0:
        # Return empty cards or a message if no data
        return get_summary_cards_layout(pd.DataFrame())
    filtered_df = pd.DataFrame(filtered_data)
    return get_summary_cards_layout(filtered_df)


'''
@app.callback(
    Output("weekly-login-trends-graph", "figure"),
    Input("filtered-data-store", "data"),
    Input("trend-breakdown-dropdown", "value"),
    Input("trend-top-n-slider", "value")    
)
def update_weekly_login_trends(filtered_data, breakdown_dim, top_n):
    import pandas as pd
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    return get_weekly_login_trends_figure(filtered_df, breakdown_dim, top_n)
'''


'''
@app.callback(
    Output("office-filter-dropdown", "options"),
    Output("app-filter-dropdown", "options"),
    Input("filtered-data-store", "data"),
)
def update_app_usage_by_office_filters(filtered_data):
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()

    # Office dropdown options
    office_options = [{"label": "All Offices", "value": "All"}] + [{"label": office, "value": office} for office in sorted(filtered_df["OfficeName"].unique())] if "OfficeName" in filtered_df.columns else []

    # App dropdown options
    app_options = [{"label": "All Apps", "value": "All"}] + [{"label": app, "value": app} for app in sorted(filtered_df["App"].unique())] if "App" in filtered_df.columns else []

    return office_options, app_options

@app.callback(
    Output("app-usage-by-office-graph", "figure"),
    Input("filtered-data-store", "data"),
    Input("office-filter-dropdown", "value"),
    Input("app-filter-dropdown", "value"),
    Input("sortby-dropdown", "value"),
    Input("showtop-dropdown", "value"),
)
def update_app_usage_by_office_graph(filtered_data, selected_offices, selected_apps, sortby, showtop):
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    # Default values if None
    if not sortby:
        sortby = "desc"
    if not showtop:
        showtop = 10
    return get_app_usage_by_office_figure(filtered_df, selected_offices, selected_apps, sortby, int(showtop))
'''


'''
@app.callback(
    Output("activity-app-dropdown", "options"),
    Output("max-login-count-dropdown", "options"),
    Input("filtered-data-store", "data"),
)
def update_user_activity_distribution_filters(filtered_data):
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()

    # App dropdown options
    app_options = [{"label": "All Apps", "value": "All"}] + [{"label": app, "value": app} for app in sorted(filtered_df["App"].unique())] if "App" in filtered_df.columns else []

    user_login_counts = filtered_df.groupby("UserId")["LoginCount"].sum().reset_index()
    max_count = int(user_login_counts["LoginCount"].max()) if not user_login_counts.empty else 1
    count_options = [{"label": i-1, "value": i-1} for i in range(1, max_count + 1, 100)]
    return app_options, count_options

@app.callback(
    Output("user-activity-distribution-graph", "figure"),
    Input("filtered-data-store", "data"),
    Input("activity-app-dropdown", "value"),
    Input("max-login-count-dropdown", "value"),
    Input("activity-bins-slider", "value"),
)
def update_user_activity_distribution_graph(filtered_data, selected_apps, max_count, num_bins):
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    return get_user_activity_distribution_figure(filtered_df, max_count, selected_apps, num_bins)
'''


'''
@app.callback(
    Output("popularity-apps-checklist", "options"),
    Output("popularity-apps-checklist", "value"),
    Input("filtered-data-store", "data"),
)
def update_popularity_apps_checklist(filtered_data):
    import pandas as pd
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    if "App" not in filtered_df.columns or "LoginCount" not in filtered_df.columns:
        return [], []
    # Get top 10 apps by total LoginCount
    top_apps = (
        filtered_df.groupby("App")["LoginCount"].sum()
        .sort_values(ascending=False)
        .head(10)
        .index.tolist()
    )
    options = [{"label": app, "value": app} for app in top_apps]
    return options, top_apps

@app.callback(
    Output("weekly-app-popularity-graph", "figure"),
    Input("filtered-data-store", "data"),
    Input("popularity-apps-checklist", "value"),
    Input("popularity-display-type", "value"),
)
def update_weekly_app_popularity_graph(filtered_data, selected_apps, display_type):
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    return get_weekly_app_popularity_figure(filtered_df, selected_apps, display_type)
'''


'''
@app.callback(
    Output("data-table", "data"),
    Input("filtered-data-store", "data"),
)
def update_data_table(filtered_data):
    filtered_df = pd.DataFrame(filtered_data) if filtered_data else pd.DataFrame()
    return get_data_table_data(filtered_df)
'''

# --- Callback to clear all filters ---
@app.callback(
    Output("week-dropdown", "value", allow_duplicate=True),
    Output("app-dropdown", "value", allow_duplicate=True),
    Output("office-dropdown", "value", allow_duplicate=True),
    Output("user-dropdown", "value", allow_duplicate=True),
    Output("member-dropdown", "value", allow_duplicate=True),
    Output("login-count-slider", "value", allow_duplicate=True),
    Output("date-range-picker", "start_date", allow_duplicate=True),
    Output("date-range-picker", "end_date", allow_duplicate=True),
    Input("clear-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_all_filters(n_clicks):
    # Initial values for all filters
    week_default = []
    app_default = []
    office_default = []
    user_default = []
    member_default = []
    login_count_default = [int(df['LoginCount'].min()), int(df['LoginCount'].max())]
    date_start_default = df['StartOfWeek'].min().strftime('%Y-%m-%d')
    date_end_default = df['EndOfWeek'].max().strftime('%Y-%m-%d')
    return week_default, app_default, office_default, user_default, member_default, login_count_default, date_start_default, date_end_default

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=8050, debug=True)