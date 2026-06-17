from __future__ import annotations

import hmac
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .core import Bundle, KnowledgeError, create_audit_log, ensure_dir, render_doc, search_retrieval, slug, unique_time_id, utc_now, write_text


FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
FORMAL_STATUSES = {"verified", "approved", "active"}


@dataclass(frozen=True)
class FeishuSettings:
    app_id: str
    app_secret: str
    verification_token: str
    reply_enabled: bool
    token_auto_approve: bool


def load_feishu_settings() -> FeishuSettings:
    return FeishuSettings(
        app_id=os.environ.get("FEISHU_APP_ID", "").strip(),
        app_secret=os.environ.get("FEISHU_APP_SECRET", "").strip(),
        verification_token=os.environ.get("FEISHU_VERIFICATION_TOKEN", "").strip(),
        reply_enabled=os.environ.get("FEISHU_REPLY_ENABLED", "true").lower() != "false",
        token_auto_approve=os.environ.get("FEISHU_TOKEN_AUTO_APPROVE", "false").lower() == "true",
    )


def handle_feishu_event(bundle: Bundle, payload: dict[str, Any], settings: FeishuSettings | None = None) -> dict[str, Any]:
    settings = settings or load_feishu_settings()
    if "encrypt" in payload:
        raise KnowledgeError("encrypted Feishu events are not supported yet; disable event encryption or add FEISHU_ENCRYPT_KEY support")
    if is_url_verification(payload):
        verify_event_token(payload, settings)
        return {"challenge": extract_challenge(payload)}
    verify_event_token(payload, settings)
    event_type = extract_event_type(payload)
    if event_type != "im.message.receive_v1":
        return {"ok": True, "ignored": event_type or "unknown"}
    incoming = parse_message_event(payload)
    if not incoming["text"].strip():
        return {"ok": True, "ignored": "empty_message"}
    reply = build_reply(bundle, incoming, settings)
    create_feishu_audit(bundle, incoming, reply)
    sent = False
    if settings.reply_enabled and settings.app_id and settings.app_secret:
        sent = send_feishu_reply(settings, incoming["messageId"], reply)
    return {"ok": True, "reply": reply, "sent": sent}


def is_url_verification(payload: dict[str, Any]) -> bool:
    if payload.get("type") == "url_verification":
        return True
    header = payload.get("header") or {}
    event = payload.get("event") or {}
    return header.get("event_type") == "url_verification" or event.get("type") == "url_verification"


def extract_challenge(payload: dict[str, Any]) -> str:
    event = payload.get("event") or {}
    return str(payload.get("challenge") or event.get("challenge") or "")


def extract_event_type(payload: dict[str, Any]) -> str:
    header = payload.get("header") or {}
    return str(header.get("event_type") or payload.get("type") or "")


def verify_event_token(payload: dict[str, Any], settings: FeishuSettings) -> None:
    expected = settings.verification_token
    if not expected:
        return
    header = payload.get("header") or {}
    event = payload.get("event") or {}
    supplied = str(header.get("token") or payload.get("token") or event.get("token") or "")
    if not hmac.compare_digest(supplied, expected):
        raise KnowledgeError("invalid Feishu verification token")


def parse_message_event(payload: dict[str, Any]) -> dict[str, str]:
    event = payload.get("event") or {}
    message = event.get("message") or {}
    sender = event.get("sender") or {}
    sender_id = sender.get("sender_id") or {}
    content = parse_message_content(message.get("content", ""))
    text = strip_bot_mentions(str(content.get("text", "")))
    return {
        "messageId": str(message.get("message_id") or ""),
        "chatId": str(message.get("chat_id") or ""),
        "chatType": str(message.get("chat_type") or ""),
        "messageType": str(message.get("message_type") or ""),
        "text": text,
        "openId": str(sender_id.get("open_id") or ""),
        "userId": str(sender_id.get("user_id") or ""),
        "unionId": str(sender_id.get("union_id") or ""),
    }


def parse_message_content(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        parsed = json.loads(str(raw))
    except json.JSONDecodeError:
        return {"text": str(raw)}
    return parsed if isinstance(parsed, dict) else {"text": str(parsed)}


def strip_bot_mentions(text: str) -> str:
    text = re.sub(r"@\S+\s*", "", text)
    text = re.sub(r"<at[^>]*>.*?</at>", "", text)
    return text.strip()


def build_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> str:
    text = incoming["text"].strip()
    lowered = text.lower()
    if lowered in {"/help", "help", "帮助", "/帮助"}:
        return help_text()
    if "token" in lowered or "令牌" in text or "申请知识工程" in text:
        return token_request_reply(incoming, settings)
    material = parse_project_material(text)
    if material:
        source_path, knowledge_path = create_project_material_drafts(bundle, incoming, material)
        return "\n".join(
            [
                "已保存为项目资料草稿，并生成待审核知识草稿。",
                f"项目: {material['projectId']}",
                f"原始资料: {source_path}",
                f"整理草稿: {knowledge_path}",
                "状态: draft",
                "审核通过前不会进入正式知识。",
            ]
        )
    intake = parse_intake(text)
    if intake:
        path = create_intake_draft(bundle, incoming, intake)
        return f"已生成待审核知识草稿：{path}\n状态: draft\n审核通过前不会进入正式知识。"
    chunks = [row for row in search_retrieval(bundle, text, limit=8) if row.get("status") in FORMAL_STATUSES]
    if not chunks:
        return "我没有在已审核知识里找到可靠答案。你可以换个关键词，或发送“沉淀：...”提交一条待审核知识。"
    lines = ["基于已审核知识，找到这些相关内容："]
    for idx, row in enumerate(chunks[:3], 1):
        snippet = compact_snippet(str(row.get("text", "")))
        lines.append(f"{idx}. {row.get('title') or row.get('path')} [{row.get('status')}]")
        lines.append(f"   来源: {row.get('sourceRef') or row.get('path')}")
        lines.append(f"   摘要: {snippet}")
    lines.append("需要沉淀新经验时，发送：沉淀：<内容>。")
    return "\n".join(lines)


def help_text() -> str:
    return "\n".join(
        [
            "桢知知识机器人可用命令：",
            "1. 直接提问：检索已审核知识并回复来源。",
            "2. 申请知识工程 token：识别申请人，进入审批流程。",
            "3. 沉淀：<内容>：提交待审核知识草稿。",
            "4. 资料：<项目ID>\\n<内容>：保存项目原始资料并生成整理草稿。",
            "5. 会议纪要：<项目ID>\\n<内容>：保存会议纪要并生成整理草稿。",
            "6. 帮助：查看命令。",
        ]
    )


def token_request_reply(incoming: dict[str, str], settings: FeishuSettings) -> str:
    if incoming.get("chatType") != "p2p":
        return "我识别到 token 申请。为避免泄露，请私聊我发送“申请知识工程 token”，我不会在群里发送 token。"
    if not settings.token_auto_approve:
        return "已收到你的知识工程 token 申请。我已记录你的飞书身份，负责人审批后会私发初始化命令。"
    token = os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN", "").strip()
    if not token:
        return "token 自动发放未完成：服务器没有配置 ZHENZHI_KNOWLEDGE_API_TOKEN。"
    return "\n".join(
        [
            "你的知识工程初始化命令：",
            "git clone https://github.com/meimei7959/company_knowledge_core.git",
            "cd company_knowledge_core",
            f"export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD={token}",
            "bash scripts/setup-teammate.sh --user-id <你的名字> --ai-tool codex",
        ]
    )


def parse_intake(text: str) -> str:
    for prefix in ["沉淀：", "沉淀:", "整理：", "整理:", "记录：", "记录:"]:
        if text.startswith(prefix):
            return text.removeprefix(prefix).strip()
    return ""


def create_intake_draft(bundle: Bundle, incoming: dict[str, str], content: str) -> str:
    if not content:
        raise KnowledgeError("empty intake content")
    if looks_like_secret(content):
        raise KnowledgeError("intake content looks like a secret; refusing to store it")
    draft_id = unique_time_id("feishu-intake")
    path = bundle.root / "knowledge" / "engineering" / f"{draft_id}.md"
    ensure_dir(path.parent)
    owner = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    frontmatter = {
        "type": "KnowledgeItem",
        "title": draft_id,
        "timestamp": utc_now(),
        "owner": owner,
        "status": "draft",
        "scope": "engineering",
        "sourceRef": f"feishu://message/{incoming.get('messageId')}",
        "confidence": "medium",
        "submittedBy": owner,
        "reviewStatus": "pending",
    }
    body = "\n".join(
        [
            "## Draft",
            "",
            content,
            "",
            "## Review Notes",
            "",
            "- Created from Feishu bot intake.",
            "- Human review required before verified status.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    return str(path.relative_to(bundle.root))


def parse_project_material(text: str) -> dict[str, str]:
    patterns = [
        r"^(?P<kind>资料|项目资料|会议纪要|会议记录|原始资料)[:：]\s*(?P<project>[A-Za-z0-9._\-\u4e00-\u9fff]+)\s*[\n，,：:]\s*(?P<body>.+)$",
        r"^(?P<project>[A-Za-z0-9._\-\u4e00-\u9fff]+)\s*(?P<kind>资料|项目资料|会议纪要|会议记录|原始资料)[:：]\s*(?P<body>.+)$",
        r"^(?P<project>[A-Za-z0-9._\-\u4e00-\u9fff]+项目).*(?P<kind>资料|会议纪要|会议记录|原始资料).*[。:：]\s*(?P<body>.+)$",
    ]
    normalized = text.strip()
    for pattern in patterns:
        match = re.match(pattern, normalized, re.DOTALL)
        if match:
            project_raw = match.group("project").strip()
            body = match.group("body").strip()
            if not body:
                return {}
            source_type = "meeting_notes" if "会议" in match.group("kind") else "project_material"
            return {"projectId": normalize_project_id(project_raw), "projectRaw": project_raw, "sourceType": source_type, "body": body}
    return {}


def normalize_project_id(project_raw: str) -> str:
    try:
        return slug(project_raw)
    except KnowledgeError:
        digest = hashlib.sha1(project_raw.encode("utf-8")).hexdigest()[:8]
        return f"project-{digest}"


def create_project_material_drafts(bundle: Bundle, incoming: dict[str, str], material: dict[str, str]) -> tuple[str, str]:
    content = material["body"]
    if looks_like_secret(content):
        raise KnowledgeError("material looks like it contains a secret; refusing to store it")
    owner = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    project_id = material["projectId"]
    source_id = unique_time_id("source")
    source_path = bundle.root / "projects" / project_id / "sources" / f"{source_id}.md"
    ensure_dir(source_path.parent)
    source_ref = f"feishu://message/{incoming.get('messageId')}"
    source_fm = {
        "type": "SourceMaterial",
        "title": source_id,
        "timestamp": utc_now(),
        "sourceId": source_id,
        "sourceType": material["sourceType"],
        "sourceRef": source_ref,
        "owner": owner,
        "status": "draft",
        "sensitivity": "internal",
        "projectId": project_id,
        "submittedBy": owner,
        "reviewStatus": "pending",
    }
    source_body = "\n".join(
        [
            "## Summary",
            "",
            compact_snippet(content, 240),
            "",
            "## Original Text",
            "",
            content,
            "",
            "## Handling Notes",
            "",
            "- Created from Feishu bot intake.",
            "- Treat as source material, not verified knowledge.",
        ]
    )
    write_text(source_path, render_doc(source_fm, source_body))

    knowledge_id = unique_time_id("feishu-material")
    knowledge_path = bundle.root / "knowledge" / "engineering" / f"{knowledge_id}.md"
    ensure_dir(knowledge_path.parent)
    knowledge_fm = {
        "type": "KnowledgeItem",
        "title": knowledge_id,
        "timestamp": utc_now(),
        "owner": owner,
        "status": "draft",
        "scope": "engineering",
        "projectId": project_id,
        "sourceRef": str(source_path.relative_to(bundle.root)),
        "confidence": "medium",
        "submittedBy": owner,
        "reviewStatus": "pending",
    }
    knowledge_body = "\n".join(
        [
            "## Draft Summary",
            "",
            compact_snippet(content, 500),
            "",
            "## Review Checklist",
            "",
            "- Confirm projectId is correct.",
            "- Extract decisions, risks, todos, and reusable lessons if needed.",
            "- Keep as draft until human review.",
        ]
    )
    write_text(knowledge_path, render_doc(knowledge_fm, knowledge_body))
    return str(source_path.relative_to(bundle.root)), str(knowledge_path.relative_to(bundle.root))


def looks_like_secret(text: str) -> bool:
    lowered = text.lower()
    secret_markers = ["token", "secret", "password", "api_key", "apikey", "密钥", "密码", "令牌"]
    return any(marker in lowered for marker in secret_markers)


def compact_snippet(text: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def create_feishu_audit(bundle: Bundle, incoming: dict[str, str], reply: str) -> None:
    actor = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    details = "\n".join(
        [
            f"messageId: {incoming.get('messageId')}",
            f"chatId: {incoming.get('chatId')}",
            f"chatType: {incoming.get('chatType')}",
            f"userId: {incoming.get('userId')}",
            f"openId: {incoming.get('openId')}",
            f"replyPreview: {compact_snippet(reply, 80)}",
        ]
    )
    create_audit_log(bundle, actor, "feishu.message.receive", incoming.get("messageId", ""), after="replied", policy_result="bot_gateway", details=details)


def send_feishu_reply(settings: FeishuSettings, message_id: str, text: str) -> bool:
    if not message_id:
        return False
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/im/v1/messages/{message_id}/reply"
    body = {
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    with urllib.request.urlopen(req, timeout=8) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code") != 0:
        raise KnowledgeError(f"Feishu reply failed: {result.get('msg') or result.get('code')}")
    return True


def get_tenant_access_token(settings: FeishuSettings) -> str:
    url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
    data = json.dumps({"app_id": settings.app_id, "app_secret": settings.app_secret}).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise KnowledgeError(f"Feishu token request failed: {exc}") from exc
    token = result.get("tenant_access_token", "")
    if not token:
        raise KnowledgeError(f"Feishu token request failed: {result.get('msg') or result.get('code')}")
    return str(token)
