from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.summary_cards import get_summary_cards_layout

def register_callbacks(app):
    @app.callback(
        Output("summary-cards-container", "children"),
        Input("filtered-query-store", "data"),
    )
    def update_summary_cards(filtered_query):
        q_total_logins = 'SELECT SUM([LoginCount]) AS TotalLogins ' + filtered_query
        q_unique_users = 'SELECT COUNT(DISTINCT [UserId]) AS UniqueUsers '+ filtered_query
        # q_avg_logins_per_user = 'SELECT AVG([LoginCount]) AS AvgLoginsPerUser '+ filtered_query
        q_most_used_app = 'SELECT TOP 10 [App], SUM([LoginCount]) AS TotalLogins '+ filtered_query + ' GROUP BY [App] ORDER BY TotalLogins DESC'
        q_top_office = 'SELECT TOP 10 [OfficeName], SUM([LoginCount]) AS TotalLogins ' + filtered_query + ' GROUP BY [OfficeName] ORDER BY TotalLogins DESC'
        queries = {
            "total_logins": q_total_logins,
            "unique_users": q_unique_users,
            # "avg_logins_per_user": q_avg_logins_per_user,
            "most_used_app": q_most_used_app,
            "top_office": q_top_office
        }   

        results = run_queries(queries, len(queries.keys()))    
        total_logins = results["total_logins"].iloc[0]["TotalLogins"] if not results["total_logins"].empty else 0
        unique_users = results["unique_users"].iloc[0]["UniqueUsers"] if not results["unique_users"].empty else 0
        avg_login_per_user = int(total_logins/unique_users) if unique_users != 0 else ""

        if total_logins is not None and total_logins > 0:
            total_logins = f"{total_logins:,}"
        else:
            total_logins = ""
        if unique_users is not None and unique_users > 0:
            unique_users = f"{unique_users:,}"
        else:
            unique_users = ""        
        

        filtered_data = {
            "TotalLogins": total_logins,
            "UniqueUsers": unique_users,
            "AvgLoginsPerUser": avg_login_per_user,
            "MostUsedApp": results["most_used_app"].iloc[0]["App"] if not results["most_used_app"].empty else "N/A",
            "TopOffice": results["top_office"].iloc[0]["OfficeName"] if not results["top_office"].empty else "N/A"
        }
        return get_summary_cards_layout(filtered_data)    