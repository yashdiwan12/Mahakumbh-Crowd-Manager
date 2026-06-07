# API Documentation

## REST Endpoints

### `GET /api/health`
Health check endpoint. Returns `{"status": "ok"}`.

### `GET /api/insights`
Returns historical Mahakumbh data, the 2028 AI prediction, and historical risks/educational advice.

### `GET /api/locations`
Lists all seeded locations (Ghats, Transit Hubs, etc.) from the SQLite database.

### `GET /api/route?source_id={uuid}&target_id={uuid}`
Calculates the optimal safe route using the A* engine based on real-time edge congestion and safety scores. Returns `{"path": [uuid1, uuid2, ...]}`.

### `POST /api/simulate`
Protected by `x-api-key` header. Accepts simulated crowd updates to bypass internal WebSocket simulation.

## WebSocket

### `WS /api/v1/stream`
Real-time state broadcast. Emits JSON payloads every 2 seconds containing the full global state (nodes, edges, and generated alerts).
