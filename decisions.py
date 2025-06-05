"""Simple rule-based decision module."""


def decide(message: str) -> str:
    """Return a decision label based on the message."""
    if "help" in message.lower():
        return "help"
    return "default"
