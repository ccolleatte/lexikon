#!/bin/bash
set -e

cd /app
export DATABASE_URL="postgresql://lexikon:lexikon@postgres:5432/lexikon"

echo "Installing dependencies..."
pip install -q -r requirements.txt

echo "Running Alembic migrations..."
alembic upgrade head

echo "✅ Migrations completed successfully!"
