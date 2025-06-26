from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

def make_options(values):
    return [{"label": str(v), "value": v} for v in sorted(values) if pd.notnull(v)]

def get_filters_layout(df):
    filters_layout = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Checklist(
                        id='select-all-weeks',
                        options=[{'label': 'All Weeks', 'value': 'all'}],
                        value=[],
                        inline=True,
                        style={"marginTop": "5px"}
                    ),                    
                    dcc.Dropdown(
                        id="week-dropdown", 
                        options=make_options(df['Week'].unique()), 
                        placeholder="Week",
                        multi=True
                    )                   
                ], width=1),
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
                        options=make_options(df['App'].unique()),
                        placeholder="App",
                        multi=True
                    )                 
                ], width=3),
                dbc.Col([
                    # dcc.Checklist(
                    #     id='select-all-offices',
                    #     options=[{'label': 'Select All Offices', 'value': 'all'}],
                    #     value=[],
                    #     inline=True,
                    #     style={"marginTop": "5px"}
                    # ),  
                    html.Br(),                     
                    dcc.Dropdown(
                        id="office-dropdown", 
                        options=[{"label": "All Offices", "value": "All"}] + make_options(df['OfficeName'].unique()),
                        placeholder="Office Name",
                        value="All",
                        multi=True
                    )
                ], width=3),                  
                dbc.Col([
                    # dcc.Checklist(
                    #     id='select-all-users',
                    #     options=[{'label': 'Select All Users', 'value': 'all'}],
                    #     value=[],
                    #     inline=True,
                    #     style={"marginTop": "5px"}
                    # ),   
                    html.Br(),            
                    dcc.Dropdown(
                        id="user-dropdown", 
                        options=[{"label": "All Users", "value": "All"}] + make_options(df['UserId'].unique()),
                        placeholder="User ID",
                        value="All",
                        multi=True
                    )
                ], width=2),                    
                dbc.Col([
                    # dcc.Checklist(
                    #     id='select-all-members',
                    #     options=[{'label': 'Select All Members', 'value': 'all'}],
                    #     value=[],
                    #     inline=True,
                    #     style={"marginTop": "5px"}
                    # ),    
                    html.Br(),                    
                    dcc.Dropdown(
                        id="member-dropdown", 
                        options=[{"label": "All Members", "value": "All"}] + make_options(df['MemberFullName'].unique()) if 'MemberFullName' in df.columns else [], 
                        placeholder="Member Name",
                        value="All",
                        multi=True
                    )
                ], width=3)                    
            ], className="mb-2"),
            dbc.Row([                
                dbc.Col([
                    html.Label("Login Count Range"),
                    dcc.RangeSlider(
                        0,
                        df['LoginCount'].max(),
                        step=None,
                        id='login-count-slider',
                        # value=df['LoginCount'].max(),
                        updatemode="mouseup",
                        marks={str(count-1): str(count-1) for count in range(df['LoginCount'].min(), df['LoginCount'].max() + 45, 45)},
                    )                     
                ], width=12)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col([
                    html.Label("Date Range"),
                    dcc.DatePickerRange(
                        id="date-range-picker",
                        start_date_placeholder_text=df['StartOfWeek'].min().strftime('%m/%d/%Y'),
                        end_date_placeholder_text=df['EndOfWeek'].max().strftime ('%m/%d/%Y')
                    )
                ], width=3)
            ])
        ]),
        className="mb-3"
    )    
    return filters_layout