#!/bin/sh

set -eu

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Seeding initial data..."
python manage.py seed_data

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting application..."
exec "$@"