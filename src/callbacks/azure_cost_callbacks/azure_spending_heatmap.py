from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.azure_cost_components.azure_spending_heatmap import get_spending_heatmap_figure

def register_callbacks(app):

    @app.callback(
        Output("spending-heatmap-subscription-dropdown", "options"),
        Input("tenant-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        Input("subscription-dropdown", "value"),
        prevent_initial_call=True
    )
    def populate_subscription_filter(selected_tenants, filter_data, filtered_subscriptions):
        if not filter_data:
            return []
        if filtered_subscriptions and "All" not in filtered_subscriptions:
            subscription_options = [{"label": f"All Subscriptions", "value": "All"}] + [{"label": str(v), "value": v} for v in filtered_subscriptions]
        else:        
            df_unique_subscriptions = pd.DataFrame(filter_data["unique_subscriptions"])  
            if selected_tenants and len(selected_tenants) != 0 and "All" not in selected_tenants:
                df_unique_subscriptions = df_unique_subscriptions[df_unique_subscriptions["Tenant"].isin(selected_tenants)]
                selected_tenants = ' ' + ','.join(selected_tenants) + ' '
            else:
                selected_tenants = ' '
            subscription_options = [{"label": f"All{selected_tenants}Subscriptions", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_subscriptions["SubscriptionName"] if pd.notnull(v)]
        return subscription_options
        
    @app.callback(
        Output("spending-heatmap-service-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("provider-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        Input("service-dropdown", "value"),        
        Input("spending-heatmap-subscription-dropdown", "value"),
        prevent_initial_call=True
    )
    def populate_service_filter(selected_subscriptions, selected_resourcegroups, selected_providers, filter_data, filtered_services, filtered_subscriptions):
        if not filter_data:
            return []
        
        if filtered_services and "All" not in filtered_services:
            provider_options = [{"label": f"All Services", "value": "All"}] + [{"label": str(v), "value": v} for v in filtered_services]
        else:          
            df_unique_service_providers = pd.DataFrame(filter_data["unique_service_providers"])   

            if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
                df_unique_service_providers = df_unique_service_providers[df_unique_service_providers['SubscriptionsUsed'].apply(
                    lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(','))
                )]    

            if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
                df_unique_service_providers = df_unique_service_providers[df_unique_service_providers['ResourceGroupsUsed'].apply(
                    lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(','))
                )]             

            if selected_providers and len(selected_providers) != 0 and "All" not in selected_providers:  
                df_unique_service_providers = df_unique_service_providers[df_unique_service_providers["Provider"].isin(selected_providers)]     

            if filtered_subscriptions and len(filtered_subscriptions) != 0 and "All" not in filtered_subscriptions:
                df_unique_service_providers = df_unique_service_providers[df_unique_service_providers['SubscriptionsUsed'].apply(
                    lambda x: any(subscription.strip() in filtered_subscriptions for subscription in x.split(','))
                )]   

            provider_options = [{"label": f"All Services", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_service_providers["ServiceName"].unique() if pd.notnull(v)]
        return provider_options      


    @app.callback(
        Output("azure-spending-heatmap-graph", "figure"),
        Input("azure-cost-filtered-query-store", "data"),
        Input("azure-spending-heatmap-top-n-slider", "value"),
        Input("spending-heatmap-subscription-dropdown", "value"),        
        Input("spending-heatmap-service-dropdown", "value"),
        Input("spending-heatmap-timescale-dropdown", "value"),
        Input("spending-heatmap-subscription-dropdown", "options"),        
        Input("spending-heatmap-service-dropdown", "options"),
    )
    def update_azure_cost_breakdown(selections, top_n, selected_subscriptions, selected_services, time_period, subscription_options, service_options):
        table_name = f"[azure_daily_cost_by_tenant_subscriptionname_resourcegroup_provider_servicename_resourcetype]"
        fields = "[UsageDay], [SubscriptionName], [ResourceGroup], [ServiceName]"
        select_clause = f"SELECT {fields}, SUM([TotalCostUSD]) as TotalCost FROM [consumable].{table_name}"
        group_by_clause = f"GROUP BY {fields}"

        where_clause = f"WHERE 1=1"        
        for k in selections.keys():
            if selections[k] and selections[k] != "All":
                match k:
                    case "UsageDay_From":
                        where_clause = f"{where_clause} AND [UsageDay] >= CAST('{selections[k]}' AS DATE)"
                    case "UsageDay_To":
                        where_clause = f"{where_clause} AND [UsageDay] <= CAST('{selections[k]}' AS DATE)"
                    case _:
                        where_clause = f"{where_clause} AND [{k}] IN ({selections[k]})"

        q_cost_aggregation = f"{select_clause} {where_clause} {group_by_clause}"

        queries = {
            "cost_aggregation": q_cost_aggregation
        }   

        results = run_queries(queries, len(queries.keys()))    

        filtered_df = results["cost_aggregation"]
        filtered_df = filtered_df.dropna(subset=['TotalCost'])
        filtered_df['TotalCost'] = pd.to_numeric(filtered_df['TotalCost'], errors='coerce')
        filtered_df['UsageDay'] = pd.to_datetime(filtered_df['UsageDay'], errors='coerce')        
        return get_spending_heatmap_figure(filtered_df, top_n, selected_subscriptions, selected_services, subscription_options, service_options, time_period)


