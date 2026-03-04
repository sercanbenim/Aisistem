"""Virtual brain that discovers and orchestrates repository modules.

The project contains many small modules that represent different cognitive
abilities (``listen``, ``think``, ``analyze`` and so on).  This module stitches
them together by scanning the repository, exposing light-weight metadata for
each module and lazily importing them when required.  The design makes it easy
to introspect the available building blocks without eagerly importing optional
dependencies such as TensorFlow.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import ast
import inspect
import importlib
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Iterable


PROJECT_ROOT = Path(__file__).resolve().parent
EXCLUDED_MODULES = {"virtual_brain", "main", "tests"}


def _discover_python_files(directory: Path) -> Iterable[Path]:
    """Yield Python files that belong to the virtual brain."""

    for path in directory.glob("*.py"):
        if path.stem.startswith("_"):
            continue
        yield path


@dataclass
class BrainRegion:
    """Metadata holder for a module participating in the virtual brain."""

    name: str
    path: Path
    description: str
    _module: ModuleType | None = field(default=None, init=False, repr=False)

    def _load(self) -> ModuleType:
        if self._module is None:
            self._module = importlib.import_module(self.name)
        return self._module

    def get_callable(self, attribute: str) -> Callable[..., Any]:
        module = self._load()
        obj = getattr(module, attribute)
        if not callable(obj):  # pragma: no cover - defensive branch
            raise TypeError(f"Attribute '{attribute}' on module '{self.name}' is not callable")
        return obj

    def available_callables(self) -> Dict[str, Callable[..., Any]]:
        """Return public callables exposed by the module."""

        module = self._load()
        members: Dict[str, Callable[..., Any]] = {}
        for attr, value in vars(module).items():
            if attr.startswith("_"):
                continue
            if callable(value):
                members[attr] = value
        return members


class VirtualBrain:
    """Aggregate view of the assistant's capabilities."""

    def __init__(self) -> None:
        self._regions: Dict[str, BrainRegion] = {}
        self._discover_regions()

    def _discover_regions(self) -> None:
        for path in _discover_python_files(PROJECT_ROOT):
            if path.stem in EXCLUDED_MODULES:
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:  # pragma: no cover - defensive branch
                continue
            doc = ast.get_docstring(tree) or "No description available."
            region = BrainRegion(name=path.stem, path=path, description=doc)
            self._regions[path.stem] = region

    def regions(self) -> Dict[str, BrainRegion]:
        """Return the discovered regions."""

        return dict(self._regions)

    def summary(self) -> str:
        """Return a human friendly summary of the virtual brain."""

        lines = []
        for name in sorted(self._regions):
            region = self._regions[name]
            first_line = region.description.splitlines()[0]
            lines.append(f"- {name}: {first_line}")
        return "\n".join(lines)

    def get_function(self, module_name: str, function_name: str) -> Callable[..., Any]:
        """Retrieve a callable from the specified region."""

        region = self._regions.get(module_name)
        if region is None:
            raise KeyError(f"Unknown region '{module_name}'")
        return region.get_callable(function_name)

    def describe_region(self, module_name: str) -> str:
        """Return an extended description for a single region."""

        region = self._regions.get(module_name)
        if region is None:
            raise KeyError(f"Unknown region '{module_name}'")
        description = inspect.cleandoc(region.description)
        callables = ", ".join(sorted(region.available_callables()))
        return f"{module_name}: {description} | callables: {callables}"

    def call(self, module_name: str, function_name: str, *args: Any, **kwargs: Any) -> Any:
        """Convenience helper for invoking a callable on a region."""

        func = self.get_function(module_name, function_name)
        return func(*args, **kwargs)


__all__ = ["VirtualBrain", "BrainRegion"]

