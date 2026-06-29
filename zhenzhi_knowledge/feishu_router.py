from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FeishuRoute:
    kind: str
    event_type: str = ""
    reason: str = ""


def route_feishu_event(payload: dict[str, Any]) -> FeishuRoute:
    if "encrypt" in payload:
        return FeishuRoute("encrypted", reason="encrypted Feishu event")
    event_type = extract_event_type(payload)
    if is_url_verification(payload):
        return FeishuRoute("url_verification", event_type)
    if is_approval_event(payload, event_type):
        return FeishuRoute("approval", event_type)
    if is_card_action_event(event_type):
        return FeishuRoute("card_action", event_type)
    if event_type == "im.message.receive_v1":
        return FeishuRoute("message", event_type)
    return FeishuRoute("ignored", event_type or "unknown")


def extract_event_type(payload: dict[str, Any]) -> str:
    header = payload.get("header") or {}
    return str(header.get("event_type") or payload.get("type") or "")


def is_url_verification(payload: dict[str, Any]) -> bool:
    return bool(payload.get("challenge"))


def is_approval_event(payload: dict[str, Any], event_type: str) -> bool:
    if "approval" in event_type.lower():
        return True
    event = payload.get("event") or {}
    legacy_type = str(event.get("type") or payload.get("type") or "").lower()
    return "approval" in legacy_type or bool(deep_find(payload, "instance_code"))


def is_card_action_event(event_type: str) -> bool:
    lowered = event_type.lower()
    return lowered.startswith("card.action") or lowered.startswith("im.message.card")


def deep_find(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = deep_find(child, key)
            if found not in (None, ""):
                return found
    if isinstance(value, list):
        for child in value:
            found = deep_find(child, key)
            if found not in (None, ""):
                return found
    return None
