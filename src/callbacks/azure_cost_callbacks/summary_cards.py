from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.azure_cost_components.summary_cards import get_summary_cards_layout

def create_query_filter(selections):
    query = " FROM consumable.azure_daily_cost_by_tenant_subscriptionname_resourcegroup_provider_servicename_resourcetype WHERE 1=1"
    for k in selections.keys():
        if selections[k] and selections[k] != "All":
            if k == "UsageDay_From":
                query += f" AND [UsageDay] >= CAST('{selections[k]}' AS DATE)"
            elif k == "UsageDay_To":
                query += f" AND [UsageDay] <= CAST('{selections[k]}' AS DATE)"
            else:
                query += f" AND [{k}] IN ({selections[k]})"
    return query
    
def register_callbacks(app):
    @app.callback(
        Output("azure-cost-summary-cards-container", "children"),
        Input("azure-cost-filtered-query-store", "data"),
    )
    def update_summary_cards(selections):
        query_filter = create_query_filter(selections)
        q_total_cost = 'SELECT SUM(TotalCostUSD) AS TotalCost' + query_filter

        queries = {
            "total_cost": q_total_cost,
        }   

        results = run_queries(queries, len(queries.keys()))    
        total_cost = results["total_cost"].iloc[0]["TotalCost"] if not results["total_cost"].empty else 0


        if total_cost is not None and total_cost > 0:
            total_cost = f"${total_cost:,.2f}"
        else:
            total_cost = ""      
        

        filtered_data = {
            "TotalCost": total_cost
        }
        return get_summary_cards_layout(filtered_data)    