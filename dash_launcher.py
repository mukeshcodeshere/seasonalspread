import dash
from dash import dcc, html, Input, Output, State
import dash_preset
import dash_onthefly
import dash_bootstrap_components as dbc
import socket

# Initialize Dash app
# Suppress callback exceptions is important when using dcc.Location for routing
# as callbacks for inactive layouts might trigger initially.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN], suppress_callback_exceptions=True)

# Custom index string to include Font Awesome for icons and custom CSS
# This ensures consistent styling across both sub-applications
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body { 
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .container {
                max-width: 900px;
                margin: 50px auto;
                padding: 30px;
                background-color: #ffffff;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .title {
                color: #007bff;
                font-size: 2.5em;
                margin-bottom: 20px;
                font-weight: bold;
            }
            .radio-group {
                margin-top: 30px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
            }
            .button-link {
                display: inline-block;
                padding: 12px 25px;
                background-color: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-size: 1.1em;
                font-weight: 600;
                transition: background-color 0.3s ease, transform 0.2s ease;
                box-shadow: 0 4px 10px rgba(40, 167, 69, 0.3);
                min-width: 250px; /* Ensure buttons have a minimum width */
                text-align: center;
            }
            .button-link:hover {
                background-color: #218838;
                transform: translateY(-2px);
                color: white; /* Keep text white on hover */
            }
            .button-link + .button-link {
                margin-top: 15px; /* Space between buttons */
            }
            .status-message {
                margin-top: 25px;
                padding: 15px;
                border-radius: 8px;
                background-color: #e9ecef;
                color: #343a40;
                font-size: 1.05em;
                border: 1px solid #dee2e6;
            }
            .card { 
                border-radius: 12px !important;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
                border: none !important;
            }
            .form-control, .form-select {
                border-radius: 8px !important;
                border: 1px solid #e0e6ed !important;
                transition: all 0.3s ease !important;
            }
            .form-control:focus, .form-select:focus {
                border-color: #007bff !important;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25) !important;
            }
            .btn {
                border-radius: 8px !important;
                transition: all 0.3s ease !important;
            }
            .btn:hover {
                transform: translateY(-1px) !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
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

server = app.server 

if __name__ == '__main__':
    #app.run(debug=True, host=get_local_ip(), port=8050) #host on local network
    #app.run(debug=True,port=8050) #only locally deployed
    app.run(debug=True) #github azure 


