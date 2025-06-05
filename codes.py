"""Code execution helpers."""


def execute(code: str, namespace: dict | None = None) -> None:
    """Execute arbitrary Python code in the provided namespace."""
    if namespace is None:
        namespace = {}
    exec(code, namespace)
