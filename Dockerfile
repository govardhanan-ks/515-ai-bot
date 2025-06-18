# Use official Python base image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy .env if needed at runtime (can also mount via Docker run)
# COPY .env .env  # Optional if passing env vars at runtime

# Set default command
CMD ["python", "main.py"]
