from functools import wraps

from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


ROLE_PERMISSIONS = {
    "owner": [
        "dashboard.view", "clients.view", "clients.create", "clients.edit", "clients.delete",
        "leads.view", "leads.create", "leads.edit", "leads.delete",
        "bookings.view", "bookings.create", "bookings.edit", "bookings.delete", "bookings.change_status",
        "projects.view", "projects.create", "projects.edit", "projects.delete",
        "gallery.view", "gallery.upload", "gallery.edit", "gallery.delete",
        "finance.view", "finance.create_invoices", "finance.record_payments", "finance.edit",
        "expenses.view", "expenses.create", "expenses.edit", "expenses.delete",
        "inventory.view", "inventory.create", "inventory.edit", "inventory.adjust",
        "equipment.view", "equipment.create", "equipment.edit",
        "printing.view", "printing.create", "printing.edit",
        "reports.view", "reports.export",
        "audit.view",
        "notifications.view", "notifications.send_sms",
        "settings.view", "settings.edit",
        "payments.view", "payments.create",
        "staff.view", "staff.edit",
    ],
    "manager": [
        "dashboard.view", "clients.view", "clients.create", "clients.edit",
        "leads.view", "leads.create", "leads.edit",
        "bookings.view", "bookings.create", "bookings.edit", "bookings.change_status",
        "projects.view", "projects.create", "projects.edit",
        "gallery.view", "gallery.upload", "gallery.edit",
        "finance.view", "finance.create_invoices", "finance.record_payments",
        "expenses.view", "expenses.create", "expenses.edit",
        "inventory.view", "inventory.create", "inventory.edit",
        "equipment.view", "equipment.edit",
        "printing.view", "printing.create", "printing.edit",
        "reports.view", "reports.export",
        "audit.view",
        "notifications.view", "notifications.send_sms",
        "payments.view", "payments.create",
    ],
    "receptionist": [
        "dashboard.view",
        "clients.view", "clients.create", "clients.edit",
        "leads.view", "leads.create", "leads.edit",
        "bookings.view", "bookings.create", "bookings.edit",
        "gallery.view",
        "finance.view",
        "notifications.view",
    ],
    "photographer": [
        "dashboard.view",
        "clients.view",
        "bookings.view",
        "projects.view", "projects.edit",
        "gallery.view", "gallery.upload", "gallery.edit",
        "equipment.view",
        "printing.view",
        "notifications.view",
    ],
    "photo_editor": [
        "dashboard.view",
        "clients.view",
        "bookings.view",
        "projects.view", "projects.edit",
        "gallery.view", "gallery.edit",
        "printing.view", "printing.edit",
        "inventory.view",
        "notifications.view",
    ],
    "printing_staff": [
        "dashboard.view",
        "clients.view",
        "bookings.view",
        "projects.view",
        "gallery.view",
        "printing.view", "printing.edit",
        "inventory.view", "inventory.edit",
        "equipment.view",
        "notifications.view",
    ],
    "accountant": [
        "dashboard.view",
        "clients.view",
        "bookings.view",
        "finance.view", "finance.create_invoices", "finance.record_payments", "finance.edit",
        "expenses.view", "expenses.create", "expenses.edit",
        "reports.view", "reports.export",
        "audit.view",
        "payments.view", "payments.create",
        "inventory.view",
        "notifications.view",
    ],
}


def get_user_role(user):
    """Get the user's role from their staff profile."""
    profile = getattr(user, "staff_profile", None)
    if profile:
        return profile.role
    if user.is_superuser:
        return "owner"
    return "receptionist"


def has_permission(user, permission):
    """Check if user has a specific permission."""
    role = get_user_role(user)
    perms = ROLE_PERMISSIONS.get(role, [])
    return permission in perms


def permission_required(permission):
    """Decorator to check permission before accessing a view."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if not has_permission(request.user, permission):
                messages.error(request, "You don't have permission to access this page.")
                return redirect("dashboard:index")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
