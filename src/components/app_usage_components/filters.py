from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

def make_options(values):
    return [{"label": str(v), "value": v} for v in sorted(values) if pd.notnull(v)]

def get_filters_layout():
    filters_layout = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Checklist(
                        id='select-all-apps',
                        options=[{'label': 'All Apps', 'value': 'all'}],
                        value=[],
                        inline=True,
                        style={"marginTop": "5px"}
                    ),                    
                    dcc.Dropdown(
                        id="app-dropdown", 
                        options = [],
                        placeholder="App",
                        multi=True,
                        disabled=False
                    )                 
                ], width=3),
                dbc.Col([
                    html.Br(),                     
                    dcc.Dropdown(
                        id="office-dropdown", 
                        options = [],
                        placeholder="Office Name",
                        value="All",
                        multi=True,
                        disabled=False
                    )
                ], width=3),                  
                dbc.Col([ 
                    html.Br(),            
                    dcc.Dropdown(
                        id="user-dropdown", 
                        options = [],
                        placeholder="User ID",
                        value="All",
                        multi=True,
                        disabled=False
                    )
                ], width=3),                    
                dbc.Col([   
                    html.Br(),                    
                    dcc.Dropdown(
                        id="member-dropdown", 
                        options = [],
                        placeholder="Member Name",
                        value="All",
                        multi=True,
                        disabled=False
                    )
                ], width=3)                    
            ], className="mb-2"),
            dbc.Row([                
                dbc.Col([
                    html.Label("Login Count Range"),
                    dcc.RangeSlider(
                        0,
                        0,
                        step=None,
                        id='login-count-slider',
                        updatemode="mouseup",
                        marks = {},
                        disabled=False,
                    )                     
                ], width=12)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col([
                    html.Label("Date Range"),
                    dcc.DatePickerRange(
                        id="date-range-picker",
                        start_date_placeholder_text="",
                        end_date_placeholder_text="",
                        disabled=False
                    )
                ], width=3)
            ])
        ]),
        className="mb-3"
    )    
    return filters_layout