from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.audit.models import AuditLog
from apps.audit.services import get_audit_logs, get_entity_history


@login_required
def audit_log_list(request):
    entity_type = request.GET.get("entity_type")
    action = request.GET.get("action")
    logs = get_audit_logs(entity_type=entity_type, action=action, limit=200)
    return render(request, "audit/list.html", {"logs": logs})


@login_required
def audit_entity_history(request, entity_type, entity_id):
    logs = get_entity_history(entity_type, entity_id)
    return render(request, "audit/entity_history.html", {
        "logs": logs,
        "entity_type": entity_type,
        "entity_id": entity_id,
    })


@login_required
def audit_detail(request, pk):
    log = get_object_or_404(AuditLog.objects.select_related("user"), pk=pk)
    return render(request, "audit/detail.html", {"log": log})
