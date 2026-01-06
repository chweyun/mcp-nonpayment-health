# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (default 8000)
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV DEBUG=False
ENV API_PREFIX=/nonpayment-health

# Run the server
CMD ["python", "run_server.py"]

