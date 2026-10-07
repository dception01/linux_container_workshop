# 04 — Publish and distribute the project

## Publish the application to GHCR

The repository contains a manually triggered GitHub Actions workflow. It does **not** publish on every push.

1. Open the repository on GitHub.
2. Go to **Actions → Publish workshop image → Run workflow** on main.
3. Wait for the build to succeed. It publishes `ghcr.io/dception01/campus-feedback:workshop-v1` for linux/amd64.
4. Open your GitHub profile's **Packages → campus-feedback → Package settings** and change package visibility to **Public**. Repository visibility alone does not guarantee package visibility.
5. On a VM without a saved GHCR login, test `docker pull ghcr.io/dception01/campus-feedback:workshop-v1`.

GitHub Actions uses its built-in GITHUB_TOKEN with packages:write; students need no token for public pulls. Never put tokens in the repository. Re-running the workflow replaces the workshop-v1 tag; freeze publishing after the final rehearsal. For a new workshop release, update the tag consistently in the workflow, env example, Compose files and instructions.

## Student quick path

```bash
git clone https://github.com/dception01/linux_container_workshop.git
cd linux_container_workshop
cp .env.example .env
docker compose -f compose.yaml -f compose.lb.yaml pull
docker compose -f compose.yaml -f compose.lb.yaml up -d --wait
```

Open http://localhost:8081 inside the VM.

## Prepare offline delivery

On the instructor VM, build the application and fetch the database and proxy images before disconnecting:

```bash
docker build -t ghcr.io/dception01/campus-feedback:workshop-v1 .
docker pull postgres:17.6-bookworm
docker pull nginx:1.28.0-alpine
bash scripts/save-images.sh
git archive --format=zip --output=workshop-source.zip HEAD
```

Distribute `workshop-source.zip` and `workshop-images.tar` on a USB drive or local share. Unzip source into a folder on the student's VM, then run from that folder:

```bash
cp .env.example .env
docker image load -i /path/to/workshop-images.tar
docker compose -f compose.yaml -f compose.lb.yaml up -d --pull never --no-build --wait
```

Docker Engine and Compose must already be installed. The image archive contains no feedback database data. The bundled SQL creates an empty database on first start. The standard archive targets amd64 VMs; use matching images for other architectures.

Offline **building** additionally needs the base image and Python package dependencies. The ready-image route is the offline fallback, not a promise of offline builds.

Sources:
- https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- https://docs.docker.com/reference/cli/docker/image/save/
- https://docs.docker.com/reference/cli/docker/image/load/
