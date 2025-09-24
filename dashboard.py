import requests
import plotly.graph_objects as go
from nicegui import ui
import datetime

STATS_URL = "http://localhost:8080/stats"
graph_data = {'x': [], 'y': []}

# Use a refreshable function to contain the dynamic UI elements
@ui.refreshable
def bison_dashboard():
    try:
        response = requests.get(STATS_URL)
        data = response.json()
        bison_count = data.get('total_bisons', 0)
        
        # Append new data
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
        
        ui.label(f"Current Bison Count: {bison_count}").classes('text-2xl font-bold')
        ui.plotly(fig).classes('w-full h-96')

    except requests.exceptions.ConnectionError:
        ui.label("Error: Could not connect to the bison tracker server.").classes('text-red-500')

# Start the dashboard UI and a timer to refresh it
ui.label("Bison Analytics Dashboard").classes('text-3xl font-bold p-4')
bison_dashboard()
ui.timer(1.0, bison_dashboard.refresh)

ui.run(port=8000)