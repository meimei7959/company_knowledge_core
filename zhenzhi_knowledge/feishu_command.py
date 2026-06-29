from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FeishuCommand:
    kind: str
    route: str
    event_type: str = ""
    incoming: dict[str, str] = field(default_factory=dict)
    decision: Any = None
    reason: str = ""


def build_message_command(incoming: dict[str, str], decision: Any | None = None) -> FeishuCommand:
    if not incoming.get("text", "").strip():
        return FeishuCommand("ignore_empty_message", "message", incoming=incoming, decision=decision, reason="empty_message")
    return FeishuCommand("process_message", "message", incoming=incoming, decision=decision)


def build_route_command(route_kind: str, event_type: str = "", reason: str = "") -> FeishuCommand:
    return FeishuCommand(route_kind, route_kind, event_type=event_type, reason=reason)
