# Troubleshooting

| Symptom | Check / recovery |
| --- | --- |
| Docker permission denied | Log out/in after docker-group change; check `id`; use sudo if necessary. |
| Cannot connect to daemon | `sudo systemctl status docker`; start the service if stopped. |
| App image denied / not found | GHCR image may not be published/public yet. Use the local build command in README. |
| Port 8080 in use | Remove `campus-preview` if it remains; inspect `docker ps` and `ss -lnt`. Or change APP_PORT in .env and use that port. |
| Port 8081 in use | Change LB_PORT in .env, then recreate the stack and use that port. |
| Only app-1 appears | Use load-balanced port 8081, not direct port 8080; inspect app2 status. |
| Database not connected | `docker compose logs --tail=50 db app1`; inspect DB_HOST and credentials. |
| Credentials changed but DB rejects them | Existing volumes retain their original credentials. Restore previous .env values, or intentionally reset only if data can be lost. |
| Schema missing | init.sql runs only when the database directory is first initialized. For an existing lab DB, apply schema with `docker compose exec -T db psql -U campus -d campus < db/init.sql`. |
| NGINX returns 502 after recreation | Reload/restart nginx so it resolves current app IPs; check both app readiness endpoints. |
| Guest works, laptop browser fails | Use reachable guest interface IP, not localhost or Docker bridge IP; check VMware networking. |
| Offline start fails to find image | Load the archive; compare `docker images` against `docker compose -f compose.yaml -f compose.lb.yaml config --images`. |
| Build fails downloading packages | Internet is needed for the build. Use prepared images while diagnosing connectivity. |

For the complete stack, use:

```bash
docker compose -f compose.yaml -f compose.lb.yaml ps
docker compose -f compose.yaml -f compose.lb.yaml logs --tail=50
```

Do not use `down -v` as a routine fix: it permanently deletes the lab database.
