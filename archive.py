"""Archive utility for storing historical data."""

from pathlib import Path


ARCHIVE_PATH = Path("archive.log")


def archive_entry(text: str) -> None:
    """Append ``text`` to the archive log."""
    with ARCHIVE_PATH.open("a", encoding="utf-8") as f:
        f.write(text + "\n")
