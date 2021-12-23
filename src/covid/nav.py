from covid.app import app
from tdash import TComponent
from dash import html
import dash_bootstrap_components as dbc


class Nav(dbc.Nav, TComponent):

    name: str = 'nav'

    def __init__(self, **kwargs):
        self.id = self.build_id()
        # this centers the items in the middle of the nav
        self._item_style = {
            'margin-top': 'auto',
            'margin-bottom': 'auto',
            'color': 'black'
        }

        self.logo = html.Div(
            id=self.build_children_id('logo'),
            children='👋',
            style={
                'margin-left': '20px',
                'margin-right': '10px',
                **self._item_style
            }
        )
        self.overview_link = self._add_link('Overview', '/')
        self.about_link = self._add_link('About', '/about')

        self.style = {
            'border-bottom': f'1px solid {app.app_config.colours.light_gray}',
            'height': '60px'
        }

        super().__init__(id=self.id, children=self.build_children(), **kwargs)

    def _add_link(self, text: str, path: str) -> dbc.NavLink:
        return dbc.NavLink(
            id=self.build_children_id(text.replace(' ', '-').lower(), 'link'),
            children=text,
            href=path,
            style=self._item_style
        )

    def build_children(self):
        return [self.logo, self.overview_link, self.about_link]
