# Architecture

## Overview

The application is split into a React frontend and a FastAPI backend. The backend exposes a REST API consumed by the frontend. Machine learning inference runs in-process using PyTorch and scikit-learn models.

## Backend Layers

- **Routers** (`backend/app/routers`): HTTP endpoints, request validation, auth guards.
- **Services** (`backend/app/services`): business logic, ML pipeline, caching, email, search, storage, webhooks, task queue.
- **CRUD** (`backend/app/crud.py`): database access.
- **Models** (`backend/app/models.py`): SQLAlchemy ORM.
- **Schemas** (`backend/app/schemas.py`): Pydantic validation.
- **Middleware** (`backend/app/middleware`): rate limiting, correlation IDs, audit logging.
- **ML** (`backend/app/ml`): model definitions and inference.

## Frontend

- Components in `src/components`.
- API client in `src/services/apiClient.js`.
- State managed via React hooks and localStorage.

## Data Flow

1. User uploads audio file via frontend.
2. Backend validates and stores temp file.
3. Ensemble prediction runs across chunks.
4. Results persisted to database.
5. Frontend displays chunk-wise and model-wise predictions.

## Security

- JWT access/refresh tokens.
- bcrypt password hashing.
- Rate limiting middleware.
- CORS configuration.
- Role-based access control (user/admin).

## Observability

- Structured JSON logging.
- Correlation IDs per request.
- Prometheus metrics endpoint (`/metrics`).
- Audit log for all mutating requests.

## Backup & Recovery

- SQLite/Postgres backup via `backup_service`.
- Restore utilities.
- Retention pruning.

## Deployment

- Docker Compose with backend, db, frontend.
- GitHub Actions CI for tests and lint.
- Health/readiness endpoints.
PY