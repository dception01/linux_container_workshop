#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker --version
docker compose version
docker info >/dev/null
test -f .env || { echo 'Run: cp .env.example .env'; exit 1; }
docker compose -f compose.yaml -f compose.lb.yaml config --quiet
echo 'Preflight passed. Ensure ports 8080 and 8081 are available.'
