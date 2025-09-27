import datetime
import random
import time
from nicegui import ui, app
import plotly.graph_objects as go
from collections import deque
import json

# --- 1. CONFIGURATION AND MOCK DATA STORE ---
# NOTE: In a real application, the data would be fetched from an external API (e.g., http://localhost:8080/stats)
# As the backend is not running, we mock the real-time data changes.

MAX_HISTORY_POINTS = 50
live_data = {
    'total_bisons': 0,
    'total_detections': 0,
    'avg_confidence': 0.0,
    'fps': 0.0,
    'stream_status': 'Connecting...',
    'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'detection_counts': {'bison': 0, 'deer': 0, 'elk': 0, 'other': 0}
}
history_data = deque(maxlen=MAX_HISTORY_POINTS)
bison_count_trace = deque(maxlen=MAX_HISTORY_POINTS)
# Mock data for Behavioural Analytics (Hotspot/Tracking history)
mock_tracking_history = {
    "bison_id_101": [
        {"time": "09:00:00", "location": "(150, 200)", "activity": "Grazing"},
        {"time": "09:05:00", "location": "(155, 205)", "activity": "Grazing"},
        {"time": "09:10:00", "location": "(160, 210)", "activity": "Walking"},
    ],
    "bison_id_102": [
        {"time": "09:01:00", "location": "(300, 450)", "activity": "Resting"},
        {"time": "09:06:00", "location": "(300, 450)", "activity": "Resting"},
        {"time": "09:11:00", "location": "(310, 455)", "activity": "Grazing"},
    ]
}

# --- 2. DATA GENERATION AND MOCK API CALLS ---
def generate_mock_data():
    """Simulates fetching real-time data from the tracker's API."""
    now = datetime.datetime.now()
    
    # 1. Update live data (random walk for bison count)
    current_count = live_data['total_bisons']
    delta = random.randint(-1, 2)
    new_count = max(0, current_count + delta)
    
    live_data['total_bisons'] = new_count
    live_data['total_detections'] += random.randint(5, 15)
    live_data['avg_confidence'] = round(random.uniform(0.75, 0.99), 3)
    live_data['fps'] = round(random.uniform(20.0, 30.0), 1)
    live_data['stream_status'] = 'LIVE'
    live_data['last_updated'] = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # Randomly update detection counts for the bar chart
    live_data['detection_counts']['bison'] = new_count
    live_data['detection_counts']['deer'] = random.randint(0, 5)
    live_data['detection_counts']['elk'] = random.randint(0, 3)
    live_data['detection_counts']['other'] = random.randint(0, 10)

    # 2. Update historical data (for charts and tables)
    history_data.append({
        'timestamp': now.strftime('%H:%M:%S'),
        'total_bisons': new_count,
        'fps': live_data['fps'],
        'detections': live_data['total_detections'],
    })
    bison_count_trace.append((now, new_count))

# --- 3. UI COMPONENTS ---
# --- THEME FUNCTIONS ---

def toggle_dark_mode(is_dark: bool):
    """
    Toggles dark mode for the application and saves the preference to user storage.
    """
    # Save preference to user storage
    app.storage.user['dark_mode'] = is_dark
    # Apply the theme change
    ui.dark_mode(is_dark)
    # Refresh the dashboard content to update the Plotly chart theme
    #bison_dashboard.refresh()


# Shared sidebar layout
def shared_sidebar():
    """Creates the navigation sidebar."""
    with ui.left_drawer(value=True).classes('bg-[#1c1e2b] text-white p-4 w-64'):
        with ui.row().classes('items-center mb-6'):
            ui.icon('pets', size='lg').classes('text-green-600 dark:text-green-400')
            ui.label('Bison Guard Tracker').classes('text-2xl font-bold text-purple-400 dark:text-white')
            ui.separator()
                
        # with ui.column().classes('gap-6'):
        #     ui.label('Bison Guard Tracker').classes('text-2xl font-bold text-purple-400')
            
            # Navigation links using NiceGUI routing
            ui.link('Dashboard Overview', '/').classes('no-underline text-lg w-full px-3 py-2 rounded-lg hover:bg-[#3a354f] transition-colors')
            ui.link('Behaviour Analytics', '/analytics').classes('no-underline text-lg w-full px-3 py-2 rounded-lg hover:bg-[#3a354f] transition-colors')
            ui.link('Historical Trends', '/trends').classes('no-underline text-lg w-full px-3 py-2 rounded-lg hover:bg-[#3a354f] transition-colors')
            ui.separator()
            ui.label('Status').classes('text-sm font-semibold uppercase text-gray-400')
            ui.label().bind_text_from(live_data, 'stream_status', backward=lambda x: f"Stream: {x}").classes('text-sm text-green-400')
            ui.label().bind_text_from(live_data, 'last_updated', backward=lambda x: f"Last Update: {x}").classes('text-xs text-gray-500')

        # Spacer to push the toggle to the bottom
        ui.element('div').classes('flex-grow')
        
        # Light/Dark Mode Toggle at the bottom
        # Retrieve the current mode, default to True (Dark)
        # current_mode = app.storage.user.get('dark_mode', True)
        
        # with ui.row().classes('w-full justify-between items-center p-2 mt-4 border-t border-gray-300 dark:border-gray-700'):
        #     ui.icon('light_mode' if not current_mode else 'dark_mode').classes('text-xl text-gray-700 dark:text-gray-300')
        #     ui.label('Dark Mode').classes('text-gray-700 dark:text-gray-300')
            
            # The switch state is bound to the user storage key 'dark_mode'
            # The change is handled by the toggle_dark_mode function
            # ui.switch(value=current_mode, on_change=lambda e: toggle_dark_mode(e.value)).props('size="sm"').bind_value(app.storage.user, 'dark_mode')


def kpi_card(title: str, value_key: str, unit: str, color_class: str = 'text-purple-400'):
    """Creates a standard KPI card component."""
    with ui.card().classes('card shadow-xl w-full min-w-[200px] bg-gray-800/50'):
        ui.label(title).classes('text-sm font-semibold uppercase text-gray-400')
        with ui.row().classes('items-end mt-1'):
            ui.label().bind_text_from(live_data, value_key).classes(f'text-4xl font-extrabold {color_class}')
            ui.label(unit).classes('text-lg font-light text-gray-500 mb-1 ml-1')

def render_detection_chart():
    """Renders the real-time detections bar chart using ECharts."""
    categories = list(live_data['detection_counts'].keys())
    counts = list(live_data['detection_counts'].values())

    option = {
        'xAxis': {
            'type': 'category',
            'data': categories,
            'axisLabel': {'color': '#e5e7eb'},
            'axisLine': {'lineStyle': {'color': '#374151'}}
        },
        'yAxis': {
            'type': 'value',
            'axisLabel': {'color': '#e5e7eb'},
            'axisLine': {'lineStyle': {'color': '#374151'}},
            'splitLine': {'lineStyle': {'color': '#374151'}}
        },
        'series': [{
            'data': counts,
            'type': 'bar',
            'itemStyle': {
                'color': {
                    'type': 'linear',
                    'x': 0, 'y': 0, 'x2': 0, 'y2': 1,
                    'colorStops': [
                        {'offset': 0, 'color': '#a78bfa'},
                        {'offset': 0.33, 'color': '#fcd34d'},
                        {'offset': 0.66, 'color': '#34d399'},
                        {'offset': 1, 'color': '#f87171'}
                    ]
                }
            }
        }],
        'grid': {'left': '3%', 'right': '4%', 'bottom': '3%', 'containLabel': True},
        'backgroundColor': '#1c1e2b'
    }

    ui.echart(options=option).classes('w-full h-80 bg-gray-900 rounded-lg p-4')

def render_bison_count_plot():
    """Renders the Plotly line chart for Bison Count Trend."""
    
    x_data = [t[0] for t in bison_count_trace]
    y_data = [t[1] for t in bison_count_trace]

    fig = go.Figure(
        data=[go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            line={'color': '#a78bfa', 'width': 2},
            marker={'size': 8, 'symbol': 'circle', 'color': '#c4b5fd'},
        )]
    )
    fig.update_layout(
        title='Bison Count Over Time',
        xaxis_title='Time',
        yaxis_title='Bison Count',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': '#e5e7eb'},
        margin={'l': 40, 'r': 10, 't': 40, 'b': 40}
    )
    
    # Update axis to prevent Plotly from drawing the full date/time
    fig.update_xaxes(tickformat="%H:%M:%S")
    
    ui.plotly(fig).classes('w-full h-96')

# --- 4. NICEGUI PAGES ---

# Set up the custom dark theme
ui.page_title('Bison Guard Tracker')
ui.add_head_html('<style>body { background: #0f172a; color: #e2e8f0; font-family: Inter, sans-serif; }</style>')

# Refreshable component for dynamic data updates on all pages
@ui.refreshable
def dashboard_content(page_type: str):
    """This function is called by the timer and updates all dynamic elements."""
    # 1. Update KPI cards on Overview
    if page_type == '/':
        for key in ['total_bisons', 'fps', 'total_detections', 'avg_confidence']:
            # Force re-render of the elements bound to live_data (handled by ui.refreshable)
            pass 
        
        with ui.column().classes('w-full gap-6'):
            with ui.row().classes('w-full justify-around gap-6'):
                # Refresh KPI cards by simply calling the components again (NiceGUI handles diffing)
                kpi_card('Live Bison Count', 'total_bisons', 'Bisons', 'text-green-400')
                kpi_card('Processing FPS', 'fps', 'FPS', 'text-blue-400')
                kpi_card('Total Detections', 'total_detections', '', 'text-purple-400')
                kpi_card('Avg. Confidence', 'avg_confidence', '', 'text-yellow-400')
                
            with ui.grid(columns=2).classes('w-full gap-6'):
                with ui.card().classes('col-span-1 p-4 shadow-xl bg-gray-800/50'):
                    ui.label('Live Video Feed (RTSP Placeholder)').classes('text-xl font-semibold mb-2 text-purple-300')
                    # Placeholder for the live MJPEG stream from the tracker backend
                    # In a real setup, this would point to: http://localhost:8080/mjpeg
                    ui.html(f"""
                        <div class="relative w-full h-auto rounded-lg overflow-hidden shadow-2xl">
                            <img src="https://placehold.co/800x450/111827/e6edf3?text=Live+Video+Feed\\nSimulated+@+{live_data['last_updated']}" 
                                 class="w-full h-auto object-cover" alt="Live Video Feed Placeholder">
                            <div class="absolute bottom-0 right-0 p-2 bg-purple-700/80 text-white text-xs rounded-tl-lg">
                                Tracking LIVE
                            </div>
                        </div>
                    """).classes('w-full')
                
                with ui.card().classes('col-span-1 p-4 shadow-xl bg-gray-800/50'):
                    ui.label('Live Classification Counts').classes('text-xl font-semibold mb-2 text-purple-300')
                    # Re-render the chart with new data
                    render_detection_chart()

    # 2. Update Charts/Tables on Historical Trends
    elif page_type == '/trends':
        with ui.column().classes('w-full gap-6'):
            with ui.card().classes('w-full p-4 shadow-xl bg-gray-800/50'):
                ui.label('Bison Population Trend').classes('text-xl font-semibold mb-2 text-purple-300')
                render_bison_count_plot()

            with ui.card().classes('w-full p-4 shadow-xl bg-gray-800/50'):
                ui.label('Recent Tracking History').classes('text-xl font-semibold mb-2 text-purple-300')
                
                # Table for historical stats
                table_cols = [
                    {'name': 'timestamp', 'label': 'Time', 'field': 'timestamp', 'align': 'left'},
                    {'name': 'total_bisons', 'label': 'Bison Count', 'field': 'total_bisons', 'align': 'center'},
                    {'name': 'fps', 'label': 'FPS', 'field': 'fps', 'align': 'center'},
                    {'name': 'detections', 'label': 'Total Detections', 'field': 'detections', 'align': 'center'},
                ]
                # Use a reversed list for "Recent" history
                ui.table(columns=table_cols, rows=list(history_data)[::-1]).classes('w-full max-h-96 overflow-y-auto')
    
    # 3. Update Content on Behaviour Analytics
    elif page_type == '/analytics':
        with ui.column().classes('w-full gap-6'):
            ui.label('Bison Behavioural Analysis').classes('text-3xl font-bold text-purple-300')
            ui.label('Spatial and Temporal Hotspots (Simulated)').classes('text-xl font-semibold text-gray-400')
            
            with ui.card().classes('w-full p-4 shadow-xl bg-gray-800/50'):
                ui.label('Hotspot Map Placeholder').classes('text-lg font-semibold mb-2')
                # Placeholder for the visual heatmap (similar to the HTML's canvas element)
                ui.html(f"""
                    <div class="relative w-full h-80 rounded-lg overflow-hidden border border-purple-600/50 flex items-center justify-center bg-gray-900/50">
                        <span class="text-3xl text-purple-500/70 font-bold">Hotspot Map Visualization (Canvas Simulation)</span>
                        <div class="absolute top-4 left-4 text-xs bg-red-600 text-white px-2 py-1 rounded-full">
                            HIGH TRAFFIC ZONE
                        </div>
                    </div>
                """).classes('w-full')
            
            # Simulated Tracking History Drilldown
            with ui.card().classes('w-full p-4 shadow-xl bg-gray-800/50'):
                ui.label('Individual Bison Tracking History (JSON Drilldown)').classes('text-xl font-semibold mb-2 text-purple-300')
                ui.label("Click on a bison ID to view its detailed movement history.").classes('text-sm text-gray-400 mb-4')
                
                # Mock a list of trackable entities
                for bison_id in mock_tracking_history.keys():
                    with ui.row().classes('items-center justify-between w-full p-2 border-b border-gray-700 hover:bg-gray-700/50 cursor-pointer rounded-lg') \
                        .on('click', lambda bid=bison_id: open_history_modal(bid)):
                        ui.label(bison_id).classes('font-mono text-lg text-yellow-400')
                        ui.label('Click for Details').classes('text-sm text-purple-400')


def open_history_modal(bison_id: str):
    """Opens a dialog to show detailed tracking history for a specific bison."""
    history = mock_tracking_history.get(bison_id, [])
    
    with ui.dialog() as dialog, ui.card().classes('min-w-[400px] bg-gray-800'):
        ui.label(f'Tracking History for {bison_id}').classes('text-2xl font-bold text-purple-300 mb-4')
        
        # Display history in a table
        table_cols = [
            {'name': 'time', 'label': 'Time', 'field': 'time', 'align': 'left'},
            {'name': 'location', 'label': 'Location', 'field': 'location', 'align': 'left'},
            {'name': 'activity', 'label': 'Activity', 'field': 'activity', 'align': 'left'},
        ]
        ui.table(columns=table_cols, rows=history).classes('w-full max-h-96 overflow-y-auto')
        
        ui.button('Close', on_click=dialog.close).classes('mt-4 bg-purple-600 hover:bg-purple-700')
    
    dialog.open()
    
# --- PAGE DEFINITIONS ---

@ui.page('/')
def overview_page():
    shared_sidebar()
    with ui.column().classes('p-8 w-full'):
        ui.label('Detections Overview').classes('text-4xl font-extrabold text-white mb-6')
        dashboard_content('/')

@ui.page('/analytics')
def analytics_page():
    shared_sidebar()
    with ui.column().classes('p-8 w-full'):
        ui.label('Behaviour Analytics').classes('text-4xl font-extrabold text-white mb-6')
        dashboard_content('/analytics')

@ui.page('/trends')
def trends_page():
    shared_sidebar()
    with ui.column().classes('p-8 w-full'):
        ui.label('Historical Trends').classes('text-4xl font-extrabold text-white mb-6')
        dashboard_content('/trends')

# --- 5. INITIALIZATION AND LIVE REFRESH ---

# Initialize data and set up timer
generate_mock_data()
ui.timer(interval=2.0, callback=lambda: (generate_mock_data(), dashboard_content.refresh('/')))

# Run the NiceGUI app
ui.run(storage_secret='my_secret_key', dark=True, title='Bison Guard Tracker Dashboard', port=8000)
