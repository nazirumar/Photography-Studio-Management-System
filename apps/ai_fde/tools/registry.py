from __future__ import annotations

from .base import get_registry


def load_all_tools() -> None:
    """Import all tool modules to trigger @fde_tool registration."""
    from . import (  # noqa: F401
        bookings,
        clients,
        financial,
        finance,
        inventory,
        operational,
        projects,
        writes,
    )

    registry = get_registry()
    if registry.list_tools():
        return  # already loaded
