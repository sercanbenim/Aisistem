"""Simple web UI to observe brain behavior.

Run:
    python ui.py
Then open http://127.0.0.1:8000
"""

from __future__ import annotations

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from brains import Brain


def build_demo_workflow() -> dict[str, object]:
    """Return a small n8n-style workflow used by the UI."""

    return {
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


def run_workflow_demo(brain: Brain, payload: str) -> dict[str, object]:
    """Execute the built-in demo workflow."""

    return brain.run_workflow(build_demo_workflow(), payload)


class BrainUIServer(ThreadingHTTPServer):
    """HTTP server carrying a single shared Brain instance."""

    def __init__(self, server_address: tuple[str, int]) -> None:
        super().__init__(server_address, BrainUIHandler)
        self.brain = Brain()
        self.events: list[str] = []


class BrainUIHandler(BaseHTTPRequestHandler):
    """Handle simple HTML interactions for chat and demos."""

    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/":
            self.send_error(404, "Not Found")
            return
        self._render_index()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        payload = parse_qs(raw)

        if self.path == "/chat":
            message = payload.get("message", [""])[0]
            state = self.server.brain.process_message(message)
            self.server.events.append(
                f"Chat -> input='{message}' response='{state.response}' analysis={state.analysis}"
            )
        elif self.path == "/autonomous":
            try:
                cycles = int(payload.get("cycles", ["1"])[0])
            except ValueError:
                cycles = 1
            states = self.server.brain.run_autonomous(max(1, min(cycles, 10)))
            self.server.events.append(
                "Autonomous -> "
                + ", ".join([f"{item.timestamp}: {item.response}" for item in states])
            )
        elif self.path == "/workflow":
            message = payload.get("payload", [""])[0]
            result = run_workflow_demo(self.server.brain, message)
            self.server.events.append(f"Workflow -> payload='{message}' response='{result.get('response')}'")
        else:
            self.send_error(404, "Not Found")
            return

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def _render_index(self) -> None:
        brain = self.server.brain
        history = brain._memory.recall("history", [])[-5:]  # noqa: SLF001 - diagnostic UI
        events = self.server.events[-10:]

        content = f"""
<!doctype html>
<html>
<head>
<meta charset='utf-8'>
<title>Aisistem Brain UI</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
.card {{ background: #1e293b; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; }}
input, button {{ padding: 0.5rem; border-radius: 6px; border: none; }}
input {{ width: 70%; }}
button {{ background: #38bdf8; color: #0f172a; font-weight: bold; }}
pre {{ white-space: pre-wrap; word-break: break-word; }}
</style>
</head>
<body>
<h1>🧠 Aisistem Brain UI</h1>
<div class='card'>
<h2>Regions</h2>
<pre>{escape(brain.summary)}</pre>
</div>
<div class='card'>
<h2>Chat</h2>
<form method='post' action='/chat'>
<input name='message' placeholder='Type message...'/>
<button type='submit'>Send</button>
</form>
</div>
<div class='card'>
<h2>Autonomous</h2>
<form method='post' action='/autonomous'>
<input name='cycles' value='2'/>
<button type='submit'>Run cycles</button>
</form>
</div>
<div class='card'>
<h2>Workflow (n8n-style demo)</h2>
<form method='post' action='/workflow'>
<input name='payload' placeholder='Workflow payload...'/>
<button type='submit'>Run workflow</button>
</form>
</div>
<div class='card'>
<h2>Recent Memory (last 5)</h2>
<pre>{escape(str(history))}</pre>
</div>
<div class='card'>
<h2>Event Log (last 10)</h2>
<pre>{escape(str(events))}</pre>
</div>
</body>
</html>
"""
        data = content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run_ui(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = BrainUIServer((host, port))
    print(f"Brain UI running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_ui()
