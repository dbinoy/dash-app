import dash
from dash import Output, Input, State, dcc, html, callback_context
import dash_bootstrap_components as dbc

def register_callbacks(app):
    @app.callback(
        Output("chart-modal", "is_open"),
        Output("modal-chart-content", "children"),
        Input("azure-spending-trends-graph-container", "n_clicks"),
        Input("azure-top-cost-drivers-graph-container", "n_clicks"),
        Input("azure-total-spending-breakdown-graph-container", "n_clicks"),
        Input("azure-spending-heatmap-graph-container", "n_clicks"),
        Input("close-chart-modal", "n_clicks"),
        State("chart-modal", "is_open"),
        prevent_initial_call=True
    )
    def display_modal(trends_click, drivers_click, breakdown_click, heatmap_click, close_click, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return is_open, dash.no_update
        trigger = ctx.triggered[0]["prop_id"].split(".")[0]
        print(f"Triggered by: {trigger}")

        if trigger == "close-chart-modal":
            return False, dash.no_update

        # You can replace the content below with the actual chart figures
        if trigger == "azure-spending-trends-graph-container":
            return True, html.Div([
                dcc.Graph(id="azure-spending-trends-graph", style={"height": "80vh", "width": "90vw"})
            ], style={"padding": "0"})
        elif trigger == "azure-top-cost-drivers-graph-container":
            return True, html.Div([
                dcc.Graph(id="azure-top-cost-drivers-graph", style={"height": "80vh", "width": "90vw"})
            ], style={"padding": "0"})
        elif trigger == "azure-total-spending-breakdown-graph-container":
            return True, html.Div([
                dcc.Graph(id="azure-total-spending-breakdown-graph", style={"height": "80vh", "width": "90vw"})
            ], style={"padding": "0"})
        elif trigger == "azure-spending-heatmap-graph-container":
            return True, html.Div([
                dcc.Graph(id="azure-spending-heatmap-graph", style={"height": "80vh", "width": "90vw"})
            ], style={"padding": "0"})
        return is_open, dash.no_update