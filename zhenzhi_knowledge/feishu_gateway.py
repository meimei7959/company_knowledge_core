from __future__ import annotations

from typing import Any

from .core import Bundle, KnowledgeError
from .feishu_command import build_message_command, build_route_command
from .feishu_executor import execute_feishu_command
from .feishu_router import route_feishu_event


def handle_feishu_event(bundle: Bundle, payload: dict[str, Any], settings: Any | None = None) -> dict[str, Any]:
    from . import feishu_executor as impl

    settings = settings or impl.load_feishu_settings()
    route = route_feishu_event(payload)
    if route.kind == "encrypted":
        impl.create_feishu_reject_audit(bundle, payload, settings, route.reason)
        raise KnowledgeError("encrypted Feishu events are not supported yet; disable event encryption or add FEISHU_ENCRYPT_KEY support")
    if route.kind == "url_verification":
        try:
            impl.verify_event_token(payload, settings)
        except KnowledgeError as exc:
            impl.create_feishu_reject_audit(bundle, payload, settings, str(exc))
            raise
        return {"challenge": impl.extract_challenge(payload)}
    try:
        impl.verify_event_token(payload, settings)
    except KnowledgeError as exc:
        impl.create_feishu_reject_audit(bundle, payload, settings, str(exc))
        raise
    if route.kind == "message":
        incoming = impl.parse_message_event(payload)
        command = build_message_command(incoming)
        return execute_feishu_command(bundle, command, payload, settings)
    command = build_route_command(route.kind, route.event_type, route.reason)
    return execute_feishu_command(bundle, command, payload, settings)
