# Deployment Guide

## Docker Compose

```bash
docker compose up --build -d
```

Services:
- backend: FastAPI on port 8000
- db: Postgres on port 5432
- frontend: nginx on port 3000

## Environment

Copy `.env.example` to `.env` and adjust values.

## Health Checks

- Backend: `/health`
- DB: pg_isready

## Scaling

- Increase backend workers via uvicorn `--workers`.
- Use external Postgres for production.
- Configure `BACKUP_DIR` to persistent volume.

## Monitoring

- Prometheus scrape `/metrics`.
- Logs are structured JSON to stdout.

## Backup

Schedule `create_backup()` via cron or admin endpoint.

## Rollback

- Restore database from backup file.
- Redeploy previous image tag.
PY