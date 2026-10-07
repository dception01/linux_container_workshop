# 03 — Load balancing, persistence and troubleshooting

## Add app2 and NGINX

After building/running stage 02:

```bash
docker compose -f compose.yaml -f compose.lb.yaml pull nginx
docker compose -f compose.yaml -f compose.lb.yaml up -d --pull never --wait
```

The `--pull never` option ensures the unpublished application image is used from local storage.

Use **http://localhost:8081** for NGINX. Port 8080 still reaches app1 directly.

```bash
for i in $(seq 1 10); do curl -s http://localhost:8081/healthz; echo; done
```

Submit feedback through 8081; both replicas see the same records because both use PostgreSQL. Replicas run the same image, with different INSTANCE_NAME values. This is manual scaling, not autoscaling.

## Stop one instance

```bash
docker compose -f compose.yaml -f compose.lb.yaml stop app1
for i in $(seq 1 10); do curl -s http://localhost:8081/healthz; echo; done
docker compose -f compose.yaml -f compose.lb.yaml start app1
```

NGINX passively detects failures and retries eligible requests. Expect remaining successful requests to show app-2; perfect continuity is not guaranteed. POST retries are deliberately not enabled for already-sent requests to avoid duplicate writes. After recovery, allow the five-second failure timeout to expire.

NGINX resolves these upstream names on startup. If a container is **recreated** with a different IP (rather than merely stopped/started), reload its configuration using `docker compose -f compose.yaml -f compose.lb.yaml exec nginx nginx -s reload`, or restart NGINX.

## Prove persistence

Submit a memorable feedback entry first. Then:

```bash
docker compose -f compose.yaml -f compose.lb.yaml down
docker compose -f compose.yaml -f compose.lb.yaml up -d --pull never --wait
```

The old containers were removed; the named database volume remained. Confirm the feedback is still present. `docker volume ls` shows `campus-workshop_campus-data`.

## Deliberate failure exercise

```bash
docker compose -f compose.yaml -f compose.lb.yaml stop db
curl -i http://localhost:8080/readyz
curl -i http://localhost:8080/healthz
docker compose -f compose.yaml -f compose.lb.yaml start db
```

Readiness fails but liveness still succeeds. The page reports database unavailable. A healthcheck does not itself restart an unhealthy container or give NGINX active health checking.

## Intentional reset only

The following deletes **all workshop feedback**:

```bash
docker compose -f compose.yaml -f compose.lb.yaml down -v
```

No reset is required for normal shutdown.

Connection to Kubernetes/OpenShift: app replicas map conceptually to Deployment replicas, internal discovery to Services, configuration to ConfigMaps/Secrets, database storage to PVCs, and entry routing to Ingress/Routes. This lab does not implement a Kubernetes cluster or host/database high availability.
