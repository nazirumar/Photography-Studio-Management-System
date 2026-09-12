from __future__ import annotations

import logging
import time
from typing import Any

from apps.ai_fde.models.action import AIToolExecution
from apps.ai_fde.tools.base import FDEContext, ToolRegistry, get_registry

logger = logging.getLogger(__name__)


def execute_tool(
    tool_name: str,
    context: FDEContext,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Execute a registered FDE tool with timing, logging, and error handling.

    Args:
        tool_name: Name of the tool in the registry.
        context: The FDE context carrying user, studio, and request metadata.
        arguments: Validated arguments to pass to the tool handler.

    Returns:
        A dict with keys ``success`` (bool), ``result`` (tool output), and
        ``execution_id`` (UUID of the ``AIToolExecution`` record).
    """
    registry = get_registry()
    execution = _create_execution_record(tool_name, context, registry)
    start: float = 0.0

    try:
        tool = registry.get(tool_name)
        execution.status = AIToolExecution.Status.RUNNING
        execution.risk_class = tool.risk_level
        execution.save(update_fields=["status", "risk_class"])

        start = time.monotonic()
        result = tool.handler(context, arguments)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        execution.status = AIToolExecution.Status.SUCCESS
        execution.duration_ms = elapsed_ms
        execution.save(update_fields=["status", "duration_ms"])

        return {
            "success": result.get("success", True),
            "result": result,
            "execution_id": str(execution.id),
        }

    except Exception as exc:
        logger.exception("Tool %r execution failed", tool_name)
        elapsed_ms = int((time.monotonic() - start) * 1000) if start else 0
        execution.status = AIToolExecution.Status.FAILED
        execution.error_code = type(exc).__name__
        execution.error_message = str(exc)[:2000]
        execution.duration_ms = elapsed_ms
        execution.save(update_fields=[
            "status",
            "error_code",
            "error_message",
            "duration_ms",
        ])
        return {
            "success": False,
            "result": {"error": str(exc)},
            "execution_id": str(execution.id),
        }


def _create_execution_record(
    tool_name: str,
    context: FDEContext,
    registry: ToolRegistry,
) -> AIToolExecution:
    """Create and persist an ``AIToolExecution`` record."""
    try:
        tool = registry.get(tool_name)
        risk_class = tool.risk_level
    except ValueError:
        risk_class = AIToolExecution.RiskClass.READ

    return AIToolExecution.objects.create(
        studio=context.studio,
        user=context.user,
        tool_name=tool_name,
        validated_arguments={},
        risk_class=risk_class,
        status=AIToolExecution.Status.PENDING,
    )
