from __future__ import annotations

import hmac
import hashlib
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import (
    Bundle,
    KnowledgeError,
    accept_project_task_result,
    as_list,
    capability_feature_flags,
    create_access_credential_request,
    create_audit_log,
    create_discussion_session,
    create_project_task,
    create_source_material,
    create_task_notification,
    ensure_dir,
    ensure_default_project_agents,
    ensure_project_initialization_task,
    find_project_task,
    finish_project_task,
    list_review_queue,
    load_object,
    make_project,
    make_skill,
    make_tool,
    needs_product_manager_agent,
    parse_frontmatter,
    publish_knowledge_bundle,
    product_manager_agent_decision,
    render_doc,
    review_path,
    search_audit_logs,
    search_retrieval,
    set_project_task_status,
    slug,
    finalize_discussion_session,
    submit_discussion_turn,
    update_frontmatter_file,
    unique_time_id,
    utc_now,
    write_text,
)
from .operational_store import (
    record_feishu_delivery_attempt,
    record_operational_event,
)


FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
FORMAL_STATUSES = {"verified", "approved", "active"}
REVIEWABLE_REFERENCE_STATUSES = {"draft", "observed", "reviewing", "pending"}
SOURCE_REFERENCE_STATUSES = {"stored"}
SEARCH_ANSWER_TYPES = {"KnowledgeItem", "SourceMaterial", "Decision", "Policy", "Workflow", "ToolAsset", "SkillAsset", "Agent", "Project"}
GLOBAL_KNOWLEDGE_PROJECT_IDS = {"company-knowledge-core"}
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

PROJECT_GROUP_OPTIONS = [
    ("后续确认", "later"),
    ("需要创建或绑定项目群", "create_or_bind"),
    ("暂不需要项目群", "none"),
]

URL_PATTERN = re.compile(r"https?://[^\s，,。；;）)】\\>]+")
RESEARCH_INTAKE_PREFIXES = (
    "研究一下",
    "研究下",
    "看一下",
    "看看",
    "分析一下",
    "分析下",
    "参考一下",
    "相关的",
    "相关资料",
    "学习一下",
)
SYSTEM_CHANGE_KEYWORDS = (
    "改一下skill",
    "改 skill",
    "修改skill",
    "修改 skill",
    "更新skill",
    "更新 skill",
    "新增skill",
    "新增 skill",
    "融入体系",
    "改一下流程",
    "更新流程",
    "修改流程",
    "改工作流",
    "更新工作流",
    "修改工作流",
    "改agents",
    "改 agents",
    "更新agents",
    "更新 agents",
    "改规则",
    "更新规则",
    "修改规则",
)

MATERIAL_FOLLOWUP_KEYWORDS = (
    "进入能力候选复核",
    "加入能力候选",
    "加入候选材料",
    "加入候选",
    "加到候选",
    "转成能力候选",
    "生成能力候选",
    "继续复核",
    "继续处理",
    "继续分析",
    "加大后选材料",
    "加大候选材料",
)

MATERIAL_STATUS_FOLLOWUP_KEYWORDS = (
    "结果",
    "结果呢",
    "怎么没有结果",
    "没有结果",
    "整理结果",
    "分析结果",
    "处理结果",
    "整理完了吗",
    "分析完了吗",
    "处理完了吗",
    "完成了吗",
    "好了没",
    "进度",
    "状态",
    "现在怎么样",
    "怎么样了",
    "有用吗",
    "有没有用",
    "有没有作用",
    "有什么用",
    "价值",
    "建议怎么做",
)


def agent_ring_enabled() -> bool:
    return os.environ.get("AGENT_RING_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}


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
    approval_doc_folder_token: str
    approval_doc_folder_tokens: dict[str, str]
    approval_doc_domain: str
    approval_doc_share_names: list[str]
    user_open_id_map: dict[str, str]


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
        approval_doc_folder_token=os.environ.get("FEISHU_APPROVAL_DOC_FOLDER_TOKEN", "").strip(),
        approval_doc_folder_tokens=parse_string_map(os.environ.get("FEISHU_APPROVAL_DOC_FOLDER_TOKENS_JSON", "{}")),
        approval_doc_domain=os.environ.get("FEISHU_APPROVAL_DOC_DOMAIN", "https://xcn68awb7dsi.feishu.cn").strip().rstrip("/"),
        approval_doc_share_names=split_open_ids(os.environ.get("FEISHU_APPROVAL_DOC_SHARE_NAMES", "梅晓华")),
        user_open_id_map=parse_user_open_id_map(os.environ.get("FEISHU_USER_OPEN_ID_MAP_JSON", "{}")),
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


def parse_user_open_id_map(raw: str) -> dict[str, str]:
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {normalize_person_name(str(key)): str(value).strip() for key, value in parsed.items() if str(value).strip()}


def parse_string_map(raw: str) -> dict[str, str]:
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(key).strip(): str(value).strip() for key, value in parsed.items() if str(key).strip() and str(value).strip()}


def handle_feishu_event(bundle: Bundle, payload: dict[str, Any], settings: FeishuSettings | None = None) -> dict[str, Any]:
    from .feishu_gateway import handle_feishu_event as gateway_handle_feishu_event

    return gateway_handle_feishu_event(bundle, payload, settings)


def feishu_message_event_dir(bundle: Bundle) -> Path:
    path = bundle.zz_dir / "feishu-message-events"
    ensure_dir(path)
    return path


def feishu_message_event_path(bundle: Bundle, message_id: str) -> Path:
    return feishu_message_event_dir(bundle) / f"{slug(message_id)}.json"


def load_feishu_message_event(bundle: Bundle, message_id: str) -> dict[str, Any]:
    if not message_id:
        return {}
    path = feishu_message_event_path(bundle, message_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"messageId": message_id, "status": "corrupt"}


def claim_feishu_message_event(bundle: Bundle, incoming: dict[str, str]) -> dict[str, Any]:
    message_id = incoming.get("messageId", "")
    if not message_id:
        return {}
    path = feishu_message_event_path(bundle, message_id)
    if not path.exists() and legacy_feishu_message_processed(bundle, message_id):
        legacy = {
            "messageId": message_id,
            "status": "completed_legacy",
            "createdAt": utc_now(),
            "lastDuplicateAt": utc_now(),
            "duplicateCount": 1,
            "source": "audit_log",
        }
        write_text(path, json.dumps(legacy, ensure_ascii=False, indent=2) + "\n")
        return legacy
    record: dict[str, Any] = {
        "messageId": message_id,
        "status": "processing",
        "createdAt": utc_now(),
        "chatId": incoming.get("chatId", ""),
        "chatType": incoming.get("chatType", ""),
        "openId": incoming.get("openId", ""),
        "userId": incoming.get("userId", ""),
        "textHash": hashlib.sha256(incoming.get("text", "").encode("utf-8")).hexdigest(),
        "duplicateCount": 0,
    }
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        record_operational_event(
            message_id,
            "feishu",
            "processing",
            actor_ref=incoming.get("openId") or incoming.get("userId") or "feishu-user",
            target_ref=f"feishu://message/{message_id}",
            idempotency_key=message_id,
            summary="Feishu message callback accepted and reserved for processing.",
        )
        return {}
    except FileExistsError:
        existing = load_feishu_message_event(bundle, message_id)
        try:
            existing["duplicateCount"] = int(existing.get("duplicateCount", 0)) + 1
        except (TypeError, ValueError):
            existing["duplicateCount"] = 1
        existing["lastDuplicateAt"] = utc_now()
        write_text(path, json.dumps(existing, ensure_ascii=False, indent=2) + "\n")
        record_operational_event(
            message_id,
            "feishu",
            "duplicate",
            actor_ref=incoming.get("openId") or incoming.get("userId") or "feishu-user",
            target_ref=f"feishu://message/{message_id}",
            idempotency_key=message_id,
            summary=f"Duplicate Feishu message callback suppressed. duplicateCount={existing.get('duplicateCount', 1)}",
        )
        return existing


def legacy_feishu_message_processed(bundle: Bundle, message_id: str) -> bool:
    if not message_id:
        return False
    return any(row.get("action") == "feishu.message.receive" for row in search_audit_logs(bundle, target=message_id))


def complete_feishu_message_event(bundle: Bundle, incoming: dict[str, str], reply: str, sent: bool, reply_error: str) -> None:
    message_id = incoming.get("messageId", "")
    if not message_id:
        return
    path = feishu_message_event_path(bundle, message_id)
    record = load_feishu_message_event(bundle, message_id) or {"messageId": message_id, "createdAt": utc_now()}
    record.update(
        {
            "status": "completed",
            "completedAt": utc_now(),
            "reply": reply,
            "replyHash": hashlib.sha256(reply.encode("utf-8")).hexdigest(),
            "sent": bool(sent),
            "replyError": reply_error,
        }
    )
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    status = "sent" if sent else ("failed" if reply_error else "not_sent")
    error_info = classify_feishu_delivery_error(reply_error) if reply_error else {"errorClass": ""}
    record_operational_event(
        message_id,
        "feishu",
        "completed",
        actor_ref=incoming.get("openId") or incoming.get("userId") or "feishu-user",
        target_ref=f"feishu://message/{message_id}",
        idempotency_key=message_id,
        error_class=str(error_info.get("errorClass") or ""),
        summary="Feishu message callback completed with delivery status: " + status,
    )
    record_feishu_delivery_attempt(
        message_id,
        "reply",
        status,
        event_id=message_id,
        response_code="ok" if sent else "",
        error_class=str(error_info.get("errorClass") or ""),
        summary=reply_error or "Feishu delivery completed.",
    )


def task_status_notification_text(status: str, task_id: str, executor_label: str, detail: str = "") -> str:
    normalized = status.strip().lower()
    if normalized in {"processing", "started", "parsing"}:
        lines = [f"{executor_label} 已开始解析资料。", f"任务编号：{task_id}"]
    elif normalized in {"indexing", "chunking", "vector_indexing"}:
        lines = [f"{executor_label} 正在切片入库资料。", f"任务编号：{task_id}"]
    elif normalized in {"completed", "done", "finished"}:
        lines = ["资料已整理完成。", f"任务编号：{task_id}"]
    elif normalized in {"failed", "blocked"}:
        lines = ["资料处理遇到问题，已记录等待处理。", f"任务编号：{task_id}"]
    else:
        lines = [f"资料处理状态已更新：{status or '处理中'}。", f"任务编号：{task_id}"]
    if detail.strip():
        lines.append(detail.strip())
    return "\n".join(lines)


def task_source_message_id(bundle: Bundle, task: dict[str, Any]) -> str:
    direct = str(task.get("feishuMessageId") or "").strip()
    if direct:
        return direct
    refs = task.get("sourceMaterialRefs") or []
    if isinstance(refs, str):
        refs = [refs]
    for ref in refs:
        source_path = bundle.root / str(ref)
        if not source_path.exists():
            continue
        try:
            source = load_object(source_path)
        except Exception:
            continue
        source_ref = str(source.get("sourceRef") or "").strip()
        if source_ref.startswith("feishu://message/"):
            return source_ref.rsplit("/", 1)[-1]
    return ""


def feishu_incoming_from_event(record: dict[str, Any]) -> dict[str, str]:
    return {
        "messageId": str(record.get("messageId") or ""),
        "chatId": str(record.get("chatId") or ""),
        "chatType": str(record.get("chatType") or ""),
        "openId": str(record.get("openId") or ""),
        "userId": str(record.get("userId") or ""),
        "text": "",
        "messageType": "text",
        "mentionedOpenIds": "",
        "mentionedUserIds": "",
    }


def append_feishu_message_status_update(
    bundle: Bundle,
    message_id: str,
    status: str,
    text: str,
    sent: bool,
    error: str = "",
    task_id: str = "",
) -> None:
    if not message_id:
        return
    path = feishu_message_event_path(bundle, message_id)
    record = load_feishu_message_event(bundle, message_id) or {"messageId": message_id, "createdAt": utc_now()}
    updates = record.get("statusUpdates")
    if not isinstance(updates, list):
        updates = []
    updates.append(
        {
            "taskId": task_id,
            "status": status,
            "text": text,
            "sent": bool(sent),
            "error": compact_snippet(error, 500),
            "updatedAt": utc_now(),
        }
    )
    record["statusUpdates"] = updates
    record["lastStatus"] = status
    record["lastStatusSent"] = bool(sent)
    record["lastStatusError"] = compact_snippet(error, 500)
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def create_feishu_status_notification_record(
    bundle: Bundle,
    task: dict[str, Any],
    task_id: str,
    message_id: str,
    status: str,
    text: str,
    sent: bool,
    error: str,
    actor: str,
) -> str:
    directory = bundle.root / "notifications"
    ensure_dir(directory)
    notification_id = unique_time_id("notification")
    path = directory / f"{notification_id}.md"
    frontmatter = {
        "type": "NotificationRecord",
        "title": f"feishu_task_status {task_id}",
        "description": "Feishu task status delivery trace.",
        "timestamp": utc_now(),
        "notificationId": notification_id,
        "taskId": task_id,
        "projectId": str(task.get("projectId") or ""),
        "recipient": str(task.get("submitter") or task.get("requester") or task.get("owner") or ""),
        "channel": "feishu",
        "messageType": "feishu_task_status",
        "status": "sent" if sent else "failed",
        "sentAt": utc_now() if sent else "",
        "sourceMessageRef": f"feishu://message/{message_id}" if message_id else "",
        "failureReason": compact_snippet(error, 300),
        "retryCount": 0,
        "lastAttemptAt": utc_now(),
        "deadLetterAt": "",
    }
    body = "\n".join(
        [
            "## Message",
            "",
            text,
            "",
            "## Delivery",
            "",
            f"- status: {'sent' if sent else 'failed'}",
            f"- taskStatus: {status}",
            f"- error: {compact_snippet(error, 500) if error else 'none'}",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    ref = str(path.relative_to(bundle.root))
    create_audit_log(
        bundle,
        actor or "feishu-status-notifier",
        "feishu.task_status.notification",
        task_id,
        after="sent" if sent else "failed",
        policy_result="bot_gateway",
        details=f"notificationRef={ref}\nmessageId={message_id}\nstatus={status}\nerror={compact_snippet(error, 500)}",
    )
    return ref


def notify_feishu_task_status(
    bundle: Bundle,
    task_id: str,
    status: str,
    actor: str = "feishu-status-notifier",
    detail: str = "",
    settings: FeishuSettings | None = None,
) -> dict[str, Any]:
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    updates: dict[str, Any] = {"status": status}
    if updates:
        update_frontmatter_file(task_path, updates)
        task.update(updates)
    runner_id = str(task.get("runnerId") or task.get("assignedRunner") or "").strip()
    executor_label = manual_runner_executor_label(bundle, task) if runner_id else "资料处理器"
    text = task_status_notification_text(status, task_id, executor_label, detail)
    message_id = task_source_message_id(bundle, task)
    if not message_id:
        notification_ref = create_feishu_status_notification_record(bundle, task, task_id, "", status, text, False, "missing_feishu_message_id", actor)
        return {"ok": False, "sent": False, "taskId": task_id, "status": status, "error": "missing_feishu_message_id", "notificationRef": notification_ref}
    event = load_feishu_message_event(bundle, message_id)
    if not event:
        notification_ref = create_feishu_status_notification_record(bundle, task, task_id, message_id, status, text, False, "missing_feishu_message_event", actor)
        append_feishu_message_status_update(bundle, message_id, status, text, False, "missing_feishu_message_event", task_id)
        return {"ok": False, "sent": False, "taskId": task_id, "status": status, "messageId": message_id, "error": "missing_feishu_message_event", "notificationRef": notification_ref}
    settings = settings or load_feishu_settings()
    sent = False
    error = ""
    if settings.reply_enabled and settings.app_id and settings.app_secret:
        try:
            sent = send_feishu_incoming_response(settings, feishu_incoming_from_event(event), {"msg_type": "text", "reply": text})
        except urllib.error.HTTPError as exc:
            error = feishu_http_error_detail(exc)
        except Exception as exc:
            error = str(exc)
    else:
        error = "feishu_reply_disabled_or_missing_credentials"
    append_feishu_message_status_update(bundle, message_id, status, text, sent, error, task_id)
    error_info = classify_feishu_delivery_error(error) if error else {"errorClass": ""}
    record_feishu_delivery_attempt(
        message_id,
        "task_status",
        "sent" if sent else "failed",
        event_id=message_id,
        response_code="ok" if sent else "",
        error_class=str(error_info.get("errorClass") or ""),
        summary=error or f"taskId={task_id}; status={status}",
    )
    notification_ref = create_feishu_status_notification_record(bundle, task, task_id, message_id, status, text, sent, error, actor)
    return {
        "ok": bool(sent),
        "sent": bool(sent),
        "taskId": task_id,
        "status": status,
        "messageId": message_id,
        "notificationRef": notification_ref,
        "error": error,
    }


def knowledge_query_log_dir(bundle: Bundle) -> Path:
    path = bundle.zz_dir / "knowledge-query-logs"
    ensure_dir(path)
    return path


def knowledge_query_log_path(bundle: Bundle, query_id: str) -> Path:
    return knowledge_query_log_dir(bundle) / f"{slug(query_id)}.json"


def project_group_binding_dir(bundle: Bundle) -> Path:
    path = bundle.zz_dir / "project-group-bindings"
    ensure_dir(path)
    return path


def project_group_binding_path(bundle: Bundle, chat_id: str) -> Path:
    return project_group_binding_dir(bundle) / f"{slug(chat_id)}.json"


def load_project_group_binding(bundle: Bundle, chat_id: str) -> dict[str, Any]:
    if not chat_id:
        return {}
    path = project_group_binding_path(bundle, chat_id)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_project_group_binding(bundle: Bundle, incoming: dict[str, str], project_id: str, project_name: str, actor: str, note: str = "") -> str:
    chat_id = incoming.get("chatId", "")
    if not chat_id:
        raise KnowledgeError("missing chat id for project group binding")
    path = project_group_binding_path(bundle, chat_id)
    record = {
        "type": "ProjectGroupBinding",
        "chatId": chat_id,
        "chatType": incoming.get("chatType", ""),
        "projectId": project_id,
        "projectName": project_name,
        "actor": actor,
        "note": note,
        "updatedAt": utc_now(),
    }
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return str(path.relative_to(bundle.root))


def load_knowledge_query_log(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "corrupt", "path": str(path)}


def update_knowledge_query_log_delivery(
    bundle: Bundle,
    log_ref: str,
    channel: str,
    status: str,
    sent: bool = False,
    reply_error: str = "",
) -> None:
    if not log_ref:
        return
    path = bundle.root / log_ref
    record = load_knowledge_query_log(path)
    if not record:
        return
    record["delivery"] = {
        "channel": channel,
        "status": status,
        "sent": bool(sent),
        "replyError": reply_error,
        "updatedAt": utc_now(),
    }
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def update_knowledge_query_delivery(bundle: Bundle, incoming: dict[str, str], sent: bool, reply_error: str) -> None:
    message_id = incoming.get("messageId", "")
    if not message_id:
        return
    candidates: list[Path] = []
    for path in sorted(knowledge_query_log_dir(bundle).glob("*.json")):
        record = load_knowledge_query_log(path)
        if record.get("messageId") == message_id:
            candidates.append(path)
    if not candidates:
        return
    path = candidates[-1]
    record = load_knowledge_query_log(path)
    update_knowledge_query_log_delivery(bundle, str(path.relative_to(bundle.root)), "feishu", "sent" if sent else ("failed" if reply_error else "not_sent"), sent, reply_error)


def feishu_http_error_detail(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        body = ""
    return f"HTTP Error {exc.code}: {exc.reason}" + (f" | {compact_snippet(body, 500)}" if body else "")


def classify_feishu_delivery_error(detail: str) -> dict[str, Any]:
    lowered = detail.lower()
    if not detail:
        return {"errorClass": "", "critical": False, "message": "", "nextAction": ""}
    if "permission" in lowered or "scope" in lowered or "forbidden" in lowered or "no authority" in lowered:
        return {
            "errorClass": "missing_send_scope",
            "critical": True,
            "message": "飞书应用缺少发消息/发卡片权限，消息没有发出。",
            "nextAction": "在飞书开放平台补齐 im:message 相关权限并重新发布应用，再重试。",
        }
    if "app_secret" in lowered or "app credential" in lowered or "tenant_access_token" in lowered or "999916" in lowered:
        return {
            "errorClass": "app_credential_invalid",
            "critical": True,
            "message": "飞书应用凭据不可用，消息没有发出。",
            "nextAction": "检查 FEISHU_APP_ID/FEISHU_APP_SECRET 的密钥引用和飞书应用状态，然后重试发送。",
        }
    if "bot" in lowered and ("chat" in lowered or "group" in lowered):
        return {
            "errorClass": "bot_not_in_chat",
            "critical": True,
            "message": "飞书机器人不在目标会话里，消息没有发出。",
            "nextAction": "把机器人加入对应群或改用有效 open_id/chat_id 后重试。",
        }
    return {
        "errorClass": "feishu_delivery_failed",
        "critical": False,
        "message": "飞书消息发送失败。",
        "nextAction": "查看 AuditLog 和 Feishu API 返回摘要，修复后重试。",
    }


def create_feishu_permission_notification(bundle: Bundle, incoming: dict[str, str], error_info: dict[str, Any], detail: str) -> str:
    if not error_info.get("critical"):
        return ""
    directory = bundle.root / "notifications"
    ensure_dir(directory)
    notification_id = unique_time_id("notification")
    path = directory / f"{notification_id}.md"
    actor = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    message_id = incoming.get("messageId", "")
    summary = "\n".join(
        [
            str(error_info.get("message") or "飞书消息发送失败。"),
            "",
            f"下一步：{error_info.get('nextAction') or '修复飞书应用配置后重试。'}",
            f"消息：{message_id or 'unknown'}",
        ]
    )
    frontmatter = {
        "type": "NotificationRecord",
        "title": f"feishu_permission_failure {message_id or notification_id}",
        "description": "Feishu delivery permission failure notification trace.",
        "timestamp": utc_now(),
        "notificationId": notification_id,
        "taskId": "",
        "projectId": "",
        "recipient": actor,
        "channel": "feishu",
        "messageType": "feishu_permission_failure",
        "status": "failed",
        "sentAt": "",
        "sourceMessageRef": f"feishu://message/{message_id}" if message_id else "",
        "failureReason": str(error_info.get("errorClass") or "feishu_delivery_failed"),
        "retryCount": 0,
        "lastAttemptAt": utc_now(),
        "deadLetterAt": "",
    }
    body = "\n".join(
        [
            "## Message Summary",
            "",
            summary,
            "",
            "## Delivery",
            "",
            f"- errorClass: {error_info.get('errorClass')}",
            f"- detail: {compact_snippet(detail, 500)}",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    ref = str(path.relative_to(bundle.root))
    create_audit_log(
        bundle,
        actor,
        "feishu.permission.notification",
        message_id or notification_id,
        after="failed",
        policy_result="bot_gateway",
        details=f"notificationRef={ref}\nerrorClass={error_info.get('errorClass')}\nnextAction={error_info.get('nextAction')}",
    )
    return ref


def fail_feishu_message_event(bundle: Bundle, incoming: dict[str, str], exc: Exception) -> None:
    message_id = incoming.get("messageId", "")
    if not message_id:
        return
    path = feishu_message_event_path(bundle, message_id)
    record = load_feishu_message_event(bundle, message_id) or {"messageId": message_id, "createdAt": utc_now()}
    record.update({"status": "failed", "failedAt": utc_now(), "error": compact_snippet(str(exc), 500)})
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    record_operational_event(
        message_id,
        "feishu",
        "failed",
        actor_ref=incoming.get("openId") or incoming.get("userId") or "feishu-user",
        target_ref=f"feishu://message/{message_id}",
        idempotency_key=message_id,
        error_class=type(exc).__name__,
        summary=str(exc),
    )


def feishu_card_event_dir(bundle: Bundle) -> Path:
    path = bundle.zz_dir / "feishu-card-events"
    ensure_dir(path)
    return path


def feishu_card_job_dir(bundle: Bundle) -> Path:
    path = bundle.zz_dir / "feishu-card-jobs"
    ensure_dir(path)
    return path


def feishu_card_submit_job_key(payload: dict[str, Any], action_name: str, form: dict[str, str]) -> str:
    event = payload.get("event") if isinstance(payload.get("event"), dict) else {}
    context = event.get("context") if isinstance(event.get("context"), dict) else {}
    source = {
        "actionName": action_name,
        "openMessageId": str(context.get("open_message_id") or deep_find(payload, "open_message_id") or ""),
        "form": form,
    }
    return hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def reserve_feishu_card_submit_job(bundle: Bundle, job_key: str, action_name: str, form: dict[str, str]) -> tuple[bool, Path, str]:
    path = feishu_card_job_dir(bundle) / f"{job_key}.json"
    record = {
        "jobKey": job_key,
        "actionName": action_name,
        "status": "queued",
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
        "formHash": hashlib.sha256(json.dumps(form, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
    }
    try:
        ensure_dir(path.parent)
        with path.open("x", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)
        return True, path, "queued"
    except FileExistsError:
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            return False, path, str(existing.get("status") or "queued")
        except Exception:
            return False, path, "queued"


def update_feishu_card_submit_job(path: Path, status: str, detail: str = "") -> None:
    try:
        record = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        record = {}
    record["status"] = status
    record["updatedAt"] = utc_now()
    if detail:
        record["detail"] = compact_snippet(detail, 500)
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")


def save_feishu_card_action_event(bundle: Bundle, payload: dict[str, Any], action_name: str, form: dict[str, str], response: dict[str, Any] | None = None, status: str = "received") -> None:
    event_id = str(deep_find(payload, "event_id") or unique_time_id("card-action"))
    path = feishu_card_event_dir(bundle) / f"{slug(event_id)}.json"
    event = payload.get("event") if isinstance(payload.get("event"), dict) else {}
    context = event.get("context") if isinstance(event.get("context"), dict) else {}
    operator = event.get("operator") if isinstance(event.get("operator"), dict) else {}
    record: dict[str, Any] = {
        "eventId": event_id,
        "status": status,
        "updatedAt": utc_now(),
        "eventType": extract_event_type(payload),
        "actionName": action_name,
        "formKeys": sorted(form.keys()),
        "formHash": hashlib.sha256(json.dumps(form, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "openMessageId": str(context.get("open_message_id") or deep_find(payload, "open_message_id") or ""),
        "openChatId": str(context.get("open_chat_id") or deep_find(payload, "open_chat_id") or ""),
        "operatorKeys": sorted(operator.keys()),
    }
    if response is not None:
        record["responseKeys"] = sorted(response.keys())
        card = response.get("card") if isinstance(response.get("card"), dict) else {}
        record["responseCardType"] = card.get("type", "")
        record["responseHasData"] = bool(card.get("data"))
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    record_operational_event(
        event_id,
        "feishu-card",
        status,
        actor_ref=str(deep_find(payload, "open_id") or deep_find(payload, "user_id") or "feishu-card"),
        target_ref=f"feishu://card/{record.get('openMessageId') or event_id}",
        idempotency_key=str(record.get("openMessageId") or event_id),
        summary=f"Feishu card action {action_name or 'unknown'} status {status}.",
    )


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


def is_card_action_event(event_type: str) -> bool:
    lowered = event_type.lower()
    return lowered.startswith("card.action") or lowered.startswith("im.message.card")


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


def create_feishu_reject_audit(bundle: Bundle, payload: dict[str, Any], settings: FeishuSettings, reason: str) -> None:
    event_type = extract_event_type(payload)
    supplied = supplied_event_token(payload)
    target = str(deep_find(payload, "message_id") or deep_find(payload, "instance_code") or event_type or "unknown")
    expected = settings.verification_token
    details = "\n".join(
        [
            f"reason: {reason}",
            f"eventType: {event_type or 'unknown'}",
            f"providedVerificationPresent: {bool(supplied)}",
            f"configuredVerificationPresent: {bool(expected)}",
            f"verificationMatched: {bool(supplied and expected and hmac.compare_digest(supplied, expected))}",
            f"hasEncrypt: {'encrypt' in payload}",
            f"payloadShape: {safe_payload_shape(payload)}",
        ]
    )
    create_audit_log(bundle, "feishu-callback", "feishu.event.rejected", target, after="rejected", policy_result="bot_gateway", details=details)
    record_operational_event(
        f"feishu-reject-{hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode('utf-8')).hexdigest()[:16]}",
        "feishu",
        "rejected",
        actor_ref="feishu-callback",
        target_ref=target,
        idempotency_key=target,
        error_class="feishu_callback_rejected",
        summary=reason,
    )


def supplied_event_token(payload: dict[str, Any]) -> str:
    header = payload.get("header") or {}
    event = payload.get("event") or {}
    return str(header.get("token") or payload.get("token") or event.get("token") or "")


def safe_payload_shape(payload: dict[str, Any]) -> str:
    keys = sorted(str(key) for key in payload.keys())
    return ",".join(keys) if keys else "empty"


def token_fingerprint(value: str) -> str:
    if not value:
        return "missing"
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"len={len(value)} sha256={digest}"


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
        "mentionedUserIds": ",".join(extract_mentioned_user_ids(message, content)),
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


def extract_mentioned_user_ids(message: dict[str, Any], content: dict[str, Any]) -> list[str]:
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
            value = str(user_id.get("user_id") or "")
        else:
            value = str(mention.get("user_id") or "")
        if value and value not in result:
            result.append(value)
    return result


def parse_knowledge_query_text(text: str) -> dict[str, str]:
    raw = text.strip()
    question = re.sub(r"^(查知识|检索知识|搜索知识)\s*[:：]?\s*", "", raw).strip()
    project_query = ""
    match = re.match(r"^项目\s+([^,，\n]+)[,，\s]*(?:问题|查|查询)?\s*[:：]?\s*(.+)$", question)
    if match:
        project_query = match.group(1).strip()
        question = match.group(2).strip()
    return {"question": question, "projectQuery": project_query}


@dataclass(frozen=True)
class LocalIntentDecision:
    intent: str
    confidence: float
    fields: dict[str, str]
    missing_fields: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class FeishuIntentDecision:
    intent: str
    confidence: float
    fields: dict[str, str]
    missing_fields: tuple[str, ...] = ()
    reason: str = ""


def is_project_status_prompt_without_project(text: str) -> bool:
    stripped = text.strip(" ：:，,。?？")
    if stripped in {"项目状态", "项目详情", "项目进度", "查项目", "查项目状态", "查看项目状态", "项目情况"}:
        return True
    return bool(re.match(r"^(?:查|看|查看|查询|了解)?(?:一下|下)?(?:项目)?(?:状态|进度|详情|情况)$", stripped))


def classify_local_intent(text: str) -> LocalIntentDecision | None:
    stripped = text.strip()
    if not stripped:
        return None
    project_query = parse_project_status_query(stripped)
    if project_query:
        return LocalIntentDecision(
            intent="status_query",
            confidence=0.98,
            fields={"projectName": project_query},
            reason="local_project_status_pattern",
        )
    if is_project_status_prompt_without_project(stripped):
        return LocalIntentDecision(
            intent="status_query",
            confidence=0.95,
            fields={},
            missing_fields=("项目名称",),
            reason="local_project_status_missing_project",
        )
    lowered = stripped.lower()
    if "token" in lowered or "令牌" in stripped or "申请知识工程" in stripped:
        return LocalIntentDecision(
            intent="credential_request",
            confidence=0.9,
            fields={},
            reason="local_credential_keyword",
        )
    if parse_project_init(stripped):
        return LocalIntentDecision(
            intent="create_project",
            confidence=0.95,
            fields={},
            reason="local_project_init_pattern",
        )
    if parse_project_material(stripped):
        return LocalIntentDecision(
            intent="capture_material",
            confidence=0.92,
            fields={},
            reason="local_project_material_pattern",
        )
    if is_system_change_request(stripped):
        return LocalIntentDecision(
            intent="tool_or_skill_request",
            confidence=0.92,
            fields={"approvalBoundary": "system_change"},
            reason="local_system_change_keyword",
        )
    research_material = parse_research_material(stripped)
    if research_material:
        return LocalIntentDecision(
            intent="capture_material",
            confidence=0.91,
            fields={"intakeMode": "research"},
            reason=research_material.get("reason", "local_research_material_pattern"),
        )
    if parse_intake(stripped):
        return LocalIntentDecision(
            intent="capture_material",
            confidence=0.9,
            fields={},
            reason="local_common_intake_pattern",
        )
    if re.match(r"^(查知识|检索知识|搜索知识)\b", stripped):
        parsed = parse_knowledge_query_text(stripped)
        return LocalIntentDecision(
            intent="knowledge_query",
            confidence=0.95,
            fields={"question": parsed["question"], "projectName": parsed["projectQuery"]},
            reason="local_knowledge_query_pattern",
        )
    return None


def record_local_intent_decision(bundle: Bundle, incoming: dict[str, str], decision: LocalIntentDecision) -> None:
    create_audit_log(
        bundle,
        incoming.get("openId") or incoming.get("userId") or "feishu-user",
        "feishu.local_router.decision",
        incoming.get("messageId", ""),
        after=decision.intent,
        policy_result="local_router",
        details=json.dumps(
            {
                "intent": decision.intent,
                "confidence": decision.confidence,
                "reason": decision.reason,
                "fieldKeys": sorted(decision.fields.keys()),
                "missingFields": list(decision.missing_fields),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )


def record_feishu_intent_decision(bundle: Bundle, incoming: dict[str, str], decision: FeishuIntentDecision) -> None:
    create_audit_log(
        bundle,
        incoming.get("openId") or incoming.get("userId") or "feishu-user",
        "feishu.intent_router.decision",
        incoming.get("messageId", ""),
        after=decision.intent,
        policy_result="intent_state_machine",
        details=json.dumps(
            {
                "intent": decision.intent,
                "confidence": decision.confidence,
                "reason": decision.reason,
                "fieldKeys": sorted(decision.fields.keys()),
                "missingFields": list(decision.missing_fields),
            },
            ensure_ascii=False,
            sort_keys=True,
        ),
    )


def parse_bind_project_group_text(text: str) -> str:
    match = re.match(r"^绑定项目群\s*[:：]\s*项目\s+(.+)$", text.strip())
    return match.group(1).strip() if match else ""


def bind_project_group(bundle: Bundle, incoming: dict[str, str], project_name: str, actor: str, note: str = "") -> str:
    if is_private_chat(incoming):
        return bind_project_group_entry_text(incoming)
    if not project_name:
        return "项目群绑定还缺：项目名称。"
    resolved = resolve_project_ref(bundle, project_name)
    if resolved.get("error"):
        return str(resolved.get("message") or f"没找到项目：{project_name}。请先创建项目，再绑定项目群。")
    project = load_object(Path(resolved["path"]))
    project_id = str(project.get("projectId") or Path(resolved["path"]).parent.name)
    display_name = str(project.get("title") or project_name)
    binding_ref = write_project_group_binding(bundle, incoming, project_id, display_name, actor, note)
    create_audit_log(bundle, actor, "project_group.bind", binding_ref, after=project_id, policy_result="bot_gateway", details=f"chatId: {incoming.get('chatId', '')}\nprojectName: {display_name}\nnote: {note or 'n/a'}")
    return "\n".join(
        [
            "已绑定项目群。",
            f"项目: {display_name}",
            f"项目编号: {project_id}",
            f"绑定记录: {binding_ref}",
            "后续在这个群里直接问知识时，我会默认查该项目范围和通用知识。",
        ]
    )


def retrieval_row_allowed_for_query(row: dict[str, Any], project_id: str) -> tuple[bool, str]:
    row_project = str(row.get("projectId") or "")
    if row_project in GLOBAL_KNOWLEDGE_PROJECT_IDS:
        return True, ""
    if project_id:
        if row_project and row_project != project_id:
            return False, "wrong_project"
        return True, ""
    if row_project:
        return False, "project_scope_required"
    return True, ""


def retrieval_citation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": row.get("path", ""),
        "chunkId": row.get("chunkId", ""),
        "title": row.get("title", ""),
        "status": row.get("status", ""),
        "sourceRef": row.get("sourceRef", ""),
        "projectId": row.get("projectId", ""),
        "score": row.get("score", 0),
    }


def render_knowledge_query_answer(result: dict[str, Any]) -> str:
    if result["answerMode"] == "needs_clarification":
        return str(result["clarification"])
    if result["answerMode"] == "reviewable_reference":
        lines = ["没有找到已审核答案，但找到这些待审核经验，可参考但不要当作正式结论："]
        for idx, row in enumerate(result["chunks"][:3], 1):
            snippet = compact_snippet(str(row.get("text", "")))
            lines.append(f"{idx}. {row.get('title') or row.get('path')} [{row.get('status')}]")
            lines.append(f"   来源: {row.get('sourceRef') or row.get('path')}")
            lines.append(f"   知识文件: {row.get('path')}")
            lines.append(f"   摘要: {snippet}")
        lines.append("需要正式复用时，发送“沉淀：<内容>”补充材料，知识工程 Agent Review 后才能提升为 verified。")
        return "\n".join(lines)
    if result["answerMode"] == "source_reference":
        lines = ["找到已入库资料："]
        for idx, row in enumerate(result["chunks"][:3], 1):
            snippet = compact_snippet(str(row.get("text", "")))
            lines.append(f"{idx}. {row.get('title') or row.get('path')}")
            lines.append(f"   来源: {row.get('sourceRef') or row.get('path')}")
            lines.append(f"   资料文件: {row.get('path')}")
            lines.append(f"   内容预览: {snippet}")
        return "\n".join(lines)
    if result["answerMode"] == "no_reliable_answer":
        return no_reliable_answer_text(result["incoming"])
    lines = ["基于已审核知识，找到这些相关内容："]
    if result.get("projectId"):
        lines.append(f"范围: 项目 {result['projectId']} + 通用知识")
    else:
        lines.append("范围: 通用已审核知识")
    for idx, row in enumerate(result["chunks"][:3], 1):
        snippet = compact_snippet(str(row.get("text", "")))
        lines.append(f"{idx}. {row.get('title') or row.get('path')} [{row.get('status')}]")
        lines.append(f"   来源: {row.get('sourceRef') or row.get('path')}")
        lines.append(f"   摘要: {snippet}")
    lines.append("需要沉淀新经验时，发送：沉淀：<内容>。")
    return "\n".join(lines)


def write_knowledge_query_log(bundle: Bundle, result: dict[str, Any]) -> str:
    query_id = result["queryId"]
    path = knowledge_query_log_path(bundle, query_id)
    record = {
        "type": "KnowledgeQueryLog",
        "queryId": query_id,
        "status": result["answerMode"],
        "createdAt": result["createdAt"],
        "completedAt": utc_now(),
        "latencyMs": result["latencyMs"],
        "actor": result["actor"],
        "messageId": result["incoming"].get("messageId", ""),
        "chatId": result["incoming"].get("chatId", ""),
        "chatType": result["incoming"].get("chatType", ""),
        "queryText": result["queryText"],
        "queryHash": hashlib.sha256(result["queryText"].encode("utf-8")).hexdigest(),
        "projectQuery": result["projectQuery"],
        "projectBindingRef": result.get("projectBindingRef", ""),
        "resolvedProjectId": result["projectId"],
        "retrievalMode": "local_hybrid_hash_vector_lexical",
        "answerMode": result["answerMode"],
        "citations": [retrieval_citation(row) for row in result["chunks"][:5]],
        "rejectedCandidates": result["rejectedCandidates"][:10],
        "candidateCount": result["candidateCount"],
        "delivery": {"channel": "feishu", "status": "pending", "sent": False, "replyError": ""},
    }
    write_text(path, json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return str(path.relative_to(bundle.root))


def run_knowledge_query(bundle: Bundle, incoming: dict[str, str], text: str, project_query: str = "") -> dict[str, Any]:
    started = time.monotonic()
    created_at = utc_now()
    parsed = parse_knowledge_query_text(text)
    question = parsed["question"].strip()
    explicit_project = (project_query or parsed["projectQuery"]).strip()
    bound_project = load_project_group_binding(bundle, incoming.get("chatId", "")) if not explicit_project else {}
    if bound_project:
        explicit_project = str(bound_project.get("projectId") or bound_project.get("projectName") or "")
    query_id = unique_time_id("kq")
    actor = incoming.get("openId") or incoming.get("userId") or "knowledge-query-user"
    result: dict[str, Any] = {
        "apiVersion": "v0.1",
        "kind": "KnowledgeQueryResult",
        "queryId": query_id,
        "createdAt": created_at,
        "actor": actor,
        "incoming": incoming,
        "queryText": question,
        "projectQuery": explicit_project,
        "projectBindingRef": str(project_group_binding_path(bundle, incoming.get("chatId", "")).relative_to(bundle.root)) if bound_project else "",
        "projectId": "",
        "answerMode": "no_reliable_answer",
        "chunks": [],
        "rejectedCandidates": [],
        "candidateCount": 0,
        "latencyMs": 0,
    }
    if not question:
        result["answerMode"] = "needs_clarification"
        result["clarification"] = "请直接告诉我要查什么知识，例如：飞书卡片 JSON 2.0 怎么写？"
        result["latencyMs"] = int((time.monotonic() - started) * 1000)
        result["reply"] = render_knowledge_query_answer(result)
        result["logRef"] = write_knowledge_query_log(bundle, result)
        create_audit_log(bundle, actor, "knowledge_query.completed", query_id, after=result["answerMode"], policy_result="served_by_bot", details=f"logRef: {result['logRef']}\nquery: {question or text}")
        return result
    if explicit_project:
        resolved = resolve_project_ref(bundle, explicit_project)
        if resolved.get("error"):
            result["answerMode"] = "needs_clarification"
            result["clarification"] = str(resolved.get("message") or "这个问题需要更明确的项目名称。")
            result["latencyMs"] = int((time.monotonic() - started) * 1000)
            result["reply"] = render_knowledge_query_answer(result)
            result["logRef"] = write_knowledge_query_log(bundle, result)
            create_audit_log(bundle, actor, "knowledge_query.completed", query_id, after=result["answerMode"], policy_result="served_by_bot", details=f"logRef: {result['logRef']}\nprojectQuery: {explicit_project}\nquery: {question}")
            return result
        project = load_object(Path(resolved["path"]))
        result["projectId"] = str(project.get("projectId") or Path(resolved["path"]).parent.name)
    rows = [row for row in search_retrieval(bundle, question, limit=50) if row.get("type") in SEARCH_ANSWER_TYPES]
    allowed_rows: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for row in rows:
        allowed, reason = retrieval_row_allowed_for_query(row, result["projectId"])
        if allowed:
            allowed_rows.append(row)
        else:
            rejected.append({**retrieval_citation(row), "reason": reason})
    result["candidateCount"] = len(allowed_rows)
    result["rejectedCandidates"] = rejected
    answerable_rows = unique_retrieval_rows(
        [
            row
            for row in allowed_rows
            if (
                row.get("type") != "SourceMaterial"
                and (row.get("status") in FORMAL_STATUSES or row.get("status") in REVIEWABLE_REFERENCE_STATUSES)
            )
            or (
                row.get("type") == "SourceMaterial"
                and row.get("status") in SOURCE_REFERENCE_STATUSES
                and "Classified source reference stored by Feishu direct material intake." in str(row.get("text") or "")
            )
        ]
    )
    if answerable_rows and answerable_rows[0].get("status") in FORMAL_STATUSES:
        result["answerMode"] = "verified_answer"
        result["chunks"] = [row for row in answerable_rows if row.get("status") in FORMAL_STATUSES]
    elif answerable_rows and answerable_rows[0].get("type") == "SourceMaterial":
        result["answerMode"] = "source_reference"
        result["chunks"] = [
            row
            for row in answerable_rows
            if row.get("type") == "SourceMaterial"
            and row.get("status") in SOURCE_REFERENCE_STATUSES
            and "Classified source reference stored by Feishu direct material intake." in str(row.get("text") or "")
        ]
    elif answerable_rows and answerable_rows[0].get("status") in REVIEWABLE_REFERENCE_STATUSES:
        result["answerMode"] = "reviewable_reference"
        result["chunks"] = [row for row in answerable_rows if row.get("status") in REVIEWABLE_REFERENCE_STATUSES]
    else:
        result["answerMode"] = "no_reliable_answer"
        result["chunks"] = []
    result["latencyMs"] = int((time.monotonic() - started) * 1000)
    result["reply"] = render_knowledge_query_answer(result)
    result["logRef"] = write_knowledge_query_log(bundle, result)
    details = "\n".join(
        [
            f"logRef: {result['logRef']}",
            f"answerMode: {result['answerMode']}",
            f"projectId: {result['projectId'] or 'general'}",
            f"candidateCount: {result['candidateCount']}",
            f"rejectedCount: {len(result['rejectedCandidates'])}",
            f"latencyMs: {result['latencyMs']}",
        ]
    )
    create_audit_log(bundle, actor, "knowledge_query.completed", query_id, after=result["answerMode"], policy_result="served_by_bot", details=details)
    return result


def has_material_status_followup_signal(text: str) -> bool:
    normalized = normalize_for_keyword_match(text)
    if not normalized:
        return False
    return any(normalize_for_keyword_match(keyword) in normalized for keyword in MATERIAL_STATUS_FOLLOWUP_KEYWORDS)


def classify_feishu_intent(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> FeishuIntentDecision:
    del settings
    text = incoming["text"].strip()
    local_intent = classify_local_intent(text)
    previous_material = latest_research_material_source_for_chat(bundle, incoming)
    material_correction = parse_material_correction(text)
    if material_correction:
        return FeishuIntentDecision(
            intent="material_correction",
            confidence=0.96,
            fields={
                "hasPreviousMaterial": str(bool(previous_material)).lower(),
            },
            reason="material_correction_signal",
        )
    material_followup = parse_material_followup(text)
    if material_followup:
        return FeishuIntentDecision(
            intent="material_followup",
            confidence=0.96,
            fields={
                "action": material_followup["action"],
                "keyword": material_followup.get("keyword", ""),
                "hasPreviousMaterial": str(bool(previous_material)).lower(),
            },
            reason="material_followup_keyword_with_context_priority",
        )
    if has_material_status_followup_signal(text):
        return FeishuIntentDecision(
            intent="material_status",
            confidence=0.92,
            fields={"hasPreviousMaterial": str(bool(previous_material)).lower()},
            reason="material_status_followup_signal",
        )
    if local_intent and local_intent.intent in {"status_query", "credential_request", "tool_or_skill_request"}:
        return FeishuIntentDecision(local_intent.intent, local_intent.confidence, local_intent.fields, local_intent.missing_fields, local_intent.reason)
    if parse_project_init(text):
        return FeishuIntentDecision("create_project", 0.95, {}, reason="project_init_pattern")
    if parse_project_material(text):
        return FeishuIntentDecision("project_material", 0.92, {}, reason="project_material_pattern")
    if parse_research_material(text):
        return FeishuIntentDecision("research_material", 0.93, {}, reason="research_material_pattern")
    if parse_intake(text):
        return FeishuIntentDecision("research_material", 0.88, {"intakeMode": "plain_text"}, reason="plain_material_intake_pattern")
    if is_ambiguous_short_input(text):
        return FeishuIntentDecision("clarification_required", 0.82, {}, reason="ambiguous_short_input")
    return FeishuIntentDecision("knowledge_query", 0.72, {}, reason="default_knowledge_query")


def handle_feishu_intent(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, decision: FeishuIntentDecision) -> str:
    text = incoming["text"].strip()
    if decision.intent == "status_query":
        return render_project_status_text(project_status_summary(bundle, decision.fields.get("projectName", "")))
    if decision.intent == "credential_request":
        return token_request_reply(bundle, incoming, settings)
    if decision.intent == "tool_or_skill_request":
        return system_change_request_reply()
    if decision.intent == "create_project":
        return project_init_reply(bundle, incoming, settings, parse_project_init(text))
    if decision.intent == "project_material":
        material = parse_project_material(text)
        _source_path, _task_path, task_id, assignee = create_project_material_task(bundle, incoming, settings, material)
        return "\n".join(
            [
                "已接收原始资料，并创建知识沉淀任务。",
                f"项目：{material['projectRaw']}",
                f"任务编号：{task_id}",
                f"负责人：{assignee}",
                "当前状态：等待整理",
                "负责人会在指定执行电脑的 Codex / Claude 中处理，完成后我会通知提交人；如发现可复用 Agent 能力，会进入 CapabilityCandidate、Review 和 Approval。",
            ]
        )
    if decision.intent == "research_material":
        research_material = parse_research_material(text)
        if not research_material:
            intake = parse_intake(text)
            research_material = {"title": "研究资料：飞书记录", "content": intake, "sourceRef": ""}
        material_source = create_research_material_source(bundle, incoming, settings, research_material)
        if material_source.get("idempotent"):
            manual_body = substantial_manual_research_body(research_material)
            if manual_body:
                return complete_research_material_from_manual_body(bundle, material_source["sourceRef"], research_material, incoming, manual_body)
            return render_existing_research_material_reply(bundle, material_source)
        return process_research_material_source_inline(bundle, material_source["sourceRef"])
    if decision.intent == "material_correction":
        return handle_material_correction(bundle, incoming, text)
    if decision.intent == "material_followup":
        return handle_material_followup(bundle, incoming, {"action": decision.fields.get("action", ""), "keyword": decision.fields.get("keyword", "")})
    if decision.intent == "material_status":
        return handle_material_status_followup(bundle, incoming)
    if decision.intent == "clarification_required":
        return ambiguous_short_input_text()
    return str(run_knowledge_query(bundle, incoming, text)["reply"])


def build_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> str:
    text = incoming["text"].strip()
    lowered = text.lower()
    if lowered in {"/help", "help", "帮助", "/帮助"}:
        return help_text(incoming)
    safety_reply = handle_dangerous_intent(incoming, text)
    if safety_reply:
        return safety_reply
    menu_reply = handle_menu_shortcut(incoming, text)
    if menu_reply:
        return menu_reply
    review_reply = handle_review_command(bundle, incoming, text)
    if review_reply:
        return review_reply
    bind_project_name = parse_bind_project_group_text(text)
    if bind_project_name:
        return bind_project_group(bundle, incoming, bind_project_name, incoming.get("openId") or incoming.get("userId") or "feishu-user")
    decision = classify_feishu_intent(bundle, incoming, settings)
    record_feishu_intent_decision(bundle, incoming, decision)
    return handle_feishu_intent(bundle, incoming, settings, decision)


def default_manual_runner_id() -> str:
    return os.environ.get("FEISHU_MANUAL_RUNNER", "runner.meimei-mac-local-codex").strip() or "runner.meimei-mac-local-codex"


def render_research_material_reply(bundle: Bundle, task_ref: str, task_id: str, runner_id: str) -> str:
    return "\n".join(
        [
            "已收到，已创建资料处理任务。",
            "当前状态：等待资料整理。",
            f"任务编号：{task_id}",
        ]
    )


def render_existing_research_material_reply(bundle: Bundle, material_task: dict[str, Any]) -> str:
    source_ref = str(material_task.get("sourceRef") or "")
    title = "资料"
    status = "已入库"
    if source_ref and (bundle.root / source_ref).exists():
        try:
            source = load_object(bundle.root / source_ref)
            title = str(source.get("title") or title)
            status = human_source_status_label(str(source.get("status") or "stored"))
        except Exception:
            pass
    lines = [
        "这个资料之前已经接收，不会重复解析或切片。" if status == "等待浏览器补抓" else "这个资料之前已经入库，不会重复解析或切片。",
        f"标题：{title}",
        f"状态：{status}",
    ]
    return "\n".join(lines)


def substantial_manual_research_body(material: dict[str, str]) -> str:
    content = str(material.get("content") or "")
    if not content.strip():
        return ""
    cleaned = URL_PATTERN.sub("", content)
    for prefix in RESEARCH_INTAKE_PREFIXES:
        cleaned = cleaned.replace(prefix, "")
    cleaned = re.sub(r"\r\n?", "\n", cleaned)
    cleaned = re.sub(r"[ \t\f\v]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip(" ：:，,\n")
    return cleaned if len(cleaned) >= 80 else ""


def title_from_manual_research_body(material: dict[str, str], manual_body: str, fallback: str) -> str:
    for line in manual_body.splitlines():
        line = line.strip(" #：:，,")
        if 4 <= len(line) <= 80:
            return line
    material_title = str(material.get("title") or "").strip()
    if material_title and "mp.weixin.qq.com" not in material_title:
        return material_title
    return fallback or "公众号资料"


def complete_research_material_from_manual_body(
    bundle: Bundle,
    source_ref: str,
    material: dict[str, str],
    incoming: dict[str, str],
    manual_body: str,
) -> str:
    from .feishu_material_processor import classify_research_reference, store_research_material_reference

    source_path = bundle.root / source_ref
    if not source_ref or not source_path.exists():
        return "没有找到可补齐的原资料，请重新发送链接和正文。"
    source = load_object(source_path)
    source_url = str(source.get("sourceRef") or material.get("sourceRef") or "")
    title = title_from_manual_research_body(material, manual_body, str(source.get("title") or "公众号资料"))
    classification = classify_research_reference(title, manual_body, "user_supplied_text")
    reference = {
        "title": title,
        "sourceUrl": source_url,
        "sourceKind": "user_supplied_text",
        "extractionOk": True,
        "extractionError": "",
        "browserPending": False,
        "content": manual_body,
        "summary": f"已使用用户补充正文入库《{title}》。 原始链接：{source_url or '未识别'}。 已归类为{classification['categoryLabel']}并存入来源资料库。",
        "category": classification["category"],
        "categoryLabel": classification["categoryLabel"],
        "tags": classification["tags"],
        "sourceRefs": [source_ref],
    }
    stored_ref = store_research_material_reference(bundle, source_ref, reference)
    try:
        publish_knowledge_bundle(bundle, actor="feishu-manual-material-completion", reason=f"manual body completed {stored_ref or source_ref}")
    except Exception:
        pass
    preview = compact_snippet(manual_body, 220)
    return "\n".join(
        [
            "资料已入库：",
            f"- 标题：{title}",
            f"- 来源：{source_url or '未识别'}",
            f"- 分类：{classification['categoryLabel']}",
            "- 正文抽取：已使用你补充的正文",
            "",
            "存储内容预览：",
            preview,
            "",
            "内容不对可直接回复：修正：<正确内容>。",
        ]
    )


def human_source_status_label(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {"stored", "captured", "registered", "referenced"}:
        return "已入库"
    if normalized in {"browser_pending"}:
        return "等待浏览器补抓"
    return display_status(normalized)


def human_task_status_label(status: str) -> str:
    normalized = status.strip().lower()
    if normalized in {"pending", "waiting_runner"}:
        return "等待资料整理"
    if normalized in {"processing", "in_progress", "running"}:
        return "正在整理资料"
    if normalized in {"done", "accepted", "completed"}:
        return "已完成"
    if normalized in {"cancelled", "canceled", "deleted"}:
        return "已取消重复处理"
    if normalized in {"rejected"}:
        return "已驳回"
    if normalized in {"blocked", "failed"}:
        return "处理遇到问题，已记录"
    return display_status(normalized)


def parse_material_followup(text: str) -> dict[str, str]:
    normalized = normalize_for_keyword_match(text)
    if not normalized:
        return {}
    for keyword in MATERIAL_FOLLOWUP_KEYWORDS:
        if normalize_for_keyword_match(keyword) in normalized:
            return {"action": "capability_candidate_review", "keyword": keyword}
    return {}


def parse_material_correction(text: str) -> str:
    stripped = text.strip()
    for prefix in ["修正：", "修正:", "更正：", "更正:", "纠正：", "纠正:"]:
        if stripped.startswith(prefix):
            return stripped.removeprefix(prefix).strip()
    normalized = normalize_for_keyword_match(stripped)
    if any(signal in normalized for signal in ["内容不对", "存错了", "解析错了", "提取错了", "标题错了"]):
        return stripped
    return ""


def latest_research_material_source_for_chat(bundle: Bundle, incoming: dict[str, str]) -> dict[str, Any]:
    chat_id = str(incoming.get("chatId") or "").strip()
    open_id = str(incoming.get("openId") or "").strip()
    user_id = str(incoming.get("userId") or "").strip()
    source_root = bundle.root / "projects" / "company-knowledge-core" / "sources"
    candidates: list[dict[str, Any]] = []
    for path in sorted(source_root.glob("*.md")):
        try:
            source = load_object(path)
        except Exception:
            continue
        if str(source.get("intakeSource") or "") != "feishu_research_material":
            continue
        same_chat = chat_id and str(source.get("feishuChatId") or "") == chat_id
        same_sender = open_id and str(source.get("feishuOpenId") or "") == open_id
        same_user = user_id and str(source.get("feishuUserId") or "") == user_id
        if not (same_chat or same_sender or same_user):
            continue
        source["path"] = str(path.relative_to(bundle.root))
        candidates.append(source)
    candidates.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    return candidates[0] if candidates else {}


def handle_material_followup(bundle: Bundle, incoming: dict[str, str], followup: dict[str, str]) -> str:
    del followup
    previous = latest_research_material_source_for_chat(bundle, incoming)
    if not previous:
        return "没有找到上一条已入库资料。请先发链接或资料。"
    status = str(previous.get("status") or "")
    if status == "browser_pending":
        return "\n".join(
            [
                "这条资料已接收，正在等待浏览器补抓正文。",
                f"标题：{previous.get('title') or '资料'}",
                "正文读到后会自动保存、切片并更新索引。",
            ]
        )
    return "\n".join(
        [
            "这条资料已入库。",
            f"标题：{previous.get('title') or '资料'}",
            "不会在单条资料里创建能力候选任务；知识工程 Agent 会按周期统一复盘、清理和系统化。",
        ]
    )


def handle_material_status_followup(bundle: Bundle, incoming: dict[str, str]) -> str:
    previous = latest_research_material_source_for_chat(bundle, incoming)
    if not previous:
        return "没有找到上一条已入库资料。请先发链接或资料。"
    status = str(previous.get("status") or "")
    title = str(previous.get("title") or "上一条资料")
    summary = material_source_preview(bundle, previous)
    pending = status == "browser_pending"
    lines = [
        "上一条资料已接收，正在等待浏览器补抓。" if pending else "上一条资料已入库。",
        f"资料：{title}",
        f"当前状态：{human_source_status_label(status or 'stored')}",
    ]
    if summary:
        lines.extend(["", "存储内容预览：", summary])
    lines.extend(
        [
            "",
            "内容不对可直接回复：修正：<正确内容>。",
        ]
    )
    return "\n".join(lines)


def source_markdown_frontmatter_and_body(source_path: Path) -> tuple[dict[str, Any], str]:
    raw = source_path.read_text(encoding="utf-8")
    parsed = parse_frontmatter(raw)
    if isinstance(parsed, tuple) and len(parsed) == 2:
        return dict(parsed[0]), str(parsed[1])
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            body = parts[2].strip()
    return dict(parsed), body


def material_source_preview(bundle: Bundle, source: dict[str, Any], limit: int = 260) -> str:
    source_path = bundle.root / str(source.get("path") or "")
    if not source_path.exists():
        return ""
    try:
        _fm, body = source_markdown_frontmatter_and_body(source_path)
    except Exception:
        return ""
    preview = body
    marker = "## Extracted Text"
    if marker in body:
        preview = body.split(marker, 1)[1]
        next_section = preview.find("\n## ")
        if next_section >= 0:
            preview = preview[:next_section]
    return compact_snippet(preview, limit)


def handle_material_correction(bundle: Bundle, incoming: dict[str, str], text: str) -> str:
    correction = parse_material_correction(text)
    if not correction:
        return "请直接回复：修正：<正确内容>。"
    previous = latest_research_material_source_for_chat(bundle, incoming)
    if not previous:
        return "没有找到可修正的上一条入库资料。请先发链接或资料。"
    source_path = bundle.root / str(previous.get("path") or "")
    if not source_path.exists():
        return "上一条入库资料文件不存在，无法修正。"
    frontmatter, body = source_markdown_frontmatter_and_body(source_path)
    before_status = str(frontmatter.get("status") or "")
    frontmatter.update(
        {
            "status": "stored",
            "userCorrectionStatus": "applied",
            "userCorrectionAt": utc_now(),
            "userCorrectionMessageId": incoming.get("messageId", ""),
            "updatedAt": utc_now(),
        }
    )
    body = "\n".join(
        [
            body.rstrip(),
            "",
            "## User Correction",
            "",
            correction,
            "",
        ]
    )
    write_text(source_path, render_doc(frontmatter, body))
    create_audit_log(
        bundle,
        incoming.get("openId") or incoming.get("userId") or "feishu-user",
        "material.referenceCorrectionApplied",
        str(source_path.relative_to(bundle.root)),
        before=before_status,
        after="stored",
        policy_result="source_reference_corrected",
        details=f"messageId={incoming.get('messageId', '')}\ncorrection={compact_snippet(correction, 180)}",
    )
    try:
        publish_knowledge_bundle(bundle, actor="feishu-material-correction", reason=f"source correction {source_path.relative_to(bundle.root)}")
    except Exception:
        pass
    return "\n".join(
        [
            "修正已写入。",
            f"资料：{frontmatter.get('title') or '上一条资料'}",
            "",
            "修正内容预览：",
            compact_snippet(correction, 260),
        ]
    )


def material_task_result_summary(bundle: Bundle, task: dict[str, Any]) -> str:
    refs: list[str] = []
    result_ref = str(task.get("resultRef") or "").strip()
    if result_ref:
        refs.append(result_ref)
    task_id = str(task.get("taskId") or "").strip()
    if task_id:
        refs.append(f"projects/company-knowledge-core/task-results/tr-{slug(task_id)}.md")
    for ref in refs:
        path = bundle.root / ref
        if not path.exists():
            continue
        try:
            frontmatter, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        summary = str(frontmatter.get("summary") or "").strip()
        if summary:
            return compact_snippet(summary, 260)
        lines = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")]
        if lines:
            return compact_snippet(" ".join(lines[:4]), 260)
    return compact_snippet(str(task.get("summary") or ""), 260)


def create_material_capability_candidate_review_task(
    bundle: Bundle,
    incoming: dict[str, str],
    previous: dict[str, Any],
    followup: dict[str, str],
) -> dict[str, str]:
    requester = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    source_refs = as_list(previous.get("sourceMaterialRefs"))
    result_ref = str(previous.get("resultRef") or "").strip()
    if result_ref and result_ref not in source_refs:
        source_refs.append(result_ref)
    previous_task_id = str(previous.get("taskId") or "")
    existing = find_existing_material_capability_review_task(bundle, previous_task_id, incoming)
    if existing:
        return existing
    task_path = create_project_task(
        bundle,
        title=f"复核资料是否可提升 Agent 团队：{previous.get('title') or previous_task_id}",
        project_id="company-knowledge-core",
        requester=requester,
        assignee="agent.company-knowledge-core.knowledge-engineering",
        task_type="knowledge_review",
        priority="normal",
        source_material_refs=source_refs,
        expected_output=[
            "判断资料对 Agent 团队提升是否有作用。",
            "说明它比现有 Skill、Tool、Workflow、设计理念或检查点好在哪里。",
            "给出建议动作：仅保存、进入候选、建议改 Skill、建议改 Tool、建议改规则，或不采纳。",
            "保留来源和边界，不直接修改正式体系。",
        ],
        work_source_type="research",
        knowledge_task_refs=[previous_task_id] if previous_task_id else [],
        research_question=str(previous.get("researchQuestion") or previous.get("title") or ""),
        source_reason=f"Feishu follow-up requested capability candidate review: {followup.get('keyword') or followup.get('action')}",
    )
    task_fm, _ = parse_task_file(task_path)
    update_frontmatter_file(
        task_path,
        {
            "intakeSource": "feishu_material_followup",
            "processingMode": "capability_candidate_review_queue",
            "upstreamTaskId": previous_task_id,
            "feishuMessageId": incoming.get("messageId", ""),
            "feishuChatId": incoming.get("chatId", ""),
            "feishuChatType": incoming.get("chatType", ""),
            "feishuOpenId": incoming.get("openId", ""),
            "feishuUserId": incoming.get("userId", ""),
            "approvalRequired": False,
            "approvalReason": "Capability candidate review may be prepared without approval; mutating Skill, Tool, Workflow, AGENTS, rules, or permissions requires separate approval.",
        },
    )
    return {"taskId": str(task_fm.get("taskId") or task_path.stem), "taskRef": str(task_path.relative_to(bundle.root))}


def find_existing_material_capability_review_task(bundle: Bundle, previous_task_id: str, incoming: dict[str, str]) -> dict[str, str]:
    if not previous_task_id:
        return {}
    chat_id = str(incoming.get("chatId") or "")
    task_root = bundle.root / "projects" / "company-knowledge-core" / "tasks"
    for path in sorted(task_root.glob("*.md"), reverse=True):
        try:
            task = load_object(path)
        except Exception:
            continue
        if str(task.get("intakeSource") or "") != "feishu_material_followup":
            continue
        if str(task.get("upstreamTaskId") or "") != previous_task_id:
            continue
        if chat_id and str(task.get("feishuChatId") or "") not in {"", chat_id}:
            continue
        return {
            "taskId": str(task.get("taskId") or path.stem),
            "taskRef": str(path.relative_to(bundle.root)),
            "status": str(task.get("status") or ""),
            "resultRef": str(task.get("resultRef") or ""),
        }
    return {}


def process_material_capability_candidate_review_inline(bundle: Bundle, previous: dict[str, Any], review_task: dict[str, str]) -> str:
    task_id = str(review_task.get("taskId") or "")
    task_ref = str(review_task.get("taskRef") or "")
    status = str(review_task.get("status") or "")
    if status in {"done", "completed", "accepted"}:
        existing_summary = material_task_result_summary(bundle, {"taskId": task_id, "resultRef": review_task.get("resultRef", "")})
        return "\n".join(["能力候选复核已完成。", existing_summary or "结论已记录。", f"复核任务：{task_id}"])
    review_text = build_material_capability_review_text(bundle, previous)
    try:
        finish_project_task(
            bundle,
            task_id,
            "done",
            "能力候选复核已完成。",
            output_refs=[task_ref] if task_ref else [],
            evidence_refs=as_list(previous.get("sourceMaterialRefs")) + ([str(previous.get("resultRef"))] if previous.get("resultRef") else []),
            next_actions=["如确认有稳定提升价值，再进入 Skill / Tool / 规则 / 检查点变更评审。"],
            executor_agent="agent.company-knowledge-core.knowledge-engineering",
            tests_or_checks=["checked source summary", "checked behavior-change value", "kept system mutation boundary"],
            open_risks=["当前只是候选复核，不代表已修改正式体系。"],
        )
    except Exception as exc:
        create_audit_log(
            bundle,
            "agent.company-knowledge-core.knowledge-engineering",
            "feishu.material_capability_review.finish_failed",
            task_id,
            after="failed",
            policy_result="feishu_direct_reply",
            details=f"{type(exc).__name__}: {exc}",
        )
    return "\n".join([review_text, "", f"复核任务：{task_id}"])


def build_material_capability_review_text(bundle: Bundle, previous: dict[str, Any]) -> str:
    title = str(previous.get("title") or previous.get("taskId") or "上一条资料")
    summary = material_task_result_summary(bundle, previous)
    combined = f"{title}\n{summary}".lower()
    signals = {
        "信息抓取/多源读取": ["read", "读取", "网页", "youtube", "github", "rss", "视频", "字幕", "资料"],
        "失败回退/路由": ["fallback", "回退", "路由", "失败", "备用", "降级"],
        "工具使用标准": ["tool", "工具", "cli", "api", "插件"],
        "检查点/验收": ["checklist", "检查", "验收", "标准", "gate"],
    }
    matched = [name for name, words in signals.items() if any(word in combined for word in words)]
    useful = bool(matched)
    if useful:
        usefulness = "有用，但还只是候选。"
        better_than_current = f"它可能补强我们现在较弱的：{'、'.join(matched)}。"
        suggestion = "进入能力候选池，后续用真实项目复用结果验证；验证稳定后再改 Skill / Tool / 规则 / 检查点。"
    else:
        usefulness = "暂时看不出能直接提升 Agent 团队。"
        better_than_current = "还没有证明比现有工具、流程或设计理念更好。"
        suggestion = "先只作为资料保存，不进入正式能力变更。"
    return "\n".join(
        [
            "能力候选复核结果：",
            f"- 是否有用：{usefulness}",
            f"- 对比现有：{better_than_current}",
            f"- 建议：{suggestion}",
            "- 边界：这不是正式变更；不会直接改 Skill、Tool、Workflow、AGENTS、规则或权限。",
        ]
    )


def process_research_material_task_inline(bundle: Bundle, task_id: str, runner_id: str) -> str:
    from .feishu_material_processor import process_research_material_task

    try:
        result = process_research_material_task(
            bundle,
            task_id,
            runner_id=runner_id,
            notify_feishu=False,
            publish_index=True,
        )
    except Exception as exc:
        return "\n".join(
            [
                "已收到，资料已保存，但自动整理失败。",
                f"任务编号：{task_id}",
                f"原因：{exc}",
            ]
        )
    detail = str(result.get("detail") or "").strip()
    if detail:
        return "\n".join([detail, "", f"任务编号：{task_id}"])
    return "\n".join(["资料已整理完成。", f"任务编号：{task_id}"])


def process_research_material_source_inline(bundle: Bundle, source_ref: str) -> str:
    from .feishu_material_processor import process_research_material_source

    try:
        result = process_research_material_source(bundle, source_ref, publish_index=True)
    except Exception as exc:
        return "\n".join(
            [
                "资料已收到，但正文抽取或入库更新失败。",
                f"原因：{exc}",
            ]
        )
    return str(result.get("detail") or "资料已入库。")


def manual_runner_label(bundle: Bundle, runner_id: str = "") -> str:
    runner_id = runner_id.strip() or default_manual_runner_id()
    runner = load_runner_record(bundle, runner_id)
    for key in ("displayName", "deviceDisplayName", "computerDisplayName", "machineDisplayName", "label"):
        value = str(runner.get(key, "")).strip()
        if value:
            return value
    configured = os.environ.get("FEISHU_MANUAL_RUNNER_LABEL", "").strip()
    if configured and runner_id == default_manual_runner_id():
        return configured
    title = str(runner.get("title", "")).strip()
    owner = str(runner.get("owner", "")).strip()
    tool = str(runner.get("tool", "") or runner.get("client", "") or "Codex").strip()
    if owner:
        return f"{owner}的电脑上的 {tool}"
    if "meimei" in runner_id.lower() or "meimei" in title.lower():
        return f"梅梅的电脑上的 {tool}"
    if title:
        return title
    return f"{runner_id} 上的 {tool}"


def load_runner_record(bundle: Bundle, runner_id: str) -> dict[str, Any]:
    direct = bundle.root / "runners" / f"{runner_id}.md"
    if direct.exists():
        return load_object(direct)
    runners_dir = bundle.root / "runners"
    if not runners_dir.exists():
        return {}
    for path in runners_dir.glob("*.md"):
        try:
            record = load_object(path)
        except Exception:
            continue
        if str(record.get("runnerId", "")).strip() == runner_id:
            return record
    return {}


def build_feishu_response(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> dict[str, Any]:
    text = incoming["text"].strip()
    card = card_for_menu_text(text, incoming)
    if card:
        return {"msg_type": "interactive", "card": card, "reply": card_fallback_text(card)}
    local_intent = classify_local_intent(text)
    if local_intent and local_intent.intent == "status_query":
        record_local_intent_decision(bundle, incoming, local_intent)
        summary = project_status_summary(bundle, local_intent.fields.get("projectName", ""))
        return {"msg_type": "interactive", "card": project_status_card(summary), "reply": render_project_status_text(summary)}
    return {"msg_type": "text", "reply": build_reply(bundle, incoming, settings)}


def card_fallback_text(card: dict[str, Any]) -> str:
    header = card.get("header", {})
    title = header.get("title", {}) if isinstance(header, dict) else {}
    content = title.get("content", "表单") if isinstance(title, dict) else "表单"
    return f"{content}：请在飞书卡片中填写并提交。"


def card_for_menu_text(text: str, incoming: dict[str, str]) -> dict[str, Any] | None:
    stripped = text.strip()
    selection = re.sub(r"\s+", "", stripped).lower()
    if stripped in {"创建项目", "新建项目", "立项"}:
        return project_create_card()
    if selection in {"a", "选a", "选择a", "a.", "a。"} or stripped in {"已有仓库接入", "接入已有仓库", "已有仓库"}:
        return project_create_card("existing")
    if selection in {"b", "选b", "选择b", "b.", "b。"} or stripped in {"从头创建新项目", "从零创建新项目", "新建仓库", "没有仓库"}:
        return project_create_card("new")
    if stripped in {"查知识", "检索知识", "搜索知识"}:
        return knowledge_search_card()
    if stripped in {"记录知识", "记录资料", "沉淀知识", "沉淀资料"}:
        return material_capture_card()
    if stripped in {"会议纪要", "记录会议"}:
        return meeting_notes_card()
    if stripped in {"申请工具", "申请技能", "申请工具/技能", "登记工具", "登记技能"}:
        return tool_skill_request_card()
    if stripped in {"召唤 Agent", "找 Agent", "组建 Agent 团队", "组队"}:
        return agent_team_card()
    if stripped in {"组织讨论", "Agent 讨论", "发起讨论", "需求讨论", "技术方案讨论"}:
        return discussion_create_card()
    if stripped in {"绑定项目群", "项目群绑定", "绑定群"} and not is_private_chat(incoming):
        return bind_project_group_card()
    if stripped in {"项目交接", "交接"}:
        return project_handoff_card()
    return None


def is_private_chat(incoming: dict[str, str]) -> bool:
    return incoming.get("chatType") == "p2p"


def handle_dangerous_intent(incoming: dict[str, str], text: str) -> str:
    normalized = text.strip().lower()
    destructive = any(term in normalized for term in ["删除", "删掉", "清空", "清除", "重置", "销毁", "destroy", "delete", "reset", "wipe"])
    protected_target = any(term in normalized for term in ["知识库", "知识工程", "体系", "项目", "权限", "数据", "仓库", "agent hub", "core"])
    if not (destructive and protected_target):
        return ""
    return "\n".join(
        [
            "这是高风险操作，我不能直接执行。",
            "我可以帮你生成变更/归档/清理申请，说明目标、范围、原因和影响。",
            "需要项目 owner 或知识工程 owner 审批后，才允许由受控流程处理。",
            "请补充：对象、原因、保留范围、期望完成时间。",
        ]
    )


def handle_menu_shortcut(incoming: dict[str, str], text: str) -> str:
    stripped = text.strip()
    selection = re.sub(r"\s+", "", stripped).lower()
    if stripped in {"新手引导", "我该怎么开始", "开始使用", "使用手册", "完整手册"}:
        return help_text(incoming)
    if stripped in {"创建项目", "新建项目", "立项"}:
        return project_creation_entry_text()
    if selection in {"a", "选a", "选择a", "a.", "a。"} or stripped in {"已有仓库接入", "接入已有仓库", "已有仓库"}:
        return existing_repo_project_entry_text()
    if selection in {"b", "选b", "选择b", "b.", "b。"} or stripped in {"从头创建新项目", "从零创建新项目", "新建仓库", "没有仓库"}:
        return new_repo_project_entry_text()
    if stripped in {"召唤 Agent", "找 Agent", "组建 Agent 团队", "组队"}:
        return agent_team_entry_text()
    if stripped in {"查知识", "检索知识", "搜索知识"}:
        return knowledge_search_entry_text()
    if stripped in {"记录知识", "记录资料", "沉淀知识", "沉淀资料"}:
        return knowledge_capture_entry_text()
    if stripped in {"会议纪要", "记录会议"}:
        return meeting_notes_entry_text()
    if stripped in {"申请 token", "申请Token", "申请知识工程 token"}:
        return token_entry_text(incoming)
    if stripped in {"申请工具", "申请技能", "申请工具/技能", "登记工具", "登记技能"}:
        return tool_skill_entry_text()
    if stripped in {"绑定项目群", "项目群绑定", "绑定群"}:
        return bind_project_group_entry_text(incoming)
    if stripped in {"项目交接", "交接"}:
        return project_handoff_entry_text()
    return ""


def is_ambiguous_short_input(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    compact = re.sub(r"\s+", "", stripped)
    if len(compact) <= 1:
        return True
    if re.fullmatch(r"[A-Za-z0-9]{1,2}", compact):
        return True
    return False


def ambiguous_short_input_text() -> str:
    return "\n".join(
        [
            "我还不能确定你要做什么，所以不会拿这个去检索知识库。",
            "",
            "如果你是在创建项目，请回复：",
            "A. 已有仓库接入",
            "B. 从头创建新项目",
            "",
            "如果你要查知识，请发送：查知识：<你的问题>。",
        ]
    )


def project_creation_entry_text() -> str:
    return "\n".join(
        [
            "项目启动卡",
            "我会帮你创建项目草稿，并把真实项目启动需要的事项一起串起来：项目 Owner、主责 Agent、默认 Runner、代码仓库、项目群、初始化任务、审批。",
            "",
            "请选择一种情况继续，或直接填写我发出的交互卡：",
            "A. 已有仓库接入",
            "创建项目：已有仓库 <Git URL>，项目Owner <姓名/手机号/邮箱>，项目名称 <可选>，项目目标 <可选>，主责Agent <可选>，项目群 <后续确认/需要创建或绑定/暂不需要>",
            "",
            "B. 从头创建新项目",
            "创建项目：项目名称 <名称>，项目Owner <姓名/手机号/邮箱>，项目目标 <目标>，主责Agent <可选>，项目群 <后续确认/需要创建或绑定/暂不需要>",
            "",
            "我会先生成启动卡和项目草稿，进入 owner 审批；仓库创建、群创建、Agent 拉入、权限开通会作为审批后的执行清单，不会越权直接做。",
        ]
    )


def existing_repo_project_entry_text() -> str:
    return "\n".join(
        [
            "已选择：已有仓库接入",
            "这表示项目代码或仓库已经存在，我会帮你把它纳入项目启动流程，而不是重新创建仓库。",
            "",
            "请补齐这张项目启动卡：",
            "创建项目：已有仓库 <Git URL>，项目Owner <姓名/手机号/邮箱>，项目名称 <可选>，项目目标 <可选>，主责Agent <可选>，项目群 <后续确认/需要创建或绑定/暂不需要>",
            "",
            "后续会做：登记项目、绑定仓库、检查 README/AGENTS/目录结构、确认 Agent team、创建或绑定项目群、进入 owner 审批。",
        ]
    )


def new_repo_project_entry_text() -> str:
    return "\n".join(
        [
            "已选择：从头创建新项目",
            "这表示本地和公司知识工程里还没有这个项目，我会帮你准备项目启动和仓库创建流程。",
            "",
            "请补齐这张项目启动卡：",
            "创建项目：项目名称 <名称>，项目Owner <姓名/手机号/邮箱>，项目目标 <目标>，主责Agent <可选>，项目群 <后续确认/需要创建或绑定/暂不需要>",
            "",
            "后续会做：登记项目、发起 owner 审批、按项目名称生成仓库名、申请创建仓库、初始化 README/AGENTS/目录结构、创建或绑定项目群、确认 Agent team。",
        ]
    )


def agent_team_entry_text() -> str:
    return "\n".join(
        [
            "Agent team 编组卡",
            "我会先判断项目阶段和目标，再建议需要哪些 Agent、人类角色、工具和交付物。",
            "",
            "请按这个格式发：",
            "组建 Agent 团队：项目 <项目名称>，阶段 <想法/需求/开发/测试/运营/交接>，目标 <要完成什么>，期望输出 <方案/代码/内容/分析/运营动作>，已有成员 <可选>",
            "",
            "确认后我会输出：推荐 Agent、职责边界、协作顺序、需要的工具/技能、需要 owner 确认的风险项。",
        ]
    )


def knowledge_search_entry_text() -> str:
    return "\n".join(
        [
            "知识检索卡",
            "请直接问我要查的知识。",
            "我会在服务端快速检索已审核知识，并给出来源；找不到可靠答案会告诉你缺什么资料。",
            "",
            "如果是项目问题，可以写：",
            "查知识：项目 <项目名称>，问题 <你的问题>",
            "",
            "例如：",
            "- 飞书卡片 JSON 2.0 怎么写？",
            "- Agent Ring 怎么回填任务结果？",
            "- 会议纪要为什么不能直接入知识库？",
        ]
    )


def knowledge_capture_entry_text() -> str:
    return "\n".join(
        [
            "知识沉淀卡",
            "我会先判断资料是公共知识还是项目知识，再登记原文并创建处理任务；通过 Review 后才会进入可复用知识。",
            "请先选择：公共知识/通用经验，或项目资料/项目知识。",
            "",
            "项目知识：",
            "资料：项目 <项目名称>\n<原文、链接或文件说明>",
            "",
            "公共知识：",
            "沉淀：<原文、结论、证据、适用范围、限制>",
        ]
    )


def meeting_notes_entry_text() -> str:
    return "\n".join(
        [
            "会议纪要沉淀卡",
            "我会先登记会议纪要并创建知识沉淀任务，由中央调度器分配给匹配的 Agent Ring Runner，再进入 Review。",
            "",
            "请按这个格式发：",
            "会议纪要：项目 <项目名称>\n参会人：<姓名>\n结论：<内容>\n待办：<负责人-事项-时间>\n风险：<内容>",
        ]
    )


def token_entry_text(incoming: dict[str, str]) -> str:
    if not is_private_chat(incoming):
        return "访问凭证和 Agent Ring 接入只能私聊申请和处理。请私聊我说明：要接入什么工具/工作台、用途、适用项目和负责人。"
    return "\n".join(
        [
            "这个快捷入口已升级为访问凭证 / Agent Ring 接入申请。",
            "它不建议放在一级菜单里。普通员工需要工具时，优先走“申请工具/技能”；我会判断是否需要访问凭证。",
            "",
            "如果你确实需要接入本地工具、Agent Ring、模型 API 或项目服务，请私聊按这个格式发：",
            "访问凭证申请：使用人 <姓名>，用途 <本地开发/自动化/项目接入>，默认项目 <项目名称>，接入对象 <Codex/Claude/Agent Ring/模型API/其他>，凭证类型 <中央API/Runner注册/本地工具/模型API/项目服务>",
            "",
            "中央处理器只记录 secretRef、授权范围和审计；本地工具或项目服务 token 由 Secret Manager 或 Agent Ring 本地安全存储管理。",
        ]
    )


def plain_text(content: str) -> dict[str, str]:
    return {"tag": "plain_text", "content": content}


def card_input(name: str, label: str, placeholder: str, multiline: bool = False, required: bool = True) -> dict[str, Any]:
    label_text = label
    if not required and "可选" not in label_text:
        label_text = f"{label_text}，可选"
    placeholder_text = placeholder
    if multiline and "可分行" not in placeholder_text:
        placeholder_text = f"{placeholder_text}；可分行填写"
    return {
        "tag": "input",
        "name": name,
        "element_id": name,
        "label": plain_text(label_text),
        "placeholder": plain_text(placeholder_text),
        "default_value": "",
    }


def card_select(name: str, label: str, placeholder: str, options: list[tuple[str, str]], default: str = "") -> dict[str, Any]:
    element: dict[str, Any] = {
        "tag": "select_static",
        "name": name,
        "element_id": name,
        "placeholder": plain_text(f"{label}：{placeholder}"),
        "options": [{"text": plain_text(text), "value": value} for text, value in options],
    }
    if default:
        element["initial_option"] = default
    return element


def project_group_select(default: str = "later") -> dict[str, Any]:
    return card_select("createGroup", "是否创建或绑定项目群", "请选择", PROJECT_GROUP_OPTIONS, default)


def value_to_option(options: list[tuple[str, str]], value: str) -> dict[str, Any]:
    for text, option_value in options:
        if option_value == value:
            return {"text": plain_text(text), "value": option_value}
    return {"text": plain_text(value), "value": value}


def encode_form_submit_name(action: str, extra: dict[str, Any] | None = None) -> str:
    parts = [action]
    for key, value in (extra or {}).items():
        parts.append(f"{key}={value}")
    return "|".join(parts)


def parse_form_submit_name(name: str) -> tuple[str, dict[str, str]]:
    parts = [part for part in name.split("|") if part]
    if not parts:
        return "", {}
    params: dict[str, str] = {}
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        params[key] = value
    return parts[0], params


def submit_button(action: str, text: str, extra: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "tag": "button",
        "text": plain_text(text),
        "type": "primary",
        "name": encode_form_submit_name(action, extra),
        "form_action_type": "submit",
        "value": {"action": action, **(extra or {})},
    }


def callback_button(action: str, text: str, extra: dict[str, str] | None = None, button_type: str = "primary") -> dict[str, Any]:
    return {
        "tag": "button",
        "text": plain_text(text),
        "type": button_type,
        "value": {"action": action, **(extra or {})},
        "behaviors": [{"type": "callback", "value": {"action": action, **(extra or {})}}],
    }


def interactive_card(title: str, elements: list[dict[str, Any]], template: str = "blue") -> dict[str, Any]:
    body_elements: list[dict[str, Any]] = []
    form_elements: list[dict[str, Any]] = []
    form_tags = {"input", "select_static"}
    for element in elements:
        button_action = ""
        if element.get("tag") == "button" and isinstance(element.get("value"), dict):
            button_action = str(element["value"].get("action", ""))
        if element.get("tag") in form_tags or (element.get("tag") == "button" and button_action.endswith("_submit")):
            form_elements.append(element)
        else:
            body_elements.append(element)
    if form_elements:
        body_elements.append(
            {
                "tag": "form",
                "element_id": "form_main",
                "name": "form_main",
                "elements": form_elements,
            }
        )
    return {
        "schema": "2.0",
        "config": {"wide_screen_mode": True},
        "header": {"template": template, "title": plain_text(title)},
        "body": {"direction": "vertical", "elements": body_elements},
    }


def project_create_card(default_repo_mode: str = "") -> dict[str, Any]:
    if not default_repo_mode:
        return project_create_choice_card()
    return project_create_details_card(default_repo_mode)


def project_create_choice_card() -> dict[str, Any]:
    return interactive_card(
        "创建项目",
        [
            {"tag": "markdown", "content": "先选项目来源。我会按场景减少填写项；已有仓库会优先从 Git 地址推断项目名、仓库名和初始化状态。"},
            callback_button("project_create_mode", "已有仓库接入/老项目迁移", {"repoMode": "existing"}, "primary"),
            callback_button("project_create_mode", "从头创建新项目", {"repoMode": "new"}, "default"),
        ],
    )


def project_create_details_card(repo_mode: str) -> dict[str, Any]:
    if repo_mode == "existing":
        return interactive_card(
            "已有仓库接入",
            [
                {"tag": "markdown", "content": "只填 Git 地址和项目 Owner。项目名称、仓库名、README/AGENTS/目录结构会在接入检查里自动推断和补齐。"},
                card_input("repoUrl", "Git 地址", "例如：https://github.com/company/project.git 或 git@github.com:company/project.git"),
                card_input("projectOwner", "项目 Owner", "例如：梅晓华 / 手机号 / 邮箱 / open_id"),
                card_input("projectName", "项目名称，可选", "不填时从仓库名推断", required=False),
                card_input("goal", "项目目标，可选", "不填时创建接入检查任务后补齐", required=False),
                card_input("leadAgent", "主责 Agent，可选", "不填时由项目经理 Agent 建议", required=False),
                project_group_select("later"),
                submit_button("project_create_submit", "开始接入", {"repoMode": "existing"}),
            ],
        )
    return interactive_card(
        "创建项目启动卡",
        [
            {"tag": "markdown", "content": "从头创建只需要最小启动信息。系统会按项目名称生成仓库名；Runner、Agent team、项目群和权限会进入启动清单后续确认。"},
            card_input("projectName", "项目名称", "例如：桢知 Agent Hub 与知识工程中枢"),
            card_input("projectOwner", "项目 Owner", "责任归属，例如：梅晓华 / 手机号 / 邮箱 / open_id"),
            card_input("goal", "项目目标", "一句话说明要解决什么问题"),
            card_input("leadAgent", "主责 Agent，可选", "不填时由项目经理 Agent 建议", required=False),
            project_group_select("later"),
            submit_button("project_create_submit", "提交启动卡", {"repoMode": "new"}),
        ],
    )


def task_acceptance_card(task_id: str, title: str, result_summary: str, human_required: bool = True) -> dict[str, Any]:
    return interactive_card(
        "任务结果验收",
        [
            {"tag": "markdown", "content": f"任务 `{task_id}` 已完成，需验收后才会进入下一岗位。\n\n**交付**：{title}\n\n**结果摘要**：{result_summary}"},
            card_input("reason", "验收意见，可选", "通过、要求修改或拒绝的原因", required=False),
            submit_button("task_acceptance_accept", "验收通过", {"taskId": task_id, "human": "true" if human_required else "false"}),
            submit_button("task_acceptance_changes", "要求修改", {"taskId": task_id, "human": "true" if human_required else "false"}),
            submit_button("task_acceptance_reject", "拒绝交付", {"taskId": task_id, "human": "true" if human_required else "false"}),
        ],
    )


def discussion_decision_required_card(discussion_id: str, title: str, summary: str, open_questions: list[str] | None = None) -> dict[str, Any]:
    questions = "\n".join(f"- {item}" for item in open_questions or []) or "- 见讨论汇总"
    return interactive_card(
        "讨论需要人类决策",
        [
            {"tag": "markdown", "content": f"讨论 `{discussion_id}` 已完成 Agent 回合，但仍有待决问题。\n\n**主题**：{title}\n\n**摘要**：{summary}\n\n**待决问题**：\n{questions}"},
        ],
        "orange",
    )


def material_capture_card(scope: str = "") -> dict[str, Any]:
    if scope == "project":
        return project_material_capture_card()
    if scope == "common":
        return common_knowledge_capture_card()
    return material_capture_choice_card()


def material_capture_choice_card() -> dict[str, Any]:
    return interactive_card(
        "记录知识",
        [
            {"tag": "markdown", "content": "先确认这份资料的归属。项目知识会挂到具体项目上下文；公共知识会进入公司级知识工程，由知识工程 Agent 处理。两类都会保存原文、创建处理任务，并在 Review 后才可复用。"},
            callback_button("material_capture_scope", "公共知识/通用经验", {"scope": "common"}, "primary"),
            callback_button("material_capture_scope", "项目资料/项目知识", {"scope": "project"}, "default"),
        ],
    )


def project_material_capture_card() -> dict[str, Any]:
    return interactive_card(
        "记录项目资料",
        [
            {"tag": "markdown", "content": "我会保存原文并创建知识/能力处理任务。总结、结构化知识、Agent Skill、Workflow 或 Tool 建议由后续 Agent Ring 任务处理。"},
            card_input("projectName", "项目名称", "请输入项目名称"),
            card_input("content", "资料原文", "粘贴资料原文、链接说明或文件说明", multiline=True),
            card_select(
                "processingAction",
                "处理方式",
                "选择知识或 Agent 能力产出",
                [
                    ("沉淀知识", "knowledge_extract"),
                    ("提炼 Agent Skill", "skill_extract"),
                    ("提炼 Agent Workflow", "workflow_extract"),
                    ("生成 Tool 注册建议", "tool_candidate"),
                    ("创建能力发布草案", "capability_release_draft"),
                ],
                "knowledge_extract",
            ),
            submit_button("material_capture_submit", "提交项目资料", {"scope": "project"}),
        ],
    )


def common_knowledge_capture_card() -> dict[str, Any]:
    return interactive_card(
        "记录公共知识",
        [
            {"tag": "markdown", "content": "公共知识不绑定具体项目，会进入公司级知识工程处理。请尽量提供原文、来源链接、结论、适用范围和限制；我会保存原文并创建知识/能力处理任务。"},
            card_input("title", "标题，可选", "不填时由处理 Agent 从内容中提炼", required=False),
            card_input("content", "资料原文", "粘贴资料原文、链接说明或文件说明", multiline=True),
            card_input("sourceRef", "来源，可选", "例如：飞书文档链接、会议纪要链接、网页、聊天消息说明", required=False),
            card_input("scopeNote", "适用范围，可选", "例如：飞书卡片实现、Agent 工作流、知识工程通用规则", required=False),
            card_select(
                "processingAction",
                "处理方式",
                "选择知识或 Agent 能力产出",
                [
                    ("沉淀知识", "knowledge_extract"),
                    ("提炼 Agent Skill", "skill_extract"),
                    ("提炼 Agent Workflow", "workflow_extract"),
                    ("生成 Tool 注册建议", "tool_candidate"),
                    ("创建能力发布草案", "capability_release_draft"),
                ],
                "knowledge_extract",
            ),
            submit_button("material_capture_submit", "提交资料", {"scope": "common"}),
        ],
    )


def knowledge_search_card() -> dict[str, Any]:
    return interactive_card(
        "知识检索",
        [
            {"tag": "markdown", "content": "直接写你要查的问题。我会快速检索已审核知识并给出来源。"},
            card_input("projectName", "项目名称，可选", "项目 <项目名称>", required=False),
            card_input("question", "要查什么知识", "例如：Agent Ring 怎么回填任务结果？", multiline=True),
            submit_button("knowledge_search_submit", "提交问题"),
        ],
    )


def meeting_notes_card() -> dict[str, Any]:
    return interactive_card(
        "记录会议纪要",
        [
            {"tag": "markdown", "content": "我会登记会议纪要原文并创建知识沉淀任务，通过 Review 后才会进入可复用知识。"},
            card_input("projectName", "项目名称", "请输入项目名称"),
            card_input("participants", "参会人", "例如：梅晓华、产品 Agent、后端 Agent", required=False),
            card_input("conclusion", "结论", "会议确认的结论", multiline=True),
            card_input("todos", "待办", "负责人-事项-时间", multiline=True, required=False),
            card_input("risks", "风险", "风险或不确定项", multiline=True, required=False),
            submit_button("meeting_notes_submit", "提交会议纪要"),
        ],
    )


def agent_team_card() -> dict[str, Any]:
    return interactive_card(
        "组建 Agent 团队",
        [
            {"tag": "markdown", "content": "填写目标后，我会生成 Agent 编组建议和需要确认的风险项。具体工程任务由中央调度器再分配给 Runner。"},
            card_input("projectName", "项目名称", "请输入项目名称"),
            card_select(
                "stage",
                "项目阶段",
                "请选择",
                [("想法", "想法"), ("需求", "需求"), ("开发", "开发"), ("测试", "测试"), ("运营", "运营"), ("交接", "交接")],
                "需求",
            ),
            card_input("goal", "目标", "这次要完成什么", multiline=True),
            card_input("expectedOutput", "期望输出", "例如：方案/代码/内容/分析/运营动作", required=False),
            card_input("existingMembers", "已有成员", "已有 Agent、Runner 或协作方，可留空", required=False),
            submit_button("agent_team_submit", "提交编组需求"),
        ],
    )


def discussion_create_card() -> dict[str, Any]:
    return interactive_card(
        "发起 Agent 讨论",
        [
            {"tag": "markdown", "content": "用于产品、研发、测试等 Agent 围绕需求或方案进行回合制讨论。讨论过程会记录、通知，并产出决策或后续任务。"},
            card_input("projectName", "项目名称", "不填则作为公司级讨论", required=False),
            card_input("title", "讨论标题", "例如：AI Agent 搭建需求实现方案讨论"),
            card_input("topic", "讨论问题", "要讨论什么、需要形成什么结论", multiline=True),
            card_input("participants", "参与 Agent，可选", "逗号分隔；默认项目经理/产品/研发/测试", required=False),
            card_input("relatedTaskId", "关联任务，可选", "如果是某个任务触发，填写任务编号", required=False),
            submit_button("discussion_create_submit", "创建讨论会"),
        ],
    )


def bind_project_group_card() -> dict[str, Any]:
    return interactive_card(
        "绑定项目群",
        [
            {"tag": "markdown", "content": "绑定后，本群会进入项目助手模式。请确认这是项目正式协作群，并且项目 Owner 同意绑定。"},
            card_input("projectName", "项目名称", "请输入项目名称"),
            card_select("ownerConfirmed", "Owner 已确认", "请选择", [("是", "是"), ("否", "否"), ("待确认", "待确认")], "待确认"),
            card_input("note", "备注", "群用途、范围或补充说明", multiline=True, required=False),
            submit_button("bind_project_group_submit", "提交绑定申请"),
        ],
    )


def project_handoff_card() -> dict[str, Any]:
    return interactive_card(
        "项目交接",
        [
            {"tag": "markdown", "content": "我会把交接整理成清单：阶段成果、仓库、文档、知识草稿、AgentRun、待办、权限关闭、接手团队。"},
            card_input("projectName", "项目名称", "请输入项目名称"),
            card_input("currentStage", "当前阶段", "例如：开发完成 / 测试中 / 运营接手"),
            card_input("handoffTo", "接手方", "接手 Agent、Runner、团队或项目"),
            card_input("handoffScope", "交接范围", "仓库/文档/群/账号/待办/运营资料", multiline=True),
            card_input("operationGoal", "继续目标", "交接后下一阶段要完成什么", multiline=True, required=False),
            submit_button("project_handoff_submit", "提交交接卡"),
        ],
        template="turquoise",
    )


def tool_skill_request_card() -> dict[str, Any]:
    return interactive_card(
        "申请工具/技能",
        [
            {"tag": "markdown", "content": "工具能不能调用、调用结果能不能写入项目、能不能进入知识库，是三件事。我会先生成草稿并进入 Review。"},
            card_input("name", "名称", "工具或技能名称"),
            card_select("assetType", "类型", "请选择", [("工具", "tool"), ("技能", "skill")], "tool"),
            card_input("owner", "Owner", "负责人、Agent 或团队"),
            card_input("purpose", "用途", "解决什么问题", multiline=True),
            card_select("scope", "适用范围", "请选择", [("公司通用", "company"), ("项目私有", "project")], "company"),
            card_input("projectName", "适用项目", "项目私有时填写", required=False),
            card_input("io", "输入输出", "输入、输出、依赖和结果去向", multiline=True, required=False),
            card_select("risk", "风险等级", "请选择", [("L1 只读/低风险", "L1"), ("L2 写草稿/中风险", "L2"), ("L3 外部系统/高风险", "L3")], "L2"),
            submit_button("tool_skill_submit", "提交申请"),
        ],
        template="purple",
    )


def tool_skill_entry_text() -> str:
    return "\n".join(
        [
            "工具/技能申请卡",
            "工具能不能调用、调用结果能不能写入项目、能不能进入知识库，是三件事，我会分开审核。",
            "",
            "请按这个格式发：",
            "申请工具/技能：名称 <名称>，类型 <工具/技能>，owner <负责人>，用途 <解决什么问题>，适用范围 <公司通用/项目私有>，输入输出 <说明>，风险 <是否写数据/发消息/调用外部系统>",
            "",
            "确认后我会生成 ToolAsset / SkillAsset 草稿，进入 Review 和 owner 审批。",
        ]
    )


def bind_project_group_entry_text(incoming: dict[str, str]) -> str:
    if is_private_chat(incoming):
        return "绑定项目群需要在目标项目群里操作。请把我拉进项目群后，在群里发送：绑定项目群：项目 <项目名称>。"
    return "\n".join(
        [
            "项目群绑定卡",
            "绑定后，本群会进入项目助手模式：资料、会议纪要、Agent 协作、待审核、交接都会默认围绕这个项目处理。",
            "",
            "请发送：",
            "绑定项目群：项目 <项目名称>",
            "",
            "绑定前请确认：这个群是项目正式协作群，群主或项目 owner 同意绑定。",
        ]
    )


def project_handoff_entry_text() -> str:
    return "\n".join(
        [
            "项目交接卡",
            "我会把交接做成清单：阶段成果、仓库、文档、知识草稿、AgentRun、待办、权限关闭、接手团队。",
            "",
            "请按这个格式发：",
            "项目交接：项目 <项目名称>，当前阶段 <阶段>，接手人/团队 <姓名/团队>，交接范围 <仓库/文档/群/账号/待办>，继续运营目标 <目标>",
            "",
            "确认后我会生成交接草稿，交给项目 owner 确认。",
        ]
    )


def help_text(incoming: dict[str, str]) -> str:
    if is_private_chat(incoming):
        return agent_hub_help_text()
    return project_assistant_help_text()


def agent_hub_help_text() -> str:
    return "\n".join(
        [
            "我是桢知 Agent Hub，公司 Agent 团队入口。",
            "你不用懂知识工程，也不用记命令。说目标，我来判断该找谁、建什么、走哪条流程。",
            "",
            "你现在可能要做的是：",
            "有想法 -> 创建项目 -> 组建 Agent 团队 -> 项目群协作",
            "有问题 -> 查知识 -> 给答案和来源",
            "有资料 -> 登记材料 -> 创建任务 -> 本地处理 -> Review -> 进入知识库",
            "要工具 -> 申请工具/技能 -> owner 审批",
            "",
            "直接照着发：",
            "1. 我想做一个 <目标>，需要哪些人和 Agent？",
            "2. 创建项目：项目名称 <名称>，项目负责人 <姓名/手机号/邮箱>",
            "3. 查一下 <问题>",
            "4. 沉淀：<结论、资料或踩坑经验>",
            "5. 申请工具/技能：<名称、用途、owner、适用项目>",
            "",
            "完整说明见《桢知 Agent Hub 使用手册》。",
            "安全边界：我不会直接删除知识库、改权限、发客户承诺或执行高风险操作；这类事情会先生成申请，交给 owner 审批。",
        ]
    )


def project_assistant_help_text() -> str:
    return "\n".join(
        [
            "我是这个群里的项目助手，会围绕当前项目帮大家协作。",
            "如果这个群还没绑定项目，先发：绑定项目群：项目 <项目名称>",
            "",
            "本群常见协作：",
            "会议/资料 -> 登记材料 -> 创建任务 -> 项目 owner 本地处理 / Review",
            "需求/问题 -> 召唤合适 Agent -> 给出建议和待确认项",
            "阶段结束 -> 交接清单 -> 接手团队继续运营",
            "",
            "直接照着发：",
            "1. 资料：项目 <项目名称>\\n<内容>",
            "2. 会议纪要：项目 <项目名称>\\n<内容>",
            "3. 请产品 Agent 看一下这个需求",
            "4. 项目交接：<阶段、接手人、资料范围>",
            "5. 待审核",
            "",
            "完整说明见《桢知 Agent Hub 使用手册》。",
            "安全边界：我可以整理草稿和发起审批，但不会直接发布正式知识、改权限、删除项目或执行高风险工具。",
        ]
    )


def no_reliable_answer_text(incoming: dict[str, str]) -> str:
    if is_private_chat(incoming):
        return "\n".join(
            [
                "我没有在已审核知识里找到可靠答案。",
                "你可以换个关键词，或让我创建项目、召唤 Agent、申请工具/技能、沉淀知识。",
                "发送“帮助”查看 Agent Hub 入口。",
            ]
        )
    return "\n".join(
        [
            "我没有在已审核知识里找到可靠答案。",
            "项目内可以发送“资料：项目 <项目名称>\\n<内容>”或“会议纪要：项目 <项目名称>\\n<内容>”创建处理任务。",
            "发送“帮助”查看项目助手入口。",
        ]
    )


def unique_retrieval_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = str(row.get("path") or row.get("sourceRef") or row.get("chunkId") or "")
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def credential_field(text: str, label: str) -> str:
    for pattern in [rf"{label}\s*[：:]\s*([^，,\n]+)", rf"{label}\s+([^，,\n]+)"]:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def credential_type_from_text(text: str) -> str:
    explicit = credential_field(text, "凭证类型")
    lowered = (explicit or text).lower()
    if "runner" in lowered or "agent ring" in lowered or "工作台" in text:
        return "runner_registration"
    if "模型" in text or "model" in lowered or "llm" in lowered:
        return "model_api"
    if "codex" in lowered or "claude" in lowered or "本地工具" in text:
        return "local_tool"
    if "项目服务" in text or "第三方" in text:
        return "project_service"
    return "central_api"


def credential_secret_ref(requester: str, credential_type: str) -> str:
    return f"secretref://zhenzhi/{slug(credential_type)}/{slug(requester or 'unknown')}"


def credential_setup_message(secret_ref: str, credential_type: str) -> str:
    return "\n".join(
        [
            "你的访问凭证申请已通过。",
            f"凭证类型：{credential_type}",
            f"secretRef：{secret_ref}",
            "下一步：在 Secret Manager 或 Agent Ring 本地安全存储中配置真实 secret。",
            "中央处理器只保存 secretRef、授权范围和审计记录，不会在飞书里发送真实 token/key。",
            "本地初始化仍可执行：bash scripts/setup-teammate.sh --user-id <你的名字> --ai-tool codex",
        ]
    )


def token_request_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> str:
    if incoming.get("chatType") != "p2p":
        return "我识别到访问凭证申请。为避免泄露，请私聊我发送“申请知识工程 token”；我不会在群里处理或发送 secret。"
    requester = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    text = incoming.get("text", "")
    credential_type = credential_type_from_text(text)
    project_name = credential_field(text, "默认项目") or credential_field(text, "项目")
    project_id = slug(project_name) if project_name and re.search(r"[A-Za-z0-9]", project_name) else ""
    purpose = credential_field(text, "用途") or "知识工程访问凭证申请"
    request_path = create_access_credential_request(
        bundle,
        requester=requester,
        purpose=purpose,
        project_id=project_id,
        credential_type=credential_type,
        credential_scope="personal_setup" if credential_type in {"central_api", "local_tool", "runner_registration"} else "project",
        risk="L2" if credential_type in {"central_api", "runner_registration", "model_api"} else "L1",
        expiry=credential_field(text, "有效期"),
        approver=first_mentioned_open_id(incoming) or "",
    )
    approval_line = trigger_approval_for_target(
        bundle,
        settings,
        incoming,
        approval_type=APPROVAL_TYPE_AGENT_TOKEN,
        target_ref=str(request_path.relative_to(bundle.root)),
        requested_status="approved",
        project_id=project_id,
        project_name=project_name or "Access Credential",
        owner_open_id=first_mentioned_open_id(incoming) or incoming.get("openId", ""),
        summary=f"访问凭证申请：{credential_type}；用途：{purpose}",
    )
    if not settings.token_auto_approve:
        return f"已收到你的访问凭证申请。我已记录申请单：{request_path.relative_to(bundle.root)}。\n{approval_line}"
    secret_ref = credential_secret_ref(requester, credential_type)
    return "已自动批准访问凭证申请。\n" + credential_setup_message(secret_ref, credential_type)


def parse_project_init(text: str) -> dict[str, str]:
    normalized = text.strip()
    if not re.search(r"(立项|项目立项|立项申请|创建项目|创建一个项目|建项目|新建项目|新增项目|立个项目)", normalized):
        return {}
    name = extract_named_value(normalized, ["项目名称", "项目名", "项目"])
    if not name:
        name_patterns = [
            r"(?:名字|名称|项目名|项目名称)\s*(?:叫做|叫|是|为|:|：)\s*(?P<name>[^\n，,。；;]+)",
            r"(?:创建一个项目|创建项目|建项目|新建项目|新增项目|立个项目|立项申请|立项)[:：\s]+(?P<name>[^\n，,。；;]+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, normalized)
            if match:
                name = cleanup_project_name(match.group("name"))
                break
    owner_name = extract_named_value(normalized, ["项目Owner", "项目 Owner", "项目负责人", "负责人", "owner", "Owner", "所属人"])
    if not owner_name:
        owner_match = re.search(r"(?:项目Owner|项目 Owner|项目负责人|负责人|所属人)\s*(?:叫做|叫|是|为)\s*(?P<owner>[A-Za-z0-9._\-\u4e00-\u9fff]+)", normalized)
        if owner_match:
            owner_name = owner_match.group("owner").strip()
    repo_url = extract_named_value(normalized, ["已有仓库", "仓库地址", "代码仓库", "仓库", "repo", "Repo"])
    repo_name = extract_named_value(normalized, ["新建仓库", "仓库名", "repoName", "RepoName"])
    repo_mode = ""
    if re.search(r"(已有仓库|已有 repo|已有Repo|接入仓库)", normalized, re.IGNORECASE):
        repo_mode = "existing"
    elif re.search(r"(新建仓库|创建仓库|从头创建|从零开始|没有仓库)", normalized, re.IGNORECASE):
        repo_mode = "new"
    elif repo_url.startswith(("http://", "https://", "git@")):
        repo_mode = "existing"
    goal = extract_named_value(normalized, ["项目目标", "目标", "背景", "要解决的问题"])
    agents = extract_named_value(normalized, ["需要Agent", "需要 Agent", "需要角色", "Agent", "团队"])
    lead_agent = extract_named_value(normalized, ["主责Agent", "主责 Agent", "项目Agent", "项目 Agent"])
    default_runner = extract_named_value(normalized, ["默认Runner", "默认 Runner", "执行设备", "默认设备"])
    create_group = normalize_project_group_preference(extract_named_value(normalized, ["创建项目群", "项目群", "建群", "拉群"]))
    return {
        "projectName": name,
        "ownerName": owner_name,
        "repoMode": repo_mode,
        "repoUrl": repo_url,
        "repoName": repo_name,
        "goal": goal,
        "agents": agents,
        "leadAgent": lead_agent,
        "defaultRunner": default_runner,
        "createGroup": create_group,
    }


def normalize_project_group_preference(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return "后续确认"
    normalized = raw.lower().replace(" ", "")
    mapping = {
        "later": "后续确认",
        "pending": "后续确认",
        "后续确认": "后续确认",
        "待确认": "后续确认",
        "create_or_bind": "需要创建或绑定项目群",
        "create": "需要创建或绑定项目群",
        "bind": "需要创建或绑定项目群",
        "yes": "需要创建或绑定项目群",
        "是": "需要创建或绑定项目群",
        "需要": "需要创建或绑定项目群",
        "需要创建项目群": "需要创建或绑定项目群",
        "需要创建或绑定项目群": "需要创建或绑定项目群",
        "需要创建或绑定": "需要创建或绑定项目群",
        "创建项目群": "需要创建或绑定项目群",
        "绑定项目群": "需要创建或绑定项目群",
        "none": "暂不需要项目群",
        "no": "暂不需要项目群",
        "否": "暂不需要项目群",
        "不需要": "暂不需要项目群",
        "暂不需要": "暂不需要项目群",
        "暂不需要项目群": "暂不需要项目群",
    }
    return mapping.get(normalized, raw)


def extract_named_value(text: str, labels: list[str]) -> str:
    for label in labels:
        pattern = rf"{re.escape(label)}\s*(?:[:：]|是|为|叫做|叫)\s*(?P<value>[^\n，,。；;]+)"
        match = re.search(pattern, text)
        if match:
            return match.group("value").strip()
        loose_pattern = rf"{re.escape(label)}\s+(?P<value>[^\n，,。；;]+)"
        loose_match = re.search(loose_pattern, text)
        if loose_match:
            return loose_match.group("value").strip()
    return ""


def cleanup_project_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^(叫做|叫|是|为)\s*", "", value)
    value = re.sub(r"\s*(项目Owner|项目 Owner|项目负责人|负责人|所属人).*$", "", value).strip()
    return value.strip("。；;，, ")


def project_init_reply(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, project_intake: dict[str, str]) -> str:
    project_name = project_intake.get("projectName", "").strip()
    owner_name = project_intake.get("ownerName", "").strip()
    default_owner_to_submitter = project_intake.get("defaultOwnerToSubmitter") == "true"
    owner_open_id = first_mentioned_open_id(incoming) or (owner_name if owner_name.startswith("ou_") else "") or resolve_person_open_id(settings, owner_name) or (incoming.get("openId", "") if default_owner_to_submitter else "")
    owner_user_id = first_mentioned_user_id(incoming)
    if not owner_user_id and owner_open_id == incoming.get("openId"):
        owner_user_id = incoming.get("userId", "")
    owner_lookup_message = ""
    if not owner_open_id and owner_name:
        lookup = lookup_feishu_user_by_name(settings, owner_name)
        owner_open_id = lookup.get("openId", "")
        owner_user_id = lookup.get("userId", "")
        owner_lookup_message = lookup.get("message", "")
    if not project_name:
        return project_launch_missing_text(project_intake, ["项目名称"])
    if not owner_open_id:
        if owner_name:
            message = owner_lookup_message or f"未找到项目 Owner {owner_name}。"
            return f"{message}\n{project_launch_missing_text(project_intake, ['项目 Owner'])}"
        return project_launch_missing_text(project_intake, ["项目 Owner"])
    project_id = normalize_project_id(project_name)
    target_ref = f"projects/{slug(project_id)}/project.md"
    existing_status = project_status(bundle, project_id)
    if existing_status in FORMAL_STATUSES:
        return f"项目已存在：{project_name}\n项目ID：{project_id}\n状态：{existing_status}"
    pending_approval = find_pending_approval_for_target(bundle, target_ref)
    if pending_approval:
        return f"项目草稿已存在：{project_name}\n已发起飞书审批：{pending_approval}"
    project_path = bundle.root / target_ref
    if not project_path.exists():
        project_path = make_project(bundle, project_id, project_name, owner_open_id)
    if owner_name and not owner_name.startswith("ou_"):
        update_frontmatter_file(project_path, {"humanOwner": owner_name})
    launch_path = write_project_launch_plan(bundle, project_id, project_name, owner_open_id, project_intake)
    project_agents = ensure_default_project_agents(
        bundle,
        project_id,
        project_name,
        owner_open_id,
        project_intake.get("leadAgent", ""),
        project_intake.get("agents", ""),
        project_intake.get("goal", ""),
        project_intake.get("repoMode", ""),
    )
    init_assignee = f"agent.{slug(project_id)}.project-manager"
    init_task_path = ensure_project_initialization_task(
        bundle,
        project_id,
        project_name,
        incoming.get("openId", "") or owner_open_id,
        init_assignee,
        project_intake,
        agent_ring_enabled(),
    )
    approval_line = trigger_approval_for_target(
        bundle,
        settings,
        incoming,
        approval_type=APPROVAL_TYPE_PROJECT_INIT,
        target_ref=str(project_path.relative_to(bundle.root)),
        requested_status="verified",
        project_id=project_id,
        project_name=project_name,
        owner_open_id=owner_user_id or owner_open_id,
        summary=f"项目立项申请：{project_name}",
    )
    return "\n".join(
        [
            f"项目草稿已创建：{project_name}",
            f"项目ID：{project_id}",
            f"启动清单：{launch_path.relative_to(bundle.root)}",
            "初始化任务：已创建，审批通过后会通知接管方式。",
            f"项目 Agent：{', '.join(path.stem for path in project_agents)}",
            "Runner 状态：" + ("Agent Ring 已启用，等待自动调度。" if agent_ring_enabled() else "Agent Ring 未启用，审批通过后会提示指定执行电脑接管初始化任务。"),
            project_launch_summary(project_intake),
            approval_line,
            "",
            "审批通过后的执行顺序：",
            "1. 项目经理 Agent 确认项目范围、里程碑、Agent team。",
            "2. 处理代码仓库：已有仓库则登记并检查初始化；新项目则走仓库创建审批和初始化。",
            "3. 创建或绑定项目群，把项目 Owner、协作成员和确认后的 Agent 拉入协作。",
            "4. 初始化项目资料：README、AGENTS、项目目标、决策记录、工具/技能清单、Review 规则。",
            "5. 项目进入运行：AgentRun、资料沉淀、待审核、交接都回到这个项目上下文。",
        ]
    )


def submit_project_create_card(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, form: dict[str, str]) -> str:
    repo_mode = form.get("repoMode", "")
    if repo_mode not in {"existing", "new"}:
        repo_mode = "existing" if form.get("repoUrl") else "new" if form.get("repoName") else ""
    repo_url = form.get("repoUrl", "").strip()
    inferred_repo_name = infer_repo_name_from_url(repo_url)
    project_name = form.get("projectName", "").strip()
    if not project_name and repo_mode == "existing":
        project_name = infer_project_name_from_repo(repo_url)
    owner_name = form.get("projectOwner", "").strip() or incoming.get("openId", "")
    repo_name = form.get("repoName", "").strip()
    if not repo_name:
        repo_name = inferred_repo_name if repo_mode == "existing" else normalize_project_id(project_name) if project_name else ""
    goal = form.get("goal", "").strip()
    if not goal and repo_mode == "existing" and project_name:
        goal = f"接入已有仓库 {project_name}，完成项目初始化检查和知识工程登记。"
    intake = {
        "projectName": project_name,
        "ownerName": owner_name,
        "repoMode": repo_mode,
        "repoUrl": repo_url,
        "repoName": repo_name,
        "goal": goal,
        "agents": form.get("agents", ""),
        "leadAgent": form.get("leadAgent", ""),
        "defaultRunner": form.get("defaultRunner", ""),
        "createGroup": normalize_project_group_preference(form.get("createGroup", "")),
        "defaultOwnerToSubmitter": "true",
    }
    missing = []
    if not intake["projectName"]:
        missing.append("项目名称")
    if not intake["ownerName"]:
        missing.append("项目 Owner")
    if repo_mode == "new" and not intake["goal"]:
        missing.append("项目目标")
    if repo_mode == "existing" and not intake["repoUrl"]:
        missing.append("已有仓库地址")
    if missing:
        return project_launch_missing_text(intake, missing)
    return project_init_reply(bundle, incoming, settings, intake)


def infer_repo_name_from_url(repo_url: str) -> str:
    value = repo_url.strip().rstrip("/")
    if not value:
        return ""
    if value.startswith("git@") and ":" in value:
        value = value.rsplit(":", 1)[-1]
    else:
        parsed = urllib.parse.urlparse(value)
        value = parsed.path or value
    name = value.rsplit("/", 1)[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name.strip()


def infer_project_name_from_repo(repo_url: str) -> str:
    repo_name = infer_repo_name_from_url(repo_url)
    return repo_name.replace("_", " ").replace("-", " ").strip() or repo_name


def submit_knowledge_search_card(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, form: dict[str, str]) -> str:
    question = form.get("question", "").strip()
    if not question:
        return "还缺：问题。请在卡片里填写要查询的内容。"
    return str(run_knowledge_query(bundle, {**incoming, "text": question}, question)["reply"])


def submit_material_capture_card(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, form: dict[str, str]) -> str:
    scope = form.get("scope", "").strip() or ("project" if form.get("projectName", "").strip() else "common")
    content = form.get("content", "").strip()
    if not content:
        return "知识记录卡还缺：资料原文。请粘贴原文、链接说明或文件说明。"
    if scope == "project":
        project_name = form.get("projectName", "").strip()
        if not project_name:
            return "项目资料卡还缺：项目名称。公共知识请从“记录知识”重新选择“公共知识/通用经验”。"
        material = {
            "projectId": normalize_project_id(project_name),
            "projectRaw": project_name,
            "sourceType": "project_material",
            "body": content,
            "processingAction": form.get("processingAction", "knowledge_extract"),
        }
        _source_path, _task_path, task_id, assignee = create_project_material_task(bundle, incoming, settings, material)
        profile = material_processing_profile(material["processingAction"])
        return "\n".join(
            [
                "已接收项目资料，并创建企业 Agent 能力/知识处理任务。",
                f"项目：{project_name}",
                f"任务编号：{task_id}",
                f"处理方式：{profile['taskType']}",
                f"负责人：{assignee}",
                "当前状态：" + display_task_status("pending" if agent_ring_enabled() else "waiting_runner"),
                "后续处理：" + ("会解析原文，生成知识或 CapabilityCandidate；Review/Approval 通过后才进入企业 Agent 能力包。" if agent_ring_enabled() else "已通知负责人接管；处理完成后会回传结果并进入能力/知识 Review。"),
            ]
        )
    _source_path, _task_path, task_id, assignee = create_common_knowledge_material_task(bundle, incoming, settings, form)
    profile = material_processing_profile(form.get("processingAction", ""))
    return "\n".join(
        [
            "已接收公共知识资料，并创建企业 Agent 能力/知识处理任务。",
            f"任务编号：{task_id}",
            f"处理方式：{profile['taskType']}",
            f"负责人：{assignee}",
            "当前状态：" + display_task_status("pending" if agent_ring_enabled() else "waiting_runner"),
            "后续处理：" + ("知识工程 Agent 会解析原文，生成知识或 CapabilityCandidate；Review/Approval 通过后才进入公司级可复用知识或企业 Agent 能力包。" if agent_ring_enabled() else "已通知负责人接管；处理完成后会回传结果并进入能力/知识 Review。"),
        ]
    )


def submit_agent_team_card(form: dict[str, str]) -> str:
    project_name = form.get("projectName", "").strip()
    goal = form.get("goal", "").strip()
    missing = []
    if not project_name:
        missing.append("项目名称")
    if not goal:
        missing.append("目标")
    if missing:
        return f"Agent 编组卡还缺：{'、'.join(missing)}。"
    return "\n".join(
        [
            "已收到 Agent 编组需求。",
            f"项目: {project_name}",
            f"阶段: {form.get('stage', '待确认')}",
            f"目标: {goal}",
            f"期望输出: {form.get('expectedOutput', '') or '待确认'}",
            f"已有成员: {form.get('existingMembers', '') or '待确认'}",
            "",
            "下一步: 项目经理 Agent 会整理推荐 Agent、职责边界、协作顺序、工具/技能需求和需要 owner 确认的风险项。",
        ]
    )


def split_agent_list(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[,，\n]+", value or "") if part.strip()]


def submit_discussion_create_card(bundle: Bundle, incoming: dict[str, str], form: dict[str, str]) -> str:
    title = form.get("title", "").strip()
    topic = form.get("topic", "").strip()
    if not title or not topic:
        missing = []
        if not title:
            missing.append("讨论标题")
        if not topic:
            missing.append("讨论问题")
        return f"讨论会还缺：{'、'.join(missing)}。"
    project_raw = form.get("projectName", "").strip()
    project_id = normalize_project_id(project_raw) if project_raw else ""
    requester = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    result = create_discussion_session(
        bundle,
        title,
        project_id,
        requester,
        topic,
        split_agent_list(form.get("participants", "")) or None,
        form.get("relatedTaskId", "").strip(),
    )
    return "\n".join(
        [
            "已创建 Agent 讨论会。",
            f"讨论编号: {result['discussionId']}",
            f"讨论记录: {result['discussionRef']}",
            f"项目: {project_raw or '公司级/待绑定项目'}",
            "后续处理: 已通知参与 Agent 提交观点；全部观点提交后，项目经理 Agent 汇总并生成决策或后续任务。",
        ]
    )


def submit_bind_project_group_card(bundle: Bundle, incoming: dict[str, str], form: dict[str, str]) -> str:
    if is_private_chat(incoming):
        return bind_project_group_entry_text(incoming)
    project_name = form.get("projectName", "").strip()
    if not project_name:
        return "项目群绑定卡还缺：项目名称。"
    return bind_project_group(
        bundle,
        incoming,
        project_name,
        incoming.get("openId") or incoming.get("userId") or "feishu-card",
        note=f"ownerConfirmed={form.get('ownerConfirmed', '') or '待确认'}; {form.get('note', '') or '无'}",
    )


def submit_project_handoff_card(form: dict[str, str]) -> str:
    required = {
        "projectName": "项目名称",
        "currentStage": "当前阶段",
        "handoffTo": "接手方",
        "handoffScope": "交接范围",
    }
    missing = [label for key, label in required.items() if not form.get(key, "").strip()]
    if missing:
        return f"项目交接卡还缺：{'、'.join(missing)}。"
    return "\n".join(
        [
            "已收到项目交接需求。",
            f"项目: {form.get('projectName', '')}",
            f"当前阶段: {form.get('currentStage', '')}",
            f"接手方: {form.get('handoffTo', '')}",
            f"交接范围: {form.get('handoffScope', '')}",
            f"继续目标: {form.get('operationGoal', '') or '待确认'}",
            "",
            "下一步: 我会生成交接清单草稿，覆盖成果、仓库、文档、任务、知识草稿、权限和后续运营目标。",
        ]
    )


def submit_tool_skill_card(bundle: Bundle, incoming: dict[str, str], form: dict[str, str]) -> str:
    name = form.get("name", "").strip()
    owner = form.get("owner", "").strip() or incoming.get("openId") or "feishu-user"
    asset_type = form.get("assetType", "tool")
    risk = form.get("risk", "L2").strip().upper() or "L2"
    if not name:
        raise KnowledgeError("缺少工具/技能名称")
    if asset_type == "tool":
        path = make_tool(
            bundle,
            tool_id=f"tool.{name}",
            name=name,
            owner=owner,
            repo=form.get("projectName") or "pending",
            entrypoint="pending-review",
            risk=risk,
        )
        return "\n".join(
            [
                "已创建工具申请草稿。",
                f"名称: {name}",
                f"对象: {path.relative_to(bundle.root)}",
                "状态: testing，进入 Review 和 owner 审批。",
            ]
        )
    path = make_skill(
        bundle,
        skill_id=f"skill.{name}",
        name=name,
        owner=owner,
        purpose=form.get("purpose", ""),
        scope=form.get("scope", "") or "company",
        risk=risk,
        project_id=form.get("projectName", ""),
        source_ref=f"feishu://card/{incoming.get('messageId')}",
    )
    return f"已创建技能资产申请草稿：{path.relative_to(bundle.root)}\n状态: draft，进入 Review、Eval 和 owner 审批。"


def project_launch_missing_text(project_intake: dict[str, str], missing: list[str]) -> str:
    missing_text = "、".join(missing)
    return "\n".join(
        [
            f"项目启动卡还缺：{missing_text}。",
            "项目 Owner 请 @ 对方，或输入姓名/手机号/邮箱。",
            "",
            "已有仓库接入：",
            "创建项目：已有仓库 <Git URL>，项目Owner <姓名/手机号/邮箱>，项目名称 <可选>，项目目标 <可选>，主责Agent <可选>，项目群 <后续确认/需要创建或绑定/暂不需要>",
            "",
            "从头创建新项目：",
            "创建项目：项目名称 <名称>，项目Owner <姓名/手机号/邮箱>，项目目标 <目标>，主责Agent <可选>，项目群 <后续确认/需要创建或绑定/暂不需要>",
        ]
    )


def project_launch_summary(project_intake: dict[str, str]) -> str:
    repo_mode = project_intake.get("repoMode", "")
    repo_line = "代码仓库：待确认"
    if repo_mode == "existing":
        repo_line = f"代码仓库：接入已有仓库 {project_intake.get('repoUrl') or '待补充 URL'}"
    elif repo_mode == "new":
        repo_line = f"代码仓库：审批后新建 {project_intake.get('repoName') or '待补充仓库名'}"
    agents = project_intake.get("agents") or "待项目经理 Agent 推荐"
    lead_agent = project_intake.get("leadAgent") or "待项目经理 Agent 推荐"
    runner = project_intake.get("defaultRunner") or "待 Agent Ring 注册"
    group = normalize_project_group_preference(project_intake.get("createGroup", ""))
    goal = project_intake.get("goal") or "待补充"
    return "\n".join(
        [
            "项目启动卡摘要：",
            f"- 项目目标：{goal}",
            f"- {repo_line}",
            f"- 主责 Agent：{lead_agent}",
            f"- 默认 Runner：{runner}",
            f"- 需要 Agent：{agents}",
            f"- 项目群协作：{group}",
        ]
    )


def project_intake_needs_product_manager(project_intake: dict[str, str]) -> bool:
    return needs_product_manager_agent(project_intake.get("agents", ""), project_intake.get("goal", ""), project_intake.get("repoMode", ""))


def project_intake_product_manager_reason(project_intake: dict[str, str]) -> str:
    needed, reason = product_manager_agent_decision(project_intake.get("agents", ""), project_intake.get("goal", ""), project_intake.get("repoMode", ""))
    return ("included: " if needed else "skipped: ") + reason


def write_project_launch_plan(bundle: Bundle, project_id: str, project_name: str, owner_open_id: str, project_intake: dict[str, str]) -> Path:
    project_dir = bundle.root / "projects" / slug(project_id)
    ensure_dir(project_dir)
    launch_path = project_dir / "launch.md"
    frontmatter = {
        "type": "Workflow",
        "title": f"{project_name} Launch",
        "description": f"Project launch workflow for {project_name}.",
        "timestamp": utc_now(),
        "owner": owner_open_id,
        "status": "draft",
        "scope": "project",
        "projectId": project_id,
    }
    body = "\n".join(
        [
            "## Project",
            "",
            f"- projectId: {project_id}",
            f"- owner: {owner_open_id}",
            f"- status: draft",
            "",
            "## Intake",
            "",
            f"- goal: {project_intake.get('goal') or 'TBD'}",
            f"- repoMode: {project_intake.get('repoMode') or 'TBD'}",
            f"- repoUrl: {project_intake.get('repoUrl') or 'TBD'}",
            f"- repoName: {project_intake.get('repoName') or 'TBD'}",
            f"- requestedAgents: {project_intake.get('agents') or 'TBD'}",
            f"- leadAgent: {project_intake.get('leadAgent') or 'TBD'}",
            f"- defaultRunner: {project_intake.get('defaultRunner') or 'TBD'}",
            f"- createProjectGroup: {project_intake.get('createGroup') or 'TBD'}",
            "",
            "## Startup Milestones",
            "",
            "- M0 Intake Complete: project owner, goal, repo mode, group preference, requested Agent roles, and requester are captured or listed as missing.",
            "- M1 Approval And Ownership: owner approval path is created or explicitly not required; human project owner is accountable.",
            "- M2 Initialization Executed: repository path, README/AGENTS/review rules, project group, default Agent team, and Runner/manual handoff are ready or blocked with owner.",
            "- M3 First Work Queue: the first actionable ProjectTask list is created from the approved launch context.",
            "",
            "Business or product milestones are not guessed during project creation. The Project Manager Agent proposes them during the initialization task after reading the goal, owner constraints, repo state, and requested roles.",
            "",
            "## Default Agent Team",
            "",
            f"- Project Manager Agent: agent.{slug(project_id)}.project-manager owns project initialization closure and task flow.",
            *(
                [f"- Product Manager Agent: agent.{slug(project_id)}.product-manager owns product requirement clarification and acceptance criteria."]
                if project_intake_needs_product_manager(project_intake)
                else []
            ),
            f"- Knowledge Engineering Agent: agent.{slug(project_id)}.knowledge-engineering owns project material and reusable knowledge drafts.",
            f"- Executor Agent: agent.{slug(project_id)}.executor owns local execution through Agent Ring or manual runner.",
            "",
            "Product Manager decision:",
            "",
            f"- {project_intake_product_manager_reason(project_intake)}",
            "",
            "Requested role input:",
            "",
            f"- {project_intake.get('agents') or 'TBD'}",
            "",
            "Product Manager Agent is included by default unless the intake clearly says product work is already complete or not needed.",
            "Product requirement clarification becomes a first ProjectTask only when Product Manager Agent is included or a human product owner is explicit.",
            "Requested frontend, backend, test, ops, or domain roles become candidate Agents or first ProjectTasks after the Project Manager Agent confirms actual need and available runners.",
            "",
            "## Flow Entry",
            "",
            "- Project creation creates the launch record and the project_initialization ProjectTask.",
            "- The project_initialization task is assigned to the Project Manager Agent.",
            "- Scheduler assigns the task to Agent Ring when available; otherwise it becomes waiting_runner.",
            "- Project Manager Agent writes TaskResult with evidence, blockers, risks, and first ProjectTask list.",
            "- After TaskResult, work flows into first ProjectTasks such as repo setup, implementation, material ingest, tool request, or review preparation.",
            "- Product discovery is a first ProjectTask only when Product Manager Agent or human product owner is explicit.",
            "",
            "## Launch Checklist",
            "",
            "- Confirm human project owner.",
            "- Confirm project manager Agent as the initialization owner.",
            "- Confirm whether this project uses an existing repository or needs a new repository.",
            "- Register repository in project metadata after approval.",
            "- Initialize repository README, AGENTS instructions, project structure, and review gates.",
            "- Create or bind Feishu project group.",
            "- Confirm Agent team and role boundaries.",
            "- Confirm Runner or manual handoff path for the initialization task.",
            "- Register project tools and private skills when needed.",
            "- Start project AgentRun workflow.",
            "- Keep decisions, lessons, materials, and handoff notes in project context.",
            "",
            "## Closed Loop Acceptance",
            "",
            "- Project draft and launch.md exist and link back to the owner, repository mode, Agent team, group plan, Runner, and M0-M3 startup milestones.",
            "- Project initialization task has assignee, required capabilities, runner/manual handoff status, expected output, notification trail, and audit trail.",
            "- Existing repo is inspected or new repo creation is requested through approved integration.",
            "- Project group is created or deliberately marked unnecessary.",
            "- Project manager Agent writes TaskResult with evidence, risks, blockers, and first ProjectTask list.",
            "- Knowledge or governance output, if produced, enters Review before reuse.",
        ]
    )
    write_text(launch_path, render_doc(frontmatter, body + "\n"))
    return launch_path


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


def parse_project_status_query(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    patterns = [
        r"^(?:查|看|查看|查询|了解)?(?:一下|下)?(?:项目)?(?:状态|进度|详情|情况)[:：\s]+(?P<project>.+)$",
        r"^(?:查|看|查看|查询)\s*项目\s*[:：\s]+(?P<project>.+)$",
        r"^(?P<project>.+?)(?:的)?(?:项目)?(?:状态|详情|进度|情况)(?:怎么样|如何|是什么)?[?？。]?$",
    ]
    for pattern in patterns:
        match = re.match(pattern, stripped)
        if match:
            return match.group("project").strip(" ：:，,。")
    if is_project_status_prompt_without_project(stripped):
        return ""
    return ""


def project_status_summary(bundle: Bundle, project_query: str) -> dict[str, Any]:
    resolved = resolve_project_ref(bundle, project_query)
    if resolved.get("error"):
        return resolved
    project_path = Path(resolved["path"])
    project = load_object(project_path)
    project_id = str(project.get("projectId") or project_path.parent.name)
    project_dir = project_path.parent
    tasks = project_task_summaries(project_dir)
    agents = project_agent_summaries(bundle, project)
    runners = project_runner_summaries(bundle, project_id, tasks)
    approvals = project_approval_summaries(bundle, project_id, str(project.get("title", "")), load_feishu_settings())
    results = project_result_summaries(bundle, project_id)
    progress = project_progress_summary(tasks)
    risks = project_risk_summaries(tasks, runners, approvals)
    decisions_needed = project_decision_summaries(tasks, approvals, risks)
    health = project_health_state(tasks, runners, risks, decisions_needed)
    next_actions = project_next_actions(tasks, runners, risks, decisions_needed)
    return {
        "kind": "ProjectStatus",
        "query": project_query,
        "path": str(project_path.relative_to(bundle.root)),
        "projectId": project_id,
        "title": project.get("title") or project_id,
        "owner": project.get("humanOwner") or project.get("owner") or "unknown",
        "status": project.get("status") or "unknown",
        "agents": agents,
        "runners": runners,
        "tasks": tasks,
        "approvals": approvals,
        "results": results,
        "progress": progress,
        "health": health,
        "risks": risks,
        "decisionsNeeded": decisions_needed,
        "nextActions": next_actions,
    }


def resolve_project_ref(bundle: Bundle, project_query: str) -> dict[str, Any]:
    query = project_query.strip()
    if not query:
        return {"error": "missing_project", "message": "请告诉我要查哪个项目，例如：项目状态：Company Knowledge Core"}
    project_root = bundle.root / "projects"
    query_slug = safe_slug(query)
    if query_slug:
        exact_path = project_root / query_slug / "project.md"
        if exact_path.exists():
            return {"path": exact_path}
    matches: list[Path] = []
    normalized = re.sub(r"\s+", "", query).lower()
    for path in sorted(project_root.glob("*/project.md")):
        fm = load_object(path)
        title = str(fm.get("title", ""))
        project_id = str(fm.get("projectId", path.parent.name))
        candidates = {title, project_id, path.parent.name}
        title_slug = safe_slug(title)
        if title_slug:
            candidates.add(title_slug)
        compact_candidates = {re.sub(r"\s+", "", item).lower() for item in candidates if item}
        if normalized in compact_candidates:
            matches.append(path)
        elif normalized and any(normalized in item for item in compact_candidates):
            matches.append(path)
    unique: list[Path] = []
    for path in matches:
        if path not in unique:
            unique.append(path)
    if len(unique) == 1:
        return {"path": unique[0]}
    if len(unique) > 1:
        names = [str(load_object(path).get("title") or path.parent.name) for path in unique[:5]]
        return {"error": "ambiguous_project", "message": "找到多个项目，请说得更具体：" + "、".join(names)}
    return {"error": "not_found", "message": f"没找到项目：{project_query}。请用项目名称查询，不需要输入项目 ID。"}


def safe_slug(value: str) -> str:
    try:
        return slug(value)
    except KnowledgeError:
        return ""


def project_task_summaries(project_dir: Path) -> list[dict[str, str]]:
    task_dir = project_dir / "tasks"
    rows: list[dict[str, str]] = []
    for path in sorted(task_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
        if path.name == "index.md":
            continue
        fm = load_object(path)
        rows.append(
            {
                "taskId": str(fm.get("taskId") or path.stem),
                "title": str(fm.get("title") or path.stem),
                "taskType": str(fm.get("taskType") or "task"),
                "status": str(fm.get("status") or "unknown"),
                "assignee": first_value(fm.get("assignee")) or first_value(fm.get("assignedRunner")) or "unassigned",
                "path": str(path.relative_to(project_dir.parent.parent)),
            }
        )
    return rows


def project_agent_summaries(bundle: Bundle, project: dict[str, Any]) -> list[dict[str, str]]:
    agents: list[dict[str, str]] = []
    for agent_id in value_list(project.get("relatedAgents")):
        path = bundle.root / "agents" / f"{slug(agent_id)}.md"
        if not path.exists():
            agents.append({"agentId": agent_id, "title": agent_id, "status": "missing"})
            continue
        fm = load_object(path)
        agents.append({"agentId": str(fm.get("agentId") or agent_id), "title": str(fm.get("title") or agent_id), "status": str(fm.get("status") or "unknown")})
    return agents


def project_runner_summaries(bundle: Bundle, project_id: str, tasks: list[dict[str, str]]) -> list[dict[str, str]]:
    assigned = {slug(str(task.get("assignee", ""))) for task in tasks if str(task.get("assignee", "")).startswith("runner.")}
    runners: list[dict[str, str]] = []
    runner_dir = bundle.root / "runners"
    for path in sorted(runner_dir.glob("*.md")):
        if path.name == "index.md":
            continue
        fm = load_object(path)
        runner_id = str(fm.get("runnerId") or path.stem)
        projects = {slug(item) for item in value_list(fm.get("availableProjects"))}
        if slug(project_id) in projects or slug(runner_id) in assigned:
            runners.append(
                {
                    "runnerId": runner_id,
                    "title": str(fm.get("title") or runner_id),
                    "status": str(fm.get("status") or "unknown"),
                    "capabilities": ", ".join(value_list(fm.get("capabilities"))[:4]) or "not declared",
                }
            )
    return runners


def project_approval_summaries(bundle: Bundle, project_id: str, project_name: str, settings: FeishuSettings | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(approval_request_dir(bundle).glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if item.get("projectId") != project_id and item.get("projectName") != project_name:
            continue
        if settings:
            item = reconcile_approval_request_if_needed(bundle, settings, item)
        rows.append(
            {
                "instanceCode": str(item.get("instanceCode") or path.stem),
                "type": str(item.get("approvalType") or "approval"),
                "status": str(item.get("finalStatus") or "pending"),
                "targetRef": str(item.get("targetRef") or ""),
                "syncWarning": str(item.get("_syncWarning") or ""),
            }
        )
        if len(rows) >= 3:
            break
    return rows


def feishu_approval_instance_detail(settings: FeishuSettings, instance_code: str) -> dict[str, Any]:
    if not settings.app_id or not settings.app_secret or not instance_code:
        return {}
    token = get_tenant_access_token(settings)
    params = urllib.parse.urlencode({"locale": "zh-CN", "user_id_type": "open_id"})
    url = f"{FEISHU_API_BASE}/approval/v4/instances/{urllib.parse.quote(instance_code)}?{params}"
    result = feishu_json_request("GET", url, token)
    data = result.get("data") or {}
    return data if isinstance(data, dict) else {}


def subscribe_feishu_approval_events(settings: FeishuSettings, approval_code: str) -> None:
    if not settings.app_id or not settings.app_secret or not approval_code:
        return
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/approval/v4/approvals/{urllib.parse.quote(approval_code)}/subscribe"
    feishu_json_request("POST", url, token, {})


def final_status_from_feishu_approval(external_status: str, requested_status: str) -> str:
    status = str(external_status or "").strip().upper()
    if status in {"APPROVED", "PASS", "AGREE", "APPROVE", "APPROVAL_APPROVED", "2"}:
        return requested_status or "approved"
    if status in {"REJECTED", "REJECT", "REFUSED", "DENIED", "CANCELED", "CANCELLED", "DELETED", "3", "4", "5"}:
        return "rejected"
    return ""


def apply_project_approval_status(bundle: Bundle, request: dict[str, str], new_status: str, reviewer: str, source: str) -> None:
    if request.get("approvalType") != APPROVAL_TYPE_PROJECT_INIT:
        return
    target_ref = request.get("targetRef", "")
    if not target_ref:
        return
    target_path = bundle.root / target_ref
    if not target_path.exists():
        ensure_approval_target_exists(bundle, request, request.get("instanceCode", ""))
    if not target_path.exists():
        return
    updates: dict[str, Any] = {
        "status": new_status,
        "reviewer": reviewer,
        "reviewedAt": utc_now(),
        "approvalStatus": new_status,
        "approvalSource": source,
    }
    owner_name = str(request.get("ownerName") or "").strip()
    if owner_name and not owner_name.startswith("ou_"):
        updates["humanOwner"] = owner_name
    update_frontmatter_file(target_path, updates)


def reconcile_approval_request_if_needed(bundle: Bundle, settings: FeishuSettings, request: dict[str, str]) -> dict[str, str]:
    if request.get("finalStatus"):
        return request
    instance_code = request.get("instanceCode", "")
    if not instance_code:
        return request
    try:
        detail = feishu_approval_instance_detail(settings, instance_code)
    except KnowledgeError as exc:
        warning = compact_snippet(str(exc), 180)
        create_audit_log(
            bundle,
            "feishu-approval",
            "feishu.approval.reconcile_failed",
            request.get("targetRef", instance_code),
            after="failed",
            policy_result=request.get("approvalType", ""),
            details=f"instanceCode: {instance_code}\nreason: {compact_snippet(str(exc), 300)}",
        )
        failed = dict(request)
        failed["_syncWarning"] = warning
        return failed
    external_status = str(detail.get("status") or "")
    final_status = final_status_from_feishu_approval(external_status, request.get("requestedStatus", "approved"))
    if not final_status:
        return request
    updated = dict(request)
    updated["finalStatus"] = final_status
    updated["externalStatus"] = external_status
    updated["reconciledAt"] = utc_now()
    save_approval_request(bundle, instance_code, updated)
    apply_project_approval_status(bundle, updated, final_status, "feishu-approval-reconcile", "feishu_status_query")
    notify_approval_result(bundle, settings, updated, final_status != "rejected", instance_code, final_status)
    create_audit_log(
        bundle,
        "feishu-approval-reconcile",
        "feishu.approval.reconciled",
        updated.get("targetRef", instance_code),
        after=final_status,
        policy_result=updated.get("approvalType", ""),
        details=f"instanceCode: {instance_code}\nexternalStatus: {external_status}",
    )
    return updated


def project_result_summaries(bundle: Bundle, project_id: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted((bundle.root / "task-results").glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True):
        if path.name == "index.md":
            continue
        fm = load_object(path)
        if str(fm.get("projectId") or "") != project_id:
            continue
        rows.append({"taskId": str(fm.get("taskId") or ""), "status": str(fm.get("status") or ""), "summary": compact_snippet(str(fm.get("summary") or ""), 120)})
        if len(rows) >= 3:
            break
    return rows


def project_progress_summary(tasks: list[dict[str, str]]) -> dict[str, int]:
    done_statuses = {"done", "rejected"}
    blocked_statuses = {"blocked", "waiting_runner", "changes_requested"}
    completed = [task for task in tasks if task.get("status") in done_statuses]
    blocked = [task for task in tasks if task.get("status") in blocked_statuses]
    waiting_acceptance = [task for task in tasks if task.get("status") == "waiting_acceptance"]
    active = [task for task in tasks if task.get("status") not in done_statuses]
    return {
        "total": len(tasks),
        "completed": len(completed),
        "active": len(active),
        "blocked": len(blocked),
        "waitingAcceptance": len(waiting_acceptance),
    }


def project_risk_summaries(
    tasks: list[dict[str, str]],
    runners: list[dict[str, str]],
    approvals: list[dict[str, str]],
) -> list[dict[str, str]]:
    risks: list[dict[str, str]] = []
    blocked_tasks = [task for task in tasks if task.get("status") == "blocked"]
    manual_tasks = [task for task in tasks if task.get("status") == "waiting_runner"]
    pending_tasks = [task for task in tasks if task.get("status") in {"pending", "processing", "waiting_acceptance", "changes_requested"}]
    pending_approvals = [item for item in approvals if item.get("status") in {"pending", "submitted", "running"}]
    if blocked_tasks:
        task = blocked_tasks[0]
        risks.append(
            {
                "severity": "high",
                "risk": f"任务阻塞：{task['title']}",
                "owner": task.get("assignee") or "unassigned",
                "next": "项目经理确认阻塞原因、责任人和恢复时间。",
            }
        )
    if manual_tasks:
        task = manual_tasks[0]
        is_initialization = task.get("taskType") == "project_initialization"
        risks.append(
            {
                "severity": "high",
                "risk": f"{'项目初始化' if is_initialization else '任务'}等待执行电脑接管：{task['title']}",
                "owner": task.get("assignee") or "project-manager",
                "next": "登记匹配能力的 Agent 工作台执行电脑，或由项目经理 Agent 明确人工接管和结果写回责任。",
            }
        )
    if pending_tasks and not runners:
        risks.append(
            {
                "severity": "medium",
                "risk": "存在未完成任务，但暂无可用执行电脑。",
                "owner": "project-manager",
                "next": "登记或绑定具备项目能力的 Agent 工作台执行电脑。",
            }
        )
    if pending_approvals:
        approval = pending_approvals[0]
        risks.append(
            {
                "severity": "medium",
                "risk": f"{display_approval_type(approval['type'])}等待处理",
                "owner": "human-reviewer",
                "next": "提醒审批人处理，或确认是否需要补充材料。",
            }
        )
    if not tasks:
        risks.append(
            {
                "severity": "medium",
                "risk": "项目尚未形成可跟踪任务。",
                "owner": "project-manager",
                "next": "创建项目初始化任务或首批 ProjectTask。",
            }
        )
    return risks[:5]


def project_decision_summaries(
    tasks: list[dict[str, str]],
    approvals: list[dict[str, str]],
    risks: list[dict[str, str]],
) -> list[str]:
    decisions: list[str] = []
    if any(task.get("status") == "waiting_runner" for task in tasks):
        decisions.append("决定由项目经理 Agent 人工接管，还是先登记匹配能力的 Agent 工作台执行电脑后自动执行。")
    if any(item.get("status") in {"pending", "submitted", "running"} for item in approvals):
        decisions.append("确认待审批事项是否具备批准条件，或退回补充材料。")
    if any("未形成可跟踪任务" in item.get("risk", "") for item in risks):
        decisions.append("确认项目下一阶段的最小可交付物和首批任务。")
    return decisions[:3]


def project_health_state(
    tasks: list[dict[str, str]],
    runners: list[dict[str, str]],
    risks: list[dict[str, str]],
    decisions: list[str],
) -> str:
    if any(task.get("status") == "blocked" for task in tasks):
        return "blocked"
    if decisions:
        return "needs_decision"
    if any(item.get("severity") == "high" for item in risks):
        return "at_risk"
    if risks or (tasks and not runners):
        return "at_risk"
    return "on_track"


def project_next_actions(
    tasks: list[dict[str, str]],
    runners: list[dict[str, str]],
    risks: list[dict[str, str]] | None = None,
    decisions: list[str] | None = None,
) -> list[str]:
    actions: list[str] = []
    manual = [task for task in tasks if task.get("status") == "waiting_runner"]
    pending = [task for task in tasks if task.get("status") in {"pending", "processing", "waiting_acceptance", "changes_requested", "blocked"}]
    if decisions:
        actions.append(decisions[0])
    if manual:
        actions.append(f"接管等待人工接管的任务：{manual[0]['title']}")
    if not runners:
        actions.append("登记或绑定可用 Agent 工作台执行电脑。")
    if risks:
        actions.append(risks[0]["next"])
    if pending:
        actions.append(f"推进当前未完成任务：{pending[0]['title']} ({pending[0]['status']})")
    if not actions:
        actions.append("暂无阻塞；继续按任务列表推进。")
    unique: list[str] = []
    for action in actions:
        if action not in unique:
            unique.append(action)
    return unique[:3]


STATUS_LABELS = {
    "draft": "草稿",
    "pending": "待处理",
    "processing": "处理中",
    "waiting_runner": "等待执行电脑接管",
    "waiting_acceptance": "等待验收",
    "changes_requested": "需要返工",
    "needs_human_approval": "等待人工审批",
    "needs_clarification": "等待补充信息",
    "done": "已完成",
    "verified": "已验证",
    "approved": "已批准",
    "resolved": "已解决",
    "blocked": "已阻塞",
    "missing": "缺失",
    "active": "运行中",
    "observed": "已记录",
    "reviewing": "审核中",
    "submitted": "已提交",
    "running": "处理中",
    "rejected": "已驳回",
    "unknown": "未知",
    "unassigned": "未分配",
    "approval_required": "等待审批",
    "clarification_required": "等待补充信息",
    "launch_approved": "立项已批准",
    "project_draft": "项目草稿",
    "testing": "测试中",
    "escalated": "已升级",
}


HEALTH_LABELS = {
    "on_track": "正常推进",
    "at_risk": "存在风险",
    "blocked": "已阻塞",
    "needs_decision": "需要决策",
    "unknown": "未知",
}


SEVERITY_LABELS = {
    "high": "高",
    "medium": "中",
    "low": "低",
}


APPROVAL_TYPE_LABELS = {
    APPROVAL_TYPE_PROJECT_INIT: "项目立项审批",
    APPROVAL_TYPE_KNOWLEDGE_INGEST: "知识入库审批",
    APPROVAL_TYPE_AGENT_TOKEN: "访问凭证审批",
}


def display_status(value: str) -> str:
    raw = str(value or "unknown").strip()
    key = raw.lower().replace(" ", "_")
    return STATUS_LABELS.get(key, raw.replace("_", " ").replace("-", " "))


def display_health(value: str) -> str:
    raw = str(value or "unknown").strip()
    key = raw.lower().replace(" ", "_")
    return HEALTH_LABELS.get(key, raw.replace("_", " ").replace("-", " "))


def display_severity(value: str) -> str:
    raw = str(value or "medium").strip()
    key = raw.lower().replace(" ", "_")
    return SEVERITY_LABELS.get(key, raw)


def display_approval_type(value: str) -> str:
    raw = str(value or "approval").strip()
    key = raw.lower().replace(" ", "_")
    return APPROVAL_TYPE_LABELS.get(key, raw.replace("_", " ").replace("-", " "))


def display_approval_status(value: str) -> str:
    raw = str(value or "pending").strip().lower().replace(" ", "_")
    if raw in {"verified", "approved", "active", "launch_approved"}:
        return "已通过"
    if raw in {"rejected", "canceled", "cancelled", "deleted"}:
        return "已驳回/取消"
    if raw in {"pending", "submitted", "running"}:
        return "待处理"
    return display_status(raw)


def display_open_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw.startswith("ou_"):
        return raw
    user_map = parse_user_open_id_map(os.environ.get("FEISHU_USER_OPEN_ID_MAP_JSON", "{}"))
    for name, open_id in user_map.items():
        if open_id == raw:
            return name
    return f"未配置展示名（open_id 尾号 {raw[-6:]}）"


def display_owner(value: str) -> str:
    raw = str(value or "").strip()
    if not raw or raw in {"unknown", "unassigned"}:
        return "未登记"
    if raw.startswith("ou_"):
        return display_open_id(raw)
    return raw


def display_capabilities(value: str) -> str:
    raw = str(value or "").strip()
    if not raw or raw == "not declared":
        return "未声明"
    return humanize_project_action(raw)


def display_task_status(status: str) -> str:
    raw = str(status or "")
    label = display_status(raw)
    if raw == "waiting_runner":
        return f"{label}（Agent Ring 未启用，需要指定执行电脑处理）"
    return label


def humanize_project_action(text: str) -> str:
    result = str(text or "").strip()
    replacements = {
        "waiting_runner": "等待执行电脑接管",
        "waiting_acceptance": "等待验收",
        "changes_requested": "需要返工",
        "TaskResult": "任务结果",
        "AgentRun": "执行记录",
        "Runner": "执行电脑",
        "Agent Ring": "Agent 工作台",
        "ProjectTask": "项目任务",
        "pending": "待处理",
        "processing": "处理中",
        "blocked": "已阻塞",
        "needs_decision": "需要决策",
        "project_init": "项目立项审批",
        "not declared": "未声明",
    }
    for source, target in replacements.items():
        result = result.replace(source, target)
    return result


def render_project_status_text(summary: dict[str, Any]) -> str:
    if summary.get("error"):
        return str(summary.get("message"))
    progress = summary.get("progress") or {}
    lines = [
        f"项目：{summary['title']}",
        f"当前状态：{display_status(str(summary.get('status', 'unknown')))}；健康度：{display_health(str(summary.get('health', 'unknown')))}",
        f"任务进度：共 {progress.get('total', 0)} 个，已完成 {progress.get('completed', 0)} 个，未完成 {progress.get('active', 0)} 个，阻塞 {progress.get('blocked', 0)} 个，待验收 {progress.get('waitingAcceptance', 0)} 个",
        f"负责人：{display_owner(str(summary.get('owner', '')))}",
        "",
        "**项目 Agent**",
    ]
    agents = summary.get("agents") or []
    lines.extend([f"- {item['title']}：{display_status(item.get('status', ''))}" for item in agents[:5]] or ["- 暂未登记项目 Agent"])
    lines.extend(["", "**执行电脑 / Runner**"])
    runners = summary.get("runners") or []
    lines.extend([f"- {item['title']}：{display_status(item.get('status', ''))}；能力：{display_capabilities(item.get('capabilities', ''))}" for item in runners[:5]] or ["- 暂未绑定可用执行电脑；当前需要人工接管或登记 Agent 工作台。"])
    lines.extend(["", "**当前任务**"])
    tasks = summary.get("tasks") or []
    open_tasks = [task for task in tasks if task.get("status") not in {"done", "rejected"}]
    lines.extend([f"- {task['title']}：{display_task_status(task.get('status', ''))}" for task in open_tasks[:5]] or ["- 暂无未完成任务"])
    if summary.get("approvals"):
        lines.extend(["", "**审批**"])
        for item in summary["approvals"]:
            line = f"- {display_approval_type(item['type'])}：{display_approval_status(item['status'])}（审批号尾号 {item['instanceCode'][-8:]}）"
            if item.get("syncWarning"):
                line += "；状态未自动回传，请检查飞书审批事件订阅，或配置可查询审批实例的用户授权。"
            lines.append(line)
    if summary.get("results"):
        lines.extend(["", "**最近结果**"])
        lines.extend([f"- {item['taskId']}：{display_status(item['status'])}；{item['summary']}" for item in summary["results"]])
    if summary.get("risks"):
        lines.extend(["", "**风险 / 阻塞**"])
        lines.extend([f"- {display_severity(item['severity'])}风险：{humanize_project_action(item['risk'])}；建议：{humanize_project_action(item['next'])}" for item in summary["risks"]])
    if summary.get("decisionsNeeded"):
        lines.extend(["", "**待决策**"])
        lines.extend([f"- {humanize_project_action(item)}" for item in summary["decisionsNeeded"]])
    lines.extend(["", "**建议下一步**"])
    lines.extend([f"- {humanize_project_action(item)}" for item in summary.get("nextActions", [])])
    lines.extend(["", f"内部记录位置：{summary['path']}（排查时使用，日常只看上面的状态和下一步。）"])
    return "\n".join(lines)


def project_status_card(summary: dict[str, Any]) -> dict[str, Any]:
    if summary.get("error"):
        return interactive_card("项目状态", [{"tag": "markdown", "content": str(summary.get("message"))}], "red")
    content = render_project_status_text(summary)
    return interactive_card(f"项目状态：{summary['title']}", [{"tag": "markdown", "content": content}], "blue")


def value_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def first_value(value: Any) -> str:
    items = value_list(value)
    return items[0] if items else ""


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
    requester = incoming.get("userId") or approval_user_id_for(settings, incoming.get("openId", ""))
    if not requester:
        return "审批未发起：无法识别提交人飞书身份。"
    reviewers = reviewers_for(settings, approval_type, project_id)
    if not reviewers and approval_type == APPROVAL_TYPE_KNOWLEDGE_INGEST and owner_open_id:
        reviewers = [owner_open_id]
    reviewers = [item for item in (approval_user_id_for(settings, reviewer) for reviewer in reviewers) if item]
    owner_user_id = approval_user_id_for(settings, owner_open_id) or requester
    submitter_name = approval_identity_display(settings, requester)
    owner_name = approval_identity_display(settings, owner_user_id)
    form_values = {
        "approval_type": approval_type,
        "approval_type_label": approval_type_label(approval_type),
        "object_path": target_ref,
        "project_id": project_id,
        "project_name": project_name,
        "owner_open_id": owner_user_id,
        "owner_name": owner_name,
        "requested_status": requested_status,
        "requested_status_label": approval_status_label(requested_status),
        "submitter": requester,
        "submitter_name": submitter_name,
        "summary": compact_snippet(summary, 500),
    }
    approval_doc: dict[str, str] = {}
    try:
        approval_doc = create_approval_change_doc(bundle, settings, form_values)
    except KnowledgeError as exc:
        create_audit_log(
            bundle,
            requester,
            "feishu.approval_doc.failed",
            target_ref,
            after="failed",
            policy_result=approval_type,
            details=compact_snippet(str(exc), 500),
        )
    if approval_doc.get("url"):
        form_values["approval_doc_url"] = approval_doc["url"]
    event_subscription_status = "skipped"
    event_subscription_error = ""
    try:
        subscribe_feishu_approval_events(settings, approval_code)
        event_subscription_status = "subscribed"
    except (KnowledgeError, urllib.error.URLError) as exc:
        event_subscription_status = "failed"
        event_subscription_error = compact_snippet(str(exc), 500)
        create_audit_log(
            bundle,
            requester,
            "feishu.approval_event_subscription.failed",
            target_ref,
            after="failed",
            policy_result=approval_type,
            details=f"approvalCode: {approval_code}\nreason: {event_subscription_error}",
        )
    try:
        instance_code = create_feishu_approval_instance(
            settings,
            requester_user_id=requester,
            approval_code=approval_code,
            approver_user_ids=reviewers,
            form_values=form_values,
        )
    except (KnowledgeError, urllib.error.URLError) as exc:
        create_audit_log(
            bundle,
            requester,
            "feishu.approval.failed",
            target_ref,
            after="failed",
            policy_result=approval_type,
            details=compact_snippet(str(exc), 500),
        )
        return f"审批发起失败：{compact_snippet(str(exc), 80)}"
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
            "ownerOpenId": owner_open_id,
            "ownerUserId": owner_user_id,
            "ownerName": owner_name,
            "submitterOpenId": incoming.get("openId", ""),
            "submitterUserId": requester,
            "submitterName": submitter_name,
            "chatId": incoming.get("chatId", ""),
            "messageId": incoming.get("messageId", ""),
            "approvalDocUrl": approval_doc.get("url", ""),
            "approvalDocNodeToken": approval_doc.get("nodeToken", ""),
            "approvalDocObjToken": approval_doc.get("objToken", ""),
            "eventSubscriptionStatus": event_subscription_status,
            "eventSubscriptionError": event_subscription_error,
        },
    )
    details = "\n".join(
        [
            f"instanceCode: {instance_code}",
            f"approvalDoc: {approval_doc.get('url', '')}",
            f"eventSubscriptionStatus: {event_subscription_status}",
            f"eventSubscriptionError: {event_subscription_error}",
        ]
    )
    create_audit_log(bundle, requester, "feishu.approval.create", target_ref, after="pending", policy_result=approval_type, details=details)
    if approval_doc.get("url"):
        return f"已发起飞书审批：{instance_code}\n审批说明: {approval_doc['url']}"
    return f"已发起飞书审批：{instance_code}"


def project_status(bundle: Bundle, project_id: str) -> str:
    project_path = bundle.root / "projects" / slug(project_id) / "project.md"
    if not project_path.exists():
        return ""
    return frontmatter_value(project_path, "status")


def find_pending_approval_for_target(bundle: Bundle, target_ref: str) -> str:
    directory = approval_request_dir(bundle)
    for path in sorted(directory.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            request = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if request.get("targetRef") == target_ref and not request.get("finalStatus"):
            return request.get("instanceCode", "")
    return ""


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


def approval_type_label(approval_type: str) -> str:
    return {
        APPROVAL_TYPE_AGENT_TOKEN: "Agent Token 申请",
        APPROVAL_TYPE_PROJECT_INIT: "项目立项",
        APPROVAL_TYPE_KNOWLEDGE_INGEST: "知识入库",
        "security": "安全审批",
    }.get(approval_type, approval_type or "审批")


def approval_status_label(status: str) -> str:
    return {
        "verified": "审核通过，进入可复用状态",
        "approved": "审批通过",
        "active": "启用",
        "rejected": "驳回",
    }.get(status, status or "-")


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


def first_mentioned_user_id(incoming: dict[str, str]) -> str:
    mentioned = incoming.get("mentionedUserIds", "")
    return split_open_ids(mentioned)[0] if mentioned else ""


def resolve_person_open_id(settings: FeishuSettings, name: str) -> str:
    if not name:
        return ""
    return settings.user_open_id_map.get(normalize_person_name(name), "")


def approval_user_id_for(settings: FeishuSettings, identity: str) -> str:
    identity = (identity or "").strip()
    if not identity:
        return ""
    if not identity.startswith("ou_"):
        return identity
    if not settings.app_id or not settings.app_secret:
        return identity
    try:
        token = get_tenant_access_token(settings)
        users = list_feishu_users(token, limit=500)
    except KnowledgeError:
        return identity
    for user in users:
        if str(user.get("open_id") or user.get("openId") or "") == identity:
            return str(user.get("user_id") or user.get("userId") or identity)
    return identity


def approval_identity_display(settings: FeishuSettings, identity: str) -> str:
    identity = (identity or "").strip()
    if not identity:
        return "-"
    if not settings.app_id or not settings.app_secret:
        return identity
    try:
        token = get_tenant_access_token(settings)
        users = list_feishu_users(token, limit=500)
    except KnowledgeError:
        return identity
    for user in users:
        values = [
            user.get("open_id"),
            user.get("openId"),
            user.get("user_id"),
            user.get("userId"),
            user.get("union_id"),
            user.get("unionId"),
            user.get("email"),
            user.get("mobile"),
            user.get("employee_no"),
        ]
        if any(str(value or "") == identity for value in values):
            return display_user_name(user)
    return identity


def normalize_person_name(name: str) -> str:
    return re.sub(r"\s+", "", name).strip("@").lower()


def lookup_feishu_user_by_name(settings: FeishuSettings, name: str) -> dict[str, str]:
    if not name:
        return {}
    if not settings.app_id or not settings.app_secret:
        return {"message": f"未找到负责人 {name}。"}
    try:
        token = get_tenant_access_token(settings)
        users = list_feishu_users(token, limit=300)
    except KnowledgeError as exc:
        message = str(exc)
        if "contact:" in message or "Access denied" in message or "99991672" in message:
            return {"message": f"通讯录权限不足，未找到 {name}。"}
        return {"message": f"通讯录查询失败：{compact_snippet(message, 80)}"}
    normalized = normalize_person_name(name)
    matches = [user for user in users if user_matches_name(user, normalized)]
    if len(matches) == 1:
        return {
            "openId": str(matches[0].get("open_id") or matches[0].get("openId") or ""),
            "userId": str(matches[0].get("user_id") or matches[0].get("userId") or ""),
            "message": f"已从通讯录匹配负责人：{display_user_name(matches[0])}",
        }
    if len(matches) > 1:
        names = "、".join(display_user_name(user) for user in matches[:5])
        return {"message": f"找到多个负责人：{names}。"}
    candidates = similar_feishu_users(users, normalized)
    if candidates:
        names = "、".join(display_user_name(user) for user in candidates[:5])
        return {"message": f"未找到 {name}。候选：{names}。"}
    names = "、".join(display_user_name(user) for user in users[:5])
    suffix = f"候选：{names}。" if names else ""
    return {"message": f"未找到负责人 {name}。{suffix}"}


def list_feishu_users(token: str, limit: int = 300) -> list[dict[str, Any]]:
    department_ids = list_feishu_department_ids(token, limit=200)
    users: list[dict[str, Any]] = []
    seen: set[str] = set()
    for department_id in department_ids:
        page_token = ""
        while len(users) < limit:
            params = {"user_id_type": "open_id", "department_id_type": "open_department_id", "department_id": department_id, "page_size": "100"}
            if page_token:
                params["page_token"] = page_token
            query = urllib.parse.urlencode(params)
            result = feishu_json_request("GET", f"{FEISHU_API_BASE}/contact/v3/users?{query}", token)
            data = result.get("data", {})
            items = data.get("items") or data.get("users") or []
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    identity = str(item.get("open_id") or item.get("union_id") or item)
                    if identity not in seen:
                        seen.add(identity)
                        users.append(item)
            if not data.get("has_more") or not data.get("page_token"):
                break
            page_token = str(data.get("page_token"))
    return users[:limit]


def list_feishu_department_ids(token: str, limit: int = 200) -> list[str]:
    department_ids = ["0"]
    index = 0
    while index < len(department_ids) and len(department_ids) < limit:
        department_id = department_ids[index]
        index += 1
        page_token = ""
        while len(department_ids) < limit:
            params = {"department_id_type": "open_department_id", "page_size": "50"}
            if page_token:
                params["page_token"] = page_token
            query = urllib.parse.urlencode(params)
            result = feishu_json_request("GET", f"{FEISHU_API_BASE}/contact/v3/departments/{urllib.parse.quote(department_id)}/children?{query}", token)
            data = result.get("data", {})
            for item in data.get("items") or []:
                if not isinstance(item, dict):
                    continue
                child = str(item.get("open_department_id") or item.get("department_id") or "")
                if child and child not in department_ids:
                    department_ids.append(child)
            if not data.get("has_more") or not data.get("page_token"):
                break
            page_token = str(data.get("page_token"))
    return department_ids


def user_matches_name(user: dict[str, Any], normalized: str) -> bool:
    fields = [
        user.get("name"),
        user.get("en_name"),
        user.get("nickname"),
        user.get("email"),
        user.get("mobile"),
        user.get("employee_no"),
    ]
    return any(normalize_person_name(str(value)) == normalized for value in fields if value)


def similar_feishu_users(users: list[dict[str, Any]], normalized: str) -> list[dict[str, Any]]:
    if not normalized:
        return []
    candidates: list[dict[str, Any]] = []
    for user in users:
        values = [user.get("name"), user.get("en_name"), user.get("nickname"), user.get("email"), user.get("mobile"), user.get("employee_no")]
        normalized_values = [normalize_person_name(str(value)) for value in values if value]
        if any(normalized in value or value in normalized for value in normalized_values):
            candidates.append(user)
    return candidates


def display_user_name(user: dict[str, Any]) -> str:
    return str(user.get("name") or user.get("en_name") or user.get("email") or user.get("open_id") or "unknown")


def create_feishu_approval_instance(
    settings: FeishuSettings,
    requester_user_id: str,
    approval_code: str,
    approver_user_ids: list[str],
    form_values: dict[str, str],
) -> str:
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/approval/v4/instances"
    body: dict[str, Any] = {
        "approval_code": approval_code,
        "user_id": requester_user_id,
        "form": json.dumps(approval_form(form_values), ensure_ascii=False),
        "uuid": unique_time_id("approval-request"),
    }
    if settings.approval_node_approver_key and approver_user_ids:
        body["node_approver_user_id_list"] = [{"key": settings.approval_node_approver_key, "value": approver_user_ids}]
    result = feishu_json_request("POST", url, token, body)
    data_obj = result.get("data") or {}
    instance_code = str(data_obj.get("instance_code") or data_obj.get("instanceCode") or "")
    if not instance_code:
        raise KnowledgeError("Feishu approval create failed: missing instance_code")
    return instance_code


def create_approval_change_doc(bundle: Bundle, settings: FeishuSettings, values: dict[str, str]) -> dict[str, str]:
    title = approval_doc_title(values)
    markdown = build_approval_change_markdown(bundle, values, title)
    token = get_tenant_access_token(settings)
    doc = create_drive_docx(token, title, approval_doc_folder_token(settings, values.get("approval_type", "")))
    obj_token = doc.get("document_id", "")
    if not obj_token:
        raise KnowledgeError("Feishu approval doc create failed: missing drive docx token")
    append_docx_markdown(token, obj_token, markdown)
    shared = share_docx_with_names(token, obj_token, settings.approval_doc_share_names)
    url = f"{settings.approval_doc_domain}/docx/{obj_token}"
    return {"url": url, "objToken": obj_token, "title": title, "location": "drive", "sharedWith": ",".join(shared)}


def approval_doc_folder_token(settings: FeishuSettings, approval_type: str) -> str:
    return settings.approval_doc_folder_tokens.get(approval_type, "") or settings.approval_doc_folder_token


def create_drive_docx(token: str, title: str, folder_token: str = "") -> dict[str, str]:
    body = {"title": title[:800]}
    if folder_token:
        body["folder_token"] = folder_token
    result = feishu_json_request("POST", f"{FEISHU_API_BASE}/docx/v1/documents", token, body)
    data = result.get("data") or {}
    doc = data.get("document") if isinstance(data.get("document"), dict) else data
    if not isinstance(doc, dict):
        return {}
    document_id = str(doc.get("document_id") or doc.get("documentId") or doc.get("token") or "")
    return {"document_id": document_id}


def share_docx_with_names(token: str, document_id: str, names: list[str]) -> list[str]:
    if not document_id or not names:
        return []
    users = list_feishu_users(token, limit=500)
    shared: list[str] = []
    for name in names:
        normalized = normalize_person_name(name)
        matches = [user for user in users if user_matches_name(user, normalized)]
        if len(matches) != 1:
            continue
        open_id = str(matches[0].get("open_id") or "")
        if not open_id:
            continue
        feishu_json_request(
            "POST",
            f"{FEISHU_API_BASE}/drive/v1/permissions/{urllib.parse.quote(document_id)}/members?type=docx",
            token,
            {"member_type": "openid", "member_id": open_id, "perm": "edit", "type": "user"},
        )
        shared.append(display_user_name(matches[0]))
    return shared


def approval_doc_title(values: dict[str, str]) -> str:
    label = {
        APPROVAL_TYPE_AGENT_TOKEN: "Agent Token",
        APPROVAL_TYPE_PROJECT_INIT: "项目立项",
        APPROVAL_TYPE_KNOWLEDGE_INGEST: "知识入库",
    }.get(values.get("approval_type", ""), values.get("approval_type", "审批"))
    project_name = values.get("project_name") or values.get("project_id") or "通用"
    return f"{label}审批说明-{project_name}-{unique_time_id('doc')}"


def build_approval_change_markdown(bundle: Bundle, values: dict[str, str], title: str) -> str:
    target_ref = values.get("object_path", "")
    target_path = bundle.root / target_ref if target_ref else None
    target_text = safe_read_text(target_path) if target_path else ""
    target_fm = parse_frontmatter(target_text)
    source_text = ""
    source_ref = str(target_fm.get("sourceRef", ""))
    if source_ref and not source_ref.startswith("feishu://"):
        source_text = safe_read_text(bundle.root / source_ref)
    conflicts = related_conflict_refs(bundle, target_ref, values.get("project_id", ""))
    decision = values.get("requested_status", "")
    sections = [
        f"# {title}",
        "",
        "## 审批结论待定",
        "",
        f"- 审批事项：{values.get('approval_type_label') or approval_type_label(values.get('approval_type', ''))}",
        f"- 项目名称：{values.get('project_name') or values.get('project_id') or '-'}",
        f"- 项目ID：{values.get('project_id') or '-'}",
        f"- 提交人：{values.get('submitter_name') or values.get('submitter') or '-'}",
        f"- 项目负责人：{values.get('owner_name') or values.get('owner_open_id') or '-'}",
        f"- 审批通过后：{values.get('requested_status_label') or approval_status_label(decision)}",
        "",
        "## 审批人需要决定",
        "",
        "- 同意：允许本次变更进入正式流程。",
        "- 不同意：本次变更保持草稿或驳回，不进入正式知识库/项目流程。",
        "- 如发现冲突：以审批意见为准，后续由机器人记录 ConflictRecord 或修正草稿。",
        "",
        "## 变更摘要",
        "",
        values.get("summary", "") or "暂无摘要。",
        "",
        "## 拟入库或拟变更内容",
        "",
        fenced(target_text or "暂无目标文件内容。", "markdown"),
    ]
    if source_text:
        sections.extend(["", "## 来源材料摘要", "", fenced(compact_snippet(source_text, 3000), "markdown")])
    if conflicts:
        sections.extend(["", "## 相关冲突记录", ""])
        sections.extend([f"- {item}" for item in conflicts])
    else:
        sections.extend(["", "## 相关冲突记录", "", "- 暂未发现同目标或同项目的未解决冲突记录。"])
    sections.extend(["", "## 系统信息", "", f"- 对象路径：{target_ref or '-'}", f"- 目标状态：{decision or '-'}"])
    sections.extend(
        [
            "",
            "## 归档说明",
            "",
            "- 本文档由知识工程机器人在发起飞书审批前自动生成。",
            "- 审批结果回调后，知识工程会更新对象状态并写入 AuditLog。",
            "- 本文档作为审批依据归档在机器人云空间审批目录下，不作为正式业务知识直接检索复用。",
        ]
    )
    return "\n".join(sections)


def fenced(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text[:6000]}\n```"


def safe_read_text(path: Path | None) -> str:
    if not path or not path.exists() or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    result: dict[str, Any] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def related_conflict_refs(bundle: Bundle, target_ref: str, project_id: str) -> list[str]:
    conflict_dir = bundle.root / "knowledge" / "conflicts"
    if not conflict_dir.exists():
        return []
    needles = [item for item in [target_ref, project_id] if item]
    matches: list[str] = []
    for path in sorted(conflict_dir.glob("*.md")):
        text = safe_read_text(path)
        if any(needle in text for needle in needles):
            matches.append(str(path.relative_to(bundle.root)))
        if len(matches) >= 5:
            break
    return matches


def append_docx_markdown(token: str, document_id: str, markdown: str) -> None:
    blocks = markdown_to_docx_blocks(markdown)
    if not blocks:
        return
    for start in range(0, len(blocks), 40):
        chunk = blocks[start : start + 40]
        feishu_json_request(
            "POST",
            f"{FEISHU_API_BASE}/docx/v1/documents/{urllib.parse.quote(document_id)}/blocks/{urllib.parse.quote(document_id)}/children",
            token,
            {"index": -1, "children": chunk},
        )


def markdown_to_docx_blocks(markdown: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    in_code = False
    code_lines: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            if in_code:
                blocks.extend(text_blocks("\n".join(code_lines), prefix=""))
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            continue
        blocks.extend(text_blocks(line))
    if code_lines:
        blocks.extend(text_blocks("\n".join(code_lines), prefix=""))
    return blocks[:100]


def text_blocks(text: str, prefix: str = "") -> list[dict[str, Any]]:
    chunks = [text[i : i + 1800] for i in range(0, len(text), 1800)] or [""]
    return [
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": prefix + chunk,
                            "text_element_style": {},
                        }
                    }
                ],
                "style": {},
            },
        }
        for chunk in chunks
        if chunk
    ]


def feishu_json_request(method: str, url: str, token: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            result = json.loads(body)
        except json.JSONDecodeError:
            raise KnowledgeError(f"Feishu API request failed: HTTP {exc.code} {compact_snippet(body, 160)}") from exc
    except urllib.error.URLError as exc:
        raise KnowledgeError(f"Feishu API request failed: {exc}") from exc
    if result.get("code") != 0:
        raise KnowledgeError(f"Feishu API request failed: {result.get('msg') or result.get('code')}")
    return result


def approval_form(values: dict[str, str]) -> list[dict[str, Any]]:
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
        f"审批说明文档: {values.get('approval_doc_url', '') or '-'}",
        f"审批事项: {values.get('approval_type_label') or approval_type_label(values.get('approval_type', ''))}",
        f"项目名称: {values.get('project_name', '') or '-'}",
        f"项目ID: {values.get('project_id', '') or '-'}",
        f"提交人: {values.get('submitter_name') or values.get('submitter', '')}",
        f"负责人: {values.get('owner_name') or values.get('owner_open_id', '')}",
        f"通过后: {values.get('requested_status_label') or approval_status_label(values.get('requested_status', ''))}",
        f"系统对象: {values.get('object_path', '')}",
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
    status = approval_event_status(payload)
    if not instance_code:
        audit_ignored_approval_event(bundle, payload, "approval_event_without_instance_code", status)
        return {"ok": True, "ignored": "approval_event_without_instance_code"}
    request = load_approval_request(bundle, instance_code)
    if not request:
        audit_ignored_approval_event(bundle, payload, "unknown_approval_instance", status, instance_code)
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
        audit_ignored_approval_event(bundle, payload, "approval_status_not_final", status, instance_code)
        return {"ok": True, "ignored": "approval_status_not_final", "status": status, "instanceCode": instance_code}
    if target_ref.startswith("token-request:"):
        result = handle_token_approval_result(bundle, settings, request, reviewer, approved, instance_code)
        request["finalStatus"] = result["status"]
        save_approval_request(bundle, instance_code, request)
        return result
    new_status = request.get("requestedStatus", "verified") if approved else "rejected"
    if approved:
        ensure_approval_target_exists(bundle, request, instance_code)
    if request.get("approvalType") == APPROVAL_TYPE_PROJECT_INIT:
        apply_project_approval_status(bundle, {**request, "instanceCode": instance_code}, new_status, reviewer, "feishu_callback")
        audit_path = create_audit_log(bundle, reviewer, "feishu.approval.project_status_updated", target_ref, after=new_status, policy_result=request.get("approvalType", ""), details=f"instanceCode: {instance_code}\nstatus: {status}")
    else:
        audit_path = review_path(bundle, Path(target_ref), new_status, reviewer)
    create_audit_log(bundle, reviewer, "feishu.approval.callback", target_ref, after=new_status, policy_result=request.get("approvalType", ""), details=f"instanceCode: {instance_code}\nstatus: {status}")
    request["finalStatus"] = new_status
    save_approval_request(bundle, instance_code, request)
    notify_approval_result(bundle, settings, request, approved, instance_code, new_status)
    return {"ok": True, "instanceCode": instance_code, "targetRef": target_ref, "status": new_status, "auditRef": str(audit_path.relative_to(bundle.root))}


def approval_event_status(payload: dict[str, Any]) -> str:
    return str(
        deep_find(payload, "status")
        or deep_find(payload, "approval_status")
        or deep_find(payload, "approvalStatus")
        or deep_find(payload, "instance_status")
        or deep_find(payload, "instanceStatus")
        or deep_find(payload, "result")
        or ""
    ).upper()


def audit_ignored_approval_event(bundle: Bundle, payload: dict[str, Any], reason: str, status: str, instance_code: str = "") -> None:
    target = instance_code or str(deep_find(payload, "instance_code") or deep_find(payload, "instanceCode") or "unknown")
    details = "\n".join(
        [
            f"reason: {reason}",
            f"status: {status or '-'}",
            f"eventType: {extract_event_type(payload) or '-'}",
            f"approvalCodePresent: {bool(deep_find(payload, 'approval_code') or deep_find(payload, 'approvalCode'))}",
            f"payloadShape: {safe_payload_shape(payload)}",
        ]
    )
    create_audit_log(bundle, "feishu-approval", "feishu.approval.ignored", target, after="ignored", policy_result="approval_callback", details=details)


def ensure_approval_target_exists(bundle: Bundle, request: dict[str, str], instance_code: str) -> None:
    target_ref = request.get("targetRef", "")
    if not target_ref:
        return
    target_path = bundle.root / target_ref
    if target_path.exists():
        return
    if request.get("approvalType") != APPROVAL_TYPE_PROJECT_INIT:
        return
    project_id = request.get("projectId", "")
    project_name = request.get("projectName", "")
    owner = request.get("ownerOpenId") or request.get("ownerUserId") or request.get("ownerName") or "unknown"
    if not project_id or not project_name:
        return
    recreated = make_project(bundle, project_id, project_name, owner)
    create_audit_log(
        bundle,
        "feishu-approval",
        "feishu.approval.target_recreated",
        str(recreated.relative_to(bundle.root)),
        after="draft",
        policy_result=request.get("approvalType", ""),
        details=f"instanceCode: {instance_code}\nmissingTargetRef: {target_ref}",
    )


def notify_approval_result(bundle: Bundle, settings: FeishuSettings, request: dict[str, str], approved: bool, instance_code: str, new_status: str) -> None:
    submitter = request.get("submitterOpenId", "")
    if submitter:
        notify_approval_recipient(
            bundle,
            settings,
            request,
            submitter,
            approval_result_message(request, approved, instance_code, new_status),
            "submitter",
            approval_result_card(request, approved, instance_code, new_status),
        )
    if approved and request.get("approvalType") == APPROVAL_TYPE_PROJECT_INIT:
        owner = feishu_open_id_for(settings, request.get("ownerOpenId") or request.get("ownerUserId", ""))
        if owner:
            owner_sent = notify_approval_recipient(
                bundle,
                settings,
                request,
                owner,
                project_owner_onboarding_message(request, instance_code, new_status),
                "project_owner",
                project_owner_onboarding_card(request, instance_code, new_status),
            )
            if not owner_sent and submitter:
                notify_approval_recipient(
                    bundle,
                    settings,
                    request,
                    submitter,
                    project_owner_unreachable_message(request),
                    "submitter_owner_notify_failed",
                    card_result("负责人通知未送达", project_owner_unreachable_message(request), "orange"),
                )
        notify_project_initialization_handoff_if_needed(bundle, settings, request, submitter, owner)


def notify_project_initialization_handoff_if_needed(
    bundle: Bundle,
    settings: FeishuSettings,
    request: dict[str, str],
    submitter: str,
    owner: str,
) -> bool:
    if agent_ring_enabled() or request.get("approvalType") != APPROVAL_TYPE_PROJECT_INIT:
        return False
    project_id = request.get("projectId", "")
    if not project_id:
        return False
    task_id = f"project-init-{slug(project_id)}"
    try:
        task_path = find_project_task(bundle, task_id)
        task = load_object(task_path)
    except KnowledgeError as exc:
        create_audit_log(
            bundle,
            "feishu-approval",
            "feishu.projectInit.manual_runner_missing",
            project_id,
            after="missing",
            policy_result=APPROVAL_TYPE_PROJECT_INIT,
            details=f"taskId: {task_id}\nreason: {compact_snippet(str(exc), 300)}",
        )
        return False
    assignee = str(task.get("assignee") or f"agent.{slug(project_id)}.project-manager")
    notify_open_id = owner or submitter or request.get("ownerOpenId", "")
    return notify_manual_runner_required(
        bundle,
        settings,
        {"openId": notify_open_id},
        task_path,
        task_id,
        assignee,
        request.get("targetRef", ""),
        project_id,
    )


def notify_approval_recipient(bundle: Bundle, settings: FeishuSettings, request: dict[str, str], open_id: str, text: str, role: str, card: dict[str, Any] | None = None) -> bool:
    try:
        if card is not None and settings.app_id and settings.app_secret:
            send_feishu_direct_response(settings, open_id, {"msg_type": "interactive", "card": card})
        else:
            send_feishu_message(settings, open_id, text)
        create_audit_log(
            bundle,
            "feishu-approval",
            "feishu.approval.notify_sent",
            request.get("targetRef", ""),
            after="sent",
            policy_result=request.get("approvalType", ""),
            details=f"recipientRole: {role}\nrecipientOpenId: {open_id}\nmessageType: {'interactive' if card is not None else 'text'}",
        )
        return True
    except (KnowledgeError, urllib.error.URLError) as exc:
        if card is not None:
            try:
                send_feishu_message(settings, open_id, text)
                create_audit_log(
                    bundle,
                    "feishu-approval",
                    "feishu.approval.notify_card_failed_text_fallback_sent",
                    request.get("targetRef", ""),
                    after="fallback_sent",
                    policy_result=request.get("approvalType", ""),
                    details=f"recipientRole: {role}\n{compact_snippet(str(exc), 500)}",
                )
                return True
            except (KnowledgeError, urllib.error.URLError) as fallback_exc:
                exc = fallback_exc
        create_audit_log(
            bundle,
            "feishu-approval",
            "feishu.approval.notify_failed",
            request.get("targetRef", ""),
            after="failed",
            policy_result=request.get("approvalType", ""),
            details=f"recipientRole: {role}\n{compact_snippet(str(exc), 500)}",
        )
        return False


def notify_manual_runner_required(
    bundle: Bundle,
    settings: FeishuSettings,
    incoming: dict[str, str],
    task_path: Path,
    task_id: str,
    assignee: str,
    source_ref: str = "",
    project_id: str = "",
) -> bool:
    if agent_ring_enabled():
        return False
    try:
        set_project_task_status(bundle, task_id, "waiting_runner", "feishu-bot")
    except KnowledgeError:
        create_audit_log(
            bundle,
            "feishu-bot",
            "feishu.manualRunner.status_failed",
            str(task_path.relative_to(bundle.root)) if task_path.exists() else task_id,
            after="failed",
            policy_result="manual_runner_notify",
        )
    task = load_object(task_path)
    task_ref = str(task_path.relative_to(bundle.root))
    recipients = manual_runner_recipients(settings, incoming, assignee, project_id)
    if not recipients:
        create_task_notification(
            bundle,
            task_path,
            task,
            "task_waiting_runner",
            recipient="unresolved",
            delivery_status="failed",
            summary=f"任务需要手动接管，但没有可通知的飞书 open_id：{task.get('title', task_id)}。",
            source_message_ref=source_ref,
            failure_reason="missing recipient open_id",
        )
        return False
    if not settings.app_id or not settings.app_secret:
        for recipient in recipients:
            create_task_notification(
                bundle,
                task_path,
                task,
                "task_waiting_runner",
                recipient=recipient,
                delivery_status="failed",
                summary=f"任务需要手动接管，但飞书应用凭证未配置：{task.get('title', task_id)}。",
                source_message_ref=source_ref,
                failure_reason="missing Feishu app credentials",
            )
        return False
    card = manual_runner_required_card(bundle, task, task_ref, assignee, source_ref)
    sent_any = False
    for recipient in recipients:
        try:
            send_feishu_direct_response(settings, recipient, {"msg_type": "interactive", "card": card})
            create_task_notification(
                bundle,
                task_path,
                task,
                "task_waiting_runner",
                recipient=recipient,
                delivery_status="sent",
                summary=f"已通知手动接管任务：{task.get('title', task_id)}。",
                source_message_ref=source_ref,
            )
            sent_any = True
        except (KnowledgeError, urllib.error.URLError) as exc:
            create_task_notification(
                bundle,
                task_path,
                task,
                "task_waiting_runner",
                recipient=recipient,
                delivery_status="failed",
                summary=f"任务需要手动接管，但飞书通知发送失败：{task.get('title', task_id)}。",
                source_message_ref=source_ref,
                failure_reason=compact_snippet(str(exc), 500),
            )
    return sent_any


def manual_runner_recipients(settings: FeishuSettings, incoming: dict[str, str], assignee: str, project_id: str = "") -> list[str]:
    candidates: list[str] = []
    if assignee.startswith("ou_"):
        candidates.append(assignee)
    project_reviewers = settings.project_reviewer_open_ids.get(project_id, []) if project_id else []
    candidates.extend(project_reviewers)
    candidates.extend(settings.common_reviewer_open_ids)
    submitter = incoming.get("openId", "")
    if submitter:
        candidates.append(submitter)
    seen: set[str] = set()
    recipients: list[str] = []
    for item in candidates:
        value = item.strip()
        if value and value.startswith("ou_") and value not in seen:
            recipients.append(value)
            seen.add(value)
    return recipients


def manual_runner_required_card(bundle: Bundle, task: dict[str, Any], task_ref: str, assignee: str, source_ref: str = "") -> dict[str, Any]:
    task_id = str(task.get("taskId") or "")
    title = str(task.get("title") or task_id or "待处理任务")
    project_id = str(task.get("projectId") or "company-knowledge-core")
    task_type = str(task.get("taskType") or "")
    source_items = as_markdown_list(task.get("sourceMaterialRefs")) or (f"- {source_ref}" if source_ref else "- 无")
    executor_label = manual_runner_executor_label(bundle, task)
    action_lines = manual_runner_action_lines(task, task_id, executor_label)
    if task_type == "project_initialization":
        content = "\n".join(
            [
                f"项目已立项，但 Agent Ring 还没启用。这个初始化任务需要由 {executor_label} 接管。",
                "",
                f"**任务编号**：{task_id}",
                f"**任务名称**：{title}",
                f"**项目**：{project_id}",
                f"**负责 Agent**：{assignee or task.get('assignee') or '待确认'}",
                "**当前阶段**：等待执行电脑接管",
                "",
                "**你现在要做**：",
                *action_lines,
                "",
                "**高级接入方式**：",
                f"- API: POST /v0/tasks/pull taskId={task_id}",
                "- CLI/API token 由 Agent Ring 或临时 Runner 凭据提供，不要把 token 写进知识库。",
            ]
        )
        return card_result("项目初始化需要执行电脑接管", content, "orange")
    content = "\n".join(
        [
            f"Agent Ring 还没启用，这个任务需要由 {executor_label} 接管。",
            "",
            f"**任务编号**：{task_id}",
            f"**任务名称**：{title}",
            f"**项目**：{project_id}",
            f"**负责 Agent**：{assignee or task.get('assignee') or '待确认'}",
            "**当前阶段**：等待执行电脑接管",
            "",
            "**原始资料**：",
            source_items,
            "",
            "**你现在要做**：",
            *action_lines,
            "",
            "**上下文拉取**：",
            f"- API: POST /v0/tasks/pull taskId={task_id}",
            "- CLI/API token 由 Agent Ring 或临时 Runner 凭据提供，不要把 token 写进知识库。",
        ]
    )
    return card_result("需要手动接管任务", content, "orange")


def manual_runner_executor_label(bundle: Bundle, task: dict[str, Any]) -> str:
    runner_id = str(task.get("runnerId") or task.get("assignedRunner") or "").strip()
    if runner_id:
        return manual_runner_label(bundle, runner_id)
    return "指定执行电脑上的 Codex / Claude"


def manual_runner_action_lines(task: dict[str, Any], task_id: str, executor_label: str) -> list[str]:
    task_type = str(task.get("taskType") or "")
    if task_type == "project_initialization":
        return [
            f"1. 到 {executor_label} 对应会话里说：接管项目初始化任务 {task_id}",
            "2. 先从中央处理器拉取 task context pack；不要只读本地旧 bundle。",
            "3. 读取 launch.md、项目记录、任务说明、审批状态、仓库/项目群/Agent team/Runner 信息。",
            "4. 检查老仓库迁移或新仓库创建路径，补齐 README、AGENTS、Review 规则和项目上下文。",
            "5. 写回 TaskResult、AgentRun 或人工接管记录，列出风险、阻塞和首批 ProjectTask。",
        ]
    return [
        f"1. 到 {executor_label} 对应会话里说：接管知识工程任务 {task_id}",
        "2. 先从中央处理器拉取 task context pack；不要只读本地旧 bundle。",
        "3. 让本地 Agent 读取任务卡、SourceMaterial 和原始资料。",
        "4. 生成 TaskResult、结构化 KnowledgeItem draft 和证据引用。",
        "5. 写回任务结果后，调度器会自动评价，并创建 Review / Retry / Repair 后续任务。",
    ]


def as_markdown_list(value: Any) -> str:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
    elif isinstance(value, str) and value.strip():
        items = [value.strip()]
    else:
        items = []
    return "\n".join(f"- {item}" for item in items)


def feishu_open_id_for(settings: FeishuSettings, identity: str) -> str:
    identity = (identity or "").strip()
    if not identity:
        return ""
    if identity.startswith("ou_"):
        return identity
    if not settings.app_id or not settings.app_secret:
        return ""
    try:
        token = get_tenant_access_token(settings)
        users = list_feishu_users(token, limit=500)
    except KnowledgeError:
        return ""
    for user in users:
        values = [
            user.get("user_id"),
            user.get("userId"),
            user.get("union_id"),
            user.get("unionId"),
            user.get("email"),
            user.get("mobile"),
            user.get("employee_no"),
        ]
        if any(str(value or "") == identity for value in values):
            return str(user.get("open_id") or user.get("openId") or "")
    return ""


def approval_result_message(request: dict[str, str], approved: bool, instance_code: str, new_status: str) -> str:
    approval_type = request.get("approvalType", "")
    project_name = request.get("projectName") or request.get("projectId") or "未命名项目"
    project_id = request.get("projectId", "")
    if approval_type == APPROVAL_TYPE_PROJECT_INIT:
        headline = f"项目立项已通过：{project_name}" if approved else f"项目立项未通过：{project_name}"
        lines = [headline]
        if project_id:
            lines.append(f"项目ID：{project_id}")
        lines.append(f"状态：{project_approval_display_status(approved, new_status)}")
    elif approval_type == APPROVAL_TYPE_KNOWLEDGE_INGEST:
        headline = "知识入库已通过。" if approved else "知识入库未通过。"
        lines = [headline]
        if project_name:
            lines.append(f"项目：{project_name}")
        lines.append(f"状态：{display_approval_status(new_status)}")
    else:
        headline = f"{approval_type_label(approval_type)}已通过。" if approved else f"{approval_type_label(approval_type)}未通过。"
        lines = [headline]
        lines.append(f"状态：{display_approval_status(new_status)}")
    lines.append(f"审批编号：{short_approval_code(instance_code)}")
    doc_url = request.get("approvalDocUrl", "")
    if doc_url:
        lines.append(f"审批说明：{doc_url}")
    return "\n".join(lines)


def project_approval_display_status(approved: bool, new_status: str) -> str:
    if approved and str(new_status or "").lower() in {"verified", "approved", "active", "launch_approved"}:
        return "已立项"
    if not approved:
        return "未通过"
    return display_approval_status(new_status)


def short_approval_code(instance_code: str) -> str:
    value = str(instance_code or "").strip()
    if not value:
        return "未记录"
    return value if len(value) <= 12 else f"尾号 {value[-8:]}"


def approval_result_card(request: dict[str, str], approved: bool, instance_code: str, new_status: str) -> dict[str, Any]:
    approval_type = request.get("approvalType", "")
    project_name = request.get("projectName") or request.get("projectId") or "未命名项目"
    project_id = request.get("projectId", "")
    title = "项目立项审批已通过" if approved and approval_type == APPROVAL_TYPE_PROJECT_INIT else approval_type_label(approval_type) + ("已通过" if approved else "未通过")
    if not approved and approval_type == APPROVAL_TYPE_PROJECT_INIT:
        title = "项目立项审批未通过"
    lines = [
        f"项目：{project_name}",
        f"状态：{project_approval_display_status(approved, new_status) if approval_type == APPROVAL_TYPE_PROJECT_INIT else display_approval_status(new_status)}",
        f"审批编号：{short_approval_code(instance_code)}",
    ]
    if project_id:
        lines.insert(1, f"项目ID：{project_id}")
    target_ref = request.get("targetRef", "")
    if target_ref and approval_type != APPROVAL_TYPE_PROJECT_INIT:
        lines.append(f"项目文件：{target_ref}")
    doc_url = request.get("approvalDocUrl", "")
    if doc_url:
        lines.append(f"审批说明：{doc_url}")
    if approved and approval_type == APPROVAL_TYPE_PROJECT_INIT:
        lines.extend(
            [
                "",
                "下一步：",
                "1. 项目经理 Agent 确认项目范围、里程碑和 Agent team。",
                "2. 处理代码仓库、项目群和初始资料。",
                "3. 项目运行过程中的资料、决策和 AgentRun 回写到知识工程。",
            ]
        )
    return card_result(title, "\n".join(lines), "green" if approved else "red")


def project_owner_onboarding_message(request: dict[str, str], instance_code: str, new_status: str) -> str:
    project_name = request.get("projectName") or request.get("projectId") or "未命名项目"
    project_id = request.get("projectId", "")
    return "\n".join(
        [
            f"你负责的项目已立项：{project_name}",
            f"项目ID：{project_id}",
            f"状态：{project_approval_display_status(True, new_status)}",
            "",
            "后续如何给这个项目补充资料：",
            f"1. 在群里发：会议纪要：项目 {project_name}，然后粘贴会议内容。",
            f"2. 在群里发：资料：项目 {project_name}，然后粘贴资料链接、文件说明或原文。",
            "3. 需要沉淀经验时发：沉淀：<经验>",
            f"4. 本地初始化接管：对项目经理 Agent 说“接管项目初始化任务 project-init-{slug(project_id)}”。",
            "5. 本地 Agent 开发前执行 sync pull/start，结束执行 finish/sync push。",
            "6. 需要本地工具、Agent Ring 或模型 API 接入时，私聊机器人说明接入对象、用途和适用项目。",
            "",
            f"审批编号：{short_approval_code(instance_code)}",
        ]
    )


def project_owner_onboarding_card(request: dict[str, str], instance_code: str, new_status: str) -> dict[str, Any]:
    project_name = request.get("projectName") or request.get("projectId") or "未命名项目"
    content = project_owner_onboarding_message(request, instance_code, new_status)
    return card_result(f"你负责的项目已立项：{project_name}", content, "green")


def project_owner_unreachable_message(request: dict[str, str]) -> str:
    project_name = request.get("projectName") or request.get("projectId") or "未命名项目"
    project_id = request.get("projectId", "")
    owner_name = request.get("ownerName") or request.get("ownerOpenId") or "项目负责人"
    return "\n".join(
        [
            f"项目已立项，但负责人通知未送达：{project_name}",
            f"项目ID：{project_id}",
            f"负责人：{owner_name}",
            "原因：机器人当前不可主动私聊该负责人。",
            "处理：请把负责人加入机器人的可见范围，或把机器人和负责人放到项目群里。",
        ]
    )


def handle_token_approval_result(bundle: Bundle, settings: FeishuSettings, request: dict[str, str], reviewer: str, approved: bool, instance_code: str) -> dict[str, Any]:
    submitter = request.get("submitterOpenId", "")
    if approved and settings.token_send_on_approval and submitter:
        target_ref = request.get("targetRef", "")
        credential_type = "central_api"
        if target_ref:
            target_path = bundle.root / target_ref
            if target_path.exists():
                try:
                    credential_type = str(parse_frontmatter(target_path.read_text(encoding="utf-8"))[0].get("credentialType", "central_api"))
                except Exception:
                    credential_type = "central_api"
        secret_ref = credential_secret_ref(submitter, credential_type)
        send_feishu_message(settings, submitter, credential_setup_message(secret_ref, credential_type))
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


def extract_urls(text: str) -> list[str]:
    urls: list[str] = []
    for match in URL_PATTERN.finditer(text):
        value = match.group(0).strip()
        if value and value not in urls:
            urls.append(value)
    return urls


def normalize_for_keyword_match(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def is_system_change_request(text: str) -> bool:
    normalized = normalize_for_keyword_match(text)
    return any(keyword.replace(" ", "").lower() in normalized for keyword in SYSTEM_CHANGE_KEYWORDS)


def parse_research_material(text: str) -> dict[str, str]:
    stripped = text.strip()
    if not stripped:
        return {}
    urls = extract_urls(stripped)
    lowered = stripped.lower()
    starts_with_research = any(stripped.startswith(prefix) for prefix in RESEARCH_INTAKE_PREFIXES)
    contains_research = any(prefix in stripped for prefix in RESEARCH_INTAKE_PREFIXES)
    if is_system_change_request(stripped):
        return {}
    if not urls and not starts_with_research:
        return {}
    content = stripped
    for prefix in RESEARCH_INTAKE_PREFIXES:
        if content.startswith(prefix):
            content = content.removeprefix(prefix).strip(" ：:，,\n")
            break
    source_ref = urls[0] if urls else ""
    title = "研究资料"
    if urls:
        try:
            parsed = urllib.parse.urlparse(urls[0])
            title = f"研究资料：{parsed.netloc or urls[0]}"
        except ValueError:
            title = "研究资料：外部链接"
    elif content:
        title = f"研究资料：{compact_snippet(content, 30)}"
    reason = "local_url_material_pattern" if urls and not contains_research else "local_research_material_pattern"
    return {"title": title, "content": content or stripped, "sourceRef": source_ref, "reason": reason}


def system_change_request_reply() -> str:
    return "\n".join(
        [
            "这是体系变更请求，不会直接改中枢。",
            "我会按变更流程处理：先保存来源和问题，再生成 Skill / Workflow / 规则变更候选，经过评审后才能合入主体系。",
            "如果只是发资料给我研究，请直接发链接或说“研究一下”。",
        ]
    )


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
        r"^(?P<kind>资料|项目资料|会议纪要|会议记录|原始资料)[:：]\s*(?:项目\s*)?(?P<project>[^\n，,：:]+?)\s*[\n，,：:]\s*(?P<body>.+)$",
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


def process_card_submit(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, form: dict[str, str], action_name: str) -> str:
    if action_name == "project_create_submit":
        return submit_project_create_card(bundle, incoming, settings, form)
    if action_name in {"task_acceptance_accept", "task_acceptance_changes", "task_acceptance_reject"}:
        return submit_task_acceptance_card(bundle, incoming, form, action_name)
    if action_name == "knowledge_search_submit":
        return submit_knowledge_search_card(bundle, incoming, settings, form)
    if action_name == "material_capture_submit":
        return submit_material_capture_card(bundle, incoming, settings, form)
    if action_name == "meeting_notes_submit":
        text = "\n".join(
            [
                f"会议纪要：项目 {form.get('projectName', '')}",
                f"参会人：{form.get('participants', '')}",
                f"结论：{form.get('conclusion', '')}",
                f"待办：{form.get('todos', '')}",
                f"风险：{form.get('risks', '')}",
            ]
        )
        return build_reply(bundle, {**incoming, "text": text}, settings)
    if action_name == "discussion_create_submit":
        return submit_discussion_create_card(bundle, incoming, form)
    if action_name == "tool_skill_submit":
        return submit_tool_skill_card(bundle, incoming, form)
    if action_name == "agent_team_submit":
        return submit_agent_team_card(form)
    if action_name == "bind_project_group_submit":
        return submit_bind_project_group_card(bundle, incoming, form)
    if action_name == "project_handoff_submit":
        return submit_project_handoff_card(form)
    return "我没有识别这个卡片动作，请重新从菜单发起。"


def submit_task_acceptance_card(bundle: Bundle, incoming: dict[str, str], form: dict[str, str], action_name: str) -> str:
    task_id = form.get("taskId", "").strip()
    if not task_id:
        raise KnowledgeError("验收卡缺少 taskId，请重新发起验收卡。")
    decision_map = {
        "task_acceptance_accept": "accepted",
        "task_acceptance_changes": "changes_requested",
        "task_acceptance_reject": "rejected",
    }
    reviewer = incoming.get("openId") or incoming.get("userId") or "feishu-reviewer"
    result = accept_project_task_result(
        bundle,
        task_id,
        decision_map[action_name],
        reviewer,
        reason=form.get("reason", ""),
        human=normalize_card_form_value(form.get("human", "")).lower() in {"true", "1", "yes", "是"},
    )
    lines = [
        f"任务：{task_id}",
        f"验收决策：{result['decision']}",
        f"任务状态：{result['taskStatus']}",
        f"结果记录：{result['resultRef']}",
    ]
    followups = result.get("followupTaskRefs") or []
    if followups:
        lines.append(f"后续任务：{', '.join(followups)}")
    else:
        lines.append("后续任务：暂无，当前交付已闭环或等待项目经理继续安排。")
    return "\n".join(lines)


def run_card_submit_job(
    bundle: Bundle,
    incoming: dict[str, str],
    settings: FeishuSettings,
    form: dict[str, str],
    action_name: str,
    actor: str,
    job_path: Path,
) -> None:
    update_feishu_card_submit_job(job_path, "running")
    try:
        reply = process_card_submit(bundle, incoming, settings, form, action_name)
        create_audit_log(bundle, actor, "feishu.card.submit", action_name or "unknown", after="handled", policy_result="bot_gateway", details=compact_snippet(reply, 500))
        send_feishu_response(settings, incoming["messageId"], {"msg_type": "interactive", "card": card_result("已提交", reply)})
        create_audit_log(
            bundle,
            "feishu-card",
            "feishu.async_submit_result.sent",
            incoming["messageId"],
            after="sent",
            policy_result="bot_gateway",
            details=f"actionName: {action_name}\njob: {job_path.name}",
        )
        update_feishu_card_submit_job(job_path, "done", reply)
    except Exception as exc:
        detail = feishu_http_error_detail(exc) if isinstance(exc, urllib.error.HTTPError) else f"{type(exc).__name__}: {exc}"
        create_audit_log(bundle, actor, "feishu.card.submit_failed", action_name or "unknown", after="failed", policy_result="bot_gateway", details=compact_snippet(detail, 500))
        try:
            send_feishu_response(settings, incoming["messageId"], {"msg_type": "interactive", "card": card_result("提交失败", str(exc), "red")})
        except Exception as send_exc:
            create_audit_log(
                bundle,
                "feishu-card",
                "feishu.async_submit_result.failed",
                incoming["messageId"],
                after="failed",
                policy_result="bot_gateway",
                details=f"actionName: {action_name}\n{type(send_exc).__name__}: {send_exc}",
            )
        update_feishu_card_submit_job(job_path, "failed", detail)


def start_card_submit_job(
    bundle: Bundle,
    incoming: dict[str, str],
    settings: FeishuSettings,
    form: dict[str, str],
    action_name: str,
    actor: str,
    job_path: Path,
) -> None:
    threading.Thread(target=run_card_submit_job, args=(bundle, dict(incoming), settings, dict(form), action_name, actor, job_path), daemon=True).start()


def handle_card_action_event(bundle: Bundle, payload: dict[str, Any], settings: FeishuSettings) -> dict[str, Any]:
    event = payload.get("event") or {}
    action = event.get("action") or {}
    action_value = action.get("value") if isinstance(action.get("value"), dict) else {}
    form = normalize_card_form_values(action.get("form_value") or action.get("formValues") or action.get("form") or {})
    for key, value in action_value.items():
        if key != "action" and key not in form:
            form[str(key)] = normalize_card_form_value(value)
    submit_action_name, submit_params = parse_form_submit_name(str(action.get("name") or ""))
    for key, value in submit_params.items():
        if key not in form:
            form[key] = value
    action_name = str(action_value.get("action") or form.get("action") or submit_action_name or "")
    operator = event.get("operator") or {}
    operator_id = operator.get("operator_id") or {}
    if isinstance(operator_id, dict):
        open_id = str(operator_id.get("open_id") or operator_id.get("openId") or operator.get("open_id") or operator.get("openId") or "")
        user_id = str(operator_id.get("user_id") or operator_id.get("userId") or operator.get("user_id") or operator.get("userId") or "")
    else:
        open_id = str(operator.get("open_id") or operator.get("openId") or "")
        user_id = str(operator_id or operator.get("user_id") or operator.get("userId") or "")
    incoming = {
        "messageId": str(deep_find(payload, "message_id") or deep_find(payload, "open_message_id") or unique_time_id("card")),
        "chatId": str(deep_find(payload, "open_chat_id") or deep_find(payload, "chat_id") or ""),
        "chatType": str(deep_find(payload, "chat_type") or ""),
        "text": "",
        "openId": open_id,
        "userId": user_id,
        "mentionedOpenIds": "",
        "mentionedUserIds": "",
    }
    save_feishu_card_action_event(bundle, payload, action_name, form, status="received")
    try:
        if action_name == "project_create_mode":
            repo_mode = action_value.get("repoMode") or form.get("repoMode") or "existing"
            normalized_mode = "new" if repo_mode == "new" else "existing"
            card = project_create_details_card(normalized_mode)
            followup_sent = send_feishu_response_later(settings, incoming["messageId"], {"msg_type": "interactive", "card": card}, bundle=bundle, action_name=action_name)
            content = "已收到，正在发送新的项目启动卡，请在新回复里填写。" if followup_sent else "已选择，请使用新生成的精简启动卡继续。"
            response = card_action_response("已选择", content, None, action_name)
            save_feishu_card_action_event(bundle, payload, action_name, form, response=response, status="responded")
            return response
        if action_name == "material_capture_scope":
            scope = str(action_value.get("scope") or form.get("scope") or "common")
            normalized_scope = "project" if scope == "project" else "common"
            card = material_capture_card(normalized_scope)
            followup_sent = send_feishu_response_later(settings, incoming["messageId"], {"msg_type": "interactive", "card": card}, bundle=bundle, action_name=action_name)
            content = "已收到，正在发送对应的知识记录卡，请在新回复里填写。" if followup_sent else "已选择，请使用新生成的知识记录卡继续。"
            response = card_action_response("已选择", content, None, action_name)
            save_feishu_card_action_event(bundle, payload, action_name, form, response=response, status="responded")
            return response
        if settings.reply_enabled:
            job_key = feishu_card_submit_job_key(payload, action_name, form)
            reserved, job_path, job_status = reserve_feishu_card_submit_job(bundle, job_key, action_name, form)
            if reserved:
                start_card_submit_job(bundle, incoming, settings, form, action_name, open_id or user_id or "feishu-card", job_path)
                response_content = "已收到，正在后台处理。完成后我会发结果卡。"
                response_status = "queued"
                replacement_card = submitted_replacement_card("已提交，处理中", response_content, action_name)
            else:
                response_content = "这张卡已经提交过了，我正在处理或已经处理完成，请等结果卡。"
                response_status = f"duplicate_{job_status}"
                replacement_card = submitted_replacement_card("已提交，请勿重复操作", response_content, action_name)
            response = card_action_response("已收到", response_content, replacement_card, action_name)
            save_feishu_card_action_event(bundle, payload, action_name, form, response=response, status=response_status)
            return response
        reply = process_card_submit(bundle, incoming, settings, form, action_name)
        create_audit_log(bundle, open_id or user_id or "feishu-card", "feishu.card.submit", action_name or "unknown", after="handled", policy_result="bot_gateway", details=compact_snippet(reply, 500))
        result_sent = send_feishu_response_later(settings, incoming["messageId"], {"msg_type": "interactive", "card": card_result("已提交", reply)}, bundle=bundle, action_name=action_name)
        response_content = "已提交，处理结果会在新回复里发送。" if result_sent else reply
        response = card_action_response("已提交", response_content, submitted_replacement_card("已提交", response_content, action_name), action_name)
        save_feishu_card_action_event(bundle, payload, action_name, form, response=response, status="responded")
        return response
    except Exception as exc:
        create_audit_log(bundle, open_id or user_id or "feishu-card", "feishu.card.submit_failed", action_name or "unknown", after="failed", policy_result="bot_gateway", details=compact_snippet(str(exc), 500))
        send_feishu_response_later(settings, incoming["messageId"], {"msg_type": "interactive", "card": card_result("提交失败", str(exc), "red")}, bundle=bundle, action_name=action_name)
        response = card_action_response("提交失败", str(exc), submitted_replacement_card("提交失败", str(exc), action_name, ok=False), action_name, ok=False)
        save_feishu_card_action_event(bundle, payload, action_name, form, response=response, status="failed")
        return response


def card_action_response(title: str, content: str, card: dict[str, Any] | None, action_name: str, ok: bool = True) -> dict[str, Any]:
    response: dict[str, Any] = {
        "toast": {"type": "success" if ok else "error", "content": compact_snippet(content, 120)},
    }
    if card is not None:
        response["card"] = {"type": "raw", "data": card_callback_data(card)}
    return response


def submitted_replacement_card(title: str, content: str, action_name: str, ok: bool = True) -> dict[str, Any]:
    template = "grey" if ok else "red"
    lines = [
        content,
        "",
        "这张卡片已锁定，不能再次提交。",
    ]
    if ok:
        lines.append("后续结果会通过新的消息卡片发送，请以新卡片为准。")
    else:
        lines.append("请从菜单重新发起或联系项目经理 Agent 处理，不要继续提交这张旧卡片。")
    if action_name:
        lines.append(f"操作：{action_name}")
    return card_result(title, "\n".join(lines), template)


def card_callback_data(card: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(card, ensure_ascii=False))
    if isinstance(data, dict):
        config = data.setdefault("config", {})
        if isinstance(config, dict):
            config["update_multi"] = True
    return data


def normalize_card_form_values(raw: Any) -> dict[str, str]:
    if not isinstance(raw, dict):
        return {}
    result: dict[str, str] = {}
    for key, value in raw.items():
        result[str(key)] = normalize_card_form_value(value)
    return result


def normalize_card_form_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return ",".join(normalize_card_form_value(item) for item in value if normalize_card_form_value(item))
    if isinstance(value, dict):
        for key in ["value", "text", "content", "name"]:
            if key in value:
                return normalize_card_form_value(value[key])
        if "option" in value:
            return normalize_card_form_value(value["option"])
    return str(value).strip()


def card_result(title: str, content: str, template: str = "green") -> dict[str, Any]:
    return interactive_card(title, [{"tag": "markdown", "content": content}], template)


def normalize_project_id(project_raw: str) -> str:
    try:
        return slug(project_raw)
    except KnowledgeError:
        digest = hashlib.sha1(project_raw.encode("utf-8")).hexdigest()[:8]
        return f"project-{digest}"


def material_processing_profile(action: str) -> dict[str, Any]:
    normalized = action.strip() or "knowledge_extract"
    if normalized != "knowledge_extract" and not capability_feature_flags()["FEISHU_CAPABILITY_ACTIONS_ENABLED"]:
        normalized = "knowledge_extract"
    profiles = {
        "knowledge_extract": {
            "taskType": "knowledge_capture",
            "workSourceType": "knowledge_ingest",
            "sourceReason": "Feishu material should become reviewed reusable knowledge.",
            "expectedOutput": [
                "Parse original material.",
                "Create evidence-backed summary.",
                "Create structured draft knowledge with source refs.",
                "Return TaskResult with evidenceRefs and knowledgeDraft.",
            ],
        },
        "skill_extract": {
            "taskType": "skill_extract",
            "workSourceType": "capability_intake",
            "sourceReason": "Feishu material should become a reviewed Agent Skill candidate.",
            "expectedOutput": [
                "Extract a reusable Agent Skill candidate from the material.",
                "Return TaskResult with capabilityCandidates including candidateType=skill, targetAgents, riskLevel, and evidenceRefs.",
                "Do not publish the skill directly; route through capability review.",
            ],
        },
        "workflow_extract": {
            "taskType": "workflow_extract",
            "workSourceType": "capability_intake",
            "sourceReason": "Feishu material should become a reviewed Agent Workflow candidate.",
            "expectedOutput": [
                "Extract a reusable Agent Workflow candidate from the material.",
                "Return TaskResult with capabilityCandidates including candidateType=workflow and evidenceRefs.",
                "Do not activate the workflow directly; route through capability review.",
            ],
        },
        "tool_candidate": {
            "taskType": "tool_candidate",
            "workSourceType": "capability_intake",
            "sourceReason": "Feishu material should become a Tool registration candidate.",
            "expectedOutput": [
                "Assess whether a registered ToolAsset is needed.",
                "Return TaskResult with capabilityCandidates including candidateType=tool, riskLevel, owner, and approvalRequired when appropriate.",
                "Do not expose credentials or register high-risk tools without Tool Owner review.",
            ],
        },
        "capability_release_draft": {
            "taskType": "capability_update_proposal",
            "workSourceType": "capability_intake",
            "sourceReason": "Feishu material should become a capability release proposal.",
            "expectedOutput": [
                "Identify reusable Agent capability updates from the material.",
                "Return TaskResult with capabilityCandidates and recommended next action to create CapabilityRelease.",
                "Route every candidate through capability review before release.",
            ],
        },
    }
    profile = dict(profiles.get(normalized, profiles["knowledge_extract"]))
    profile["action"] = normalized if normalized in profiles else "knowledge_extract"
    return profile


def create_project_material_task(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, material: dict[str, str]) -> tuple[str, str, str, str]:
    content = material["body"]
    if looks_like_secret(content):
        raise KnowledgeError("material looks like it contains a secret; refusing to store it")
    owner = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    project_id = material["projectId"]
    project_path = bundle.root / "projects" / slug(project_id) / "project.md"
    if not project_path.exists():
        make_project(bundle, project_id, material.get("projectRaw", project_id), owner, "")
    source_ref = f"feishu://message/{incoming.get('messageId')}"
    project_owner = project_owner_open_id(bundle, settings, project_id)
    assignee = project_owner or "梅晓华"
    title = "整理会议纪要" if material["sourceType"] == "meeting_notes" else "整理项目资料"
    profile = material_processing_profile(material.get("processingAction", ""))
    result = create_source_material(
        bundle,
        title=f"{title}：{material['projectRaw']}",
        source_ref=source_ref,
        submitter=owner,
        project_id=project_id,
        material_type="meeting" if material["sourceType"] == "meeting_notes" else "project_material",
        storage_ref="",
        content=content,
        sensitivity="internal",
        extraction_tool="feishu-bot-intake",
        extraction_status="task_created",
        create_task_flag=True,
        assignee=assignee,
        task_work_source_type=str(profile["workSourceType"]),
        task_source_reason=str(profile["sourceReason"]),
        task_extra_frontmatter={
            "capabilityProcessingAction": str(profile["action"]),
            "expectedOutput": profile["expectedOutput"],
            "updatedAt": utc_now(),
        },
        task_type=str(profile["taskType"]),
    )
    task_path = bundle.root / result["taskRef"]
    task_fm, _ = parse_task_file(task_path)
    task_id = str(task_fm.get("taskId", task_path.stem))
    notify_manual_runner_required(bundle, settings, incoming, task_path, task_id, assignee, result["sourceRef"], project_id)
    return result["sourceRef"], result["taskRef"], task_id, assignee


def create_research_material_source(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, material: dict[str, str]) -> dict[str, Any]:
    del settings
    content = material.get("content", "").strip()
    if not content:
        raise KnowledgeError("research material content is required")
    if looks_like_secret(content):
        raise KnowledgeError("material looks like it contains a secret; refusing to store it")
    owner = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    source_ref = material.get("sourceRef", "").strip() or f"feishu://message/{incoming.get('messageId')}"
    result = create_source_material(
        bundle,
        title=material.get("title", "").strip() or "研究资料",
        source_ref=source_ref,
        submitter=owner,
        project_id="company-knowledge-core",
        material_type="research_reference",
        storage_ref="",
        content=content,
        sensitivity="internal",
        extraction_tool="feishu-bot-research-intake",
        extraction_status="captured",
        create_task_flag=False,
    )
    source_path = bundle.root / result["sourceRef"]
    if source_path.exists():
        update_frontmatter_file(
            source_path,
            {
                "intakeSource": "feishu_research_material",
                "processingMode": "feishu_direct_store",
                "feishuMessageId": incoming.get("messageId", ""),
                "feishuChatId": incoming.get("chatId", ""),
                "feishuChatType": incoming.get("chatType", ""),
                "feishuOpenId": incoming.get("openId", ""),
                "feishuUserId": incoming.get("userId", ""),
                "updatedAt": utc_now(),
            },
        )
    return {
        "sourceRef": result["sourceRef"],
        "idempotent": bool(result.get("idempotent")),
    }


def create_research_material_task(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, material: dict[str, str]) -> dict[str, Any]:
    content = material.get("content", "").strip()
    if not content:
        raise KnowledgeError("research material content is required")
    owner = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    source_ref = material.get("sourceRef", "").strip() or f"feishu://message/{incoming.get('messageId')}"
    assignee = "agent.company-knowledge-core.knowledge-engineering"
    processor_runner = os.environ.get("FEISHU_DIRECT_MATERIAL_RUNNER", "runner.feishu-direct-material-processor").strip()
    result = create_source_material(
        bundle,
        title=material.get("title", "").strip() or "研究资料",
        source_ref=source_ref,
        submitter=owner,
        project_id="company-knowledge-core",
        material_type="research_reference",
        storage_ref="",
        content=content,
        sensitivity="internal",
        extraction_tool="feishu-bot-research-intake",
        extraction_status="task_created",
        create_task_flag=True,
        assignee=assignee,
        task_work_source_type="research",
        task_research_question=content,
        task_source_reason="Legacy task-status harness for source material processing.",
        task_extra_frontmatter={
            "intakeSource": "feishu_research_material",
            "processingMode": "legacy_task_status_test",
            "feishuMessageId": incoming.get("messageId", ""),
            "feishuChatId": incoming.get("chatId", ""),
            "feishuChatType": incoming.get("chatType", ""),
            "feishuOpenId": incoming.get("openId", ""),
            "feishuUserId": incoming.get("userId", ""),
            "approvalRequired": False,
        },
    )
    task_path = bundle.root / result["taskRef"]
    task_fm, _ = parse_task_file(task_path)
    task_id = str(task_fm.get("taskId", task_path.stem))
    return {
        "sourceRef": result["sourceRef"],
        "taskRef": result["taskRef"],
        "taskId": task_id,
        "assignee": assignee,
        "runnerId": processor_runner,
        "idempotent": bool(result.get("idempotent")),
    }


def create_common_knowledge_material_task(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings, form: dict[str, str]) -> tuple[str, str, str, str]:
    content = form.get("content", "").strip()
    if looks_like_secret(content):
        raise KnowledgeError("material looks like it contains a secret; refusing to store it")
    owner = incoming.get("openId") or incoming.get("userId") or "feishu-user"
    source_ref = form.get("sourceRef", "").strip() or f"feishu://message/{incoming.get('messageId')}"
    title = form.get("title", "").strip() or "公共知识资料"
    scope_note = form.get("scopeNote", "").strip()
    content_with_scope = content
    if scope_note:
        content_with_scope = f"{content}\n\n适用范围：{scope_note}"
    assignee = "agent.company-knowledge-core.knowledge-engineering"
    profile = material_processing_profile(form.get("processingAction", ""))
    result = create_source_material(
        bundle,
        title=f"公共知识沉淀：{title}",
        source_ref=source_ref,
        submitter=owner,
        project_id="company-knowledge-core",
        material_type="common_knowledge",
        storage_ref="",
        content=content_with_scope,
        sensitivity="internal",
        extraction_tool="feishu-bot-intake",
        extraction_status="task_created",
        create_task_flag=True,
        assignee=assignee,
        task_work_source_type=str(profile["workSourceType"]),
        task_source_reason=str(profile["sourceReason"]),
        task_extra_frontmatter={
            "capabilityProcessingAction": str(profile["action"]),
            "expectedOutput": profile["expectedOutput"],
            "updatedAt": utc_now(),
        },
        task_type=str(profile["taskType"]),
    )
    task_path = bundle.root / result["taskRef"]
    task_fm, _ = parse_task_file(task_path)
    task_id = str(task_fm.get("taskId", task_path.stem))
    notify_manual_runner_required(bundle, settings, incoming, task_path, task_id, assignee, result["sourceRef"], "company-knowledge-core")
    return result["sourceRef"], result["taskRef"], task_id, assignee


def parse_task_file(path: Path) -> tuple[dict[str, Any], str]:
    from .core import parse_frontmatter, read_text

    return parse_frontmatter(read_text(path))


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
    return send_feishu_response(settings, message_id, {"msg_type": "text", "reply": text})


def send_feishu_response_later(settings: FeishuSettings, message_id: str, response: dict[str, Any], bundle: Bundle | None = None, action_name: str = "") -> bool:
    if not settings.reply_enabled or not message_id:
        return False

    def worker() -> None:
        try:
            send_feishu_response(settings, message_id, response)
            if bundle is not None:
                record_feishu_delivery_attempt(
                    message_id,
                    "async_reply",
                    "sent",
                    event_id=message_id,
                    response_code="ok",
                    summary=f"actionName: {action_name}; msgType: {response.get('msg_type', 'text')}",
                )
            if bundle is not None:
                create_audit_log(
                    bundle,
                    "feishu-card",
                    "feishu.async_reply.sent",
                    message_id,
                    after="sent",
                    policy_result="bot_gateway",
                    details=f"actionName: {action_name}\nmsgType: {response.get('msg_type', 'text')}",
                )
        except urllib.error.HTTPError as exc:
            detail = feishu_http_error_detail(exc)
            error_info = classify_feishu_delivery_error(detail)
            if bundle is not None:
                notification_ref = create_feishu_permission_notification(bundle, {"messageId": message_id, "openId": "feishu-card", "userId": ""}, error_info, detail)
                record_feishu_delivery_attempt(
                    message_id,
                    "async_reply",
                    "failed",
                    event_id=message_id,
                    response_code=str(exc.code),
                    error_class=str(error_info.get("errorClass") or ""),
                    summary=detail + (f"\nnotificationRef={notification_ref}" if notification_ref else ""),
                )
                create_audit_log(
                    bundle,
                    "feishu-card",
                    "feishu.async_reply.failed",
                    message_id,
                    after="failed",
                    policy_result="bot_gateway",
                    details=f"actionName: {action_name}\n{detail}",
                )
        except Exception as exc:
            if bundle is not None:
                error_info = classify_feishu_delivery_error(str(exc))
                notification_ref = create_feishu_permission_notification(bundle, {"messageId": message_id, "openId": "feishu-card", "userId": ""}, error_info, str(exc))
                record_feishu_delivery_attempt(
                    message_id,
                    "async_reply",
                    "failed",
                    event_id=message_id,
                    error_class=str(error_info.get("errorClass") or type(exc).__name__),
                    summary=str(exc) + (f"\nnotificationRef={notification_ref}" if notification_ref else ""),
                )
                create_audit_log(
                    bundle,
                    "feishu-card",
                    "feishu.async_reply.failed",
                    message_id,
                    after="failed",
                    policy_result="bot_gateway",
                    details=f"actionName: {action_name}\n{type(exc).__name__}: {exc}",
                )

    threading.Thread(target=worker, daemon=True).start()
    return True


def send_feishu_response(settings: FeishuSettings, message_id: str, response: dict[str, Any]) -> bool:
    if not message_id:
        return False
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/im/v1/messages/{message_id}/reply"
    msg_type = str(response.get("msg_type") or "text")
    if msg_type == "interactive":
        content = json.dumps(response.get("card") or {}, ensure_ascii=False)
    else:
        content = json.dumps({"text": str(response.get("reply", ""))}, ensure_ascii=False)
    body = {
        "msg_type": msg_type,
        "content": content,
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


def send_feishu_incoming_response(settings: FeishuSettings, incoming: dict[str, str], response: dict[str, Any]) -> bool:
    try:
        if incoming.get("chatType") == "p2p" and incoming.get("openId"):
            return send_feishu_direct_response(settings, incoming["openId"], response, receive_id_type="open_id")
        if incoming.get("chatId"):
            return send_feishu_direct_response(settings, incoming["chatId"], response, receive_id_type="chat_id")
    except urllib.error.HTTPError:
        if incoming.get("messageId"):
            return send_feishu_response(settings, incoming["messageId"], response)
        raise
    if incoming.get("messageId"):
        return send_feishu_response(settings, incoming["messageId"], response)
    return False


def send_feishu_message(settings: FeishuSettings, open_id: str, text: str) -> bool:
    return send_feishu_direct_response(settings, open_id, {"msg_type": "text", "reply": text})


def send_feishu_direct_response(settings: FeishuSettings, receive_id: str, response: dict[str, Any], receive_id_type: str = "open_id") -> bool:
    if not receive_id:
        return False
    token = get_tenant_access_token(settings)
    url = f"{FEISHU_API_BASE}/im/v1/messages?receive_id_type={urllib.parse.quote(receive_id_type)}"
    msg_type = str(response.get("msg_type") or "text")
    if msg_type == "interactive":
        content = json.dumps(response.get("card") or {}, ensure_ascii=False)
    else:
        content = json.dumps({"text": str(response.get("reply", ""))}, ensure_ascii=False)
    body = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": content,
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

# Command executor layer. The functions above are the Feishu business implementation
# migrated out of feishu.py; this layer turns routed commands into audited side effects.
def execute_feishu_command(bundle: Bundle, command, payload: dict[str, Any], settings: FeishuSettings) -> dict[str, Any]:
    if command.kind == "approval":
        return handle_approval_event(bundle, payload, settings)
    if command.kind == "card_action":
        return handle_card_action_event(bundle, payload, settings)
    if command.kind == "ignored":
        return {"ok": True, "ignored": command.event_type or "unknown"}
    if command.kind == "ignore_empty_message":
        return {"ok": True, "ignored": "empty_message"}
    if command.kind == "process_message":
        return execute_message_command(bundle, command.incoming, settings)
    raise KnowledgeError(f"unsupported Feishu command: {command.kind}")


def execute_message_command(bundle: Bundle, incoming: dict[str, str], settings: FeishuSettings) -> dict[str, Any]:
    duplicate = claim_feishu_message_event(bundle, incoming)
    if duplicate:
        return {
            "ok": True,
            "duplicate": True,
            "messageId": incoming.get("messageId", ""),
            "status": duplicate.get("status", "processing"),
            "sent": False,
        }
    try:
        response = build_feishu_response(bundle, incoming, settings)
        reply = str(response.get("reply", ""))
        create_feishu_audit(bundle, incoming, reply)
    except Exception as exc:
        fail_feishu_message_event(bundle, incoming, exc)
        raise
    sent = False
    reply_error = ""
    if settings.reply_enabled and settings.app_id and settings.app_secret:
        try:
            sent = send_feishu_incoming_response(settings, incoming, response)
        except urllib.error.HTTPError as exc:
            reply_error = feishu_http_error_detail(exc)
            error_info = classify_feishu_delivery_error(reply_error)
            if response.get("msg_type") == "interactive":
                try:
                    fallback_reply = "\n".join(
                        [
                            reply,
                            "",
                            "卡片暂时发送失败，我先用文字方式继续：",
                            build_reply(bundle, incoming, settings),
                        ]
                    )
                    sent = send_feishu_response(settings, incoming["messageId"], {"msg_type": "text", "reply": fallback_reply})
                    reply_error = f"{reply_error}\nfallbackTextSent: true"
                except Exception as fallback_exc:
                    reply_error = f"{reply_error}\nfallbackTextError: {fallback_exc}"
            create_audit_log(bundle, incoming.get("openId") or incoming.get("userId") or "feishu-user", "feishu.reply.failed", incoming.get("messageId", ""), after="failed", policy_result="bot_gateway", details=reply_error)
            notification_ref = create_feishu_permission_notification(bundle, incoming, error_info, reply_error)
            record_feishu_delivery_attempt(
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
            error_info = classify_feishu_delivery_error(reply_error)
            create_audit_log(bundle, incoming.get("openId") or incoming.get("userId") or "feishu-user", "feishu.reply.failed", incoming.get("messageId", ""), after="failed", policy_result="bot_gateway", details=reply_error)
            notification_ref = create_feishu_permission_notification(bundle, incoming, error_info, reply_error)
            record_feishu_delivery_attempt(
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
    complete_feishu_message_event(bundle, incoming, reply, sent, reply_error)
    update_knowledge_query_delivery(bundle, incoming, sent, reply_error)
    return result
