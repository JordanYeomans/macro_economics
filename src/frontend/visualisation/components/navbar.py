from dash import html
import dash_bootstrap_components as dbc


# Define the navbar structure
def navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Avg Interest Rates", href="/avg_interest_rates")),
                dbc.NavItem(dbc.NavLink("Debt To Penny", href="/debt_to_penny")),
            ],
            color="dark",
            dark=True,
        ),
    ])
    return layout
