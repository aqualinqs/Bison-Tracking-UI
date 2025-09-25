# app.py
import dash
from dash import dcc, html
import plotly.graph_objects as go

# Assuming the stream manager and data handling is in a separate module
# from rtsp_bison_tracker_2 import StreamManager, create_handler

# --- Function to simulate real-time data from your Python script ---
def get_live_data():
    """Fetches data from your data source (e.g., a file, a Flask endpoint, or a WebSocket)."""
    # Replace this with a call to your real-time data source
    # For now, let's use dummy data
    data = {
        'live_detections': 5,
        'total_detections': 120,
        'avg_detections_per_min': 8.5,
        'inflow': 3,
        'outflow': 1,
        'graph_data': [
            {'time': 1, 'detections': 10},
            {'time': 2, 'detections': 15},
            {'time': 3, 'detections': 12},
            {'time': 4, 'detections': 20},
        ]
    }
    return data

# --- Initialize the Dash App ---
app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])

# --- App Layout ---
app.layout = html.Div(
    className="flex flex-col lg:flex-row h-screen bg-gray-100 p-4",
    children=[
        # Left Panel (Video Feed and Stats)
        html.Div(
            className="flex-1 bg-white rounded-lg shadow-lg p-6 flex flex-col items-center",
            children=[
                # Video placeholder
                html.Div(
                    className="w-full h-auto bg-gray-800 rounded-lg overflow-hidden",
                    children=[
                        # Replace with a video component that can display the RTSP stream (e.g., using a a `<video>` tag or a JavaScript library)
                        html.Img(src="https://via.placeholder.com/1280x720.png?text=Live+Video+Feed", className="w-full"),
                    ]
                ),

                # Stat Cards
                html.Div(
                    className="grid grid-cols-2 gap-4 mt-6 w-full",
                    children=[
                        html.Div(className="bg-gray-200 rounded-lg p-4 text-center", children=[html.P("Live Detections"), html.H2(id="live-detections", className="text-3xl font-bold text-blue-600")]),
                        html.Div(className="bg-gray-200 rounded-lg p-4 text-center", children=[html.P("Total Detections"), html.H2(id="total-detections", className="text-3xl font-bold text-blue-600")]),
                        html.Div(className="bg-gray-200 rounded-lg p-4 text-center", children=[html.P("Avg Detections/Min"), html.H2(id="avg-detections", className="text-3xl font-bold text-blue-600")]),
                        html.Div(className="bg-gray-200 rounded-lg p-4 text-center", children=[html.P("Inflow/Outflow"), html.H2(id="inflow-outflow", className="text-3xl font-bold text-blue-600")]),
                    ]
                ),
            ]
        ),

        # Right Panel (Summary Report)
        html.Div(
            className="w-full lg:w-1/4 bg-white rounded-lg shadow-lg p-6 mt-4 lg:mt-0 lg:ml-4",
            children=[
                html.H3("Summary Report", className="text-xl font-bold mb-4"),
                dcc.Graph(
                    id='detections-graph',
                    className="mb-4",
                    config={'displayModeBar': False}
                ),
                # Add more summary report elements here
            ]
        ),

        # Interval component to refresh data
        dcc.Interval(
            id='interval-component',
            interval=1000,  # in milliseconds
            n_intervals=0
        ),
    ]
)

# --- Callbacks to update the dashboard with live data ---
@app.callback(
    [
        dash.Output('live-detections', 'children'),
        dash.Output('total-detections', 'children'),
        dash.Output('avg-detections', 'children'),
        dash.Output('inflow-outflow', 'children'),
        dash.Output('detections-graph', 'figure'),
    ],
    [dash.Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    data = get_live_data()

    # Create a line graph using Plotly
    fig = go.Figure(data=go.Scatter(x=[d['time'] for d in data['graph_data']], y=[d['detections'] for d in data['graph_data']], mode='lines+markers'))
    fig.update_layout(title='Detections Over Time', xaxis_title='Time', yaxis_title='Detections')

    return (
        data['live_detections'],
        data['total_detections'],
        f"{data['avg_detections_per_min']:.1f}",
        f"{data['inflow']}/{data['outflow']}",
        fig
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)
