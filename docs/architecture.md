# Architecture Overview

## Tech Stack

- **Language:** Python 3.12+
- **Backend Framework:** Django 5.x, Django REST Framework (APIs where needed)
- **Database:** PostgreSQL 16
- **Cache / Message Broker:** Redis 7
- **Task Queue:** Celery 5.x + Celery Beat (periodic tasks)
- **Frontend:** Django Templates + HTMX + Alpine.js + Tailwind CSS
- **Containerisation:** Docker Compose
- **Testing:** pytest + factory_boy
- **Linting:** Ruff, Black
- **CI:** GitHub Actions

## Project Layout

```
studioflow/
├── manage.py
├── config/                  # settings, urls, celery, wsgi, asgi
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── testing.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/                    # all Django apps
│   ├── accounts/
│   ├── clients/
│   ├── leads/
│   ├── packages/
│   ├── bookings/
│   ├── projects/
│   ├── gallery/
│   ├── finance/
│   ├── expenses/
│   ├── inventory/
│   ├── equipment/
│   ├── printing/
│   ├── notifications/
│   ├── reports/
│   ├── dashboard/
│   ├── audit/
│   ├── studios/
│   └── core/
├── templates/
├── static/
├── media/
├── tests/
├── scripts/
└── docs/
```

## Settings Split

| File | Purpose |
|------|---------|
| `base.py` | Shared settings: installed apps, middleware, templates, auth, celery broker, storage defaults, language, timezone (`Africa/Lagos`) |
| `development.py` | DEBUG=True, local Redis, `django-debug-toolbar`, console email backend |
| `testing.py` | In-memory DB, faster hashing, override storage to file-system |
| `production.py` | DEBUG=False, S3 storage, Redis via URL, HTTPS settings, security headers |

Environment variables loaded via `python-decouple` (or `django-environ`). Secrets never committed. `.env.example` only.

## Multi-Tenancy

Every business entity is scoped to a `Studio` instance. The `Studio` model is the root tenant. At query level, all managers and views filter by `studio=request.user.staff_profile.studio` (or equivalent). Cross-studio data access is forbidden.

Tenancy is enforced:
1. At the ORM level (default managers filter by studio).
2. At the view level (mixins/decorators verify studio membership).
3. At the API level (serialisers inject studio from request context).

## Service Layer Pattern

Business logic lives in service modules, not in models or views. Each app exposes a `services.py` (or `services/` package) containing pure functions that accept explicit parameters and return results.

```
apps/
  bookings/
    services.py          # create_booking(), confirm_booking(), cancel_booking()
    models.py            # Booking model (fields + __str__ only)
    views.py             # delegates to services
    api.py               # DRF views delegate to services
```

Benefits:
- Reusable across views, API, management commands, Celery tasks.
- Easier to test (no request/response overhead).
- Enforces status-transition rules centrally.

## Async via Celery

Long-running or side-effect work offloaded to Celery workers:

| Task | Trigger |
|------|---------|
| Send email (booking confirmation, invoice, password reset) | Service method after status change |
| Generate thumbnail variants on photo upload | `post_save` signal → Celery task |
| Send in-app notifications | Service method |
| Generate PDF invoices / receipts | On-demand from view |
| Build gallery zip for download | On-demand from view |
| Aggregate reports / CSV exports | Scheduled via Celery Beat or on-demand |
| Send payment reminders | Celery Beat daily schedule |

Broker: Redis (same instance as Django cache, different DB number). Backend: same Redis.

## Storage Abstraction

Django `default_storage` abstraction:

- **Development:** `django.core.files.storage.FileSystemStorage` (local `media/` directory).
- **Production:** `django-storages` + `boto3` (S3-compatible bucket). Configured via environment variables (`AWS_STORAGE_BUCKET_NAME`, `AWS_S3_REGION_NAME`, etc.).

All file references in models use `FileField` or `ImageField` — never raw paths. This ensures portability between environments.

## Frontend Architecture

Server-rendered Django templates with progressive enhancement:

- **Django Templates:** Base layout, data display, form rendering.
- **HTMX:** AJAX interactions — inline editing, form submissions without full reload, filter/sort, pagination, modal forms. Attributes like `hx-get`, `hx-post`, `hx-swap`.
- **Alpine.js:** Client-side UI state — dropdown menus, modals, toggle panels, date pickers. No build step.
- **Tailwind CSS:** Utility-first styling via CDN in dev, compiled in production.

No JavaScript framework. No `node_modules` build pipeline for core app (Tailwind compilation is the only exception). Pages are functional without JavaScript; HTMX/Alpine enhance the experience.

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Custom User model (`email` login) | Avoids Django default `username` migration pain later |
| UUIDs for external IDs | Safe to expose in URLs/APIs, no sequential leaking |
| Package snapshot in Booking | Changing a package price later must not alter historical bookings |
| Money as `DecimalField(max_digits=14, decimal_places=2)` | Precision for financial calculations |
| AuditLog for all sensitive ops | Regulatory compliance, dispute resolution |
| Status transitions via service methods | Prevents invalid state changes, ensures audit + notification |
