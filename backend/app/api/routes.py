from fastapi import APIRouter, Depends, Header, HTTPException, status
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
import pandas as pd

from app.core.config import API_KEY
from app.db import get_db
from app import models, schemas
from app.core.state import state
from app.core.routing import routing_engine
import asyncio
import uuid

router = APIRouter()

@router.get("/insights")
async def get_insights():
    try:
        df = pd.read_excel("../Mahakumbh_Complete_Dataset.csv", engine="openpyxl")
        # Ensure we filter for Prayagraj
        df = df[df['Location'].str.contains('Prayagraj', case=False, na=False)]
        
        # Aggregate total visitors by year
        df['Total_Visitors'] = df['Domestic_Visitors'] + df['International_Visitors']
        historical = df[['Year', 'Total_Visitors']].to_dict('records')
        
        return {
            "historical_data": historical,
            "prediction_2028": 39342804,
            "historical_risks": [
                {"date": "10 Feb 2013", "event": "Mauni Amavasya Stampede", "weather": "Clear", "safety_index": 12, "advice": "Avoid peak bathing days when capacity exceeds 150%. Plan travel 2 days prior."},
                {"date": "24 Jan 2001", "event": "Sudden Downpour", "weather": "Heavy Rain", "safety_index": 35, "advice": "Pontoon bridges become highly slippery. Avoid transit during heavy rain alerts."}
            ]
        }
    except Exception as e:
        # Fallback dummy data if file is missing
        return {
            "historical_data": [
                {"Year": 1989, "Total_Visitors": 15000000},
                {"Year": 2001, "Total_Visitors": 30000000},
                {"Year": 2013, "Total_Visitors": 120000000},
                {"Year": 2019, "Total_Visitors": 240000000}
            ],
            "prediction_2028": 39342804,
            "historical_risks": [
                {"date": "10 Feb 2013", "event": "Mauni Amavasya Stampede", "weather": "Clear", "safety_index": 12, "advice": "Avoid peak bathing days when capacity exceeds 150%. Plan travel 2 days prior."},
                {"date": "24 Jan 2001", "event": "Sudden Downpour", "weather": "Heavy Rain", "safety_index": 35, "advice": "Pontoon bridges become highly slippery. Avoid transit during heavy rain alerts."}
            ]
        }

@router.get('/health')
async def health():
    return {"status": "ok"}

# Simple API key dependency (demo)
async def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.get('/protected', dependencies=[Depends(require_api_key)])
async def protected():
    return {"message": "protected data"}

# Simulation endpoint: accepts network flow state (nodes, edges)
@router.post('/simulate', dependencies=[Depends(require_api_key)])
async def simulate_update(payload: schemas.SimulateStateIn):
    # Update nodes and handle alerts with hysteresis
    for n_data in payload.nodes:
        nid = str(n_data.id)
        if nid in state.nodes:
            state.nodes[nid]["current_crowd_count"] = n_data.current_crowd_count
            
            # Recalculate dynamic safety score
            cap = state.nodes[nid].get("max_capacity") or 10000
            w_penalty = state.nodes[nid].get("weather_penalty", 0)
            density_pct = min(100.0, (n_data.current_crowd_count / cap) * 100)
            safety_score = 100 - (density_pct * 0.7) - (w_penalty * 0.3)
            state.nodes[nid]["safety_score"] = max(0, min(100, safety_score))
            
            # Hysteresis Alert Logic
            capacity = state.nodes[nid].get("max_capacity")
            if capacity and capacity > 0:
                utilization = n_data.current_crowd_count / capacity
                
                # Check if we already have an active alert for this node
                active_alert = next((a for a in state.alerts if a["location_id"] == nid), None)
                
                if utilization > 0.9 and not active_alert:
                    # Trigger alert
                    state.alerts.append({
                        "id": str(uuid.uuid4()),
                        "location_id": nid,
                        "severity": "WARNING",
                        "message": f"{state.nodes[nid]['name']} is at {int(utilization*100)}% capacity!"
                    })
                elif utilization < 0.8 and active_alert:
                    # Resolve alert
                    state.alerts.remove(active_alert)
                    
    # Update edges
    for e_data in payload.edges:
        eid = e_data.id
        if eid in state.edges:
            state.edges[eid]["current_congestion_multiplier"] = e_data.current_congestion_multiplier

    return {"ok": True}

@router.get('/route', response_model=schemas.RouteResponse)
async def get_route(source_id: str, target_id: str):
    # Run NetworkX in a background thread
    path = await asyncio.to_thread(routing_engine.calculate_route, state, source_id, target_id)
    return {"path": path}

# Locations CRUD
@router.get('/locations', response_model=List[schemas.LocationOut])
async def list_locations(db: Session = Depends(get_db)):
    items = db.query(models.Location).all()
    return items

@router.post('/locations', response_model=schemas.LocationOut)
async def create_location(payload: schemas.LocationBase, db: Session = Depends(get_db)):
    loc = models.Location(
        name=payload.name,
        type=payload.type,
        latitude=payload.latitude,
        longitude=payload.longitude,
        max_capacity=payload.max_capacity or None,
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc
