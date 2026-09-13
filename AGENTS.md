# AGENTS.md

## What This Is

StudioFlow — a Django photography studio management system. Initial target: a single studio in Nigeria, but architecture must support future multi-tenancy.

## Tech Stack

- **Backend:** Python 3.12, Django 5.1, PostgreSQL, Redis, Celery + Celery Beat, DRF (where APIs are needed)
- **Frontend:** Django Templates + HTMX + Alpine.js + Tailwind CSS (no React/Next.js)
- **DevOps:** Docker Compose, GitHub Actions, pytest, Ruff, Black
- **Entry:** `manage.py` → `config/` (settings split: `base.py`, `development.py`, `testing.py`, `production.py`)

## Development Commands

```bash
# Run tests
python -m pytest

# Lint
ruff check .

# Django checks
python manage.py check

# Migrations check
python manage.py makemigrations --check --dry-run

# Create superuser
python manage.py createsuperuser
```

## Development Rules

- **Build incrementally.** Do not implement everything at once. Follow the phased approach in the Master Prompt (Phase 0 → 15).
- **Before each phase:** Review code, review migrations, review tests, explain changes, identify risks, plan, then implement.
- **After each phase:** `ruff check .` → `pytest` → `python manage.py check` → `python manage.py makemigrations --check --dry-run`. Fix all issues.
- **Never leave failing tests.** Never suppress failing tests.
- **Custom User model required from day one** — do not use Django's default User and migrate later.

## Critical Non-Obvious Rules

- **Money = Decimal, never float.** `DecimalField(max_digits=14, decimal_places=2)`.
- **Package prices must be snapshotted into bookings** — changing a package later must not alter historical invoices.
- **Every business entity is scoped to a Studio.** Enforce multi-tenancy at query level.
- **Status transitions must be explicit** — use service methods (`complete_shoot(...)`, `start_editing(...)`) not raw `model.status = "x"; model.save()`.
- **Stock never changes without transaction history.** Never overwrite inventory quantities silently.
- **Invoice calculations are server-side authoritative.** Never compute totals only in JS.
- **Never commit secrets.** `.env.example` only.
- **Default currency is NGN but do not hard-code it** — design for future currency support.
- **Timezone:** `Africa/Lagos`, use timezone-aware datetimes.
- **Do not hard-code photo paper, frame sizes, etc.** — make them configurable.
- **Payments cannot silently disappear.** Corrections must be auditable.
- **Invoice.save()** auto-calculates `balance` and `status` — use `save(update_fields=[...])` or queryset `.update()` when bypassing auto-calculation is needed.
- **User model** uses email (no username). `AUTH_USER_MODEL = "accounts.User"`.

## Test Conventions

- Framework: **pytest** with test factories (realistic data)
- Finance tests need especially strong coverage (partial payments, overpayment, discounts, balance)
- Security tests must verify staff cannot access other studios' data
- Run: `pytest` (or `python -m pytest`)

## Linting

- Ruff for linting, Black for formatting
- Run: `ruff check .` then `black .` (or configured equivalents)

## Structure

```
studioflow/
├── config/          # settings, urls, celery, wsgi, asgi
├── apps/            # all Django apps
│   ├── accounts/    # Custom User model, auth, permissions
│   ├── clients/     # Client CRM
│   ├── leads/       # Lead pipeline
│   ├── packages/    # Service packages & addons
│   ├── bookings/    # Booking management
│   ├── projects/    # Project tracking
│   ├── gallery/     # Photo galleries & selection
│   ├── finance/     # Invoices & payments
│   ├── expenses/    # Expense tracking
│   ├── inventory/   # Inventory management
│   ├── equipment/   # Equipment tracking
│   ├── printing/    # Print jobs, frames, albums
│   ├── notifications/ # Alert system
│   ├── reports/     # Business intelligence
│   ├── audit/       # Audit trail
│   ├── dashboard/   # Main dashboard
│   ├── studios/     # Multi-tenancy
│   └── core/        # Base models, utilities
├── templates/       # HTML templates
├── static/          # Static files
├── media/           # User uploads
├── tests/           # Additional tests
├── scripts/         # Utility scripts
└── docs/            # Documentation
```

## Apps Status

| App | Services | Views | Templates | Tests |
|-----|----------|-------|-----------|-------|
| accounts | Yes | Yes | Yes | Yes |
| clients | Yes | Yes | Yes | Yes |
| leads | Yes | Yes | Yes | Yes |
| packages | Yes | Yes | Yes | Yes |
| bookings | Yes | Yes | Yes | Yes |
| projects | Yes | Yes | Yes | Yes |
| gallery | Yes | Yes | Yes | Yes |
| finance | Yes | Yes | Yes | Yes |
| expenses | Yes | Yes | Yes | Yes |
| inventory | Yes | Yes | Yes | Yes |
| equipment | Yes | Yes | Yes | Yes |
| printing | Yes | Yes | Yes | Yes |
| notifications | Yes | Yes | Yes | Yes |
| reports | Yes | Yes | Yes | Yes |
| audit | Yes | Yes | Yes | Yes |
| dashboard | Yes | Yes | Yes | Yes |
| studios | Yes | Yes | Yes | Yes |
| portal | Yes | Yes | Yes | Yes |
| payments | Yes | Yes | Yes | Yes |
| api | Yes | Yes | Yes | Yes |
| ai_fde | Yes | Yes | Yes | Yes |

## URL Routes

| App | Base URL | Namespace |
|-----|----------|-----------|
| dashboard | `/` | dashboard |
| accounts | `/accounts/` | accounts |
| clients | `/clients/` | clients |
| leads | `/leads/` | leads |
| packages | `/packages/` | packages |
| bookings | `/bookings/` | bookings |
| bookings kanban | `/bookings/kanban/` | bookings:kanban |
| projects | `/projects/` | projects |
| gallery | `/gallery/` | gallery |
| finance | `/finance/` | finance |
| expenses | `/expenses/` | expenses |
| inventory | `/inventory/` | inventory |
| equipment | `/equipment/` | equipment |
| equipment maintenance | `/equipment/maintenance/` | equipment:maintenance |
| printing | `/printing/` | printing |
| print prices | `/printing/prices/` | printing:price_list |
| notifications | `/notifications/` | notifications |
| reports | `/reports/` | reports |
| audit | `/audit/` | audit |
| studios | `/studios/` | studios |
| portal | `/portal/` | portal |
| payments | `/payments/` | payments |
| api | `/api/v1/` | api |
| calendar | `/calendar/` | bookings_calendar |
| export | `/export/` | core_export |
| backups | `/backups/` | core_backup |
| sms | `/sms/` | sms |
| communications | `/communications/` | communications |
| finance_pdf | `/finance/pdf/` | finance_pdf |
| ai_fde | `/ai-fde/` | ai_fde |
| websocket | `ws://host/ws/notifications/` | NotificationConsumer |
| websocket | `ws://host/ws/dashboard/` | DashboardConsumer |
| websocket | `ws://host/ws/portal/` | ClientPortalConsumer |

## Definition of Done

A feature is done only when: model is correct, migrations included, permissions work, server validation works, UI works, mobile layout considered, tests exist, queries reasonable, security considered, errors handled, docs updated, lint passes, tests pass.
