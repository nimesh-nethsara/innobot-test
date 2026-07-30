@echo off
echo Starting Clinic Appointment System Deployment...

REM 1. Build and start all containers in the background
docker-compose up -d --build

REM 2. Wait 5 seconds for PostgreSQL to fully initialize
echo Waiting for database to initialize...
timeout /t 5 /nobreak >nul

REM 3. Create database tables inside the running backend container
echo Creating database tables...
docker exec -it clinic_backend python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo ==================================================
echo Deployment Successful!
echo Frontend UI: http://localhost:3000
echo Backend API: http://localhost:5000
echo ==================================================
pause