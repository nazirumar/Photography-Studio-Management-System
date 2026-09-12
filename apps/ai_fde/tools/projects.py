from __future__ import annotations

import logging
from datetime import date
from typing import Any

from django.db.models import Q

from apps.projects.models import Project

from .base import FDEContext, fde_tool

logger = logging.getLogger(__name__)


def _project_to_dict(p: Project) -> dict[str, Any]:
    return {
        "id": str(p.id),
        "reference": p.reference,
        "client": str(p.client),
        "client_id": str(p.client_id) if p.client_id else None,
        "status": p.status,
        "priority": p.priority,
        "shoot_date": p.shoot_date.isoformat() if p.shoot_date else None,
        "expected_delivery": p.expected_delivery.isoformat() if p.expected_delivery else None,
        "actual_delivery": p.actual_delivery.isoformat() if p.actual_delivery else None,
        "total_captured": p.total_captured,
        "edited_count": p.edited_count,
        "printed_count": p.printed_count,
    }


@fde_tool(
    name="get_project",
    permission="projects.view_project",
    risk="read",
    description="Get a single project by ID.",
    timeout=15,
)
def get_project(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        project_id = params.get("project_id", "").strip()
        if not project_id:
            return {"success": False, "error": "project_id is required."}

        project = Project.objects.select_related("client", "booking").get(
            id=project_id, studio=context.studio
        )
        return {"success": True, "project": _project_to_dict(project)}
    except Project.DoesNotExist:
        return {"success": False, "error": "Project not found."}
    except Exception as exc:
        logger.exception("Error getting project %s", params.get("project_id"))
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="search_projects",
    permission="projects.view_project",
    risk="read",
    description="Search projects by reference or client name, optionally filtered by status.",
    timeout=15,
)
def search_projects(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        query = params.get("query", "").strip()
        status = params.get("status", "").strip()
        limit = int(params.get("limit", 10))

        qs = Project.objects.filter(studio=context.studio).select_related("client")

        if status:
            qs = qs.filter(status=status)

        if query:
            qs = qs.filter(
                Q(reference__icontains=query)
                | Q(client__first_name__icontains=query)
                | Q(client__last_name__icontains=query)
                | Q(client__display_name__icontains=query)
            )

        projects = list(qs[:limit])
        return {
            "success": True,
            "count": len(projects),
            "projects": [_project_to_dict(p) for p in projects],
        }
    except Exception as exc:
        logger.exception("Error searching projects")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_overdue_projects",
    permission="projects.view_project",
    risk="read",
    description="Get projects that are past their expected delivery date and not completed.",
    timeout=15,
)
def get_overdue_projects(context: FDEContext, params: dict[str, Any]) -> dict[str, Any]:
    try:
        today = date.today()
        projects = list(
            Project.objects.filter(
                studio=context.studio,
                expected_delivery__lt=today,
            )
            .exclude(
                status__in=[
                    Project.Status.COMPLETED,
                    Project.Status.DELIVERED,
                ]
            )
            .select_related("client")
            .order_by("expected_delivery")
        )

        return {
            "success": True,
            "count": len(projects),
            "as_of": today.isoformat(),
            "projects": [_project_to_dict(p) for p in projects],
        }
    except Exception as exc:
        logger.exception("Error getting overdue projects")
        return {"success": False, "error": str(exc)}


@fde_tool(
    name="get_projects_by_status",
    permission="projects.view_project",
    risk="read",
    description="Get all projects with a specific status.",
    timeout=15,
)
def get_projects_by_status(
    context: FDEContext, params: dict[str, Any]
) -> dict[str, Any]:
    try:
        status = params.get("status", "").strip()
        if not status:
            return {"success": False, "error": "status parameter is required."}

        valid_statuses = [choice[0] for choice in Project.Status.choices]
        if status not in valid_statuses:
            return {
                "success": False,
                "error": f"Invalid status. Valid options: {valid_statuses}",
            }

        projects = list(
            Project.objects.filter(studio=context.studio, status=status)
            .select_related("client")
            .order_by("-created_at")
        )

        return {
            "success": True,
            "status": status,
            "count": len(projects),
            "projects": [_project_to_dict(p) for p in projects],
        }
    except Exception as exc:
        logger.exception("Error getting projects by status")
        return {"success": False, "error": str(exc)}
