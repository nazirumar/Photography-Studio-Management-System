# Development Plan

## Overview

StudioFlow is built incrementally across 16 phases. Each phase delivers working, tested, deployable code. Phases build on each other; no phase requires rework of prior phases.

---

## Phase 0: Architecture Documentation

**Status:** This phase.

**Deliverables:**
- `docs/architecture.md` — tech stack, project layout, design decisions
- `docs/database.md` — models, relationships, constraints
- `docs/workflows.md` — status machines, service methods
- `docs/permissions.md` — role matrix, enforcement strategy
- `docs/development-plan.md` — this file

---

## Phase 1: Foundation

**Goal:** Runnable Django project with authentication, multi-tenancy skeleton, and CI pipeline.

**Deliverables:**
- Django project (`config/`), settings split (base, development, testing, production)
- Custom User model (email-based login)
- Studio model
- StaffProfile linking User to Studio
- Role choices on User (owner, manager, receptionist, photographer, photo_editor, printing_staff, accountant)
- Auth views: login, logout, password reset
- Base templates with Tailwind CSS, HTMX, Alpine.js
- Docker Compose (PostgreSQL, Redis, Django app)
- pytest configuration with factory_boy
- Ruff + Black configuration
- GitHub Actions CI (lint, test)
- Dashboard shell (empty landing page after login)
- First migration, zero data loss

**Acceptance:** `docker compose up` runs the app, login works, CI passes, `ruff check .` clean, `pytest` passes.

---

## Phase 2: Client CRM

**Goal:** Full client and lead management.

**Deliverables:**
- Client model, CRUD views, search/filter
- Lead model, CRUD views, status pipeline
- Lead-to-client conversion workflow
- Tags (many-to-many on Client)
- Notes on clients and leads
- Client list with search, pagination
- Lead kanban or pipeline view
- Staff assignment (account_manager on Client, assigned_to on Lead)
- AuditLog entries for all CRM operations
- Tests for all service methods
- Factory definitions for Client, Lead

**Acceptance:** Can create leads, convert to client, manage tags/notes, search clients. All operations audited.

---

## Phase 3: Packages

**Goal:** Service catalog and package management.

**Deliverables:**
- ServiceCategory model, CRUD
- Package model, CRUD, linked to category
- PackageAddon model, CRUD
- Package pricing (DecimalField)
- Package active/inactive toggle
- Package listing with category filter
- Tests for package CRUD and pricing

**Acceptance:** Can define service categories, create packages with add-ons, toggle active status.

---

## Phase 4: Bookings & Calendar

**Goal:** End-to-end booking management with calendar.

**Deliverables:**
- Booking model, status machine (enquiry → confirmed → completed/cancelled)
- Package snapshot (JSON field, frozen at booking time)
- BookingAddon (M2M with snapshotted prices)
- BookingStaff M2M (photographer/editor assignment)
- Booking CRUD views with status transitions
- Overlap detection (prevent double-booking same photographer on same date)
- Calendar view (month/week, color-coded by status)
- Booking detail page with timeline
- Deposit tracking
- Service methods: create_booking, confirm_booking, cancel_booking
- AuditLog for all booking transitions
- Notifications: booking confirmed, deposit received
- Tests for all booking workflows
- Factory definitions

**Acceptance:** Can create booking, assign staff, transition statuses, view calendar, detect overlaps. All transitions audited.

---

## Phase 5: Invoices & Payments

**Goal:** Financial document management.

**Deliverables:**
- Invoice model, status machine (draft → issued → paid/overdue/cancelled)
- InvoiceItem model (line items)
- Invoice number generation (unique per studio)
- Auto-create invoice from booking (package snapshot → line items)
- Invoice CRUD views
- Payment model, recording with audit trail
- Partial payment support
- Overpayment validation
- Receipt generation (PDF via WeasyPrint or ReportLab)
- Invoice status updates on payment
- Celery task: mark overdue invoices
- Tests for invoice/payment workflows
- Factory definitions

**Acceptance:** Can create invoices from bookings, record payments, handle partial payments, generate receipts. All financial operations audited.

---

## Phase 6: Project Workflow

**Goal:** Post-booking project tracking.

**Deliverables:**
- Project model, full status machine (13 stages)
- Auto-create project on booking confirmation
- ProjectTask model (subtasks with assignment and due dates)
- Status transition views with validation
- Project detail page with status timeline
- Task management (create, assign, complete)
- Deadline tracking
- Service methods for each transition
- AuditLog for all project status changes
- Notifications: shoot completed, selection received, editing approved
- Tests for all project workflows

**Acceptance:** Can track a project through all 13 stages, manage tasks, receive notifications at key transitions.

---

## Phase 7: Gallery & Selection

**Goal:** Photo proofing and client selection.

**Deliverables:**
- Gallery model (linked to Project)
- Photo model with image upload
- Thumbnail generation via Celery (multiple sizes)
- Proof gallery (client-facing, token-authenticated URL)
- Photo selection (client toggles photos, tracks extras)
- Extra-photo pricing
- Selection finalization (locks selection, notifies editor)
- Selection queue view for editors
- Photo sorting/ordering
- Tests for selection workflow

**Acceptance:** Can upload proofs, generate thumbnails, client can select photos, editor receives selection queue.

---

## Phase 8: Printing, Frames & Albums

**Goal:** Physical product fulfilment.

**Deliverables:**
- PrintJob model, status machine (6 stages)
- FrameOrder model, status machine
- AlbumOrder model, status machine
- Configurable paper types, frame sizes, album sizes (not hardcoded)
- Create print/frame/album orders from project
- Status transition views
- QC workflow (pass/fail with notes)
- Delivery tracking
- Tests for all production workflows

**Acceptance:** Can create print/frame/album orders, track through QC to delivery.

---

## Phase 9: Expenses & Profit

**Goal:** Expense tracking and project profitability.

**Deliverables:**
- Expense model with categories
- Link expenses to projects
- Expense CRUD with receipt upload
- Project profitability calculation (revenue - expenses)
- Expense reports by category, date range
- Tests for expense tracking

**Acceptance:** Can record expenses, link to projects, view profitability.

---

## Phase 10: Inventory & Equipment

**Goal:** Stock management and equipment tracking.

**Deliverables:**
- InventoryItem model with SKU, quantity, reorder level
- StockTransaction model (in, out, adjustment, damaged, returned)
- Stock in/out with transaction history
- Low-stock alerts (Celery Beat check)
- Equipment model with status tracking
- Equipment reservation (linked to bookings)
- Maintenance scheduling
- Tests for all inventory operations

**Acceptance:** Can manage stock levels, track transactions, receive low-stock alerts, manage equipment.

---

## Phase 11: Dashboard & Reports

**Goal:** Analytics and reporting.

**Deliverables:**
- Dashboard with KPIs (bookings this month, revenue, pending tasks)
- Charts: bookings by status, revenue trend, pipeline funnel
- Project pipeline view
- Revenue reports (by period, by package)
- Expense reports
- Profit reports
- CSV export for all reports
- Celery Beat for report caching
- Tests for report generation

**Acceptance:** Dashboard shows real KPIs, reports are accurate, CSV export works.

---

## Phase 12: Client Portal

**Goal:** Self-service portal for clients.

**Deliverables:**
- Client authentication (separate from staff login)
- Client dashboard (their bookings, invoices, projects)
- Invoice viewing and download
- Gallery access and photo selection
- Payment submission (link to Paystack in Phase 14)
- Notification preferences
- Tests for portal access and permissions

**Acceptance:** Client can log in, view their data, select photos, download invoices.

---

## Phase 13: Notifications

**Goal:** Multi-channel notification system.

**Deliverables:**
- Notification model (in-app)
- Email notifications (Celery async)
- Notification preferences per user
- Notification centre (inbox) in UI
- Mark as read/unread
- Email templates for all notification types
- Celery tasks for async email sending
- Tests for notification delivery

**Acceptance:** Notifications appear in-app and via email for all key events.

---

## Phase 14: Paystack Integration

**Goal:** Online payment processing.

**Deliverables:**
- Paystack API integration (initialisation, verification)
- Online payment flow on invoices
- Webhook handling (charge.success, charge.failed)
- Idempotency for payment recording
- Payment status updates via webhook
- Receipt generation on successful payment
- Error handling and retry logic
- Tests for payment flow and webhooks

**Acceptance:** Can pay invoices online via Paystack, webhooks update status correctly.

---

## Phase 15: Production Hardening

**Goal:** Security, performance, and operational readiness.

**Deliverables:**
- Security audit (OWASP top 10, Django security checklist)
- Rate limiting on auth endpoints
- CSRF, XSS, SQL injection testing
- Performance profiling (N+1 queries, slow queries)
- Database query optimisation
- Redis caching strategy
- Static file optimisation
- Backup and restore documentation
- Deployment runbook
- Load testing (basic)
- Final Ruff/Black pass
- All tests passing

**Acceptance:** Security audit passes, no N+1 queries, backup docs complete, deployment documented.

---

## Definition of Done

A phase is complete when:
1. All deliverables implemented and working.
2. Migrations created and tested.
3. Tests written and passing (`pytest`).
4. Lint passes (`ruff check .`).
5. No regressions in prior phases.
6. Server validation works (not just UI).
7. AuditLog entries present for all sensitive operations.
8. Permissions enforced server-side.
