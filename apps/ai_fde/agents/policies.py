from __future__ import annotations

import re
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()

_PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a|an)\s+", re.IGNORECASE),
    re.compile(r"system\s*prompt", re.IGNORECASE),
    re.compile(r"act\s+as\s+if\s+you", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior", re.IGNORECASE),
    re.compile(r"override\s+(your\s+)?instructions", re.IGNORECASE),
    re.compile(r"<\|system\|>", re.IGNORECASE),
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
]

_TOOL_SCHEMAS: dict[str, dict[str, Any]] = {}


def register_tool_schema(tool_name: str, schema: dict[str, Any]) -> None:
    """Register a tool schema for argument validation."""
    _TOOL_SCHEMAS[tool_name] = schema


def has_permission(user: Any, permission: str) -> bool:
    """Check whether *user* has the given Django permission.

    *permission* should be in ``app_label.codename`` format,
    e.g. ``"clients.view_client"``.
    """
    if not getattr(user, "is_active", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    return user.has_perm(permission)


def can_access_studio(user: Any, studio_id: str) -> bool:
    """Return True if *user* belongs to the studio identified by *studio_id*."""
    if not getattr(user, "is_active", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    user_studio_id = getattr(getattr(user, "studio", None), "id", None)
    return str(user_studio_id) == str(studio_id)


def sanitize_input(message: str) -> str:
    """Strip potential prompt-injection patterns from user input.

    Returns the cleaned message.  Patterns that look like instruction
    overrides are removed; the remainder of the message is kept intact.
    """
    cleaned = message
    for pattern in _PROMPT_INJECTION_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    return cleaned.strip()


def validate_tool_arguments(tool_name: str, arguments: dict[str, Any]) -> bool:
    """Validate *arguments* against the registered schema for *tool_name*.

    If no schema is registered the call is allowed (open validation).
    """
    schema = _TOOL_SCHEMAS.get(tool_name)
    if schema is None:
        return True

    required = schema.get("required", [])
    properties = schema.get("properties", {})

    for field in required:
        if field not in arguments:
            return False

    for key, value in arguments.items():
        if key in properties:
            expected_type = properties[key].get("type")
            if expected_type == "string" and not isinstance(value, str):
                return False
            if expected_type == "number" and not isinstance(value, (int, float)):
                return False
            if expected_type == "integer" and not isinstance(value, int):
                return False
            if expected_type == "boolean" and not isinstance(value, bool):
                return False

    return True
