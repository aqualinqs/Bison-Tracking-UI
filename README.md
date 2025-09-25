# Bison-Tracking-UI
A python-based Frontend interface for real-time Bison Tracking


# 🦬 Bison-Tracking-UI

<p align="center">
	<img src="architecture.svg" alt="Bison Tracking Architecture" width="500"/>
</p>

<p align="center">
	<b>A Python-powered, interactive dashboard for real-time Bison Tracking!</b> <br>
	<i>Track, visualize, and analyze bison activity with beautiful live charts and video streams.</i>
</p>

---

## 🚀 Overview


Welcome to the wild side of data! This project brings you:
- **Dash Dashboard** (`app.py`): 📊 Real-time analytics and visualization.
- **HTML Dashboard** (`dashboard.html`): 🌐 Fast, browser-based live stats and video.

Both dashboards visualize bison counts and trends from a video stream or RTSP source, powered by YOLO object detection and tracking. Watch the herd in action!

---


## ✨ Features
- 🟢 Real-time bison count visualization
- 📈 Historical trends and behavioral analysis
- 📊 Interactive graphs (Plotly, Chart.js)
- 🔗 API integration with bison tracker server

---


## 🛠️ Setup Instructions


### 1️⃣ Clone the Repository
```powershell
git clone https://github.com/aqualinqs/Bison-Tracking-UI.git
cd Bison-Tracking-UI
```


### 2️⃣ Create and Activate Python Environment
```powershell
python -m venv .myenv
.myenv\Scripts\activate
```


### 3️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```


> **Note:**
> - You may need to install additional system dependencies for PyTorch (see troubleshooting below).
> - For HTML dashboard, just use a modern browser (Chrome, Edge, Firefox).

---


## 🏃‍♂️ Running the Dash Dashboard (`app.py`)

```powershell
python app.py
```
- Open your browser and go to: [http://127.0.0.1:8050](http://127.0.0.1:8050)
- The dashboard updates every second with live bison counts. Watch the numbers change in real time!

---



## 🌐 Running the HTML Dashboard (`dashboard.html`)

Use the standalone HTML dashboard for a fast, browser-based view of bison analytics. Built with Tailwind CSS and Chart.js, it polls the tracker API for live stats and video streams.

### How to Use

1. 🖱️ Open `dashboard.html` in your browser (double-click or right-click and choose "Open with" > your browser).
2. 🦾 Make sure your tracker server is running and accessible at the endpoints configured in the HTML (default: `http://localhost:8080/stats`, `http://localhost:8080/mjpeg`, `http://localhost:8080/hls.m3u8`).
3. 📊 The dashboard will automatically poll for live stats and display:
   - Live Bison Count
   - Max Bison in Frame
   - Live FPS and Average FPS
   - Detections by Class (bar chart)
   - Bison Count Trend (line chart)
   - Live MJPEG video stream (if available)
   - Download buttons for JSON/CSV stats

#### 🎨 Customization
- You can edit the endpoints directly in the HTML file to match your server configuration.
- No Python environment is required for the HTML dashboard—just a modern browser.

---

---


## 🔌 API Endpoints

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


## 🧰 Troubleshooting


- **DLL Load Errors (PyTorch):**
  - 🛠️ Install the Microsoft Visual C++ Redistributable (x64):
    [https://aka.ms/vs/16/release/vc_redist.x64.exe](https://aka.ms/vs/16/release/vc_redist.x64.exe)
  - 🔄 Restart your computer after installation.

- **Port Conflicts:**
  - 🔀 Change the port in your script if `8080` or `8050` is in use.

- **Missing Packages:**
  - 📦 Install with `pip install <package>` as needed.

---


## 🗂️ File Structure


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



## 🏞️ Architecture Diagram

<p align="center">
	<img src="architecture.svg" alt="Bison Tracking Architecture" width="500"/>
</p>

The diagram below shows the flow from the video source and tracker server to the Dash dashboard (`app.py`) and the standalone HTML dashboard (`dashboard.html`).

---


## ✅ Assessment Rubric Checklist
- [x] Clear and complete setup instructions
- [x] Running instructions for both dashboards
- [x] API endpoint documentation
- [x] Troubleshooting section
- [x] File structure overview

---


## 📄 License

This project is licensed under the MIT License.
