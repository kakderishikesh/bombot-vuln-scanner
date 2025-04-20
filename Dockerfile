FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required packages including Go
RUN apt-get update && \
    apt-get install -y curl git gcc make wget tar build-essential && \
    wget https://golang.org/dl/go1.21.6.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz && \
    rm go1.21.6.linux-amd64.tar.gz

# Set Go environment variables
ENV PATH="/usr/local/go/bin:$PATH"

# Install osv-scanner from source
RUN go install github.com/google/osv-scanner/v2/cmd/osv-scanner@v2

# Copy Python app code
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]