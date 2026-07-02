# Black Sky Sentinel — Southern Punjab Risk Dashboard

A geospatial risk analysis dashboard that ranks 11 districts in Southern Punjab, Pakistan by composite risk scores. It combines data from multiple authoritative sources and uses the **Analytic Hierarchy Process (AHP)** to let decision-makers explore, weight, and visualize district-level risks in real time.

![Tech Stack](https://img.shields.io/badge/Backend-Flask-blue) ![Tech Stack](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB) ![Map](https://img.shields.io/badge/Maps-Leaflet-199900) ![License](https://img.shields.io/badge/License-MIT-green)

---

## What It Does

The dashboard synthesizes 7 risk criteria into a single composite score for each district:

| Criterion | Data Source |
|---|---|
| Blackout vulnerability (load shedding hours) | NEPRA |
| Flood exposure | NDMA (2022) |
| Heat stress (max temperature May–Sep) | Open-Meteo |
| 4G coverage gaps | PTA |
| Healthcare deficits (hospitals + clinics) | OpenStreetMap |
| Infrastructure gaps (substations + towers) | OpenStreetMap |
| Population exposure | PBS Census 2023 |

Users can adjust criterion weights via sliders or choose a **preset scenario** (Monsoon, Grid Crisis, Heat Wave, etc.), and the map instantly recolors to reflect the new priority ranking.

### Districts Covered

Multan · Khanewal · Rajanpur · Dera Ghazi Khan · Bahawalpur · Bahawalnagar · Lodhran · Pakpattan · Sahiwal · Okara · Rahim Yar Khan

---

## Features

- **Interactive choropleth map** — districts colored by risk tier (Critical / High / Moderate / Low)
- **AHP weight sliders** — adjust the importance of each criterion (1–10 scale) and see live percentage contributions
- **5 preset scenarios** — Equal Weight, Monsoon, Grid Crisis, Heat Wave, Communications Blackout
- **District detail card** — click any district to see its score breakdown, raw indicators, and rank
- **Risk summary bar** — shows distribution of risk tiers and the top 3 highest-risk districts
- **Export to JSON or CSV** — download the current analysis with metadata and timestamps
- **Scenario comparison** — side-by-side comparison of multiple scenarios via the API
- **WCAG 2.1 AA accessible** — keyboard navigable, screen-reader friendly, sufficient color contrast

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 · Flask 3.0 · Flask-CORS |
| Frontend | React 18 · Vite 5 · Leaflet 1.9 |
| Maps | Leaflet.js with CartoDB dark basemap |
| Data | JSON files (no database required) |
| Styling | Custom CSS with CSS variables (dark theme) |

---

## Quickstart

### Prerequisites

- Python 3.9+
- Node.js 18+

### 1. Clone the repo

```bash
git clone https://github.com/Qandeel-01/Black-Sky-Sentinel.git
cd Black-Sky-Sentinel
```

### 2. Start the backend

```powershell
# Windows PowerShell
python -m venv backend\.venv
& backend\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python backend/app.py
```

```bash
# macOS / Linux
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
python backend/app.py
```

The Flask API runs at **http://localhost:5000**.

### 3. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The app opens at **http://localhost:5173**. Vite proxies all `/api` requests to the Flask backend automatically.

### 4. Windows one-click start

```batch
start.bat
```

This launches both the backend and frontend in separate console windows.

---

## Configuration

Copy the example environment files and edit as needed:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

**Backend (`backend/.env`)**

```env
FLASK_ENV=development
FLASK_PORT=5000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DATA_PATH=data
LOG_LEVEL=INFO
LOG_PATH=logs
```

**Frontend (`frontend/.env`)**

```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check and list of all endpoints |
| `GET` | `/api/real-scores` | Full district data with raw indicators and 0–100 scores |
| `GET` | `/api/districts` | Compact district list with metadata |
| `GET` | `/api/criteria` | Criterion definitions and data sources |
| `GET` | `/api/scenarios` | Preset AHP scenario definitions |
| `GET` | `/api/geojson` | GeoJSON boundaries for all 11 districts |
| `GET` | `/api/settlements` | Settlement polygons (if generated) |
| `POST` | `/api/calculate` | Compute composite scores from custom weights |
| `GET` | `/api/report/<district_id>` | Detailed report for a single district |
| `POST` | `/api/compare` | Side-by-side scenario comparison |

### Example: Custom weight calculation

```bash
curl -X POST http://localhost:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"weights": {"blackout": 8, "flood": 6, "heat": 4, "coverage": 5, "healthcare": 7, "infrastructure": 5, "population": 6}}'
```

---

## Project Structure

```
black-sky-sentinel/
├── backend/
│   ├── app.py                  # Flask API (8 endpoints, AHP engine)
│   ├── requirements.txt
│   ├── .env.example
│   └── data/
│       ├── real_scores.json    # District scores + raw indicators
│       ├── southern_punjab.geojson  # Map boundaries
│       └── settlements.json    # Settlement polygons
├── frontend/
│   └── src/
│       ├── App.jsx             # Root component, state management, export
│       ├── components/
│       │   ├── Map.jsx         # Leaflet choropleth map
│       │   ├── AHPPanel.jsx    # Weight sliders + scenario buttons
│       │   ├── DistrictCard.jsx # District detail panel
│       │   ├── RiskSummaryBar.jsx # Top bar with tier counts
│       │   └── Legend.jsx      # Risk tier color legend
│       └── App.css
├── dashboard.html              # Standalone single-file version
├── start.bat                   # Windows launcher
└── README.md
```

---

## Data Sources

| Source | What It Provides |
|---|---|
| [NEPRA](https://nepra.org.pk/) | Load shedding duration by district |
| [NDMA](https://ndma.gov.pk/) | Flood exposure data (2022 floods) |
| [PBS](https://www.pbs.gov.pk/) | Population by district (Census 2023) |
| [PTA](https://pta.gov.pk/) | 4G mobile network coverage |
| [OpenStreetMap](https://www.openstreetmap.org/) | Hospitals, clinics, substations, towers |
| [Open-Meteo](https://open-meteo.com/) | Historical max temperatures |

---

## License

MIT — see [LICENSE](LICENSE) for details.
