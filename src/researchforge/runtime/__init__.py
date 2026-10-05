"""Agent runtimes: what executes one investigation phase.

The production runtime is :class:`researchforge.runtime.dsh.DshHeadlessRuntime`.
Tests use scripted runtimes that satisfy the same protocol.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from researchforge.workspace import Workspace

EventSink = Callable[[str, dict], object]


@dataclass
class RunOutcome:
    ok: bool
    session_id: str | None
    final_text: str = ""
    finish_reason: str | None = None
    exit_code: int | None = None
    tool_calls: int = 0
    failed_tool_calls: int = 0
    error: str | None = None
    usage: dict = field(default_factory=dict)
    duration_s: float = 0.0


class AgentRuntime(Protocol):
    name: str

    def run_phase(
        self,
        ws: Workspace,
        prompt: str,
        *,
        phase: str,
        session_id: str | None,
        on_event: EventSink,
    ) -> RunOutcome: ...
