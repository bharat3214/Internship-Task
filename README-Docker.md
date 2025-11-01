# Dynamic DB TODO List - Docker Setup

This is a containerized full-stack TODO application with React frontend and Flask backend.

## Prerequisites

- Docker and Docker Compose installed on your system
- `.env` file in the `backend` directory (copy from `.env.example` and fill in your values)

## Project Structure

```
Dynamic-DB-TODO-List/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   └── ...
├── docker-compose.yml
└── README-Docker.md
```

## Running the Application

### Method 1: Using Docker Compose (Recommended)

1. **Setup environment variables**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env file with your database credentials and JWT secret
   ```

2. **Build and start all services**:
   ```bash
   # From the root directory
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3003
   - Backend API: http://localhost:5000
   - Health check: http://localhost:5000/health

4. **Stop the application**:
   ```bash
   docker-compose down
   ```

### Method 2: Running Individual Services

#### Backend Only:
```bash
cd backend
docker build -t todo-backend .
docker run -p 5000:5000 --env-file .env todo-backend
```

#### Frontend Only:
```bash
cd frontend
docker build -t todo-frontend .
docker run -p 3003:3003 -e REACT_APP_API_URL=http://localhost:5000/api todo-frontend
```

## Development Mode

For development with file watching and hot reload:

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart frontend
docker-compose restart backend
```

## Environment Variables

### Backend (.env file):
```bash
MONGO_URI=your_mongodb_connection_string
POSTGRES_URI=your_postgresql_connection_string
JWT_SECRET_KEY=your_jwt_secret_key
```

### Frontend:
- `REACT_APP_API_URL`: Backend API URL (automatically set in docker-compose)
- `PORT`: Port for the React dev server (set to 3003)

## Useful Commands

```bash
# Build without cache
docker-compose build --no-cache

# View running containers
docker-compose ps

# Execute commands in running containers
docker-compose exec backend bash
docker-compose exec frontend sh

# View logs
docker-compose logs backend
docker-compose logs frontend

# Stop and remove containers, networks, images, and volumes
docker-compose down --rmi all --volumes --remove-orphans
```

## Troubleshooting

1. **Port already in use**: Make sure ports 3003 and 5000 are not used by other applications
2. **Database connection issues**: Check your `.env` file credentials
3. **Container won't start**: Check logs with `docker-compose logs [service-name]`
4. **Permission issues**: Make sure Docker has proper permissions on your system

## Health Checks

Both services include health checks:
- Backend: Checks `/health` endpoint
- Frontend: Checks if the React app is responding

You can check the health status with:
```bash
docker-compose ps
```

## Production Notes

For production deployment:
1. Set `FLASK_ENV=production` in backend environment
2. Build frontend for production and serve with nginx
3. Use proper secrets management instead of `.env` files
4. Configure proper logging and monitoring