from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime
def azure_spending_heatmap_layout():
    return dbc.Card([
        dbc.CardHeader("Resource Group Spending Heatmap"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Subscription: "),
                    dcc.Dropdown(
                        id="spending-heatmap-subscription-dropdown",
                        options=[
                            {"label": "All Subscriptions", "value": "All"}
                        ],
                        multi=True,
                        disabled=False
                    )
                ], width=4),  
                dbc.Col([
                    html.Label("Service: "),
                    dcc.Dropdown(
                        id="spending-heatmap-service-dropdown",
                        options=[
                            {"label": "All Services", "value": "All"}
                        ],
                        multi=True,
                        disabled=False
                    )
                ], width=4),
                dbc.Col([
                    html.Label("Service: "),
                    dcc.Dropdown(
                        id="spending-heatmap-timescale-dropdown",
                        options=[
                            {"label": "Daily", "value": "daily"},
                            {"label": "Weekly", "value": "weekly"},
                            {"label": "Monthly", "value": "monthly"}
                        ],
                        value="monthly",
                        clearable=False,
                    )
                ], width=4)                                                  
            ]),
            dbc.Row([                
                dbc.Col([
                    html.Label("Top Resource Groups: "),
                    dcc.Slider(
                        id="azure-spending-heatmap-top-n-slider",
                        min=1,
                        max=25,
                        step=1,
                        value=20,
                        marks={i: str(i) for i in range(1, 26)}
                    )
                ], width=12),                            
            ]),            
            html.Div(dcc.Graph(id="azure-spending-heatmap-graph", style={"height": "710px"}), id="azure-spending-heatmap-graph-container", n_clicks=0) 
        ])
    ])

def get_spending_heatmap_figure(df, top_n, selected_subscriptions, selected_services, subscription_options, service_options, time_period):
    subscription_options = list(map(lambda x: x.get('value'), subscription_options) )
    service_options = list(map(lambda x: x.get('value'), service_options)  )
    subscription_options.remove("All")
    service_options.remove("All")

    if selected_services is not None and len(selected_services) > 0 and "All" not in selected_services:        
        df = df[df["ServiceName"].isin(selected_services)]  
    else:
        if len(service_options) > 0 and "All" not in service_options:        
            df = df[df["ServiceName"].isin(service_options)]

    if selected_subscriptions is not None and len(selected_subscriptions) > 0 and "All" not in selected_subscriptions:        
        df = df[df["SubscriptionName"].isin(selected_subscriptions)]
    else:
        if len(subscription_options) > 0 and "All" not in subscription_options:        
            df = df[df["SubscriptionName"].isin(subscription_options)]  
    # print(f"Time Period: {time_period}")
    # print(f"Top N for heatmap: {top_n}")
    # print(f"Selected Subscriptions: {selected_subscriptions}")
    # print(f"Selected Services: {selected_services}")
    # print(f"Subscription Options: {subscription_options}")
    # print(f"Service Options: {service_options}")
    # print(f"DataFrame for heatmap: {df.head(20)}")
    if df is not None and (not df.empty) and f"TotalCost" in df.columns and f"UsageDay" in df.columns: 
        match time_period:
            case 'daily':
                df['TimePeriod'] = df['UsageDay'].dt.strftime('%Y-%m-%d')
            case 'weekly':
                df['TimePeriod'] = df['UsageDay'].dt.strftime('%Y-W%U')
            case 'monthly':
                df['TimePeriod'] = df['UsageDay'].dt.strftime('%Y-%m')
            case _:
                df['TimePeriod'] = df['UsageDay'].dt.strftime('%Y-%m-%d')   
        heatmap_data = df.groupby(['ResourceGroup', 'TimePeriod'])['TotalCost'].sum().reset_index()  
        pivot_data = heatmap_data.pivot_table(
            index='ResourceGroup',
            columns='TimePeriod',  # or your date column name
            values='TotalCost',  # or your cost column name
            aggfunc='sum',
            fill_value=0
        )          
        pivot_data.fillna(0, inplace=True)        
        resource_group_totals = pivot_data.sum(axis=1).sort_values(ascending=False)
        top_resource_groups = resource_group_totals.head(top_n).index
        pivot_data = pivot_data.loc[top_resource_groups]            
        match time_period:
            case 'daily':
                sorted_columns = sorted(pivot_data.columns, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
            case 'weekly':
                sorted_columns = sorted(pivot_data.columns)
            case 'monthly':
                sorted_columns = sorted(pivot_data.columns, key=lambda x: datetime.strptime(x, '%Y-%m'))
            case _:
                sorted_columns = sorted(pivot_data.columns, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))

        pivot_data = pivot_data[sorted_columns]
        fig = px.imshow(
            pivot_data.values,
            x = pivot_data.columns,
            y = pivot_data.index,
            aspect="auto",
            color_continuous_scale="Blues",
            title="Resource Group Cost Heatmap"
        )        
    else:
        fig = px.imshow([[0]], x=[""], y=[""],  aspect="auto",color_continuous_scale="Blues", title="Resource Group Cost Heatmap" )

    fig.update_layout(
        xaxis_nticks=top_n,  # adjust for readability
        yaxis_nticks=top_n,
        xaxis_title=f"Time Period ({time_period.title()})",
        yaxis_title="Resource Group",
        coloraxis_colorbar_title="Cost (USD)"    ,
        margin={"t": 30, "l": 0, "r": 0, "b": 0},    
    )

    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Period: %{x}<br>Cost: $%{z:,.2f}<extra></extra>"
    )
    fig.update_xaxes(tickangle=45)             
    return fig        
