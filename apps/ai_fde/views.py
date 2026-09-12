from __future__ import annotations

import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.services import get_user_studio
from apps.ai_fde.models.action import AIActionProposal
from apps.ai_fde.models.conversation import AIConversation
from apps.ai_fde.services.confirmation import (
    approve_proposal,
    execute_proposal,
    get_pending_proposals,
    reject_proposal,
)
from apps.ai_fde.services.conversation import (
    get_conversations,
    get_messages,
)

logger = logging.getLogger(__name__)


@login_required
def ai_fde_chat(request):
    """AI FDE chat page and message handler."""
    if request.method == "GET":
        studio = get_user_studio(request.user)
        conversations = get_conversations(request.user, studio)
        return render(request, "ai_fde/chat.html", {
            "conversations": conversations,
        })

    # POST - handle chat messages
    from apps.ai_fde.agents.graph import fde_graph
    from apps.ai_fde.services.conversation import add_message, get_or_create_conversation

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    message = body.get("message", "").strip()
    conversation_id = body.get("conversation_id")
    current_page = body.get("current_page", "")

    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    studio = get_user_studio(request.user)

    conversation = get_or_create_conversation(
        user=request.user,
        studio=studio,
        conversation_id=conversation_id,
    )

    add_message(conversation, "user", message)

    config = {"configurable": {"thread_id": str(conversation.pk)}}
    initial_state = {
        "conversation_id": str(conversation.pk),
        "studio_id": str(studio.pk),
        "user_id": str(request.user.pk),
        "user_message": message,
        "current_page": current_page,
        "current_entity_type": None,
        "current_entity_id": None,
        "intent": None,
        "messages": [],
        "tool_calls": [],
        "tool_results": [],
        "retrieved_documents": [],
        "proposed_action": None,
        "requires_confirmation": False,
        "final_response": None,
        "errors": [],
        "model_used": None,
        "total_tokens": 0,
    }

    try:
        result = fde_graph.invoke(initial_state, config)
        response = result.get("final_response") or {
            "type": "text",
            "text": "No response generated.",
        }
    except Exception as exc:
        logger.error("Graph error: %s", exc)
        response = {
            "type": "text",
            "text": "Sorry, I encountered an error. Please try again.",
        }

    response_text = response.get("text", json.dumps(response, default=str))
    add_message(conversation, "assistant", response_text)

    return JsonResponse({
        "response": response,
        "conversation_id": str(conversation.pk),
    })


@login_required
def ai_fde_conversations(request):
    """List all conversations for the current user."""
    studio = get_user_studio(request.user)
    conversations = get_conversations(request.user, studio)

    if request.headers.get("Accept") == "application/json":
        data = [
            {
                "id": str(c.id),
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in conversations
        ]
        return JsonResponse({"conversations": data})

    return render(request, "ai_fde/conversations.html", {
        "conversations": conversations,
    })


@login_required
def ai_fde_conversation_detail(request, pk):
    """Show a single conversation with its messages."""
    studio = get_user_studio(request.user)
    conversation = get_object_or_404(
        AIConversation, pk=pk, user=request.user, studio=studio
    )
    messages_qs = get_messages(conversation)

    if request.headers.get("Accept") == "application/json":
        data = [
            {
                "id": str(m.id),
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages_qs
        ]
        return JsonResponse({
            "conversation": {
                "id": str(conversation.id),
                "title": conversation.title,
            },
            "messages": data,
        })

    return render(request, "ai_fde/conversation_detail.html", {
        "conversation": conversation,
        "messages": messages_qs,
    })


@login_required
def ai_fde_proposals(request):
    """List pending action proposals for the current user."""
    studio = get_user_studio(request.user)
    proposals = get_pending_proposals(request.user, studio)

    if request.headers.get("Accept") == "application/json":
        data = [
            {
                "id": str(p.id),
                "tool_name": p.tool_name,
                "arguments": p.arguments,
                "risk_level": p.risk_level,
                "status": p.status,
                "expires_at": p.expires_at.isoformat() if p.expires_at else None,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in proposals
        ]
        return JsonResponse({"proposals": data})

    return render(request, "ai_fde/proposals.html", {
        "proposals": proposals,
    })


@login_required
@require_POST
def ai_fde_approve_proposal(request, pk):
    """Approve an action proposal and execute the associated tool."""
    studio = get_user_studio(request.user)

    proposal = get_object_or_404(
        AIActionProposal,
        pk=pk,
        user=request.user,
        studio=studio,
    )

    try:
        proposal = approve_proposal(proposal.id, request.user)
        result = execute_proposal(proposal.id)

        if request.headers.get("Accept") == "application/json":
            return JsonResponse({
                "status": "executed",
                "proposal_id": str(proposal.id),
                "result": result,
            })

        messages.success(request, f"Action '{proposal.tool_name}' approved and executed.")
        return redirect("ai_fde:proposals")

    except ValueError as exc:
        if request.headers.get("Accept") == "application/json":
            return JsonResponse({"error": str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect("ai_fde:proposals")


@login_required
@require_POST
def ai_fde_reject_proposal(request, pk):
    """Reject an action proposal."""
    studio = get_user_studio(request.user)

    proposal = get_object_or_404(
        AIActionProposal,
        pk=pk,
        user=request.user,
        studio=studio,
    )

    try:
        proposal = reject_proposal(proposal.id, request.user)

        if request.headers.get("Accept") == "application/json":
            return JsonResponse({
                "status": "rejected",
                "proposal_id": str(proposal.id),
            })

        messages.success(request, f"Action '{proposal.tool_name}' rejected.")
        return redirect("ai_fde:proposals")

    except ValueError as exc:
        if request.headers.get("Accept") == "application/json":
            return JsonResponse({"error": str(exc)}, status=400)
        messages.error(request, str(exc))
        return redirect("ai_fde:proposals")
