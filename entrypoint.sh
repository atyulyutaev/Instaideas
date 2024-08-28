#!/bin/bash
# Stop on error
set -e

# Run migrations
echo "Running migrations..."
python migrate.py

# Run the main application
echo "Starting main application..."
exec python run.py