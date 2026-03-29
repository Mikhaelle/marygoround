#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h postgres -U "${POSTGRES_USER:-merygoround}" -q 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL is ready."

echo "Running database migrations..."
cd /app && alembic upgrade head

echo "Starting application..."
exec "$@"
