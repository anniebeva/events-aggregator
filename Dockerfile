FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --frozen --no-dev

CMD ["uv", "run", "uvicorn", "events_aggregator.main:app", "--host", "0.0.0.0", "--port", "8000"]