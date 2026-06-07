import asyncio
import websockets
import json
import requests
import time
from uuid import uuid4

BASE_URL = "http://127.0.0.1:8000/api"
WS_URL = "ws://127.0.0.1:8000/api/v1/stream"
API_KEY = "your-demo-api-key"

async def test_websocket():
    print("Connecting to WebSocket...")
    try:
        async with websockets.connect(WS_URL) as ws:
            print("Connected! Waiting for state...")
            message = await ws.recv()
            state = json.loads(message)
            print(f"Received state with {len(state['nodes'])} nodes, {len(state['edges'])} edges, {len(state['alerts'])} alerts.")
            return state
    except Exception as e:
        print(f"WebSocket test failed: {e}")

def test_simulate():
    print("Testing /simulate...")
    # First, fetch existing locations to get valid IDs, or we can just push new ones if DB is empty.
    # Wait, simulate only updates existing ones. Let's create some dummy ones first.
    headers = {"x-api-key": API_KEY}
    
    n1 = requests.post(f"{BASE_URL}/locations", json={"name": "Node A", "type": "ghat", "latitude": 0, "longitude": 0, "max_capacity": 100}).json()
    n2 = requests.post(f"{BASE_URL}/locations", json={"name": "Node B", "type": "transit", "latitude": 1, "longitude": 1, "max_capacity": 100}).json()
    
    if "id" not in n1 or "id" not in n2:
        print("Failed to create locations.", n1, n2)
        return None, None
    
    id1 = n1["id"]
    id2 = n2["id"]
    print(f"Created nodes {id1} and {id2}")
    
    # We can't create paths via API right now (no POST /paths).
    # We will just push state for nodes to trigger alerts.
    payload = {
        "nodes": [
            {"id": id1, "current_crowd_count": 95}, # Should trigger alert
            {"id": id2, "current_crowd_count": 10}
        ],
        "edges": []
    }
    
    r = requests.post(f"{BASE_URL}/simulate", json=payload, headers=headers)
    print("Simulate response:", r.status_code, r.text)
    return id1, id2

def test_route(id1, id2):
    print("Testing /route...")
    # Since we don't have edges in DB, route will probably be empty. Let's just make sure it returns 200.
    r = requests.get(f"{BASE_URL}/route", params={"source_id": id1, "target_id": id2})
    print("Route response:", r.status_code, r.text)

async def main():
    # Wait for server to start
    time.sleep(2)
    id1, id2 = test_simulate()
    if id1 and id2:
        await test_websocket()
        test_route(id1, id2)

if __name__ == "__main__":
    asyncio.run(main())
