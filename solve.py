"""Generic problem solving functions."""


def solve_equation(a: float, b: float) -> float:
    """Return solution to ``a * x + b = 0``."""
    if a == 0:
        raise ValueError("a cannot be zero")
    return -b / a
