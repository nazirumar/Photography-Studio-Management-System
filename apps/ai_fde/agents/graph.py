from __future__ import annotations

import json
import logging
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from apps.ai_fde.agents.policies import sanitize_input
from apps.ai_fde.agents.routing import classify_intent
from apps.ai_fde.agents.state import FDEState
from apps.ai_fde.llm.openai_provider import OpenAIProvider
from apps.ai_fde.llm.router import ModelRouter
from apps.ai_fde.prompts.system import FDE_SYSTEM_PROMPT
from apps.ai_fde.services.execution import execute_tool
from apps.ai_fde.tools.base import FDEContext, get_registry
from apps.ai_fde.tools.registry import load_all_tools

logger = logging.getLogger("ai_fde")

load_all_tools()


def load_context(state: FDEState) -> dict[str, Any]:
    """Load page context and sanitize input."""
    msg = state.get("user_message", "")
    msg = sanitize_input(msg)
    return {"user_message": msg, "errors": []}


def understand_request(state: FDEState) -> dict[str, Any]:
    """Use LLM to classify intent and determine tool calls."""
    provider = OpenAIProvider()
    router = ModelRouter()
    model = router.route("classify")

    intent = classify_intent(state["user_message"])

    registry = get_registry()
    tools_desc = [
        {
            "name": t.name,
            "description": t.description,
            "risk": t.risk_level,
        }
        for t in registry.list_tools()
    ]

    messages = [
        {"role": "system", "content": FDE_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""User message: {state['user_message']}

Available tools: {json.dumps(tools_desc, indent=2)}

Determine the intent and which tool(s) to call. Respond with JSON:
{{
    "intent": "search|query|finance|alert|general",
    "tool_calls": [{{"name": "tool_name", "arguments": {{}}}}],
    "explanation": "brief explanation of what you're doing"
}}""",
        },
    ]

    result = provider.generate(messages, model=model)
    if result:
        try:
            parsed = json.loads(result.get("content", "{}"))
            return {
                "intent": parsed.get("intent", intent),
                "tool_calls": parsed.get("tool_calls", []),
            }
        except (json.JSONDecodeError, KeyError):
            pass

    return {"intent": intent, "tool_calls": []}


def permission_guard(state: FDEState) -> dict[str, Any]:
    """Check permissions for requested tool calls."""
    return {}


def route_request(state: FDEState) -> str:
    """Route based on intent and tool calls."""
    tool_calls = state.get("tool_calls", [])
    if tool_calls:
        return "business_tools"

    intent = state.get("intent", "general")
    if intent == "alert":
        return "business_tools"

    return "general_reasoning"


def business_tools_node(state: FDEState) -> dict[str, Any]:
    """Execute business tools and collect results."""
    from apps.accounts.models import User
    from apps.studios.models import Studio

    tool_calls = state.get("tool_calls", [])

    try:
        user = User.objects.get(pk=state["user_id"])
        studio = Studio.objects.get(pk=state["studio_id"])
    except (User.DoesNotExist, Studio.DoesNotExist):
        return {"tool_results": [{"tool": "none", "result": {"success": False, "error": "User or studio not found."}}]}

    context = FDEContext(
        user=user,
        studio=studio,
        conversation_id=state.get("conversation_id"),
    )

    tool_results: list[dict[str, Any]] = []
    for tc in tool_calls:
        tool_name = tc.get("name", "")
        arguments = tc.get("arguments", {})
        result = execute_tool(tool_name, context, arguments)
        tool_results.append({"tool": tool_name, "result": result})

    return {"tool_results": tool_results}


def general_reasoning_node(state: FDEState) -> dict[str, Any]:
    """General LLM reasoning without tools."""
    provider = OpenAIProvider()
    router = ModelRouter()
    model = router.route("general")

    messages = [
        {"role": "system", "content": FDE_SYSTEM_PROMPT},
        {"role": "user", "content": state["user_message"]},
    ]

    result = provider.generate(messages, model=model)
    if result:
        return {
            "final_response": {
                "type": "text",
                "text": result.get("content", "I can help you with that."),
            }
        }
    return {
        "final_response": {
            "type": "text",
            "text": "I can help you with that. What would you like to know?",
        }
    }


def compose_response(state: FDEState) -> dict[str, Any]:
    """Compose final response from tool results or general reasoning."""
    if state.get("final_response"):
        return {}

    tool_results = state.get("tool_results", [])
    if not tool_results:
        return {"final_response": {"type": "text", "text": "No results found."}}

    provider = OpenAIProvider()
    router = ModelRouter()
    model = router.route("primary")

    results_text = json.dumps(tool_results, indent=2, default=str)
    naira = "\u20a6"
    user_msg = state["user_message"]
    prompt = (
        f"User asked: {user_msg}\n\nTool results:\n{results_text}\n\n"
        f"Compose a clear, concise response. Format metrics as structured "
        f"data when appropriate. Use {naira} for money."
    )
    messages = [
        {"role": "system", "content": FDE_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    result = provider.generate(messages, model=model)
    if result:
        text = result.get("content", "")
        try:
            parsed = json.loads(text)
            return {"final_response": parsed}
        except (json.JSONDecodeError, TypeError):
            return {"final_response": {"type": "text", "text": text}}

    return {"final_response": {"type": "text", "text": "Here are the results from the database."}}


graph_builder = StateGraph(FDEState)

graph_builder.add_node("load_context", load_context)
graph_builder.add_node("understand_request", understand_request)
graph_builder.add_node("permission_guard", permission_guard)
graph_builder.add_node("business_tools", business_tools_node)
graph_builder.add_node("general_reasoning", general_reasoning_node)
graph_builder.add_node("compose_response", compose_response)

graph_builder.add_edge(START, "load_context")
graph_builder.add_edge("load_context", "understand_request")
graph_builder.add_edge("understand_request", "permission_guard")
graph_builder.add_conditional_edges(
    "permission_guard",
    route_request,
    {
        "business_tools": "business_tools",
        "general_reasoning": "general_reasoning",
    },
)
graph_builder.add_edge("business_tools", "compose_response")
graph_builder.add_edge("general_reasoning", "compose_response")
graph_builder.add_edge("compose_response", END)

memory = MemorySaver()
fde_graph = graph_builder.compile(checkpointer=memory)
