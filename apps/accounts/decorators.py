from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from apps.accounts.models import Role


def owner_or_manager_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if hasattr(request.user, "staff_profile") and request.user.staff_profile.role in (Role.OWNER, Role.MANAGER):
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access this page.")
        return redirect("dashboard:index")
    return wrapper


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if hasattr(request.user, "staff_profile") and request.user.staff_profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access this page.")
            return redirect("dashboard:index")
        return wrapper
    return decorator
