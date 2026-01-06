FROM python:3.11-slim

# No system dependencies needed anymore

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv
# COPY --from uv:latest /bin/uv /bin/uv
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Export and install dependencies
RUN uv sync

# Copy application code
COPY . .

# Set Python path so imports work correctly
ENV PYTHONPATH="/app/src:/app/tools/python/converter:${PYTHONPATH}"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Start Service
CMD ["uv", "run", "uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8000"]
