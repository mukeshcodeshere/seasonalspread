import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
# from SeasonalPriceUtilitiesN import contractMonths, yearList, getSeasonalPrices, createSpread, createSpread_Custom, createSpread_Calendar, createSpread_Quarterly
# Assuming SeasonalPriceUtilitiesN is not directly used in the Dash app itself for this problem,
# but rather the data from the SQL table is pre-processed or contains the 'spread' column.
# If these functions are meant to be used dynamically, they would need to be integrated into the callbacks.
from sqlalchemy import create_engine
from urllib import parse
import datetime
from datetime import datetime, timedelta
import numpy as np
import os
from dotenv import load_dotenv
# Import shared styles - UPDATED
from dash_styles import (
    CARD_HEADER_COLORS, CONTAINER_FLUID_CLASSES, CARD_COMMON_CLASSES, CARD_BORDER_RADIUS,
    DROPDOWN_INPUT_STYLE, SHADOW_SM_CLASS, PLOTLY_GRAPH_CONFIG, PLOTLY_TEMPLATE_LIGHT,
    GRAPH_MARGIN, GRAPH_CONTAINER_CLASSES, TEXT_CENTER_CLASS, TEXT_PRIMARY_CLASS,
    TEXT_MUTED_CLASS, FW_BOLD_CLASS, FS_4_CLASS, DISPLAY_5_CLASS, LEAD_CLASS, # Updated FS_4_CLASS, DISPLAY_5_CLASS
    ME_3_CLASS, MB_1_CLASS, MB_2_CLASS, MB_3_CLASS, MB_4_CLASS, MB_5_CLASS, # Updated ME_3_CLASS, MB_1_CLASS
    PY_3_CLASS, PY_4_CLASS, PY_5_CLASS, W_100_CLASS, D_FLEX_CLASS, # Updated PY_3_CLASS, PY_5_CLASS
    ALIGN_ITEMS_CENTER_CLASS, JUSTIFY_CONTENT_CENTER_CLASS, MS_3_CLASS, PB_3_CLASS, # Updated MS_3_CLASS, PB_3_CLASS
    MT_4_CLASS, # Updated MT_4_CLASS
    DATATABLE_STYLE_TABLE, DATATABLE_STYLE_CELL, DATATABLE_STYLE_HEADER, DATATABLE_STYLE_HEADER_CELL
)
# Load environment variables from .env file
load_dotenv("credential.env")

# Database connection setup
server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

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

# Load data from SQL
query = "SELECT * FROM [TradePriceAnalyzer].[contractMargins]"
data = pd.read_sql(query, con=engine)
data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
data["LastTrade"] = pd.to_datetime(data["LastTrade"], errors="coerce")


# Define the layout for the "Preset Calculation" application
layout_preset = dbc.Container([
    html.H2("Seasonal Spread Analysis", className=f"{TEXT_CENTER_CLASS} {TEXT_PRIMARY_CLASS} {MB_4_CLASS} {FW_BOLD_CLASS}"),

    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-filter {ME_3_CLASS}"),
                html.Span("Filter Options", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["primary"]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Group", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(id='group-dropdown', placeholder='Select Group', className=SHADOW_SM_CLASS, style=DROPDOWN_INPUT_STYLE)
                ], md=3, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("Type", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(id='type-dropdown', placeholder='Select Type', className=SHADOW_SM_CLASS, style=DROPDOWN_INPUT_STYLE)
                ], md=3, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("Region", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(id='region-dropdown', placeholder='Select Region', className=SHADOW_SM_CLASS, style=DROPDOWN_INPUT_STYLE)
                ], md=3, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("Name (Instrument)", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(id='name-dropdown', placeholder='Select Instrument Name', className=SHADOW_SM_CLASS, style=DROPDOWN_INPUT_STYLE)
                ], md=3, className=MB_3_CLASS),
                dbc.Col([
                    html.Label("Month", className=f"form-label fw-semibold {MB_2_CLASS}"),
                    dcc.Dropdown(id='month-dropdown', placeholder='Select Month', className=SHADOW_SM_CLASS, style=DROPDOWN_INPUT_STYLE)
                ], md=3, className=MB_3_CLASS),
            ], className=MB_4_CLASS),
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS),

    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-chart-line {ME_3_CLASS}"),
                html.Span("Seasonal Spread Chart", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["info"]),
        dbc.CardBody([
            dcc.Graph(id='spread-figure', config=PLOTLY_GRAPH_CONFIG, className=GRAPH_CONTAINER_CLASSES),
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS),

    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-chart-bar {ME_3_CLASS}"),
                html.Span("Spread Distribution Histogram", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["info"]),
        dbc.CardBody([
            dcc.Graph(id='spread-histogram', config=PLOTLY_GRAPH_CONFIG, className=GRAPH_CONTAINER_CLASSES),
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS),


    dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.I(className=f"fas fa-table {ME_3_CLASS}"),
                html.Span("Filtered Data Preview", className=f"{FW_BOLD_CLASS} {FS_4_CLASS}")
            ], className=f"{D_FLEX_CLASS} {ALIGN_ITEMS_CENTER_CLASS} {PY_3_CLASS}")
        ], className=CARD_HEADER_COLORS["success"]),
        dbc.CardBody([
            dash_table.DataTable(
                id='data-preview',
                page_size=10,
                style_table=DATATABLE_STYLE_TABLE,
                style_cell=DATATABLE_STYLE_CELL,
                style_header=DATATABLE_STYLE_HEADER
            )
        ])
    ], className=CARD_COMMON_CLASSES, style=CARD_BORDER_RADIUS)

], fluid=True, className=CONTAINER_FLUID_CLASSES)


# Function to register all callbacks for this application
def register_callbacks(app):
    # Dropdown: Group (Initial population)
    @app.callback(
        Output('group-dropdown', 'options'),
        Output('group-dropdown', 'value'), # Clear value on initial load
        Input('group-dropdown', 'id') # Dummy input to trigger initial population
    )
    def populate_group(_):
        groups = sorted(data['Group'].dropna().unique())
        return [{'label': g, 'value': g} for g in groups], None

    # Dropdown: Type (Cascading from Group)
    @app.callback(
        Output('type-dropdown', 'options'),
        Output('type-dropdown', 'value'), # Clear value when options change
        Input('group-dropdown', 'value')
    )
    def update_type(group):
        if group:
            types = sorted(data[data['Group'] == group]['Type'].dropna().unique())
            return [{'label': t, 'value': t} for t in types], None
        return [], None

    # Dropdown: Region (Cascading from Group and Type)
    @app.callback(
        Output('region-dropdown', 'options'),
        Output('region-dropdown', 'value'), # Clear value when options change
        Input('group-dropdown', 'value'),
        Input('type-dropdown', 'value')
    )
    def update_region(group, commodity_type): # Renamed 'type' to 'commodity_type' to avoid conflict with Python's built-in type()
        if group and commodity_type:
            regions = sorted(data[
                (data['Group'] == group) &
                (data['Type'] == commodity_type)
            ]['Region'].dropna().unique())
            return [{'label': r, 'value': r} for r in regions], None
        return [], None

    # Dropdown: Name (InstrumentName) (Cascading from Group, Type, and Region)
    @app.callback(
        Output('name-dropdown', 'options'),
        Output('name-dropdown', 'value'), # Clear value when options change
        Input('group-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('region-dropdown', 'value')
    )
    def update_name(group, commodity_type, region):
        if group and commodity_type and region:
            names = sorted(data[
                (data['Group'] == group) &
                (data['Type'] == commodity_type) &
                (data['Region'] == region)
            ]['InstrumentName'].dropna().unique())
            return [{'label': n, 'value': n} for n in names], None
        return [], None

    # Dropdown: Month (Cascading from Group, Type, Region, and Name)
    @app.callback(
        Output('month-dropdown', 'options'),
        Output('month-dropdown', 'value'), # Clear value when options change
        Input('group-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('name-dropdown', 'value')
    )
    def update_month(group, commodity_type, region, instrument_name):
        if group and commodity_type and region and instrument_name:
            months = sorted(data[
                (data['Group'] == group) &
                (data['Type'] == commodity_type) &
                (data['Region'] == region) &
                (data['InstrumentName'] == instrument_name)
            ]['Month'].dropna().unique())
            return [{'label': m, 'value': m} for m in months], None
        return [], None

    # Callback for seasonal chart and histogram
    @app.callback(
        Output('spread-figure', 'figure'),
        Output('spread-histogram', 'figure'),
        Input('group-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('name-dropdown', 'value'),
        Input('month-dropdown', 'value')
    )
    def update_figure(group, commodity_type, region, instrument_name, month):
        # Ensure all necessary filters are selected before attempting to plot
        if not all([group, commodity_type, region, instrument_name, month]):
            return go.Figure(), go.Figure() # Return empty figures

        filtered_df = data[
            (data['Group'] == group) &
            (data['Type'] == commodity_type) &
            (data['Region'] == region) &
            (data['InstrumentName'] == instrument_name) &
            (data['Month'] == month)
        ].copy()

        filtered_df = filtered_df.sort_values("Date")
        today = pd.Timestamp.today().normalize()

        historical_df = filtered_df[filtered_df['LastTrade'] <= today].copy()
        current_df = filtered_df[filtered_df['LastTrade'] > today].copy()

        fig = go.Figure()
        seasonal_data = {}

        for year in historical_df['Year'].unique():
            year_group = historical_df[historical_df['Year'] == year].copy()
            last_trade = year_group['LastTrade'].max()
            year_filtered = year_group[year_group['Date'] <= last_trade].sort_values('Date').tail(252).copy()
            if len(year_filtered) == 252:
                year_filtered = year_filtered.reset_index(drop=True)
                year_filtered['TradingDay'] = range(1, 253)
                seasonal_data[str(year)] = year_filtered

        if not historical_df.empty and not current_df.empty:
            last_hist_trade = historical_df['LastTrade'].max()
            # Calculate next month start from last_hist_trade, ensuring it's not before the earliest current_df date
            next_month_start = (last_hist_trade + pd.offsets.MonthBegin(1)).normalize()

            # Filter current_df for dates on or after next_month_start and take up to 252 trading days
            current_filtered = current_df[current_df['Date'] >= next_month_start].sort_values('Date').head(252).copy()

            if not current_filtered.empty:
                current_filtered = current_filtered.reset_index(drop=True)
                current_filtered['TradingDay'] = range(1, len(current_filtered) + 1)
                seasonal_data["Current"] = current_filtered


        for label, df in seasonal_data.items():
            fig.add_trace(go.Scatter(
                x=df["TradingDay"],
                y=df["spread"],
                mode="lines",
                name=label,
                line=dict(color="black" if label == "Current" else None,
                            width=3 if label == "Current" else 1.5),
                opacity=1.0 if label == "Current" else 0.6
            ))

        fig.update_layout(
            title="Seasonal Spread by Year",
            xaxis_title="Trading Day (1 to 252)",
            yaxis_title="Spread",
            margin=GRAPH_MARGIN,
            legend_title="Season",
            template=PLOTLY_TEMPLATE_LIGHT
        )

        hist_fig = go.Figure()
        if not filtered_df.empty and 'spread' in filtered_df.columns:
            spread_data = filtered_df["spread"].dropna()

            if not spread_data.empty:
                hist_fig.add_trace(go.Histogram(
                    x=spread_data,
                    marker_color='lightblue',
                    nbinsx=50,  # Increased bins
                    name='Spread Distribution',
                    hovertemplate="<b>Range:</b> %{x:.2f}<br><b>Frequency:</b> %{y}<extra></extra>"
                ))

                median_val = spread_data.median()
                std_dev = spread_data.std()
                mean_val = spread_data.mean()
                min_val = spread_data.min()
                max_val = spread_data.max()
                latest_value = spread_data.iloc[-1] if not spread_data.empty else None


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

                hist_fig.add_annotation(
                    xref="paper", yref="paper",
                    x=0.98, y=0.98,
                    text=stats_text,
                    showarrow=False,
                    align="left",
                    bgcolor="white",
                    bordercolor="black",
                    borderwidth=1,
                    borderpad=5,
                    font=dict(size=10, color="black")
                )

                hist_fig.add_vline(x=median_val, line_dash="dash", line_color="green",
                                     annotation_text=f"Median: {median_val:.2f}",
                                     annotation_position="top left", name="Median")

                hist_fig.add_vline(x=median_val + std_dev, line_dash="dot", line_color="purple",
                                     annotation_text=f"+1 SD: {(median_val + std_dev):.2f}",
                                     annotation_position="top right", name="+1 SD")
                hist_fig.add_vline(x=median_val - std_dev, line_dash="dot", line_color="purple",
                                     annotation_text=f"-1 SD: {(median_val - std_dev):.2f}",
                                     annotation_position="bottom left", name="-1 SD")

                hist_fig.add_vline(x=median_val + (2 * std_dev), line_dash="dot", line_color="orange",
                                     annotation_text=f"+2 SD: {(median_val + (2 * std_dev)):.2f}",
                                     annotation_position="top right", name="+2 SD")
                hist_fig.add_vline(x=median_val - (2 * std_dev), line_dash="dot", line_color="orange",
                                     annotation_text=f"-2 SD: {(median_val - (2 * std_dev)):.2f}",
                                     annotation_position="bottom left", name="-2 SD")

                if latest_value is not None:
                    hist_fig.add_vline(x=latest_value, line_dash="solid", line_color="blue", line_width=2,
                                         annotation_text=f"Latest: {latest_value:.2f}",
                                         annotation_position="bottom right", name="Latest Value")
            else:
                hist_fig.add_annotation(text="No spread data available for the selected filters.",
                                         xref="paper", yref="paper",
                                         x=0.5, y=0.5, showarrow=False,
                                         font=dict(size=16, color="gray"))
        else:
            hist_fig.add_annotation(text="No spread data to display histogram.",
                                     xref="paper", yref="paper",
                                     x=0.5, y=0.5, showarrow=False,
                                     font=dict(size=16, color="gray"))

        hist_fig.update_layout(
            title="Distribution of Spread (Histogram)",
            xaxis_title="Spread",
            yaxis_title="Frequency",
            template=PLOTLY_TEMPLATE_LIGHT,
            margin=GRAPH_MARGIN,
            showlegend=True # Ensure legend is shown for vlines
        )

        return fig, hist_fig

    # DataTable: Filtered Data Preview
    @app.callback(
        Output('data-preview', 'data'),
        Output('data-preview', 'columns'),
        Input('group-dropdown', 'value'),
        Input('type-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('name-dropdown', 'value'),
        Input('month-dropdown', 'value')
    )
    def update_table(group, commodity_type, region, instrument_name, month):
        if not all([group, commodity_type, region, instrument_name, month]):
            return [], [] # Return empty data and columns

        filtered_df = data[
            (data['Group'] == group) &
            (data['Type'] == commodity_type) &
            (data['Region'] == region) &
            (data['InstrumentName'] == instrument_name) &
            (data['Month'] == month)
        ].copy()

        filtered_df = filtered_df.sort_values("Date")
        filtered_df["LastTrade"] = pd.to_datetime(filtered_df["LastTrade"], errors="coerce")
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors="coerce")
        filtered_df["Year"] = filtered_df["Date"].dt.year

        if filtered_df.empty:
            return [], []

        columns = [{"name": i, "id": i} for i in filtered_df.columns]
        return filtered_df.to_dict('records'), columns