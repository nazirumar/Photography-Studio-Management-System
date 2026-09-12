# Performance Optimization Guide

## Database Indexes

For production PostgreSQL, add these indexes:

```sql
-- Booking performance
CREATE INDEX idx_booking_studio_date ON bookings_booking (studio_id, date);
CREATE INDEX idx_booking_studio_status ON bookings_booking (studio_id, status);
CREATE INDEX idx_booking_client_date ON bookings_booking (client_id, date);

-- Invoice performance
CREATE INDEX idx_invoice_studio_status ON finance_invoice (studio_id, status);
CREATE INDEX idx_invoice_studio_date ON finance_invoice (studio_id, issue_date);

-- Payment performance
CREATE INDEX idx_payment_studio_date ON finance_payment (studio_id, payment_date);
CREATE INDEX idx_payment_invoice_studio ON finance_payment (invoice_id, studio_id);

-- Audit log performance
CREATE INDEX idx_audit_entity ON audit_auditlog (entity_type, entity_id);
CREATE INDEX idx_audit_user_time ON audit_auditlog (user_id, timestamp);
CREATE INDEX idx_audit_action_time ON audit_auditlog (action, timestamp);

-- Project performance
CREATE INDEX idx_project_studio_status ON projects_project (studio_id, status);

-- Photo performance
CREATE INDEX idx_photo_gallery_selected ON gallery_photo (gallery_id, is_selected);

-- Lead performance
CREATE INDEX idx_lead_studio_status ON leads_lead (studio_id, status);
```

## Caching Strategy

| View | Cache Duration | Cache Key |
|------|---------------|-----------|
| Dashboard stats | 5 min | `dashboard:stats:{studio_id}` |
| Revenue report | 15 min | `reports:revenue:{studio_id}:{date_range}` |
| Package list | 1 hour | `packages:list:{studio_id}` |
| Client list | 5 min | `clients:list:{studio_id}` |
| Static assets | 30 days | WhiteNoise handles this |

## Query Optimization Rules

1. **Always use `select_related()`** for ForeignKey lookups in list views
2. **Use `prefetch_related()`** for reverse ForeignKey and ManyToMany
3. **Use `only()`** when not all fields are needed
4. **Use `values()` / `values_list()`** for data-only queries (reports, aggregates)
5. **Avoid N+1 queries** - use `Prefetch` objects for complex prefetches
6. **Use `exists()`** instead of `count() > 0` for existence checks
7. **Use `update()` / `delete()`** queryset methods for bulk operations

## Performance Monitoring

Enable Django debug toolbar in development:
```bash
pip install django-debug-toolbar
```

Check query count in views:
```python
from django.db import connection
print(len(connection.queries))
```
