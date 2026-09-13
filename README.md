# StudioFlow

Production-ready photography studio management system built with Django. Designed for a single studio in Nigeria with architecture supporting future multi-tenancy.

## Tech Stack

- **Backend:** Python 3.12, Django 6.1, PostgreSQL 18, Redis, Celery + Celery Beat
- **Frontend:** Django Templates + HTMX + Alpine.js + Tailwind CSS (CDN)
- **AI Module:** LangGraph, Groq (qwen/qwen3.6-27b), fastembed (ONNX local embeddings), pgvector RAG
- **API:** Django REST Framework with Token auth, drf-spectacular (Swagger/ReDoc)
- **Real-time:** Django Channels + WebSocket (notifications, portal updates)
- **DevOps:** Docker Compose, GitHub Actions, pytest, Ruff, Black

## Features

### Core Business (Phases 0–15)
- **Custom User Model** — Email-based auth, role-based access (Owner, Manager, Photographer, Editor, Sales, Assistant)
- **Client CRM** — Full client profiles, lifetime value tracking, multi-tenant isolation
- **Lead Pipeline** — Kanban-style lead tracking with status transitions
- **Booking System** — Status workflow (enquiry → confirmed → completed), calendar view, Kanban drag-and-drop
- **Package Management** — Service packages with addons, price snapshots on bookings
- **Project Workflow** — Post-shoot project tracking with task management
- **Gallery System** — Photo upload, client selection workflow, selection statistics
- **Finance** — Invoice generation, partial/overpayment handling, Paystack integration
- **Expenses** — Category-based expense tracking
- **Inventory** — Stock management with transaction history, low-stock alerts
- **Equipment** — Equipment tracking, maintenance scheduling with overdue alerts
- **Printing** — Print jobs, frame orders, album orders, studio-specific price lists
- **Notifications** — In-app alerts, email queue with retry, SMS (Termii), WhatsApp
- **Reports** — Revenue, expenses, bookings, clients, leads, packages, gallery reports
- **Audit Trail** — Full audit log with expandable before/after diff view
- **Dashboard** — Chart.js visualizations, key metrics, overdue maintenance alerts

### AI FDE (Film & Digital Expert)
- **Conversational AI** — LangGraph state graph with 7 nodes (understand → route → tools → RAG → respond)
- **Tool System** — 23 registered tools (12 read, 11 write) for studio operations
- **Knowledge Base** — pgvector RAG with local embeddings (BAAI/bge-small-en-v1.5, 384-dim)
- **LLM Provider** — Groq API via OpenAI-compatible interface with retry/backoff
- **Studio Context** — Dynamic studio stats injected into AI context

### Client Portal
- **Separate Auth** — ClientUser model (distinct from staff)
- **Dashboard** — Booking status, invoices, gallery links
- **WebSocket** — Real-time booking, payment, gallery notifications
- **Online Booking Request** — Public form at `/bookings/request/`, auto-creates lead
- **Survey/Feedback** — Post-shoot NPS survey at `/feedback/<uuid>/`

### Revenue & Payments
- **Invoice Payment Links** — Paystack checkout URLs on invoices at `/finance/<uuid>/pay/`
- **Paystack Webhook** — Auto-confirms online payments at `/finance/paystack/webhook/`
- **Automated Payment Reminders** — Celery Beat daily tasks: 7-day, 3-day, overdue (7/14/30 days)

### Staff & Operations
- **Staff Scheduling** — Weekly availability calendar at `/staff/schedule/`
- **Booking Staff Assignment** — Assign photographers to bookings at `/staff/assign/<booking_pk>/`
- **Contract Templates** — Generate contracts with digital signatures at `/contracts/`
- **iCal Calendar Sync** — Export bookings to Google Calendar at `/bookings/ical/`

### Marketing & Communications
- **Bulk SMS/Email/WhatsApp** — Client segment messaging at `/notifications/bulk/`
- **SMS Delivery Tracking** — Termii delivery status dashboard at `/notifications/sms-status/`
- **Online Booking Form** — Public self-service at `/bookings/request/`

### Business Intelligence
- **Revenue Forecasting** — ML-lite projections at `/reports/forecast/`
- **NPS Tracking** — Client satisfaction scores at `/feedback/`

### Inventory & Supply Chain
- **Supplier Management** — Vendor profiles at `/inventory/suppliers/`
- **Supplier Orders** — Order tracking with auto-inventory updates
- **Purchase Orders** — Create and receive orders from suppliers

### Progressive Web App
- **PWA Support** — Installable mobile app experience
- **Service Worker** — Offline caching for static assets
- **Push Notifications** — Browser push notifications for updates

### DevOps & Infrastructure
- **Docker Compose** — web, postgres, redis, celery, celery-beat
- **GitHub Actions** — CI/CD pipeline
- **Seed Data** — `python manage.py seed_data` populates demo data, AI knowledge base, print prices
- **Backups** — Automated PostgreSQL backup management
- **API Docs** — `/api/docs/` (Swagger), `/api/redoc/` (ReDoc)
- **Health Checks** — `/health/celery/`, `/health/celery/tasks/`
- **Search** — Global search across clients, bookings, invoices, leads
- **Calendar** — Visual calendar view for bookings
- **CSV Import/Export** — Client data bulk operations

## Quick Start

### Docker (Recommended)
```bash
cp .env.example .env    # Configure environment variables
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_data
docker compose exec web python manage.py createsuperuser
# Visit http://localhost:8000
```

### Local Development
```bash
# Install dependencies
uv sync --all-extras

# Set up environment
cp .env.example .env    # Configure DATABASE_URL, REDIS_URL, API keys

# Database
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser

# Run services (separate terminals)
python manage.py runserver
celery -A config worker -l info
celery -A config beat -l info
```

### Login
- **Staff:** `admin@lagosstudio.com` / `studio123`
- **Client Portal:** `funke.nwosu@email.com` / `client123`

## Configuration

Key environment variables in `.env`:
```
DATABASE_URL=postgres://studioflow:studioflow@localhost:5432/studioflow
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=True

# AI (Groq)
AI_BASE_URL=https://api.groq.com/openai/v1
AI_API_KEY=gsk_...
AI_MODEL=qwen/qwen3.6-27b

# Payments (Paystack)
PAYSTACK_SECRET_KEY=sk_test_...

# SMS (Termii)
TERMII_API_KEY=...
```

## Project Structure

```
studioflow/
├── config/              # Settings, URLs, Celery, ASGI
│   ├── settings/        # base, development, testing, production
│   ├── urls.py
│   ├── routing.py       # WebSocket ASGI routing
│   └── celery.py
├── apps/
│   ├── accounts/        # Custom User, roles, permissions
│   ├── studios/         # Multi-tenancy base
│   ├── clients/         # Client CRM
│   ├── leads/           # Lead pipeline
│   ├── packages/        # Service packages & addons
│   ├── bookings/        # Booking management + Kanban
│   ├── projects/        # Project tracking + tasks
│   ├── gallery/         # Photo galleries & selection
│   ├── finance/         # Invoices & payments
│   ├── expenses/        # Expense tracking
│   ├── inventory/       # Stock management
│   ├── equipment/       # Equipment + maintenance
│   ├── printing/        # Print, frame, album jobs + price lists
│   ├── notifications/   # Alerts, email, SMS, WhatsApp
│   ├── reports/         # Business intelligence
│   ├── audit/           # Audit trail
│   ├── dashboard/       # Main dashboard
│   ├── portal/          # Client portal (separate auth)
│   ├── staff/           # Staff scheduling & assignments
│   ├── contracts/       # Booking contracts & signatures
│   ├── feedback/        # Client surveys & NPS
│   ├── ai_fde/          # AI Film & Digital Expert
│   ├── api/             # REST API
│   └── core/            # Shared models, utilities, template tags
├── templates/           # HTML templates
├── static/              # Static files
├── media/               # User uploads
└── pyproject.toml       # Dependencies & tool config
```

## URL Routes

| Route | Description |
|-------|-------------|
| `/` | Dashboard |
| `/accounts/` | User management, auth |
| `/clients/` | Client CRM |
| `/leads/` | Lead pipeline |
| `/packages/` | Service packages |
| `/bookings/` | Booking list + detail |
| `/bookings/kanban/` | Kanban drag-and-drop pipeline |
| `/bookings/request/` | **Public booking request form** |
| `/bookings/requests/` | Staff: review booking requests |
| `/bookings/ical/` | **iCal export all bookings** |
| `/calendar/` | Visual calendar |
| `/projects/` | Project tracking |
| `/gallery/` | Photo galleries |
| `/finance/` | Invoices & payments |
| `/finance/<uuid>/pay/` | **Online payment (Paystack)** |
| `/finance/paystack/webhook/` | **Paystack webhook** |
| `/expenses/` | Expense tracking |
| `/inventory/` | Stock management |
| `/inventory/suppliers/` | **Supplier management** |
| `/equipment/` | Equipment tracking |
| `/equipment/maintenance/` | Maintenance logs |
| `/printing/` | Print jobs |
| `/printing/prices/` | Studio-specific price lists |
| `/notifications/` | Alert center |
| `/notifications/bulk/` | **Bulk SMS/Email/WhatsApp** |
| `/notifications/sms-status/` | **SMS delivery dashboard** |
| `/staff/schedule/` | **Staff availability schedule** |
| `/contracts/` | **Booking contracts** |
| `/feedback/` | **Client surveys & NPS** |
| `/feedback/<uuid>/` | **Public survey form** |
| `/reports/` | Business reports |
| `/reports/forecast/` | **Revenue forecasting** |
| `/audit/` | Audit trail |
| `/portal/` | Client portal |
| `/ai-fde/` | AI assistant chat |
| `/api/v1/` | REST API |
| `/api/docs/` | Swagger API docs |
| `/api/redoc/` | ReDoc API docs |
| `/export/` | CSV export |
| `/backups/` | Database backups |
| `/search/` | Global search |

## Testing

```bash
# Run all tests (186 tests)
pytest

# Run specific app
pytest apps/bookings/tests/
pytest apps/finance/tests/

# Verbose output
pytest -v
```

## API

Token-based authentication:
```bash
# Get token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -d '{"username": "admin@lagosstudio.com", "password": "studio123"}'

# Use token
curl -H "Authorization: Token <your-token>" http://localhost:8000/api/v1/clients/
```

## License

Proprietary — StudioFlow
