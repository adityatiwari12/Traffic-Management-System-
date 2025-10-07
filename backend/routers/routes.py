from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import openrouteservice
import os
from dotenv import load_dotenv
import numpy as np
from ..routers.auth import get_current_active_user
from pydantic import BaseModel
from typing import List, Optional

# Load environment variables
load_dotenv()

# Initialize OpenRouteService client
ORS_API_KEY = os.getenv("ORS_API_KEY")
if not ORS_API_KEY:
    print("Warning: ORS_API_KEY not found in environment variables. Route optimization will not work.")
else:
    client = openrouteservice.Client(key=ORS_API_KEY)

# Router
router = APIRouter()

# Pydantic models
class Coordinate(BaseModel):
    lng: float
    lat: float

class RouteRequest(BaseModel):
    start: Coordinate
    end: Coordinate
    profile: str = "driving-car"  # driving-car, cycling-regular, foot-walking
    alternatives: bool = False
    optimize_waypoints: bool = False

class RouteLegStep(BaseModel):
    distance: float
    duration: float
    instruction: str
    name: str
    way_points: List[int]

class RouteLeg(BaseModel):
    steps: List[RouteLegStep]
    summary: dict
    way_points: List[int]

class Route(BaseModel):
    distance: float
    duration: float
    geometry: dict
    segments: List[RouteLeg]

@router.post("/optimize", response_model=Route)
async def get_optimized_route(
    route_request: RouteRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get an optimized route between two points using OpenRouteService
    """
    if not ORS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenRouteService API key not configured"
        )
    
    try:
        # Convert coordinates to the format expected by ORS
        coordinates = [
            [route_request.start.lng, route_request.start.lat],
            [route_request.end.lng, route_request.end.lat]
        ]
        
        # Get route from OpenRouteService
        route = client.directions(
            coordinates=coordinates,
            profile=route_request.profile,
            format='geojson',
            alternatives=route_request.alternatives,
            optimize_waypoints=route_request.optimize_waypoints
        )
        
        # Format the response
        if route['features']:
            feature = route['features'][0]  # Get the first (best) route
            
            # Extract route segments and steps
            segments = []
            for leg in feature['properties']['segments']:
                steps = []
                for step in leg['steps']:
                    steps.append(RouteLegStep(
                        distance=step['distance'],
                        duration=step['duration'],
                        instruction=step.get('instruction', ''),
                        name=step.get('name', ''),
                        way_points=step.get('way_points', [])
                    ))
                
                segments.append(RouteLeg(
                    steps=steps,
                    summary=leg.get('summary', {}),
                    way_points=leg.get('way_points', [])
                ))
            
            return Route(
                distance=feature['properties']['summary']['distance'],
                duration=feature['properties']['summary']['duration'],
                geometry=feature['geometry'],
                segments=segments
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="No route found between the specified points"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating route: {str(e)}"
        )

@router.get("/geocode")
async def geocode(
    query: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Geocode an address or place name to get coordinates
    """
    if not ORS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenRouteService API key not configured"
        )
    
    try:
        # Use ORS geocoding service
        result = client.pelias_search(
            text=query,
            focus_point=[-73.9857, 40.7484]  # Focus on NYC by default
        )
        
        # Format the response
        features = []
        for feature in result.get('features', []):
            if 'coordinates' in feature.get('geometry', {}):
                features.append({
                    'name': feature.get('properties', {}).get('label', ''),
                    'coordinates': {
                        'lng': feature['geometry']['coordinates'][0],
                        'lat': feature['geometry']['coordinates'][1]
                    },
                    'type': feature.get('properties', {}).get('layer', '')
                })
        
        return {"results": features}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error geocoding address: {str(e)}"
        )
