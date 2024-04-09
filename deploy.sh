#!/bin/bash

# Pull the latest changes from the master branch
git pull origin main

# Build a new Docker image
docker build --build-arg DATABASE_URL=$DATABASE_URL -t fastapi-app .

# Apply Alembic migrations
docker run --rm -v $(pwd)/alembic:/alembic fastapi-app alembic upgrade head


# Stop and remove the existing container (if any)
docker stop fastapi-container
docker rm fastapi-container

# Run a new container using the newly built image
docker run -d -p 8000:8000 --name fastapi-container fastapi-app
