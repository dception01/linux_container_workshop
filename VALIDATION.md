# Preparation validation

Checked in the authoring workspace:

- 12 application tests passed: missing-database preview, health/readiness distinction, input bounds, parameterized insert, storage-failure response, HTML escaping and request-size limit.
- Python source compiled successfully.
- Docker Compose v2.39.4 validated the base, build and load-balancing configurations with `config --quiet`; workflow YAML also parsed successfully.
- Shell scripts passed Bash syntax checking.

Database interactions in the application tests are mocked. These tests do not prove live PostgreSQL persistence, container image builds, NGINX failover or VMware access. Docker Engine was not available in the authoring workspace. Complete the rehearsal in INSTRUCTOR.md on the Ubuntu VM before teaching.

Run application tests:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q tests
```

Ubuntu may require `sudo apt install python3-venv` first. Tests are optional for students and are not part of the timed lab.
