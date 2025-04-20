# Use lightweight official Python image
FROM python:3.11-slim

# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    tar \
    unzip \
    && apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy dependency list and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install osv-scanner (correct .tar.gz build for Linux AMD64)
RUN curl -LO https://github.com/google/osv-scanner/releases/latest/download/osv-scanner_1.7.3_linux_amd64.tar.gz && \
    tar -xzf osv-scanner_1.7.3_linux_amd64.tar.gz && \
    mv osv-scanner /usr/local/bin/osv-scanner && \
    chmod +x /usr/local/bin/osv-scanner && \
    rm osv-scanner_1.7.3_linux_amd64.tar.gz

# Copy your application code into the container
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]