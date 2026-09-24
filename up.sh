#!/usr/bin/env sh
set -e
cd "$(dirname "$0")"
[ -f .env ] || cp .env.example .env
docker compose --profile full up -d --build
echo
echo "Open http://127.0.0.1:7302"
echo "First build may take several minutes."
