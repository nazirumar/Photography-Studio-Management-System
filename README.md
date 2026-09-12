# StudioFlow

Photography studio management system built with Django.

## Tech Stack

- Python 3.12+, Django 5.1
- PostgreSQL, Redis, Celery
- HTMX + Alpine.js + Tailwind CSS
- Docker Compose

## Quick Start

1. Copy `.env.example` to `.env` and configure
2. `docker compose up -d`
3. `docker compose exec web python manage.py migrate`
4. `docker compose exec web python manage.py createsuperuser`
5. Visit http://localhost:8000

## Development

```bash
# Install with uv
uv sync --all-extras

# Run locally
python manage.py runserver

# Run tests
pytest

# Lint
ruff check .
black --check .
```

## Docker

```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Project Structure

```
studioflow/
├── config/          # Settings, URLs, Celery
├── apps/            # Django apps
│   ├── accounts/    # Custom User, roles, auth
│   ├── studios/     # Studio model (multi-tenancy)
│   ├── clients/     # Client CRM
│   ├── leads/       # Lead pipeline
│   ├── packages/    # Photography packages
│   ├── bookings/    # Booking system
│   ├── projects/    # Project workflow
│   ├── gallery/     # Photo management
│   ├── finance/     # Invoices, payments
│   ├── expenses/    # Expense tracking
│   ├── inventory/   # Stock management
│   ├── equipment/   # Equipment tracking
│   ├── printing/    # Print, frame, album jobs
│   ├── notifications/
│   ├── reports/
│   ├── dashboard/   # Main dashboard
│   ├── audit/       # Audit logging
│   └── core/        # Shared base models
├── templates/
├── static/
├── media/
└── docs/
```