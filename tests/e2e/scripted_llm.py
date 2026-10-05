"""A scripted OpenAI-compatible Chat Completions server for end-to-end tests.

It stands in for the model so the real DeepSeek Harness binary can be tested
without an API key: dsh sends a normal streaming request through its
``llm-pi-ai`` adapter; this server answers with the next scripted tool call for
the current ResearchForge phase, or with a final text once the script for that
phase is exhausted. Every request is recorded for assertions.

This is test infrastructure only. It is not a model and is never used by the
product.
"""

from __future__ import annotations

import json
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PREFIX = "mcp__researchforge__"
STEP_RE = re.compile(r"# ResearchForge step: (\w+)")
FOCUS_ID_RE = re.compile(r"investigates uncertainty (U\d+)")
FOCUS_TOKEN = "__FOCUS__"  # replaced by the focused uncertainty id in scripted arguments


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return ""


class ScriptedLLM:
    def __init__(self, script: dict[str, list[tuple[str, dict]]]) -> None:
        self.script = script
        self.requests: list[dict] = []
        self.tool_names_seen: set[str] = set()
        self.actions: list[str] = []  # loop actions in the order the controller requested them
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._server.shutdown()

    def respond(self, body: dict) -> dict:
        """Return {'tool': (name, args)} or {'text': str} for a request."""
        messages = body.get("messages", [])
        for tool in body.get("tools") or []:
            self.tool_names_seen.add(tool.get("function", {}).get("name", ""))
        action, start, focus_id = None, None, None
        for i, m in enumerate(messages):
            if m.get("role") == "user":
                text = _text(m.get("content"))
                match = STEP_RE.search(text)
                if match:
                    action, start = match.group(1), i
                    fm = FOCUS_ID_RE.search(text)
                    focus_id = fm.group(1) if fm else None
        if action is None:
            return {"text": "ResearchForge investigation"}  # e.g. a session-title request
        if not any(m.get("role") == "assistant" for m in messages[start + 1:]):
            self.actions.append(action)  # first request of a new step
        step =sum(1 for m in messages[start + 1:] if m.get("role") == "assistant" and m.get("tool_calls"))
        steps = self.script.get(action, [])
        if step < len(steps):
            name, args = steps[step]
            if focus_id:
                args = json.loads(json.dumps(args).replace(FOCUS_TOKEN, focus_id))
            return {"tool": (PREFIX + name, args)}
        return {"text": f"Recorded the {action} step results."}

    def _handler(self):
        llm = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # silence the default stderr access log
                pass

            def do_GET(self):
                if self.path.rstrip("/").endswith("/models"):
                    self._json({"object": "list", "data": [{"id": "scripted-model", "object": "model"}]})
                else:
                    self._json({"error": "not found"}, 404)

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length) or b"{}")
                llm.requests.append(body)
                if not self.path.rstrip("/").endswith("/chat/completions"):
                    return self._json({"error": "not found"}, 404)
                answer = llm.respond(body)
                if body.get("stream"):
                    self._stream(answer, body.get("model", "scripted-model"))
                else:
                    self._json(self._completion(answer, body.get("model", "scripted-model")))

            def _json(self, obj, status=200):
                data = json.dumps(obj).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            @staticmethod
            def _completion(answer, model):
                msg = {"role": "assistant", "content": answer.get("text")}
                finish = "stop"
                if "tool" in answer:
                    name, args = answer["tool"]
                    msg["tool_calls"] = [{"id": f"call_{int(time.time() * 1e6)}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}]
                    finish = "tool_calls"
                return {"id": "cmpl", "object": "chat.completion", "created": int(time.time()), "model": model,
                        "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}

            def _stream(self, answer, model):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                base = {"id": "chatcmpl-scripted", "object": "chat.completion.chunk", "created": int(time.time()), "model": model}

                def send(choices, usage=None):
                    chunk = {**base, "choices": choices}
                    if usage is not None:
                        chunk["usage"] = usage
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                    self.wfile.flush()

                if "tool" in answer:
                    name, args = answer["tool"]
                    call_id = f"call_{int(time.time() * 1e6)}"
                    send([{"index": 0, "delta": {"role": "assistant", "content": None, "tool_calls": [
                        {"index": 0, "id": call_id, "type": "function", "function": {"name": name, "arguments": ""}}]}, "finish_reason": None}])
                    send([{"index": 0, "delta": {"tool_calls": [{"index": 0, "function": {"arguments": json.dumps(args)}}]}, "finish_reason": None}])
                    finish = "tool_calls"
                else:
                    send([{"index": 0, "delta": {"role": "assistant", "content": answer["text"]}, "finish_reason": None}])
                    finish = "stop"
                send([{"index": 0, "delta": {}, "finish_reason": finish}])
                send([], usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15})
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()

        return Handler
