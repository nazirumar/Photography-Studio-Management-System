FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml uv.lock ./
RUN /root/.local/bin/uv sync --no-dev --all-extras

COPY . .

RUN /root/.local/bin/uv run python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["/root/.local/bin/uv", "run", "sh", "-c", "python -c \"import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute('CREATE EXTENSION IF NOT EXISTS vector'); print('pgvector extension enabled')\" 2>&1 || echo 'pgvector extension skipped'; python manage.py migrate --noinput 2>&1; python manage.py create_superadmin_if_needed 2>&1; python manage.py createcachetable 2>&1; daphne -b 0.0.0.0 -p 8000 config.asgi:application"]
