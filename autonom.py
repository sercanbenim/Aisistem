"""Automatic loop runner for the assistant."""

from brains import Brain


def run_auto(cycles: int = 3) -> None:
    """Run autonomous cognition cycles."""

    brain = Brain()
    brain.run_autonomous(cycles=cycles)
