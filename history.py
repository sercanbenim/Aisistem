"""Conversation history tracker."""

_history: list[str] = []


def add(entry: str) -> None:
    _history.append(entry)


def get() -> list[str]:
    return list(_history)
