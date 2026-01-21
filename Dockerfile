FROM python:3.11-slim

RUN pip install --no-cache-dir uv
WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

ENV PYTHONPATH="/app/src:/app/tools/python/converter:${PYTHONPATH}"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

CMD ["uv", "run", "uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
