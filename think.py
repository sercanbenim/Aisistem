"""Reasoning helpers for the assistant.

The preferred backend is ``chat.chatbot_response``. When heavyweight runtime
requirements are missing, this module falls back to a deterministic local
response strategy so the rest of the brain can keep operating.
"""

from __future__ import annotations


try:
    from chat import chatbot_response as _chatbot_response
except Exception:  # pragma: no cover - optional dependency path
    _chatbot_response = None


def _fallback_response(message: str) -> str:
    cleaned = message.strip()
    if not cleaned:
        return "I need an input signal to think."
    return f"Autonomous reflection: I understood '{cleaned}'."


def generate_response(message: str) -> str:
    """Generate a response using the chatbot model or local fallback."""

    if _chatbot_response is None:
        return _fallback_response(message)
    return _chatbot_response(message)
