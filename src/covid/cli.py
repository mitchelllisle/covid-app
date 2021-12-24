from covid.app import app, Content, Url
from covid.overview import overview
from covid.missing import Page404

from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
from tdash import children, path_name, Nav, NavLink

url = Url()
nav = Nav(links=[NavLink('Overview', '/'), NavLink('About', '/about')])

content = Content()

missing = Page404()


app.layout = dbc.Container(
    id='container',
    fluid=True,
    children=[url, nav, content],
    style={'padding': '0px'}
)


@app.callback(
    Output(component_id=content.id, component_property=children),
    Input(component_id=url.id, component_property=path_name)
)
def display_page(page: str):
    routes = {
        '/': overview
    }
    try:
        return routes[page]
    except KeyError:
        return missing


def main():
    app.run_server(debug=True, host='0.0.0.0')
