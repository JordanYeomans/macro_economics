import datetime

from dash import dcc
from dash import html
import plotly.graph_objects as go
from src.backend.data.fiscaldata_treasury_gov.debt_to_the_penny import DebtToThePenny


def plot_debt_to_penny():

    start_date = datetime.datetime(year=1990, month=1, day=1)
    end_date = datetime.datetime.today()

    df = DebtToThePenny().get_all_data_between_dates(start_date=start_date, end_date=end_date)

    debt_type_list = ['debt_held_public_amt', 'intragov_hold_amt', 'tot_pub_debt_out_amt']
    plot_list = list()
    for debt_type in debt_type_list:
        plot = go.Scatter(x=df['date'],
                          y=df[debt_type],
                          line=dict(width=1),
                          name=debt_type)
        plot_list.append(plot)

    fig = go.Figure(plot_list)

    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Debt To Penny'
                      )
    return fig


# Define the page layout
layout = html.Div(id='parent',
                  children=[html.H1(id='H1',
                                    children='Debt To The Penny',
                                    style={'textAlign': 'center',
                                           'marginTop': 40,
                                           'marginBottom': 40,
                                           'marginRight': 40,
                                           'marginLeft': 40,
                                           }),

                            dcc.Graph(id='line_plot', figure=plot_debt_to_penny())

                            ]
                  )
