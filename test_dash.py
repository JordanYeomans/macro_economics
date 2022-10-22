from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State

app = Dash(__name__)

app.layout = html.Div([

    dash_table.DataTable(
        id='adding-rows-table',
        columns=[{
            'name': 'date',
            'id': 'column-date',
            'deletable': False,
            'renamable': False
        },
            {
            'name': 'date_2',
            'id': 'column-date_2',
            'deletable': False,
            'renamable': False
        }],
        data=[
            {'column-date': '2022-01-01',
             'column-date_2': 1},
        ],
        editable=True,
        row_deletable=True
    ),

    html.Button('Add Row', id='editing-rows-button', n_clicks=0),

    dcc.Graph(id='adding-rows-graph')
])


@app.callback(
    Output('adding-rows-table', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('adding-rows-graph', 'figure'),
    Input('adding-rows-table', 'data'),
    Input('adding-rows-table', 'columns'))
def display_output(rows, columns):
    x = [c['name'] for c in columns]
    z = [[row.get(c['id'], None) for c in columns] for row in rows]

    print(x)
    print(z)

    return {
        'data': [{
            'type': 'heatmap',
            'z': [[row.get(c['id'], None) for c in columns] for row in rows],
            'x': [c['name'] for c in columns]
        }]
    }



if __name__ == '__main__':
    app.run_server(debug=True)