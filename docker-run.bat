@echo off

REM Check if Docker is installed
docker --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not accessible.
    exit /b 1
)

REM Check if the Dockerfile exists
if not exist ".\Docker\gateway-app\Dockerfile" (
    echo Error: Dockerfile not found.
    exit /b 1
)

REM Run the Docker build command
docker build -t iot-gateway -f ".\Docker\gateway-app\Dockerfile" .
if %errorlevel% neq 0 (
    echo Error: Docker build failed.
    exit /b 1
)

REM Check if the Docker network named "iot" exists
docker network inspect iot > nul 2>&1
if %errorlevel% equ 0 (
    echo Docker network "iot" already exists.
) else (
    echo Creating Docker network "iot"...
    docker network create iot
    echo Docker network "iot" created.
)

REM Check if the container is already running
docker ps -q --filter "name=iot-gateway" > nul 2>&1
if %errorlevel% equ 0 (
    echo Stopping and removing existing container...
    docker stop iot-gateway > nul 2>&1
    docker rm iot-gateway > nul 2>&1
)

REM Run the Docker run command
docker run --name iot-gateway -it --network iot iot-gateway
if %errorlevel% neq 0 (
    echo Error: Docker RUN failed.
    exit /b 1
)