"""Basic pattern recognition helpers."""


def recognize(pattern: str, text: str) -> bool:
    return pattern in text
