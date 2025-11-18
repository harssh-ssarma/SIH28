#!/bin/bash

# Enterprise Celery Setup Script
# Quick start for Celery workers and Flower monitoring

set -e

echo "========================================="
echo "  Enterprise Celery Setup"
echo "  1000+ Universities Support"
echo "========================================="

# Check if Redis is running
echo ""
echo "[1/5] Checking Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Please start Redis first:"
    echo "   sudo systemctl start redis"
    echo "   OR"
    echo "   redis-server &"
    exit 1
fi
echo "✅ Redis is running"

# Check if PostgreSQL is running
echo ""
echo "[2/5] Checking PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL may not be running. Please verify."
fi

# Create Celery directories
echo ""
echo "[3/5] Creating Celery directories..."
mkdir -p /var/run/celery
mkdir -p /var/log/celery
chmod 755 /var/run/celery /var/log/celery
echo "✅ Directories created"

# Start Celery workers
echo ""
echo "[4/5] Starting Celery workers..."

# High priority workers (10 instances)
echo "  Starting HIGH priority workers (×10)..."
for i in {1..10}; do
    celery -A celery_config worker \
        --queue=timetable.high \
        --concurrency=1 \
        --max-tasks-per-child=5 \
        --loglevel=info \
        --hostname=worker-high-$i@%h \
        --pidfile=/var/run/celery/worker-high-$i.pid \
        --logfile=/var/log/celery/worker-high-$i.log \
        --detach
done

# Normal priority workers (20 instances)
echo "  Starting NORMAL priority workers (×20)..."
for i in {1..20}; do
    celery -A celery_config worker \
        --queue=timetable.normal \
        --concurrency=1 \
        --max-tasks-per-child=10 \
        --loglevel=info \
        --hostname=worker-normal-$i@%h \
        --pidfile=/var/run/celery/worker-normal-$i.pid \
        --logfile=/var/log/celery/worker-normal-$i.log \
        --detach
done

# Low priority workers (20 instances)
echo "  Starting LOW priority workers (×20)..."
for i in {1..20}; do
    celery -A celery_config worker \
        --queue=timetable.low \
        --concurrency=1 \
        --max-tasks-per-child=10 \
        --loglevel=info \
        --hostname=worker-low-$i@%h \
        --pidfile=/var/run/celery/worker-low-$i.pid \
        --logfile=/var/log/celery/worker-low-$i.log \
        --detach
done

# Callback workers (5 instances, high concurrency)
echo "  Starting CALLBACK workers (×5)..."
for i in {1..5}; do
    celery -A celery_config worker \
        --queue=callbacks \
        --concurrency=10 \
        --max-tasks-per-child=100 \
        --loglevel=info \
        --hostname=worker-callback-$i@%h \
        --pidfile=/var/run/celery/worker-callback-$i.pid \
        --logfile=/var/log/celery/worker-callback-$i.log \
        --detach
done

echo "✅ All workers started (55 total)"

# Start Celery Beat (scheduler)
echo ""
echo "[5/5] Starting Celery Beat scheduler..."
celery -A celery_config beat \
    --loglevel=info \
    --pidfile=/var/run/celery/beat.pid \
    --logfile=/var/log/celery/beat.log \
    --schedule=/var/run/celery/celerybeat-schedule \
    --detach
echo "✅ Celery Beat started"

# Start Flower monitoring
echo ""
echo "[BONUS] Starting Flower monitoring..."
celery -A celery_config flower \
    --port=5555 \
    --broker=redis://localhost:6379/0 \
    --basic_auth=admin:admin123 \
    --url_prefix=flower \
    --detach

echo ""
echo "========================================="
echo "  ✅ Enterprise Celery Setup Complete!"
echo "========================================="
echo ""
echo "Workers Started:"
echo "  - High Priority:   10 workers"
echo "  - Normal Priority: 20 workers"
echo "  - Low Priority:    20 workers"
echo "  - Callbacks:       5 workers (10 concurrency each)"
echo "  - TOTAL:           55 workers"
echo ""
echo "Monitoring:"
echo "  - Flower UI: http://localhost:5555"
echo "  - Username:  admin"
echo "  - Password:  admin123"
echo ""
echo "Logs:"
echo "  - /var/log/celery/worker-*.log"
echo "  - /var/log/celery/beat.log"
echo ""
echo "To stop all workers:"
echo "  ./scripts/stop_celery.sh"
echo ""
echo "To view status:"
echo "  celery -A celery_config inspect active"
echo "  celery -A celery_config inspect stats"
echo ""
