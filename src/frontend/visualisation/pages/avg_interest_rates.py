import datetime

from dash import dcc
from dash import html
import plotly.graph_objects as go
from src.backend.data.fiscaldata_treasury_gov.avg_interest_rates import AvgInterestRates
from src.backend.data.fiscaldata_treasury_gov.summary_of_treasury_securities_outstanding import \
    SummaryOfTreasurySecuritiesOutstanding
from src.backend.data.home_treasury_gov.daily_treasury_yield_curve import DailyTreasuryYieldCurve

start_date = datetime.datetime(year=2001, month=1, day=1)
end_date = datetime.datetime.today()


def plot_outstanding():
    sec_desc = 'Bills'

    sotso = SummaryOfTreasurySecuritiesOutstanding()

    sotso_df = sotso.get_security_data_between_dates(start_date=start_date,
                                                     end_date=end_date,
                                                     security_desc='Bills')

    plot_list = list()

    plot_list.append(go.Scatter(x=sotso_df['date'],
                                y=sotso_df['total_mil_amt'],
                                line=dict(width=1),
                                name=f'Total Outstanding {sec_desc}'))

    fig = go.Figure(plot_list)

    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Total Outstanding ($)'
                      )
    return fig


def plot_avg_interest_rates():
    dtyc = DailyTreasuryYieldCurve()
    air = AvgInterestRates()

    dtyc_df = dtyc.get_all_data_between_dates(start_date=start_date,
                                              end_date=end_date)

    security_desc_list = ['Treasury Bills']
    plot_list = list()
    for security_desc in security_desc_list:
        air_df = air.get_security_data_between_dates(start_date=start_date,
                                                     end_date=end_date,
                                                     security_desc=security_desc)

        plot_list.append(go.Scatter(x=air_df['date'],
                                    y=air_df['avg_interest_rate_amt'] * 100,
                                    line=dict(width=1),
                                    name=security_desc))

    list_of_maturity = ['1 Mo', '2 Mo', '3 Mo', '6 Mo', '1 Yr']
    for maturity in list_of_maturity:
        plot_list.append(go.Scatter(x=dtyc_df['date'],
                                    y=dtyc_df[maturity],
                                    line=dict(width=1),
                                    name=maturity))

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

                            dcc.Graph(id='line_plot', figure=plot_avg_interest_rates()),
                            dcc.Graph(id='line_plot_outstanding', figure=plot_outstanding())

                            ]
                  )
