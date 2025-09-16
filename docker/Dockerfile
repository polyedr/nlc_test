# slim + Python 3.12
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl netcat-openbsd \
 && rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy requirements first (layer cache)
COPY requirements.txt /app/requirements.txt
# (опционально) dev-зависимости, если нужны в образе
# COPY requirements-dev.txt /app/requirements-dev.txt

# Install deps
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt
# && pip install --no-cache-dir -r requirements-dev.txt

# Copy project
COPY project /app/project

# Entrypoint/entry scripts
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Default CMD overridden by compose
CMD ["/entrypoint.sh"]
