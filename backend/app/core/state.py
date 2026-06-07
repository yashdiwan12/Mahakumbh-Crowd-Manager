from typing import Dict, Any, List
from uuid import UUID
import asyncio
from app.db import SessionLocal
from app.models import Location, Path, Alert

class GlobalState:
    def __init__(self):
        # In-memory stores
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    def load_from_db(self):
        """Loads initial state from DB."""
        db = SessionLocal()
        try:
            locations = db.query(Location).all()
            import random
            
            for loc in locations:
                w_cond, w_penalty = "Clear", 0
                
                # Initialize with >100k crowd if capacity allows, otherwise a high random
                base_crowd = random.randint(110000, 250000)
                cap = loc.max_capacity if loc.max_capacity else 500000
                initial_crowd = min(base_crowd, cap)
                
                density_pct = min(100.0, (initial_crowd / cap) * 100)
                safety_score = 100 - (density_pct * 0.7) - (w_penalty * 0.3)
                
                self.nodes[str(loc.id)] = {
                    "id": str(loc.id),
                    "name": loc.name,
                    "type": loc.type,
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                    "max_capacity": cap,
                    "current_crowd_count": initial_crowd,
                    "weather_condition": w_cond,
                    "weather_penalty": w_penalty,
                    "safety_score": max(0, min(100, safety_score))
                }
            
            paths = db.query(Path).all()
            for p in paths:
                self.edges[str(p.id)] = {
                    "id": str(p.id),
                    "source_id": str(p.source_location_id),
                    "target_id": str(p.target_location_id),
                    "base_distance_meters": p.base_distance_meters,
                    "current_congestion_multiplier": p.current_congestion_multiplier
                }
            
            alerts = db.query(Alert).filter(Alert.is_resolved == False).all() if hasattr(Alert, 'is_resolved') else db.query(Alert).all()
            for a in alerts:
                self.alerts.append({
                    "id": str(a.id),
                    "location_id": str(a.location_id),
                    "severity": a.severity,
                    "message": a.message
                })
        finally:
            db.close()

    async def flush_to_db(self):
        """Flushes in-memory state back to DB periodically."""
        async with self._lock:
            # We copy the state to avoid holding the lock during slow DB operations
            nodes_copy = list(self.nodes.values())
            edges_copy = list(self.edges.values())
        
        # Execute DB update in a background thread to avoid blocking the event loop
        await asyncio.to_thread(self._sync_flush, nodes_copy, edges_copy)

    def _sync_flush(self, nodes_copy, edges_copy):
        import uuid
        db = SessionLocal()
        try:
            # Update locations
            for n_data in nodes_copy:
                db.query(Location).filter(Location.id == uuid.UUID(n_data["id"])).update({
                    "current_crowd_count": n_data["current_crowd_count"]
                })
            
            # Update paths
            for e_data in edges_copy:
                db.query(Path).filter(Path.id == uuid.UUID(e_data["id"])).update({
                    "current_congestion_multiplier": e_data["current_congestion_multiplier"]
                })
            
            db.commit()
        except Exception as e:
            print(f"Error flushing state to DB: {e}")
        finally:
            db.close()

# Singleton instance
state = GlobalState()
