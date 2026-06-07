# Architecture Overview

## The Tech Stack
*   **Frontend**: Next.js 13, React 18, Google Maps API, Recharts
*   **Backend**: FastAPI, Python 3.11+, WebSockets, SQLite + SQLAlchemy
*   **AI/ML**: Scikit-Learn (Gradient Boosting Regressor), NetworkX (A* Routing)

## System Flow
1. **Data Intake**: The backend loads node/edge structures from SQLite. 
2. **Simulation**: The `websocket.py` loop simulates active crowd fluctuations. It computes a `Safety Index` dynamically for each sector.
3. **Emergency Routing**: If a sector's safety drops below 30%, it triggers a `CRITICAL` alert. The `routing.py` engine detects this and assigns an infinite penalty (`1,000,000` congestion multiplier) to the sector.
4. **Broadcast**: The backend blasts the updated `nodes`, `edges`, and `alerts` array over WebSockets.
5. **Frontend Rendering**: The Next.js dashboard consumes the WebSocket payload. If an active route exists, it hits the `GET /api/route` endpoint, receives the A* calculated path, and invokes the Google Maps Directions API to visually snap the new route to physical roads.
