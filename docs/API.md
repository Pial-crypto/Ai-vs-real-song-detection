# API Reference

## Health

- `GET /` - root message.
- `GET /health` - health status with DB check.
- `GET /ready` - readiness probe.
- `GET /metrics` - Prometheus metrics.

## Auth

- `POST /api/v1/auth/register` - register user.
- `POST /api/v1/auth/login` - login, returns tokens.
- `POST /api/v1/auth/refresh` - refresh access token.
- `GET /api/v1/auth/me` - current user.

## Users (admin)

- `GET /api/v1/users` - list users.
- `GET /api/v1/users/{id}` - get user.

## Predictions

- `POST /prediction` - upload audio, run prediction.
- `POST /api/v1/predictions` - save prediction.
- `GET /api/v1/predictions/me` - current user's predictions.
- `GET /api/v1/predictions/user/{id}` - user's predictions.
- `GET /api/v1/predictions/{id}` - get prediction.
- `DELETE /api/v1/predictions/{id}` - delete prediction.

## Dashboards

- `POST /api/v1/dashboards/{prediction_id}` - add dashboard.
- `GET /api/v1/dashboards` - list dashboards.

## Backups (admin)

- `POST /api/v1/backups/create` - create backup.
- `GET /api/v1/backups` - list backups.
- `POST /api/v1/backups/prune` - prune old backups.

## Analytics (admin)

- `GET /api/v1/analytics/summary` - summary stats.

## Notifications

- `GET /api/v1/notifications` - list.
- `POST /api/v1/notifications` - create.
- `POST /api/v1/notifications/{id}/read` - mark read.
- `POST /api/v1/notifications/read-all` - mark all read.

## Feature Flags (admin)

- `GET /api/v1/feature-flags` - list.
- `POST /api/v1/feature-flags/{key}` - upsert.
- `GET /api/v1/feature-flags/{key}/enabled` - check.

## Profiles

- `GET /api/v1/profiles/me` - get profile.
- `PUT /api/v1/profiles/me` - update profile.

## Batch

- `POST /api/v1/batch?total_files=N` - create job.
- `GET /api/v1/batch` - list jobs.
- `GET /api/v1/batch/{id}` - get job.
- `POST /api/v1/batch/{id}/progress` - update progress.
- `POST /api/v1/batch/{id}/complete` - complete job.

## Export

- `POST /api/v1/export?fmt=json` - create export job.
- `POST /api/v1/export/{id}/complete` - complete.

## Audit (admin)

- `GET /api/v1/audit` - list audit logs.

## Models (admin)

- `GET /api/v1/models` - list model metadata.
- `POST /api/v1/models` - register model.

## Search

- `GET /api/v1/search/predictions?q=` - search predictions.
- `GET /api/v1/search/users?q=` - search users (admin).

## Tasks (admin)

- `GET /api/v1/tasks` - list tasks.
- `GET /api/v1/tasks/stats` - stats.

## Cache (admin)

- `GET /api/v1/cache/stats` - stats.
- `POST /api/v1/cache/clear` - clear.

## Webhooks (admin)

- `GET /api/v1/webhooks` - list.
- `POST /api/v1/webhooks` - register.
- `POST /api/v1/webhooks/{id}/test` - test delivery.
PY