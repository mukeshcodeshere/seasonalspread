import dash
from dash import dcc, html, Input, Output, State
import dash_preset
import dash_onthefly
import dash_bootstrap_components as dbc
import socket
from dash_styles import EXTERNAL_STYLESHEETS, INDEX_STRING_CUSTOM_CSS # Import from dash_styles

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=EXTERNAL_STYLESHEETS, suppress_callback_exceptions=True)

app.title = "Spread Calculation App"  # Set title
server = app.server                     # Expose server early for deployment


# Custom index string to include Font Awesome for icons and custom CSS
# This ensures consistent styling across both sub-applications
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        {INDEX_STRING_CUSTOM_CSS}
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# Define the main layout with URL routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Represents the URL in the browser
    html.Div(id='page-content')  # Content will change based on the URL
])

# Define the layout for the launcher page
launcher_layout = html.Div(
    className='container',
    children=[
        html.H1("Welcome to the Calculation Launcher", className='title'),
        html.P("Please select the desired calculation mode to launch the application."),
        html.Div(
            className='radio-group',
            children=[
                # Use dcc.Link to navigate to different paths
                dcc.Link('Go to Preset Calculation', href='/preset', className='button-link'),
                dcc.Link('Go to On-the-fly Calculation', href='/on-the-fly', className='button-link')
            ]
        )
    ]
)

# Callback to update page content based on URL pathname
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/preset':
        # Return the layout of the preset application
        return dash_preset.layout_preset
    elif pathname == '/on-the-fly':
        # Return the layout of the on-the-fly application
        return dash_onthefly.layout_onthefly
    else:
        # Default to the launcher page if no specific path is matched
        return launcher_layout

# Register callbacks from both imported applications
# This is crucial for their interactivity to work within the main app
dash_preset.register_callbacks(app)
dash_onthefly.register_callbacks(app)


# Get local IP address dynamically
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external host (does not send packets)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

if __name__ == '__main__':
    #app.run(debug=True, host=get_local_ip(), port=8050) #host on local network
    #app.run(debug=True,port=8050) #only locally deployed
    app.run(debug=True) #github azure
