import os
import subprocess
from datetime import datetime

from django.conf import settings
from django.core.management import call_command


def create_backup():
    """Create a database backup."""
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{timestamp}.json"
    filepath = os.path.join(backup_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            call_command("dumpdata", "--indent", "2", stdout=f, verbosity=0)
        return {"success": True, "filename": filename, "filepath": filepath}
    except Exception as e:
        return {"success": False, "error": str(e)}


def restore_backup(filepath):
    """Restore a database from backup."""
    try:
        call_command("loaddata", filepath, verbosity=0)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_backups():
    """List all available backups."""
    backup_dir = os.path.join(settings.BASE_DIR, "backups")
    if not os.path.exists(backup_dir):
        return []
    backups = []
    for f in sorted(os.listdir(backup_dir), reverse=True):
        if f.startswith("backup_") and f.endswith(".json"):
            filepath = os.path.join(backup_dir, f)
            size = os.path.getsize(filepath)
            backups.append({
                "filename": f,
                "filepath": filepath,
                "size": f"{size / 1024:.1f} KB",
                "created": datetime.fromtimestamp(os.path.getctime(filepath)),
            })
    return backups
