import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

from apps.accounts.decorators import role_required


@require_GET
@login_required
@role_required(["owner", "manager"])
def celery_health_check(request):
    """Check Celery worker health and task status."""
    from celery import current_app

    try:
        inspect = current_app.control.inspect()
        active = inspect.active()
        scheduled = inspect.scheduled()
        registered = inspect.registered()

        workers = {}
        if active:
            for worker, tasks in active.items():
                workers[worker] = {
                    "status": "online",
                    "active_tasks": len(tasks),
                    "registered_tasks": len(registered.get(worker, [])) if registered else 0,
                }

        if not workers:
            return JsonResponse({
                "status": "warning",
                "message": "No Celery workers detected",
                "workers": {},
                "timestamp": datetime.now().isoformat(),
            })

        return JsonResponse({
            "status": "healthy",
            "message": f"{len(workers)} worker(s) online",
            "workers": workers,
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "workers": {},
            "timestamp": datetime.now().isoformat(),
        }, status=500)


@require_GET
@login_required
@role_required(["owner", "manager"])
def celery_task_status(request):
    """Get status of recent Celery tasks."""
    from django_celery_beat.models import PeriodicTask

    tasks = PeriodicTask.objects.all().values("name", "task", "enabled", "last_run_at")
    task_list = list(tasks)

    return JsonResponse({
        "tasks": task_list,
        "count": len(task_list),
    })
