import datetime

from dash import dcc
from dash import html
import plotly.graph_objects as go
from src.backend.data.fiscaldata_treasury_gov.avg_interest_rates import AvgInterestRates


def plot_avg_interest_rates():
    avg_interest_rates = AvgInterestRates()

    start_date = avg_interest_rates.create_date(year=1990, month=1, day=1)
    end_date = datetime.datetime.today()

    security_desc_list = ['Treasury Bills', 'Treasury Notes', 'Treasury Bonds']
    plot_list = list()
    for security_desc in security_desc_list:
        df = avg_interest_rates.get_security_data_between_dates(start_date=start_date,
                                                                end_date=end_date,
                                                                security_desc=security_desc)

        plot_list.append(go.Scatter(x=df['record_date'],
                                    y=df['avg_interest_rate_amt'] * 100,
                                    line=dict(width=1),
                                    name=security_desc))

    fig = go.Figure(plot_list)

    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Avg Interest Rate (%)'
                      )
    return fig


# Define the page layout
layout = html.Div(id='parent',
                  children=[html.H1(id='H1',
                                    children='Average Interest Rates',
                                    style={'textAlign': 'center',
                                           'marginTop': 40,
                                           'marginBottom': 40,
                                           'marginRight': 40,
                                           'marginLeft': 40,
                                           }),

                            dcc.Graph(id='line_plot', figure=plot_avg_interest_rates())

                            ]
                  )
