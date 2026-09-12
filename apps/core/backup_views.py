from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.core.backup_service import create_backup, list_backups, restore_backup


@login_required
def backup_list(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    backups = list_backups()
    return render(request, "core/backups.html", {"backups": backups})


@login_required
def backup_create(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    if request.method == "POST":
        result = create_backup()
        if result["success"]:
            messages.success(request, f"Backup created: {result['filename']}")
        else:
            messages.error(request, f"Backup failed: {result['error']}")
    return redirect("core_backup:list")


@login_required
def backup_restore(request, filename):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect("dashboard:index")
    if request.method == "POST":
        import os
        from django.conf import settings
        filepath = os.path.join(settings.BASE_DIR, "backups", filename)
        if os.path.exists(filepath):
            result = restore_backup(filepath)
            if result["success"]:
                messages.success(request, "Backup restored successfully.")
            else:
                messages.error(request, f"Restore failed: {result['error']}")
        else:
            messages.error(request, "Backup file not found.")
    return redirect("core_backup:list")
