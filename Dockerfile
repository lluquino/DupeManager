# DupeManager — Dockerfile

FROM python:3.12-slim AS base

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ backend/
COPY frontend/ frontend/
COPY .env.example .env.example

# Create data directory
RUN mkdir -p data

EXPOSE 8097

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8097"]
