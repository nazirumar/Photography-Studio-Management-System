# Key Business Workflows

All status transitions go through service methods. Each transition validates pre-conditions, writes an AuditLog entry, and triggers relevant Notifications. Invalid transitions raise exceptions.

---

## Lead to Client to Booking Conversion

```
Lead (status: new)
  │
  ├─> Contacted (status change)
  ├─> Qualified (status change)
  ├─> Proposal Sent (status change)
  ├─> Won → convert to Client + create Booking
  └─> Lost → archive
```

**Service method:** `convert_lead_to_booking(lead_id, package_id, shoot_date, ...)`

1. Validate lead status is `won` or `proposal_sent`.
2. Create `Client` record from lead data.
3. Link `lead.converted_client = client`.
4. Create `Booking` with `status=enquiry`.
5. Create `AuditLog` entry for conversion.
6. Send notification to assigned staff.

---

## Booking Lifecycle

```
Enquiry → Tentative → Awaiting Deposit → Confirmed → In Progress → Completed
                                                        │
                                                        └→ Cancelled (at any pre-confirmed stage)
```

**Transitions:**

| From | To | Method | Pre-conditions |
|------|----|--------|----------------|
| Enquiry | Tentative | `tentative_booking(booking)` | Client has been contacted |
| Tentative | Awaiting Deposit | `request_deposit(booking)` | Package and date agreed |
| Awaiting Deposit | Confirmed | `confirm_booking(booking)` | Deposit payment received and recorded |
| Confirmed | In Progress | `start_booking(booking)` | Shoot date arrived |
| In Progress | Completed | `complete_booking(booking)` | Shoot finished, all files captured |
| Any pre-confirmed | Cancelled | `cancel_booking(booking, reason)` | Cancellation reason required |

**Service method:** `create_booking(client_id, package_id, shoot_date, addons=[], ...)`

1. Validate client exists and is active.
2. Validate package is active.
3. Snapshot package data into `booking.package_snapshot` (JSON).
4. Copy selected addons into `BookingAddon` with current prices.
5. Calculate `total_amount` from package + addons.
6. Set `deposit_amount` from package default or override.
7. Create booking with initial status.
8. Write AuditLog.
9. Send booking confirmation notification/email.

---

## Project Lifecycle

```
Scheduled → Shoot Completed → Files Imported → Awaiting Client Selection
  → Selection Received → Editing → Editing Review → Ready For Print
  → Printing → Quality Control → Ready For Delivery → Delivered → Completed
```

**Transitions:**

| From | To | Method | Trigger |
|------|----|--------|---------|
| (auto) | Scheduled | `create_project_from_booking(booking)` | When booking confirmed |
| Scheduled | Shoot Completed | `complete_shoot(project)` | Photographer marks shoot done |
| Shoot Completed | Files Imported | `import_files(project, photo_paths[]))` | Staff uploads raw files |
| Files Imported | Awaiting Selection | `create_proof_gallery(project)` | Proof gallery published to client |
| Awaiting Selection | Selection Received | `finalize_selection(project)` | Client submits selections |
| Selection Received | Editing | `start_editing(project)` | Editor picks up project |
| Editing | Editing Review | `submit_editing(project)` | Editor completes edits |
| Editing Review | Ready For Print | `approve_editing(project)` | Manager reviews and approves |
| Ready For Print | Printing | `start_printing(project)` | Print jobs initiated |
| Printing | Quality Control | `start_qc(project)` | Printing finished |
| Quality Control | Ready For Delivery | `pass_qc(project)` | QC passed |
| Ready For Delivery | Delivered | `deliver_project(project)` | Delivered to client |
| Delivered | Completed | `complete_project(project)` | Client confirms receipt |

Each transition:
- Validates current status.
- Updates `project.status` and `updated_at`.
- Writes AuditLog with `status_change` action.
- Sends notification to relevant staff (e.g., editor notified when selection received).

---

## Invoice Lifecycle

```
Draft → Issued → Partially Paid → Paid
                     │
                     ├→ Overdue (if past due_date)
                     └→ Cancelled
```

**Transitions:**

| From | To | Method | Pre-conditions |
|------|----|--------|----------------|
| (auto) | Draft | `create_invoice(client, items[])` | Items provided |
| Draft | Issued | `issue_invoice(invoice)` | All items valid, totals calculated |
| Issued / Partially Paid | Partially Paid | `record_payment(invoice, amount)` | Payment amount > 0, balance > 0 |
| Partially Paid / Issued | Paid | `record_payment(invoice, amount)` | Payment covers full balance |
| Issued / Partially Paid | Overdue | `mark_overdue(invoice)` | Called by Celery Beat daily check |
| Draft | Cancelled | `cancel_invoice(invoice, reason)` | Reason required, no payments recorded |

**Service method:** `create_invoice_for_booking(booking_id)`

1. Build invoice items from `booking.package_snapshot`.
2. Add any addon items.
3. Calculate subtotal, tax, discount, total.
4. Set due_date based on booking terms.
5. Create Invoice + InvoiceItems.
6. Link to booking and client.
7. Write AuditLog.

---

## Payment Recording

```
Payment submitted → Validate amount → Record Payment → Update Invoice Status → AuditLog → Receipt
```

**Service method:** `record_payment(invoice_id, amount, method, reference, recorded_by)`

1. Validate invoice is not cancelled.
2. Validate amount > 0.
3. Validate amount <= outstanding balance (overpayment handled separately).
4. Create Payment record linking to invoice and client.
5. Calculate new `amount_paid` on invoice.
6. Update invoice status:
   - If `amount_paid >= total` → `paid`
   - If `amount_paid > 0` → `partially_paid`
7. Write AuditLog with `payment` action (amount, method, reference).
8. Send payment confirmation notification.
9. Generate receipt (PDF on demand).

**Overpayment:** If amount > balance, raise validation error. Partial overpayment must be explicitly approved by Manager/Owner.

---

## Photo Selection Workflow

```
Editor uploads proofs → Create proof gallery → Client accesses private gallery
  → Client selects photos → Finalize selection → Editor receives selection queue
```

**Steps:**

1. **Upload proofs:** Staff uploads high-res photos to project gallery via `upload_proofs(project, files[])`.
   - Celery task generates thumbnails.
   - Each Photo gets a UUID for direct URL access.

2. **Publish gallery:** `create_proof_gallery(project)` sets gallery `is_public=True` and generates a unique shareable link.

3. **Client selects:** Client visits gallery URL, authenticates (or uses token link), toggles photos. Each selection saved via `select_photo(photo_id, client_id, selected=True/False)`.
   - Tracks `extra_charge` if selection exceeds package allowance.

4. **Finalize:** `finalize_selection(project)` locks the selection, notifies editor with a selection queue.

5. **Editor receives:** `get_selection_queue(project)` returns ordered list of selected photos for editing workflow.

---

## Print Job Lifecycle

```
Pending → Preparing → Printing → Quality Check → Ready → Delivered
```

**Transitions:**

| From | To | Method |
|------|----|--------|
| (auto) | Pending | `create_print_jobs(project, specs[])` |
| Pending | Preparing | `start_print_preparation(print_job)` |
| Preparing | Printing | `start_printing(print_job)` |
| Printing | Quality Check | `finish_printing(print_job)` |
| Quality Check | Ready | `pass_print_qc(print_job)` |
| Ready | Delivered | `deliver_print(print_job)` |

**Service method:** `create_print_jobs(project, specs[])`

1. Validate project status allows printing.
2. For each spec (photo, paper_type, size, quantity):
   - Validate paper_type and size exist in system configuration.
   - Create PrintJob with `pending` status.
   - Deduct inventory items (paper stock) via `stock_out()`.
3. Write AuditLog for each job.

---

## Inventory Management

All stock changes require a `StockTransaction` record. Direct quantity overwrites are forbidden.

### Stock In (Receiving)

**Service method:** `stock_in(item_id, quantity, reference, notes, recorded_by)`

1. Validate item exists and quantity > 0.
2. Create `StockTransaction(type='in', quantity=+N)`.
3. Update `item.quantity += quantity`.
4. Write AuditLog.

### Stock Out (Usage)

**Service method:** `stock_out(item_id, quantity, reference, notes, recorded_by)`

1. Validate `item.quantity >= quantity`.
2. Create `StockTransaction(type='out', quantity=-N)`.
3. Update `item.quantity -= quantity`.
4. If `item.quantity <= item.reorder_level`, trigger low-stock notification.
5. Write AuditLog.

### Adjustment

**Service method:** `adjust_stock(item_id, new_quantity, reason, recorded_by)`

1. Calculate delta: `delta = new_quantity - item.quantity`.
2. Create `StockTransaction(type='adjustment', quantity=delta)`.
3. Update `item.quantity = new_quantity`.
4. Write AuditLog with reason.

### Damaged / Returned

**Service method:** `record_damaged(item_id, quantity, notes, recorded_by)` / `record_returned(item_id, quantity, notes, recorded_by)`

Same pattern as stock_out but with distinct `transaction_type` for reporting.

---

## Notification Rules

| Event | Recipients | Channel |
|-------|-----------|---------|
| Booking confirmed | Client, assigned staff | Email + in-app |
| Deposit received | Owner, accountant | In-app |
| Shoot completed | Manager, editor | In-app |
| Selection received | Editor | In-app + email |
| Editing approved | Printing staff | In-app |
| Invoice issued | Client | Email + in-app |
| Payment received | Client, accountant | Email + in-app |
| Low stock alert | Manager, printing staff | In-app + email |
| Print job ready | Manager | In-app |
| Project delivered | Client | Email + in-app |
| Overdue invoice | Client, accountant | Email + in-app |
