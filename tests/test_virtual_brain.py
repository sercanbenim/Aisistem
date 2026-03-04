import importlib
import sys
import types
from unittest import mock


def test_virtual_brain_summary_lists_regions():
    virtual_brain = importlib.import_module("virtual_brain").VirtualBrain()
    summary = virtual_brain.summary()
    assert "listen" in summary
    assert "think" in summary


def test_virtual_brain_get_function_with_stubbed_think():
    fake_chat = types.ModuleType("chat")
    fake_chat.chatbot_response = lambda message: "ok"
    with mock.patch.dict(sys.modules, {"chat": fake_chat}):
        think = importlib.reload(importlib.import_module("think"))
        assert think.generate_response("hello") == "ok"


def test_think_fallback_when_chat_import_fails():
    with mock.patch.dict(sys.modules, {"chat": None}):
        think = importlib.reload(importlib.import_module("think"))
        response = think.generate_response("hello")
        assert "hello" in response.lower()


def test_brain_autonomous_cycles_store_memory():
    fake_chat = types.ModuleType("chat")
    fake_chat.chatbot_response = lambda message: f"answer:{message[:20]}"

    outputs: list[str] = []

    fake_speak = types.ModuleType("speak")
    fake_speak.say = lambda message: outputs.append(message)

    with mock.patch.dict(sys.modules, {"chat": fake_chat, "speak": fake_speak}):
        brains = importlib.reload(importlib.import_module("brains"))
        brain = brains.Brain()
        states = brain.run_autonomous(cycles=2)

    assert len(states) == 2
    assert len(outputs) == 2
    assert all(state.response.startswith("answer:") for state in states)


def test_brain_n8n_style_workflow_runs_linear_nodes():
    fake_chat = types.ModuleType("chat")
    fake_chat.chatbot_response = lambda message: f"chat:{message}"

    fake_speak = types.ModuleType("speak")
    fake_speak.say = lambda message: message

    with mock.patch.dict(sys.modules, {"chat": fake_chat, "speak": fake_speak}):
        brains = importlib.reload(importlib.import_module("brains"))
        brain = brains.Brain()

        workflow = {
            "start": "normalize",
            "nodes": {
                "normalize": {
                    "module": "understand",
                    "function": "normalize",
                    "input": "payload",
                    "output": "normalized",
                    "next": "respond",
                },
                "respond": {
                    "module": "think",
                    "function": "generate_response",
                    "input": "normalized",
                    "output": "response",
                    "next": None,
                },
            },
        }
        result = brain.run_workflow(workflow, "HELLO")

    assert result["normalized"] == "hello"
    assert result["response"] == "chat:hello"


def test_brain_n8n_style_workflow_condition_branching():
    fake_chat = types.ModuleType("chat")
    fake_chat.chatbot_response = lambda message: f"chat:{message}"

    fake_speak = types.ModuleType("speak")
    fake_speak.say = lambda message: message

    with mock.patch.dict(sys.modules, {"chat": fake_chat, "speak": fake_speak}):
        brains = importlib.reload(importlib.import_module("brains"))
        brain = brains.Brain()

        workflow = {
            "start": "normalize",
            "nodes": {
                "normalize": {
                    "module": "understand",
                    "function": "normalize",
                    "input": "payload",
                    "output": "normalized",
                    "next": "gate",
                },
                "gate": {
                    "type": "condition",
                    "key": "normalized",
                    "operator": "contains",
                    "value": "hello",
                    "true_next": "respond",
                    "false_next": "fallback",
                },
                "respond": {
                    "module": "think",
                    "function": "generate_response",
                    "input": "normalized",
                    "output": "response",
                    "next": None,
                },
                "fallback": {
                    "module": "understand",
                    "function": "normalize",
                    "input": "payload",
                    "output": "response",
                    "next": None,
                },
            },
        }
        result = brain.run_workflow(workflow, "Hello n8n")

    assert result["response"] == "chat:hello n8n"
