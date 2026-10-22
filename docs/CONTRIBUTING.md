# Contributing

## Development Setup

1. Clone repository.
2. Install backend deps: `pip install -r backend/requirements.txt`
3. Install frontend deps: `npm install`
4. Run backend: `uvicorn backend.app.main:app --reload`
5. Run frontend: `npm start`

## Code Style

- Python: ruff (see `ruff.toml`).
- JS: CRA eslint config.

## Tests

- Backend: `python -m pytest backend/tests`
- Frontend: `npm test -- --watchAll=false`

## Pull Requests

- Keep changes focused.
- Add tests for new functionality.
- Update docs when changing APIs.
- Ensure ruff and tests pass.

## Commit Messages

Use conventional style: `type(scope): description`.
PY