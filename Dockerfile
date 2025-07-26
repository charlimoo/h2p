# Dockerfile

# Stage 1: Use the official Playwright base image.
# This ensures all system dependencies for browsers are pre-installed.
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set common Python environment variables for containerized apps.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- Security: Create a non-root user to run the application ---
# This follows the best practice from your original Dockerfile.
RUN groupadd --system app && useradd --system --gid app --no-create-home app

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching.
COPY requirements.txt .

# Install the Python dependencies using pip.
RUN pip install --no-cache-dir -r requirements.txt

# Install the browser binaries required by Playwright.
# We only need chromium for this specific service.
RUN playwright install chromium

# Copy your application's source code into the container.
COPY app.py .

# Change ownership of the application code to the non-root user.
RUN chown -R app:app /app

# Switch from the root user to the newly created 'app' user.
USER app

# Expose the port that the application will listen on.
EXPOSE 5000

# Define the command to run the application using Gunicorn.
# This runs as the non-root 'app' user.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=4", "app:app"]
