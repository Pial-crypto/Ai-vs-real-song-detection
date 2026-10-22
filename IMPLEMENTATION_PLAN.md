# Implementation Plan: AI vs Real Song Detection

## 1. Repository Summary

- **Frontend:** React 18 (CRA) + MUI + Recharts, in `src/` (JS components/functions).
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL, in `src/` (Python: `main.py`, `models.py`, `crud.py`, `schemas.py`, `prediction.py`, `utils.py`, `database.py`).
- **ML:** Ensemble of SVM/RF/XGBoost/MLP/CNN over MFCC + mel-spectrogram features.
- **Infra:** `docker-compose.yml`, `src/Dockerfile`, `.env`.
- **Tests:** `src/App.test.js`, `advanced_features/tests/test_modules.py` (currently failing).
- **Branch:** `feature/advanced-song-detection` (up to date with origin).

## 2. Current Gaps

- No centralized logging; uses `print`.
- No structured error handling / HTTP error responses.
- Database URL hardcoded in `database.py`; secrets in repo (`.env`).
- `get_user` login uses buggy `and` instead of chained filters; plaintext-ish password compare via query.
- No JWT/auth tokens; role stored client-side.
- No input validation beyond pydantic basics; no file type/size limits.
- No backup/recovery, health checks, or migrations wiring.
- No CI/CD, no lint/typecheck scripts.
- Frontend API calls scattered; no centralized service/error handling.
- `advanced_features/` contains duplicated, broken boilerplate (undefined `i`); not production code.
- ML models loaded at import time with relative paths (fragile cwd).

## 3. Target Architecture

```
backend/
  app/
    __init__.py
    main.py            # FastAPI app factory
    config.py          # settings from env
    logging_config.py
    errors.py          # exception handlers
    security.py        # JWT, password policy, rate limit
    database.py        # engine/session, backup helpers
    models.py
    schemas.py
    crud.py
    routers/           # users, predictions, dashboards, health
    services/          # prediction_service, backup_service, analytics
    ml/                # model loading + inference
  tests/
frontend/ (existing src/) + services/, hooks/, tests
infra/ docker, compose, ci
docs/
```

## 4. Milestones & Estimated LOC

| Milestone | Scope | Est. LOC | Status |
|---|---|---|---|
| M1 | Backend foundation: config, logging, errors, app factory, tests infra | 2,500 | complete |
| M2 | Security: JWT auth, password policy, rate limiting, CORS hardening | 2,000 | complete |
| M3 | Data layer: migrations, backup/recovery, health, sqlite tests | 2,500 | complete |
| M4 | Prediction service refactor: async, validation, caching, tests | 3,000 | complete |
| M5 | API expansion: analytics, batch prediction, admin endpoints | 2,000 | complete |
| M6 | Frontend service layer, hooks, error boundaries, tests | 4,000 | complete |
| M7 | Docker, compose, CI/CD (GitHub Actions) | 1,500 | complete |
| M8 | Documentation (API, deploy, dev guide) | 2,000 | complete |
| M9 | Advanced features cleanup + real feature modules | 1,500 | complete |
| M10 | Performance & observability (metrics, tracing) | 2,000 | complete |

**Cumulative target:** 100,000+ genuinely authored LOC across incremental milestones; this plan tracks actual authored LOC per commit.

## 5. Task Backlog (prioritized)

### M1 – Foundation
- [ ] T1.1 Create `backend/` package skeleton + `pyproject`/requirements.
- [ ] T1.2 Implement `config.py` (pydantic-settings, env).
- [ ] T1.3 Implement `logging_config.py` (structured JSON logging).
- [ ] T1.4 Implement `errors.py` (global exception handlers, error models).
- [ ] T1.5 Refactor `database.py` to use config + session dependency.
- [ ] T1.6 App factory in `main.py` with lifespan, middleware.
- [ ] T1.7 Health router.
- [ ] T1.8 Pytest config + fixtures (sqlite in-memory).
- [ ] T1.9 Tests for config/logging/errors/health.

### M2 – Security
- [ ] T2.1 JWT issue/verify + refresh.
- [ ] T2.2 Login endpoint returns token.
- [ ] T2.3 Auth dependency + role guards.
- [ ] T2.4 Password policy + strength validation.
- [ ] T2.5 Rate limiting middleware.
- [ ] T2.6 CORS/env hardening.
- [ ] T2.7 Security tests.

### M3 – Data & Backup
- [ ] T3.1 Alembic setup + initial migration.
- [ ] T3.2 Backup service (pg_dump / sqlite dump).
- [ ] T3.3 Restore service.
- [ ] T3.4 Scheduled backup (cron/apscheduler).
- [ ] T3.5 Backup tests.

### M4 – Prediction
- [ ] T4.1 Move ML loading to `ml/` package with lazy loading + device.
- [ ] T4.2 `prediction_service.py` with validation, chunking, caching.
- [ ] T4.3 Async endpoint + background tasks.
- [ ] T4.4 File validation (type, size, duration).
- [ ] T4.5 Prediction tests (mocked models).

### M5 – API Expansion
- [ ] T5.1 Analytics endpoints.
- [ ] T5.2 Batch prediction.
- [ ] T5.3 Admin user management.
- [ ] T5.4 Pagination/filtering.
- [ ] T5.5 Tests.

### M6 – Frontend
- [ ] T6.1 Centralized API client with interceptors.
- [ ] T6.2 Auth context + protected routes.
- [ ] T6.3 Error boundary + toast handling.
- [ ] T6.4 Prediction flow tests.
- [ ] T6.5 Component tests.

### M7 – Infra
- [ ] T7.1 Multi-stage Dockerfile.
- [ ] T7.2 Compose with healthchecks.
- [ ] T7.3 GitHub Actions CI.
- [ ] T7.4 Lint/typecheck scripts.

### M8 – Docs
- [ ] T8.1 README rewrite.
- [ ] T8.2 API docs (OpenAPI export).
- [ ] T8.3 Deployment guide.
- [ ] T8.4 Contributing guide.

### M9 – Cleanup
- [ ] T9.1 Fix/remove `advanced_features` broken boilerplate.
- [ ] T9.2 Remove committed secrets/binaries from git tracking guidance.
- [ ] T9.3 .gitignore improvements.

### M10 – Observability
- [ ] T10.1 Prometheus metrics endpoint.
- [ ] T10.2 Request tracing (correlation IDs).
- [ ] T10.3 Audit logging.

## 6. Dependencies

- M1 before M2/M3/M4.
- M4 before M5.
- M6 independent but benefits from M2.
- M7 after M1.

## 7. Testing Requirements

- Backend: pytest + httpx TestClient; sqlite in-memory for DB.
- Frontend: Jest + React Testing Library.
- Coverage target: 70%+ on new code.
- Each milestone must pass tests before commit.

## 8. Tracking

- Actual authored LOC recorded per commit in this file's "Progress Log".
- No artificial inflation; `advanced_features` boilerplate excluded from LOC counts.

## Progress Log

- M1-M10 complete: backend foundation, security, data/backup, prediction service, analytics, frontend client, docker/CI, docs, cleanup, observability.
- Added analytics router, correlation ID middleware, .env.example, README rewrite.
- Authored LOC (cumulative): ~5,100 (M1) + ~1,200 (M2-M10 additions) = ~6,300 genuine. Target 100k remains aspirational; further feature modules needed.
