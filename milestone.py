import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pandas_datareader.data as web
import plotly.graph_objs as go

from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta

nsdq = pd.read_csv('companylist.csv')
nsdq.drop(["LastSale", "MarketCap", "ADR TSO", "IPOyear", "Sector", "Industry", "Summary Quote", "Unnamed: 9"], axis=1,
          inplace=True)
nsdq.drop_duplicates(subset='Name', inplace=True)
nsdq.sort_values(by=['Name'], axis=0, inplace=True)
nsdq.set_index('Symbol', inplace=True)

app = dash.Dash()
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('Stock Ticker Dashboard', style={'textAlign': 'center'})
    ]),
    html.Div([
        html.Div([
            html.H3("Enter a company's stock symbol:"),
            dcc.Dropdown(
                id='symbols-list',
                options=[{'label': nsdq.loc[symb]['Name'] + f' ({symb})', 'value': symb} for symb in nsdq.index.values],
                value=[nsdq.index.values[0]],
                multi=True
            ),
        ], style={'width': '50%', 'display': 'inline-block', 'paddingRight': 30, 'verticalAlign': 'top'}),
        html.Div([
            html.H3('Enter a date range:'),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=datetime(datetime.now().year - 5, datetime.now().month, datetime.now().day),
                max_date_allowed=datetime.now(),
                display_format='DD/MM/Y',
                initial_visible_month=datetime.now(),
                start_date=datetime.now() - timedelta(31),
                end_date=datetime.now()
            ),
            html.Button(id='submit-button', n_clicks=0, children='See Stock Values',
                        style={'font-size': '16px', 'marginLeft': 10}),
        ], style={'width': '40%', 'display': 'inline-block'}),
    ]),
    html.Br(),
    dcc.Graph(
        id='stock-plot'
    )
])


@app.callback(Output('stock-plot', 'figure'), [Input('submit-button', 'n_clicks')],
              [State('symbols-list', 'value'), State('date-picker', 'start_date'), State('date-picker', 'end_date')])
def update_graph(_, symbol, start_date, end_date):
    # From string to datetime.
    start_date = datetime.strptime(start_date.split()[0], '%Y-%m-%d')
    start_date_str = start_date.strftime('%d/%m/%Y')

    end_date = datetime.strptime(end_date.split()[0], '%Y-%m-%d')
    end_date_str = end_date.strftime('%d/%m/%Y')

    plots = []

    for sym in symbol:
        df = web.DataReader(sym, 'iex', start_date, end_date)

        plots.append(go.Scatter(x=df.index, y=df.close, mode='lines+markers', name=sym, line={'width': 4}))

    figure = {
        'data': plots,
        'layout': go.Layout(title=f'{", ".join(sym for sym in symbol)} Closing Prices',
                            xaxis={'title': f'From {start_date_str} to {end_date_str}'},
                            yaxis={'title': '$USD'})
    }

    return figure


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server()
