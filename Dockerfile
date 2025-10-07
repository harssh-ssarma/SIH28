# Multi-stage Dockerfile for SIH28 Timetable Management System
# This dockerfile builds all services for production deployment

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
# Install dependencies and fix vulnerabilities
RUN npm ci --only=production && npm audit fix --force || true
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Django Backend
FROM python:3.11-slim AS django-builder
WORKDIR /app/backend/django
# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
COPY backend/django/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY backend/django/ ./
RUN python manage.py collectstatic --noinput

# Stage 3: Build FastAPI Service
FROM python:3.11-slim AS fastapi-builder
WORKDIR /app/backend/fastapi
# Install system dependencies for ortools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*
COPY backend/fastapi/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
COPY backend/fastapi/ ./

# Stage 4: Frontend Production
FROM node:18-alpine AS frontend-production
WORKDIR /app
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder /app/frontend/public ./public
EXPOSE 3000
CMD ["node", "server.js"]

# Stage 5: Django Production  
FROM python:3.11-slim AS django-production
WORKDIR /app
COPY --from=django-builder /app/backend/django ./
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "erp.wsgi:application"]

# Stage 6: FastAPI Production
FROM python:3.11-slim AS fastapi-production
WORKDIR /app
COPY --from=fastapi-builder /app/backend/fastapi ./
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
CMD ["/docker-entrypoint.sh"]