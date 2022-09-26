from dash import dcc
from dash import html
import plotly.graph_objects as go
from src.backend.data.home_treasury_gov.daily_treasury_yield_curve import DailyTreasuryYieldCurve


def plot_yield_curve():
    dtyc = DailyTreasuryYieldCurve()

    years = [2020, 2021, 2022]
    months = [3, 6, 9, 12]

    dates = list()
    for y in years:
        for m in months:
            dates.append(dtyc.create_date(year=y, month=m, day=1))

    plot_list = list()
    for date in dates:
        yc_data = dtyc.get_yield_curve_for_date(date=date)

        if yc_data is not None:
            plot_list.append(go.Scatter(x=yc_data['Days'],
                                        y=yc_data['Yield (%)'],
                                        line=dict(width=1),
                                        name=date.strftime('%d/%m/%Y')))

    fig = go.Figure(plot_list)

    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Yield (%)',
                      )

    return fig


# Define the page layout
layout = html.Div(id='parent',
                  children=[html.H1(id='H1',
                                    children='Yield Curve',
                                    style={'textAlign': 'center',
                                           'marginTop': 40,
                                           'marginBottom': 40,
                                           'marginRight': 40,
                                           'marginLeft': 40,
                                           }),

                            dcc.Graph(id='line_plot', figure=plot_yield_curve())

                            ]
                  )
