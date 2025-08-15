from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries

def register_azure_cost_filter_callbacks(app):
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
        q_unique_reservations = 'SELECT [ReservationId], [ResourceGroupsUsed], [SubscriptionsUsed] FROM [consumable].[azure_reservations]'
        q_unique_app_tags = 'SELECT COALESCE([App], \'\') AS App, COALESCE([SubscriptionUsed], \'\') AS SubscriptionUsed, COALESCE([ResourceGroupUsed], \'\') AS ResourceGroupUsed FROM [consumable].[azure_tag_usages_App]'
        q_unique_costcenter_tags = 'SELECT COALESCE([CostCenter], \'\') AS CostCenter, COALESCE([SubscriptionUsed], \'\') AS SubscriptionUsed, COALESCE([ResourceGroupUsed], \'\') AS ResourceGroupUsed FROM [consumable].[azure_tag_usages_CostCenter]'
        q_unique_product_tags = 'SELECT COALESCE([Product], \'\') AS Product, COALESCE([SubscriptionUsed], \'\') AS SubscriptionUsed, COALESCE([ResourceGroupUsed], \'\') AS ResourceGroupUsed FROM [consumable].[azure_tag_usages_Product]'
        q_unique_project_tags = 'SELECT COALESCE([Project], \'\') AS Project, COALESCE([SubscriptionUsed], \'\') AS SubscriptionUsed, COALESCE([ResourceGroupUsed], \'\') AS ResourceGroupUsed FROM [consumable].[azure_tag_usages_Project]'
        queries = {
            "earliest_and_latest_dates": q_earliest_and_latest_dates,
            "unique_tenants": q_unique_tenants,
            "unique_subscriptions": q_unique_subscriptions,
            "unique_service_providers": q_unique_service_providers,
            "unique_resource_types": q_unique_resource_types,
            "unique_reservations": q_unique_reservations,
            "unique_app_tags": q_unique_app_tags,
            "unique_costcenter_tags": q_unique_costcenter_tags,
            "unique_product_tags": q_unique_product_tags,
            "unique_project_tags": q_unique_project_tags
        }    
        results = run_queries(queries, len(queries.keys()))
        filter_data = {
            "earliest_and_latest_dates": results["earliest_and_latest_dates"].to_dict("records"),
            "unique_tenants": results["unique_tenants"].to_dict("records"),
            "unique_subscriptions": results["unique_subscriptions"].to_dict("records"),
            "unique_service_providers": results["unique_service_providers"].to_dict("records"),
            "unique_resource_types": results["unique_resource_types"].to_dict("records"),
            "unique_reservations": results["unique_reservations"].to_dict("records"),
            "unique_app_tags": results["unique_app_tags"].to_dict("records"),
            "unique_costcenter_tags": results["unique_costcenter_tags"].to_dict("records"),
            "unique_product_tags": results["unique_product_tags"].to_dict("records"),
            "unique_project_tags": results["unique_project_tags"].to_dict("records")
        }
        unique_subscriptions = pd.DataFrame(filter_data["unique_subscriptions"])['SubscriptionName'].tolist()
        queries = {}
        for subscription in unique_subscriptions:
            if subscription is not None:
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
        prevent_initial_call=False
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
            if subscription is not None:
                if (not selected_subscriptions) or ("All" in selected_subscriptions) or (subscription in selected_subscriptions):
                    df_unique_resourcegroups = pd.DataFrame(filter_data[f"unique_resourcegroups_{subscription.replace('-', '_')}"])
                    unique_resourcegroups.extend(df_unique_resourcegroups["ResourceGroup"].tolist())
        filtered_resourcegroup = sorted([s for s in unique_resourcegroups if s and len(s.strip()) > 0])


        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            selected_subscriptions = ' ' + ','.join(selected_subscriptions) + ' '
        else:
            selected_subscriptions = ' '

        resourcegroup_options = [{"label": f"All{selected_subscriptions}Resource Groups", "value": "All"}]

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

        provider_options = [{"label": f"All Service Names", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_service_providers["ServiceName"].unique() if pd.notnull(v)]
        return provider_options    

    @app.callback(
        Output("reservation-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_reservation_filter(selected_subscriptions, selected_resourcegroups, filter_data):
        if not filter_data:
            return []
        
        df_unique_reservations = pd.DataFrame(filter_data["unique_reservations"])   

        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            df_unique_reservations = df_unique_reservations[df_unique_reservations['SubscriptionsUsed'].apply(
                lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(','))
            )]    

        if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
            df_unique_reservations = df_unique_reservations[df_unique_reservations['ResourceGroupsUsed'].apply(
                lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(','))
            )]              

        reservation_options = [{"label": f"All Reservation Id", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_reservations["ReservationId"].unique() if pd.notnull(v)]
        return reservation_options
    
    @app.callback(
        Output("resourcetype-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("provider-dropdown", "value"),
        Input("service-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_resourcetype_filter(selected_subscriptions, selected_resourcegroups, selected_providers, selected_services, filter_data):
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

        if selected_services and len(selected_services) != 0 and "All" not in selected_services:
            df_unique_service_providers = df_unique_service_providers[df_unique_service_providers["ServiceName"].isin(selected_services)]  

        df_unique_resource_types = pd.DataFrame(filter_data["unique_resource_types"])
        df_unique_resource_types = df_unique_resource_types[df_unique_resource_types["ServiceUsed"].apply(
            lambda x: any(service.strip() in df_unique_service_providers['ServiceName'].tolist() for service in x.split(','))
        )] 
        df_unique_resource_types = df_unique_resource_types[df_unique_resource_types["ProviderUsed"].apply(
            lambda x: any(provider.strip() in df_unique_service_providers['Provider'].tolist() for provider in x.split(','))
        )]
        resourcetype_options = [{"label": f"All Resource Types", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_resource_types["ResourceType"].unique() if pd.notnull(v)]
        return resourcetype_options    
    
    @app.callback(
        Output("app-tag-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_app_tag_filter(selected_subscriptions, selected_resourcegroups, filter_data):
        if not filter_data:
            return []
        
        df_unique_app_tags = pd.DataFrame(filter_data["unique_app_tags"])   
        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            df_unique_app_tags = df_unique_app_tags[df_unique_app_tags['SubscriptionUsed'].apply(
                lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(',') if x is not None)
            )]    

        if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
            df_unique_app_tags = df_unique_app_tags[df_unique_app_tags['ResourceGroupUsed'].apply(
                lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(',') if x is not None)
            )]             

        tag_options = [{"label": f"All Apps", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_app_tags["App"].unique() if pd.notnull(v)]
        return tag_options
    
    @app.callback(
        Output("costcenter-tag-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_costcenter_tag_filter(selected_subscriptions, selected_resourcegroups, filter_data):
        if not filter_data:
            return []
        
        df_unique_costcenter_tags = pd.DataFrame(filter_data["unique_costcenter_tags"])   
        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            df_unique_costcenter_tags = df_unique_costcenter_tags[df_unique_costcenter_tags['SubscriptionUsed'].apply(
                lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(',') if x is not None)
            )]    

        if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
            df_unique_costcenter_tags = df_unique_costcenter_tags[df_unique_costcenter_tags['ResourceGroupUsed'].apply(
                lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(',') if x is not None)
            )]             

        tag_options = [{"label": f"All Cost Centers", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_costcenter_tags["CostCenter"].unique() if pd.notnull(v)]
        return tag_options    
        
    @app.callback(
        Output("product-tag-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_product_tag_filter(selected_subscriptions, selected_resourcegroups, filter_data):
        if not filter_data:
            return []
        
        df_unique_product_tags = pd.DataFrame(filter_data["unique_product_tags"])   
        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            df_unique_product_tags = df_unique_product_tags[df_unique_product_tags['SubscriptionUsed'].apply(
                lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(',') if x is not None)
            )]    

        if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
            df_unique_product_tags = df_unique_product_tags[df_unique_product_tags['ResourceGroupUsed'].apply(
                lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(',') if x is not None)
            )]             

        tag_options = [{"label": f"All Products", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_product_tags["Product"].unique() if pd.notnull(v)]
        return tag_options           
    
    @app.callback(
        Output("project-tag-dropdown", "options"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("azure-cost-filter-data-store", "data"),    
        prevent_initial_call=True
    )
    def populate_project_tag_filter(selected_subscriptions, selected_resourcegroups, filter_data):
        if not filter_data:
            return []
        
        df_unique_project_tags = pd.DataFrame(filter_data["unique_project_tags"])   
        if selected_subscriptions and len(selected_subscriptions) != 0 and "All" not in selected_subscriptions:
            df_unique_project_tags = df_unique_project_tags[df_unique_project_tags['SubscriptionUsed'].apply(
                lambda x: any(subscription.strip() in selected_subscriptions for subscription in x.split(',') if x is not None)
            )]    

        if selected_resourcegroups and len(selected_resourcegroups) != 0 and "All" not in selected_resourcegroups:
            df_unique_project_tags = df_unique_project_tags[df_unique_project_tags['ResourceGroupUsed'].apply(
                lambda x: any(resource.strip() in selected_resourcegroups for resource in x.split(',') if x is not None)
            )]             

        tag_options = [{"label": f"All Projects", "value": "All"}]+[{"label": str(v), "value": v} for v in df_unique_project_tags["Project"].unique() if pd.notnull(v)]
        return tag_options       

    
    @app.callback(
        Output("azure-cost-date-range-picker", "start_date", allow_duplicate=True),
        Output("azure-cost-date-range-picker", "end_date", allow_duplicate=True),
        Output("tenant-dropdown", "value", allow_duplicate=True),
        Output("subscription-dropdown", "value", allow_duplicate=True),
        Output("resourcegroup-dropdown", "value", allow_duplicate=True),
        Output("provider-dropdown", "value", allow_duplicate=True),
        Output("service-dropdown", "value", allow_duplicate=True),
        Output("reservation-dropdown", "value", allow_duplicate=True),
        Output("resourcetype-dropdown", "value", allow_duplicate=True),
        Output("app-tag-dropdown", "value", allow_duplicate=True),
        Output("costcenter-tag-dropdown", "value", allow_duplicate=True),
        Output("product-tag-dropdown", "value", allow_duplicate=True),
        Output("project-tag-dropdown", "value", allow_duplicate=True),
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
        reservation_default = []
        resourcetype_default = []
        app_tag_default = []
        costcenter_tag_default = []
        product_tag_default = []
        project_tag_default = []
        if not filter_data:
            date_start_default = ""
            date_end_default = ""
        else:
            df_earliest_and_latest_dates = pd.DataFrame(filter_data["earliest_and_latest_dates"])        
            date_start_default = df_earliest_and_latest_dates["EarliestDay"][0]
            date_end_default = df_earliest_and_latest_dates["LatestDay"][0]
        return date_start_default, date_end_default, tenant_default, subscription_default, resourcegroup_default, provider_default, service_default, reservation_default, resourcetype_default, app_tag_default, costcenter_tag_default, product_tag_default, project_tag_default
    
    @app.callback(
        Output("azure-cost-filtered-query-store", "data"), 
        Input("azure-cost-filter-data-store", "data"), 
        Input("azure-cost-date-range-picker", "start_date"),
        Input("azure-cost-date-range-picker", "end_date"),    
        Input("tenant-dropdown", "value"),
        Input("subscription-dropdown", "value"),
        Input("resourcegroup-dropdown", "value"),
        Input("provider-dropdown", "value"),    
        Input("service-dropdown", "value"),
        Input("reservation-dropdown", "value"),
        Input("resourcetype-dropdown", "value"),
        prevent_initial_call=True
    )
    def filter_data_query(filter_data, start_date, end_date, selected_tenants, selected_subscriptions, selected_resourcegroups, selected_providers, selected_services, selected_reservations, selected_resourcetypes):
        df_earliest_and_latest_dates = pd.DataFrame(filter_data["earliest_and_latest_dates"])
        start_placeholder = df_earliest_and_latest_dates["EarliestDay"][0]
        end_placeholder = df_earliest_and_latest_dates["LatestDay"][0]        
        selections = {
            "UsageDay_From": start_date if start_date is not None else start_placeholder,
            "UsageDay_To": end_date if end_date is not None else end_placeholder,
            "Tenant": ", ".join(["'"+tenant+"'" for tenant in selected_tenants]) if selected_tenants and len(selected_tenants) > 0 and "All" not in selected_tenants else "",
            "SubscriptionName": ", ".join(["'"+subscription+"'" for subscription in selected_subscriptions]) if selected_subscriptions and len(selected_subscriptions) > 0 and "All" not in selected_subscriptions else "",
            "ResourceGroup": ", ".join(["'"+resourcegroup+"'" for resourcegroup in selected_resourcegroups]) if selected_resourcegroups and len(selected_resourcegroups) > 0 and "All" not in selected_resourcegroups else "",
            "Provider": ", ".join(["'"+provider+"'" for provider in selected_providers]) if selected_providers and len(selected_providers) > 0 and "All" not in selected_providers else "",
            "ServiceName": ", ".join(["'"+service+"'" for service in selected_services]) if selected_services and len(selected_services) > 0 and "All" not in selected_services else "",
            "ReservationId": ", ".join(["'"+reservation+"'" for reservation in selected_reservations]) if selected_reservations and len(selected_reservations) > 0 and "All" not in selected_reservations else "",
            "ResourceType": ", ".join(["'"+resourcetype+"'" for resourcetype in selected_resourcetypes]) if selected_resourcetypes and len(selected_resourcetypes) > 0 and "All" not in selected_resourcetypes else ""
        }
        return selections
    
    @app.callback(
        Output("azure-cost-table-data-store", "data"),  
        Input("azure-cost-filtered-query-store", "data"), 
        prevent_initial_call=True
    )
    def fetch_table_data(selections):
        table_name = f"[d_cost_by_tenant_sub_rg_provider_service_reservation_type_app_costcenter_product_project]"
        fields = "[UsageDay], [SubscriptionName], [ResourceGroup], [ServiceName], [ReservationId]"
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

        q_table_data_query = f"{select_clause} {where_clause} {group_by_clause}"
        queries = {
            "table_data": q_table_data_query
        }   
        results = run_queries(queries, len(queries.keys()))    
        table_data = {
            "table_data": results["table_data"].to_dict("records")
        }

        return table_data