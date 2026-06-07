import math
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Location, Path

DATABASE_URL = "sqlite:///./dev.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

GHATS = [
    {"id": str(uuid.uuid4()), "name": "Ram Ghat", "lat": 23.1830, "lng": 75.7660, "cap": 500000},
    {"id": str(uuid.uuid4()), "name": "Mahakaleshwar Temple", "lat": 23.1827, "lng": 75.7682, "cap": 250000},
    {"id": str(uuid.uuid4()), "name": "Harsiddhi Temple", "lat": 23.1800, "lng": 75.7640, "cap": 150000},
    {"id": str(uuid.uuid4()), "name": "Mangalnath Temple", "lat": 23.2100, "lng": 75.7850, "cap": 120000},
    {"id": str(uuid.uuid4()), "name": "Kal Bhairav Temple", "lat": 23.2200, "lng": 75.7800, "cap": 100000},
    {"id": str(uuid.uuid4()), "name": "Ujjain Junction (Transit)", "lat": 23.1700, "lng": 75.7800, "cap": 350000},
    {"id": str(uuid.uuid4()), "name": "Nanakheda Bus Stand", "lat": 23.1500, "lng": 75.7750, "cap": 180000},
    {"id": str(uuid.uuid4()), "name": "Triveni Ghat (Shipra)", "lat": 23.1600, "lng": 75.7600, "cap": 200000},
    {"id": str(uuid.uuid4()), "name": "Sandipani Ashram", "lat": 23.2150, "lng": 75.7830, "cap": 80000},
]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    session = SessionLocal()
    try:
        for g in GHATS:
            loc = Location(
                id=uuid.UUID(g["id"]),
                name=g["name"],
                type="ghat",
                latitude=g["lat"],
                longitude=g["lng"],
                max_capacity=g["cap"],
                current_crowd_count=0
            )
            session.add(loc)
            
        session.commit()
        
        for i in range(len(GHATS)):
            for j in range(i + 1, len(GHATS)):
                g1, g2 = GHATS[i], GHATS[j]
                dist = haversine(g1["lat"], g1["lng"], g2["lat"], g2["lng"])
                
                if dist < 4500:
                    path1 = Path(
                        id=uuid.uuid4(),
                        source_location_id=uuid.UUID(g1["id"]),
                        target_location_id=uuid.UUID(g2["id"]),
                        base_distance_meters=dist,
                        current_congestion_multiplier=1.0
                    )
                    path2 = Path(
                        id=uuid.uuid4(),
                        source_location_id=uuid.UUID(g2["id"]),
                        target_location_id=uuid.UUID(g1["id"]),
                        base_distance_meters=dist,
                        current_congestion_multiplier=1.0
                    )
                    session.add(path1)
                    session.add(path2)
        session.commit()
        print("Successfully seeded realistic Mahakumbh coordinates and paths!")
    finally:
        session.close()

if __name__ == "__main__":
    reset_db()
