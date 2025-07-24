import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from src.utils.cache import cache
from src.components.layout import create_layout
from src.components.azure_cost_layout import azure_cost_layout
from src.components.welcome_layout import welcome_layout
from src.callbacks import register_all_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Analytics Dashboard"
app.config.suppress_callback_exceptions = True
server = app.server
cache.init_app(server)

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("App Usage Telemetry", href="/app-usage", className="nav-link")),
        dbc.NavItem(dbc.NavLink("Azure Cost & Usage", href="/azure-cost", className="nav-link")),
    ],
    brand="Analytics Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    class_name="mb-4"
)

#Multi-pag layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', className='container')
])

#Routing callback
@app.callback(
    dash.Output('page-content', 'children'),
    dash.Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/app-usage':
        return create_layout()
    elif pathname == '/azure-cost':
        return azure_cost_layout()
    else:
        return welcome_layout()
# app.layout = create_layout()
register_all_callbacks(app) 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True)