# syntax=docker/dockerfile:1
ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
FROM ${PYTHON_IMAGE} AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production
WORKDIR /app
RUN groupadd --gid 10001 blocia \
    && useradd --uid 10001 --gid 10001 --create-home blocia \
    && mkdir -p /app/data /app/models \
    && chown -R 10001:10001 /app

# The HTTP API installs only the application's lightweight dependencies.
FROM base AS api
COPY pyproject.toml ./
COPY app ./app
COPY config ./config
COPY ml/artifacts ./ml/artifacts
RUN python -m pip install --no-cache-dir .
ENV PORT=8000 \
    BLOCIA_DATABASE_PATH=/app/data/blocia.sqlite3 \
    BLOCIA_PRELOAD_CLASSIFIER=0 \
    BLOCIA_PRELOAD_LOCAL_CHAT=0
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD ["python", "-c", "import os; from urllib.request import urlopen; urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health', timeout=4).close()"]
CMD ["/bin/sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"$PORT\" --workers 1 --proxy-headers --forwarded-allow-ips '*' --timeout-graceful-shutdown 30"]

# CPU-only inference keeps Torch, encoder weights and generation out of the API.
FROM base AS inference
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY app ./app
COPY config ./config
COPY ml ./ml
RUN python -m pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu 'torch>=2.6' \
    && python -m pip install --no-cache-dir '.[local]'
COPY scripts/inference-entrypoint.sh /usr/local/bin/inference-entrypoint.sh
RUN chmod 755 /usr/local/bin/inference-entrypoint.sh
ENV BLOCIA_ENABLE_LOCAL_CHAT=0 \
    BLOCIA_PREPARE_MODELS=1 \
    BLOCIA_PRELOAD_CLASSIFIER=1 \
    HF_HOME=/app/models/.cache \
    HF_HUB_DISABLE_TELEMETRY=1 \
    HF_HUB_DISABLE_PROGRESS_BARS=1 \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2
USER 10001:10001
EXPOSE 8001
HEALTHCHECK --interval=30s --timeout=5s --start-period=20m --retries=3 \
    CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8001/ready', timeout=4).close()"]
ENTRYPOINT ["/usr/local/bin/inference-entrypoint.sh"]
CMD ["uvicorn", "app.inference_main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1", "--timeout-graceful-shutdown", "110"]
