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
