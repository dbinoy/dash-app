from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.azure_cost_components.azure_cost_breakdown import get_azure_cost_breakdown_figure

def register_callbacks(app):
    @app.callback(
        Output("azure-total-spending-breakdown-graph", "figure"),
        Input("azure-cost-filtered-query-store", "data"),
        Input("total-spending-breakdown-dropdown", "value")
    )
    def update_azure_cost_breakdown(selections, group_by):
        table_name = f"[azure_monthly_cost_by_tenant_subscriptionname_resourcegroup_provider_servicename_resourcetype]"
        group_by_clause = ', '.join(['['+group+']' for group in group_by.split(",")])
        fields = f'{group_by_clause}, SUM([TotalCostUSD]) AS TotalCost'
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

        q_cost_breakdown = f"SELECT {fields} FROM [consumable].{table_name} {where_clause} GROUP BY {group_by_clause} ORDER BY {group_by_clause}"

        queries = {
            "cost_breakdown": q_cost_breakdown
        }   

        results = run_queries(queries, len(queries.keys()))    

        filtered_df = results["cost_breakdown"]
        return get_azure_cost_breakdown_figure(filtered_df, group_by)


