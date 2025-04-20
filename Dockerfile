# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system tools
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && apt-get clean

# Install latest pip
RUN pip install --upgrade pip

# Set work directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Install osv-scanner
RUN curl -LO https://github.com/google/osv-scanner/releases/latest/download/osv-scanner-linux-amd64 \
    && chmod +x osv-scanner-linux-amd64 \
    && mv osv-scanner-linux-amd64 /usr/local/bin/osv-scanner

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]