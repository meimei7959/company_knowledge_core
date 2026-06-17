from __future__ import annotations

import hmac
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import (
    Bundle,
    KnowledgeError,
    create_audit_log,
    ensure_dir,
    list_review_queue,
    make_project,
    render_doc,
    review_path,
    search_retrieval,
    slug,
    unique_time_id,
    utc_now,
    write_text,
)


FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
FORMAL_STATUSES = {"verified", "approved", "active"}
APPROVAL_TYPE_AGENT_TOKEN = "agent_token"
APPROVAL_TYPE_PROJECT_INIT = "project_init"
APPROVAL_TYPE_KNOWLEDGE_INGEST = "knowledge_ingest"
DEFAULT_APPROVAL_WIDGETS = {
    "change_type": "widget17816810502430001",
    "project_name": "widget17816812084890001",
    "project_owner": "widget17816816166430001",
    "sub_type": "widget17816812747070001",
    "member": "widget17816813081730001",
    "description": "widget17816813651240001",
}
DEFAULT_CHANGE_TYPE_OPTIONS = {
    APPROVAL_TYPE_AGENT_TOKEN: "mqhqw8sk-3kt86yj7owt-0",
    APPROVAL_TYPE_PROJECT_INIT: "mqhqw8sk-x7hpdoqx0p-0",
    APPROVAL_TYPE_KNOWLEDGE_INGEST: "mqhqw8sk-kybdohz4afi-0",
}


@dataclass(frozen=True)
class FeishuSettings:
    app_id: str
    app_secret: str
    verification_token: str
    reply_enabled: bool
    token_auto_approve: bool
    approval_enabled: bool
    approval_code_project: str
    approval_code_common: str
    approval_code_security: str
    approval_node_approver_key: str
    common_reviewer_open_ids: list[str]
    security_reviewer_open_ids: list[str]
    project_reviewer_open_ids: dict[str, list[str]]
    token_send_on_approval: bool


def load_feishu_settings() -> FeishuSettings:
    return FeishuSettings(
        app_id=os.environ.get("FEISHU_APP_ID", "").strip(),
        app_secret=os.environ.get("FEISHU_APP_SECRET", "").strip(),
        verification_token=os.environ.get("FEISHU_VERIFICATION_TOKEN", "").strip(),
        reply_enabled=os.environ.get("FEISHU_REPLY_ENABLED", "true").lower() != "false",
        token_auto_approve=os.environ.get("FEISHU_TOKEN_AUTO_APPROVE", "false").lower() == "true",
        approval_enabled=os.environ.get("FEISHU_APPROVAL_ENABLED", "false").lower() == "true",
        approval_code_project=os.environ.get("FEISHU_APPROVAL_CODE_PROJECT", "").strip(),
        approval_code_common=os.environ.get("FEISHU_APPROVAL_CODE_COMMON", "").strip(),
        approval_code_security=os.environ.get("FEISHU_APPROVAL_CODE_SECURITY", "").strip(),
        approval_node_approver_key=os.environ.get("FEISHU_APPROVAL_NODE_APPROVER_KEY", "").strip(),
        common_reviewer_open_ids=split_open_ids(os.environ.get("FEISHU_COMMON_REVIEWER_OPEN_IDS", "")),
        security_reviewer_open_ids=split_open_ids(os.environ.get("FEISHU_SECURITY_REVIEWER_OPEN_IDS", "")),
        project_reviewer_open_ids=parse_project_reviewer_map(os.environ.get("FEISHU_PROJECT_REVIEWER_OPEN_IDS_JSON", "{}")),
        token_send_on_approval=os.environ.get("FEISHU_TOKEN_SEND_ON_APPROVAL", "false").lower() == "true",
    )


def split_open_ids(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_project_reviewer_map(raw: str) -> dict[str, list[str]]:
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    result: dict[str, list[str]] = {}
    for key, value in parsed.items():
        if isinstance(value, list):
            result[str(key)] = [str(item).strip() for item in value if str(item).strip()]
        elif isinstance(value, str):
            result[str(key)] = split_open_ids(value)
    return result


def handle_feishu_event(bundle: Bundle, payload: dict[str, Any], settings: FeishuSettings | None = None) -> dict[str, Any]:
    settings = settings or load_feishu_settings()
    if "encrypt" in payload:
        raise KnowledgeError("encrypted Feishu events are not supported yet; disable event encryption or add FEISHU_ENCRYPT_KEY support")
    if is_url_verification(payload):
        verify_event_token(payload, settings)
        return {"challenge": extract_challenge(payload)}
    verify_event_token(payload, settings)
    event_type = extract_event_type(payload)
    if is_approval_event(payload, event_type):
        return handle_approval_event(bundle, payload, settings)
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


def is_approval_event(payload: dict[str, Any], event_type: str) -> bool:
    if "approval" in event_type.lower():
        return True
    event = payload.get("event") or {}
    legacy_type = str(event.get("type") or payload.get("type") or "").lower()
    return "approval" in legacy_type or bool(deep_find(payload, "instance_code"))


def verify_event_token(payload: dict[str, Any], settings: FeishuSettings) -> None:
    expected = settings.verification_token
    if not expected:
        if os.environ.get("FEISHU_ALLOW_UNSIGNED_EVENTS", "false").lower() == "true":
            return
        raise KnowledgeError("missing Feishu verification token")
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
        "mentionedOpenIds": ",".join(extract_mentioned_open_ids(message, content)),
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


def extract_mentioned_open_ids(message: dict[str, Any], content: dict[str, Any]) -> list[str]:
    candidates: list[Any] = []
    for source in (message, content):
        mentions = source.get("mentions") if isinstance(source, dict) else None
        if isinstance(mentions, list):
            candidates.extend(mentions)
    result: list[str] = []
    for mention in candidates:
        if not isinstance(mention, dict):
            continue
        user_id = mention.get("id") or mention.get("user_id") or mention.get("userId") or {}
        if isinstance(user_id, dict):
            open_id = str(user_id.get("open_id") or "")
        else:
            open_id = str(mention.get("open_id") or "")
        if open_id and open_id not in result:
            result.append(open_id)
    return result


def build_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> str:
    text = incoming["text"].strip()
    lowered = text.lower()
    if lowered in {"/help", "help", "帮助", "/帮助"}:
        return help_text()
    review_reply = handle_review_command(bundle, incoming, text)
    if review_reply:
        return review_reply
    if "token" in lowered or "令牌" in text or "申请知识工程" in text:
        return token_request_reply(bundle, incoming, settings)
    project_intake = parse_project_init(text)
    if project_intake:
        return project_init_reply(bundle, incoming, settings, project_intake)
    material = parse_project_material(text)
    if material:
        source_path, knowledge_path = create_project_material_drafts(bundle, incoming, material)
        project_owner = project_owner_open_id(bundle, settings, material["projectId"])
        if not project_owner:
            return "\n".join(
                [
                    "已保存为项目资料草稿，并生成待审核知识草稿。",
                    f"项目: {material['projectId']}",
                    f"原始资料: {source_path}",
                    f"整理草稿: {knowledge_path}",
                    "状态: draft",
                    "审批未发起：这个项目还没有配置项目负责人 open_id，请先完成项目立项或配置 FEISHU_PROJECT_REVIEWER_OPEN_IDS_JSON。",
                ]
            )
        approval_line = trigger_approval_for_target(
            bundle,
            settings,
            incoming,
            approval_type=APPROVAL_TYPE_KNOWLEDGE_INGEST,
            target_ref=knowledge_path,
            requested_status="verified",
            project_id=material["projectId"],
            project_name=material["projectRaw"],
            owner_open_id=project_owner,
            summary=material["body"],
        )
        return "\n".join(
            [
                "已保存为项目资料草稿，并生成待审核知识草稿。",
                f"项目: {material['projectId']}",
                f"原始资料: {source_path}",
                f"整理草稿: {knowledge_path}",
                "状态: draft",
                approval_line,
            ]
        )
    intake = parse_intake(text)
    if intake:
        path = create_intake_draft(bundle, incoming, intake)
        approval_line = trigger_approval_for_target(
            bundle,
            settings,
            incoming,
            approval_type=APPROVAL_TYPE_KNOWLEDGE_INGEST,
            target_ref=path,
            requested_status="verified",
            project_id="",
            project_name="通用知识",
            owner_open_id=first_mentioned_open_id(incoming) or incoming.get("openId", ""),
            summary=intake,
        )
        return f"已生成待审核知识草稿：{path}\n状态: draft\n{approval_line}"
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
            "3. 立项申请：项目名称 <名称>，项目负责人 @负责人。",
            "4. 资料：<项目ID>\\n<内容>：保存项目原始资料并生成知识入库审批。",
            "5. 会议纪要：<项目ID>\\n<内容>：保存会议纪要并生成知识入库审批。",
            "6. 沉淀：<内容>：提交通用知识草稿。",
            "7. 审批会按 Agent Token、项目立项、知识入库三类自动发起飞书审批。",
            "8. 帮助：查看命令。",
        ]
    )


def token_request_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> str:
    if incoming.get("chatType") != "p2p":
        return "我识别到 token 申请。为避免泄露，请私聊我发送“申请知识工程 token”，我不会在群里发送 token。"
    approval_line = trigger_approval_for_target(
        bundle,
        settings,
        incoming,
        approval_type=APPROVAL_TYPE_AGENT_TOKEN,
        target_ref=f"token-request:{incoming.get('messageId')}",
        requested_status="approved",
        project_id="",
        project_name="Agent Token",
        owner_open_id=first_mentioned_open_id(incoming) or incoming.get("openId", ""),
        summary="知识工程 API Token 申请",
    )
    if not settings.token_auto_approve:
        return f"已收到你的知识工程 token 申请。我已记录你的飞书身份。\n{approval_line}"
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


def parse_project_init(text: str) -> dict[str, str]:
    normalized = text.strip()
    if not re.match(r"^(立项|项目立项|立项申请|创建项目)", normalized):
        return {}
    name = extract_named_value(normalized, ["项目名称", "项目名", "项目"])
    if not name:
        match = re.match(r"^(?:立项|项目立项|立项申请|创建项目)[:：\s]+(?P<name>[^\n，,。；;]+)", normalized)
        if match:
            name = match.group("name").strip()
    owner_name = extract_named_value(normalized, ["项目负责人", "负责人", "owner"])
    return {"projectName": name, "ownerName": owner_name}


def extract_named_value(text: str, labels: list[str]) -> str:
    for label in labels:
        pattern = rf"{re.escape(label)}\s*[:：]\s*(?P<value>[^\n，,。；;]+)"
        match = re.search(pattern, text)
        if match:
            return match.group("value").strip()
    return ""


def project_init_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, project_intake: dict[str, str]) -> str:
    project_name = project_intake.get("projectName", "").strip()
    owner_open_id = first_mentioned_open_id(incoming) or incoming.get("openId", "")
    if not project_name:
        return "立项申请还缺项目名称。请发送：立项申请：项目名称 <名称>，项目负责人 @负责人。"
    if not owner_open_id:
        return "立项申请还缺项目负责人。请在消息里 @项目负责人，或让负责人本人发起立项。"
    project_id = normalize_project_id(project_name)
    project_path = make_project(bundle, project_id, project_name, owner_open_id)
    approval_line = trigger_approval_for_target(
        bundle,
        settings,
        incoming,
        approval_type=APPROVAL_TYPE_PROJECT_INIT,
        target_ref=str(project_path.relative_to(bundle.root)),
        requested_status="verified",
        project_id=project_id,
        project_name=project_name,
        owner_open_id=owner_open_id,
        summary=f"项目立项申请：{project_name}",
    )
    return "\n".join(
        [
            "已生成项目立项草稿。",
            f"项目: {project_name}",
            f"项目ID: {project_id}",
            f"项目负责人: {owner_open_id}",
            f"项目卡: {project_path.relative_to(bundle.root)}",
            "状态: draft",
            approval_line,
        ]
    )


def handle_review_command(bundle: Bundle, incoming: dict[str, str], text: str) -> str:
    stripped = text.strip()
    if stripped in {"待审核", "/待审核", "review list", "/review list"}:
        return render_review_queue(bundle)
    approve_target = parse_target_command(stripped, ["通过", "审核通过", "approve", "/approve"])
    if approve_target:
        return review_target_from_feishu(bundle, incoming, approve_target, "")
    reject_target = parse_target_command(stripped, ["驳回", "拒绝", "reject", "/reject"])
    if reject_target:
        return review_target_from_feishu(bundle, incoming, reject_target, "rejected")
    return ""


def render_review_queue(bundle: Bundle) -> str:
    queue = list_review_queue(bundle)
    if not queue:
        return "当前没有待审核对象。"
    lines = ["待审核队列："]
    for idx, item in enumerate(queue[:10], 1):
        lines.append(f"{idx}. {item['path']}")
        lines.append(f"   {item['type']} / {item['status']} / owner={item['owner'] or 'unknown'}")
    if len(queue) > 10:
        lines.append(f"还有 {len(queue) - 10} 条未显示。")
    lines.append("审核命令：通过 <对象路径>；驳回 <对象路径>。")
    return "\n".join(lines)


def parse_target_command(text: str, prefixes: list[str]) -> str:
    for prefix in prefixes:
        if text == prefix:
            return ""
        if text.startswith(prefix + " "):
            return text[len(prefix) :].strip()
        if text.startswith(prefix + "："):
            return text[len(prefix) + 1 :].strip()
        if text.startswith(prefix + ":"):
            return text[len(prefix) + 1 :].strip()
    return ""


def review_target_from_feishu(bundle: Bundle, incoming: dict[str, str], target: str, explicit_status: str) -> str:
    target = target.strip()
    if not target:
        return "请带上对象路径，例如：通过 knowledge/engineering/xxx.md"
    status = explicit_status or next_review_status(bundle, target)
    reviewer = incoming.get("openId") or incoming.get("userId") or "feishu-reviewer"
    audit_path = review_path(bundle, Path(target), status, reviewer)
    return "\n".join(
        [
            "审核已处理。",
            f"对象: {target}",
            f"状态: {status}",
            f"审核人: {reviewer}",
            f"审计: {audit_path.relative_to(bundle.root)}",
        ]
    )


def next_review_status(bundle: Bundle, target: str) -> str:
    path = bundle.root / target
    if not path.exists():
        raise KnowledgeError(f"target not found: {target}")
    text = path.read_text(encoding="utf-8")
    frontmatter: dict[str, str] = {}
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip().strip('"')
    object_type = frontmatter.get("type", "")
    status = frontmatter.get("status", "")
    if status == "testing" or object_type == "ToolAsset":
        return "approved"
    if status == "open":
        return "resolved"
    if status == "stale_candidate":
        return "stale"
    return "verified"


def trigger_approval_for_target(
    bundle: Bundle,
    settings: FeishuSettings,
    incoming: dict[str, str],
    approval_type: str,
    target_ref: str,
    requested_status: str,
    project_id: str,
    project_name: str,
    owner_open_id: str,
    summary: str,
) -> str:
    if not settings.approval_enabled:
        return "审批未启用：已保留为 draft，等待审批模板配置。"
    approval_code = approval_code_for_type(settings, approval_type)
    if not approval_code:
        return f"审批模板未配置：缺少 {approval_type} 类 approval_code，已保留为 draft。"
    requester = incoming.get("openId") or incoming.get("userId")
    if not requester:
        return "审批未发起：无法识别提交人飞书身份。"
    reviewers = reviewers_for(settings, approval_type, project_id)
    if not reviewers and approval_type == APPROVAL_TYPE_KNOWLEDGE_INGEST and owner_open_id:
        reviewers = [owner_open_id]
    instance_code = create_feishu_approval_instance(
        settings,
        requester_open_id=requester,
        approval_code=approval_code,
        approver_open_ids=reviewers,
        form_values={
            "approval_type": approval_type,
            "object_path": target_ref,
            "project_id": project_id,
            "project_name": project_name,
            "owner_open_id": owner_open_id or requester,
            "requested_status": requested_status,
            "submitter": requester,
            "summary": compact_snippet(summary, 500),
        },
    )
    save_approval_request(
        bundle,
        instance_code,
        {
            "instanceCode": instance_code,
            "approvalCode": approval_code,
            "approvalType": approval_type,
            "targetRef": target_ref,
            "requestedStatus": requested_status,
            "projectId": project_id,
            "projectName": project_name,
            "ownerOpenId": owner_open_id or requester,
            "submitterOpenId": requester,
            "chatId": incoming.get("chatId", ""),
            "messageId": incoming.get("messageId", ""),
        },
    )
    create_audit_log(bundle, requester, "feishu.approval.create", target_ref, after="pending", policy_result=approval_type, details=f"instanceCode: {instance_code}")
    return f"已发起飞书审批：{instance_code}"


def approval_code_for_type(settings: FeishuSettings, approval_type: str) -> str:
    if approval_type in {APPROVAL_TYPE_PROJECT_INIT, APPROVAL_TYPE_KNOWLEDGE_INGEST}:
        return settings.approval_code_project or settings.approval_code_common
    if approval_type == "security":
        return settings.approval_code_security or settings.approval_code_common
    return settings.approval_code_common


def reviewers_for(settings: FeishuSettings, approval_type: str, project_id: str) -> list[str]:
    if approval_type == APPROVAL_TYPE_KNOWLEDGE_INGEST:
        return settings.project_reviewer_open_ids.get(project_id, []) or settings.common_reviewer_open_ids
    if approval_type == "security":
        return settings.security_reviewer_open_ids or settings.common_reviewer_open_ids
    return settings.common_reviewer_open_ids


def first_project_reviewer(settings: FeishuSettings, project_id: str) -> str:
    reviewers = settings.project_reviewer_open_ids.get(project_id, [])
    return reviewers[0] if reviewers else ""


def project_owner_open_id(bundle: Bundle, settings: FeishuSettings, project_id: str) -> str:
    reviewer = first_project_reviewer(settings, project_id)
    if reviewer:
        return reviewer
    project_path = bundle.root / "projects" / slug(project_id) / "project.md"
    if not project_path.exists():
        return ""
    owner = frontmatter_value(project_path, "owner")
    return owner if owner.startswith("ou_") else ""


def frontmatter_value(path: Path, key: str) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    for line in parts[1].splitlines():
        if line.startswith(key + ":"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""


def first_mentioned_open_id(incoming: dict[str, str]) -> str:
    mentioned = incoming.get("mentionedOpenIds", "")
    return split_open_ids(mentioned)[0] if mentioned else ""


def create_feishu_approval_instance(
    settings: FeishuSettings,
    requester_open_id: str,
    approval_code: str,
    approver_open_ids: list[str],
    form_values: dict[str, str],
) -> str:
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/approval/v4/instances?user_id_type=open_id"
    body: dict[str, Any] = {
        "approval_code": approval_code,
        "open_id": requester_open_id,
        "form": json.dumps(approval_form(form_values), ensure_ascii=False),
        "uuid": unique_time_id("approval-request"),
    }
    if settings.approval_node_approver_key and approver_open_ids:
        body["node_approver_open_id_list"] = [{"key": settings.approval_node_approver_key, "value": approver_open_ids}]
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code") != 0:
        raise KnowledgeError(f"Feishu approval create failed: {result.get('msg') or result.get('code')}")
    data_obj = result.get("data") or {}
    instance_code = str(data_obj.get("instance_code") or data_obj.get("instanceCode") or "")
    if not instance_code:
        raise KnowledgeError("Feishu approval create failed: missing instance_code")
    return instance_code


def approval_form(values: dict[str, str]) -> list[dict[str, str]]:
    approval_type = values.get("approval_type", "")
    fields: list[dict[str, Any]] = [
        {
            "id": approval_widget_id("change_type"),
            "type": "radioV2",
            "value": approval_change_type_value(approval_type),
        },
        {
            "id": approval_widget_id("project_name"),
            "type": "input",
            "value": values.get("project_name") or values.get("project_id") or "-",
        },
        {
            "id": approval_widget_id("member"),
            "type": "contact",
            "value": [values.get("submitter", "")],
        },
        {
            "id": approval_widget_id("description"),
            "type": "document",
            "value": approval_description(values),
        },
    ]
    owner_open_id = values.get("owner_open_id", "")
    if owner_open_id:
        fields.append({"id": approval_widget_id("project_owner"), "type": "contact", "value": [owner_open_id]})
    sub_type = os.environ.get("FEISHU_APPROVAL_SUB_TYPE_DEFAULT_VALUE", "").strip()
    if sub_type:
        fields.append({"id": approval_widget_id("sub_type"), "type": "radioV2", "value": sub_type})
    return [field for field in fields if field.get("id") and field.get("value") not in ("", [])]


def approval_widget_id(name: str) -> str:
    env_name = f"FEISHU_APPROVAL_WIDGET_{name.upper()}"
    return os.environ.get(env_name, DEFAULT_APPROVAL_WIDGETS.get(name, "")).strip()


def approval_change_type_value(approval_type: str) -> str:
    env_name = f"FEISHU_APPROVAL_TYPE_VALUE_{approval_type.upper()}"
    return os.environ.get(env_name, DEFAULT_CHANGE_TYPE_OPTIONS.get(approval_type, "")).strip()


def approval_description(values: dict[str, str]) -> str:
    parts = [
        f"对象: {values.get('object_path', '')}",
        f"审批类型: {values.get('approval_type', '')}",
        f"项目ID: {values.get('project_id', '') or '-'}",
        f"目标状态: {values.get('requested_status', '')}",
        f"提交人: {values.get('submitter', '')}",
        "",
        values.get("summary", ""),
    ]
    return "\n".join(parts).strip()


def approval_request_dir(bundle: Bundle) -> Path:
    path = bundle.zz_dir / "approval-requests"
    ensure_dir(path)
    return path


def save_approval_request(bundle: Bundle, instance_code: str, data: dict[str, str]) -> None:
    path = approval_request_dir(bundle) / f"{slug(instance_code)}.json"
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def load_approval_request(bundle: Bundle, instance_code: str) -> dict[str, str]:
    path = approval_request_dir(bundle) / f"{slug(instance_code)}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def handle_approval_event(bundle: Bundle, payload: dict[str, Any], settings: FeishuSettings) -> dict[str, Any]:
    instance_code = str(deep_find(payload, "instance_code") or deep_find(payload, "instanceCode") or "")
    approval_code = str(deep_find(payload, "approval_code") or deep_find(payload, "approvalCode") or "")
    status = str(deep_find(payload, "status") or deep_find(payload, "approval_status") or "").upper()
    if not instance_code:
        return {"ok": True, "ignored": "approval_event_without_instance_code"}
    request = load_approval_request(bundle, instance_code)
    if not request:
        return {"ok": True, "ignored": "unknown_approval_instance", "instanceCode": instance_code}
    expected_code = request.get("approvalCode", "")
    if expected_code and approval_code and approval_code != expected_code:
        raise KnowledgeError("approval callback approval_code mismatch")
    final_status = request.get("finalStatus", "")
    if final_status:
        return {"ok": True, "idempotent": True, "instanceCode": instance_code, "targetRef": request.get("targetRef", ""), "status": final_status}
    reviewer = str(deep_find(payload, "open_id") or deep_find(payload, "operator_id") or "feishu-approval")
    target_ref = request.get("targetRef", "")
    approved = status in {"2", "APPROVED", "PASS", "AGREE", "APPROVE", "APPROVAL_APPROVED"}
    rejected = status in {"3", "4", "5", "REJECTED", "REJECT", "REFUSED", "DENIED", "CANCELED", "CANCELLED"}
    if not approved and not rejected:
        return {"ok": True, "ignored": "approval_status_not_final", "status": status, "instanceCode": instance_code}
    if target_ref.startswith("token-request:"):
        result = handle_token_approval_result(bundle, settings, request, reviewer, approved, instance_code)
        request["finalStatus"] = result["status"]
        save_approval_request(bundle, instance_code, request)
        return result
    new_status = request.get("requestedStatus", "verified") if approved else "rejected"
    audit_path = review_path(bundle, Path(target_ref), new_status, reviewer)
    create_audit_log(bundle, reviewer, "feishu.approval.callback", target_ref, after=new_status, policy_result=request.get("approvalType", ""), details=f"instanceCode: {instance_code}\nstatus: {status}")
    request["finalStatus"] = new_status
    save_approval_request(bundle, instance_code, request)
    return {"ok": True, "instanceCode": instance_code, "targetRef": target_ref, "status": new_status, "auditRef": str(audit_path.relative_to(bundle.root))}


def handle_token_approval_result(bundle: Bundle, settings: FeishuSettings, request: dict[str, str], reviewer: str, approved: bool, instance_code: str) -> dict[str, Any]:
    submitter = request.get("submitterOpenId", "")
    if approved and settings.token_send_on_approval and submitter:
        token = os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN", "").strip()
        if token:
            send_feishu_message(
                settings,
                submitter,
                "\n".join(
                    [
                        "你的知识工程 token 申请已通过。",
                        "初始化命令：",
                        "git clone https://github.com/meimei7959/company_knowledge_core.git",
                        "cd company_knowledge_core",
                        f"export ZHENZHI_KNOWLEDGE_API_TOKEN_PROD={token}",
                        "bash scripts/setup-teammate.sh --user-id <你的名字> --ai-tool codex",
                    ]
                ),
            )
    elif not approved and submitter:
        send_feishu_message(settings, submitter, "你的知识工程 token 申请未通过。")
    result = "approved" if approved else "rejected"
    create_audit_log(bundle, reviewer, "feishu.token.approval", request.get("targetRef", ""), after=result, policy_result=APPROVAL_TYPE_AGENT_TOKEN, details=f"instanceCode: {instance_code}")
    return {"ok": True, "instanceCode": instance_code, "targetRef": request.get("targetRef", ""), "status": result}


def deep_find(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = deep_find(child, key)
            if found not in (None, ""):
                return found
    elif isinstance(value, list):
        for item in value:
            found = deep_find(item, key)
            if found not in (None, ""):
                return found
    return None


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


def send_feishu_message(settings: FeishuSettings, open_id: str, text: str) -> bool:
    if not open_id:
        return False
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/im/v1/messages?receive_id_type=open_id"
    body = {
        "receive_id": open_id,
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
        raise KnowledgeError(f"Feishu message send failed: {result.get('msg') or result.get('code')}")
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
