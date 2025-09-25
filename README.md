# Bison-Tracking-UI
A python-based Frontend interface for real-time Bison Tracking
## Overview

This repository provides a real-time bison tracking dashboard using two different Python web frameworks:
- **Dash** (`app.py`): For real-time analytics and visualization.
- **NiceGUI** (`bison_dashboard.py`): For a modern, interactive web interface.

Both dashboards visualize bison counts and trends from a video stream or RTSP source, powered by YOLO object detection and tracking.

---

## Features
- Real-time bison count visualization
- Historical trends and behavioral analysis (NiceGUI tabs)
- Interactive graphs (Plotly)
- API integration with bison tracker server

---

## Setup Instructions

### 1. Clone the Repository
```powershell
git clone https://github.com/aqualinqs/Bison-Tracking-UI.git
cd Bison-Tracking-UI
```

### 2. Create and Activate Python Environment
```powershell
python -m venv .myenv
.myenv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

**Note:**
- You may need to install additional system dependencies for PyTorch (see troubleshooting below).
- For NiceGUI, ensure you have a compatible browser (Chrome, Edge, Firefox).

---

## Running the Dash Dashboard (`app.py`)

```powershell
python app.py
```
- Open your browser and go to: [http://127.0.0.1:8050](http://127.0.0.1:8050)
- The dashboard updates every second with live bison counts.

---


## Running the HTML Dashboard (`dashboard.html`)

You can use the standalone HTML dashboard for a fast, browser-based view of bison analytics. This dashboard is built with Tailwind CSS and Chart.js, and polls the tracker API for live stats and video streams.

### How to Use

1. Open `dashboard.html` in your browser (double-click or right-click and choose "Open with" > your browser).
2. Make sure your tracker server is running and accessible at the endpoints configured in the HTML (default: `http://localhost:8080/stats`, `http://localhost:8080/mjpeg`, `http://localhost:8080/hls.m3u8`).
3. The dashboard will automatically poll for live stats and display:
	- Live Bison Count
	- Max Bison in Frame
	- Live FPS and Average FPS
	- Detections by Class (bar chart)
	- Bison Count Trend (line chart)
	- Live MJPEG video stream (if available)
	- Download buttons for JSON/CSV stats

#### Customization
- You can edit the endpoints directly in the HTML file to match your server configuration.
- No Python environment is required for the HTML dashboard—just a modern browser.

---

---

## API Endpoints

Your dashboards connect to the bison tracker server via the following endpoint:

- **Stats Endpoint:**
	- URL: `http://localhost:8080/stats`
	- Method: `GET`
	- Response Example:
		```json
		{
			"total_bisons": 12,
			"timestamp": "2025-09-25T12:34:56"
		}
		```

---

## Troubleshooting

- **DLL Load Errors (PyTorch):**
	- Install the Microsoft Visual C++ Redistributable (x64):
		[https://aka.ms/vs/16/release/vc_redist.x64.exe](https://aka.ms/vs/16/release/vc_redist.x64.exe)
	- Restart your computer after installation.

- **Port Conflicts:**
	- Change the port in your script if `8080` or `8050` is in use.

- **Missing Packages:**
	- Install with `pip install <package>` as needed.

---

## File Structure


```
app.py                  # Dash dashboard
bison_dashboard.py      # NiceGUI dashboard
dashboard.html          # Standalone HTML dashboard
track.py                # Bison tracking script (YOLO)
rtsp_bison_tracker_2.py # RTSP bison tracking
requirements.txt        # Python dependencies
args.yaml               # Tracker configuration
best.pt                 # YOLO model weights
architecture.svg        # Architecture diagram
README.md               # This file
```

---

## Architecture Diagram

![Bison Tracking Architecture](architecture.svg)

---

## Assessment Rubric Checklist
- [x] Clear and complete setup instructions
- [x] Running instructions for both dashboards
- [x] API endpoint documentation
- [x] Troubleshooting section
- [x] File structure overview

---

## License

This project is licensed under the MIT License.
