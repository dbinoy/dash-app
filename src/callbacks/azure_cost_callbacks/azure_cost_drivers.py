from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.azure_cost_components.azure_cost_drivers import get_top_cost_driver_figure

def register_callbacks(app):
    @app.callback(
        Output("azure-top-cost-drivers-graph", "figure"),
        Input("azure-cost-filtered-query-store", "data"),
        Input("azure-cost-driver-by-dropdown", "value"),
        Input("azure-cost-driver-top-n-slider", "value"),
    )
    def update_azure_cost_breakdown(selections, by, top_n):
        table_name = f"[azure_monthly_cost_by_tenant_subscriptionname_resourcegroup_provider_servicename_resourcetype]"
        select_clause = f"SELECT TOP {top_n} [{by}], SUM(TotalCostUSD) AS TotalCost FROM [consumable].{table_name}"

        where_clause = f"WHERE 1=1"        
        for k in selections.keys():
            if selections[k] and selections[k] != "All":
                match k:
                    case "UsageDay_From":
                        where_clause = f"{where_clause} AND [BillingMonth] >= CAST('{selections[k]}' AS DATE)"
                    case "UsageDay_To":
                        where_clause = f"{where_clause} AND [BillingMonth] <= CAST('{selections[k]}' AS DATE)"
                    case _:
                        where_clause = f"{where_clause} AND [{k}] IN ({selections[k]})"

        q_cost_drivers = f"{select_clause} {where_clause} GROUP BY {by} ORDER BY TotalCost DESC"

        queries = {
            "cost_drivers": q_cost_drivers
        }   

        results = run_queries(queries, len(queries.keys()))    

        filtered_df = results["cost_drivers"]
        return get_top_cost_driver_figure(filtered_df, by)


