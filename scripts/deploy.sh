#!bin/bash

set -e

echo "Starting deployment..."

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "Error: .env file not found!"
  exit 1
fi

echo "Building new Docker images..."
docker compose -f docker-compose.prod.yml --env-file .env build --no-cache

echo "Performing rolling update..."
docker compose -f docker-compoes.prod.yml --env-file .env up -d --force-recreate --remove-oprhans

echo "Waiting for services t o be healthy..."
sleep 15

echo "Collecting static files..."
docker compose -f docker-compoes.prod.yml --env-file exec -T web python TutorApp/manage.py collectstatic --no-input

echo "Cleaning up old images..."
docker image prune -f

echo "completed!"


