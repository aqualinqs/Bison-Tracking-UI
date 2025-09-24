import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import requests
import datetime

# The URL for your bison tracker's stats endpoint
STATS_URL = "http://localhost:8080/stats"

# Initialize the Dash app
app = dash.Dash(__name__)

# Initial data for the graph
graph_data = {'x': [], 'y': []}

app.layout = html.Div([
    html.H1("Real-Time Bison Tracking Dashboard", style={'textAlign': 'center'}),
    html.Div(id='live-update-text', style={'fontSize': '24px', 'textAlign': 'center'}),
    dcc.Graph(id='live-update-graph'),

    # This component triggers a callback every 1 second
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    Output('live-update-graph', 'figure'),
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    try:
        response = requests.get(STATS_URL)
        data = response.json()
        bison_count = data.get('total_bisons', 0)
        timestamp = data.get('timestamp', str(datetime.datetime.now()))
        
        # Append new data to the graph
        graph_data['x'].append(datetime.datetime.now())
        graph_data['y'].append(bison_count)

        # Create the Plotly figure
        fig = go.Figure(
            data=[go.Scatter(
                x=list(graph_data['x']),
                y=list(graph_data['y']),
                mode='lines+markers'
            )]
        )
        fig.update_layout(
            title='Bison Count Over Time',
            xaxis_title='Time',
            yaxis_title='Bison Count'
        )

        return fig, f"Current Bison Count: {bison_count}"
    except requests.exceptions.ConnectionError:
        return dash.no_update, "Error: Could not connect to the bison tracker server."

if __name__ == '__main__':
    app.run_server(debug=True)