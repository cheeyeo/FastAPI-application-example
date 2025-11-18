#!/usr/bin/env bash

set -o errexit
set -o errtrace
set -o nounset
set -o pipefail

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
fastapi run --workers 4 app/main.py