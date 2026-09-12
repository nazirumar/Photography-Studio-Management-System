from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.projects.models import Project, ProjectTask


def generate_next_project_reference(studio):
    """Generate next project reference for a studio."""
    last = Project.objects.filter(studio=studio).order_by("-created_at").first()
    if last and last.reference:
        try:
            num = int(last.reference.split("-")[-1]) + 1
        except (ValueError, IndexError):
            num = 1
    else:
        num = 1
    return f"PRJ-{num:04d}"


def create_project(studio, data, user):
    """Create a new project."""
    with transaction.atomic():
        reference = data.pop("reference", None) or generate_next_project_reference(studio)
        project = Project.objects.create(
            studio=studio, reference=reference, **data
        )
        AuditLog.objects.create(
            user=user,
            action="project_created",
            entity_type="Project",
            entity_id=str(project.id),
            after_values={
                "reference": reference,
                "client": str(project.client),
            },
        )
        return project


def update_project(project, data, user):
    """Update a project."""
    with transaction.atomic():
        before = {"status": project.status, "priority": project.priority}
        for key, value in data.items():
            setattr(project, key, value)
        project.save()
        AuditLog.objects.create(
            user=user,
            action="project_updated",
            entity_type="Project",
            entity_id=str(project.id),
            before_values=before,
            after_values={"status": project.status, "priority": project.priority},
        )
        return project


def update_project_status(project, new_status, user):
    """Update project status with audit."""
    with transaction.atomic():
        old_status = project.status
        project.status = new_status
        if new_status == Project.Status.DELIVERED:
            project.actual_delivery = timezone.now().date()
        project.save(update_fields=["status", "actual_delivery", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="project_status_changed",
            entity_type="Project",
            entity_id=str(project.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return project


def create_task(project, data, user):
    """Create a task for a project."""
    with transaction.atomic():
        task = ProjectTask.objects.create(project=project, **data)
        AuditLog.objects.create(
            user=user,
            action="task_created",
            entity_type="ProjectTask",
            entity_id=str(task.id),
            after_values={"title": task.title, "project": project.reference},
        )
        return task


def update_task_status(task, new_status, user):
    """Update task status."""
    with transaction.atomic():
        old_status = task.status
        task.status = new_status
        if new_status == ProjectTask.Status.DONE:
            task.completed_date = timezone.now()
        task.save(update_fields=["status", "completed_date", "updated_at"])
        AuditLog.objects.create(
            user=user,
            action="task_status_changed",
            entity_type="ProjectTask",
            entity_id=str(task.id),
            before_values={"status": old_status},
            after_values={"status": new_status},
        )
        return task
