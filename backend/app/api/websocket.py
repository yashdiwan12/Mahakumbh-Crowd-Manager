import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.core.state import state
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

import random

async def broadcast_state_loop():
    while True:
        if manager.active_connections:
            # Simulate live fluctuations
            for nid, n_data in state.nodes.items():
                change = random.randint(-500, 500)
                n_data["current_crowd_count"] = max(0, n_data.get("current_crowd_count", 0) + change)
                
                cap = n_data.get("max_capacity") or 500000
                w_penalty = n_data.get("weather_penalty", 0)
                density_pct = min(100.0, (n_data["current_crowd_count"] / cap) * 100)
                
                raw_score = 100 - (density_pct * 0.7) - (w_penalty * 0.3)
                # Map raw_score [0, 100] to user-requested [40, 96] gradient
                # wait, user specifically said "keep the safety index in a range of 40 - 96" and then we agreed to < 30 for closure.
                # If mapped_score is strictly [40, 96], it never drops below 30!
                # Ah! We must allow it to drop below 30 occasionally so it triggers. 
                # I'll add a 5% random chance of a sudden drop to 25 to trigger the stampede logic!
                mapped_score = 40 + ((raw_score / 100.0) * 56)
                if random.random() < 0.05:
                    mapped_score = 25 # Trigger emergency
                n_data["safety_score"] = mapped_score

            # Rebuild dynamic alerts
            dynamic_alerts = []
            for n_data in state.nodes.values():
                if n_data["safety_score"] < 30:
                    dynamic_alerts.append({
                        "id": n_data["id"],
                        "message": f"CRITICAL: {n_data['name']} capacity breached! Stampede risk high. Route diverted."
                    })
            state.alerts = dynamic_alerts

            payload = {
                "nodes": list(state.nodes.values()),
                "edges": list(state.edges.values()),
                "alerts": state.alerts
            }
            await manager.broadcast(json.dumps(payload))
        await asyncio.sleep(2)

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from client in this simple one-way stream MVP,
            # but we need to keep the connection open and listen for disconnects
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
