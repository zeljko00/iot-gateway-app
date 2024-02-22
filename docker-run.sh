#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not accessible."
    exit 1
fi

# Check if the Dockerfile exists
if [ ! -f "./Docker/gateway-app/Dockerfile" ]; then
    echo "Error: Dockerfile not found."
    exit 1
fi

# Run the Docker build command
docker build -t iot-gateway -f "./Docker/gateway-app/Dockerfile" .
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed."
    exit 1
fi

# Check if the Docker network named "iot" exists
if docker network inspect iot &> /dev/null; then
    echo "Docker network 'iot' already exists."
else
    echo "Creating Docker network 'iot'..."
    docker network create iot
    echo "Docker network 'iot' created."
fi

# Check if the container is already running
if docker ps -q --filter "name=iot-gateway" &> /dev/null; then
    echo "Stopping and removing existing container..."
    docker stop iot-gateway > /dev/null
    docker rm iot-gateway > /dev/null
fi

# Run the Docker run command
docker run --name iot-gateway -it --network iot iot-gateway
if [ $? -ne 0 ]; then
    echo "Error: Docker RUN failed."
    exit 1
fi

echo "Docker build successful."
