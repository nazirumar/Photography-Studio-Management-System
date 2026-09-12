from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


@dataclass
class FDEContext:
    user: Any  # accounts.User
    studio: Any  # studios.Studio
    conversation_id: str | None = None
    request_id: str | None = None


RISK_LEVELS = ("read", "low_risk_write", "high_risk_write")


@dataclass
class FDETool:
    name: str
    description: str
    handler: Callable[..., dict[str, Any]]
    permission: str
    risk_level: str  # "read", "low_risk_write", "high_risk_write"
    input_schema: dict[str, Any]
    timeout: int = 30

    def __post_init__(self) -> None:
        if self.risk_level not in RISK_LEVELS:
            raise ValueError(
                f"Invalid risk_level {self.risk_level!r}; must be one of {RISK_LEVELS}"
            )


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, FDETool] = {}

    def register(self, tool: FDETool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool
        logger.info("Registered FDE tool: %s (risk=%s)", tool.name, tool.risk_level)

    def get(self, name: str) -> FDETool:
        try:
            return self._tools[name]
        except KeyError:
            raise ValueError(f"Tool {name!r} not found in registry") from None

    def list_tools(self) -> list[FDETool]:
        return list(self._tools.values())

    def list_by_risk(self, risk: str) -> list[FDETool]:
        return [t for t in self._tools.values() if t.risk_level == risk]

    def validate_input(self, name: str, arguments: dict[str, Any]) -> bool:
        tool = self.get(name)
        schema = tool.input_schema

        # Check required fields
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in arguments:
                raise ValueError(
                    f"Missing required field {field_name!r} for tool {name!r}"
                )

        # Basic type-checking against properties
        properties = schema.get("properties", {})
        for key, value in arguments.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(
                        f"Field {key!r} must be a string for tool {name!r}"
                    )
                if expected_type == "integer" and not isinstance(value, int):
                    raise ValueError(
                        f"Field {key!r} must be an integer for tool {name!r}"
                    )
                if expected_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Field {key!r} must be a number for tool {name!r}"
                    )
                if expected_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(
                        f"Field {key!r} must be a boolean for tool {name!r}"
                    )

        return True


_global_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    return _global_registry


def fde_tool(
    name: str,
    permission: str,
    risk: str = "read",
    description: str = "",
    timeout: int = 30,
) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]:
    def decorator(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        # Derive input_schema from function annotations / docstring if available
        schema: dict[str, Any] = _build_schema_from_params(func)

        tool = FDETool(
            name=name,
            description=description or func.__doc__ or "",
            handler=func,
            permission=permission,
            risk_level=risk,
            input_schema=schema,
            timeout=timeout,
        )
        _global_registry.register(tool)
        return func

    return decorator


def _build_schema_from_params(func: Callable[..., Any]) -> dict[str, Any]:
    import inspect

    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    # Expected signature: (context, params) - skip both
    if len(params) <= 2:
        return {"type": "object", "properties": {}, "required": []}

    # If someone defines extra params beyond context/params, build schema from them
    properties: dict[str, Any] = {}
    required: list[str] = []
    for param_name in params[2:]:
        param_info = sig.parameters[param_name]
        annotation = param_info.annotation
        prop: dict[str, Any] = {}

        if annotation is inspect.Parameter.empty or annotation is str:
            prop["type"] = "string"
        elif annotation is int:
            prop["type"] = "integer"
        elif annotation is float:
            prop["type"] = "number"
        elif annotation is bool:
            prop["type"] = "boolean"

        if param_info.default is not inspect.Parameter.empty:
            prop["default"] = param_info.default
        else:
            required.append(param_name)

        properties[param_name] = prop

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }
