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

CMD ["/root/.local/bin/uv", "run", "sh", "-c", "python manage.py migrate --noinput && python manage.py createcachetable && python manage.py create_superadmin_if_needed || true && daphne -b 0.0.0.0 -p 8000 config.asgi:application"]
