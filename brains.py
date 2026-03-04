"""High level orchestration for a brain-like virtual assistant.

Besides interactive and autonomous chat, this module now supports an n8n-style
workflow runner where each node maps to a discovered module/function and passes
context to the next node.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from Memory import MemoryManager
from virtual_brain import VirtualBrain


@dataclass
class CognitiveState:
    """Snapshot produced by one cognition cycle."""

    raw_input: str
    normalized_input: str
    analysis: dict[str, Any]
    response: str
    timestamp: str


class Brain:
    """High level orchestrator combining discovered brain regions."""

    def __init__(self) -> None:
        self._virtual_brain = VirtualBrain()
        self._memory = MemoryManager()

        self._listen: Callable[..., str] = self._virtual_brain.get_function(
            "listen", "get_input"
        )
        self._think: Callable[[str], str] = self._virtual_brain.get_function(
            "think", "generate_response"
        )
        self._speak: Callable[[str], None] = self._virtual_brain.get_function("speak", "say")

        self._normalize = self._load_optional("understand", "normalize")
        self._word_frequencies = self._load_optional("analyze", "word_frequencies")
        self._archive_entry = self._load_optional("archive", "archive_entry")

    def _load_optional(self, module: str, function: str) -> Callable[..., Any] | None:
        try:
            return self._virtual_brain.get_function(module, function)
        except (KeyError, AttributeError, ImportError):
            return None

    @property
    def summary(self) -> str:
        """Return a textual description of all loaded brain regions."""

        return self._virtual_brain.summary()

    def _timestamp(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def _normalize_text(self, message: str) -> str:
        if self._normalize is None:
            return message.strip().lower()
        return str(self._normalize(message)).strip()

    def _analyze_text(self, message: str) -> dict[str, Any]:
        if self._word_frequencies is None:
            return {"length": len(message), "words": len(message.split())}
        frequencies = self._word_frequencies(message)
        top_terms = sorted(frequencies.items(), key=lambda item: item[1], reverse=True)[:3]
        return {"length": len(message), "words": len(message.split()), "top_terms": top_terms}

    def _store_state(self, state: CognitiveState) -> None:
        history = self._memory.recall("history", [])
        history.append(
            {
                "input": state.raw_input,
                "normalized": state.normalized_input,
                "analysis": state.analysis,
                "response": state.response,
                "timestamp": state.timestamp,
            }
        )
        self._memory.store("history", history)
        self._memory.store("last_response", state.response)

    def process_message(self, message: str) -> CognitiveState:
        """Run one complete cognition cycle and return the resulting state."""

        normalized = self._normalize_text(message)
        analysis = self._analyze_text(normalized)
        try:
            response = self._think(normalized)
        except Exception as exc:  # pragma: no cover - resilience path
            response = f"Internal reasoning fallback: {exc}"
        state = CognitiveState(
            raw_input=message,
            normalized_input=normalized,
            analysis=analysis,
            response=response,
            timestamp=self._timestamp(),
        )
        self._store_state(state)
        if self._archive_entry is not None:
            self._archive_entry(f"[{state.timestamp}] USER={message} BOT={response}")
        return state

    def _build_autonomous_prompt(self) -> str:
        history = self._memory.recall("history", [])
        regions_count = len(self._virtual_brain.regions())
        if not history:
            return (
                "Autonomous boot thought: establish baseline awareness and state "
                f"using {regions_count} regions."
            )
        last = history[-1]
        return (
            "Autonomous reflection: refine previous response "
            f"'{last['response']}' using analysis {last['analysis']}."
        )

    def run_autonomous(self, cycles: int = 3) -> list[CognitiveState]:
        """Run autonomous cognition cycles without user input."""

        states: list[CognitiveState] = []
        for _ in range(cycles):
            prompt = self._build_autonomous_prompt()
            state = self.process_message(prompt)
            self._speak(state.response)
            states.append(state)
        return states

    def run_workflow(self, workflow: dict[str, Any], payload: str) -> dict[str, Any]:
        """Execute an n8n-like workflow graph.

        Workflow shape::

            {
              "start": "node_id",
              "nodes": {
                "node_id": {
                  "module": "understand",
                  "function": "normalize",
                  "input": "payload",
                  "output": "normalized",
                  "next": "another_node"
                }
              }
            }

        Supported nodes:
        - function node: ``module`` + ``function`` (+ optional ``input``/``output``)
        - condition node: ``type='condition'`` with ``key``, ``operator`` and ``value``
          and branch targets ``true_next``/``false_next``
        """

        context: dict[str, Any] = {
            "payload": payload,
            "last_response": self._memory.recall("last_response"),
            "history": self._memory.recall("history", []),
        }
        nodes = workflow.get("nodes", {})
        current = workflow.get("start")
        visited = 0

        while current is not None:
            if current not in nodes:
                raise KeyError(f"Unknown workflow node: {current}")
            visited += 1
            if visited > 100:
                raise RuntimeError("Workflow exceeded safe node limit (possible loop)")

            node = nodes[current]
            node_type = node.get("type", "function")
            if node_type == "condition":
                current = self._run_condition_node(node, context)
                continue

            module = node["module"]
            function = node["function"]
            func = self._virtual_brain.get_function(module, function)
            input_key = node.get("input", "payload")
            output_key = node.get("output", function)
            value = context.get(input_key)
            context[output_key] = func(value)
            current = node.get("next")

        if "response" in context:
            self._memory.store("last_response", context["response"])
        return context

    def _run_condition_node(self, node: dict[str, Any], context: dict[str, Any]) -> str | None:
        key = node["key"]
        operator = node.get("operator", "equals")
        expected = node.get("value")
        actual = context.get(key)

        if operator == "contains":
            result = str(expected) in str(actual)
        elif operator == "equals":
            result = actual == expected
        elif operator == "starts_with":
            result = str(actual).startswith(str(expected))
        else:
            raise ValueError(f"Unsupported operator: {operator}")

        return node.get("true_next") if result else node.get("false_next")

    def run(self) -> None:
        """Run interactive chat loop until user quits or input ends."""

        print("Virtual brain initialised. Available regions:")
        print(self.summary)
        while True:
            try:
                message = self._listen()
            except EOFError:
                break
            if message.lower() == "quit":
                break
            state = self.process_message(message)
            self._speak(state.response)


def run() -> None:
    Brain().run()


if __name__ == "__main__":
    run()
