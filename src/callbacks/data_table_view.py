from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.data_table_view import get_data_table_data

def register_callbacks(app):
    @app.callback(
        Output("data-table", "data"),
        Input("filtered-query-store", "data"),
    )
    def update_data_table(filtered_query):
        q_data_table = f'''
        SELECT
            MIN([Date]) AS StartOfWeek,
            [App],
            [OfficeName],
            [UserId],
            SUM([LoginCount]) AS LoginCount
        {filtered_query}
        AND [App] IS NOT NULL
        AND [OfficeName] IS NOT NULL
        AND [UserId] IS NOT NULL
        GROUP BY
            DATEPART(week, [Date]),
            [App],
            [OfficeName],
            [UserId]    
        ORDER BY
            StartOfWeek, LoginCount DESC, [App], [OfficeName], [UserId]
        '''
        # print("Generated Data Table Query:", q_data_table)  # Debugging line to check the generated query
        queries = {
            "data_table_data": q_data_table
        }
        results = run_queries(queries, len(queries.keys()))
        filtered_df = results["data_table_data"]
        return get_data_table_data(filtered_df)    