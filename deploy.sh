#!/bin/bash
check_root_url() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
    if [ $response -eq 200 ]; then
        echo "Root URL returned 200 status code"
        return 0
    else
        echo "Root URL did not return 200 status code"
        return 1
    fi
}


cd
cd gimmie_feedback
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

# Check if the root URL returns 200 status code
if check_root_url; then
    echo "Deployment successful"
else
    echo "Deployment failed. Reverting to the previous image"
    # Revert to the previous image
    docker stop fastapi-container
    docker rm fastapi-container
    # Run the previous container
    docker run -d -p 8000:8000 --name fastapi-container previous-image
fi
