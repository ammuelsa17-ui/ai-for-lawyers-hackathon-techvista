FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and ensure schema.sql is present
COPY app/ ./app/
COPY scripts/ ./scripts/

# Create data directory for SQLite persistence
RUN mkdir -p /app/data

ENV DATABASE_PATH=/app/data/casepilot.db
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
