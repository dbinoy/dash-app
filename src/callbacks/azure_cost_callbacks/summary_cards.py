from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime
from src.utils.db import run_queries
from src.components.azure_cost_components.summary_cards import get_summary_cards_layout

def create_query_filter(selections, table_name="azure_daily_cost_by_tenant_subscriptionname_resourcegroup_provider_servicename_resourcetype", include_date=True, use_keys = []):
    query = f" FROM consumable.{table_name} WHERE 1=1"
    for k in selections.keys():
        if selections[k] and selections[k] != "All":
            if k == "UsageDay_From":
                if include_date:
                    query += f" AND [UsageDay] >= CAST('{selections[k]}' AS DATE)"
            elif k == "UsageDay_To":
                if include_date:
                    query += f" AND [UsageDay] <= CAST('{selections[k]}' AS DATE)"
            else:
                if len(use_keys) == 0 or k in use_keys:
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
        q_avg_cost = 'SELECT AVG(daily_cost) AS AvgDailyCost FROM (SELECT UsageDay, SUM(TotalCostUSD) AS daily_cost' + query_filter + 'GROUP BY UsageDay) AS daily_costs' 
        q_max_cost = 'SELECT MAX(daily_cost) AS MaxDailyCost FROM (SELECT UsageDay, SUM(TotalCostUSD) AS daily_cost' + query_filter + 'GROUP BY UsageDay) AS daily_costs'
        q_stdev_cost = 'SELECT STDEV(daily_cost) AS StdDevDailyCost FROM (SELECT UsageDay, SUM(TotalCostUSD) AS daily_cost' + query_filter + 'GROUP BY UsageDay) AS daily_costs'
        q_unique_resources = 'SELECT SUM(UniqueResources) AS UniqueResourceCount' + create_query_filter(selections, "azure_unique_resource_counts", False)
        q_most_expensive_subscription = f'''
        WITH DailyTotals as(SELECT Tenant, SubscriptionName, SUM(TotalCostUSD) DailyCost 
        {create_query_filter(selections, "azure_daily_cost_by_tenant_subscriptionname", False, ["Tenant","SubscriptionName"])} 
        GROUP BY Tenant, SubscriptionName) SELECT SubscriptionName FROM DailyTotals WHERE DailyCost = (SELECT MAX(DailyCost) from DailyTotals)
        '''

        queries = {
            "total_cost": q_total_cost,
            "avg_cost": q_avg_cost,
            "max_cost": q_max_cost,
            "stdev_cost": q_stdev_cost,
            "unique_resources": q_unique_resources,
            "most_expensive_subscription": q_most_expensive_subscription
        }   

        results = run_queries(queries, len(queries.keys()))    
        total_cost = results["total_cost"].iloc[0]["TotalCost"] if not results["total_cost"].empty else 0
        avg_daily_cost = results["avg_cost"].iloc[0]["AvgDailyCost"] if not results["avg_cost"].empty else 0
        max_daily_cost = results["max_cost"].iloc[0]["MaxDailyCost"] if not results["max_cost"].empty else 0
        stdev_cost = results["stdev_cost"].iloc[0]["StdDevDailyCost"] if not results["stdev_cost"].empty else 0
        unique_resources = results["unique_resources"].iloc[0]["UniqueResourceCount"] if not results["unique_resources"].empty else 0
        most_expensive_subscription = results["most_expensive_subscription"].iloc[0]["SubscriptionName"] if not results["most_expensive_subscription"].empty else "N/A"

        if total_cost is not None and total_cost > 0:
            total_cost = f"${total_cost:,.2f}"
        else:
            total_cost = ""      
        
        cost_variance = stdev_cost / avg_daily_cost if avg_daily_cost > 0 else 0

        if avg_daily_cost is not None and avg_daily_cost > 0:
            avg_daily_cost = f"${avg_daily_cost:,.2f}"
        else:
            avg_daily_cost = "$0.00"

        if max_daily_cost is not None and max_daily_cost > 0:
            max_daily_cost = f"${max_daily_cost:,.2f}"
        else:
            max_daily_cost = "$0.00"

        

        filtered_data = {
            "TotalCost": total_cost,
            "AvgDailyCost": avg_daily_cost,
            "MaxDailyCost": max_daily_cost,
            "UniqueResources": unique_resources,
            "CostVariance": f"{cost_variance:.2%}" if cost_variance > 0 else "0%",
            "MostExpensiveSubscription": most_expensive_subscription
        }
        return get_summary_cards_layout(filtered_data)    