"""Central information registry."""

_info: dict[str, str] = {}


def add_info(key: str, value: str) -> None:
    _info[key] = value


def get_info(key: str) -> str | None:
    return _info.get(key)
