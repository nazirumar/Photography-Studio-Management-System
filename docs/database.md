# Database Design & Entity Relationships

## Conventions

- **Primary keys:** UUIDs (`uuid.uuid4`) for all externally-exposed entities. Internal joins use Django's auto-generated `BigAutoField` PKs.
- **Money fields:** `DecimalField(max_digits=14, decimal_places=2)` everywhere. Never `FloatField`.
- **Timestamps:** `created_at`, `updated_at` on every model. Timezone-aware (`DateTimeField(auto_now_add=True)` / `auto_now=True`).
- **Soft deletes:** Not used. Hard deletes with audit trail (AuditLog records deletions).
- **Studio scoping:** Every business entity has a `studio` FK. Queries always filter by studio.
- **Unique constraints:** Scoped to `studio` where applicable (e.g., `unique_together = [("studio", "email")]`).
- **Indexes:** On all `studio` FK fields, status fields, date fields used for filtering/sorting, and any frequently-queried text fields.

## Entity Relationship Diagram (Simplified)

```
Studio ─┬─> User ──── StaffProfile
         ├─> Client ──── Tag (M2M)
         ├─> Lead
         ├─> ServiceCategory ──> Package ──> PackageAddon
         ├─> Booking ──> BookingAddon
         │     ├─> BookingStaff (M2M: User)
         │     └─> PackageSnapshot (JSON field)
         ├─> Project ──> ProjectTask
         │     ├─> Gallery ──> Photo ──> PhotoSelection
         │     ├─> PrintJob
         │     ├─> FrameOrder
         │     └─> AlbumOrder
         ├─> Invoice ──> InvoiceItem
         │     └─> Payment
         ├─> Expense
         ├─> InventoryItem ──> StockTransaction
         ├─> Equipment
         ├─> Notification
         └─> AuditLog
```

## Model Details

### Studio

Root tenant. All data scoped here.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| name | CharField(200) | |
| slug | SlugField(200) | unique |
| email | EmailField | |
| phone | CharField(20) | |
| address | TextField | |
| logo | ImageField | |
| timezone | CharField(50) | default `Africa/Lagos` |
| currency | CharField(3) | default `NGN`, future-proof |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### User (Custom)

Replaces Django's default User. Email-based authentication.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| email | EmailField | unique, used for login |
| first_name | CharField(150) | |
| last_name | CharField(150) | |
| phone | CharField(20) | |
| is_active | BooleanField | |
| is_staff | BooleanField | Django admin access |
| is_superuser | BooleanField | |
| role | CharField(20) | choices: owner, manager, receptionist, photographer, photo_editor, printing_staff, accountant |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### StaffProfile

Extended info linking a User to a Studio.

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| user | OneToOneField(User) | |
| studio | ForeignKey(Studio) | |
| job_title | CharField(100) | |
| bio | TextField | |
| avatar | ImageField | |
| is_active | BooleanField | |

### Client

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| first_name | CharField(150) | |
| last_name | CharField(150) | |
| email | EmailField | |
| phone | CharField(20) | |
| address | TextField | |
| account_manager | ForeignKey(User) | optional, assigned staff |
| tags | ManyToManyField(Tag) | |
| notes | TextField | |
| source | CharField(50) | how they found the studio |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

Unique: `(studio, email)`.

### Lead

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| first_name | CharField(150) | |
| last_name | CharField(150) | |
| email | EmailField | |
| phone | CharField(20) | |
| source | CharField(50) | |
| status | CharField(20) | new, contacted, qualified, proposal_sent, won, lost |
| notes | TextField | |
| converted_client | OneToOneField(Client) | set when lead converts |
| assigned_to | ForeignKey(User) | |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### ServiceCategory

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| studio | ForeignKey(Studio) | |
| name | CharField(200) | |
| description | TextField | |
| sort_order | IntegerField | |

### Package

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| category | ForeignKey(ServiceCategory) | |
| name | CharField(200) | |
| description | TextField | |
| price | DecimalField(14,2) | base price |
| is_active | BooleanField | |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### PackageAddon

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| package | ForeignKey(Package) | |
| name | CharField(200) | |
| price | DecimalField(14,2) | |

### Booking

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| client | ForeignKey(Client) | |
| package | ForeignKey(Package) | |
| package_snapshot | JSONField | frozen copy of package + addons at booking time |
| status | CharField(20) | enquiry, tentative, awaiting_deposit, confirmed, in_progress, completed, cancelled |
| shoot_date | DateField | |
| shoot_time | TimeField | |
| venue | CharField(300) | |
| notes | TextField | |
| total_amount | DecimalField(14,2) | sum of package + selected addons |
| deposit_amount | DecimalField(14,2) | required deposit |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### BookingAddon

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| booking | ForeignKey(Booking) | |
| addon | ForeignKey(PackageAddon) | |
| price | DecimalField(14,2) | snapshotted at booking time |

### BookingStaff (M2M)

| Field | Type | Notes |
|-------|------|-------|
| booking | ForeignKey(Booking) | |
| user | ForeignKey(User) | photographer/editor assigned |
| role | CharField(50) | photographer, assistant, editor, etc. |

### Project

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| booking | OneToOneField(Booking) | |
| status | CharField(30) | scheduled → shoot_completed → files_imported → awaiting_selection → selection_received → editing → editing_review → ready_for_print → printing → quality_control → ready_for_delivery → delivered → completed |
| deadline | DateField | |
| notes | TextField | |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### ProjectTask

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| project | ForeignKey(Project) | |
| title | CharField(200) | |
| assigned_to | ForeignKey(User) | |
| status | CharField(20) | pending, in_progress, completed |
| due_date | DateField | |

### Gallery

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | OneToOneField(Project) | |
| title | CharField(200) | |
| is_public | BooleanField | client-facing proof gallery |
| created_at | DateTimeField | |

### Photo

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| gallery | ForeignKey(Gallery) | |
| image | ImageField | original high-res |
| thumbnail | ImageField | generated by Celery task |
| filename | CharField(255) | |
| file_size | BigIntegerField | bytes |
| sort_order | IntegerField | |
| created_at | DateTimeField | |

### PhotoSelection

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| photo | ForeignKey(Photo) | |
| client | ForeignKey(Client) | |
| selected | BooleanField | |
| extra_charge | DecimalField(14,2) | if exceeds included count |
| notes | TextField | client notes on photo |
| created_at | DateTimeField | |

### Invoice

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| client | ForeignKey(Client) | |
| booking | ForeignKey(Booking) | nullable, for booking-linked invoices |
| project | ForeignKey(Project) | nullable, for project-linked invoices |
| status | CharField(20) | draft, issued, partially_paid, paid, overdue, cancelled |
| invoice_number | CharField(50) | auto-generated, unique per studio |
| subtotal | DecimalField(14,2) | |
| discount | DecimalField(14,2) | |
| tax | DecimalField(14,2) | |
| total | DecimalField(14,2) | |
| due_date | DateField | |
| notes | TextField | |
| created_at | DateTimeField | |
| issued_at | DateTimeField | |
| paid_at | DateTimeField | |

### InvoiceItem

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| invoice | ForeignKey(Invoice) | |
| description | CharField(300) | |
| quantity | PositiveIntegerField | |
| unit_price | DecimalField(14,2) | |
| total | DecimalField(14,2) | |

### Payment

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| invoice | ForeignKey(Invoice) | |
| client | ForeignKey(Client) | |
| amount | DecimalField(14,2) | |
| method | CharField(20) | cash, bank_transfer, card, online |
| reference | CharField(100) | transaction reference |
| recorded_by | ForeignKey(User) | |
| notes | TextField | |
| created_at | DateTimeField | |

### Expense

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| project | ForeignKey(Project) | nullable |
| category | CharField(100) | transport, props, rental, etc. |
| description | TextField | |
| amount | DecimalField(14,2) | |
| date | DateField | |
| receipt | FileField | |
| recorded_by | ForeignKey(User) | |
| created_at | DateTimeField | |

### InventoryItem

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| name | CharField(200) | |
| description | TextField | |
| sku | CharField(50) | unique per studio |
| quantity | IntegerField | current stock |
| unit | CharField(20) | rolls, sheets, frames, etc. |
| reorder_level | IntegerField | |
| unit_cost | DecimalField(14,2) | |
| created_at | DateTimeField | |
| updated_at | DateTimeField | |

### StockTransaction

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| item | ForeignKey(InventoryItem) | |
| transaction_type | CharField(20) | in, out, adjustment, damaged, returned |
| quantity | IntegerField | positive for in, negative for out |
| reference | CharField(100) | project, booking, or reason |
| notes | TextField | |
| recorded_by | ForeignKey(User) | |
| created_at | DateTimeField | |

### Equipment

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| studio | ForeignKey(Studio) | |
| name | CharField(200) | |
| description | TextField | |
| serial_number | CharField(100) | |
| status | CharField(20) | available, in_use, maintenance, retired |
| last_maintenance | DateField | |
| created_at | DateTimeField | |

### PrintJob

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | ForeignKey(Project) | |
| photo | ForeignKey(Photo) | |
| paper_type | CharField(100) | configurable, not hardcoded |
| size | CharField(50) | configurable |
| quantity | PositiveIntegerField | |
| status | CharField(20) | pending, preparing, printing, quality_check, ready, delivered |
| notes | TextField | |
| created_at | DateTimeField | |
| completed_at | DateTimeField | |

### FrameOrder

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | ForeignKey(Project) | |
| frame_type | CharField(100) | configurable |
| size | CharField(50) | configurable |
| quantity | PositiveIntegerField | |
| status | CharField(20) | pending, ordered, received, ready, delivered |
| notes | TextField | |
| created_at | DateTimeField | |
| completed_at | DateTimeField | |

### AlbumOrder

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | ForeignKey(Project) | |
| album_type | CharField(100) | configurable |
| size | CharField(50) | configurable |
| page_count | PositiveIntegerField | |
| quantity | PositiveIntegerField | |
| status | CharField(20) | pending, designing, printing, binding, quality_check, ready, delivered |
| notes | TextField | |
| created_at | DateTimeField | |
| completed_at | DateTimeField | |

### Notification

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| user | ForeignKey(User) | |
| title | CharField(200) | |
| message | TextField | |
| is_read | BooleanField | |
| link | URLField | optional deep link |
| created_at | DateTimeField | |

### AuditLog

| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | PK |
| studio | ForeignKey(Studio) | |
| user | ForeignKey(User) | |
| action | CharField(50) | create, update, delete, status_change, payment, login, etc. |
| entity_type | CharField(100) | e.g., "Booking", "Invoice" |
| entity_id | CharField(100) | UUID or PK of the entity |
| changes | JSONField | before/after diff |
| ip_address | GenericIPAddressField | |
| user_agent | TextField | |
| created_at | DateTimeField | |
