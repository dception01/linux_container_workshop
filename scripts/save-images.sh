#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Run after building/pulling the complete stack. Exports images, not database data.
mapfile -t images < <(docker compose -f compose.yaml -f compose.lb.yaml config --images | sort -u)
docker image save -o workshop-images.tar "${images[@]}"
echo 'Created workshop-images.tar. Copy it together with the project ZIP.'
