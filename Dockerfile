FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY src ./src

RUN uv sync --frozen --no-dev

CMD ["sh", "-c", ".venv/bin/alembic upgrade head && .venv/bin/uvicorn events_aggregator.main:app --host 0.0.0.0 --port 8000"]