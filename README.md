# Aisistem

A.I assistant for everyone.

## Virtual brain

Run the assistant:

```bash
python -m main
```

The brain runs a cognitive loop inspired by real brain flow:

- **Perception**: listen for input and normalize text.
- **Comprehension**: analyze language signals (length, words, and top terms).
- **Reasoning**: generate a response from `think`.
- **Memory**: store cycle history in memory.
- **Action**: speak the result and archive when archive utilities exist.

## Autonomous mode

Run autonomous thinking cycles (no user input):

```bash
python -c "import autonom; autonom.run_auto(3)"
```

In autonomous mode, the assistant produces internal prompts based on prior
memory, so each cycle reflects on previous outputs.

## n8n-style workflow mode

You can run graph workflows where each node calls a module function and passes
its output to the next node.

```python
from brains import Brain

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

result = Brain().run_workflow(workflow, "HELLO")
print(result["response"])
```

Condition nodes are also supported with `type="condition"` and branching via
`true_next` / `false_next`.


## Web UI

You can open a simple browser UI to see chat, autonomous cycles, workflow runs,
and recent brain memory in one page:

```bash
python ui.py
```

Then open `http://127.0.0.1:8000`.
