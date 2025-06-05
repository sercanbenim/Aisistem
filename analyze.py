"""Basic analysis utilities."""

from collections import Counter
from typing import Dict


def word_frequencies(text: str) -> Dict[str, int]:
    """Return a frequency mapping of words in ``text``."""
    tokens = text.lower().split()
    return Counter(tokens)
