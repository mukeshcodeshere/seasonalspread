import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# Sample data
np.random.seed(0)
dates = pd.date_range(start='2023-01-01', periods=100)

datasets = {
    "Dataset A": np.cumsum(np.random.randn(100)),
    "Dataset B": np.cumsum(np.random.randn(100) * 0.5),
    "Dataset C": np.cumsum(np.random.randn(100) * 2),
}

# Dash app setup
app = dash.Dash(__name__)
app.title = "Simple Demo Dash App"

# Expose the server for Gunicorn/Azure
server = app.server

app.layout = html.Div([
    html.H1("Simple Dash Line Chart Demo"),
    
    dcc.Dropdown(
        id='dataset-dropdown',
        options=[{'label': name, 'value': name} for name in datasets.keys()],
        value='Dataset A'
    ),
    
    dcc.Graph(id='line-chart')
])

@app.callback(
    Output('line-chart', 'figure'),
    Input('dataset-dropdown', 'value')
)
def update_chart(selected_dataset):
    y_data = datasets[selected_dataset]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=y_data,
        mode='lines+markers',
        name=selected_dataset
    ))
    fig.update_layout(title=f"Line Chart: {selected_dataset}", xaxis_title="Date", yaxis_title="Value")
    return fig

if __name__ == '__main__':
    app.run(debug=True)
