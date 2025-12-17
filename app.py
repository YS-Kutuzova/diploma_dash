import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from layouts import create_layout
from callbacks import setup_callbacks

def create_app():
  
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    
    app.title = "🏙️ Информационно-аналитическая система для оценки обеспеченности районов Санкт-Петербурга объектами спортивной инфраструктуры"
    app.layout = create_layout()

    setup_callbacks(app)
  

    return app


