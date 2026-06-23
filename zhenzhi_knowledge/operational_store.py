from __future__ import annotations

import hashlib
import json
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .core import Bundle, KnowledgeError, connect_database, database_url, fetchall_dicts, utc_now


OPERATIONAL_MIGRATION_VERSION = "20260621_001_operational_store"
OPERATIONAL_MIGRATION_CHECKSUM = "sha256:" + hashlib.sha256(OPERATIONAL_MIGRATION_VERSION.encode("utf-8")).hexdigest()
OPERATIONAL_TABLES = [
    "operational_events",
    "api_command_envelopes",
    "feishu_delivery_attempts",
    "migration_versions",
]
SECRET_ENV_NAMES = [
    "FEISHU_APP_SECRET",
    "FEISHU_VERIFICATION_TOKEN",
    "ZHENZHI_KNOWLEDGE_API_TOKEN",
]
DATABASE_ENV_NAMES = [
    "DATABASE_URL",
    "ZHENZHI_KNOWLEDGE_DATABASE_URL",
]


def operational_strict() -> bool:
    return os.environ.get("ZHENZHI_KNOWLEDGE_OPERATIONAL_STRICT", "false").lower() == "true"


def safe_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def ensure_operational_schema(applied_by: str = "api") -> dict[str, Any]:
    conn = connect_database()
    started = time.perf_counter()
    try:
        conn.execute(
            """
            create table if not exists migration_versions (
                version text primary key,
                "appliedAt" text not null default '',
                "appliedBy" text not null default '',
                checksum text not null default '',
                "rollbackNotes" text not null default ''
            )
            """
        )
        conn.execute(
            """
            create table if not exists operational_events (
                "eventId" text primary key,
                "sourceChannel" text not null default '',
                "idempotencyKey" text not null default '',
                "actorRef" text not null default '',
                "projectRef" text not null default '',
                "targetRef" text not null default '',
                status text not null default '',
                "errorClass" text not null default '',
                summary text not null default '',
                "createdAt" text not null default '',
                "updatedAt" text not null default ''
            )
            """
        )
        conn.execute(
            """
            create table if not exists api_command_envelopes (
                "commandId" text primary key,
                route text not null default '',
                "actorRef" text not null default '',
                "permissionDecision" text not null default '',
                "idempotencyKey" text not null default '',
                "requestHash" text not null default '',
                "responseHash" text not null default '',
                "auditRef" text not null default '',
                "notificationRefs" jsonb not null default '[]'::jsonb,
                status text not null default '',
                "createdAt" text not null default '',
                "updatedAt" text not null default ''
            )
            """
        )
        conn.execute(
            """
            create table if not exists feishu_delivery_attempts (
                "attemptId" text primary key,
                "eventId" text not null default '',
                "messageId" text not null default '',
                "cardId" text not null default '',
                "jobKey" text not null default '',
                "deliveryMethod" text not null default '',
                "responseCode" text not null default '',
                "retryCount" integer not null default 0,
                "finalStatus" text not null default '',
                "errorClass" text not null default '',
                summary text not null default '',
                "createdAt" text not null default '',
                "updatedAt" text not null default ''
            )
            """
        )
        conn.execute('create index if not exists operational_events_status_idx on operational_events (status)')
        conn.execute('create index if not exists operational_events_source_idx on operational_events ("sourceChannel")')
        conn.execute('create index if not exists api_command_route_idx on api_command_envelopes (route)')
        conn.execute('create index if not exists feishu_delivery_message_idx on feishu_delivery_attempts ("messageId")')
        conn.execute(
            """
            insert into migration_versions (version, "appliedAt", "appliedBy", checksum, "rollbackNotes")
            values (%s, %s, %s, %s, %s)
            on conflict (version) do update set
                "appliedAt" = excluded."appliedAt",
                "appliedBy" = excluded."appliedBy",
                checksum = excluded.checksum,
                "rollbackNotes" = excluded."rollbackNotes"
            """,
            (
                OPERATIONAL_MIGRATION_VERSION,
                utc_now(),
                applied_by,
                OPERATIONAL_MIGRATION_CHECKSUM,
                "Rollback drops additive operational tables only after backup/clone verification.",
            ),
        )
        conn.commit()
        return {
            "ok": True,
            "version": OPERATIONAL_MIGRATION_VERSION,
            "latencyMs": round((time.perf_counter() - started) * 1000, 2),
            "tables": OPERATIONAL_TABLES,
        }
    finally:
        conn.close()


def try_ensure_operational_schema(applied_by: str = "api") -> dict[str, Any]:
    try:
        return ensure_operational_schema(applied_by)
    except Exception as exc:
        if operational_strict():
            raise
        return {"ok": False, "error": compact_error(exc)}


def record_operational_event(
    event_id: str,
    source_channel: str,
    status: str,
    actor_ref: str = "",
    project_ref: str = "",
    target_ref: str = "",
    idempotency_key: str = "",
    error_class: str = "",
    summary: str = "",
) -> dict[str, Any]:
    event_id = event_id or f"event-{safe_hash([source_channel, target_ref, utc_now()])[:16]}"
    return _write(
        """
        insert into operational_events (
            "eventId", "sourceChannel", "idempotencyKey", "actorRef", "projectRef", "targetRef",
            status, "errorClass", summary, "createdAt", "updatedAt"
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        on conflict ("eventId") do update set
            "sourceChannel" = excluded."sourceChannel",
            "idempotencyKey" = excluded."idempotencyKey",
            "actorRef" = excluded."actorRef",
            "projectRef" = excluded."projectRef",
            "targetRef" = excluded."targetRef",
            status = excluded.status,
            "errorClass" = excluded."errorClass",
            summary = excluded.summary,
            "updatedAt" = excluded."updatedAt"
        """,
        (
            event_id,
            source_channel,
            idempotency_key,
            actor_ref,
            project_ref,
            target_ref,
            status,
            error_class,
            compact_text(summary),
            utc_now(),
            utc_now(),
        ),
        "operational_events",
        event_id,
    )


def record_api_command_envelope(
    route: str,
    payload: dict[str, Any],
    status: str,
    permission_decision: str = "allowed",
    response: dict[str, Any] | None = None,
    audit_ref: str = "",
    notification_refs: list[str] | None = None,
) -> dict[str, Any]:
    envelope = payload.get("commandEnvelope") if isinstance(payload.get("commandEnvelope"), dict) else {}
    actor = str(envelope.get("actorRef") or payload.get("actorRef") or payload.get("actor") or "api")
    idem = str(envelope.get("idempotencyKey") or payload.get("idempotencyKey") or "")
    command_id = safe_hash([route, actor, idem or safe_hash(payload), permission_decision])[:32]
    return _write(
        """
        insert into api_command_envelopes (
            "commandId", route, "actorRef", "permissionDecision", "idempotencyKey",
            "requestHash", "responseHash", "auditRef", "notificationRefs", status, "createdAt", "updatedAt"
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)
        on conflict ("commandId") do update set
            "permissionDecision" = excluded."permissionDecision",
            "responseHash" = excluded."responseHash",
            "auditRef" = excluded."auditRef",
            "notificationRefs" = excluded."notificationRefs",
            status = excluded.status,
            "updatedAt" = excluded."updatedAt"
        """,
        (
            command_id,
            route,
            actor,
            permission_decision,
            idem,
            safe_hash(payload),
            safe_hash(response or {}),
            audit_ref,
            json.dumps(notification_refs or [], ensure_ascii=False),
            status,
            utc_now(),
            utc_now(),
        ),
        "api_command_envelopes",
        command_id,
    )


def record_feishu_delivery_attempt(
    message_id: str,
    delivery_method: str,
    final_status: str,
    event_id: str = "",
    card_id: str = "",
    job_key: str = "",
    response_code: str = "",
    retry_count: int = 0,
    error_class: str = "",
    summary: str = "",
) -> dict[str, Any]:
    attempt_id = safe_hash([event_id, message_id, card_id, job_key, delivery_method, final_status, retry_count])[:32]
    return _write(
        """
        insert into feishu_delivery_attempts (
            "attemptId", "eventId", "messageId", "cardId", "jobKey", "deliveryMethod",
            "responseCode", "retryCount", "finalStatus", "errorClass", summary, "createdAt", "updatedAt"
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        on conflict ("attemptId") do update set
            "responseCode" = excluded."responseCode",
            "retryCount" = excluded."retryCount",
            "finalStatus" = excluded."finalStatus",
            "errorClass" = excluded."errorClass",
            summary = excluded.summary,
            "updatedAt" = excluded."updatedAt"
        """,
        (
            attempt_id,
            event_id,
            message_id,
            card_id,
            job_key,
            delivery_method,
            response_code,
            int(retry_count),
            final_status,
            error_class,
            compact_text(summary),
            utc_now(),
            utc_now(),
        ),
        "feishu_delivery_attempts",
        attempt_id,
    )


def operational_store_status() -> dict[str, Any]:
    conn = connect_database()
    try:
        rows: dict[str, int | None] = {}
        for table in OPERATIONAL_TABLES:
            exists = bool(conn.execute("select to_regclass(%s)", (table,)).fetchone()[0])
            if exists:
                rows[table] = int(conn.execute(f"select count(*) from {table}").fetchone()[0])
            else:
                rows[table] = None
        versions = []
        if rows.get("migration_versions") is not None:
            versions = fetchall_dicts(conn.execute('select version, "appliedAt", "appliedBy", checksum, "rollbackNotes" from migration_versions'))
        return {"ok": all(value is not None for value in rows.values()), "version": OPERATIONAL_MIGRATION_VERSION, "tables": rows, "versions": versions}
    finally:
        conn.close()


def rollback_operational_schema(to_version: str, allow_destructive: bool = False) -> dict[str, Any]:
    if to_version not in {"base", "none", "0"}:
        raise KnowledgeError("only rollback --to base is supported for additive operational-store migration")
    if not allow_destructive:
        raise KnowledgeError("rollback requires --allow-destructive after backup/clone verification")
    conn = connect_database()
    try:
        for table in ["feishu_delivery_attempts", "api_command_envelopes", "operational_events", "migration_versions"]:
            conn.execute(f"drop table if exists {table}")
        conn.commit()
        return {"ok": True, "rolledBackTo": to_version, "droppedTables": OPERATIONAL_TABLES}
    finally:
        conn.close()


def backup_readiness() -> dict[str, Any]:
    backup_ref = os.environ.get("ZHENZHI_KNOWLEDGE_BACKUP_REF", "").strip() or os.environ.get("PG_BACKUP_REF", "").strip()
    pg_dump_ref = os.environ.get("ZHENZHI_KNOWLEDGE_PG_DUMP_REF", "").strip()
    blockers: list[str] = []
    if not backup_ref:
        blockers.append("missing backup snapshot ref: set ZHENZHI_KNOWLEDGE_BACKUP_REF or PG_BACKUP_REF")
    if not pg_dump_ref:
        blockers.append("missing pg_dump evidence ref: set ZHENZHI_KNOWLEDGE_PG_DUMP_REF")
    return {"ready": not blockers, "backupRefPresent": bool(backup_ref), "pgDumpRefPresent": bool(pg_dump_ref), "blockers": blockers}


def live_readiness_report(check_feishu_api: bool = False, migrate: bool = False) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    blockers: list[str] = []

    _check_env(checks, blockers, "FEISHU_APP_ID", safe_suffix=True)
    _check_env(checks, blockers, "FEISHU_APP_SECRET", secret=True)
    _check_env(checks, blockers, "FEISHU_VERIFICATION_TOKEN", secret=True)
    _check_env(checks, blockers, "ZHENZHI_KNOWLEDGE_API_TOKEN", secret=True)
    env_present = {item["name"]: bool(item.get("present")) for item in checks}
    callback_url = os.environ.get("FEISHU_CALLBACK_URL", "").strip()
    checks.append(
        {
            "name": "FEISHU_CALLBACK_URL",
            "label": "Feishu callback public URL",
            "ok": bool(callback_url),
            "publicUrl": redact_url(callback_url) if callback_url else "",
        }
    )
    if not callback_url:
        blockers.append("missing FEISHU_CALLBACK_URL")
    env_present["FEISHU_CALLBACK_URL"] = bool(callback_url)

    database_ready = False
    try:
        parsed = urllib.parse.urlparse(database_url())
        database_ready = True
        checks.append({"name": "DATABASE_URL", "label": "PostgreSQL database DSN", "ok": True, "scheme": parsed.scheme, "host": parsed.hostname or "", "database": (parsed.path or "").strip("/")})
    except Exception as exc:
        blockers.append(str(exc))
        checks.append({"name": "DATABASE_URL", "label": "PostgreSQL database DSN", "ok": False, "error": compact_error(exc)})

    if migrate:
        schema = try_ensure_operational_schema("readiness")
    else:
        schema = try_ensure_operational_schema("readiness-check")
    schema_ready = bool(schema.get("ok"))
    checks.append({"name": "postgres_operational_schema", "label": "PostgreSQL operational schema", **schema})
    if not schema.get("ok"):
        blockers.append(f"postgres operational schema unavailable: {schema.get('error')}")

    api_port = os.environ.get("ZHENZHI_KNOWLEDGE_API_PORT", "").strip()
    api_port_configured = bool(api_port)
    if api_port:
        checks.append({"name": "api_port", "label": "API gateway port configuration", "ok": _port_available(api_port), "port": api_port})
    else:
        checks.append({"name": "api_port", "label": "API gateway port configuration", "ok": False, "error": "missing ZHENZHI_KNOWLEDGE_API_PORT"})
        blockers.append("missing ZHENZHI_KNOWLEDGE_API_PORT")

    feishu_api_ready = False
    if check_feishu_api:
        feishu = _check_feishu_token_api()
        feishu_api_ready = bool(feishu.get("ok"))
        checks.append({"name": "feishu_api_reachability", "label": "Feishu tenant token API reachability", **feishu})
        if not feishu.get("ok"):
            blockers.append(f"Feishu API unreachable or rejected credentials: {feishu.get('error')}")
    else:
        checks.append(
            {
                "name": "feishu_api_reachability",
                "label": "Feishu tenant token API reachability",
                "ok": False,
                "skipped": True,
                "nextAction": "rerun readiness with --check-feishu-api from staging network",
            }
        )
        blockers.append("Feishu API reachability not checked")

    backup = backup_readiness()
    backup_ready = bool(backup.get("ready"))
    checks.append({"name": "backup_readiness", "label": "PostgreSQL backup prerequisites", **backup})
    blockers.extend(backup["blockers"])

    reply_enabled = os.environ.get("FEISHU_REPLY_ENABLED", "true").lower() != "false"
    capabilities = [
        _readiness_capability(
            "feishu_credentials",
            "Feishu app credentials",
            env_present.get("FEISHU_APP_ID", False) and env_present.get("FEISHU_APP_SECRET", False) and env_present.get("FEISHU_VERIFICATION_TOKEN", False),
            blockers=[
                *([] if env_present.get("FEISHU_APP_ID") else ["missing FEISHU_APP_ID"]),
                *([] if env_present.get("FEISHU_APP_SECRET") else ["missing FEISHU_APP_SECRET"]),
                *([] if env_present.get("FEISHU_VERIFICATION_TOKEN") else ["missing FEISHU_VERIFICATION_TOKEN"]),
            ],
            evidence=["FEISHU_APP_ID present", "FEISHU_APP_SECRET present", "FEISHU_VERIFICATION_TOKEN present"],
            next_action="Set Feishu app id, app secret, and verification token in the runtime secret store.",
        ),
        _readiness_capability(
            "feishu_callback_route",
            "Feishu callback route",
            bool(callback_url) and env_present.get("FEISHU_VERIFICATION_TOKEN", False),
            blockers=[
                *([] if callback_url else ["missing FEISHU_CALLBACK_URL"]),
                *([] if env_present.get("FEISHU_VERIFICATION_TOKEN") else ["missing FEISHU_VERIFICATION_TOKEN"]),
            ],
            evidence=["POST /integrations/feishu/events route implemented", "Feishu URL verification/token rejection handled"],
            next_action="Configure Feishu event/card callback URL to POST /integrations/feishu/events.",
        ),
        _readiness_capability(
            "feishu_message_delivery",
            "Feishu message delivery",
            reply_enabled and env_present.get("FEISHU_APP_ID", False) and env_present.get("FEISHU_APP_SECRET", False) and feishu_api_ready,
            blockers=[
                *([] if reply_enabled else ["FEISHU_REPLY_ENABLED disables live replies"]),
                *([] if env_present.get("FEISHU_APP_ID") else ["missing FEISHU_APP_ID"]),
                *([] if env_present.get("FEISHU_APP_SECRET") else ["missing FEISHU_APP_SECRET"]),
                *([] if feishu_api_ready else ["Feishu API reachability not proven"]),
            ],
            evidence=["text reply path implemented", "direct message API path implemented", "permission failure notification path implemented"],
            next_action="Rerun readiness with --check-feishu-api from staging network, then send live text probe.",
        ),
        _readiness_capability(
            "feishu_card_delivery",
            "Feishu interactive card delivery",
            reply_enabled and bool(callback_url) and env_present.get("FEISHU_APP_ID", False) and env_present.get("FEISHU_APP_SECRET", False) and feishu_api_ready,
            blockers=[
                *([] if reply_enabled else ["FEISHU_REPLY_ENABLED disables live card replies"]),
                *([] if callback_url else ["missing FEISHU_CALLBACK_URL"]),
                *([] if env_present.get("FEISHU_APP_ID") else ["missing FEISHU_APP_ID"]),
                *([] if env_present.get("FEISHU_APP_SECRET") else ["missing FEISHU_APP_SECRET"]),
                *([] if feishu_api_ready else ["Feishu API reachability not proven"]),
            ],
            evidence=["interactive card response path implemented", "card callback idempotency job path implemented", "fallback text path implemented"],
            next_action="Rerun readiness with --check-feishu-api, then submit and retry a live Feishu card.",
        ),
        _readiness_capability(
            "api_gateway_routes",
            "API gateway routes and bearer auth",
            env_present.get("ZHENZHI_KNOWLEDGE_API_TOKEN", False) and api_port_configured,
            blockers=[
                *([] if env_present.get("ZHENZHI_KNOWLEDGE_API_TOKEN") else ["missing ZHENZHI_KNOWLEDGE_API_TOKEN"]),
                *([] if api_port_configured else ["missing ZHENZHI_KNOWLEDGE_API_PORT"]),
            ],
            evidence=["GET /health route implemented", "POST /v0/metrics/report route implemented", "bearer auth rejection writes API command envelope"],
            next_action="Set API token and port, then run live HTTP API smoke from the target network.",
        ),
        _readiness_capability(
            "postgres_operational_store",
            "PostgreSQL operational store",
            database_ready and schema_ready,
            blockers=[
                *([] if database_ready else ["DATABASE_URL is required and must point to PostgreSQL"]),
                *([] if schema_ready else [f"postgres operational schema unavailable: {schema.get('error')}"]),
            ],
            evidence=["operational_events table", "api_command_envelopes table", "feishu_delivery_attempts table"],
            next_action="Provide staging PostgreSQL DSN and rerun readiness --migrate.",
        ),
        _readiness_capability(
            "migration",
            "Operational migration",
            schema_ready,
            blockers=[] if schema_ready else [f"migration not applied: {schema.get('error')}"],
            evidence=[OPERATIONAL_MIGRATION_VERSION, OPERATIONAL_MIGRATION_CHECKSUM],
            next_action="Run scripts/ops/postgres_live_ops.py migrate against staging PostgreSQL.",
        ),
        _readiness_capability(
            "rollback",
            "Rollback prerequisites",
            backup_ready and schema_ready,
            blockers=[*(backup.get("blockers") or []), *([] if schema_ready else ["migration must be applied before rollback rehearsal"])],
            evidence=["rollback command is guarded by --allow-destructive", "rollback target limited to cloned/restored base"],
            next_action="Record backup snapshot and pg_dump refs, then rehearse rollback only on a cloned/restored staging DB.",
        ),
        _readiness_capability(
            "health",
            "Health endpoint prerequisite",
            api_port_configured and schema_ready,
            blockers=[
                *([] if api_port_configured else ["missing ZHENZHI_KNOWLEDGE_API_PORT"]),
                *([] if schema_ready else ["operational store must be available for /health"]),
            ],
            evidence=["GET /health validates bundle and operational store"],
            next_action="Start API service and verify GET /health from staging network.",
        ),
        _readiness_capability(
            "metrics",
            "Metrics route prerequisite",
            env_present.get("ZHENZHI_KNOWLEDGE_API_TOKEN", False) and api_port_configured,
            blockers=[
                *([] if env_present.get("ZHENZHI_KNOWLEDGE_API_TOKEN") else ["missing ZHENZHI_KNOWLEDGE_API_TOKEN"]),
                *([] if api_port_configured else ["missing ZHENZHI_KNOWLEDGE_API_PORT"]),
            ],
            evidence=["POST /v0/metrics/report route implemented"],
            next_action="Run bearer-authenticated POST /v0/metrics/report smoke against live API.",
        ),
        _readiness_capability(
            "backup",
            "Backup prerequisites",
            backup_ready,
            blockers=backup.get("blockers") or [],
            evidence=["ZHENZHI_KNOWLEDGE_BACKUP_REF or PG_BACKUP_REF", "ZHENZHI_KNOWLEDGE_PG_DUMP_REF"],
            next_action="Create or attach staging backup snapshot and pg_dump evidence refs before live acceptance.",
        ),
    ]
    capability_blockers = [
        f"{item['label']}: {blocker}"
        for item in capabilities
        if not item["ok"]
        for blocker in item.get("blockers", [])
    ]
    all_blockers = _dedupe([*blockers, *capability_blockers])
    return {
        "status": "ready" if not all_blockers else "blocked",
        "generatedAt": utc_now(),
        "checks": checks,
        "capabilities": capabilities,
        "readableLabels": [{"name": item["name"], "label": item["label"], "status": "ready" if item["ok"] else "blocked"} for item in capabilities],
        "blockers": all_blockers,
    }


def write_readiness_artifact(bundle: Bundle, report: dict[str, Any]) -> str:
    directory = bundle.zz_dir / "evidence"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"feishu-api-postgres-readiness-{utc_now().replace(':', '').replace('-', '')}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path.relative_to(bundle.root))


def compact_error(exc: Exception) -> str:
    return compact_text(redact_sensitive_text(f"{type(exc).__name__}: {exc}"), 300)


def compact_text(value: str, limit: int = 500) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def redact_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urllib.parse.urlunparse((parsed.scheme, host, parsed.path, "", "", ""))


def redact_sensitive_text(value: str) -> str:
    text = str(value)
    for name in SECRET_ENV_NAMES:
        secret = os.environ.get(name, "").strip()
        if secret:
            text = text.replace(secret, f"<redacted:{name}>")
    for name in DATABASE_ENV_NAMES:
        dsn = os.environ.get(name, "").strip()
        if dsn:
            text = text.replace(dsn, redact_url(dsn))
            parsed = urllib.parse.urlparse(dsn)
            if parsed.password:
                text = text.replace(parsed.password, "<redacted:DATABASE_PASSWORD>")
    return text


def _readiness_capability(
    name: str,
    label: str,
    ok: bool,
    blockers: list[str],
    evidence: list[str],
    next_action: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "label": label,
        "ok": bool(ok),
        "blockers": _dedupe(blockers),
        "evidence": evidence,
        "nextAction": "" if ok else next_action,
    }


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        item = str(value).strip()
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _write(sql: str, params: tuple[Any, ...], table: str, object_id: str) -> dict[str, Any]:
    try:
        try_ensure_operational_schema("api")
        conn = connect_database()
        try:
            conn.execute(sql, params)
            conn.commit()
        finally:
            conn.close()
        return {"ok": True, "table": table, "id": object_id}
    except Exception as exc:
        if operational_strict():
            raise
        return {"ok": False, "table": table, "id": object_id, "error": compact_error(exc)}


def _check_env(checks: list[dict[str, Any]], blockers: list[str], name: str, secret: bool = False, safe_suffix: bool = False) -> None:
    value = os.environ.get(name, "").strip()
    item: dict[str, Any] = {"name": name, "ok": bool(value), "present": bool(value)}
    if safe_suffix and value:
        item["suffix"] = value[-6:]
    if secret and value:
        item["fingerprint"] = hashlib.sha256(value.encode("utf-8")).hexdigest()[:10]
    checks.append(item)
    if not value:
        blockers.append(f"missing {name}")


def _port_available(value: str) -> bool:
    try:
        port = int(value)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            return sock.connect_ex(("127.0.0.1", port)) != 0
    except Exception:
        return False


def _check_feishu_token_api() -> dict[str, Any]:
    app_id = os.environ.get("FEISHU_APP_ID", "").strip()
    app_secret = os.environ.get("FEISHU_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        return {"ok": False, "error": "missing Feishu app id or secret"}
    data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json; charset=utf-8"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return {"ok": False, "error": compact_error(exc)}
    return {"ok": body.get("code") == 0, "code": body.get("code"), "message": compact_text(str(body.get("msg") or ""))}
