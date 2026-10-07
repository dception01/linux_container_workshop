# 02 — Build the application and connect storage

All commands run from the repository root inside Ubuntu. Copy `.env.example` to `.env` if not done already.

## A. Build and run the web app alone

```bash
docker build -t ghcr.io/dception01/campus-feedback:workshop-v1 .
docker run -d --name campus-preview -p 8080:8000   -e TEAM_NAME="Team Linux" -e INSTANCE_NAME=preview   ghcr.io/dception01/campus-feedback:workshop-v1
curl http://localhost:8080/healthz
```

Open http://localhost:8080. The landing page loads and displays **Database: Not connected**. Feedback entry is disabled until storage is available. Inspect `Dockerfile`: base image, working directory, dependencies, copy, user and command. `EXPOSE` documents the container port; `-p` publishes it.

```bash
docker logs campus-preview
docker rm -f campus-preview
```

The preview must be removed to release port 8080.

## B. Start the database and application

The image from A is already local:

```bash
docker compose up -d --wait
docker compose ps
```

Alternatively, build and start in one step:

```bash
docker compose -f compose.yaml -f compose.build.yaml up -d --build --wait
```

Open port 8080 and submit feedback, or:

```bash
curl -i -X POST http://localhost:8080/feedback   --data-urlencode 'team=Team Linux'   --data-urlencode 'rating=5'   --data-urlencode 'comment=We connected our first database!'
curl http://localhost:8080/readyz
```

POST should return **303** (redirect to the page). `/healthz` checks the application process; `/readyz` checks database/schema access and returns 503 if unavailable.

Inspect real records and service-name resolution:

```bash
docker compose exec db psql -U campus -d campus -c 'SELECT * FROM feedback;'
docker compose exec app1 python -c "import socket; print(socket.gethostbyname('db'))"
docker compose logs --tail=30 app1 db
```

If you change the example database username/name, update the psql command accordingly.

## C. Observe networking without Compose (optional instructor exercise)

After stopping the Compose stack with `docker compose down`, reproduce it with individual containers. This uses a separate volume so it does not alter the Compose database:

```bash
docker network create campus-manual
docker volume create campus-manual-data
docker run -d --name db-manual --network campus-manual --network-alias db   --env-file .env   -v campus-manual-data:/var/lib/postgresql/data   -v "$PWD/db/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro"   postgres:17.6-bookworm
docker logs db-manual
```

Wait for PostgreSQL's final "ready to accept connections" message, then:

```bash
docker run -d --name app-manual --network campus-manual --env-file .env   -e DB_HOST=db -e INSTANCE_NAME=manual -p 8080:8000   ghcr.io/dception01/campus-feedback:workshop-v1
```

`--env-file` and Compose parse quoted values differently, so TEAM_NAME may show literal quotes in this optional exercise. Override it with `-e TEAM_NAME="Team Linux"` if needed.

After testing, clean up the manual containers and network (volume retained):

```bash
docker rm -f app-manual db-manual
docker network rm campus-manual
docker compose up -d --wait
```

Checkpoint: explain why DB_HOST is `db`, not localhost, and why both services can use their standard internal ports.
