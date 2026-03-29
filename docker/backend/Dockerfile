FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY . .

RUN uv pip install --system -e ".[dev]"

RUN chmod +x /app/docker-entrypoint.sh || true

EXPOSE 8000

CMD ["uvicorn", "merygoround.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
