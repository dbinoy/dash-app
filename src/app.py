import dash
import dash_bootstrap_components as dbc
from src.components.layout import create_layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "User Login Telemetry Dashboard"
server = app.server

app.layout = create_layout()

if __name__ == "__main__":
    from src.callbacks import register_all_callbacks
    register_all_callbacks(app)    
    app.run(host='0.0.0.0', port=8050, debug=True)