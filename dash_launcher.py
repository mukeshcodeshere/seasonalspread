import dash
from dash import dcc, html, Input, Output
import dash_preset
import dash_onthefly

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Basic layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Simple launcher layout
launcher_layout = html.Div([
    html.H1("Welcome to Spread Calculator"),
    html.P("Choose a mode:"),
    html.Div([
        dcc.Link("Preset Calculation", href="/preset"),
        html.Br(),
        dcc.Link("On-the-fly Calculation", href="/on-the-fly")
    ])
])

# Routing callback
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/preset':
        return dash_preset.layout_preset
    elif pathname == '/on-the-fly':
        return dash_onthefly.layout_onthefly
    else:
        return launcher_layout

# Register sub-app callbacks
dash_preset.register_callbacks(app)
dash_onthefly.register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
