import dash
from dash import Dash, html, dcc, Input, Output,dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from SeasonalPriceUtilitiesN import contractMonths, yearList, getSeasonalPrices, createSpread, createSpread_Custom, createSpread_Calendar, createSpread_Quarterly
from sqlalchemy import create_engine
from urllib import parse
import dash_bootstrap_components as dbc
import datetime
from datetime import datetime, timedelta
import numpy as np
import os
from dotenv import load_dotenv

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
    html.H2("Seasonal Spread Analysis"),

    dbc.Row([
        dbc.Col([dcc.Dropdown(id='group-dropdown', placeholder='Select Group')]),
        dbc.Col([dcc.Dropdown(id='region-dropdown', placeholder='Select Region')]),
        dbc.Col([dcc.Dropdown(id='instrument-dropdown', placeholder='Select Instrument')]),
        dbc.Col([dcc.Dropdown(id='month-dropdown', placeholder='Select Month')]),
    ]),

    html.Br(),
    dcc.Graph(id='spread-figure'),
    html.Br(),
    dcc.Graph(id='spread-histogram'),

    html.H4("Filtered Data Preview"),
    dash_table.DataTable(
        id='data-preview',
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={
            'backgroundColor': 'black',
            'color': 'white',
            'textAlign': 'left',
            'fontSize': 12,
        },
        style_header={
            'backgroundColor': 'rgb(30, 30, 30)',
            'fontWeight': 'bold'
        }
    )
], fluid=True)


# Function to register all callbacks for this application
def register_callbacks(app):
    # Dropdown: Group
    @app.callback(
        Output('group-dropdown', 'options'),
        Input('group-dropdown', 'id')
    )
    def populate_group(_):
        groups = sorted(data['Group'].dropna().unique())
        return [{'label': g, 'value': g} for g in groups]

    # Dropdown: Region
    @app.callback(
        Output('region-dropdown', 'options'),
        Input('group-dropdown', 'value')
    )
    def update_region(group):
        if group:
            regions = sorted(data[data['Group'] == group]['Region'].dropna().unique())
            return [{'label': r, 'value': r} for r in regions]
        return []

    # Dropdown: Instrument
    @app.callback(
        Output('instrument-dropdown', 'options'),
        Input('region-dropdown', 'value'),
        Input('group-dropdown', 'value')
    )
    def update_instrument(region, group):
        if group and region:
            instruments = sorted(data[
                (data['Group'] == group) &
                (data['Region'] == region)
            ]['InstrumentName'].dropna().unique())
            return [{'label': i, 'value': i} for i in instruments]
        return []

    # Dropdown: Month
    @app.callback(
        Output('month-dropdown', 'options'),
        Input('instrument-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('group-dropdown', 'value')
    )
    def update_month(instrument, region, group):
        if group and region and instrument:
            months = sorted(data[
                (data['Group'] == group) &
                (data['Region'] == region) &
                (data['InstrumentName'] == instrument)
            ]['Month'].dropna().unique())
            return [{'label': m, 'value': m} for m in months]
        return []

    # Callback for seasonal chart and histogram
    @app.callback(
        Output('spread-figure', 'figure'),
        Output('spread-histogram', 'figure'),
        Input('group-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('instrument-dropdown', 'value'),
        Input('month-dropdown', 'value')
    )
    def update_figure(group, region, instrument, month):
        filtered_df = data[
            (data['Group'] == group) &
            (data['Region'] == region) &
            (data['InstrumentName'] == instrument) &
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
            next_month_start = (last_hist_trade + pd.offsets.MonthBegin(1)).normalize()
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
                line=dict(color="white" if label == "Current" else None,
                          width=3 if label == "Current" else 1.5),
                opacity=1.0 if label == "Current" else 0.6
            ))

        fig.update_layout(
            title="Seasonal Spread by Year",
            xaxis_title="Trading Day (1 to 252)",
            yaxis_title="Spread",
            margin=dict(l=40, r=40, t=60, b=40),
            legend_title="Season",
            template='plotly_dark'
        )

        hist_fig = go.Figure()
        if not filtered_df.empty and 'spread' in filtered_df.columns:
            hist_fig.add_trace(go.Histogram(
                x=filtered_df["spread"],
                marker_color='lightblue',
                nbinsx=50
            ))

        hist_fig.update_layout(
            title="Distribution of Spread (Histogram)",
            xaxis_title="Spread",
            yaxis_title="Frequency",
            template="plotly_dark",
            margin=dict(l=40, r=40, t=60, b=40)
        )

        return fig, hist_fig

    # DataTable: Filtered Data Preview
    @app.callback(
        Output('data-preview', 'data'),
        Output('data-preview', 'columns'),
        Input('group-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('instrument-dropdown', 'value'),
        Input('month-dropdown', 'value')
    )
    def update_table(group, region, instrument, month):
        filtered_df = data[
            (data['Group'] == group) &
            (data['Region'] == region) &
            (data['InstrumentName'] == instrument) &
            (data['Month'] == month)
        ].copy()

        filtered_df = filtered_df.sort_values("Date")
        filtered_df["LastTrade"] = pd.to_datetime(filtered_df["LastTrade"], errors="coerce")
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors="coerce")
        filtered_df["Year"] = filtered_df["Date"].dt.year

        if filtered_df.empty:
            return [], []

        columns = [{"name": i, "id": i} for i in filtered_df.columns]
        return filtered_df.to_dict("records"), columns
