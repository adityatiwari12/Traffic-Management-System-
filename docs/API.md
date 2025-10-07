# Traffic Management System API Documentation

## Overview

The Traffic Management System API provides endpoints for traffic prediction, route optimization, and real-time traffic monitoring.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login with username and password.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user_id": "integer"
}
```

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

### Traffic Predictions

#### GET /predictions/current
Get current traffic predictions for all monitored routes.

**Response:**
```json
{
  "predictions": [
    {
      "route_id": "string",
      "current_traffic_level": "integer",
      "predicted_traffic_level": "integer",
      "prediction_time": "datetime",
      "confidence": "float"
    }
  ]
}
```

#### POST /predictions/route
Get traffic prediction for a specific route.

**Request Body:**
```json
{
  "start_location": {
    "latitude": "float",
    "longitude": "float"
  },
  "end_location": {
    "latitude": "float",
    "longitude": "float"
  },
  "departure_time": "datetime"
}
```

**Response:**
```json
{
  "route_id": "string",
  "estimated_duration": "integer",
  "traffic_level": "integer",
  "alternative_routes": [
    {
      "route_id": "string",
      "estimated_duration": "integer",
      "traffic_level": "integer"
    }
  ]
}
```

### Routes Management

#### GET /routes/
Get all available routes.

**Query Parameters:**
- `limit`: Maximum number of routes to return (default: 100)
- `offset`: Number of routes to skip (default: 0)

**Response:**
```json
{
  "routes": [
    {
      "id": "string",
      "name": "string",
      "start_point": {
        "latitude": "float",
        "longitude": "float"
      },
      "end_point": {
        "latitude": "float",
        "longitude": "float"
      },
      "distance": "float",
      "average_duration": "integer"
    }
  ],
  "total": "integer"
}
```

#### POST /routes/
Create a new route.

**Request Body:**
```json
{
  "name": "string",
  "start_point": {
    "latitude": "float",
    "longitude": "float"
  },
  "end_point": {
    "latitude": "float",
    "longitude": "float"
  },
  "waypoints": [
    {
      "latitude": "float",
      "longitude": "float"
    }
  ]
}
```

#### GET /routes/{route_id}
Get details of a specific route.

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "start_point": {
    "latitude": "float",
    "longitude": "float"
  },
  "end_point": {
    "latitude": "float",
    "longitude": "float"
  },
  "waypoints": [
    {
      "latitude": "float",
      "longitude": "float"
    }
  ],
  "distance": "float",
  "average_duration": "integer",
  "traffic_history": [
    {
      "timestamp": "datetime",
      "traffic_level": "integer",
      "duration": "integer"
    }
  ]
}
```

### Admin Endpoints

#### GET /admin/stats
Get system statistics (Admin only).

**Response:**
```json
{
  "total_routes": "integer",
  "total_predictions": "integer",
  "active_users": "integer",
  "system_uptime": "string",
  "average_response_time": "float"
}
```

#### GET /admin/users
Get all users (Admin only).

**Response:**
```json
{
  "users": [
    {
      "id": "integer",
      "username": "string",
      "email": "string",
      "full_name": "string",
      "is_active": "boolean",
      "created_at": "datetime"
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated users

## Data Models

### Traffic Level
Integer values representing traffic density:
- 1: Light traffic
- 2: Moderate traffic
- 3: Heavy traffic
- 4: Severe congestion

### Location
```json
{
  "latitude": "float",
  "longitude": "float"
}
```

### Route
```json
{
  "id": "string",
  "name": "string",
  "start_point": "Location",
  "end_point": "Location",
  "waypoints": ["Location"],
  "distance": "float",
  "average_duration": "integer"
}
```

### User
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "is_active": "boolean",
  "created_at": "datetime"
}
```
