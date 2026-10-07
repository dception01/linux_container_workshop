# 00 — Prepare the Ubuntu VM

Run these commands **inside Ubuntu**, not Windows PowerShell. Start with a clean Ubuntu 26.04 LTS amd64 VM, working internet and a sudo-capable user. Suggested starting allocation: 2 vCPUs, 4 GB RAM, 25 GB disk. Test on the actual student hardware.

## Install Docker Engine and Compose

If `docker version` and `docker compose version` already work, skip installation. For an existing conflicting Docker installation, consult the official guide before replacing packages.

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

Add the official repository:

```bash
. /etc/os-release
sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: ${UBUNTU_CODENAME:-$VERSION_CODENAME}
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker run --rm hello-world
```

For this dedicated lab user, enable commands without sudo:

```bash
sudo usermod -aG docker "$USER"
```

Log out of Ubuntu and log back in. Docker-group membership grants root-equivalent control over the VM; use it only for trusted lab users.

```bash
docker version
docker compose version
git clone https://github.com/dception01/linux_container_workshop.git
cd linux_container_workshop
cp .env.example .env
bash scripts/preflight.sh
```

Edit `TEAM_NAME` in `.env`; keep values containing spaces quoted. Leave the database settings unchanged for the first run. Do not commit `.env` or registry tokens.

## VMware networking

Start with NAT and confirm the guest has internet. Use the VM browser for the simplest access, or the guest's reachable IP from the host laptop. `hostname -I` can include Docker bridge addresses; identify the VMware guest interface with `ip -br address`.

Other students' laptops do not automatically have access to a NAT guest. For our trial session, you can use your own VM or follow along on the shared screen. Only configure bridged networking if the campus network permits it and you need cross-laptop access.

Source: https://docs.docker.com/engine/install/ubuntu/
