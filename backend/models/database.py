from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import enum
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL - default to SQLite if not specified in environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./nyc_traffic.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    ""
    Dependency to get a database session.
    Use this in your FastAPI path operations to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = relationship("Trip", back_populates="user")
    saved_locations = relationship("SavedLocation", back_populates="user")

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Trip details
    pickup_latitude = Column(Float, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    dropoff_latitude = Column(Float, nullable=False)
    dropoff_longitude = Column(Float, nullable=False)
    
    # Predicted and actual times
    predicted_duration_seconds = Column(Float)
    actual_duration_seconds = Column(Float)
    
    # Trip metadata
    passenger_count = Column(Integer, default=1)
    vendor_id = Column(Integer)
    store_and_fwd_flag = Column(String(1), default='N')
    
    # Timestamps
    pickup_datetime = Column(DateTime, default=datetime.utcnow)
    dropoff_datetime = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trips")
    route = relationship("Route", back_populates="trip", uselist=False)

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    
    # Route details
    distance_meters = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    geometry = Column(String)  # Store as GeoJSON string
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = relationship("Trip", back_populates="route")
    steps = relationship("RouteStep", back_populates="route")

class RouteStep(Base):
    __tablename__ = "route_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    
    # Step details
    distance_meters = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    instruction = Column(String)
    name = Column(String)
    way_points = Column(String)  # Store as JSON array of integers
    
    # Relationships
    route = relationship("Route", back_populates="steps")

class SavedLocation(Base):
    __tablename__ = "saved_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Location details
    name = Column(String, nullable=False)
    address = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_locations")

# Create all tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

# Run this to initialize the database
if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully.")
