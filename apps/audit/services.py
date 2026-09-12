from django.db.models import Count

from apps.audit.models import AuditLog


def get_audit_logs(entity_type=None, entity_id=None, user=None, action=None, limit=100):
    """Get audit logs with optional filters."""
    qs = AuditLog.objects.select_related("user")
    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if entity_id:
        qs = qs.filter(entity_id=entity_id)
    if user:
        qs = qs.filter(user=user)
    if action:
        qs = qs.filter(action=action)
    return qs[:limit]


def get_entity_history(entity_type, entity_id):
    """Get full history for a specific entity."""
    return AuditLog.objects.filter(
        entity_type=entity_type, entity_id=entity_id
    ).select_related("user").order_by("-timestamp")


def get_recent_activity(studio=None, limit=50):
    """Get recent activity across all entities."""
    qs = AuditLog.objects.select_related("user")
    if studio:
        from apps.accounts.models import StaffProfile
        staff_users = StaffProfile.objects.filter(studio=studio).values_list("user_id", flat=True)
        qs = qs.filter(user_id__in=staff_users)
    return qs[:limit]


def get_user_activity(user, limit=50):
    """Get activity for a specific user."""
    return AuditLog.objects.filter(user=user).select_related("user")[:limit]


def get_action_summary(start_date=None, end_date=None):
    """Get summary of actions by type."""
    qs = AuditLog.objects.all()
    if start_date:
        qs = qs.filter(timestamp__date__gte=start_date)
    if end_date:
        qs = qs.filter(timestamp__date__lte=end_date)

    return list(
        qs.values("action").annotate(count=Count("id")).order_by("-count")
    )


def get_entity_type_summary():
    """Get summary of entities by type."""
    return list(
        AuditLog.objects.values("entity_type").annotate(
            count=Count("id")
        ).order_by("-count")
    )
