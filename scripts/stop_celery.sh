#!/bin/bash

# Stop all Celery workers gracefully

set -e

echo "========================================="
echo "  Stopping Celery Workers"
echo "========================================="

# Stop all workers
echo ""
echo "Stopping all Celery workers..."

# Find all worker PIDs
if [ -d "/var/run/celery" ]; then
    for pidfile in /var/run/celery/worker-*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            if ps -p $pid > /dev/null 2>&1; then
                echo "  Stopping worker PID $pid..."
                kill -TERM $pid
                # Wait for graceful shutdown
                sleep 2
                # Force kill if still running
                if ps -p $pid > /dev/null 2>&1; then
                    kill -KILL $pid
                fi
            fi
            rm -f "$pidfile"
        fi
    done
fi

# Stop Celery Beat
echo ""
echo "Stopping Celery Beat..."
if [ -f "/var/run/celery/beat.pid" ]; then
    pid=$(cat /var/run/celery/beat.pid)
    if ps -p $pid > /dev/null 2>&1; then
        kill -TERM $pid
        sleep 1
    fi
    rm -f /var/run/celery/beat.pid
fi

# Stop Flower
echo ""
echo "Stopping Flower..."
pkill -f "celery.*flower" || true

echo ""
echo "========================================="
echo "  ✅ All Celery processes stopped"
echo "========================================="
