# Unified deal monitor (development)
Local only: Django development server, not production ready. Existing Astro and Scrapling files are retained during migration.
```sh
export DJANGO_SECRET_KEY="$(openssl rand -hex 32)"
export MONITOR_DB_PASSWORD="$(openssl rand -hex 24)"
docker compose -f compose.monitor.yaml up -d --build
docker compose -f compose.monitor.yaml exec web python manage.py createsuperuser
```
Open http://localhost:8098 or http://HOST-LAN-IP:8098. Sign in with the account you created. Database persists in a named volume. Keep the same database password on subsequent starts. Do not expose this debug server to the public internet.
Current scope: create, list and delete multiple per-user USD alerts. No automatic monitoring or notifications yet. Next: edit/pause, integrate Scrapling, scheduler, notification delivery, production WSGI and Oracle deployment.
