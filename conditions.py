"""Store and evaluate simple conditions."""

_conditions: dict[str, bool] = {}


def set_condition(name: str, value: bool) -> None:
    _conditions[name] = value


def check_condition(name: str) -> bool:
    return _conditions.get(name, False)
