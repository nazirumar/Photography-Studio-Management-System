from __future__ import annotations

from django.contrib import admin

from apps.ai_fde.models import (
    AIActionProposal,
    AIConversation,
    AIToolExecution,
    AIMessage,
    AIUsageLog,
    FDEContext,
    KnowledgeChunk,
    KnowledgeDocument,
)


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "studio", "user", "title", "created_at")
    list_filter = ("studio", "created_at")
    search_fields = ("title",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "role", "created_at")
    list_filter = ("role", "created_at")
    readonly_fields = ("id", "created_at")


@admin.register(AIToolExecution)
class AIToolExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "studio",
        "user",
        "tool_name",
        "risk_class",
        "status",
        "duration_ms",
        "created_at",
    )
    list_filter = ("risk_class", "status", "tool_name")
    readonly_fields = ("id", "created_at")


@admin.register(AIActionProposal)
class AIActionProposalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "studio",
        "user",
        "tool_name",
        "risk_level",
        "status",
        "expires_at",
        "created_at",
    )
    list_filter = ("status", "risk_level")
    readonly_fields = ("id", "created_at")


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "studio", "title", "document_type", "status", "chunk_count", "created_at")
    list_filter = ("document_type", "status")
    search_fields = ("title",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(KnowledgeChunk)
class KnowledgeChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "document", "chunk_index", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at")


@admin.register(AIUsageLog)
class AIUsageLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "studio",
        "user",
        "model_name",
        "input_tokens",
        "output_tokens",
        "tool_calls_count",
        "latency_ms",
        "estimated_cost_usd",
        "error",
        "created_at",
    )
    list_filter = ("model_name", "error")
    readonly_fields = ("id", "created_at")


@admin.register(FDEContext)
class FDEContextAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "current_page", "current_entity_type", "created_at")
    list_filter = ("current_page",)
    readonly_fields = ("id", "created_at")
