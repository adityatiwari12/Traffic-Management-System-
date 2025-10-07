# NYC Taxi Route Optimization - Backend

This is the backend service for the NYC Taxi Route Optimization application. It provides APIs for route optimization, travel time prediction, and analytics.

## Features

- **User Authentication**: JWT-based authentication system with role-based access control
- **Route Optimization**: Integration with OpenRouteService for route calculation
- **Travel Time Prediction**: Machine learning model for predicting taxi trip durations
- **Analytics Dashboard**: Endpoints for trip analytics and insights
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **Machine Learning**: Scikit-learn, XGBoost, LightGBM
- **Geospatial**: OpenRouteService API, OSRM
- **API Documentation**: Swagger UI & ReDoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   └── utils.py         # Utility functions
├── models/
│   ├── __init__.py
│   └── database.py      # Database models and configuration
├── routers/
│   ├── __init__.py
│   ├── auth.py          # Authentication endpoints
│   ├── routes.py        # Route optimization endpoints
│   ├── predictions.py   # Travel time prediction endpoints
│   └── admin.py         # Admin dashboard endpoints
├── static/              # Static files
├── tests/               # Test files
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- SQLite (included with Python) or PostgreSQL

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the example environment file and update it with your configuration:
   ```bash
   cp .env.example .env
   ```
5. Initialize the database:
   ```bash
   python init_db.py
   ```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access the following documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database
DATABASE_URL=sqlite:///./nyc_traffic.db

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouteService API
ORS_API_KEY=your-ors-api-key-here

# Admin User
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# Logging
LOG_LEVEL=INFO
```

## API Endpoints

### Authentication

- `POST /api/auth/token` - Get access token
- `GET /api/auth/me` - Get current user info

### Routes

- `POST /api/routes/optimize` - Get optimized route between two points
- `GET /api/routes/geocode` - Geocode an address

### Predictions

- `POST /api/predictions/predict` - Predict trip duration
- `GET /api/predictions/model-info` - Get model information

### Admin

- `GET /api/admin/analytics/summary` - Get analytics summary
- `GET /api/admin/analytics/zones` - Get zone analytics
- `GET /api/admin/analytics/timeseries` - Get time series data
- `GET /api/admin/system/status` - Get system status

## Development

### Running Tests

```bash
pytest
```

### Code Style

This project uses `black` for code formatting and `isort` for import sorting:

```bash
black .
isort .
```

### Database Migrations

This project uses SQLAlchemy with Alembic for database migrations. To create a new migration:

```bash
alembic revision --autogenerate -m "Your migration message"
alembic upgrade head
```

## Deployment

### Docker

Build and run the application using Docker:

```bash
docker-compose up --build
```

### Production

For production deployment, consider using:

- **ASGI Server**: Uvicorn with Gunicorn
- **Process Manager**: Systemd, Supervisor, or Docker
- **Reverse Proxy**: Nginx or Traefik
- **Database**: PostgreSQL with connection pooling (PgBouncer)
- **Caching**: Redis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
