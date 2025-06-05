"""Manage a simple network of nodes."""


class Network:
    def __init__(self) -> None:
        self.nodes: list[str] = []

    def add_node(self, name: str) -> None:
        self.nodes.append(name)
