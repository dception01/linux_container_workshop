# Testing notes

Checks completed so far:

- 12 application tests passed: missing-database preview, health/readiness distinction, input bounds, parameterized insert, storage-failure response, HTML escaping and request-size limit.
- Python source compiled successfully.
- Docker Compose v2.39.4 validated the base, build and load-balancing configurations with `config --quiet`; workflow YAML also parsed successfully.
- Shell scripts passed Bash syntax checking.

The tests use mocked database connections. Live PostgreSQL persistence, image builds, NGINX failover and browser access through VMware still need to be checked on the Ubuntu VM. Follow the [rehearsal checklist](INSTRUCTOR.md) to complete those checks.

Run application tests:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q tests
```

Ubuntu may require `sudo apt install python3-venv` first. Tests are optional for students and are not part of the timed lab.
