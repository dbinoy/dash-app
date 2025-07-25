from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries

def register_azure_cost_callbacks(app):
    @app.callback(
        Output("azure-cost-filter-data-store", "data"),
        Input("azure-cost-filtered-query-store", "id"), 
        prevent_initial_call=False
    )
    def load_filter_data(_):
        q_earliest_and_latest_dates = 'SELECT [EarliestDay], [LatestDay]  FROM [consumable].[azure_earliest_and_latest_dates]'
        q_unique_tenants ='SELECT DISTINCT([Tenant]) FROM [consumable].[azure_subscriptions] ORDER BY [Tenant]'
        q_unique_subscriptions = 'SELECT [Tenant], [SubscriptionName] FROM [consumable].[azure_subscriptions] ORDER BY [SubscriptionName]'
        q_unique_service_providers = 'SELECT [Provider], [ServiceName], [ResourceGroupsUsed], [SubscriptionsUsed] FROM [consumable].[azure_service_providers] ORDER BY [Provider], [ServiceName]'
        q_unique_resource_types = 'SELECT [ResourceType], [ServiceUsed], [ProviderUsed] FROM [consumable].[azure_resource_types]'

        queries = {
            "earliest_and_latest_dates": q_earliest_and_latest_dates,
            "unique_tenants": q_unique_tenants,
            "unique_subscriptions": q_unique_subscriptions,
            "unique_service_providers": q_unique_service_providers,
            "unique_resource_types": q_unique_resource_types
        }    
        results = run_queries(queries, len(queries.keys()))
        filter_data = {
            "earliest_and_latest_dates": results["earliest_and_latest_dates"].to_dict("records"),
            "unique_tenants": results["unique_tenants"].to_dict("records"),
            "unique_subscriptions": results["unique_subscriptions"].to_dict("records"),
            "unique_service_providers": results["unique_service_providers"].to_dict("records"),
            "unique_resource_types": results["unique_resource_types"].to_dict("records")
        }
        
        unique_subscriptions = pd.DataFrame(filter_data["unique_subscriptions"])['SubscriptionName'].tolist()
        queries = {}
        for subscription in unique_subscriptions:
            queries[f"unique_resourcegroups_{subscription.replace('-', '_')}"] = f'SELECT [SubscriptionName], [ResourceGroup] FROM [consumable].[azure_resourcegroups_{subscription.replace('-', '_')}]ORDER BY [ResourceGroup]'   
        results = run_queries(queries, len(queries.keys()))
        for key in results.keys():
            filter_data[key] = results[key].to_dict("records")
        return filter_data
    
    @app.callback(
        Output("azure-cost-date-range-picker", "start_date_placeholder_text"),
        Output("azure-cost-date-range-picker", "end_date_placeholder_text"),
        Output("tenant-dropdown", "options"),
        Input("azure-cost-filter-data-store", "data"),
        prevent_initial_call=True
    )
    def populate_date_and_tenant_filter(filter_data):
        if not filter_data:
            return "", "", []
        df_earliest_and_latest_dates = pd.DataFrame(filter_data["earliest_and_latest_dates"])
        df_unique_tenants = pd.DataFrame(filter_data["unique_tenants"])
        start_placeholder = df_earliest_and_latest_dates["EarliestDay"][0]
        end_placeholder = df_earliest_and_latest_dates["LatestDay"][0]
        tenant_options = [{"label": "All Tenants", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_tenants["Tenant"] if pd.notnull(v)]

        return str(start_placeholder), str(end_placeholder), tenant_options
    
    @app.callback(
        Output("subscription-dropdown", "options"),
        Input("tenant-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_subscription_filter(selected_tenants, filter_data):
        if not filter_data:
            return []
        df_unique_subscriptions = pd.DataFrame(filter_data["unique_subscriptions"])  
        if selected_tenants and len(selected_tenants) != 0 and "All" not in selected_tenants:
            df_unique_subscriptions = df_unique_subscriptions[df_unique_subscriptions["Tenant"].isin(selected_tenants)]
            selected_tenants = ' ' + ','.join(selected_tenants) + ' '
        else:
            selected_tenants = ' '
        subscription_options = [{"label": f"All{selected_tenants}Subscriptions", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_subscriptions["SubscriptionName"] if pd.notnull(v)]
        return subscription_options
    
    @app.callback(
        Output("resourcegroup-dropdown", "options"),
        Input("tenant-dropdown", "value"),
        Input("subscription-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_resourcegroup_filter(selected_tenants, selected_subscriptions, filter_data):
        if not filter_data:
            return []
        unique_resourcegroups = []
        
        df_unique_subscriptions = pd.DataFrame(filter_data["unique_subscriptions"])  
        if selected_tenants and len(selected_tenants) != 0 and "All" not in selected_tenants:
            df_unique_subscriptions = df_unique_subscriptions[df_unique_subscriptions["Tenant"].isin(selected_tenants)]

        unique_subscriptions = df_unique_subscriptions['SubscriptionName'].tolist()
        for subscription in unique_subscriptions:
            if (not selected_subscriptions) or ("All" in selected_subscriptions) or (subscription in selected_subscriptions):
                df_unique_resourcegroups = pd.DataFrame(filter_data[f"unique_resourcegroups_{subscription.replace('-', '_')}"])
                unique_resourcegroups.extend(df_unique_resourcegroups["ResourceGroup"].tolist())
        filtered_resourcegroup = sorted([s for s in unique_resourcegroups if s and len(s.strip()) > 0])


        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            selected_subscriptions = ' ' + ','.join(selected_subscriptions) + ' '
        else:
            selected_subscriptions = ' '

        resourcegroup_options = [{"label": f"All{selected_subscriptions}ResourceGroups", "value": "All"}]

        if len(filtered_resourcegroup) < len(unique_resourcegroups):
            resourcegroup_options = resourcegroup_options + [{"label":"Blank", "value":""}]

        resourcegroup_options = resourcegroup_options+[{"label": v, "value": v} for v in filtered_resourcegroup if len(filtered_resourcegroup) > 0]
        return resourcegroup_options

    @app.callback(
        Output("provider-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_provider_filter(selected_subscriptions, selected_resourcegroups, filter_data):
        if not filter_data:
            return []
        
        df_unique_service_providers = pd.DataFrame(filter_data["unique_service_providers"])   

        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            df_unique_service_providers = df_unique_service_providers[df_unique_service_providers['SubscriptionsUsed'].apply(
                lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(','))
            )]    

        if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
            df_unique_service_providers = df_unique_service_providers[df_unique_service_providers['ResourceGroupsUsed'].apply(
                lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(','))
            )]             

        provider_options = [{"label": f"All Providers", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_service_providers["Provider"].unique() if pd.notnull(v)]
        return provider_options
    
    @app.callback(
        Output("service-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("provider-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_service_filter(selected_subscriptions, selected_resourcegroups, selected_providers, filter_data):
        if not filter_data:
            return []
        
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

        provider_options = [{"label": f"All Services", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_service_providers["ServiceName"].unique() if pd.notnull(v)]
        return provider_options    

    @app.callback(
        Output("azure-cost-date-range-picker", "start_date", allow_duplicate=True),
        Output("azure-cost-date-range-picker", "end_date", allow_duplicate=True),
        Output("tenant-dropdown", "value", allow_duplicate=True),
        Output("subscription-dropdown", "value", allow_duplicate=True),
        Output("resourcegroup-dropdown", "value", allow_duplicate=True),
        Output("provider-dropdown", "value", allow_duplicate=True),
        Output("service-dropdown", "value", allow_duplicate=True),
        Input("azure-cost-clear-filters-btn", "n_clicks"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def clear_all_filters(n_clicks, filter_data):
        tenant_default = []
        subscription_default = []
        resourcegroup_default = []
        provider_default = []
        service_default = []
        if not filter_data:
            date_start_default = ""
            date_end_default = ""
        else:
            df_earliest_and_latest_dates = pd.DataFrame(filter_data["earliest_and_latest_dates"])        
            date_start_default = df_earliest_and_latest_dates["EarliestDay"][0]
            date_end_default = df_earliest_and_latest_dates["LatestDay"][0]
        return date_start_default, date_end_default, tenant_default, subscription_default, resourcegroup_default, provider_default, service_default