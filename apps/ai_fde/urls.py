from __future__ import annotations

from django.urls import path

from . import views

app_name = "ai_fde"

urlpatterns = [
    path("", views.ai_fde_chat, name="chat"),
    path("conversations/", views.ai_fde_conversations, name="conversations"),
    path(
        "conversations/<uuid:pk>/",
        views.ai_fde_conversation_detail,
        name="conversation_detail",
    ),
    path("proposals/", views.ai_fde_proposals, name="proposals"),
    path(
        "proposals/<uuid:pk>/approve/",
        views.ai_fde_approve_proposal,
        name="approve_proposal",
    ),
    path(
        "proposals/<uuid:pk>/reject/",
        views.ai_fde_reject_proposal,
        name="reject_proposal",
    ),
]
