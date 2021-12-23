from typing import Dict, List, Tuple
from datetime import date, timedelta
from collections import namedtuple

from covid.components import Label, SquareDropdown
from covid.app import app

from tdash import TComponent, path_name, children, value, figure, Stat, TChart
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import pandas as pd


class StateDropdown(html.Div, TComponent):

    name: str = 'state-dropdown'
    State = namedtuple('State', ('name', 'abbr'))

    def __init__(self, **kwargs):
        self.label = 'State'

        self.states = [
            self.State('Australian Capital Territory', 'ACT'),
            self.State('Tasmania', 'TAS'),
            self.State('Victoria', 'VIC'),
            self.State('Western Australia', 'WA'),
            self.State('Northern Territory', 'NT'),
            self.State('Queensland', 'QLD'),
            self.State('New South Wales', 'NSW'),
        ]

        self.label = Label(id=self.build_children_id('label'), children='State')
        self.dropdown = SquareDropdown(
            id=self.build_children_id('select'),
            options=sorted(
                [{'label': state.name, 'value': state.abbr} for state in self.states],
                key=lambda x: x['label']
            ),
            style={'width': '300px'}
        )

        super().__init__(children=self.build_children(), **kwargs)

    def build_children(self):
        return [self.label, self.dropdown]


class DatePicker(html.Div, TComponent):

    name: str = 'date-picker'

    def __init__(self, **kwargs):
        self.id = self.build_id()
        self.label = Label(id=self.build_children_id('label'), children='Date')
        self.dropdown = dcc.DatePickerRange(
            id=self.build_children_id('select'),
            min_date_allowed=app.app_config.data.min_date,
            max_date_allowed=date.today(),
        )
        self.style = {'float': 'right', 'margin-right': '20%'}

        super().__init__(id=self.id, children=self.build_children(), **kwargs)

    def build_children(self):
        return [self.label, self.dropdown]


class Overview(html.Div, TComponent):

    name: str = 'overview'

    def __init__(self, **kwargs):
        self.id = self.build_id()
        self.url = dcc.Location(id=self.build_children_id('url'))
        self.dropdown = StateDropdown(id=self.build_children_id('state-dropdown'))
        self.date = DatePicker()

        self.n_cases = Stat(
            id=self.build_children_id('n-cases'),
            title='Total Number of Cases',
            subtitle='The total number of cases recorded in the last 90 days',
            color=app.app_config.colours.orange
        )
        self.n_deaths = Stat(
            id=self.build_children_id('n-deaths'),
            title='Total Number of Deaths',
            subtitle='The total number of deaths recorded in the last 90 days',
            color=app.app_config.colours.red
        )
        self.n_tests = Stat(
            id=self.build_children_id('n-tests'),
            title='Total Number of Tests',
            subtitle='The total number of tests administered in the last 90 days',
            color=app.app_config.colours.blue
        )
        self.n_positives = Stat(
            id=self.build_children_id('n-positives'),
            title='Total Number of Positive Tests',
            subtitle='The total number of positive test results reported in the last 90 days',
            color=app.app_config.colours.aqua
        )
        self.n_recovered = Stat(
            id=self.build_children_id('n-recovered'),
            title='Total Number of People Recovered',
            subtitle='The total number of people recovered in the last 90 days',
            color=app.app_config.colours.aqua
        )

        self.time_series = TChart(
            id=self.build_children_id('time-series'),
            title='Number of cases over time, per state',
            subtitle='This shows the number of cases that have been reported over time. You can '
                     'highlight areas to drill in to, or optionally select specific dates from the '
                     'filter above. You can also remove states from the chart by clicking them in'
                     'the legend. Double click a state to isolate it.'
        )

        self.vaccs_vs_hosps = TChart(
            id=self.build_children_id('vaccs-vs-hosps'),
            title='The number of Vaccinations vs the Number of Hospitalisations'
        )

        self.children = self.build_children()

        super().__init__(id=self.id, children=self.children, **kwargs)

    def build_children(self):
        return dbc.Col([
            self.url,
            dbc.Row([dbc.Col(self.dropdown), dbc.Col(self.date)]),
            dbc.Row(
                children=[
                    dbc.Col(self.n_cases),
                    dbc.Col(self.n_deaths),
                    dbc.Col(self.n_tests),
                    dbc.Col(self.n_positives),
                    dbc.Col(self.n_recovered)
                ],
                className="g-0"
            ),
            html.Br(),
            dbc.Row([
                dbc.Col(self.time_series, width=6),
                dbc.Col(self.vaccs_vs_hosps, width=6),
            ])
        ])


class Aggregations(pd.DataFrame):
    @property
    def calculated_fields(self):
        return list(self.column_sums)

    @property
    def last_90_days(self) -> Tuple[date, date]:
        _today = date.today()
        return _today - timedelta(days=90), _today

    @property
    def column_sums(self) -> Dict:
        return {
            'deaths': 'sum',
            'confirmed': 'sum',
            'tests': 'sum',
            'positives': 'sum',
            'recovered': 'sum',
            'hosp': 'sum',
            'vaccines': 'sum'
        }

    def counts_by_state(self, state: str = None) -> pd.DataFrame:
        _temp = self[(self.state_abbrev == state)] if state else self
        return (
            _temp
            .agg(self.column_sums)
        )

    def time_series_by_state(self, state: str = None) -> Tuple[pd.DataFrame, List[str]]:
        _temp = self[(self.state_abbrev == state)] if state else self
        _data = _temp.groupby(['date', 'state_abbrev']).agg(self.column_sums).reset_index()
        _states = list(_temp.state_abbrev.unique())
        return _data, _states

    def time_series_overall(self, state: str = None) -> pd.DataFrame:
        _temp = self[(self.state_abbrev == state)] if state else self
        _data = _temp.groupby(['date']).agg(self.column_sums).reset_index()
        return _data


overview = Overview()


@app.callback(
    [
        Output(overview.n_cases.value.id, children),
        Output(overview.n_deaths.value.id, children),
        Output(overview.n_tests.value.id, children),
        Output(overview.n_positives.value.id, children),
        Output(overview.n_recovered.value.id, children)
    ],
    [
        Input(overview.url.id, path_name),
        Input(overview.dropdown.dropdown.id, value)
    ],
    prevent_initial_call=False
)
def get_n_deaths_info(_: str, state: str):
    df = Aggregations(app.app_config.data.data)
    counts = df.counts_by_state(state)
    return (
        f'{counts.confirmed:,.0f}',
        f'{counts.deaths:,.0f}',
        f'{counts.tests:,.0f}',
        f'{counts.positives:,.0f}',
        f'{counts.recovered:,.0f}',
    )


@app.callback(
    Output(overview.time_series.graph.id, figure),
    [
        Input(overview.url.id, path_name),
        Input(overview.dropdown.dropdown.id, value)
    ],
    prevent_initial_call=False
)
def make_time_series_chart(_: str, state: str):
    df = Aggregations(app.app_config.data.data)
    time_series, states = df.time_series_by_state(state)
    fig = go.Figure()
    for state in states:
        _state_data = time_series[time_series.state_abbrev == state]
        fig.add_trace(
            go.Scatter(
                x=_state_data.date,
                y=_state_data.confirmed,
                mode='lines',
                name=state
            )
        )
    fig.update_layout(template='plotly_white')
    return fig


@app.callback(
    Output(overview.vaccs_vs_hosps.graph.id, figure),
    [
        Input(overview.url.id, path_name),
        Input(overview.dropdown.dropdown.id, value)
    ],
    prevent_initial_call=False
)
def make_time_series_chart(_: str, state: str):
    df = Aggregations(app.app_config.data.data)
    time_series = df.time_series_overall(state)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=time_series.date,
            y=time_series.vaccines,
            mode='lines',
            name='Vaccinations'
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=time_series.date,
            y=time_series.hosp,
            mode='lines',
            name='Hospitalisations'
        ),
        secondary_y=True
    )
    fig.update_layout(template='plotly_white')
    return fig
