#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for PostgreSQL to start..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

# Apply database migrations
flask db upgrade

# Run the application
exec "$@"