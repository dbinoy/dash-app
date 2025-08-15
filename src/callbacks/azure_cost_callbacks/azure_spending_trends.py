from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.azure_cost_components.azure_spending_trends import get_azure_spending_trends_figure

def register_callbacks(app):
    @app.callback(
        Output("azure-spending-trends-graph", "figure"),
        Input("azure-cost-filtered-query-store", "data"),
        Input("spending-trend-time-aggregation-dropdown", "value"),
        Input("spending-trend-group-by-dropdown", "value")  
    )
    def update_azure_spending_trends(selections, time_aggregation, group_by):
        table_name = f"[{time_aggregation[0]}_cost_by_tenant_sub_rg_provider_service_reservation_type_app_costcenter_product_project]"
        fields = f'SUM([TotalCostUSD]) AS {time_aggregation.capitalize()}Cost'
        group_by_clause = ''
        where_clause = f"WHERE 1=1"
        match time_aggregation:
            case "daily":
                fields = f"[UsageDay], {fields}"
                group_by_clause = "[UsageDay]"
            case "weekly":
               fields = f"[WeekStartDate], DATEPART(year, [WeekStartDate]) AS [Year], DATEPART(week, [WeekStartDate]) AS [Week],  {fields}"
               group_by_clause = "[WeekStartDate]"
            case "monthly":
                fields = f"[BillingMonth], DATEPART(year, [BillingMonth]) AS [Year], DATEPART(month, [BillingMonth]) AS [Month],  {fields}"
                group_by_clause = "[BillingMonth]"
            case _:
                fields = f"{fields}"

        match group_by:
            case "subscriptionname":
                fields = f"[SubscriptionName], {fields}"
                group_by_clause = f"[SubscriptionName], {group_by_clause}"
            case "resourcegroup":
                fields = f"[ResourceGroup], {fields}"       
                group_by_clause = f"[ResourceGroup], {group_by_clause}"            
            case "servicename":
                fields = f"[ServiceName], {fields}"
                group_by_clause = f"[ServiceName], {group_by_clause}"
            case _:
                fields = f"{fields}"
                group_by_clause = f"{group_by_clause}"

        for k in selections.keys():
            if selections[k] and selections[k] != "All":
                match k:
                    case "UsageDay_From":
                        match time_aggregation:
                            case "daily":
                                where_clause = f"{where_clause} AND [UsageDay] >= CAST('{selections[k]}' AS DATE)"
                            case "weekly":
                                where_clause = f"{where_clause} AND [WeekStartDate] >= CAST('{selections[k]}' AS DATE)"
                            case "monthly":
                                where_clause = f"{where_clause} AND [BillingMonth] >= CAST('{selections[k]}' AS DATE)"
                    case "UsageDay_To":
                        match time_aggregation:
                            case "daily":
                                where_clause = f"{where_clause} AND [UsageDay] <= CAST('{selections[k]}' AS DATE)"
                            case "weekly":
                                where_clause = f"{where_clause} AND [WeekStartDate] <= CAST('{selections[k]}' AS DATE)"
                            case "monthly":
                                where_clause = f"{where_clause} AND [BillingMonth] <= CAST('{selections[k]}' AS DATE)"

                    case _:
                        where_clause = f"{where_clause} AND [{k}] IN ({selections[k]})"

        q_cost_trend = f"SELECT {fields} FROM [consumable].{table_name} {where_clause} GROUP BY {group_by_clause} ORDER BY {group_by_clause}"

        queries = {
            "cost_trend": q_cost_trend
        }   

        results = run_queries(queries, len(queries.keys()))    

        filtered_df = results["cost_trend"]
        return get_azure_spending_trends_figure(filtered_df, time_aggregation, group_by)


