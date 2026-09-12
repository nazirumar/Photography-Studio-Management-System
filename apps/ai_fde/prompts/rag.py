from __future__ import annotations

RAG_CONTEXT_PROMPT = """\
You are answering a question about a photography studio's operations.

The following documents were retrieved from the studio's knowledge base:

{context}

User question: {question}

Use ONLY the information above to answer. If the context does not contain \
enough information, say so clearly.
"""

RAG_ANSWER_PROMPT = """\
Based on the provided context, answer the user's question concisely.

Context:
{context}

Question: {question}

Rules:
- Answer only from the provided context
- If the context is insufficient, respond with "I don't have enough information \
to answer that question."
- Keep the answer actionable and studio-relevant
- Use bullet points for multiple items
- Format monetary values in Nigerian Naira (₦)
"""
