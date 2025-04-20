# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/go/bin:$PATH"

# Install system tools and Go
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    gcc \
    build-essential \
    && apt-get clean

# Install Go
ENV GOLANG_VERSION=1.22.2
RUN wget https://go.dev/dl/go$GOLANG_VERSION.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go$GOLANG_VERSION.linux-amd64.tar.gz && \
    rm go$GOLANG_VERSION.linux-amd64.tar.gz
ENV PATH=$PATH:/usr/local/go/bin

# Install osv-scanner
RUN go install github.com/google/osv-scanner/v2/cmd/osv-scanner@v2 && \
    cp /root/go/bin/osv-scanner /usr/local/bin/osv-scanner

# Create app directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for Uvicorn
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
