import dash
from dash import dcc
import dash_bootstrap_components as dbc
from tdash import TComponent

from covid.config import Config


class Content(dbc.Col, TComponent):
    name: str = 'content'

    def __init__(self, **kwargs):
        self.id = self.build_id('page')
        self.style = {
            'padding-left': '10px',
            'padding-right': '10px'
        }
        super().__init__(id=self.id, **kwargs)


class Url(dcc.Location, TComponent):
    name: str = 'url'

    def __init__(self, **kwargs):
        self.id = self.build_id('location')
        super().__init__(id=self.id, **kwargs)


class CovidApp(dash.Dash):
    def __init__(self, **kwargs):
        self.app_config = Config()
        super().__init__(**kwargs)


app = CovidApp(
    name='covid-app-client',
    external_stylesheets=[dbc.themes.COSMO],
    prevent_initial_callbacks=True,
    update_title=None,
    suppress_callback_exceptions=True
)
