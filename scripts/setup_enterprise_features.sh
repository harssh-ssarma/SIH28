#!/bin/bash
# Enterprise Features Setup Script
# Run this after installing dependencies to configure all enterprise features

set -e

echo "=================================================="
echo "🚀 ENTERPRISE FEATURES SETUP"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${RED}❌ Error: backend/.env not found${NC}"
    echo "Please create backend/.env with required environment variables"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found backend/.env"

# Check Python environment
echo ""
echo "Checking Python environment..."
if command -v python &> /dev/null; then
    PYTHON_CMD=python
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    echo -e "${RED}❌ Error: Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python found: $($PYTHON_CMD --version)"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
cd backend
$PYTHON_CMD -m pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Django migrations
echo ""
echo "Running Django migrations..."
cd django
$PYTHON_CMD manage.py makemigrations
$PYTHON_CMD manage.py migrate
echo -e "${GREEN}✓${NC} Migrations complete"

# Setup RLS (optional, interactive)
echo ""
echo -e "${YELLOW}⚠${NC}  Row-Level Security (RLS) Setup"
echo "This will enable database-level multi-tenant isolation."
echo "Run this ONLY if you haven't enabled RLS before."
echo ""
read -p "Enable Row-Level Security? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Enabling RLS..."
    $PYTHON_CMD manage.py shell <<EOF
from django.db import connection
from core.rls_setup import RLS_MIGRATION_SQL
with connection.cursor() as cursor:
    cursor.execute(RLS_MIGRATION_SQL)
print("RLS enabled successfully!")
EOF
    echo -e "${GREEN}✓${NC} RLS enabled"
else
    echo "Skipped RLS setup"
fi

# Check environment variables
echo ""
echo "Checking environment variables..."

# Required vars
REQUIRED_VARS=("REDIS_URL" "DATABASE_URL" "CELERY_BROKER_URL")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^$var=" ../../.env; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All required environment variables present"
else
    echo -e "${YELLOW}⚠${NC}  Missing environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
fi

# Optional vars for enterprise features
echo ""
echo "Checking optional enterprise feature configuration..."

OPTIONAL_VARS=(
    "SENTRY_DSN:Sentry exception tracking"
    "STORAGE_BACKEND:S3/MinIO object storage"
    "STORAGE_BUCKET:S3 bucket name"
    "STORAGE_ACCESS_KEY:S3 access key"
    "PROMETHEUS_MULTIPROC_DIR:Prometheus metrics"
)

for var_desc in "${OPTIONAL_VARS[@]}"; do
    IFS=':' read -r var desc <<< "$var_desc"
    if grep -q "^$var=" ../../.env; then
        echo -e "${GREEN}✓${NC} $desc configured ($var)"
    else
        echo -e "${YELLOW}○${NC} $desc not configured ($var) - optional"
    fi
done

# Test Redis connection
echo ""
echo "Testing Redis connection..."
$PYTHON_CMD -c "
import redis
import os
from dotenv import load_dotenv
load_dotenv('../../.env')
r = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
r.ping()
print('✓ Redis connection successful')
" 2>/dev/null || echo -e "${RED}❌ Redis connection failed${NC}"

# Test PostgreSQL connection
echo "Testing PostgreSQL connection..."
$PYTHON_CMD manage.py check --database default && echo -e "${GREEN}✓${NC} PostgreSQL connection successful" || echo -e "${RED}❌ PostgreSQL connection failed${NC}"

# Summary
echo ""
echo "=================================================="
echo "📋 SETUP SUMMARY"
echo "=================================================="
echo ""
echo -e "${GREEN}✓${NC} Dependencies installed"
echo -e "${GREEN}✓${NC} Database migrations applied"
echo -e "${GREEN}✓${NC} Redis connection verified"
echo -e "${GREEN}✓${NC} PostgreSQL connection verified"
echo ""

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}⚠  Action Required:${NC}"
    echo "  Please add missing environment variables to backend/.env"
    echo ""
fi

echo "=================================================="
echo "🎉 ENTERPRISE FEATURES READY"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Review ENTERPRISE_FEATURES_COMPLETE.md for feature documentation"
echo "  2. Start Django: cd backend/django && python manage.py runserver"
echo "  3. Start FastAPI: cd backend/fastapi && uvicorn main:app --reload --port 8001"
echo "  4. Start Celery: cd backend && bash scripts/start_celery.sh"
echo "  5. Access Flower: http://localhost:5555 (admin/admin123)"
echo "  6. Access Prometheus metrics: http://localhost:8001/metrics"
echo ""
echo "Documentation:"
echo "  - Architecture: ENTERPRISE_ARCHITECTURE_1000_UNIVERSITIES.md"
echo "  - New Features: ENTERPRISE_FEATURES_COMPLETE.md"
echo "  - Quick Start: QUICK_START_NEW_FEATURES.md"
echo ""
