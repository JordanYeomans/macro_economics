import dash

from dash import html, dcc
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

from src.frontend.visualisation.components.navbar import navbar
from src.frontend.visualisation.pages.management import page_dict

# Connect to main app.py file
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                suppress_callback_exceptions=True)

pages = page_dict()

# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar(),
    html.Div(id='page-content', children=[]),
])


# Create the callback to handle mutlipage inputs
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname in pages.keys():
        return pages[pathname].layout
    else:
        return "404 Page Error! Please choose a link"


# Run the app on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=True)
