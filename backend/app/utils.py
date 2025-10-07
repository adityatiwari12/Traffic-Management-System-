import os
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger = logging.getLogger(__name__)
    return logger

# Security utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Data processing utilities
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth specified in decimal degrees.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def format_duration(seconds: float) -> str:
    """Format duration in seconds to a human-readable string."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def format_distance(kilometers: float) -> str:
    """Format distance in kilometers to a human-readable string."""
    if kilometers < 1:
        return f"{int(kilometers * 1000)}m"
    else:
        return f"{kilometers:.1f}km"

# Error handling
class AppException(Exception):
    """Base exception for application-specific exceptions."""
    def __init__(self, message: str, code: int = 400, **kwargs):
        self.message = message
        self.code = code
        self.kwargs = kwargs
        super().__init__(message)

class NotFoundException(AppException):
    """Raised when a resource is not found."""
    def __init__(self, resource: str, **kwargs):
        super().__init__(f"{resource} not found", 404, **kwargs)

class UnauthorizedException(AppException):
    """Raised when authentication or authorization fails."""
    def __init__(self, message: str = "Not authenticated", **kwargs):
        super().__init__(message, 401, **kwargs)

class ForbiddenException(AppException):
    """Raised when the user doesn't have permission to access a resource."""
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, 403, **kwargs)

# Request validation
def validate_coordinates(lat: float, lng: float) -> None:
    """Validate that coordinates are within valid ranges."""
    if not (-90 <= lat <= 90):
        raise HTTPException(
            status_code=400,
            detail=f"Latitude must be between -90 and 90, got {lat}"
        )
    if not (-180 <= lng <= 180):
        raise HTTPException(
            status_code=400,
            detail=f"Longitude must be between -180 and 180, got {lng}"
        )

# Rate limiting (simple in-memory implementation)
class RateLimiter:
    """Simple rate limiter for API endpoints."""
    def __init__(self, requests: int, window: int):
        self.requests = requests
        self.window = window  # in seconds
        self.requests_log = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if the client is allowed to make a request."""
        current_time = datetime.utcnow().timestamp()
        
        if client_id not in self.requests_log:
            self.requests_log[client_id] = []
        
        # Remove old requests outside the time window
        self.requests_log[client_id] = [
            t for t in self.requests_log[client_id]
            if current_time - t < self.window
        ]
        
        if len(self.requests_log[client_id]) < self.requests:
            self.requests_log[client_id].append(current_time)
            return True
        
        return False

# Initialize logger
logger = setup_logging()
