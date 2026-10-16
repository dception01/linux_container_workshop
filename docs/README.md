# Docker Workshop: Installation and Hands-on Labs

Build a Flask application, package it as an image, and connect it to Redis using Docker Compose.

## Contents

1. [Before you begin](#1-before-you-begin)
2. [Install OpenSSH and Docker](#2-install-openssh-and-docker)
3. [Lab 1: Run a Flask application in Docker](#3-lab-1-run-a-flask-application-in-docker)
4. [Understand the Dockerfile](#4-understand-the-dockerfile)
5. [Lab 2: Connect Flask and Redis with Compose](#5-lab-2-connect-flask-and-redis-with-compose)
6. [Test networking and persistence](#6-test-networking-and-persistence)
7. [Manage and troubleshoot containers](#7-manage-and-troubleshoot-containers)
8. [Command reference and completion checklist](#8-command-reference-and-completion-checklist)

## 1. Before you begin

**Environment:** an Ubuntu VM with a sudo-enabled user, internet access, and a terminal running Bash. Ubuntu 24.04 LTS is a suitable workshop baseline. Run commands inside the Ubuntu VM unless a step says otherwise.

These are two standalone introductory labs from the installation notes. They use port **5000** and are separate from the Campus Feedback project, which uses PostgreSQL and ports 8080/8081.

- Copy code blocks using GitHub's copy button. Do not copy terminal prompts or output.
- Run blocks in order. Blocks beginning with `cat > filename <<'EOF'` create files: copy the entire block, including the final `EOF` line.
- File-creation blocks overwrite files with the same names. Use the lab directories below.
- No shell aliases are required. All Compose commands are written in full.
- The Flask development server is used here for learning. Production deployments should use a suitable WSGI server, such as Gunicorn.

| Location | Browser address |
| --- | --- |
| Browser inside Ubuntu VM | `http://localhost:5000` |
| Browser on your laptop | `http://VM_IP:5000` — replace `VM_IP` with the VM's reachable address |

`localhost` refers to the machine where the browser or command runs. Find the VM address with `ip -br address`; use the VMware network interface address, not a Docker bridge. Host-to-VM access depends on VMware networking and firewall settings.

## 2. Install OpenSSH and Docker

If Docker and Compose already work, skip installation and go to **2.5**. The installation sequence below is for a fresh Ubuntu lab VM. If another Docker distribution is installed, review the official installation guide's conflicting-package instructions before changing it.

### 2.1 Install basic tools and optional SSH access

Refresh the package index and install the tools used in the workshop:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git nano openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh --no-pager
```

`enable --now` starts the service and enables it at boot. SSH is optional when working directly in the VM console. When using SSH from a laptop, substitute your real username and VM address:

```bash
ssh YOUR_USERNAME@VM_IP
```

### 2.2 Add Docker's official package repository

Download the repository signing key:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Register the Ubuntu repository. The shell inserts your Ubuntu codename and CPU architecture:

```bash
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

If you previously configured Docker through `docker.list`, do not add a second duplicate entry; use the existing working setup or ask the instructor to reconcile it.

### 2.3 Install Docker Engine and the Compose plugin

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo systemctl status docker --no-pager
```

### 2.4 Allow Docker commands without sudo

```bash
sudo usermod -aG docker "$USER"
```

Log out and back in, or run the following command separately to start a shell with the new group membership:

```bash
newgrp docker
```

Membership in the `docker` group grants root-level control over this VM. Use it only for trusted lab users.

### 2.5 Verify installation

```bash
cat /etc/os-release
docker --version
docker compose version
git --version
docker info
docker run --rm hello-world
```

**Checkpoint:** `hello-world` prints a success message, and `docker compose version` succeeds. The test container exits and is removed by `--rm`; its image remains downloaded.

## 3. Lab 1: Run a Flask application in Docker

**Goal:** build an image from source and serve a page through a published port.

### 3.1 Create the project directory

```bash
mkdir -p ~/docker-workshop-demo
cd ~/docker-workshop-demo
pwd
```

### 3.2 Create the application

The following block writes `app.py`:

```bash
cat > app.py <<'EOF'
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>Workshop Demo: Hello from inside Docker!</h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF
```

Binding to `0.0.0.0` lets the app receive traffic through the container's network interfaces.

### 3.3 Create the dependency file

These version pins are retained from the workshop notes; they are lab examples, not a claim that these are the latest releases.

```bash
cat > requirements.txt <<'EOF'
Flask==3.0.3
EOF
```

### 3.4 Create the Dockerfile

The filename must be exactly `Dockerfile`, with no extension:

```bash
cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
EOF
```

### 3.5 Exclude unnecessary build files

```bash
cat > .dockerignore <<'EOF'
.git
__pycache__/
*.pyc
.env
.venv/
venv/
EOF
```

### 3.6 Build and run

```bash
docker build -t workshop-web-app:1.0 .
docker image ls workshop-web-app
docker run -d --name my-running-app -p 5000:5000 workshop-web-app:1.0
docker ps
```

| Option | Meaning |
| --- | --- |
| `-t workshop-web-app:1.0` | Assign an image name and tag |
| Final `.` in `docker build` | Use the current directory as the build context |
| `-d` | Run in the background |
| `--name my-running-app` | Give the container a predictable name |
| `-p 5000:5000` | Map VM port 5000 to container port 5000 |

### 3.7 Test and inspect

```bash
curl http://localhost:5000
docker logs --tail=20 my-running-app
docker exec my-running-app pwd
docker exec my-running-app ls -la /app
```

**Checkpoint:** the browser and `curl` display “Workshop Demo: Hello from inside Docker!”

**Try it:** edit the heading with `nano app.py`. Refresh the browser. It will still show the old heading because the running container uses the code copied into its image. Rebuild and replace it:

```bash
docker build -t workshop-web-app:1.0 .
docker stop my-running-app
docker rm my-running-app
docker run -d --name my-running-app -p 5000:5000 workshop-web-app:1.0
curl http://localhost:5000
```

### 3.8 Finish Lab 1

Free port 5000 before beginning Lab 2:

```bash
docker stop my-running-app
docker rm my-running-app
```

The image remains available. Removing the container does not remove its image.

## 4. Understand the Dockerfile

A Dockerfile describes how to build an image. Filesystem-changing instructions can create filesystem layers; metadata instructions configure image settings rather than each adding a new filesystem layer.

| Instruction | Purpose in this lab |
| --- | --- |
| `FROM python:3.12-slim` | Choose the base image; `ARG` may legally appear before `FROM` |
| `WORKDIR /app` | Set the working directory; create it if needed |
| `COPY requirements.txt .` | Copy dependencies from the build context into `/app` |
| `RUN pip install ...` | Install packages during the build |
| `COPY . .` | Copy the remaining build-context files into the working directory |
| `EXPOSE 5000` | Document the intended container port; it does not publish the port |
| `CMD ["python", "app.py"]` | Supply the default startup command |
| `ENV NAME=value` | Set an environment variable in the image |
| `ENTRYPOINT ["program"]` | Define the executable; runtime arguments usually become its arguments |

### What do the two dots in `COPY . .` mean?

The first dot means the root of the build context, excluding `.dockerignore` matches. The second means the current directory inside the image, set here by `WORKDIR /app`. In this Dockerfile, `COPY . .` has the same destination as `COPY . /app/`.

### Why copy requirements before application code?

Separating the dependency copy allows the dependency installation step to remain cached when only `app.py` changes. A changed dependency file invalidates that step and later steps. Cache reuse also depends on the build inputs and available cache; it is not guaranteed solely by an unchanged filename.

### Why use the JSON form of CMD?

`CMD ["python", "app.py"]` launches Python without an extra shell wrapper. This gives the main process direct signal delivery. Graceful shutdown still depends on how the application handles signals. Shell-form `CMD python app.py` adds a shell that may not forward signals as intended.

## 5. Lab 2: Connect Flask and Redis with Compose

**Goal:** run two services on a shared network and store a visit counter in Redis.

| Component | Role | Address |
| --- | --- | --- |
| Browser | Requests the page | VM port 5000 |
| `web` service | Flask application; increments and displays the counter | Container port 5000 |
| `redis` service | Stores the `hits` key | `redis:6379` within the Compose network |
| `redis_data` volume | Keeps Redis files across container replacement | Mounted at `/data` |

Each page request goes to Flask. Flask increments `hits` in Redis and returns the resulting number. Redis has no published host port in this lab.

### 5.1 Create a separate project directory

```bash
mkdir -p ~/compose-demo
cd ~/compose-demo
```

### 5.2 Create the application

```bash
cat > app.py <<'EOF'
import time

from flask import Flask
import redis

app = Flask(__name__)
r = redis.Redis(host="redis", port=6379, socket_connect_timeout=2, socket_timeout=2)


def get_hit_count():
    for attempt in range(6):
        try:
            return r.incr("hits")
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            if attempt == 5:
                raise
            time.sleep(0.5)


@app.route("/")
def home():
    count = get_hit_count()
    return (
        "<h1>Docker Compose Workshop Demo</h1>"
        f"<p>This page has been viewed <strong>{count}</strong> times.</p>"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
EOF
```

The hostname `redis` matches the Compose service name. `localhost` inside `web` would refer to the web container itself, not Redis. Retries help with temporary connection problems; they do not guarantee that every request succeeds during an outage.

### 5.3 Create dependencies and build files

```bash
cat > requirements.txt <<'EOF'
Flask==3.0.3
redis==5.0.4
EOF
```

```bash
cat > Dockerfile <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
EOF
```

```bash
cat > .dockerignore <<'EOF'
.git
__pycache__/
*.pyc
.env
.venv/
venv/
EOF
```

### 5.4 Create compose.yaml

Copy the entire block; YAML indentation uses spaces, not tabs:

```bash
cat > compose.yaml <<'EOF'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  redis:
    image: redis:7.4-alpine
    command: ["redis-server", "--appendonly", "yes", "--appendfsync", "everysec"]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 2s
      timeout: 2s
      retries: 15
      start_period: 5s
    volumes:
      - redis_data:/data

volumes:
  redis_data:
EOF
```

| Configuration | Purpose |
| --- | --- |
| `build: .` | Build the web image from this directory |
| `ports` | Publish the web port on the VM |
| `depends_on` with `service_healthy` | Wait for Redis's startup health check before starting web |
| Redis health check | Run `redis-cli ping`; healthy Redis responds `PONG` |
| `restart: unless-stopped` | Restart exited containers unless deliberately stopped |
| Redis AOF options | Record writes to disk; flush approximately every second |
| `redis_data:/data` | Store persistence files in a named volume |

The volume preserves files; Redis persistence settings determine what gets written to those files. AOF with `everysec` can lose roughly the latest second of writes after an abrupt failure. This exercise uses an orderly shutdown.

These image tags may receive updates. Rehearse with the downloaded images before the event; the guide does not lock images to immutable digests.

### 5.5 Validate, build and start

```bash
docker compose config
docker compose up -d --build --wait
docker compose ps
```

Compose builds `web`, pulls Redis, creates a default network and named volume, and starts the services. Redis should show as healthy; web has no health check here, so verify it with an HTTP request.

```bash
curl http://localhost:5000
docker compose exec redis redis-cli ping
```

**Checkpoint:** the page shows a visit count and Redis returns `PONG`. Refresh the page to increase the count.

## 6. Test networking and persistence

Run all commands in this section from `~/compose-demo`.

### 6.1 Resolve the Redis service name

```bash
docker compose exec web python -c "import socket; print(socket.gethostbyname('redis'))"
```

**Expected:** an internal container-network IP address. This proves service-name resolution; it is not a complete test of network isolation.

### 6.2 Verify the value directly in Redis

```bash
docker compose exec redis redis-cli GET hits
```

**Expected:** the current counter. If it returns `(nil)`, visit the page once and retry. Each request to `/`, including `curl`, increments it. A Redis `GET` does not.

### 6.3 Prove persistence across container replacement

Record the count and current container IDs:

```bash
docker compose exec redis redis-cli GET hits
docker compose ps -q
```

Remove the containers and project network, retaining the volume:

```bash
docker compose down
```

Recreate the services:

```bash
docker compose up -d --wait
docker compose ps -q
docker compose exec redis redis-cli GET hits
```

**Checkpoint:** the container IDs change but the recorded count remains. Now request the page again:

```bash
curl http://localhost:5000
```

The count increases from its saved value. Keep the same directory/project name and volume configuration during this exercise.

### 6.4 Observe a database outage

Predict what happens to the page when Redis stops:

```bash
docker compose stop redis
curl -i --max-time 15 http://localhost:5000
docker compose logs --tail=30 web redis
```

The web process remains running, but the request should fail after its retries. Restore Redis:

```bash
docker compose start redis
docker compose exec redis redis-cli ping
curl http://localhost:5000
```

If Redis is still starting, wait a few seconds and repeat the checks. Startup dependency checks do not continuously repair dependencies or automatically restart web when Redis becomes unhealthy.

## 7. Manage and troubleshoot containers

### 7.1 Common Compose operations

Run these inside `~/compose-demo`:

```bash
# Show all project containers, including stopped ones
docker compose ps -a

# Read recent service logs
docker compose logs --tail=50 web redis

# Follow web logs; Ctrl+C exits the log viewer only
docker compose logs -f web

# Show one resource-usage snapshot for all running containers
docker stats --no-stream
```

Stop and resume the lab without removing containers:

```bash
docker compose stop
docker compose start
```

After changing application source or the Dockerfile, rebuild and recreate as needed:

```bash
docker compose up -d --build --wait
```

`restart` alone does not rebuild an image or apply changed Compose configuration.

### 7.2 Cleanup choices

**Keep saved data:** remove the containers and project network, retaining images and the named volume:

```bash
docker compose down
```

**Delete the lab counter permanently:** run this only when finished with the persistence exercise:

```bash
docker compose down -v
```

The `-v` option removes this project's named volume. It does not remove the source files or built images.

### 7.3 Troubleshooting table

| Symptom | Check and next step |
| --- | --- |
| Permission denied connecting to Docker | Run `id`; confirm docker group membership, then log out and back in after `usermod` |
| Cannot connect to Docker daemon | Run `sudo systemctl status docker --no-pager`; start it with `sudo systemctl start docker` |
| Port 5000 already allocated | Run `docker ps` and `sudo ss -ltnp`; stop the Lab 1 container before Lab 2 |
| Container name already in use | Run `docker ps -a`; start the existing lab container or stop and remove it before recreating |
| Compose cannot find a configuration file | Run `pwd` and `ls`; change to `~/compose-demo` |
| YAML validation fails | Run `docker compose config`; check indentation and avoid tabs |
| VM browser works, laptop browser fails | Use the VM IP on the laptop; check VMware networking and firewall rules |
| Image or package download fails | Check VM internet/DNS access; first builds require downloads |
| Page shows an error | Check `docker compose ps -a`, web logs, and `docker compose exec redis redis-cli ping` |
| Counter resets unexpectedly | Check whether `down -v` was used or the project name, volume name, or persistence configuration changed |
| Edited code does not appear | Rebuild with `docker compose up -d --build --wait` |

### 7.4 What restart policies do

A restart policy handles an exited container process. It does not recreate a deleted container, restart a container merely because it becomes unhealthy, or add replicas when traffic increases. A deliberate `docker compose stop` is respected. These Compose labs do not implement Kubernetes-style reconciliation or automatic scaling.

## 8. Command reference and completion checklist

| Command | Purpose |
| --- | --- |
| `pwd` | Print the working directory |
| `ls -lah` | List files, sizes and permissions |
| `cd DIRECTORY` | Change directory |
| `mkdir -p DIRECTORY` | Create a directory and missing parents |
| `cat FILE` | Read a text file |
| `nano FILE` | Edit a file; save with Ctrl+O, Enter, then exit with Ctrl+X |
| `ip -br address` | Show interface addresses |
| `docker image ls` | List local images |
| `docker ps -a` | List running and stopped containers |
| `docker build -t NAME:TAG .` | Build and tag an image |
| `docker run ... IMAGE` | Create and start a new container |
| `docker start CONTAINER` | Start an existing stopped container |
| `docker stop CONTAINER` | Stop a container |
| `docker rm CONTAINER` | Remove a stopped container |
| `docker logs CONTAINER` | Read container output |
| `docker exec CONTAINER COMMAND` | Run a command inside a running container |
| `docker compose config` | Parse and display resolved Compose configuration |
| `docker compose up -d --build --wait` | Build and start the stack, waiting for running/healthy services |
| `docker compose ps` | Show project service status |
| `docker compose down` | Remove project containers and network, retain named data volumes |

Before finishing, confirm that you can:

- [ ] Run Docker commands and verify Compose installation.
- [ ] Build an image and open the Flask page.
- [ ] Explain host ports versus container ports.
- [ ] Explain both dots in `COPY . .`.
- [ ] Deploy the Flask–Redis Compose application.
- [ ] Resolve `redis` from the web container.
- [ ] Read the `hits` key directly from Redis.
- [ ] Recreate containers while preserving the counter.
- [ ] Inspect logs during a Redis outage and restore service.
- [ ] Distinguish stopping containers from deleting stored data.

## References and instructor notes

- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/)
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Docker restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/)

Prepared from the supplied installation and Docker lab notes. Command wrapping, Python indentation and Dockerfile explanations were corrected. Redis health-based startup and explicit AOF persistence were added. Shell/Python/YAML syntax was checked. The instructor reports testing the commands in the workshop VM.

Repository location: `docs/README.md`. Students can read this guide on GitHub and copy commands directly.
