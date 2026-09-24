# 📸 StudioFlow

### Photography Studio Business Management Platform

StudioFlow is a production-oriented **photography studio management platform** built with Django.

It centralizes the day-to-day operations of a photography business — clients, leads, bookings, projects, galleries, invoices, payments, expenses, inventory, equipment, staff, reporting, communication, and AI-assisted workflows.

It is designed around a real photography studio workflow while keeping the architecture ready for future **multi-studio / SaaS expansion**.

---

## 🎯 The Problem

Photography businesses often depend on disconnected tools:

- WhatsApp for client communication
- Spreadsheets for financial records
- Calendars for bookings
- Folders or cloud storage for photographs
- Manual inventory records
- Separate payment systems
- Paper or spreadsheet expense tracking

As the business grows, these disconnected workflows become difficult to manage.

## 💡 The Solution

StudioFlow brings these workflows into one platform:

**Lead → Client → Booking → Project → Gallery → Invoice → Payment → Delivery**

Alongside the customer journey, StudioFlow manages staff, equipment, inventory, expenses, contracts, notifications, reporting, and business automation.

---

# 🚀 Core Features

### 👥 CRM & Lead Management
- Client profiles
- Client history
- Lifetime value tracking
- Lead pipeline
- Kanban-style workflows
- Search and filtering

### 📅 Booking Management
- Booking lifecycle management
- Calendar view
- Kanban pipeline
- Public booking requests
- Package selection
- Staff assignment
- iCal calendar export

### 📸 Project Management
- Post-shoot project tracking
- Task management
- Project status workflows
- Staff coordination

### 🖼️ Client Galleries
- Photo uploads
- Client galleries
- Photo selection workflow
- Selection statistics
- Client portal integration

### 💰 Finance & Payments
- Invoice generation
- Payment tracking
- Partial payments
- Overpayment handling
- Paystack payment links
- Paystack webhook processing
- Automated payment reminders

### 💸 Expense Management
- Categorized expenses
- Operational cost tracking
- Financial reporting

### 📦 Inventory & Suppliers
- Stock management
- Transaction history
- Low-stock alerts
- Supplier management
- Purchase orders

### 📷 Equipment Management
- Equipment tracking
- Maintenance scheduling
- Overdue maintenance alerts

### 🖨️ Printing
- Print jobs
- Frame orders
- Album orders
- Studio-specific price lists

### 👨‍💼 Staff Operations
- Role-based access
- Staff scheduling
- Weekly availability
- Booking assignments

### 📑 Contracts
- Contract templates
- Booking contracts
- Digital signatures

### 🔔 Communications
- In-app notifications
- Queued email
- SMS integration
- WhatsApp integration
- Bulk communication workflows

### 📊 Business Intelligence
- Revenue reporting
- Expense reporting
- Booking analytics
- Client analytics
- Lead reports
- Package reports
- Revenue forecasting
- NPS / client feedback

### 🔍 Administration
- Audit trail
- Global search
- CSV import/export
- Database backup management
- Health-check endpoints

---

# 🤖 AI Film & Digital Expert

StudioFlow includes an AI-powered assistant designed for photography studio operations.

The AI layer uses:

- **LangGraph** for workflow orchestration
- OpenAI-compatible LLM APIs
- **Groq** as a configurable provider
- **23 registered studio-operation tools**
- pgvector-backed RAG
- Optional local FastEmbed embeddings
- Dynamic studio context
- Configurable AI models
- Retry and request-limit handling

A simplified AI workflow:

```text
User Request
     ↓
Understand / Route
     ↓
Tools + RAG Retrieval
     ↓
Relevant Studio Context
     ↓
LLM
     ↓
Context-Aware Response
```

This allows the assistant to work with information relevant to studio operations instead of functioning as a generic chatbot.

---

# ⚡ Background Processing

StudioFlow uses:

**Celery + Redis + Celery Beat**

for asynchronous and scheduled operations.

This architecture supports workflows such as:

- Email processing
- Notifications
- Payment reminders
- Scheduled operations
- Background business tasks

---

# 🔴 Real-Time Features

Real-time functionality is implemented using:

**Django Channels + WebSockets**

This supports features such as real-time notifications and client portal updates.

---

# 🔌 REST API

StudioFlow exposes a versioned REST API using:

**Django REST Framework**

API documentation is provided through:

- Swagger
- ReDoc
- drf-spectacular

This makes StudioFlow suitable for integrations with mobile applications, frontend applications, automation services, and external business systems.

---

# 🛠️ Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python 3.12+, Django 5.1+, Django REST Framework |
| Database | PostgreSQL, pgvector |
| Background Jobs | Celery, Celery Beat, Redis |
| Real-Time | Django Channels, WebSockets, Daphne |
| Frontend | Django Templates, HTMX, Alpine.js, Tailwind CSS |
| AI | LangGraph, RAG, OpenAI-compatible APIs, Groq option, FastEmbed |
| API Documentation | drf-spectacular, Swagger, ReDoc |
| Production | Gunicorn, Nginx, WhiteNoise |
| Infrastructure | Docker, Docker Compose |
| Testing | pytest |
| Code Quality | Ruff, Black |
| CI | GitHub Actions |

---

# 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   Staff / Clients   │
                    └──────────┬──────────┘
                               │
                               ▼
               ┌────────────────────────────┐
               │     Django Application     │
               │ Templates / HTMX / API     │
               └─────────────┬──────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
     DRF REST API     Channels/WebSockets   Business Logic
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                    PostgreSQL + pgvector
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
           Redis / Celery           AI / RAG Layer
                                    LangGraph + LLM
```

---

# 🐳 Docker Architecture

The Docker environment includes:

```text
web             → Django + Gunicorn
postgres        → PostgreSQL
redis           → Redis
celery_worker   → Celery workers
celery_beat     → Scheduled tasks
nginx           → Reverse proxy / static & media serving
```

Health checks are configured for key services.

---

# 📂 Project Structure

```text
studioflow/
│
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── routing.py
│   └── celery.py
│
├── apps/
│   ├── accounts/
│   ├── studios/
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
│   ├── audit/
│   ├── dashboard/
│   ├── portal/
│   ├── staff/
│   ├── contracts/
│   ├── feedback/
│   ├── ai_fde/
│   ├── api/
│   └── core/
│
├── templates/
├── static/
├── media/
├── docker-compose.yml
└── pyproject.toml
```

---

# ⚙️ Quick Start

## Docker — Recommended

```bash
cp .env.example .env

docker compose up -d

docker compose exec web python manage.py migrate

docker compose exec web python manage.py seed_data

docker compose exec web python manage.py createsuperuser
```

Then open:

```text
http://localhost:8000
```

---

# 💻 Local Development

StudioFlow uses `pyproject.toml` and can be installed using `uv`.

```bash
uv sync --all-extras
```

Configure the environment:

```bash
cp .env.example .env
```

Run migrations:

```bash
python manage.py migrate
```

Load demonstration data:

```bash
python manage.py seed_data
```

Create an administrator:

```bash
python manage.py createsuperuser
```

Start Django:

```bash
python manage.py runserver
```

Background services can be started separately:

```bash
celery -A config worker -l info
```

and:

```bash
celery -A config beat -l info
```

PostgreSQL and Redis must also be available when running without Docker.

---

# 🔐 Environment Configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Configuration groups include:

- Django settings
- PostgreSQL
- Redis
- SMTP email
- Paystack
- Termii SMS
- WhatsApp Business API
- AI providers and models
- LangSmith observability
- External search
- AWS S3 storage

> ⚠️ Never commit production credentials or your local `.env` file.

---

# 📚 API Documentation

| Route | Purpose |
|---|---|
| `/api/v1/` | REST API |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/ai-fde/` | AI assistant |
| `/portal/` | Client portal |
| `/bookings/request/` | Public booking request |
| `/reports/` | Business reports |

---

# 🧪 Testing & Code Quality

Run the test suite:

```bash
uv run pytest
```

Run Ruff:

```bash
uv run ruff check .
```

The GitHub Actions CI workflow performs:

```text
Push / Pull Request
        ↓
      Ruff
        ↓
     pytest
        ↓
Django System Check
        ↓
Migration Consistency Check
```

The repository also contains a deployment-stage placeholder that can later be connected to a production deployment process.

---

# 📸 Screenshots

> Product screenshots will be added to this section.

Recommended showcase:

- Dashboard
- Client CRM
- Booking Calendar / Kanban
- Project Workflow
- Finance Dashboard
- Client Gallery
- Inventory Management
- AI Assistant

---

# 🎥 Product Demo

A public product demonstration will be added here.

A short **60–120 second StudioFlow walkthrough** can demonstrate:

1. Dashboard
2. Client management
3. Booking workflow
4. Project management
5. Finance
6. Gallery
7. AI assistant

---

# 💼 Business Use Cases

StudioFlow demonstrates experience building:

- Business management platforms
- CRM systems
- Booking systems
- SaaS applications
- REST APIs
- Payment systems
- Inventory platforms
- Workflow automation
- Real-time applications
- Reporting dashboards
- AI assistants
- RAG applications

---

# 🗺️ Roadmap

Future development can include:

- Multi-studio SaaS tenancy
- Advanced analytics
- Additional payment providers
- More AI workflow automation
- Mobile applications using the REST API
- Additional third-party integrations

---

# 👨‍💻 Developer

## Nazir Umar Ibrahim

**Python / Django Full-Stack Developer**

I build production-oriented:

- Django web applications
- REST APIs
- SaaS platforms
- Business automation systems
- AI-powered applications
- RAG systems

### Core Technologies

**Python • Django • DRF • PostgreSQL • Redis • Celery • Docker • Next.js • React • LangGraph • RAG**

---

# 🤝 Available for Work

I'm available for:

**Freelance Projects • Contract Work • Remote Python/Django Roles • Backend Development • AI Integration**

If you need a developer to build or improve a:

- Django application
- REST API
- SaaS platform
- CRM
- Booking platform
- Inventory system
- Business management application
- AI assistant
- RAG application
- Business automation workflow

feel free to contact me.

---

# ⭐ About This Project

StudioFlow is one of my flagship portfolio projects.

It demonstrates how I approach complete business software rather than isolated coding exercises — combining **backend engineering, database design, APIs, asynchronous processing, real-time communication, payments, business workflows, DevOps, automated testing, and AI integration**.

---

### StudioFlow

**Built with Python, Django and AI technologies for real photography business operations.**
