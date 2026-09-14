# Save this as backend/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# System deps needed for mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# The actual startup command (migrate + runserver, or celery worker/beat)
# is set per-service in docker-compose.yml, so no CMD is fixed here.
