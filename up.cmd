@echo off
where docker >nul 2>nul
if errorlevel 1 (
  echo Docker is not installed or not in PATH.
  echo Install Docker Desktop, then run this script again.
  echo For frontend-only preview, open http://127.0.0.1:7301/
  exit /b 1
)
if not exist .env copy .env.example .env >nul
docker compose --profile full up -d --build
echo.
echo Open http://127.0.0.1:7302
echo First build may take several minutes.
