"""Collection of small algorithms used by the assistant."""

from typing import Iterable, Any


def sort_numbers(numbers: Iterable[float]) -> list[float]:
    """Return a sorted list of numbers."""
    return sorted(numbers)


def factorial(n: int) -> int:
    """Compute factorial of ``n`` using iteration."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
