from dash import html
from tdash import TComponent


class Page404(html.Div, TComponent):
    name: str = '404'

    def __init__(self, **kwargs):
        self.id = self.build_id()

        super().__init__(id=self.id, children=self.build_children(), **kwargs)

    def build_children(self):
        return html.H1('404! Page Doesn\'t exist')
