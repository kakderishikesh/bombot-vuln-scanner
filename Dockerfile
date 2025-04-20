FROM python:3.11-slim

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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Correct download of osv-scanner tar.gz archive
RUN curl -LO https://github.com/google/osv-scanner/releases/download/v1.7.3/osv-scanner_1.7.3_linux_amd64.tar.gz && \
    tar -xzf osv-scanner_1.7.3_linux_amd64.tar.gz && \
    mv osv-scanner /usr/local/bin/osv-scanner && \
    chmod +x /usr/local/bin/osv-scanner && \
    rm osv-scanner_1.7.3_linux_amd64.tar.gz

# Copy application source code
COPY . .

EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]