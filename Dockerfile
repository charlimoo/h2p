# Use an official Python runtime as a parent image
# Using a 'slim' version keeps the image smaller
FROM python:3.10-slim-bullseye

# Set environment variables
# 1. Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# 2. Prevents apt-get from asking for user input
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by Chromium browser and fonts
# - chromium: The headless browser
# - fonts-liberation: Provides necessary fonts to prevent text rendering as squares
# - We clean up the apt cache to reduce image size
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir reduces layer size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Inform Docker that the container listens on port 5001
EXPOSE 5001

# Command to run the application using Gunicorn
# -w 4: Use 4 worker processes
# -b 0.0.0.0:5001: Bind to all network interfaces on port 5001, making it accessible from outside the container
# app:app: The first 'app' is the filename (app.py), the second is the Flask application object inside the file
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
