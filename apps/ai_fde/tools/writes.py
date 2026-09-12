from __future__ import annotations

import logging
from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.notifications.models import Notification
from apps.projects.models import Project, ProjectTask

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)

User = get_user_model()


def _serialize_task(task: ProjectTask) -> dict[str, Any]:
    return {
        "id": str(task.id),
        "project_id": str(task.project_id),
        "title": task.title,
        "description": task.description,
        "assigned_to_id": str(task.assigned_to_id) if task.assigned_to_id else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "status": task.status,
        "completed_date": task.completed_date.isoformat() if task.completed_date else None,
        "notes": task.notes,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }


def _serialize_notification(notification: Notification) -> dict[str, Any]:
    return {
        "id": str(notification.id),
        "notification_type": notification.notification_type,
        "title": notification.title,
        "message": notification.message,
        "user_id": str(notification.user_id),
        "is_read": notification.is_read,
        "entity_type": notification.entity_type,
        "entity_id": notification.entity_id,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, TypeError):
        return None


def _validate_priority(value: str) -> str | None:
    value = value.strip().lower()
    valid = [choice[0] for choice in Project.Priority.choices]
    if value in valid:
        return value
    return None


@fde_tool(
    name="create_project_task",
    permission="projects.add_projecttask",
    risk="low_risk_write",
    description="Create a task for a project. Requires confirmation.",
    timeout=30,
)
def create_project_task(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    """Create a task for a project."""
    try:
        project_id = params.get("project_id", "").strip()
        title = params.get("title", "").strip()

        if not project_id:
            return {"success": False, "error": "project_id is required."}
        if not title:
            return {"success": False, "error": "title is required."}

        try:
            project = Project.objects.get(id=project_id, studio=context.studio)
        except Project.DoesNotExist:
            return {"success": False, "error": "Project not found."}

        due_date = _parse_date(params.get("due_date"))
        priority = params.get("priority", "medium")
        validated_priority = _validate_priority(priority)
        if validated_priority is None:
            return {
                "success": False,
                "error": f"Invalid priority '{priority}'. Valid options: low, medium, high, urgent.",
            }

        assigned_to = None
        assigned_to_id = params.get("assigned_to")
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(pk=assigned_to_id, studio=context.studio)
            except (User.DoesNotExist, ValueError):
                return {"success": False, "error": "Assigned user not found in this studio."}

        task = ProjectTask.objects.create(
            project=project,
            title=title,
            description=params.get("description", ""),
            assigned_to=assigned_to,
            due_date=due_date,
            priority=validated_priority,
        )

        return {
            "success": True,
            "message": f"Task '{task.title}' created for project {project.reference}.",
            "task": _serialize_task(task),
        }

    except Exception as exc:
        logger.exception("Error creating project task")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="add_project_note",
    permission="projects.change_project",
    risk="low_risk_write",
    description="Add a note to a project. Requires confirmation.",
    timeout=30,
)
def add_project_note(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    """Add internal notes to a project."""
    try:
        project_id = params.get("project_id", "").strip()
        notes = params.get("notes", "").strip()

        if not project_id:
            return {"success": False, "error": "project_id is required."}
        if not notes:
            return {"success": False, "error": "notes content is required."}

        try:
            project = Project.objects.get(id=project_id, studio=context.studio)
        except Project.DoesNotExist:
            return {"success": False, "error": "Project not found."}

        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
        user_display = context.user.get_full_name() or context.user.email
        entry = f"[{timestamp}] ({user_display}): {notes}"

        existing = project.internal_notes or ""
        if existing:
            project.internal_notes = f"{existing}\n\n{entry}"
        else:
            project.internal_notes = entry

        project.save(update_fields=["internal_notes", "updated_at"])

        return {
            "success": True,
            "message": f"Note added to project {project.reference}.",
            "project": {
                "id": str(project.id),
                "reference": project.reference,
                "internal_notes": project.internal_notes,
            },
        }

    except Exception as exc:
        logger.exception("Error adding project note")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="change_project_priority",
    permission="projects.change_project",
    risk="low_risk_write",
    description="Change project priority. Requires confirmation.",
    timeout=30,
)
def change_project_priority(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    """Change the priority of a project."""
    try:
        project_id = params.get("project_id", "").strip()
        priority = params.get("priority", "").strip()

        if not project_id:
            return {"success": False, "error": "project_id is required."}
        if not priority:
            return {"success": False, "error": "priority is required."}

        validated_priority = _validate_priority(priority)
        if validated_priority is None:
            return {
                "success": False,
                "error": f"Invalid priority '{priority}'. Valid options: low, medium, high, urgent.",
            }

        try:
            project = Project.objects.get(id=project_id, studio=context.studio)
        except Project.DoesNotExist:
            return {"success": False, "error": "Project not found."}

        old_priority = project.priority
        if old_priority == validated_priority:
            return {
                "success": False,
                "error": f"Project {project.reference} already has '{validated_priority}' priority.",
            }

        project.priority = validated_priority
        project.save(update_fields=["priority", "updated_at"])

        return {
            "success": True,
            "message": f"Priority for {project.reference} changed from '{old_priority}' to '{validated_priority}'.",
            "project": {
                "id": str(project.id),
                "reference": project.reference,
                "old_priority": old_priority,
                "new_priority": validated_priority,
            },
        }

    except Exception as exc:
        logger.exception("Error changing project priority")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="create_reminder",
    permission="notifications.add_notification",
    risk="low_risk_write",
    description="Create a reminder notification. Requires confirmation.",
    timeout=30,
)
def create_reminder(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    """Create a notification reminder."""
    try:
        title = params.get("title", "").strip()

        if not title:
            return {"success": False, "error": "title is required."}

        due_date = _parse_date(params.get("due_date"))
        description = params.get("description", "").strip()

        target_user_id = params.get("assigned_to")
        target_user = context.user
        if target_user_id:
            try:
                target_user = User.objects.get(pk=target_user_id, studio=context.studio)
            except (User.DoesNotExist, ValueError):
                return {"success": False, "error": "Assigned user not found in this studio."}

        message = description or title
        if due_date:
            message = f"{message}\n\nDue: {due_date.isoformat()}"

        notification = Notification.objects.create(
            user=target_user,
            notification_type=Notification.Type.GENERAL,
            title=title,
            message=message,
            entity_type="reminder",
        )

        user_display = target_user.get_full_name() or target_user.email
        return {
            "success": True,
            "message": f"Reminder '{notification.title}' created for {user_display}.",
            "reminder": _serialize_notification(notification),
        }

    except Exception as exc:
        logger.exception("Error creating reminder")
        return {"success": False, "error": str(exc)}
