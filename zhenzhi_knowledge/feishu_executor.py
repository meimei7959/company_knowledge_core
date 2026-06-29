from __future__ import annotations

from typing import Any, TYPE_CHECKING
import urllib.error

from .core import Bundle, KnowledgeError, create_audit_log
from .feishu_command import FeishuCommand

if TYPE_CHECKING:
    from .feishu import FeishuSettings


def execute_feishu_command(bundle: Bundle, command: FeishuCommand, payload: dict[str, Any], settings: "FeishuSettings") -> dict[str, Any]:
    from . import feishu as legacy

    if command.kind == "approval":
        return legacy.handle_approval_event(bundle, payload, settings)
    if command.kind == "card_action":
        return legacy.handle_card_action_event(bundle, payload, settings)
    if command.kind == "ignored":
        return {"ok": True, "ignored": command.event_type or "unknown"}
    if command.kind == "ignore_empty_message":
        return {"ok": True, "ignored": "empty_message"}
    if command.kind == "process_message":
        return execute_message_command(bundle, command.incoming, settings)
    raise KnowledgeError(f"unsupported Feishu command: {command.kind}")


def execute_message_command(bundle: Bundle, incoming: dict[str, str], settings: "FeishuSettings") -> dict[str, Any]:
    from . import feishu as legacy

    duplicate = legacy.claim_feishu_message_event(bundle, incoming)
    if duplicate:
        return {
            "ok": True,
            "duplicate": True,
            "messageId": incoming.get("messageId", ""),
            "status": duplicate.get("status", "processing"),
            "sent": False,
        }
    try:
        response = legacy.build_feishu_response(bundle, incoming, settings)
        reply = str(response.get("reply", ""))
        legacy.create_feishu_audit(bundle, incoming, reply)
    except Exception as exc:
        legacy.fail_feishu_message_event(bundle, incoming, exc)
        raise
    sent = False
    reply_error = ""
    if settings.reply_enabled and settings.app_id and settings.app_secret:
        try:
            sent = legacy.send_feishu_incoming_response(settings, incoming, response)
        except urllib.error.HTTPError as exc:
            reply_error = legacy.feishu_http_error_detail(exc)
            error_info = legacy.classify_feishu_delivery_error(reply_error)
            if response.get("msg_type") == "interactive":
                try:
                    fallback_reply = "\n".join(
                        [
                            reply,
                            "",
                            "卡片暂时发送失败，我先用文字方式继续：",
                            legacy.build_reply(bundle, incoming, settings),
                        ]
                    )
                    sent = legacy.send_feishu_response(settings, incoming["messageId"], {"msg_type": "text", "reply": fallback_reply})
                    reply_error = f"{reply_error}\nfallbackTextSent: true"
                except Exception as fallback_exc:
                    reply_error = f"{reply_error}\nfallbackTextError: {fallback_exc}"
            create_audit_log(bundle, incoming.get("openId") or incoming.get("userId") or "feishu-user", "feishu.reply.failed", incoming.get("messageId", ""), after="failed", policy_result="bot_gateway", details=reply_error)
            notification_ref = legacy.create_feishu_permission_notification(bundle, incoming, error_info, reply_error)
            legacy.record_feishu_delivery_attempt(
                incoming.get("messageId", ""),
                "reply",
                "failed",
                event_id=incoming.get("messageId", ""),
                response_code=str(exc.code),
                error_class=str(error_info.get("errorClass") or ""),
                summary=reply_error + (f"\nnotificationRef={notification_ref}" if notification_ref else ""),
            )
        except (KnowledgeError, urllib.error.URLError) as exc:
            reply_error = str(exc)
            error_info = legacy.classify_feishu_delivery_error(reply_error)
            create_audit_log(bundle, incoming.get("openId") or incoming.get("userId") or "feishu-user", "feishu.reply.failed", incoming.get("messageId", ""), after="failed", policy_result="bot_gateway", details=reply_error)
            notification_ref = legacy.create_feishu_permission_notification(bundle, incoming, error_info, reply_error)
            legacy.record_feishu_delivery_attempt(
                incoming.get("messageId", ""),
                "reply",
                "failed",
                event_id=incoming.get("messageId", ""),
                error_class=str(error_info.get("errorClass") or ""),
                summary=reply_error + (f"\nnotificationRef={notification_ref}" if notification_ref else ""),
            )
    result: dict[str, Any] = {"ok": True, "reply": reply, "sent": sent, "msgType": response.get("msg_type", "text")}
    if response.get("card"):
        result["card"] = response["card"]
    if reply_error:
        result["replyError"] = reply_error
    legacy.complete_feishu_message_event(bundle, incoming, reply, sent, reply_error)
    legacy.update_knowledge_query_delivery(bundle, incoming, sent, reply_error)
    return result
