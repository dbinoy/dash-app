from dash.dependencies import Input, Output, State
import pandas as pd
from src.utils.db import run_queries
from src.components.azure_cost_components.azure_cost_data_table_view import get_data_table_data

def register_callbacks(app):
    @app.callback(
        Output("azure-cost-data-table", "data"),
        Input("azure-cost-filtered-query-store", "data")
    )
    def update_data_table(selections):

        q_azure_cost_data = 'SELECT [UsageDay], [SubscriptionName], [ResourceGroup], [Provider], [ServiceName], [ReservationId], [ResourceType], SUM([TotalCostUSD]) as TotalCost ' \
        'FROM consumable.d_cost_by_tenant_sub_rg_provider_service_reservation_type_app_costcenter_product_project '

        filtered_query = "WHERE 1=1 "
        for k in selections.keys():
            if selections[k] and selections[k] != "All":
                match k:
                    case "UsageDay_From":
                        filtered_query += f"AND [UsageDay] >= CAST('{selections[k]}' AS DATE) "
                    case "UsageDay_To":
                        filtered_query += f"AND [UsageDay] <= CAST('{selections[k]}' AS DATE) "
                    case _:
                        if 'Unspecified' not in selections[k]:
                            filtered_query += f"AND [{k}] IN ({selections[k]}) "
                        else:
                            filtered_query += f"AND [{k}] IS NULL "
                            remaining_selections = selections[k].replace("'Unspecified',", ",").replace(", 'Unspecified'", ",").replace("'Unspecified'", "")
                            if len(remaining_selections) > 0 :
                                filtered_query += f"AND [{k}] IN ({remaining_selections}) "                      

        filtered_query += 'GROUP BY [SubscriptionName], [ResourceGroup], [Provider], [ServiceName], [ReservationId], [ResourceType], [UsageDay] '

        # Add ordering to the query
        filtered_query += 'ORDER BY [UsageDay], [SubscriptionName], [ResourceGroup], [Provider], [ServiceName], [ReservationId], [ResourceType] '

        # Limit to 10000 rows
        filtered_query += 'OFFSET 0 ROWS FETCH NEXT 10000 ROWS ONLY'

        q_azure_cost_data = q_azure_cost_data + filtered_query
 
        queries = {
            "azure_cost_data": q_azure_cost_data
        }

        results = run_queries(queries, len(queries.keys()))
        df = results["azure_cost_data"]
        return get_data_table_data(df)    