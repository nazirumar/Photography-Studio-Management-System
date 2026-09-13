FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY pyproject.toml ./
COPY manage.py ./
COPY config/ ./config/

RUN /root/.local/bin/uv sync --no-dev --all-extras

COPY . .

RUN /root/.local/bin/uv run python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["/root/.local/bin/uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
