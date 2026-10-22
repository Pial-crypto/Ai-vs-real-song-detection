# AI vs Real Song Detection

Full-stack application for detecting AI-generated music using an ensemble of machine learning models (SVM, Random Forest, XGBoost, MLP, CNN) over MFCC and mel-spectrogram features.

## Architecture

- **Frontend:** React 18 (Create React App) + MUI + Recharts in `src/`.
- **Backend:** FastAPI + SQLAlchemy + PostgreSQL in `backend/` (legacy copy in `src/`).
- **ML:** Ensemble inference in `backend/app/ml/inference.py`.
- **Infra:** Docker Compose, GitHub Actions CI.

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend

```bash
npm install
npm start
```

### Docker

```bash
docker compose up --build
```

## Environment Variables

See `.env.example`. Key variables:

- `DATABASE_URL` - database connection string (default sqlite).
- `SECRET_KEY` - JWT signing secret.
- `ENVIRONMENT` - development/test/production.
- `MODEL_DIR` - directory containing trained model artifacts.
- `BACKUP_DIR` - directory for database backups.

## API

- OpenAPI docs: `http://localhost:8000/docs`
- Health: `GET /health`
- Auth: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`
- Predictions: `POST /prediction`, `GET /api/v1/predictions/me`
- Analytics (admin): `GET /api/v1/analytics/summary`
- Backups (admin): `POST /api/v1/backups/create`

## Tests

Backend:

```bash
python -m pytest backend/tests -q
```

Frontend:

```bash
npm test -- --watchAll=false
```

## Lint

```bash
python -m ruff check backend
```

## Backup & Recovery

Use `/api/v1/backups/create` (admin) or `backend.app.services.backup_service.create_backup()`. Restore with `restore_sqlite`.

## Security Notes

- Passwords hashed with bcrypt.
- JWT access/refresh tokens.
- Rate limiting middleware enabled.
- CORS origins configurable via `CORS_ORIGINS`.
