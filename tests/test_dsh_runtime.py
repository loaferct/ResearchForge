import json
import stat
import sys
import textwrap

import yaml

from researchforge.config import Settings
from researchforge.runtime.dsh import DshHeadlessRuntime, build_overlay, write_overlay


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor("tag:yaml.org,2002:js", lambda loader, node: ("JS", loader.construct_scalar(node)))


def test_overlay_integrates_through_documented_rows(ws, settings):
    rows = build_overlay(ws, settings, python="/usr/bin/python3")
    mcp = rows[0]["insert"][0]
    assert mcp["name"] == "@deepseek-ai/dsh-mcp-client"
    cfg = mcp["config"]
    assert cfg["serverName"] == "researchforge" and cfg["transport"] == "stdio"
    assert cfg["command"] == "/usr/bin/python3" and cfg["args"] == ["-m", "researchforge.mcp_server"]
    assert cfg["env"]["RESEARCHFORGE_PROJECT_DIR"] == str(ws.root)
    by_id = {r.get("id"): r for r in rows[1:]}
    assert "ResearchForge" in by_id["system-prompt"]["config"]["personaPrefix"]
    assert by_id["agent-default-model"]["config"] == {"provider": "deepseek-official", "model": "deepseek-flash"}
    for row in ("tool-bash", "tool-fs", "tool-web", "tool-subagent", "session-telemetry-otel"):
        assert by_id[row] == {"id": row, "disabled": True}
    assert "llm-pi-ai" not in by_id


def test_overlay_custom_open_model_endpoint_and_secret_refs(ws, tmp_path):
    settings = Settings.model_validate({"model": {"provider": "ignored", "model": "Qwen/Qwen3-32B", "custom": {
        "provider_id": "local-vllm", "base_url": "http://127.0.0.1:8000/v1", "api_key_env": "LOCAL_LLM_KEY", "models": ["Qwen/Qwen3-32B"], "context_window": 32768}}})
    path = write_overlay(ws, settings)
    text = path.read_text()
    data = yaml.load(text, Loader=_Loader)
    by_id = {r.get("id"): r for r in data[1:]}
    pi = by_id["llm-pi-ai"]["config"]["providers"]["local-vllm"]
    assert pi == {"api": "openai-completions", "baseURL": "http://127.0.0.1:8000/v1", "models": [{"id": "Qwen/Qwen3-32B", "contextWindow": 32768}], "apiKeyEnv": "LOCAL_LLM_KEY"}
    assert by_id["agent-default-model"]["config"] == {"provider": "local-vllm", "model": "Qwen/Qwen3-32B"}
    env = data[0]["insert"][0]["config"]["env"]
    assert env["SEMANTIC_SCHOLAR_API_KEY"] == ("JS", "process.env.SEMANTIC_SCHOLAR_API_KEY ?? ''")
    assert "!!js" in text


FAKE_DSH = textwrap.dedent(
    """
    import json, sys, os
    argv = sys.argv[1:]
    prompt = sys.stdin.read()
    log = os.environ["FAKE_DSH_LOG"]
    with open(log, "a") as fh:
        fh.write(json.dumps({"argv": argv, "prompt": prompt, "cwd": os.getcwd(), "home": os.environ.get("DSH_HOME")}) + "\\n")
    if "--session-id" in argv and argv[argv.index("--session-id") + 1] == "gone":
        print("dsh: no stored Session with id gone", file=sys.stderr)
        sys.exit(1)
    sid = argv[argv.index("--session-id") + 1] if "--session-id" in argv else "session-new"
    def emit(**ev): print(json.dumps(ev), flush=True)
    emit(type="session", sessionId=sid, cwd=os.getcwd())
    emit(type="status", phase="turn_start", turn=1)
    emit(type="tool_call", callId="c1", tool="mcp__researchforge__search_papers", input={"query": "kv"})
    emit(type="tool_result", callId="c1", status="completed", result="{}")
    emit(type="tool_call", callId="c2", tool="mcp__researchforge__record_claim", input={})
    emit(type="tool_result", callId="c2", status="error", result="never retrieved")
    emit(type="text", text="Recorded the analysis.")
    emit(type="status", phase="step_end", turn=1, step=1, usage={"inputTokens": 100, "outputTokens": 20})
    emit(type="status", phase="turn_end", turn=1, reason={"kind": "completed"})
    emit(type="final", text="Recorded the analysis.")
    """
)


def _fake_dsh(tmp_path):
    script = tmp_path / "fake_dsh.py"
    script.write_text(FAKE_DSH)
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    return [sys.executable, str(script)]


def test_runtime_runs_phase_and_parses_events(ws, settings, tmp_path, monkeypatch):
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_DSH_LOG", str(log))
    rt = DshHeadlessRuntime(settings, command=_fake_dsh(tmp_path))
    events = []
    out = rt.run_phase(ws, "# phase prompt", phase="literature", session_id=None, on_event=lambda k, d: events.append((k, d)))
    assert out.ok and out.session_id == "session-new" and out.finish_reason == "completed"
    assert (out.tool_calls, out.failed_tool_calls) == (2, 1)
    assert out.usage == {"inputTokens": 100, "outputTokens": 20}
    assert out.final_text == "Recorded the analysis."
    call = json.loads(log.read_text().splitlines()[0])
    assert call["argv"][:4] == ["--profile", "headless", "--patch", str(ws.root / "dsh" / "overlay.yml")]
    assert call["argv"][-2:] == ["--json", "-"] and call["prompt"] == "# phase prompt"
    assert call["cwd"] == str(ws.root) and call["home"] == str(settings.dsh.resolved_home())
    kinds = [k for k, _ in events]
    assert kinds.count("tool_call") == 2 and ("tool_call", {"tool": "search_papers", "input": '{"query": "kv"}'}) in events
    assert any(k == "agent_text" for k in kinds)
    assert list(ws.root.glob("dsh/literature-*.jsonl"))


def test_runtime_resumes_session_and_falls_back_when_lost(ws, settings, tmp_path, monkeypatch):
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_DSH_LOG", str(log))
    rt = DshHeadlessRuntime(settings, command=_fake_dsh(tmp_path))
    events = []
    out = rt.run_phase(ws, "p", phase="gaps", session_id="session-abc", on_event=lambda k, d: events.append((k, d)))
    assert out.session_id == "session-abc"
    assert "--session-id" in json.loads(log.read_text().splitlines()[0])["argv"]
    out = rt.run_phase(ws, "p", phase="gaps", session_id="gone", on_event=lambda k, d: events.append((k, d)))
    assert out.ok and out.session_id == "session-new"
    assert any(k == "warning" and "could not resume" in d["message"] for k, d in events)


def test_runtime_reports_missing_launcher(ws, settings):
    rt = DshHeadlessRuntime(settings, command=["/nonexistent/dsh"])
    out = rt.run_phase(ws, "p", phase="formalize", session_id=None, on_event=lambda k, d: None)
    assert not out.ok and "launcher not found" in out.error
