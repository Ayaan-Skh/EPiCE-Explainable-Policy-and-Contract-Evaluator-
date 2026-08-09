# Hugging Face Spaces (Docker SDK) image for the EPiCE backend.
# HF runs containers as UID 1000 and expects the app on port 7860.
# (Render/local use Dockerfile.api instead — see docker-compose.yml.)

# --- Build stage: install deps, CPU-only torch ---
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
# CPU-only torch first, so sentence-transformers doesn't drag in the multi-GB CUDA build.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# --- Final stage ---
FROM python:3.11-slim

# Non-root user: Hugging Face Spaces run as UID 1000.
RUN useradd -m -u 1000 user

RUN apt-get update && apt-get install -y libmagic1 curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY ./api /app/api
COPY ./src /app/src
COPY ./main.py /app/main.py

# Writable dirs the app uses (vector store, uploads, logs), owned by the runtime user.
RUN mkdir -p /app/data/raw/uploads /app/data/processed /app/policy_documents /app/api/logs /app/logs \
    && chown -R user:user /app

USER user
ENV HOME=/home/user \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/home/user/.cache/huggingface

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
