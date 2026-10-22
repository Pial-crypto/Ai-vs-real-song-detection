# Multi-stage backend Dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libsndfile1 ffmpeg && rm -rf /var/lib/apt/lists/*

FROM base AS deps
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM base AS runtime
COPY --from=deps /usr/local /usr/local
COPY backend /app/backend
COPY src /app/src
ENV PYTHONPATH=/app
ENV MODEL_DIR=/app/src
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())" || exit 1
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
