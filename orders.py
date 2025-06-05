"""Store user orders."""

_orders: list[str] = []


def add_order(order: str) -> None:
    _orders.append(order)


def list_orders() -> list[str]:
    return list(_orders)
