"""Drawing utilities using turtle."""

import turtle


def draw_square(size: int) -> None:
    """Draw a square with the given ``size``."""
    t = turtle.Turtle()
    for _ in range(4):
        t.forward(size)
        t.right(90)
    turtle.done()
