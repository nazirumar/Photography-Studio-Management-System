from .models import AuditLog


def get_changes_diff(audit_log):
    """Get a formatted diff between before and after values."""
    if not audit_log.before_values or not audit_log.after_values:
        return []

    changes = []
    all_keys = set(audit_log.before_values.keys()) | set(audit_log.after_values.keys())

    for key in sorted(all_keys):
        old_val = audit_log.before_values.get(key)
        new_val = audit_log.after_values.get(key)

        if old_val != new_val:
            changes.append({
                "field": key,
                "old_value": old_val,
                "new_value": new_val,
                "type": _get_change_type(old_val, new_val),
            })

    return changes


def _get_change_type(old_val, new_val):
    """Determine the type of change."""
    if old_val is None and new_val is not None:
        return "added"
    elif old_val is not None and new_val is None:
        return "removed"
    elif old_val != new_val:
        return "changed"
    return "unchanged"


def get_entity_history(entity_type, entity_id, limit=50):
    """Get audit history for a specific entity."""
    return AuditLog.objects.filter(
        entity_type=entity_type,
        entity_id=str(entity_id),
    ).order_by("-timestamp")[:limit]


def get_user_activity(user, days=30):
    """Get user activity for the last N days."""
    from django.utils import timezone
    cutoff = timezone.now() - timezone.timedelta(days=days)
    return AuditLog.objects.filter(
        user=user,
        timestamp__gte=cutoff,
    ).order_by("-timestamp")
