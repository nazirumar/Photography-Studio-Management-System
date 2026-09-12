from __future__ import annotations

import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from django.utils import timezone

from apps.ai_fde.models.action import AIActionProposal

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.accounts.models import User
    from apps.ai_fde.models.conversation import AIConversation
    from apps.studios.models import Studio

logger = logging.getLogger(__name__)

PROPOSAL_EXPIRY_HOURS = 24


def create_proposal(
    user: User,
    studio: Studio,
    tool_name: str,
    arguments: dict[str, Any],
    risk_level: str,
    conversation: AIConversation | None = None,
) -> AIActionProposal:
    """Create a pending action proposal requiring human approval.

    Args:
        user: The user who triggered the action.
        studio: The current studio.
        tool_name: Name of the tool to execute upon approval.
        arguments: Arguments to pass to the tool.
        risk_level: Risk classification string.
        conversation: Optional associated conversation.

    Returns:
        The created ``AIActionProposal``.
    """
    proposal = AIActionProposal.objects.create(
        studio=studio,
        user=user,
        conversation=conversation,
        tool_name=tool_name,
        arguments=arguments,
        risk_level=risk_level,
        status=AIActionProposal.Status.PENDING,
        expires_at=timezone.now() + timedelta(hours=PROPOSAL_EXPIRY_HOURS),
    )
    logger.info(
        "Created action proposal %s for tool %r (risk=%s)",
        proposal.id,
        tool_name,
        risk_level,
    )
    return proposal


def approve_proposal(proposal_id: str | Any, user: User) -> AIActionProposal:
    """Approve a pending proposal.

    Args:
        proposal_id: UUID of the proposal to approve.
        user: The user performing the approval.

    Returns:
        The updated ``AIActionProposal``.

    Raises:
        AIActionProposal.DoesNotExist: If the proposal is not found.
        ValueError: If the proposal is not in pending status or has expired.
    """
    proposal = AIActionProposal.objects.get(id=proposal_id)

    if proposal.status != AIActionProposal.Status.PENDING:
        raise ValueError(
            f"Proposal {proposal.id} is not pending (current status: {proposal.status})"
        )

    if proposal.is_expired:
        proposal.status = AIActionProposal.Status.EXPIRED
        proposal.save(update_fields=["status"])
        raise ValueError(f"Proposal {proposal.id} has expired")

    proposal.status = AIActionProposal.Status.APPROVED
    proposal.save(update_fields=["status"])
    logger.info("Proposal %s approved by user %s", proposal.id, user.id)
    return proposal


def reject_proposal(proposal_id: str | Any, user: User) -> AIActionProposal:
    """Reject a pending proposal.

    Args:
        proposal_id: UUID of the proposal to reject.
        user: The user performing the rejection.

    Returns:
        The updated ``AIActionProposal``.

    Raises:
        AIActionProposal.DoesNotExist: If the proposal is not found.
        ValueError: If the proposal is not in pending status.
    """
    proposal = AIActionProposal.objects.get(id=proposal_id)

    if proposal.status != AIActionProposal.Status.PENDING:
        raise ValueError(
            f"Proposal {proposal.id} is not pending (current status: {proposal.status})"
        )

    proposal.status = AIActionProposal.Status.REJECTED
    proposal.save(update_fields=["status"])
    logger.info("Proposal %s rejected by user %s", proposal.id, user.id)
    return proposal


def get_pending_proposals(user: User, studio: Studio) -> QuerySet[AIActionProposal]:
    """Return non-expired pending proposals for a user within a studio."""
    return AIActionProposal.objects.filter(
        studio=studio,
        user=user,
        status=AIActionProposal.Status.PENDING,
        expires_at__gt=timezone.now(),
    ).order_by("-created_at")


def execute_proposal(proposal_id: str | Any) -> dict[str, Any]:
    """Execute the tool associated with an approved proposal.

    Args:
        proposal_id: UUID of the approved proposal.

    Returns:
        A dict with ``success``, ``result``, and ``execution_id`` keys.

    Raises:
        AIActionProposal.DoesNotExist: If the proposal is not found.
        ValueError: If the proposal has not been approved or has expired.
    """
    proposal = AIActionProposal.objects.get(id=proposal_id)

    if proposal.status != AIActionProposal.Status.APPROVED:
        raise ValueError(
            f"Proposal {proposal.id} is not approved (current status: {proposal.status})"
        )

    if proposal.is_expired:
        proposal.status = AIActionProposal.Status.EXPIRED
        proposal.save(update_fields=["status"])
        raise ValueError(f"Proposal {proposal.id} has expired")

    from apps.ai_fde.tools.base import FDEContext

    context = FDEContext(user=proposal.user, studio=proposal.studio)

    from apps.ai_fde.services.execution import execute_tool

    result = execute_tool(proposal.tool_name, context, proposal.arguments)

    proposal.result = result
    proposal.status = (
        AIActionProposal.Status.EXECUTED
        if result.get("success")
        else AIActionProposal.Status.REJECTED
    )
    proposal.save(update_fields=["result", "status"])

    return result
