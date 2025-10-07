# Traffic Management System - Setup Guide

## Prerequisites

- Python 3.8 or higher
- Node.js 14+ (for frontend development)
- PostgreSQL 12+ (or SQLite for development)
- Git

## Backend Setup

### 1. Clone the Repository

```bash
git clone https://github.com/adityatiwari12/Traffic-Management-System-.git
cd Traffic-Management-System-
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost/traffic_db
# For SQLite (development):
# DATABASE_URL=sqlite:///./traffic.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 5. Database Setup

Initialize the database:

```bash
python init_db.py
```

### 6. Run the Backend

```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Option A: Simple HTML Setup

For basic development, you can serve the HTML files directly:

```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx live-server --port=8080
```

### 2. Option B: Advanced Setup with Build Tools

If you want to use modern build tools:

```bash
# Initialize npm project
npm init -y

# Install development dependencies
npm install --save-dev vite
npm install --save-dev @vitejs/plugin-legacy

# Add scripts to package.json
```

Add to `package.json`:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

Create `vite.config.js`:
```javascript
import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'

export default defineConfig({
  plugins: [
    legacy({
      targets: ['defaults', 'not IE 11']
    })
  ],
  server: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 3. Run Frontend

```bash
# Simple server
python -m http.server 8080

# Or with Vite (if configured)
npm run dev
```

The frontend will be available at `http://localhost:8080`

## Docker Setup (Optional)

### 1. Using Docker Compose

```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### 2. Individual Docker Containers

Backend:
```bash
cd backend
docker build -t traffic-backend .
docker run -p 8000:8000 --env-file .env traffic-backend
```

## Database Configuration

### PostgreSQL Setup

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE traffic_db;
CREATE USER traffic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE traffic_db TO traffic_user;
```

3. Update `.env` file with connection details

### SQLite Setup (Development)

For development, you can use SQLite:
```env
DATABASE_URL=sqlite:///./traffic.db
```

## API Keys Setup

### Google Maps API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Maps JavaScript API and Directions API
4. Create credentials (API Key)
5. Add the key to your `.env` file

### OpenWeather API

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your free API key
3. Add to `.env` file

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
# If using npm setup
npm test
```

## Production Deployment

### Backend Deployment

1. **Using Gunicorn:**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Using Docker:**
```bash
docker build -t traffic-backend .
docker run -p 8000:8000 --env-file .env traffic-backend
```

### Frontend Deployment

1. **Static Hosting (Netlify, Vercel):**
```bash
# Build if using build tools
npm run build
# Deploy dist/ folder
```

2. **Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/frontend;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
```bash
# Find process using port
netstat -ano | findstr :8000
# Kill process
taskkill /PID <process_id> /F
```

2. **Database connection errors:**
- Check database is running
- Verify connection string in `.env`
- Ensure database exists

3. **CORS errors:**
- Add frontend URL to `ALLOWED_ORIGINS` in `.env`
- Check backend CORS configuration

4. **API key errors:**
- Verify API keys are correct
- Check API quotas and limits
- Ensure APIs are enabled in respective consoles

### Logs

Backend logs:
```bash
# Check application logs
tail -f logs/app.log

# Docker logs
docker logs container_name
```

## Development Tips

1. **Hot Reload:** Both frontend and backend support hot reload in development
2. **API Documentation:** Visit `http://localhost:8000/docs` for interactive API docs
3. **Database Admin:** Use tools like pgAdmin or DBeaver for database management
4. **Code Quality:** Use linters and formatters (black, flake8 for Python)

## Support

For issues and questions:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Include logs and error messages
4. Specify your environment (OS, Python version, etc.)
