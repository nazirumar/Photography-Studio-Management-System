from apps.audit.models import AuditLog


def create_audit_log(user, action, entity_type, entity_id, before_values=None, after_values=None, ip_address=None):
    return AuditLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        before_values=before_values,
        after_values=after_values,
        ip_address=ip_address,
    )


def get_user_studio(user):
    if hasattr(user, "staff_profile"):
        return user.staff_profile.studio
    return user.studio


def user_has_role(user, *role_choices):
    if not hasattr(user, "staff_profile"):
        return False
    return user.staff_profile.role in role_choices


def is_owner_or_manager(user):
    from apps.accounts.models import Role
    return user_has_role(user, Role.OWNER, Role.MANAGER)
