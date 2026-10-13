#!/usr/bin/env bash
set -euo pipefail
# Deletes ONE application Pod in this workshop profile; checks for a new Ready UID.
k() { minikube -p campus-workshop kubectl -- "$@"; }
k -n campus-workshop rollout status deployment/campus-app --timeout=120s
before=$(k -n campus-workshop get pods -l app=campus-app -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{end}')
pod=$(k -n campus-workshop get pods -l app=campus-app -o jsonpath='{.items[0].metadata.name}')
printf 'Deleting application Pod %s\n' "$pod"
k -n campus-workshop delete pod "$pod" --wait=true --timeout=90s
for ((i=0; i<60; i++)); do
  ready=$(k -n campus-workshop get deployment campus-app -o jsonpath='{.status.readyReplicas}')
  desired=$(k -n campus-workshop get deployment campus-app -o jsonpath='{.spec.replicas}')
  if [[ "$ready" == "$desired" ]]; then
    while read -r uid state; do
      if [[ "$state" == "True" && " $before " != *" $uid "* ]]; then
        echo 'PASS: a replacement Pod with a new UID is Ready.'
        k -n campus-workshop get pods -l app=campus-app -o wide
        exit 0
      fi
    done < <(k -n campus-workshop get pods -l app=campus-app -o jsonpath='{range .items[*]}{.metadata.uid}{" "}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}')
  fi
  sleep 2
done
echo 'Replacement did not become Ready within the timeout. Inspect events and Pod logs.' >&2
exit 1
