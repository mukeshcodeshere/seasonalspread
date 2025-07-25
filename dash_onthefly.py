# dash_onthefly.py
import dash
from dash import dcc, html, Input, Output, State, callback, MATCH, ALL
import plotly.graph_objects as go
import pandas as pd
# Assuming these are available and work as expected
from SeasonalPriceUtilitiesN import contractMonths, yearList, getSeasonalPrices, createSpread, createSpread_Custom, createSpread_Calendar, createSpread_Quarterly
from sqlalchemy import create_engine
from urllib import parse
import dash_bootstrap_components as dbc
import datetime
from datetime import datetime, timedelta
import numpy as np
import os
from dotenv import load_dotenv
from dash_styles import ( # Import shared styles - UPDATED
    CARD_HEADER_COLORS, CONTAINER_FLUID_CLASSES, CARD_COMMON_CLASSES, CARD_BORDER_RADIUS,
    DROPDOWN_INPUT_STYLE, SHADOW_SM_CLASS, PLOTLY_GRAPH_CONFIG, PLOTLY_TEMPLATE_LIGHT,
    GRAPH_MARGIN, GRAPH_CONTAINER_CLASSES, TEXT_CENTER_CLASS, TEXT_PRIMARY_CLASS,
    TEXT_MUTED_CLASS, FW_BOLD_CLASS, FS_4_CLASS, DISPLAY_5_CLASS, LEAD_CLASS,
    ME_3_CLASS, MB_1_CLASS, MB_2_CLASS, MB_3_CLASS, MB_4_CLASS, MB_5_CLASS,
    PY_3_CLASS, PY_4_CLASS, PY_5_CLASS, W_100_CLASS, D_FLEX_CLASS,
    ALIGN_ITEMS_CENTER_CLASS, JUSTIFY_CONTENT_CENTER_CLASS, MS_3_CLASS, PB_3_CLASS,
    MT_4_CLASS
)


# # Load environment variables from .env file
# load_dotenv("credential.env")

# # Database connection setup (assuming these are correctly loaded from .env)
# server = os.getenv("DB_SERVER")
# database = os.getenv("DB_NAME")
# username = os.getenv("DB_USERNAME")
# password = os.getenv("DB_PASSWORD")

# Read from environment variables directly (no dotenv)
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
schemaName = os.getenv("REFERENCE_SCHEMA")
table_Name = os.getenv("FUTURE_EXPIRY_TABLE")


connecting_string = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server={server};"
    f"Database={database};"
    f"Uid={username};"
    f"Pwd={password};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

params = parse.quote_plus(connecting_string)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", fast_executemany=True)

# Futures contract dictionary
futuresContractDict = {
    'F': {'abr': 'Jan', 'num': 1}, 'G': {'abr': 'Feb', 'num': 2},
    'H': {'abr': 'Mar', 'num': 3}, 'J': {'abr': 'Apr', 'num': 4},
    'K': {'abr': 'May', 'num': 5}, 'M': {'abr': 'Jun', 'num': 6},
    'N': {'abr': 'Jul', 'num': 7}, 'Q': {'abr': 'Aug', 'num': 8},
    'U': {'abr': 'Sep', 'num': 9}, 'V': {'abr': 'Oct', 'num': 10},
    'X': {'abr': 'Nov', 'num': 11}, 'Z': {'abr': 'Dec', 'num': 12}
}

# Quarterly mapping
quarterlyMonths = {
    'Q1': ['F', 'G', 'H'], # Jan, Feb, Mar
    'Q2': ['J', 'K', 'M'], # Apr, May, Jun
    'Q3': ['N', 'Q', 'U'], # Jul, Aug, Sep
    'Q4': ['V', 'X', 'Z']  # Oct, Nov, Dec
}

# Define the layout for the "On-the-fly Calculation" application
layout_onthefly = dbc.Container([
    # Header Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Seasonal Trading Analytics",
                        className=f"{DISPLAY_5_CLASS} {FW_BOLD_CLASS} {MB_1_CLASS} {TEXT_PRIMARY_CLASS}"),
                html.P("GCC",
                       className=f"{LEAD_CLASS} {TEXT_MUTED_CLASS} {MB_1_CLASS}")
            ], className=f"{TEXT_CENTER_CLASS} {PY_4_CLASS}")
        ])
    ], className=MB_5_CLASS),

    # Main Configuration Panel
    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-cog {ME_3_CLASS}"),
                html.Span("Trading Configuration", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["primary"]),

        dbc.CardBody([
            # Trade Type Selection and Global Parameters
            dbc.Row([
                dbc.Col([
                    html.Label("Strategy Type", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(
                        id='type',
                        options=[
                            {'label': 'Custom Spread', 'value': 'Custom'},
                            {'label': 'Calendar Spread', 'value': 'Calendar'},
                            {'label': 'Quarterly Spread', 'value': 'Quarterly'}
                        ],
                        value='Custom',
                        placeholder="Select your trading strategy...",
                        className=SHADOW_SM_CLASS,
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=4, className=MB_3_CLASS),
                ####
                dbc.Col([
                    html.Label("Analysis Period (Years)", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Input(
                        id='years-back',
                        type='number',
                        value=10,
                        placeholder="Years of historical data",
                        className=f"form-control {SHADOW_SM_CLASS}",
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=4, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("Roll Flag", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(
                        id='expire-flag',
                        options=[
                            {'label': 'Crude Oil (CL)', 'value': 'CL'},
                            {'label': 'Heating Oil (HO)', 'value': 'HO'},
                            {'label': 'Gasoline (XB)', 'value': 'XB'},
                            {'label': 'Brent (CO)', 'value': 'CO'},
                            {'label': 'Cash', 'value': 'Cash'}
                        ],
                        value='CL',
                        className=SHADOW_SM_CLASS,
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=4, className=MB_3_CLASS),
            ], className=MB_4_CLASS),

            # Dynamic Strategy Inputs Container
            html.Div(id='strategy-inputs-container', children=[
                # Custom Spread Configuration
                html.Div(id='custom-spread-inputs', children=[
                    dbc.Card([
                        dbc.CardHeader([
                            html.Span("Custom Spread Configuration", className="fw-semibold"),
                            dbc.Badge("First instrument is the anchor", color="info", className=MS_3_CLASS)
                        ], className=f"{CARD_HEADER_COLORS['light']} {PY_3_CLASS} border-bottom"),

                        dbc.CardBody([
                            # Headers for dynamic inputs
                            dbc.Row([
                                dbc.Col(html.Label('Instrument', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=4),
                                dbc.Col(html.Label('Contract Month', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=4),
                                dbc.Col(html.Label('Conversion Factor', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=4),
                            ], className=f"{MB_3_CLASS} {ALIGN_ITEMS_CENTER_CLASS} border-bottom {PB_3_CLASS}"),

                            # Dynamic Series Container
                            html.Div(id='series-inputs-container'),

                            # Action Buttons
                            dbc.Row([
                                dbc.Col([
                                    dbc.ButtonGroup([
                                        dbc.Button([
                                            html.I(className=f"fas fa-plus {ME_3_CLASS}"),
                                            "Add Series"
                                        ], id='add-series-btn', color="success", size="sm", className=ME_3_CLASS),
                                        dbc.Button([
                                            html.I(className=f"fas fa-minus {ME_3_CLASS}"),
                                            "Remove"
                                        ], id='remove-series-btn', color="outline-danger", size="sm"),
                                    ])
                                ], width="auto", className=f"{TEXT_CENTER_CLASS} {MT_4_CLASS}")
                            ], justify="center"),
                        ])
                    ], className=f"border-0 {SHADOW_SM_CLASS} {MB_4_CLASS}")
                ]),

                # Calendar Spread Configuration
                html.Div(id='calendar-spread-inputs', style={'display': 'none'}, children=[
                    dbc.Card([
                        dbc.CardHeader([
                            html.Span("Calendar Spread Configuration", className="fw-semibold"),
                            dbc.Badge("Y vs Y", color="warning", className=MS_3_CLASS)
                        ], className=f"{CARD_HEADER_COLORS['light']} {PY_3_CLASS} border-bottom"),

                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label('Near Year', className=f"form-label fw-semibold {MB_2_CLASS}"),
                                    dcc.Input(id='calendar-year1', type='number',
                                              placeholder='2025', className=f"form-control {SHADOW_SM_CLASS}"),
                                ], md=6, className=MB_3_CLASS),
                                dbc.Col([
                                    html.Label('Far Year', className=f"form-label fw-semibold {MB_2_CLASS}"),
                                    dcc.Input(id='calendar-year2', type='number',
                                              placeholder='2026', className=f"form-control {SHADOW_SM_CLASS}"),
                                ], md=6, className=MB_3_CLASS),
                            ], className=MB_4_CLASS),

                            # Headers for dynamic instruments
                            dbc.Row([
                                dbc.Col(html.Label('Instrument', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=6),
                                dbc.Col(html.Label('Conversion Factor', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=6),
                            ], className=f"{MB_3_CLASS} {ALIGN_ITEMS_CENTER_CLASS} border-bottom {PB_3_CLASS}"),

                            html.Div(id='calendar-instrument-inputs-container'),

                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className=f"fas fa-plus {ME_3_CLASS}"),
                                    "Add Instrument"
                                ], id='add-calendar-instrument-btn', color="success", size="sm", className=ME_3_CLASS),
                                dbc.Button([
                                    html.I(className=f"fas fa-minus {ME_3_CLASS}"),
                                    "Remove"
                                ], id='remove-calendar-instrument-btn', color="outline-danger", size="sm"),
                            ], className=f"{MT_4_CLASS} {D_FLEX_CLASS} {JUSTIFY_CONTENT_CENTER_CLASS}")
                        ])
                    ], className=f"border-0 {SHADOW_SM_CLASS} {MB_4_CLASS}")
                ]),

                # Quarterly Spread Configuration
                html.Div(id='quarterly-spread-inputs', style={'display': 'none'}, children=[
                    dbc.Card([
                        dbc.CardHeader([
                            html.Span("Quarterly Spread Configuration", className="fw-semibold"),
                            dbc.Badge("Q vs Q", color="success", className=MS_3_CLASS)
                        ], className=f"{CARD_HEADER_COLORS['light']} {PY_3_CLASS} border-bottom"),

                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label('First Quarter', className=f"form-label fw-semibold {MB_2_CLASS}"),
                                    dcc.Dropdown(
                                        id='quarterly-q1',
                                        options=[{'label': f'Q{i}', 'value': f'Q{i}'} for i in range(1,5)],
                                        placeholder='Select Q1...',
                                        className=SHADOW_SM_CLASS
                                    ),
                                ], md=6, className=MB_3_CLASS),
                                dbc.Col([
                                    html.Label('Second Quarter', className=f"form-label fw-semibold {MB_2_CLASS}"),
                                    dcc.Dropdown(
                                        id='quarterly-q2',
                                        options=[{'label': f'Q{i}', 'value': f'Q{i}'} for i in range(1,5)],
                                        placeholder='Select Q2...',
                                        className=SHADOW_SM_CLASS
                                    ),
                                ], md=6, className=MB_3_CLASS),
                            ], className=MB_4_CLASS),

                            # Headers for dynamic instruments
                            dbc.Row([
                                dbc.Col(html.Label('Instrument', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=6),
                                dbc.Col(html.Label('Conversion Factor', className=f"fw-semibold {TEXT_PRIMARY_CLASS} {MB_1_CLASS}"), md=6),
                            ], className=f"{MB_3_CLASS} {ALIGN_ITEMS_CENTER_CLASS} border-bottom {PB_3_CLASS}"),

                            html.Div(id='quarterly-instrument-inputs-container'),

                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className=f"fas fa-plus {ME_3_CLASS}"),
                                    "Add Instrument"
                                ], id='add-quarter-instrument-btn', color="success", size="sm", className=ME_3_CLASS),
                                dbc.Button([
                                    html.I(className=f"fas fa-minus {ME_3_CLASS}"),
                                    "Remove"
                                ], id='remove-quarter-instrument-btn', color="outline-danger", size="sm"),
                            ], className=f"{MT_4_CLASS} {D_FLEX_CLASS} {JUSTIFY_CONTENT_CENTER_CLASS}")
                        ])
                    ], className=f"border-0 {SHADOW_SM_CLASS} {MB_4_CLASS}")
                ]),
            ]),

            # Output Configuration
            dbc.Row([
                dbc.Col([
                    html.Label("Output Location", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Input(
                        id='location-out',
                        placeholder='e.g., Crude Oil WTI',
                        value='CL',
                        className=f"form-control {SHADOW_SM_CLASS}",
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=6, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("Units", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Input(
                        id='units-out',
                        placeholder='e.g., $/BBL',
                        value='$/BBL',
                        className=f"form-control {SHADOW_SM_CLASS}",
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=6, className=MB_3_CLASS),
            ], className=MB_4_CLASS),

            # Generate Button and CSV Output Checkbox
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.I(className=f"fas fa-chart-line {ME_3_CLASS}"),
                        "Generate Analysis"
                    ], id='generate-btn', color="primary", size="lg",
                       className=f"{W_100_CLASS} shadow", style={'borderRadius': '10px'})
                ], md=8),
                dbc.Col([
                    dbc.Checklist(
                        options=[{"label": "Output CSV", "value": 1}],
                        value=[],  # Default to unchecked
                        id="output-csv-checkbox",
                        switch=True, # Makes it a switch style
                        className=f"form-check-inline {ALIGN_ITEMS_CENTER_CLASS} {D_FLEX_CLASS} h-100"
                    ),
                ], md=4, className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {JUSTIFY_CONTENT_CENTER_CLASS}")
            ], className=MB_3_CLASS)
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS),

    # Analysis Controls
    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-sliders-h {ME_3_CLASS}"),
                html.Span("Histogram Analysis Controls", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["info"]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Start Month", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(
                        id='start-month-dropdown',
                        options=[{'label': v['abr'], 'value': v['num']} for k, v in futuresContractDict.items()],
                        value=1,  # Default to January
                        clearable=False,
                        className=SHADOW_SM_CLASS,
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=6, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("End Month", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(
                        id='end-month-dropdown',
                        options=[{'label': v['abr'], 'value': v['num']} for k, v in futuresContractDict.items()],
                        value=12,  # Default to December
                        clearable=False,
                        className=SHADOW_SM_CLASS,
                        style=DROPDOWN_INPUT_STYLE
                    ),
                ], md=6, className=MB_3_CLASS),
            ]),
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS),

    # Results Section
    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-analytics {ME_3_CLASS}"),
                html.Span("Analysis Results", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["success"]),
        dbc.CardBody([
            # Status Message
            html.Div(id='loading-output', className=f"{TEXT_CENTER_CLASS} {MB_3_CLASS} {FW_BOLD_CLASS} {TEXT_MUTED_CLASS}"),

            # Loading Component
            dcc.Loading(
                id="loading-graphs",
                type="circle",
                color="#007bff",
                children=[
                    # Chart Tabs
                    dbc.Tabs([
                        dbc.Tab([
                            dcc.Graph(
                                id='price-evolution-graph',
                                config=PLOTLY_GRAPH_CONFIG,
                                className=GRAPH_CONTAINER_CLASSES
                            )
                        ], label="Price Evolution", tab_id="price-tab", className=PY_3_CLASS),

                        dbc.Tab([
                            dcc.Graph(
                                id='volatility-graph',
                                config=PLOTLY_GRAPH_CONFIG,
                                className=GRAPH_CONTAINER_CLASSES
                            )
                        ], label="Volatility Analysis", tab_id="vol-tab", className=PY_3_CLASS),

                        dbc.Tab([
                            dcc.Graph(
                                id='histogram-graph',
                                config=PLOTLY_GRAPH_CONFIG,
                                className=GRAPH_CONTAINER_CLASSES
                            )
                        ], label="Distribution", tab_id="hist-tab", className=PY_3_CLASS),
                    ], active_tab="price-tab", className=f"{MB_3_CLASS} nav-pills"),
                ]
            )
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS),

    # Data Stores (keep these)
    dcc.Store(id='num-series-store', data=4),
    dcc.Store(id='num-calendar-instruments-store', data=1),
    dcc.Store(id='num-quarterly-instruments-store', data=1),
    # Add a store to hold the generated CSV data if needed for download
    dcc.Store(id='csv-data-store')

], fluid=True, className=CONTAINER_FLUID_CLASSES)


# Function to register all callbacks for this application
def register_callbacks(app):
    # Callback to show/hide input sections based on Trade Type
    @app.callback(
        Output('custom-spread-inputs', 'style'),
        Output('calendar-spread-inputs', 'style'),
        Output('quarterly-spread-inputs', 'style'),
        Input('type', 'value')
    )
    def toggle_input_sections(trade_type):
        if trade_type == 'Custom':
            return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
        elif trade_type == 'Calendar':
            return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
        elif trade_type == 'Quarterly':
            return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
        return {'display': 'none'}, {'display': 'none'}, {'display': 'none'}

    @app.callback(
        Output('series-inputs-container', 'children'),
        Output('num-series-store', 'data'),
        Input('add-series-btn', 'n_clicks'),
        Input('remove-series-btn', 'n_clicks'),
        State('num-series-store', 'data')
    )
    def update_series_inputs(add_clicks, remove_clicks, num_series):
        ctx = dash.callback_context

        if not ctx.triggered:
            current_num_series = num_series
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'add-series-btn':
                current_num_series = num_series + 1
            elif button_id == 'remove-series-btn':
                current_num_series = max(1, num_series - 1)
            else:
                current_num_series = num_series

        children = []
        default_series_names = ['HO', 'CL', 'HO', 'CL']
        default_contract_months = ['J', 'J', 'K', 'K']
        default_conversion_factors = [42, -1, -42, 1]

        for i in range(current_num_series):
            children.append(
                dbc.Row([
                    dbc.Col(dcc.Input(
                        id={'type': 'series-name-input', 'index': i},
                        placeholder=f'Series {i+1}',
                        value=default_series_names[i] if i < len(default_series_names) else None,
                        className=f"{MB_2_CLASS} {W_100_CLASS}"
                    ), md=4),
                    dbc.Col(dcc.Dropdown(
                        id={'type': 'contract-month-dropdown', 'index': i},
                        options=[{'label': v['abr'], 'value': k} for k, v in futuresContractDict.items()],
                        value=default_contract_months[i] if i < len(default_contract_months) else None,
                        placeholder=f"Contract {i+1}",
                        className=MB_2_CLASS
                    ), md=4),
                    dbc.Col(dcc.Input(
                        id={'type': 'conversion-factor-input', 'index': i},
                        type='number',
                        value=default_conversion_factors[i] if i < len(default_conversion_factors) else None,
                        className=f"{MB_2_CLASS} {W_100_CLASS}"
                    ), md=4),
                ])
            )
        return children, current_num_series

    # Callbacks for Calendar Spread Instruments
    @app.callback(
        Output('calendar-instrument-inputs-container', 'children'),
        Output('num-calendar-instruments-store', 'data'),
        Input('add-calendar-instrument-btn', 'n_clicks'),
        Input('remove-calendar-instrument-btn', 'n_clicks'),
        State('num-calendar-instruments-store', 'data')
    )
    def update_calendar_instrument_inputs(add_clicks, remove_clicks, num_instruments):
        ctx = dash.callback_context
        if not ctx.triggered:
            current_num_instruments = num_instruments
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'add-calendar-instrument-btn':
                current_num_instruments = num_instruments + 1
            elif button_id == 'remove-calendar-instrument-btn':
                current_num_instruments = max(1, num_instruments - 1)
            else:
                current_num_instruments = num_instruments

        children = []
        for i in range(current_num_instruments):
            children.append(
                dbc.Row([
                    dbc.Col(dcc.Input(
                        id={'type': 'calendar-instrument-name-input', 'index': i},
                        placeholder=f'Instrument {i+1}',
                        value='CL' if i == 0 else None,
                        className=f"{MB_2_CLASS} {W_100_CLASS}"
                    ), md=4),
                    dbc.Col(dcc.Input(
                        id={'type': 'calendar-conversion-factor-input', 'index': i},
                        type='number',
                        placeholder=f'Factor {i+1}',
                        value=1 if i == 0 else None,
                        className=f"{MB_2_CLASS} {W_100_CLASS}"
                    ), md=4),
                ])
            )
        return children, current_num_instruments

    # Callbacks for Quarterly Spread Instruments
    @app.callback(
        Output('quarterly-instrument-inputs-container', 'children'),
        Output('num-quarterly-instruments-store', 'data'),
        Input('add-quarter-instrument-btn', 'n_clicks'),
        Input('remove-quarter-instrument-btn', 'n_clicks'),
        State('num-quarterly-instruments-store', 'data')
    )
    def update_quarterly_instrument_inputs(add_clicks, remove_clicks, num_instruments):
        ctx = dash.callback_context
        if not ctx.triggered:
            current_num_instruments = num_instruments
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'add-quarter-instrument-btn':
                current_num_instruments = num_instruments + 1
            elif button_id == 'remove-quarter-instrument-btn':
                current_num_instruments = max(1, num_instruments - 1)
            else:
                current_num_instruments = num_instruments

        children = []
        for i in range(current_num_instruments):
            children.append(
                dbc.Row([
                    dbc.Col(dcc.Input(
                        id={'type': 'quarterly-instrument-name-input', 'index': i},
                        placeholder=f'Instrument {i+1}',
                        value='CL' if i == 0 else None,
                        className=f"{MB_2_CLASS} {W_100_CLASS}"
                    ), md=4),
                    dbc.Col(dcc.Input(
                        id={'type': 'quarterly-conversion-factor-input', 'index': i},
                        type='number',
                        placeholder=f'Factor {i+1}',
                        value=1 if i == 0 else None,
                        className=f"{MB_2_CLASS} {W_100_CLASS}"
                    ), md=4),
                ])
            )
        return children, current_num_instruments


    @app.callback(
        Output('price-evolution-graph', 'figure'),
        Output('volatility-graph', 'figure'),
        Output('histogram-graph', 'figure'),
        Output('loading-output', 'children'),
        Output('csv-data-store', 'data'), # Add output for CSV data storage
        [Input('generate-btn', 'n_clicks'),
         Input('start-month-dropdown', 'value'),
         Input('end-month-dropdown', 'value')],
        [State('type', 'value'),
         # Custom Spread States
         State({'type': 'series-name-input', 'index': ALL}, 'value'),
         State({'type': 'contract-month-dropdown', 'index': ALL}, 'value'),
         State({'type': 'conversion-factor-input', 'index': ALL}, 'value'),
         # Calendar Spread States
         State('calendar-year1', 'value'),
         State('calendar-year2', 'value'),
         State({'type': 'calendar-instrument-name-input', 'index': ALL}, 'value'),
         State({'type': 'calendar-conversion-factor-input', 'index': ALL}, 'value'),
         # Quarterly Spread States
         State('quarterly-q1', 'value'),
         State('quarterly-q2', 'value'),
         State({'type': 'quarterly-instrument-name-input', 'index': ALL}, 'value'),
         State({'type': 'quarterly-conversion-factor-input', 'index': ALL}, 'value'),

         State('years-back', 'value'), State('expire-flag', 'value'),
         State('location-out', 'value'), State('units-out', 'value'),
         State('output-csv-checkbox', 'value')] # State of the new checkbox
    )
    def generate_graphs(n_clicks, start_month, end_month, trade_type,
                        series_names, contract_months, conversion_factors,
                        calendar_year1, calendar_year2, calendar_instrument_names, calendar_conversion_factors,
                        quarterly_q1, quarterly_q2, quarterly_instrument_names, quarterly_conversion_factors,
                        years_back, expire_flag, loc_out, units_out, output_csv):

        if not n_clicks:
            return go.Figure(), go.Figure(), go.Figure(), "", None # Return None for csv_data_store initially

        loading_message = "Generating graphs... This may take a few moments depending on the data size."
        # Initial return with loading message, and empty figures
        return go.Figure(), go.Figure(), go.Figure(), loading_message, None


    @app.callback(
        Output('price-evolution-graph', 'figure', allow_duplicate=True),
        Output('volatility-graph', 'figure', allow_duplicate=True),
        Output('histogram-graph', 'figure', allow_duplicate=True),
        Output('loading-output', 'children', allow_duplicate=True),
        Output('csv-data-store', 'data', allow_duplicate=True), # Allow duplicate for this output
        [Input('generate-btn', 'n_clicks'),
         Input('start-month-dropdown', 'value'),
         Input('end-month-dropdown', 'value')],
        State('type', 'value'),
        # Custom Spread States
        State({'type': 'series-name-input', 'index': ALL}, 'value'),
        State({'type': 'contract-month-dropdown', 'index': ALL}, 'value'),
        State({'type': 'conversion-factor-input', 'index': ALL}, 'value'),
        # Calendar Spread States
        State('calendar-year1', 'value'),
        State('calendar-year2', 'value'),
        State({'type': 'calendar-instrument-name-input', 'index': ALL}, 'value'),
        State({'type': 'calendar-conversion-factor-input', 'index': ALL}, 'value'),
        # Quarterly Spread States
        State('quarterly-q1', 'value'),
        State('quarterly-q2', 'value'),
        State({'type': 'quarterly-instrument-name-input', 'index': ALL}, 'value'),
        State({'type': 'quarterly-conversion-factor-input', 'index': ALL}, 'value'),
        State('years-back', 'value'), State('expire-flag', 'value'),
        State('location-out', 'value'), State('units-out', 'value'),
        State('output-csv-checkbox', 'value'), # State of the new checkbox
        prevent_initial_call=True
    )
    def perform_graph_generation(n_clicks, start_month, end_month, trade_type,
                                 series_names, contract_months, conversion_factors,
                                 calendar_year1, calendar_year2, calendar_instrument_names, calendar_conversion_factors,
                                 quarterly_q1, quarterly_q2, quarterly_instrument_names, quarterly_conversion_factors,
                                 years_back, expire_flag, loc_out, units_out, output_csv):

        # Get expire data
        query = f"SELECT * FROM [Reference].[FuturesExpire] WHERE Ticker = '{expire_flag}'"
        temp_expire = pd.read_sql(query, con=engine)
        temp_expire.set_index(pd.to_datetime(temp_expire['LastTrade'], format='%m/%d/%y'), inplace=True)

        spread = pd.DataFrame()
        year_list_for_graph = []

        if trade_type == 'Custom':
            last_trade = contractMonths(temp_expire, contract_months[0] if contract_months else None)
            year_list1, year_list2 = yearList(last_trade, years_back, trade_type,
                                              contract_months[0] if contract_months else None,
                                              contract_months[1] if len(contract_months) > 1 else None,
                                              futuresContractDict)
            year_list_for_graph = year_list1

            series_data_list = []
            for i in range(len(series_names)):
                s_name = series_names[i]
                c_month = contract_months[i]
                cf = conversion_factors[i]

                if s_name and c_month is not None and cf is not None:
                    current_series_year_list = year_list1
                    try:
                        zz = getSeasonalPrices(s_name, s_name.split('_')[-1], c_month, current_series_year_list)
                        if zz:
                            series_data_list.append({
                                'data': zz,
                                'cf': cf,
                                'series_name': s_name,
                                'contract_month': c_month,
                                'year_list': current_series_year_list
                            })
                    except Exception as e:
                        print(f"Error fetching data for series {s_name}, month {c_month}: {e}")
                        continue

            if not series_data_list:
                return go.Figure().update_layout(title_text="Error: At least one valid series is required for Custom trade type.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None

            spread = createSpread_Custom(series_data_list, last_trade, year_list1)

        elif trade_type == 'Calendar':
            if not (calendar_year1 and calendar_year2 and calendar_instrument_names and calendar_conversion_factors):
                return go.Figure().update_layout(title_text="Error: Missing inputs for Calendar Spread.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None

            instrument_cf_list = []
            for i in range(len(calendar_instrument_names)):
                if calendar_instrument_names[i] and calendar_conversion_factors[i] is not None:
                    instrument_cf_list.append({
                        'instrument': calendar_instrument_names[i],
                        'cf': calendar_conversion_factors[i]
                    })

            if not instrument_cf_list:
                return go.Figure().update_layout(title_text="Error: At least one instrument with conversion factor is required for Calendar Spread.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None

            current_year = datetime.now().year % 100
            historical_years_for_graph = [str(y % 100) for y in range(current_year - years_back, current_year + 1)]

            spread = createSpread_Calendar(
                instrument_cf_list,
                temp_expire,
                calendar_year1,
                calendar_year2,
                years_back,
                futuresContractDict
            )
            year_list_for_graph = [col for col in spread.columns if col.startswith(str(calendar_year1 % 100))]


        elif trade_type == 'Quarterly':
            if not (quarterly_q1 and quarterly_q2 and quarterly_instrument_names and quarterly_conversion_factors):
                return go.Figure().update_layout(title_text="Error: Missing inputs for Quarterly Spread.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None

            instrument_cf_list = []
            for i in range(len(quarterly_instrument_names)):
                if quarterly_instrument_names[i] and quarterly_conversion_factors[i] is not None:
                    instrument_cf_list.append({
                        'instrument': quarterly_instrument_names[i],
                        'cf': quarterly_conversion_factors[i]
                    })

            if not instrument_cf_list:
                return go.Figure().update_layout(title_text="Error: At least one instrument with conversion factor is required for Quarterly Spread.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None

            current_year = datetime.now().year % 100
            year_list_for_graph = [str(y % 100) for y in range(current_year - years_back, current_year + 1)]

            spread = createSpread_Quarterly(
                instrument_cf_list,
                temp_expire,
                quarterly_q1,
                quarterly_q2,
                years_back,
                futuresContractDict,
                quarterlyMonths
            )

        else:
            return go.Figure().update_layout(title_text="Invalid Trade Type Selected.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None

        if spread.empty:
            return go.Figure().update_layout(title_text="No spread data generated. Check inputs.", template=PLOTLY_TEMPLATE_LIGHT, margin=GRAPH_MARGIN), go.Figure(), go.Figure(), "", None


        # Calculate volatility
        spread_vol = spread.diff().rolling(20).std() * 2
        ###############
        # --- Seasonal Price Evolution Graph ---
        fig_price_evolution = go.Figure()
        for year in year_list_for_graph[:-1]:
            if year in spread.columns:
                fig_price_evolution.add_trace(go.Scatter(x=spread.index, y=spread[year], mode='lines',
                                                         name=f'Historical {year}', opacity=0.7))

        current_year_col = year_list_for_graph[-1]
        if current_year_col in spread.columns:
            current_year_data = spread[current_year_col].dropna()
            fig_price_evolution.add_trace(go.Scatter(x=current_year_data.index, y=current_year_data,
                                                     line=dict(color='black', width=3), name=f'Current Year ({current_year_col})'))

        fig_price_evolution.update_layout(
            title_text=f"<b>Seasonal Price Evolution ({units_out or 'Value'})</b>",
            title_x=0.5,
            hovermode="x unified",
            font_color='black',
            paper_bgcolor='white',
            template=PLOTLY_TEMPLATE_LIGHT,
            height=400,
            margin=GRAPH_MARGIN,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_price_evolution.update_xaxes(
            tickformat="%b %d",
            showgrid=True, gridwidth=1, gridcolor='LightGrey'
        )
        fig_price_evolution.update_yaxes(
            title_text=units_out or "Price",
            showgrid=True, gridwidth=1, gridcolor='LightGrey'
        )

        # --- Seasonal Volatility Graph ---
        fig_volatility = go.Figure()
        for year in year_list_for_graph[:-1]:
            if year in spread_vol.columns:
                fig_volatility.add_trace(go.Scatter(x=spread_vol.index, y=spread_vol[year], mode='lines',
                                                    name=f'Historical {year} Vol', opacity=0.7))
        current_vol_col = year_list_for_graph[-1]
        if current_vol_col in spread_vol.columns:
            current_vol_data = spread_vol[current_vol_col].dropna()
            fig_volatility.add_trace(go.Scatter(x=current_vol_data.index, y=current_vol_data,
                                                line=dict(color='black', width=3), name=f'Current Year ({current_vol_col}) Vol'))

        fig_volatility.update_layout(
            title_text=f"<b>Var/Unit (20-Day Rolling Std Dev * 2)</b>",
            title_x=0.5,
            hovermode="x unified",
            font_color='black',
            paper_bgcolor='white',
            template=PLOTLY_TEMPLATE_LIGHT,
            height=400,
            margin=GRAPH_MARGIN,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_volatility.update_xaxes(
            tickformat="%b %d",
            showgrid=True, gridwidth=1, gridcolor='LightGrey'
        )
        fig_volatility.update_yaxes(
            title_text="Volatility",
            showgrid=True, gridwidth=1, gridcolor='LightGrey'
        )

        # --- Histogram Graph ---
        fig_hist = go.Figure()

        if start_month is not None and end_month is not None:
            # Logic to handle month range, including cross-year ranges
            if start_month <= end_month:
                # Normal range, e.g., Jan to Dec, or Mar to Jul
                months_to_include = list(range(start_month, end_month + 1))
            else:
                # Cross-year range, e.g., Nov to Feb (11, 12, 1, 2)
                months_to_include = list(range(start_month, 13)) + list(range(1, end_month + 1))

            month_data = spread[spread.index.month.isin(months_to_include)].stack().dropna()

            if not month_data.empty:
                fig_hist.add_trace(go.Histogram(
                    x=month_data,
                    nbinsx=100,  # Increased bins for more detail
                    name='Price Distribution',
                    hovertemplate="<b>Range:</b> %{x:.2f}<br><b>Frequency:</b> %{y}<extra></extra>",
                    marker_color='#1f77b4',  # A nice blue color
                    opacity=0.7
                ))

                median_val = month_data.median()
                std_dev = month_data.std()
                mean_val = month_data.mean()
                min_val = month_data.min()
                max_val = month_data.max()

                latest_value = spread[current_year_col].dropna().iloc[-1] if not spread[current_year_col].dropna().empty else None

                stats_text = (
                    f"<b>Statistics:</b><br>"
                    f"Median: {median_val:.2f}<br>"
                    f"Mean: {mean_val:.2f}<br>"
                    f"Std Dev: {std_dev:.2f}<br>"
                    f"Min: {min_val:.2f}<br>"
                    f"Max: {max_val:.2f}"
                )
                if latest_value is not None:
                    stats_text += f"<br>Latest: {latest_value:.2f}"


                fig_hist.add_annotation(
                    xref="paper", yref="paper",
                    x=0.98, y=0.98,
                    text=stats_text,
                    showarrow=False,
                    align="left",
                    bgcolor="rgba(255, 255, 255, 0.8)",  # Slightly transparent white background
                    bordercolor="black",
                    borderwidth=1,
                    borderpad=5,
                    font=dict(size=12, color="black")
                )

                fig_hist.add_vline(x=median_val, line=dict(dash="dash", color="green", width=2),
                                     annotation_text=f"Median: {median_val:.2f}",
                                     annotation_position="top left", name="Median",
                                     annotation_font_color="green")

                fig_hist.add_vline(x=median_val + std_dev, line=dict(dash="dot", color="orange", width=1.5),
                                     annotation_text=f"+1 SD: {(median_val + std_dev):.2f}",
                                     annotation_position="top right", name="+1 SD",
                                     annotation_font_color="orange")
                fig_hist.add_vline(x=median_val - std_dev, line=dict(dash="dot", color="orange", width=1.5),
                                     annotation_text=f"-1 SD: {(median_val - std_dev):.2f}",
                                     annotation_position="bottom left", name="-1 SD",
                                     annotation_font_color="orange")

                fig_hist.add_vline(x=median_val + (2 * std_dev), line=dict(dash="dot", color="red", width=1.5),
                                     annotation_text=f"+2 SD: {(median_val + (2 * std_dev)):.2f}",
                                     annotation_position="top right", name="+2 SD",
                                     annotation_font_color="red")
                fig_hist.add_vline(x=median_val - (2 * std_dev), line=dict(dash="dot", color="red", width=1.5),
                                     annotation_text=f"-2 SD: {(median_val - (2 * std_dev)):.2f}",
                                     annotation_position="bottom left", name="-2 SD",
                                     annotation_font_color="red")

                if latest_value is not None:
                    fig_hist.add_vline(x=latest_value, line=dict(dash="solid", color="blue", width=3),
                                         annotation_text=f"Latest: {latest_value:.2f}",
                                         annotation_position="bottom right", name="Latest Value",
                                         annotation_font_color="blue")
            else:
                fig_hist.add_annotation(text=f"No data available for the selected month range.",
                                         xref="paper", yref="paper",
                                         x=0.5, y=0.5, showarrow=False,
                                         font=dict(size=16, color="gray"))
        else:
            fig_hist.add_annotation(text="Select a start and end month to see the histogram.",
                                     xref="paper", yref="paper",
                                     x=0.5, y=0.5, showarrow=False,
                                     font=dict(size=16, color="gray"))

        # Determine month range title for the histogram
        start_month_abr = futuresContractDict[list(futuresContractDict.keys())[start_month-1]]['abr'] if start_month else ""
        end_month_abr = futuresContractDict[list(futuresContractDict.keys())[end_month-1]]['abr'] if end_month else ""
        month_range_title = f"{start_month_abr} - {end_month_abr}" if start_month and end_month else ""


        fig_hist.update_layout(
            title_text=f"<b>Price Distribution for {month_range_title}</b>",
            title_x=0.5,
            xaxis_title_text=units_out or "Price",
            yaxis_title_text="Frequency",
            font_color='black',
            paper_bgcolor='white',
            template=PLOTLY_TEMPLATE_LIGHT,
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            showlegend=True
        )

        # --- CSV Generation Logic ---
        csv_output_data = None # Initialize to None

        if 1 in output_csv: # Check if the checkbox is checked (value 1 is present)
            csv_data = {}
            csv_data['rollFlag'] = expire_flag
            csv_data['yearsBack'] = years_back

            csv_data['tickerList'] = []
            csv_data['contractMonthsList'] = []
            csv_data['yearOffsetList'] = []
            csv_data['weightsList'] = []
            csv_data['convList'] = []
            csv_data['desc'] = ''
            csv_data['group'] = ''
            csv_data['region'] = loc_out

            if trade_type == 'Custom':
                csv_data['Name'] = 'Custom Spread'
                csv_data['months'] = ''
                csv_data['desc'] = 'Custom Spread Calculation'

                for i in range(len(series_names)):
                    s_name = series_names[i]
                    c_month = contract_months[i]
                    cf = conversion_factors[i]
                    if s_name and c_month is not None and cf is not None:
                        csv_data['tickerList'].append(f"'{s_name}'")
                        csv_data['contractMonthsList'].append(f"'{c_month}'")
                        csv_data['weightsList'].append(str(cf)) # Store as string, not with quotes for numerical values
                        csv_data['convList'].append(str(cf))
                        csv_data['yearOffsetList'].append('0')

                csv_data['tickerList'] = f"[{','.join(csv_data['tickerList'])}]"
                csv_data['contractMonthsList'] = f"[{','.join(csv_data['contractMonthsList'])}]"
                csv_data['yearOffsetList'] = f"[{','.join(csv_data['yearOffsetList'])}]"
                csv_data['weightsList'] = f"[{','.join(csv_data['weightsList'])}]"
                csv_data['convList'] = f"[{','.join(csv_data['convList'])}]"

            elif trade_type == 'Calendar':
                csv_data['Name'] = f"Calendar Spread {calendar_year1} vs {calendar_year2}"
                csv_data['months'] = ''
                csv_data['desc'] = f"Calendar Spread {calendar_year1} vs {calendar_year2}"

                if calendar_instrument_names and calendar_conversion_factors:
                    for i in range(len(calendar_instrument_names)):
                        inst_name = calendar_instrument_names[i]
                        inst_cf = calendar_conversion_factors[i]
                        if inst_name and inst_cf is not None:
                            csv_data['tickerList'].append(f"'{inst_name}'")
                            csv_data['convList'].append(str(inst_cf))
                            # Assuming 'J' as a common month for illustration purposes if not explicitly defined by inputs
                            csv_data['contractMonthsList'].append("'J'") # Placeholder, needs refinement
                            csv_data['yearOffsetList'].append('0' if i == 0 else '1') # Simple assumption for 2 instruments

                csv_data['tickerList'] = f"[{','.join(csv_data['tickerList'])}]"
                csv_data['contractMonthsList'] = f"[{','.join(csv_data['contractMonthsList'])}]"
                csv_data['yearOffsetList'] = f"[{','.join(csv_data['yearOffsetList'])}]"
                csv_data['weightsList'] = csv_data['convList'] # For Calendar, weights might be similar to conversion factors
                csv_data['convList'] = f"[{','.join(csv_data['convList'])}]"

            elif trade_type == 'Quarterly':
                csv_data['Name'] = f"Quarterly Spread {quarterly_q1} vs {quarterly_q2}"
                csv_data['months'] = ''
                csv_data['desc'] = f"Quarterly Spread {quarterly_q1} vs {quarterly_q2}"

                if quarterly_instrument_names and quarterly_conversion_factors:
                    for i in range(len(quarterly_instrument_names)):
                        inst_name = quarterly_instrument_names[i]
                        inst_cf = quarterly_conversion_factors[i]
                        if inst_name and inst_cf is not None:
                            csv_data['tickerList'].append(f"'{inst_name}'")
                            csv_data['convList'].append(str(inst_cf))
                            q1_months = quarterlyMonths.get(quarterly_q1, [])
                            q2_months = quarterlyMonths.get(quarterly_q2, [])
                            # Using the first month of each quarter for contractMonthsList
                            csv_data['contractMonthsList'].append(f"'{q1_months[0]}'" if q1_months else "''")
                            csv_data['contractMonthsList'].append(f"'{q2_months[0]}'" if q2_months else "''")
                            csv_data['yearOffsetList'].append('0') # Assuming same year for Q vs Q

                csv_data['tickerList'] = f"[{','.join(csv_data['tickerList'])}]"
                csv_data['contractMonthsList'] = f"[{','.join(csv_data['contractMonthsList'])}]"
                csv_data['yearOffsetList'] = f"[{','.join(csv_data['yearOffsetList'])}]"
                csv_data['weightsList'] = csv_data['convList']
                csv_data['convList'] = f"[{','.join(csv_data['convList'])}]"

            df_csv = pd.DataFrame([csv_data])

            output_columns = [
                'Name', 'tickerList', 'contractMonthsList', 'yearOffsetList',
                'weightsList', 'convList', 'rollFlag', 'months', 'desc', 'group', 'region', 'yearsBack'
            ]
            df_csv = df_csv[output_columns]

            csv_file_path = 'userInputOnthefly.csv'
            df_csv.to_csv(csv_file_path, index=False)
            print(f"CSV file '{csv_file_path}' generated successfully.")
            csv_output_data = df_csv.to_dict('records') # Convert DataFrame to a list of dicts for dcc.Store

        return fig_price_evolution, fig_volatility, fig_hist, "", csv_output_data # Return csv_output_data