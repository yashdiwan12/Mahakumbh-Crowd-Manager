from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class LocationBase(BaseModel):
    name: str
    type: str
    latitude: float
    longitude: float
    max_capacity: Optional[int] = None

class LocationOut(LocationBase):
    id: UUID
    current_crowd_count: int

    class Config:
        orm_mode = True

from typing import List, Dict, Any

class NodeStateIn(BaseModel):
    id: str
    current_crowd_count: int

class EdgeStateIn(BaseModel):
    id: str
    current_congestion_multiplier: float

class SimulateStateIn(BaseModel):
    nodes: List[NodeStateIn]
    edges: List[EdgeStateIn]

class RouteResponse(BaseModel):
    path: List[str]
