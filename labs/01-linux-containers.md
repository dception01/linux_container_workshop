# 01 — Linux and your first container

From the cloned repository:

```bash
pwd
ls -lah
ls app
cat app/requirements.txt
head -n 20 app/app.py
mkdir -p /tmp/workshop-practice
cp .env.example /tmp/workshop-practice/settings.txt
cat /tmp/workshop-practice/settings.txt
whoami
id
ip -br address
ss -lnt
```

Explain paths, files, copying, users, interfaces and listening ports in relation to the project. Use `nano .env` to set your team name (install nano if needed).

Run a web server:

```bash
docker run -d --name first-web -p 8090:80 nginx:1.28.0-alpine
docker ps
curl -I http://localhost:8090
docker logs first-web
docker exec first-web hostname
docker stop first-web
docker rm first-web
```

Explain: image versus container, detached mode, name, host port 8090 versus container port 80, logs and process isolation. Open port 8090 in the VM browser before stopping it.

Checkpoint: each student can explain where the web server runs and which port the browser uses.
