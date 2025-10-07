from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from ..routers.auth import get_current_active_user
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Router
router = APIRouter()

# Mock data paths (in a real application, this would be a database)
MOCK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'NYC.csv')

# Pydantic models
class TimeRange(BaseModel):
    start_time: Optional[datetime] = Field(
        default_factory=lambda: (datetime.utcnow() - timedelta(days=30)).isoformat(),
        description="Start time for the query (ISO 8601 format)"
    )
    end_time: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="End time for the query (ISO 8601 format)"
    )

class ZoneAnalytics(BaseModel):
    zone_id: int
    zone_name: str
    total_trips: int
    avg_duration: float
    avg_distance: float
    avg_speed: float

class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float

class AnalyticsResponse(BaseModel):
    total_trips: int
    avg_duration_minutes: float
    avg_distance_km: float
    top_pickup_zones: List[ZoneAnalytics]
    top_dropoff_zones: List[ZoneAnalytics]
    hourly_pattern: List[TimeSeriesPoint]
    daily_pattern: List[TimeSeriesPoint]

# Mock data loading function
def load_mock_data():
    """Load mock data for demonstration"""
    try:
        # In a real application, this would query a database
        # For now, we'll generate some mock data
        return {
            "total_trips": 10000,
            "avg_duration_minutes": 15.5,
            "avg_distance_km": 8.2,
            "top_pickup_zones": [
                {"zone_id": 1, "zone_name": "Manhattan", "total_trips": 3500, "avg_duration": 12.5, "avg_distance": 5.5, "avg_speed": 26.4},
                {"zone_id": 2, "zone_name": "Brooklyn", "total_trips": 2800, "avg_duration": 18.2, "avg_distance": 9.8, "avg_speed": 32.3},
                {"zone_id": 3, "zone_name": "Queens", "total_trips": 2200, "avg_duration": 22.1, "avg_duration": 14.2, "avg_speed": 38.6},
            ],
            "top_dropoff_zones": [
                {"zone_id": 1, "zone_name": "Manhattan", "total_trips": 4200, "avg_duration": 14.2, "avg_distance": 6.1, "avg_speed": 25.8},
                {"zone_id": 4, "zone_name": "JFK Airport", "total_trips": 1800, "avg_duration": 45.5, "avg_distance": 25.3, "avg_speed": 33.4},
                {"zone_id": 5, "zone_name": "LaGuardia", "total_trips": 1200, "avg_duration": 32.7, "avg_distance": 12.8, "avg_speed": 23.5},
            ],
            "hourly_pattern": [{"timestamp": f"2023-01-01T{i:02d}:00:00Z", "value": 100 + i*15} for i in range(24)],
            "daily_pattern": [
                {"timestamp": f"2023-01-{i+1:02d}T00:00:00Z", "value": 800 + i*50} 
                for i in range(7)
            ]
        }
    except Exception as e:
        print(f"Error loading mock data: {e}")
        return None

@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(
    time_range: TimeRange = Depends(),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get summary analytics for the admin dashboard
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access admin analytics"
        )
    
    # Load mock data
    data = load_mock_data()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is not available"
        )
    
    return data

@router.get("/analytics/zones")
async def get_zone_analytics(
    time_range: TimeRange = Depends(),
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get detailed analytics by zone
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access zone analytics"
        )
    
    # In a real application, this would query the database
    # For now, return mock data
    zones = [
        {"zone_id": i, "zone_name": f"Zone {i}", "total_trips": 1000 - i*50, "avg_duration": 10 + i*2, "avg_distance": 5 + i*0.5, "avg_speed": 20 + i*2}
        for i in range(1, limit + 1)
    ]
    
    return {"zones": zones}

@router.get("/analytics/timeseries")
async def get_timeseries_analytics(
    time_range: TimeRange = Depends(),
    interval: str = "hour",
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get time series data for analytics
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access timeseries analytics"
        )
    
    # In a real application, this would query the database
    # For now, generate mock data
    if interval == "hour":
        data = [
            {"timestamp": f"2023-01-01T{hour:02d}:00:00Z", "value": 100 + hour * 10}
            for hour in range(24)
        ]
    elif interval == "day":
        data = [
            {"timestamp": f"2023-01-{day+1:02d}T00:00:00Z", "value": 500 + day * 50}
            for day in range(30)
        ]
    else:
        data = []
    
    return {"data": data, "interval": interval}

@router.get("/system/status")
async def get_system_status(current_user: dict = Depends(get_active_admin_user)):
    """
    Get system status and health metrics
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "uptime": "5d 12h 30m",
        "database": {
            "status": "connected",
            "latency_ms": 12.5
        },
        "model": {
            "status": "loaded",
            "version": "1.0.0",
            "last_updated": "2023-01-01T00:00:00Z"
        },
        "storage": {
            "used_gb": 5.2,
            "total_gb": 100,
            "usage_percent": 5.2
        },
        "requests": {
            "total": 12500,
            "last_hour": 245,
            "avg_response_time_ms": 125.5
        }
    }

# Helper function to ensure only admin users can access certain endpoints
def get_active_admin_user(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
