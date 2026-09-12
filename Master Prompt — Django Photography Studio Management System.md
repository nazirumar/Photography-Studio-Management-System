# ROLE

You are a senior full-stack Django engineer, software architect, UI/UX designer, database engineer, DevOps engineer, security engineer, QA engineer, and technical documentation writer.

Your task is to design and build a complete, production-ready **Photography Studio Management System**.

The application will initially be used internally by a photography studio in Nigeria, but its architecture must be clean enough to evolve later into a multi-tenant SaaS product for photographers and studios.

The project working name is:

# StudioFlow

Do not treat this as a simple CRUD tutorial.

Build it as professional production software with maintainable architecture, excellent performance, security, automated testing, responsive UI, clean code, proper database design, documentation, and deployment support.

---

# 1. MAIN BUSINESS OBJECTIVE

StudioFlow must manage the complete photography-studio workflow:

Client enquiry

→ Client registration

→ Package selection

→ Booking

→ Deposit/payment

→ Photography session

→ Photo upload/cataloguing

→ Client photo selection

→ Editing workflow

→ Printing

→ Album/frame preparation

→ Quality control

→ Final payment

→ Delivery

→ Completed project

It must also manage:

- Clients
- Leads
- Photography packages
- Bookings
- Calendar
- Photography jobs/projects
- Staff
- Payments
- Invoices
- Receipts
- Expenses
- Printing
- Frames
- Albums
- Inventory
- Equipment
- Photo selections
- File-delivery links
- Notifications
- Reports
- Business analytics
- Client portal
- Audit logs
- Application settings

---

# 2. TECHNOLOGY STACK

Use the latest stable versions that are compatible with one another.

## Backend

Use:

- Python
- Django
- PostgreSQL
- Django REST Framework where APIs are appropriate
- Redis
- Celery
- Celery Beat
- Django Channels only where real-time functionality provides genuine value

Prefer Django's built-in capabilities before adding unnecessary third-party packages.

## Frontend

Use server-rendered Django as the primary architecture.

Use:

- Django Templates
- HTMX
- Alpine.js
- Tailwind CSS
- Vanilla JavaScript where appropriate

Do NOT build a separate React/Next.js frontend for the initial version.

The frontend must still feel like a modern SaaS application.

## Development and deployment

Use:

- Docker
- Docker Compose
- PostgreSQL
- Redis
- Gunicorn or an appropriate production ASGI server
- Nginx
- Environment variables
- `.env.example`
- GitHub Actions for CI
- pytest
- Ruff
- Black or another compatible formatter
- pre-commit hooks

Never commit secrets.

---

# 3. ENGINEERING PRINCIPLES

Follow these rules throughout development.

## Architecture

Use a modular Django architecture.

Avoid:

- giant `models.py`
- giant `views.py`
- giant `utils.py`
- business logic inside templates
- business logic scattered across views
- circular dependencies
- unnecessary signals
- duplicated logic
- over-engineering

Use clearly separated:

- models
- services
- selectors/query services
- forms
- validators
- permissions
- tasks
- APIs
- views
- templates
- tests

Business rules should live primarily in service/domain layers rather than being duplicated across views.

Use database transactions for operations involving multiple dependent writes.

Use PostgreSQL constraints wherever possible.

Use `select_related()` and `prefetch_related()` deliberately.

Avoid N+1 database queries.

Add indexes for frequently filtered, joined, sorted, and searched fields.

---

# 4. PROJECT STRUCTURE

Create a professional project structure similar to:

```text
studioflow/
├── manage.py
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
│
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── celery.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── development.py
│       ├── testing.py
│       └── production.py
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
│   ├── dashboard/
│   ├── audit/
│   └── core/
│
├── templates/
├── static/
├── media/
├── tests/
├── scripts/
└── docs/
```

Adjust this structure when there is a strong technical reason.

---

# 5. MULTI-TENANCY PREPARATION

The first deployment may contain one studio, but design the data model so StudioFlow can later support multiple studios.

Create a `Studio` model early.

Most business entities should belong to a studio.

Examples:

```text
Studio
 ├── Staff
 ├── Clients
 ├── Packages
 ├── Bookings
 ├── Projects
 ├── Payments
 ├── Expenses
 ├── Inventory
 └── Reports
```

Every studio-owned database query must be properly scoped.

Never allow users from one studio to access another studio's information.

Do not implement complicated SaaS billing initially unless instructed, but do not design the database in a way that makes multi-tenancy impossible later.

---

# 6. AUTHENTICATION

Implement a custom Django User model from the beginning.

Do not use Django's default User model directly and then attempt migration later.

Support:

- Login
- Logout
- Password reset
- Password change
- Account activation
- Profile
- User avatar
- Last login
- Active/inactive accounts

Use email as an important account identifier.

Support roles.

Initial roles:

- Owner
- Manager
- Receptionist
- Photographer
- Photo Editor
- Printing Staff
- Accountant

Implement role-based permissions.

Examples:

Owner:

Full access.

Manager:

Most operational access.

Receptionist:

Clients, bookings and basic payment recording.

Photographer:

Assigned sessions and projects.

Editor:

Editing queues and photo-selection workflow.

Printing Staff:

Print, frame and album jobs.

Accountant:

Payments, invoices, expenses and financial reports.

Do not rely only on hiding buttons.

Permissions must be enforced server-side.

---

# 7. STUDIO SETTINGS

Allow each studio to configure:

- Studio name
- Logo
- Phone
- WhatsApp number
- Email
- Website
- Address
- City
- State
- Country
- Default currency
- Time zone
- Invoice prefix
- Receipt prefix
- Booking prefix
- Project prefix
- Tax settings
- Default booking deposit percentage
- Default payment terms
- Business hours
- Social links

For the initial target market:

Default currency may be NGN.

Display Nigerian currency cleanly:

`₦250,000`

Do not hard-code NGN throughout the system because future studios may use other currencies.

---

# 8. CLIENT MANAGEMENT

Create comprehensive client management.

Client fields should include where appropriate:

- Unique client number
- First name
- Last name
- Display name
- Phone
- WhatsApp number
- Email
- Address
- City
- State
- Notes
- Referral source
- Date created
- Last activity
- Assigned account manager
- Tags
- Status
- Studio

Allow:

- Add client
- Edit client
- Archive client
- Search clients
- Filter clients
- View client history
- View bookings
- View projects
- View invoices
- View payments
- View outstanding balance
- View delivered jobs
- Add internal notes

Do not permanently delete important business history casually.

Use archive/soft-delete strategies where appropriate.

---

# 9. LEAD / ENQUIRY MANAGEMENT

Before somebody becomes a client, support enquiries/leads.

Lead statuses:

- New
- Contacted
- Follow-up
- Quotation sent
- Negotiating
- Won
- Lost

Lead fields:

- Name
- Phone
- Email
- WhatsApp
- Event/service type
- Expected date
- Estimated budget
- Source
- Assigned staff
- Notes
- Next follow-up
- Status

Allow conversion:

`Lead → Client → Booking`

Preserve lead history after conversion.

---

# 10. PHOTOGRAPHY PACKAGES

Allow the studio to create packages.

Examples:

- Passport Photography
- Studio Portrait
- Birthday Session
- Graduation
- Wedding
- Naming Ceremony
- Corporate Photography
- Event Coverage
- Outdoor Session

Package attributes:

- Name
- Service/category
- Description
- Price
- Deposit requirement
- Duration
- Number of outfit changes
- Number of edited images
- Number of prints
- Print sizes
- Number of frames
- Frame sizes
- Album included
- Album specification
- Digital files included
- Delivery estimate
- Active/inactive
- Featured status

Allow package add-ons.

Examples:

- Additional edited image
- Additional hour
- Extra frame
- Extra album
- Drone coverage
- Additional photographer
- Express delivery
- Makeup
- Transportation

Package prices must be copied/snapshotted into bookings so changing the package later does not modify historical invoices.

---

# 11. BOOKINGS

Create a professional booking system.

Booking fields:

- Booking reference
- Client
- Package
- Service
- Shoot/event title
- Event type
- Date
- Start time
- End time
- Location
- Studio/outdoor/event
- Photographer
- Additional staff
- Package snapshot
- Base price
- Add-ons
- Discount
- Tax where applicable
- Total amount
- Deposit required
- Amount paid
- Balance
- Payment status
- Booking status
- Special instructions
- Internal notes
- Client notes
- Created by
- Created date

Booking statuses:

- Enquiry
- Tentative
- Awaiting Deposit
- Confirmed
- In Progress
- Completed
- Cancelled
- No Show

Prevent accidental double-booking of photographers/resources.

Warn staff when:

- photographer already has another assignment
- studio room is occupied
- equipment is reserved
- booking times overlap

Provide calendar views:

- Day
- Week
- Month

Allow filtering by:

- Photographer
- Service
- Status
- Location

---

# 12. BOOKING WORKFLOW

A typical booking workflow:

```text
Enquiry
↓
Quotation
↓
Booking
↓
Deposit
↓
Confirmed
↓
Shoot
↓
Photography Project
↓
Editing
↓
Printing
↓
Delivery
↓
Completed
```

Actions must be auditable.

Important status changes must record:

- previous status
- new status
- user
- timestamp
- optional note

---

# 13. PHOTOGRAPHY PROJECT MANAGEMENT

A confirmed booking should be able to create a photography project.

Project fields:

- Project reference
- Client
- Booking
- Package
- Photographer
- Editor
- Project manager
- Shoot date
- Expected delivery
- Actual delivery
- Status
- Priority
- Total captured photos
- Total photos for selection
- Selected photos
- Edited photos
- Printed photos
- Internal notes

Project workflow:

```text
Scheduled
↓
Shoot Completed
↓
Files Imported
↓
Awaiting Client Selection
↓
Selection Received
↓
Editing
↓
Editing Review
↓
Ready For Print
↓
Printing
↓
Quality Control
↓
Ready For Delivery
↓
Delivered
↓
Completed
```

Allow some steps to be skipped based on package.

Example:

Passport photography may not need the complete workflow.

---

# 14. PROJECT TASKS

Support project-related tasks.

Examples:

- Backup RAW files
- Generate previews
- Send selection gallery
- Retouch selected photos
- Design album
- Print 16x20 frame
- Verify prints
- Send delivery notification

Task fields:

- Project
- Title
- Description
- Assigned staff
- Due date
- Priority
- Status
- Completed date
- Notes

Statuses:

- To Do
- In Progress
- Blocked
- Done

---

# 15. PHOTO / GALLERY MANAGEMENT

Do NOT store raw image binary data inside PostgreSQL.

Store file metadata and paths/URLs.

Design storage abstraction so development can use local storage and production can use an object-storage provider.

Support:

- Photo previews
- Thumbnails
- Final photos
- File metadata
- Image numbering
- Upload batches
- Gallery collections
- Client selections
- Delivery files

Each image can have:

- Project
- File name
- Original file name
- Storage key
- Thumbnail
- Preview
- Image number
- Capture date where available
- Selected status
- Edited status
- Delivered status
- Notes

RAW files should generally remain outside the application's normal web-preview pipeline.

---

# 16. CLIENT PHOTO SELECTION

Implement one of the system's most valuable features.

After a shoot:

1. Photographer uploads proofs/previews.
2. System creates a private selection gallery.
3. Client receives secure access.
4. Client sees proofs.
5. Client selects preferred photographs.
6. Client submits selection.
7. Editor receives updated editing queue.

Support:

- Select/unselect image
- Selection count
- Maximum included images
- Extra-selection pricing
- Finalize selection
- Prevent accidental modification after final submission unless reopened
- Internal staff override
- Favourite/priority marker

Example:

```text
Package includes: 15 edited photographs
Selected: 18
Included: 15
Additional: 3
Extra cost: ₦15,000
```

The pricing should calculate automatically based on configured extra-photo cost.

---

# 17. CLIENT PORTAL

Create a secure client portal.

Clients should be able to:

- View bookings
- View project status
- View invoices
- View payment history
- See outstanding balance
- Access selection galleries
- Select photographs
- Approve selections
- View delivery links
- Download delivered files
- View receipts
- Update limited profile details

Clients must never see:

- staff-only notes
- internal costs
- profit
- other clients
- internal business analytics

Consider password-based accounts and secure expiring magic links where appropriate.

---

# 18. FINANCE

Create a proper finance module.

Entities may include:

- Invoice
- InvoiceItem
- Payment
- Receipt
- Credit/refund if needed

Invoice fields:

- Invoice number
- Client
- Booking
- Project
- Issue date
- Due date
- Subtotal
- Discount
- Tax
- Total
- Amount paid
- Balance
- Status
- Notes

Invoice statuses:

- Draft
- Issued
- Partially Paid
- Paid
- Overdue
- Cancelled

Support multiple partial payments.

Example:

```text
Wedding Package: ₦300,000

Deposit:
₦100,000

Second payment:
₦120,000

Final payment:
₦80,000

Balance:
₦0
```

Never assume one invoice equals one payment.

---

# 19. PAYMENT METHODS

Support configurable payment methods.

Examples:

- Cash
- Bank Transfer
- POS
- Card
- Online Payment
- Other

Payment fields:

- Reference
- Invoice
- Client
- Booking/project
- Amount
- Payment date
- Method
- External transaction reference
- Recorded by
- Notes
- Verification status

Avoid allowing payment history to be silently modified.

Use audit logs.

---

# 20. PAYSTACK

Design an integration layer for online payments.

Paystack can be implemented as an optional integration.

Use secure server-side verification.

Never trust a frontend redirect alone as proof of successful payment.

Use webhooks.

Verify webhook signatures.

Ensure idempotency.

Never create duplicate payment records from repeated webhook delivery.

Store external transaction references.

Keep payment integration isolated from business logic.

---

# 21. RECEIPTS AND INVOICES

Generate professional printable:

- Invoice
- Receipt
- Quotation

Include:

- Studio logo
- Studio name
- Contact
- Client
- Reference number
- Item description
- Amount
- Payment status
- Date
- Balance
- Footer

Support PDF export.

Keep PDF-generation code separate from core domain logic.

---

# 22. EXPENSE MANAGEMENT

Track business expenses.

Expense categories:

- Printing
- Frames
- Albums
- Fuel
- Transportation
- Electricity
- Generator
- Rent
- Internet
- Staff
- Equipment
- Repairs
- Marketing
- Software
- Miscellaneous

Fields:

- Reference
- Category
- Vendor
- Description
- Amount
- Date
- Payment method
- Project if relevant
- Receipt attachment
- Entered by
- Notes

Allow recurring categories but do not overcomplicate recurring accounting in V1.

---

# 23. PROFITABILITY

Calculate both revenue and actual project profitability.

Project financial summary:

```text
Revenue
Package: ₦250,000
Extra photographs: ₦15,000
Frame upgrade: ₦20,000

Total Revenue: ₦285,000

Costs
Printing: ₦12,000
Frames: ₦22,000
Transport: ₦10,000
Album: ₦35,000

Project Cost: ₦79,000

Gross Project Profit:
₦206,000
```

Ensure calculations use Decimal, never floating-point values for money.

---

# 24. PRINTING MANAGEMENT

Create printing workflow.

Print job fields:

- Project
- Client
- Photo
- Print size
- Quantity
- Paper/media type
- Printer/vendor
- Internal cost
- Customer price
- Status
- Requested date
- Due date
- Completed date
- Notes

Statuses:

- Pending
- Preparing
- Sent to Printer
- Printing
- Quality Check
- Ready
- Delivered
- Reprint Required

---

# 25. FRAME MANAGEMENT

Track frames.

Frame order fields:

- Project
- Size
- Type
- Orientation
- Quantity
- Supplier
- Internal cost
- Customer price
- Due date
- Status
- Notes

Examples:

- 8×10
- 12×16
- 16×20
- 20×24
- 24×36

Sizes must be configurable rather than permanently hard-coded.

---

# 26. ALBUM MANAGEMENT

Album order:

- Project
- Album type
- Size
- Number of spreads/pages
- Supplier
- Design status
- Client approval
- Printing status
- Cost
- Selling price
- Delivery date

Workflow:

```text
Pending Selection
→ Designing
→ Internal Review
→ Client Approval
→ Sent For Production
→ Received
→ Quality Check
→ Delivered
```

---

# 27. INVENTORY

Track consumable studio inventory.

Examples:

- Photo paper
- Ink
- Packaging
- Flash batteries
- Backdrops
- Albums
- Frames
- USB drives

Inventory item:

- SKU
- Name
- Category
- Quantity
- Unit
- Reorder level
- Cost price
- Supplier
- Location
- Active
- Notes

Create inventory transactions.

Types:

- Stock In
- Stock Out
- Adjustment
- Damaged
- Returned

Never simply overwrite stock quantities without transaction history.

Calculate quantity from controlled stock movements or maintain a synchronized audited quantity.

Generate low-stock alerts.

---

# 28. EQUIPMENT MANAGEMENT

Photography equipment differs from consumable inventory.

Track:

- Cameras
- Lenses
- Lights
- Flashes
- Tripods
- Stands
- Batteries
- Memory cards
- Computers
- Printers

Equipment fields:

- Asset number
- Name
- Brand
- Model
- Serial number
- Purchase date
- Purchase cost
- Warranty expiry
- Current status
- Assigned employee
- Condition
- Maintenance date
- Next maintenance
- Notes

Statuses:

- Available
- In Use
- Reserved
- Maintenance
- Damaged
- Retired

Allow equipment reservations against photography bookings.

---

# 29. STAFF MANAGEMENT

Each staff profile may contain:

- User
- Employee number
- Job title
- Role
- Phone
- Hire date
- Active status
- Emergency contact if appropriate
- Skills
- Notes

Allow assignments to bookings/projects.

Staff dashboard should show:

- today's assignments
- upcoming bookings
- editing queue
- overdue tasks
- printing jobs
- notifications

---

# 30. DASHBOARD

Create a professional SaaS-style dashboard.

Top metrics:

- Today's bookings
- Upcoming bookings
- Active projects
- Jobs awaiting editing
- Jobs awaiting client selection
- Jobs ready for printing
- Jobs ready for delivery
- Outstanding balance
- Revenue this month
- Expenses this month
- Approximate profit this month

Sections:

### Today's Schedule

Show:

- Time
- Client
- Service
- Photographer
- Status

### Workflow Pipeline

Show counts for:

```text
Shoot
Selection
Editing
Printing
Ready
Delivered
```

### Outstanding Payments

Show relevant unpaid/part-paid invoices.

### Deadlines

Show projects approaching delivery deadlines.

### Recent Activity

Examples:

- Payment recorded
- Booking confirmed
- Selection submitted
- Project moved to Editing
- Print marked complete

---

# 31. REPORTING

Reports must support date filters.

Reports:

- Daily revenue
- Weekly revenue
- Monthly revenue
- Annual revenue
- Expenses
- Profit
- Outstanding balances
- Payments by method
- Bookings by service
- Package performance
- Photographer workload
- Project turnaround time
- Client acquisition source
- Inventory usage
- Most valuable clients
- Cancellation rate

Use charts only where they improve understanding.

Tables should be exportable where appropriate.

Support CSV export.

Later support PDF where useful.

---

# 32. SEARCH

Implement global search.

Search:

- Clients
- Booking references
- Project references
- Invoice numbers
- Receipt numbers
- Phone numbers

Use efficient PostgreSQL search techniques when appropriate.

Do not execute expensive wildcard queries unnecessarily.

---

# 33. NOTIFICATIONS

Support in-app notifications.

Notification examples:

- Booking tomorrow
- Deposit overdue
- Project delivery overdue
- Client submitted selections
- Editor completed editing
- Print ready
- Low inventory
- Equipment maintenance due
- Payment received

Use Celery for asynchronous notifications.

Future channels:

- Email
- SMS
- WhatsApp

Design notification adapters/interfaces so providers can be replaced.

---

# 34. WHATSAPP SUPPORT

Do not use unofficial automation that violates service rules.

Design a clean provider layer for future official WhatsApp Business API integration.

Useful notifications:

- Booking confirmation
- Booking reminder
- Payment receipt
- Selection gallery ready
- Editing complete
- Project ready for pickup
- Delivery link available

---

# 35. AUDIT LOGGING

Add application audit logs for sensitive events.

Examples:

- payment created
- payment corrected
- invoice cancelled
- booking cancelled
- role changed
- project status changed
- inventory adjusted
- refund recorded
- user disabled

Record:

- User
- Action
- Entity
- Entity ID
- Timestamp
- Before values where sensible
- After values where sensible
- IP where appropriate

Do not log passwords, tokens or sensitive secrets.

---

# 36. SECURITY

Follow modern Django security practices.

Protect against:

- CSRF
- XSS
- SQL injection
- insecure direct object references
- broken access controls
- file upload attacks
- brute-force login where appropriate
- unsafe redirects
- insecure cookies
- exposed secrets

Production configuration should include:

- HTTPS
- secure cookies
- CSRF secure cookie
- HSTS after proper deployment validation
- allowed hosts
- trusted origins
- secure secret key management

Validate uploaded file types and sizes.

Never trust file extensions alone.

Never expose original private media using publicly guessable URLs.

---

# 37. DATABASE

Use PostgreSQL.

Important general fields should use appropriate types.

Use:

- UUIDs where useful for externally exposed entities
- timestamps
- Decimal for monetary data
- database constraints
- indexes
- unique constraints scoped to Studio

Example:

Booking reference may be unique per studio.

Invoice reference may be unique per studio.

Never use JavaScript-generated database identifiers as authoritative IDs.

---

# 38. MONEY HANDLING

Money is critical.

Use Python `Decimal`.

Never use float.

Centralize currency formatting.

Support:

```text
₦5,000
₦125,000
₦1,500,000
```

Database examples:

```python
models.DecimalField(
    max_digits=14,
    decimal_places=2,
)
```

Never compute invoice totals only in JavaScript.

The server must be authoritative.

---

# 39. TIMEZONE

Use timezone-aware datetimes.

The initial studio may operate in Nigeria.

Default suggestion:

`Africa/Lagos`

Do not disable Django timezone support.

---

# 40. FRONTEND DESIGN

Create a premium photography-business aesthetic.

The admin/staff interface should look like professional modern SaaS software.

Layout:

- Collapsible sidebar
- Header
- Search
- Notifications
- User profile menu
- Main content area

Sidebar:

```text
Dashboard

CRM
  Clients
  Leads

Studio
  Calendar
  Bookings
  Projects
  Galleries

Production
  Editing Queue
  Printing
  Frames
  Albums

Finance
  Invoices
  Payments
  Expenses

Resources
  Inventory
  Equipment

Reports
Staff
Settings
```

Use:

- good whitespace
- clear hierarchy
- accessible typography
- responsive tables
- cards
- badges
- drawers
- modals only when appropriate
- skeleton/loading indicators for asynchronous sections
- clear empty states
- confirmation for destructive actions

Avoid excessive animations.

---

# 41. MOBILE RESPONSIVENESS

Staff may use phones during events.

Ensure major workflows work on mobile:

- dashboard
- bookings
- client lookup
- payment recording
- project update
- tasks
- delivery confirmation

Desktop tables should become usable card/stack layouts where necessary.

---

# 42. ACCESSIBILITY

Use:

- semantic HTML
- labels for form fields
- keyboard navigation
- sufficient contrast
- meaningful focus styles
- accessible errors
- ARIA only where appropriate

Do not create interfaces dependent exclusively on mouse hover.

---

# 43. HTMX

Use HTMX for useful interactions:

- search
- pagination
- filters
- status updates
- modal forms
- inline actions
- dashboard widgets
- dependent fields

Every important workflow should still maintain server-side validation.

Keep HTMX partial templates organized.

Do not create an unstructured collection of fragments.

---

# 44. ALPINE.JS

Use Alpine for lightweight browser state such as:

- sidebar
- dropdowns
- tabs
- simple modals
- client-side presentation interactions

Do not move complex domain rules into Alpine.

---

# 45. API

Use Django REST Framework for APIs that actually need API access.

Possible endpoints:

```text
/api/v1/clients/
/api/v1/bookings/
/api/v1/projects/
/api/v1/payments/
/api/v1/calendar/
```

Version the API.

Implement:

- authentication
- permissions
- throttling where appropriate
- pagination
- filters
- validation
- OpenAPI documentation

Do not duplicate all server-rendered business logic in APIs.

Share services.

---

# 46. FILE STORAGE

Implement storage abstraction.

Development:

Local media storage.

Production:

S3-compatible object storage or another supported secure cloud provider.

Create separate areas for:

- avatars
- logos
- receipts
- proof images
- final deliveries
- attachments

Create thumbnail/previews asynchronously.

Do not send full-resolution files to thumbnail gallery pages.

---

# 47. PERFORMANCE

Performance requirements:

- optimized queries
- indexed filters
- pagination
- cached expensive dashboard summaries where appropriate
- async image processing
- async email
- async reports where appropriate
- avoid loading entire galleries at once
- lazy-load media
- generate thumbnails
- prevent N+1 queries

Add Django Debug Toolbar in development only.

Use query profiling during development.

---

# 48. CELERY TASKS

Use Celery for appropriate background work.

Examples:

- Email
- Thumbnail generation
- Notification dispatch
- Reminder generation
- Reports
- Cleanup of expired links
- Scheduled overdue checks

Use Celery Beat for:

- booking reminders
- delivery deadline checks
- invoice overdue checks
- low-stock checks
- equipment maintenance reminders

Ensure tasks are idempotent whenever possible.

---

# 49. TESTING

Write automated tests throughout development.

Use pytest.

Test:

## Models

- constraints
- calculations
- relationships
- states

## Services

- booking creation
- payments
- project workflow
- invoice calculations
- stock movements

## Views

- authentication
- permissions
- forms
- HTMX endpoints

## APIs

- auth
- permissions
- validation
- serialization

## Security

Ensure unauthorized staff cannot access restricted records.

## Finance

Finance calculations require especially strong coverage.

Example tests:

- partial payments
- overpayment prevention/handling
- discount
- invoice balance
- expense totals
- project profit

Aim for meaningful coverage, not artificially high coverage.

---

# 50. FACTORIES

Use test factories or fixtures with realistic data.

Example users:

- Owner
- Receptionist
- Photographer
- Editor
- Accountant

Example clients and packages.

Allow local development to seed demo data.

---

# 51. LOGGING

Configure structured and useful logging.

Separate where appropriate:

- application logs
- errors
- security events
- Celery logs

Never log:

- passwords
- secret keys
- complete card details
- authentication tokens

---

# 52. ERROR HANDLING

Create polished:

- 400
- 403
- 404
- 500

pages.

Return helpful validation errors.

Never expose stack traces in production.

---

# 53. BACKUPS

Document:

- PostgreSQL backup
- media backup
- restore procedure
- disaster recovery basics

Provide commands/scripts where appropriate.

---

# 54. CI/CD

Create GitHub Actions.

On pull requests/run:

- dependency installation
- linting
- formatting check
- tests
- Django system check
- migration consistency check

Example:

```text
ruff
pytest
python manage.py check
python manage.py makemigrations --check --dry-run
```

---

# 55. DOCKER

Provide production-conscious Docker configuration.

Services:

- web
- postgres
- redis
- celery_worker
- celery_beat
- nginx if included in deployment configuration

Use health checks where appropriate.

Avoid running development servers in production.

---

# 56. ENVIRONMENT VARIABLES

Create `.env.example`.

Possible variables:

```text
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=

DATABASE_URL=

REDIS_URL=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

PAYSTACK_PUBLIC_KEY=
PAYSTACK_SECRET_KEY=

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=
```

Never commit the actual `.env`.

---

# 57. DOCUMENTATION

Maintain professional documentation.

README must include:

- overview
- features
- architecture
- technologies
- installation
- local development
- Docker development
- environment variables
- migrations
- creating superuser
- Celery
- tests
- linting
- deployment notes

Create `/docs`.

Suggested files:

```text
docs/
├── architecture.md
├── database.md
├── permissions.md
├── workflows.md
├── api.md
├── deployment.md
├── backup_restore.md
└── contributing.md
```

---

# 58. DEVELOPMENT STRATEGY

DO NOT attempt to implement everything in one giant generation.

Build StudioFlow incrementally.

At the beginning of every phase:

1. Review current code.
2. Review current migrations.
3. Review tests.
4. Explain what will change.
5. Identify architectural risks.
6. Make a short implementation plan.

Then implement.

At the end:

1. Run formatting.
2. Run linting.
3. Run tests.
4. Run Django checks.
5. Check migrations.
6. Fix all discovered problems.
7. Update documentation.
8. Summarize changes.

Do not leave known failing tests.

---

# 59. PHASE 0 — ARCHITECTURE

Before writing feature code:

Create:

- requirements analysis
- architecture decisions
- database/domain map
- permissions matrix
- project structure
- workflow states
- naming conventions
- coding conventions

Produce a concise architecture document.

Then initialize the project.

---

# 60. PHASE 1 — FOUNDATION

Implement:

- Django project
- settings split
- environment handling
- PostgreSQL
- custom User
- Studio
- Staff profile
- Role/permissions architecture
- authentication
- base templates
- Tailwind
- HTMX
- Alpine
- main navigation
- dashboard shell
- Docker
- pytest
- Ruff
- CI

Acceptance criteria:

- App starts
- User can log in
- Studio owner exists
- Role restrictions work
- Dashboard shell loads
- PostgreSQL works
- Redis works
- Celery works
- Tests pass

---

# 61. PHASE 2 — CLIENT CRM

Implement:

- Clients
- Leads
- Lead pipeline
- Search
- Tags
- Notes
- Client details
- Lead conversion

Acceptance criteria:

A receptionist can create an enquiry and convert it into a client without duplicate data entry.

---

# 62. PHASE 3 — PACKAGES

Implement:

- Service categories
- Packages
- Package features
- Add-ons
- Pricing
- Activation/deactivation

Acceptance criteria:

Manager can create reusable photography packages and configurable add-ons.

---

# 63. PHASE 4 — BOOKINGS & CALENDAR

Implement:

- Bookings
- Assign staff
- Booking references
- Package snapshot
- Pricing calculations
- Calendar
- overlap detection
- confirmation status

Acceptance criteria:

Staff can schedule photography sessions without unknowingly double-booking staff/resources.

---

# 64. PHASE 5 — INVOICES & PAYMENTS

Implement:

- Quotations
- Invoices
- Invoice items
- Partial payments
- Receipts
- outstanding balance
- payment history

Acceptance criteria:

A ₦300,000 booking can receive several payments and always display the correct remaining balance.

---

# 65. PHASE 6 — PROJECT WORKFLOW

Implement:

- Projects
- Project status history
- Staff assignment
- Tasks
- Deadlines
- production workflow

Acceptance criteria:

A booking can progress from confirmed shoot through editing and final delivery with full history.

---

# 66. PHASE 7 — GALLERY & SELECTION

Implement:

- Proof gallery
- thumbnails
- gallery pagination
- client access
- client selection
- selection limits
- additional image pricing
- finalize selection

Acceptance criteria:

A client can securely select included photographs and automatically see extra-photo charges.

---

# 67. PHASE 8 — PRINTING, FRAMES & ALBUMS

Implement:

- Print jobs
- Frame jobs
- Album jobs
- internal costs
- customer prices
- production statuses
- quality control

---

# 68. PHASE 9 — EXPENSES & PROFIT

Implement:

- Expense categories
- Expenses
- Project cost
- Monthly expenses
- Gross project profit

Acceptance criteria:

Owner can view revenue, expenses and approximate profit rather than revenue alone.

---

# 69. PHASE 10 — INVENTORY & EQUIPMENT

Implement:

- Inventory items
- Stock transactions
- Low stock
- Equipment
- Equipment assignments
- Maintenance
- Booking reservation

---

# 70. PHASE 11 — DASHBOARD & REPORTS

Implement:

- KPIs
- finance charts
- workflow pipeline
- outstanding payments
- upcoming deadlines
- staff workload
- reports
- CSV export

Optimize database queries before completion.

---

# 71. PHASE 12 — CLIENT PORTAL

Implement:

- client authentication/access
- dashboard
- bookings
- projects
- invoices
- payments
- gallery
- delivery

Add strict authorization tests.

---

# 72. PHASE 13 — NOTIFICATIONS

Implement:

- notification center
- email provider
- booking reminders
- payment notices
- selection alerts
- delivery alerts

Run asynchronously through Celery.

---

# 73. PHASE 14 — PAYSTACK

Implement:

- initialize transaction
- verify transaction
- webhook
- signature verification
- idempotency
- reconciliation
- tests with mocked requests

Never use production credentials in source code.

---

# 74. PHASE 15 — PRODUCTION HARDENING

Perform:

- security audit
- authorization audit
- dependency audit
- database query review
- index review
- caching review
- media-security review
- logging review
- Docker review
- deployment review
- backup documentation
- restore testing
- load-sensitive endpoint review

Run all automated tests.

---

# 75. DASHBOARD EXAMPLE

The main dashboard could show:

```text
STUDIOFLOW

Good morning

TODAY
4 Bookings
7 Active Projects
3 Awaiting Editing
2 Ready for Delivery

FINANCE
Revenue This Month     ₦1,450,000
Received               ₦1,080,000
Outstanding              ₦370,000
Expenses                  ₦425,000
Estimated Profit         ₦655,000

TODAY'S BOOKINGS

10:00
Aisha Bello
Birthday Portrait
Photographer: Musa
Confirmed

13:30
Abubakar Ibrahim
Passport Session
Photographer: Nazir
Confirmed

16:00
Fatima & Umar
Pre-Wedding
Photographer: Nazir
Deposit Pending

PRODUCTION

Awaiting Selection     5
Editing                8
Printing               3
Quality Check          2
Ready For Delivery     4
```

---

# 76. CLIENT PAGE EXAMPLE

```text
Aisha Bello

Phone: +234...
WhatsApp: +234...
Email: ...

Lifetime Value: ₦485,000
Outstanding: ₦75,000

BOOKINGS
3

ACTIVE PROJECTS
1

PAYMENTS
₦410,000

Recent Activity

September 1
Wedding project created

August 30
₦150,000 payment received

August 25
Wedding booking confirmed
```

---

# 77. PROJECT PAGE EXAMPLE

```text
PROJECT
STF-PRJ-2026-0042

Client:
Aisha Bello

Service:
Wedding Photography

Package:
Premium Wedding

Status:
Editing

Shoot:
21 September 2026

Delivery Deadline:
15 October 2026

Photographer:
Nazir

Editor:
Musa

PRODUCTION

Captured:       1,420
Proofs:           320
Client Selected:   80
Edited:            52
Printed:            0

PAYMENT

Total:       ₦350,000
Paid:        ₦250,000
Outstanding: ₦100,000

WORKFLOW

✓ Shoot Completed
✓ Files Imported
✓ Selection Received
● Editing
○ Review
○ Printing
○ Delivery
```

---

# 78. IMPORTANT DOMAIN RULES

Implement these rules deliberately.

## Booking

A booking should snapshot its package pricing.

Historical bookings must not change if package pricing changes.

## Payment

Payments cannot silently disappear.

Corrections must be auditable.

## Invoice

Invoice amount calculations are server-side.

## Project

Invalid state transitions should be rejected.

Example:

Do not allow:

`Scheduled → Delivered`

unless an authorized override exists and is logged.

## Inventory

Stock cannot change without transaction history.

## Gallery

Client access must be private.

## Permissions

Every object must be scoped to the user's studio.

---

# 79. STATE MACHINES

For important workflows, implement explicit transition logic.

Do not scatter:

```python
project.status = "whatever"
project.save()
```

through the codebase.

Use controlled service methods such as:

```python
complete_shoot(...)
submit_selection(...)
start_editing(...)
complete_editing(...)
send_to_print(...)
mark_ready(...)
deliver_project(...)
```

Each action should validate:

- permission
- current state
- required data
- business rules

Then perform:

- state update
- history creation
- notification
- audit entry

inside an appropriate transaction.

---

# 80. CODING QUALITY

Use:

- clear naming
- type hints where beneficial
- concise docstrings
- modular services
- small focused functions
- reusable components
- consistent error handling

Avoid:

- premature abstractions
- unnecessary design patterns
- massive inheritance trees
- needless third-party dependencies

Code should be understandable to another Django developer.

---

# 81. MIGRATIONS

Create migrations carefully.

Never edit already-deployed migrations casually.

Add constraints and indexes deliberately.

Before each phase completion run:

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py check
```

---

# 82. GIT WORKFLOW

Make logical commits.

Examples:

```text
feat(accounts): implement custom user and staff roles
feat(clients): add CRM and lead conversion
feat(bookings): add booking workflow and calendar
feat(finance): support partial invoice payments
feat(projects): add production workflow
test(finance): cover payment reconciliation
fix(bookings): prevent photographer schedule overlap
```

Do not create one enormous commit containing the entire system.

---

# 83. DEFINITION OF DONE

A feature is not finished merely because a page appears.

A feature is complete only when:

- database model is correct
- migrations are included
- permissions work
- server validation works
- UI works
- mobile layout works where applicable
- tests exist
- queries are reasonable
- security has been considered
- errors are handled
- docs are updated
- lint passes
- tests pass

---

# 84. DO NOT DO THESE

Do not:

- create fake implementations and call them complete
- leave TODOs for core functionality
- hard-code passwords
- commit API keys
- store money as float
- expose private galleries publicly
- rely solely on client-side validation
- give every staff member admin permissions
- put all logic in views
- use signals for every business workflow
- create hundreds of packages unnecessarily
- duplicate model calculations in templates
- ignore database indexes
- ignore mobile interfaces
- ignore accessibility
- ignore audit logging around financial operations
- suppress failing tests
- disable security controls to make development easier

---

# 85. SAAS FUTURE

Do not implement this immediately unless required, but ensure the architecture can later support:

- Multiple studios
- Subscription plans
- Monthly billing
- Trial periods
- Usage limits
- Multiple studio branches
- Custom branding
- White labeling
- Custom domains
- API access
- Mobile application
- Automated WhatsApp messaging
- Advanced business analytics

Potential future plans:

```text
Starter
Professional
Studio Pro
Enterprise
```

Do not mix future subscription complexity into the initial operational StudioFlow V1.

---

# 86. FIRST RELEASE SCOPE

The first genuinely usable release must contain:

1. Authentication
2. Roles
3. Studio settings
4. Clients
5. Leads
6. Packages
7. Bookings
8. Calendar
9. Projects
10. Project workflow
11. Invoices
12. Partial payments
13. Receipts
14. Expenses
15. Basic dashboard
16. Basic reports
17. Audit logs

After that is stable, implement:

- Gallery
- Client selection
- Client portal
- Printing
- Frames
- Albums
- Inventory
- Equipment
- Paystack
- Advanced notifications

---

# 87. FIRST TASK FOR THE CODING AGENT

Do NOT immediately build every feature in this specification.

Start by doing only the following:

## Step 1

Analyze the entire specification.

## Step 2

Create:

```text
docs/architecture.md
docs/database.md
docs/workflows.md
docs/permissions.md
docs/development-plan.md
```

## Step 3

Design the initial database/domain relationships.

Show the relationship between:

```text
Studio
User
Staff
Client
Lead
Service
Package
PackageAddon
Booking
BookingAddon
Project
ProjectTask
Invoice
InvoiceItem
Payment
Expense
Gallery
Photo
PhotoSelection
PrintJob
FrameOrder
AlbumOrder
InventoryItem
StockTransaction
Equipment
Notification
AuditLog
```

## Step 4

Define which features belong in V1 and which should be postponed.

## Step 5

Initialize the Django project with:

- split settings
- custom User model
- Studio model
- staff roles
- PostgreSQL
- Redis
- Celery
- pytest
- Ruff
- Tailwind
- HTMX
- Alpine.js
- Docker
- GitHub Actions
- `.env.example`

## Step 6

Create a professional authenticated dashboard shell.

Do not implement the entire CRM yet.

## Step 7

Write tests for the foundation.

## Step 8

Run:

```bash
ruff check .
pytest
python manage.py check
python manage.py makemigrations --check --dry-run
```

Fix all issues before stopping.

## Step 9

Provide a final report containing:

- files created
- architecture decisions
- database decisions
- commands to run locally
- test results
- known limitations
- next recommended phase

Then STOP.

Wait for the next development instruction rather than automatically generating all remaining modules.

---

# 88. INSTRUCTIONS FOR FUTURE DEVELOPMENT TURNS

Whenever asked to continue:

First inspect the repository.

Do not assume the previous phase was completed correctly.

Run the existing test suite.

Study existing architecture before making changes.

Preserve working behavior.

Never replace functional code unnecessarily.

For every phase use:

```text
REVIEW
↓
PLAN
↓
IMPLEMENT
↓
TEST
↓
OPTIMIZE
↓
DOCUMENT
↓
REPORT
```

If you discover a bug from an earlier phase, fix it rather than building new code on top of a broken foundation.

---

# FINAL PRODUCT GOAL

The finished StudioFlow product should allow a photography-studio owner to open one dashboard and understand:

- Who is coming to the studio today?
- Which photographer is assigned?
- Which clients still owe money?
- Which jobs are awaiting editing?
- Which clients need to select photographs?
- Which photos need printing?
- Which albums or frames are unfinished?
- Which projects are overdue?
- How much revenue did the studio make?
- How much did the studio spend?
- What approximate profit was made?
- Which stock items are low?
- Which equipment is unavailable?
- Which completed projects are ready for delivery?

The software should eventually replace notebooks, spreadsheets, scattered WhatsApp messages, manual receipts and disconnected studio records with one secure and organized operating system for the photography business.

Build StudioFlow as software that a real photography studio can depend on every day.