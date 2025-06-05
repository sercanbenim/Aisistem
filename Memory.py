"""Simple in-memory storage for the assistant."""

import json
from typing import Any


class MemoryManager:
    """Manage key/value pairs with optional persistence."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def store(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        self._data[key] = value

    def recall(self, key: str, default: Any | None = None) -> Any:
        """Retrieve a value from memory."""
        return self._data.get(key, default)

    def save(self, path: str) -> None:
        """Persist memory to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f)

    def load(self, path: str) -> None:
        """Load memory from a JSON file if it exists."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._data = {}
