from __future__ import annotations

import re


_INTENT_KEYWORDS: dict[str, list[str]] = {
    "search": ["search", "find", "look up", "locate"],
    "query": ["show", "get", "list", "display", "view", "what are", "who is"],
    "finance": ["how much", "revenue", "profit", "income", "expense", "balance", "invoice", "payment"],
    "alert": [
        "overdue",
        "low stock",
        "maintenance",
        "expiring",
        "running out",
        "alert",
        "warning",
    ],
}

_DEFAULT_INTENT = "general"


def classify_intent(message: str) -> str:
    """Classify user intent from message using keyword matching.

    Returns one of: search, query, finance, alert, general.
    """
    normalized = message.lower().strip()

    for intent, keywords in _INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized:
                return intent

    return _DEFAULT_INTENT
