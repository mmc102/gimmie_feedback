# Use an official Python runtime as a parent image
FROM python:3.12-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define a build-time argument
ARG DATABASE_URL

# Set the environment variable using the build-time argument
ENV DATABASE_URL=$DATABASE_URL
ENV MIDDLEWARE=$MIDDLEWARE

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Run the FastAPI application using Uvicorn
CMD ["gunicorn", "main:app","-k" , "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]

