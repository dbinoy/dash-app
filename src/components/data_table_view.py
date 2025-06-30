from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd

def data_table_view_layout():
    return dbc.Card([
        dbc.CardHeader("Data Table View"),
        dbc.CardBody([
            dash_table.DataTable(
                id="data-table",
                columns=[
                    {"name": "Year", "id": "year"},
                    {"name": "StartOfWeek", "id": "startofweek"},
                    {"name": "App", "id": "app"},
                    {"name": "OfficeName", "id": "officename"},
                    {"name": "UserId", "id": "userid"},
                    {"name": "LoginCount", "id": "logincount"}
                ],
                page_size=50,
                filter_action="native",
                sort_action="native",
                page_action="native"
            ),
            html.Div("Showing 1000 rows", style={"color": "red", "fontSize": "12px"}),
            html.Small("Full data table view with filtering, sorting, and pagination capabilities. Limited to a maximum of 10000 rows.")            
        ])
    ])

def get_data_table_data(df, max_rows=1000):
    # # Only keep the columns that are present in the DataTable
    # columns = ["Year", "Week", "App", "OfficeName", "UserId"]
    # # Handle case-insensitive column names
    # col_map = {col.lower(): col for col in filtered_df.columns}
    # selected_cols = [col_map.get(c.lower(), c) for c in columns if c.lower() in col_map]
    # df = filtered_df[selected_cols].copy() if selected_cols else pd.DataFrame(columns=columns)
    # Convert Year and Week to string for DataTable filtering to work
    for col in ["Year", "LoginCount"]:
        if col in df.columns:
            df[col] = df[col].astype(str)    
    # Limit to max_rows
    df = df.head(max_rows)
    # Rename columns to match DataTable headers
    df.columns = [c.lower() for c in df.columns]
    return df.to_dict("records")