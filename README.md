# 🕉️ Mahakumbh 2028 — AI Crowd Management Platform

> An autonomous, AI-powered crowd routing and safety control room for the world's largest human gathering.

Built with **Next.js**, **FastAPI**, **Google Maps API**, and **Machine Learning** — this platform monitors real-time crowd density across major Ghats in Prayagraj and autonomously reroutes pilgrims away from stampede-risk zones using a dynamic **A\* Search Algorithm**.

---

##  Key Features

| Feature | Description |
|---------|-------------|
| **AI Routing Engine** | A* algorithm with dynamic edge weights. Benchmarked at **10.85ms** on a 5,000-node city graph. |
| **Autonomous Rerouting** | If a sector's Safety Index drops below 30%, the engine automatically applies ∞ cost and reroutes. |
| **ML Prediction** | Gradient Boosting Regressor trained on 40+ years of Kumbh data predicts **39.3M visitors** for 2028. |
| **Google Maps Integration** | Road-snapped routes via Directions API, live Traffic Layer overlay, and walking ETA/distance. |
| **Real-time WebSockets** | Live crowd fluctuations streamed at 2-second intervals to all connected dashboards. |
| **Critical Alert System** | Aggressive toast notifications when stampede risk is detected. |
| **Safety Index** | Dynamic score (40–96%) computed from crowd density (70%) + weather hazard (30%). |
| **Historical Insights** | Educational panel with past stampede data to help pilgrims plan safer visits. |

---

## Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   Next.js 13    │◄──────────────────►│   FastAPI/ASGI  │
│   React 18      │     REST API       │   Uvicorn       │
│   Google Maps   │◄──────────────────►│   SQLAlchemy    │
│   Recharts      │                    │   NetworkX (A*) │
└─────────────────┘                    └─────────────────┘
     Frontend                              Backend
```

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **Google Maps API Key** with Directions, Traffic, and Maps JavaScript APIs enabled

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/mahakumbh-crowd-management.git
cd mahakumbh-crowd-management
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env and add your GOOGLE_MAPS_API_KEY

# Seed the database with Prayagraj Ghat coordinates
python seed_database.py

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-key-here" > .env.local

# Start the dev server
npm run dev
```

### 4. Open the Dashboard
Navigate to **http://localhost:3000** in your browser.

---

##  Docker (Alternative)
```bash
# From root directory
docker-compose up --build
```
Frontend: `http://localhost:3000` | Backend: `http://localhost:8000`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/insights` | Historical data + ML prediction + risk advisories |
| `GET` | `/api/route?source_id=&target_id=` | A* optimal safe route |
| `GET` | `/api/locations` | List all seeded Ghats |
| `POST` | `/api/simulate` | Push crowd state updates (API key required) |
| `WS` | `/api/v1/stream` | Real-time WebSocket state broadcast |

---

## ML Pipeline

The prediction model is in `scripts/train_visitor_model.py`:
```bash
cd scripts
python train_visitor_model.py
```
This trains a **Gradient Boosting Regressor** on `Mahakumbh_Complete_Dataset.csv` and saves the model to `backend/app/core/visitor_model.pkl`.

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 13 | Fast Server Rendering |
| UI | React 18 | Component-based UI |
| Language | TypeScript | Type Safety |
| Styling | Custom CSS | Glassmorphism Aesthetics |
| Charts | Recharts | Data Visualization |
| Maps | Google Maps API | Real-world Paths & Traffic |
| Backend | FastAPI | High Concurrency |
| Realtime | WebSockets | Real-time Sync |
| Database | SQLAlchemy + SQLite | Flexible Schema Management |
| ML | Scikit-learn | Machine Learning Models |
| Graph | NetworkX | A* Routing Algorithm |
| Data | Pandas | Data Manipulation |

---

## Project Structure
```
mahakumbh/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py          # REST endpoints
│   │   │   └── websocket.py       # WebSocket + live simulator
│   │   ├── core/
│   │   │   ├── config.py          # Environment config
│   │   │   ├── gmaps_client.py    # Google Maps backend client
│   │   │   ├── routing.py         # A* routing engine
│   │   │   ├── state.py           # In-memory global state
│   │   │   └── visitor_model.pkl  # Trained ML model
│   │   ├── db.py                  # SQLAlchemy setup
│   │   ├── models.py              # ORM models
│   │   └── schemas.py             # Pydantic schemas
│   ├── seed_database.py           # Database seeder (9 Ghats)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map.tsx            # Google Maps + Traffic + Markers
│   │   │   └── Sidebar.tsx        # Control Room UI
│   │   ├── pages/
│   │   │   ├── _app.tsx
│   │   │   └── index.tsx          # Main dashboard
│   │   └── styles/
│   │       └── globals.css        # Neural Noir theme
│   ├── package.json
│   └── Dockerfile
├── scripts/
│   ├── train_visitor_model.py     # ML training pipeline
│   ├── benchmark_routing_algorithms.py # A* vs Dijkstra benchmark
│   └── start_services.ps1         # Windows dev start script
├── Mahakumbh_Complete_Dataset.csv  # Historical Kumbh data
├── docker-compose.yml
├── .env.example
└── README.md
```

---

<p align="center">
  Built with ❤️ for Mahakumbh 2028 — Protecting millions of pilgrims with AI.
</p>
