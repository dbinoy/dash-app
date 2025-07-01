import dash
import dash_bootstrap_components as dbc
from src.utils.cache import cache
from src.components.layout import create_layout
from src.callbacks import register_all_callbacks

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "User Login Telemetry Dashboard"
server = app.server
cache.init_app(server)
app.layout = create_layout()
register_all_callbacks(app) 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True)