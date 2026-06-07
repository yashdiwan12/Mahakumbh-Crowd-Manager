import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    max_capacity = Column(Integer, nullable=True)
    current_crowd_count = Column(Integer, default=0)

class Path(Base):
    __tablename__ = 'paths'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_location_id = Column(UUID(as_uuid=True), ForeignKey('locations.id'), nullable=False)
    target_location_id = Column(UUID(as_uuid=True), ForeignKey('locations.id'), nullable=False)
    base_distance_meters = Column(Float, nullable=False)
    current_congestion_multiplier = Column(Float, default=1.0)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey('locations.id'), nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
