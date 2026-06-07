import math
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Location, Path

DATABASE_URL = "sqlite:///./dev.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

GHATS = [
    {"id": str(uuid.uuid4()), "name": "Triveni Sangam", "lat": 25.4310, "lng": 81.8850, "cap": 500000},
    {"id": str(uuid.uuid4()), "name": "Dashashwamedh Ghat", "lat": 25.4320, "lng": 81.8650, "cap": 250000},
    {"id": str(uuid.uuid4()), "name": "Kila Ghat (Allahabad Fort)", "lat": 25.4300, "lng": 81.8750, "cap": 150000},
    {"id": str(uuid.uuid4()), "name": "Arail Ghat", "lat": 25.4200, "lng": 81.8850, "cap": 120000},
    {"id": str(uuid.uuid4()), "name": "Saraswati Ghat", "lat": 25.4280, "lng": 81.8600, "cap": 100000},
    {"id": str(uuid.uuid4()), "name": "Rasulabad Ghat", "lat": 25.4850, "lng": 81.8500, "cap": 80000},
    {"id": str(uuid.uuid4()), "name": "Prayagraj Junction (Transit)", "lat": 25.4430, "lng": 81.8280, "cap": 350000},
    {"id": str(uuid.uuid4()), "name": "Civil Lines Bus Stand", "lat": 25.4540, "lng": 81.8350, "cap": 180000},
    {"id": str(uuid.uuid4()), "name": "Jhusi (Sector 14)", "lat": 25.4350, "lng": 81.9050, "cap": 200000},
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
