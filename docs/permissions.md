# Role-Based Permissions

## Roles

| Role | Description |
|------|-------------|
| `owner` | Studio owner. Full access to everything, including staff management and settings. |
| `manager` | Studio manager. Broad operational access, limited admin/settings. |
| `receptionist` | Front-desk staff. CRM and booking management focus. |
| `photographer` | Shoots and field work. Limited to assigned projects. |
| `photo_editor` | Post-production. Limited to assigned projects. |
| `printing_staff` | Print lab and fulfilment. Print jobs, frames, albums, inventory. |
| `accountant` | Finance focus. Invoices, payments, expenses, reports. |

## Permission Enforcement

Permissions are enforced at three levels:

1. **Service layer:** Methods check user role before executing business logic.
2. **View layer:** Mixins and decorators restrict access to views.
3. **Template layer:** UI elements hidden/shown based on permissions (supplementary only, never sole enforcement).

Custom decorators and mixins:
- `@require_role(Role.OWNER)` — view-level role check.
- `@require_studio_permission(perm_string)` — fine-grained permission check.
- `StudioRequiredMixin` — verifies user belongs to the current studio.
- `OwnershipRequiredMixin` — verifies user owns or is assigned to the entity.

---

## Permissions Matrix

### CRM (Clients, Leads, Tags, Notes)

| Action | Owner | Manager | Receptionist | Photographer | PhotoEditor | PrintingStaff | Accountant |
|--------|-------|---------|--------------|--------------|-------------|---------------|------------|
| View clients | Full | Full | Full | Read | Read | Read | Read |
| Create client | Yes | Yes | Yes | No | No | No | No |
| Edit client | Full | Full | Own studio | No | No | No | No |
| Delete client | Yes | No | No | No | No | No | No |
| Assign account manager | Yes | Yes | No | No | No | No | No |
| View leads | Full | Full | Full | Read | Read | Read | Read |
| Create lead | Yes | Yes | Yes | No | No | No | No |
| Edit lead status | Yes | Yes | Yes | No | No | No | No |
| Convert lead | Yes | Yes | Yes | No | No | No | No |
| Manage tags | Yes | Yes | Yes | No | No | No | No |

### Studio (Bookings, Projects, Calendar)

| Action | Owner | Manager | Receptionist | Photographer | PhotoEditor | PrintingStaff | Accountant |
|--------|-------|---------|--------------|--------------|-------------|---------------|------------|
| View all bookings | Full | Full | Full | Assigned | Assigned | No | Read |
| Create booking | Yes | Yes | Yes | No | No | No | No |
| Edit booking | Full | Full | Yes | Assigned | No | No | No |
| Cancel booking | Yes | Yes | No | No | No | No | No |
| Assign staff to booking | Yes | Yes | No | No | No | No | No |
| View all projects | Full | Full | Read | Assigned | Assigned | Assigned | Read |
| Edit project status | Full | Full | No | Assigned | Assigned | No | No |
| View calendar | Full | Full | Full | Assigned | Assigned | No | Read |
| Manage project tasks | Full | Full | No | Assigned | Assigned | No | No |

### Production (Printing, Frames, Albums)

| Action | Owner | Manager | Receptionist | Photographer | PhotoEditor | PrintingStaff | Accountant |
|--------|-------|---------|--------------|--------------|-------------|---------------|------------|
| View print jobs | Full | Full | Read | No | No | Full | Read |
| Create print jobs | Yes | Yes | No | No | No | Yes | No |
| Edit print job status | Yes | Yes | No | No | No | Yes | No |
| View frame orders | Full | Full | Read | No | No | Full | Read |
| Create frame orders | Yes | Yes | No | No | No | Yes | No |
| View album orders | Full | Full | Read | No | No | Full | Read |
| Create album orders | Yes | Yes | No | No | No | Yes | No |

### Finance (Invoices, Payments, Expenses)

| Action | Owner | Manager | Receptionist | Photographer | PhotoEditor | PrintingStaff | Accountant |
|--------|-------|---------|--------------|--------------|-------------|---------------|------------|
| View invoices | Full | Read | No | No | No | No | Full |
| Create invoice | Yes | No | No | No | No | No | Yes |
| Edit invoice | Yes | No | No | No | No | No | Yes |
| Issue invoice | Yes | No | No | No | No | No | Yes |
| Cancel invoice | Yes | No | No | No | No | No | No |
| Record payment | Yes | No | No | No | No | No | Yes |
| View payments | Full | Read | No | No | No | No | Full |
| View expenses | Full | Read | No | No | No | No | Full |
| Create expense | Yes | Yes | No | No | No | No | Yes |
| Delete expense | Yes | No | No | No | No | No | No |

### Resources (Inventory, Equipment)

| Action | Owner | Manager | Receptionist | Photographer | PhotoEditor | PrintingStaff | Accountant |
|--------|-------|---------|--------------|--------------|-------------|---------------|------------|
| View inventory | Full | Full | No | No | No | Read | Read |
| Create inventory item | Yes | Yes | No | No | No | Yes | No |
| Edit inventory item | Yes | Yes | No | No | No | Yes | No |
| Stock in/out | Yes | Yes | No | No | No | Yes | No |
| View equipment | Full | Full | No | Read | No | Read | Read |
| Create equipment | Yes | Yes | No | No | No | No | No |
| Edit equipment | Yes | Yes | No | No | No | No | No |
| Reserve equipment | Yes | Yes | No | Yes | No | No | No |

### Reports

| Action | Owner | Manager | Receptionist | Photographer | PhotoEditor | PrintingStaff | Accountant |
|--------|-------|---------|--------------|--------------|-------------|---------------|------------|
| View dashboard | Full | Full | Read | Read | Read | Read | Read |
| View revenue reports | Full | Read | No | No | No | No | Read |
| View project reports | Full | Read | No | Read | Read | Read | Read |
| Export CSV | Yes | Yes | No | No | No | No | Yes |
| View profit reports | Full | No | No | No | No | No | No |
| View pipeline | Full | Full | No | No | No | No | No |

### Staff & Settings (Owner Only)

| Action | Owner | Manager | All Others |
|--------|-------|---------|------------|
| View staff list | Yes | No | No |
| Create staff account | Yes | No | No |
| Edit staff role | Yes | No | No |
| Deactivate staff | Yes | No | No |
| Edit studio settings | Yes | No | No |
| Manage service categories | Yes | No | No |
| Manage packages | Yes | No | No |
| View audit log | Yes | No | No |
| Manage notifications config | Yes | No | No |

---

## Implementation

### Custom Decorators

```python
from functools import wraps
from django.core.exceptions import PermissionDenied

def require_role(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            staff_profile = getattr(request.user, 'staff_profile', None)
            if not staff_profile or staff_profile.role not in roles:
                raise PermissionDenied("Insufficient permissions.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Studio Mixin

```python
class StudioRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'staff_profile'):
            raise PermissionDenied("No studio profile.")
        self.studio = request.user.staff_profile.studio
        return super().dispatch(request, *args, **kwargs)
```

### Queryset Scoping

Default managers filter by studio:

```python
class ClientManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(studio=self.model._meta.default_manager.studio)
```

In views, queryset is always filtered by the request user's studio. Staff-level filtering (e.g., photographer sees only assigned projects) is applied at the view/queryset level.

### Template Checks

```django
{% if user.staff_profile.role == "owner" or user.staff_profile.role == "manager" %}
  <button hx-get="{% url 'edit-booking' booking.pk %}">Edit</button>
{% endif %}
```

This is supplementary. Server-side enforcement is always present.
