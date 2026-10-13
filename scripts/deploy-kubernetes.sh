#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null
command -v minikube >/dev/null
minikube -p campus-workshop status >/dev/null
k() { minikube -p campus-workshop kubectl -- "$@"; }
# Build once and make the image available inside this Minikube profile.
docker build -t campus-feedback:k8s-v1 .
minikube -p campus-workshop image load campus-feedback:k8s-v1
k apply -f kubernetes/00-namespace.yaml
k apply -f kubernetes/01-config.yaml
k apply -f kubernetes/02-database.yaml
k -n campus-workshop rollout status deployment/campus-db --timeout=180s
k apply -f kubernetes/03-application.yaml
k -n campus-workshop rollout status deployment/campus-app --timeout=180s
k -n campus-workshop get pods,svc,pvc
printf '\nOpen the URL from: minikube -p campus-workshop service campus-app -n campus-workshop --url\n'
