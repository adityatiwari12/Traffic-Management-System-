from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import os
from pathlib import Path
from ..routers.auth import get_current_active_user
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Router
router = APIRouter()

# Define paths
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'trip_duration_model.joblib')

# Pydantic models
class TripFeatures(BaseModel):
    pickup_longitude: float = Field(..., example=-73.9857, description="Pickup location longitude")
    pickup_latitude: float = Field(..., example=40.7484, description="Pickup location latitude")
    dropoff_longitude: float = Field(..., example=-73.9881, description="Dropoff location longitude")
    dropoff_latitude: float = Field(..., example=40.7517, description="Dropoff location latitude")
    passenger_count: int = Field(1, ge=1, le=8, description="Number of passengers")
    pickup_datetime: str = Field(..., example="2023-01-01 12:00:00", description="Pickup date and time in UTC")
    vendor_id: int = Field(1, ge=1, le=2, description="Vendor ID (1 or 2)")
    store_and_fwd_flag: str = Field("N", regex="^[YN]$", description="Store and forward flag (Y or N)")

class TripPrediction(BaseModel):
    trip_duration_seconds: float = Field(..., description="Predicted trip duration in seconds")
    trip_duration_minutes: float = Field(..., description="Predicted trip duration in minutes")
    confidence: float = Field(..., description="Confidence score of the prediction (0-1)")

# Load the model (lazy loading)
_model = None

def load_model():
    """Load the trained model"""
    global _model
    if _model is None:
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception as e:
            print(f"Error loading model: {e}")
            _model = None
    return _model

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on the earth"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def prepare_features(trip: TripFeatures) -> dict:
    """Prepare features for model prediction"""
    # Convert pickup datetime to datetime object
    pickup_dt = datetime.strptime(trip.pickup_datetime, '%Y-%m-%d %H:%M:%S')
    
    # Calculate distance
    distance_km = haversine_distance(
        trip.pickup_latitude, trip.pickup_longitude,
        trip.dropoff_latitude, trip.dropoff_longitude
    )
    
    # Extract time features
    hour = pickup_dt.hour
    day_of_week = pickup_dt.weekday()  # 0=Monday, 6=Sunday
    month = pickup_dt.month
    
    # Prepare feature dictionary
    features = {
        'vendor_id': trip.vendor_id,
        'passenger_count': trip.passenger_count,
        'pickup_longitude': trip.pickup_longitude,
        'pickup_latitude': trip.pickup_latitude,
        'dropoff_longitude': trip.dropoff_longitude,
        'dropoff_latitude': trip.dropoff_latitude,
        'store_and_fwd_flag': 1 if trip.store_and_fwd_flag == 'Y' else 0,
        'distance_km': distance_km,
        'hour': hour,
        'day_of_week': day_of_week,
        'month': month,
        'is_weekend': 1 if day_of_week >= 5 else 0,
        'is_night': 1 if 20 <= hour <= 23 or 0 <= hour < 6 else 0,
        'is_rush_hour': 1 if (7 <= hour <= 10) or (16 <= hour <= 19) else 0
    }
    
    return features

@router.post("/predict", response_model=TripPrediction)
async def predict_trip_duration(
    trip: TripFeatures,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Predict the duration of a taxi trip in NYC based on pickup/dropoff locations and other features.
    """
    # Load the model
    model = load_model()
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction model is not available"
        )
    
    try:
        # Prepare features
        features = prepare_features(trip)
        
        # Convert to DataFrame for prediction
        X = pd.DataFrame([features])
        
        # Make prediction (assuming the model has a predict method)
        prediction_seconds = model.predict(X)[0]
        
        # For demonstration, we'll use a simple confidence score
        # In a real application, you might use prediction intervals or model's probability
        confidence = 0.9  # Placeholder confidence value
        
        return TripPrediction(
            trip_duration_seconds=float(prediction_seconds),
            trip_duration_minutes=float(prediction_seconds / 60),
            confidence=confidence
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error processing prediction: {str(e)}"
        )

@router.get("/model-info")
async def get_model_info(current_user: dict = Depends(get_current_active_user)):
    """Get information about the prediction model"""
    model = load_model()
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction model is not available"
        )
    
    try:
        model_info = {
            "model_type": str(type(model).__name__),
            "features_used": [
                'vendor_id', 'passenger_count', 'pickup_longitude', 'pickup_latitude',
                'dropoff_longitude', 'dropoff_latitude', 'store_and_fwd_flag',
                'distance_km', 'hour', 'day_of_week', 'month', 'is_weekend',
                'is_night', 'is_rush_hour'
            ],
            "model_created": "2023-01-01T00:00:00Z",  # Should be set during model training
            "model_version": "1.0.0"
        }
        
        # Add model-specific information if available
        if hasattr(model, 'feature_importances_'):
            model_info["feature_importances"] = dict(
                zip(model.feature_names_in_, model.feature_importances_.tolist())
            )
        
        return model_info
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model information: {str(e)}"
        )
