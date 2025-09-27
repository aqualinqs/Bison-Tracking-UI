import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import datetime
import random
import json

# --- 1. CONFIGURATION AND ASSUMPTIONS ---

# Base URL for the services provided by rtsp_bison_tracker_2.py
# Assuming the user is running the Python script on localhost:8080
STATS_URL = "http://localhost:8080/stats"
API_BASE_URL = "http://localhost:8080"
MJPEG_URL = "http://localhost:8080/mjpeg"

# Note on Tailwind: This Dash application uses Tailwind CSS class names
# in the 'className' property. For these classes to render correctly,
# it is assumed that the environment running Dash has a method for
# compiling/processing Tailwind (e.g., using dash-tailwindcss-components
# or a custom setup). We are applying the classes directly for maximum fidelity.

# --- 2. SIMULATED REAL-TIME DATA GENERATION ---

# Initialize global state for persistence
current_stats = {
    "total_frames": 10000,
    "total_detections": 350,
    "fps": 24.0,
    "max_bison_in_frame": 8,
    "avg_confidence": 0.85,
    "class_counts": {"bison": 8, "elk": 2, "moose": 1, "car": 0},
    "bison_count_history": [5, 6, 8, 7, 9, 8, 10, 12],
    "timestamp_history": [
        (datetime.datetime.now() - datetime.timedelta(minutes=i)).strftime('%H:%M:%S')
        for i in range(8)
    ][::-1],
}

def generate_simulated_stats():
    """Generates new simulated data for the dashboard update."""
    global current_stats
    
    # Update KPIs based on the previous state
    current_stats["total_frames"] += random.randint(50, 150)
    current_stats["total_detections"] += random.randint(5, 20)
    current_stats["fps"] = round(random.uniform(23.5, 26.5), 1)
    current_stats["max_bison_in_frame"] = random.randint(5, 15)
    current_stats["avg_confidence"] = round(random.uniform(0.80, 0.99), 3)
    current_stats["timestamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Update counts and history
    new_bison_count = random.randint(7, 13)
    current_stats["class_counts"]["bison"] = new_bison_count
    current_stats["class_counts"]["elk"] = random.randint(0, 3)
    current_stats["class_counts"]["moose"] = random.randint(0, 1)
    current_stats["class_counts"]["car"] = random.randint(0, 1)

    # Rolling history update (Max 10 points for a clean chart)
    current_stats["bison_count_history"].append(new_bison_count)
    if len(current_stats["bison_count_history"]) > 10:
        current_stats["bison_count_history"].pop(0)
    
    new_timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    current_stats["timestamp_history"].append(new_timestamp)
    if len(current_stats["timestamp_history"]) > 10:
        current_stats["timestamp_history"].pop(0)

    # Simulated Hotspot Data (20x20 grid, random values)
    current_stats["hotspot_data"] = [[random.uniform(0, 1) for _ in range(20)] for _ in range(20)]

    return current_stats

# --- 3. HELPER COMPONENTS ---

def create_kpi_card(title, value, unit="", icon_class=""):
    """Creates a standardized KPI card component."""
    return html.Div(
        className="card p-4 shadow-xl flex flex-col justify-center items-center h-full",
        children=[
            html.Div(className=f"text-4xl text-purple-400 {icon_class}"),
            html.Div(
                className="text-4xl font-extrabold mt-2 text-white",
                id=f"kpi-{title.lower().replace(' ', '_')}",
                children=[f"{value:.1f}" if isinstance(value, float) else f"{value}"],
            ),
            html.Div(className="text-sm uppercase tracking-wider text-gray-400 mt-1", children=title),
        ],
    )

# --- 4. PAGE LAYOUTS ---

def get_page_layout_overview(data):
    """Layout for the main / page (Overview and Behavioral Analysis)."""
    
    # 1. Class Detections Bar Chart
    classes = list(data["class_counts"].keys())
    counts = list(data["class_counts"].values())
    fig_classes = px.bar(
        x=classes, y=counts,
        title='Last Frame Class Detections',
        labels={'x': 'Class', 'y': 'Count'},
        color=classes,
        color_discrete_map={"bison": "#9333ea", "elk": "#f97316", "moose": "#10b981", "car": "#3b82f6"},
        template="plotly_dark",
    )
    fig_classes.update_layout(
        plot_bgcolor="#2a2438", paper_bgcolor="#2a2438", font_color="#e6edf3",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis={'showgrid': False},
        yaxis={'showgrid': True, 'gridcolor': '#3f3a53'},
    )
    fig_classes.update_traces(marker_line_width=0, opacity=0.8)

    # 2. Bison Count Trend Line Chart
    fig_trend = px.line(
        x=data["timestamp_history"], y=data["bison_count_history"],
        title='Bison Count Trend (Last 10 Updates)',
        labels={'x': 'Time', 'y': 'Bison Count'},
        template="plotly_dark",
    )
    fig_trend.update_traces(mode='lines+markers', line=dict(color="#9333ea", width=3), marker=dict(size=8, color='white', line=dict(width=2, color="#9333ea")))
    fig_trend.update_layout(
        plot_bgcolor="#2a2438", paper_bgcolor="#2a2438", font_color="#e6edf3",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis={'showgrid': True, 'gridcolor': '#3f3a53'},
        yaxis={'showgrid': True, 'gridcolor': '#3f3a53', 'rangemode':'tozero'},
    )

    # 3. Behavioral Analysis (Hotspot Map Placeholder)
    fig_hotspot = go.Figure(data=go.Heatmap(
        z=data["hotspot_data"],
        colorscale='Viridis',
        zmin=0, zmax=1
    ))
    fig_hotspot.update_layout(
        title='Bison Activity Hotspot (Simulated)',
        plot_bgcolor="#2a2438", paper_bgcolor="#2a2438", font_color="#e6edf3",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis={'showgrid': False, 'zeroline': False, 'tickvals': [], 'title': 'Grid X'},
        yaxis={'showgrid': False, 'zeroline': False, 'tickvals': [], 'title': 'Grid Y'},
    )


    return html.Div(className="p-6", children=[
        # --- Live Stats Section (KPI Cards) ---
        html.Div(className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6", children=[
            create_kpi_card("Current FPS", data["fps"], icon_class="fa-gauge-high"),
            create_kpi_card("Max Bison (Frame)", data["max_bison_in_frame"], icon_class="fa-cow"),
            create_kpi_card("Total Detections", data["total_detections"], icon_class="fa-bullseye"),
            create_kpi_card("Avg Confidence", data["avg_confidence"], icon_class="fa-check-double"),
        ]),

        # --- Chart Row 1: Detections and Trend ---
        html.Div(className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6", children=[
            html.Div(className="card p-4 shadow-xl", children=[
                dcc.Graph(id='class-detections-chart', figure=fig_classes, config={'displayModeBar': False})
            ]),
            html.Div(className="card p-4 shadow-xl", children=[
                dcc.Graph(id='bison-count-trend', figure=fig_trend, config={'displayModeBar': False})
            ]),
        ]),

        # --- Chart Row 2: Behavioral Analysis ---
        html.Div(className="grid grid-cols-1 gap-6", children=[
            html.Div(className="card p-4 shadow-xl", children=[
                dcc.Graph(id='hotspot-map', figure=fig_hotspot, config={'displayModeBar': False})
            ]),
        ]),
    ])

def get_page_layout_streams(data):
    """Layout for the /streams page (Live Video Feed)."""
    return html.Div(className="p-6", children=[
        html.H3("Live Video Streams", className="text-2xl font-bold mb-4 text-white"),
        
        # Stream Section
        html.Div(className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6", children=[
            # MJPEG Stream
            html.Div(className="card p-4 shadow-xl", children=[
                html.H4("MJPEG Stream (Low Latency)", className="text-xl font-semibold mb-2 text-white"),
                html.P("Updates every frame. Requires active connection to server.", className="text-gray-400 text-sm mb-2"),
                html.Img(
                    src=f"{API_BASE_URL}/mjpeg", 
                    className="w-full h-auto rounded-lg border border-purple-500", 
                    alt="MJPEG Live Feed"
                ),
            ]),
            # HLS Stream
            html.Div(className="card p-4 shadow-xl", children=[
                html.H4("HLS Stream (High Compatibility)", className="text-xl font-semibold mb-2 text-white"),
                html.P("Higher latency, but better for mobile/slow networks (uses HLS.js or native player).", className="text-gray-400 text-sm mb-2"),
                html.Video(
                    id='hlsVideo',
                    src=f"{API_BASE_URL}/hls.m3u8",
                    controls=True, 
                    autoPlay=True, 
                    muted=True, 
                    className="w-full h-auto rounded-lg bg-black",
                    # NOTE: In a real-world scenario, you'd need the HLS.js library loaded,
                    # which is complex in pure Dash, but we include the URL based on the HTML provided.
                ),
            ]),
        ]),
        
        # Live Stats (Duplicated from Overview for quick reference)
        html.H3("Current Stream Metrics", className="text-2xl font-bold mb-4 mt-6 text-white"),
        html.Div(className="grid grid-cols-1 md:grid-cols-4 gap-4", children=[
            create_kpi_card("Current FPS", data["fps"], icon_class="fa-video"),
            create_kpi_card("Last Update", data["timestamp"], icon_class="fa-clock"),
            create_kpi_card("Total Frames", data["total_frames"], icon_class="fa-infinity"),
            create_kpi_card("Total Detections", data["total_detections"], icon_class="fa-binoculars"),
        ]),
    ])

def get_page_layout_trends(data):
    """Layout for the /trends page (Historical Data and Reporting)."""
    
    # Simple aggregation of detection history over time (using current_stats history)
    fig_detections = px.line(
        x=data["timestamp_history"], y=data["bison_count_history"],
        title='Historical Bison Density Trend',
        labels={'x': 'Time', 'y': 'Bison Count (Per Frame)'},
        template="plotly_dark",
    )
    fig_detections.update_traces(mode='lines+markers', line=dict(color="#10b981", width=3), marker=dict(size=8, color='white', line=dict(width=2, color="#10b981")))
    fig_detections.update_layout(
        plot_bgcolor="#2a2438", paper_bgcolor="#2a2438", font_color="#e6edf3",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis={'showgrid': True, 'gridcolor': '#3f3a53'},
        yaxis={'showgrid': True, 'gridcolor': '#3f3a53', 'rangemode':'tozero'},
    )
    
    # Aggregated Class Distribution (Pie Chart)
    class_labels = list(data["class_counts"].keys())
    class_values = list(data["class_counts"].values())
    fig_pie = go.Figure(data=[go.Pie(
        labels=class_labels, values=class_values,
        pull=[0.05 if label == 'bison' else 0 for label in class_labels],
        hole=.3
    )])
    fig_pie.update_traces(
        marker=dict(colors=["#9333ea", "#f97316", "#10b981", "#3b82f6"]),
        hoverinfo='label+percent', textinfo='value'
    )
    fig_pie.update_layout(
        title='Current Class Distribution',
        plot_bgcolor="#2a2438", paper_bgcolor="#2a2438", font_color="#e6edf3",
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

    return html.Div(className="p-6", children=[
        html.H3("Historical & Aggregated Data", className="text-2xl font-bold mb-4 text-white"),
        
        # Chart Row 1
        html.Div(className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6", children=[
            html.Div(className="card p-4 shadow-xl", children=[
                dcc.Graph(id='historical-density-chart', figure=fig_detections, config={'displayModeBar': False})
            ]),
            html.Div(className="card p-4 shadow-xl", children=[
                dcc.Graph(id='class-distribution-pie', figure=fig_pie, config={'displayModeBar': False})
            ]),
        ]),
        
        # Reporting/Action Button
        html.Div(className="flex justify-end mt-6", children=[
            html.Button(
                "Download Full Data Report (PDF)", 
                id="btn-pdf-download",
                n_clicks=0,
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-6 rounded-xl transition duration-300 shadow-lg flex items-center"
            )
        ]),
    ])


# --- 5. DASH APPLICATION SETUP ---

app = dash.Dash(
    __name__, 
    external_scripts=['https://cdn.tailwindcss.com', 'https://kit.fontawesome.com/a076d05399.js'],
    external_stylesheets=['https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap'],
    suppress_callback_exceptions=True
)

# Sidebar Navigation Component
sidebar = html.Aside(
    className="sidebar w-64 p-4 flex flex-col h-full bg-[#1c1e2b] text-[#e6edf3]",
    children=[
        html.H2(
            "Bison Guard Tracker", 
            className="text-3xl font-extrabold text-white mb-6 border-b border-purple-500 pb-2"
        ),
        dcc.Link(
            html.Div("Dashboard Overview", className="p-3 my-2 rounded-lg hover:bg-purple-600 hover:text-white transition duration-200 cursor-pointer"),
            href='/', className="no-underline text-[#e6edf3]"
        ),
        dcc.Link(
            html.Div("Live Streams", className="p-3 my-2 rounded-lg hover:bg-purple-600 hover:text-white transition duration-200 cursor-pointer"),
            href='/streams', className="no-underline text-[#e6edf3]"
        ),
        dcc.Link(
            html.Div("Historical Trends", className="p-3 my-2 rounded-lg hover:bg-purple-600 hover:text-white transition duration-200 cursor-pointer"),
            href='/trends', className="no-underline text-[#e6edf3]"
        ),
        html.Div(className="flex-grow"),
        html.Div("Data last fetched: ", id="last-update-time", className="text-xs text-gray-500")
    ]
)

# Main Application Layout
app.layout = html.Div(
    className="flex h-screen bg-[#000000] font-['Inter']",
    children=[
        # 1. Sidebar
        sidebar,

        # 2. Main Content
        html.Main(
            id="page-content",
            className="flex-grow overflow-y-auto w-full",
            children=[
                dcc.Location(id='url', refresh=False),
                html.Div(id='page-layout'),
            ]
        ),
        
        # 3. Interval for Real-Time Updates (5-second interval)
        dcc.Interval(
            id='interval-component',
            interval=5*1000,  # in milliseconds
            n_intervals=0
        ),
        
        # 4. Hidden Div to store and trigger data updates across pages
        html.Div(id='data-storage', style={'display': 'none'}, children=json.dumps(generate_simulated_stats())),
    ]
)

# --- 6. CALLBACKS ---

# Callback 1: Real-Time Data Update
@app.callback(
    Output('data-storage', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_data(n):
    """Fetches/simulates new data on a fixed interval and stores it."""
    new_data = generate_simulated_stats()
    return json.dumps(new_data)

# Callback 2: Routing/Page Switching
@app.callback(
    Output('page-layout', 'children'),
    [Input('url', 'pathname'),
     Input('data-storage', 'children')]
)
def render_page(pathname, data_json):
    """Renders the correct page layout based on the URL and uses the latest data."""
    if not data_json:
        return html.Div("Loading data...", className="text-white p-10")
        
    data = json.loads(data_json)
    
    if pathname == '/streams':
        return get_page_layout_streams(data)
    elif pathname == '/trends':
        return get_page_layout_trends(data)
    elif pathname == '/':
        return get_page_layout_overview(data)
        
    # Default/404 Page
    return html.Div(
        className="p-10 text-white",
        children=[
            html.H1("404: Page Not Found", className="text-4xl text-red-500"),
            html.P(f"The path '{pathname}' does not exist.")
        ]
    )

# Callback 3: Update KPI Cards and Last Update Time (Universal Data Display)
@app.callback(
    [Output('kpi-current_fps', 'children'),
     Output('kpi-max_bison_in_frame', 'children'),
     Output('kpi-total_detections', 'children'),
     Output('kpi-avg_confidence', 'children'),
     Output('last-update-time', 'children')],
    [Input('data-storage', 'children')]
)
def update_kpi_and_time(data_json):
    """Updates the KPIs and the last update time, which are shared across all pages."""
    if not data_json:
        return [dash.no_update] * 5

    data = json.loads(data_json)

    # Format the KPI values
    fps = f"{data['fps']:.1f}"
    max_bison = f"{data['max_bison_in_frame']}"
    total_detections = f"{data['total_detections']}"
    avg_confidence = f"{data['avg_confidence']:.3f}"
    last_update = f"Data last fetched: {data['timestamp'].split(' ')[1]}"

    return fps, max_bison, total_detections, avg_confidence, last_update


# Callback 4: Live Updates for the Overview Charts (re-renders the page layout for efficiency)
@app.callback(
    Output('page-layout', 'children', allow_duplicate=True),
    [Input('data-storage', 'children'),
     State('url', 'pathname')],
     prevent_initial_call=True
)
def update_current_page_charts(data_json, pathname):
    """Triggers re-render of the current page's charts when data updates."""
    if not data_json:
        return dash.no_update
    
    data = json.loads(data_json)
    
    # Only update the layout if we are on one of the main dashboard pages
    if pathname == '/':
        return get_page_layout_overview(data)
    elif pathname == '/streams':
        return get_page_layout_streams(data)
    elif pathname == '/trends':
        return get_page_layout_trends(data)
        
    return dash.no_update


if __name__ == '__main__':
    # Setting the host to '0.0.0.0' allows access from outside the container/environment
    # Running on port 8050, the default DASH port.
    print("\n" + "="*80)
    print("      DASHBOARD READY: Navigate to http://localhost:8050 in your browser.")
    print("      Ensure your backend tracker (rtsp_bison_tracker_2.py) is running on port 8080.")
    print("="*80 + "\n")
    app.run(debug=True, host='0.0.0.0', port=8050)




