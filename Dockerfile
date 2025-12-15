FROM python:3.11-slim

# Install system dependencies (git for auto-commit)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export and install dependencies
RUN uv export --format requirements-txt > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn requests

# Copy application code
COPY . .

# Create data directory for mock inputs
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start Service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
