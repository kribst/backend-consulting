FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend-consulting/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY backend-consulting/. .

RUN cd backend-consulting && python src/manage.py collectstatic --noinput || true

RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /app/src/media && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "cd backend-consulting && python src/manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${GUNICORN_WORKERS:-3} --timeout 60 --access-logfile - --error-logfile -"]
