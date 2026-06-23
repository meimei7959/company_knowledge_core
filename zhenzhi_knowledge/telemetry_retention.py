from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .core import Bundle, create_audit_log, ensure_dir, load_object, rel, render_doc, slug, unique_time_id, utc_now, write_text


CURRENT_STATE_EVENTS = {"heartbeat", "lease_update", "progress_update", "error_report"}
TIMELINE_EVENTS = {"lease_update", "progress_update", "tool_usage", "result_writeback", "error_report"}
METRIC_EVENTS = {"heartbeat", "tool_usage", "model_usage", "error_report"}
LEARNING_TRIGGERS = {"rejected", "rework", "quality_gate_failure", "boundary_violation", "manual_correction", "repeated_blocker"}
TERMINAL_STATUSES = {"done", "rejected", "cancelled", "waiting_acceptance"}
PROTECTED_EVENT_CLASSES = {"protected_core_ref", "protected_result_ref"}
SECRET_KEYS = {"token", "secret", "password", "passwd", "api_key", "apikey", "credential", "key"}


@dataclass(frozen=True)
class TelemetryRetentionConfig:
    now: datetime | None = None
    ephemeral_ttl_hours: int = 24
    hot_ttl_hours: int = 72
    max_timeline_entries: int = 50
    actor: str = "system.telemetry-retention"

    def clock(self) -> datetime:
        return self.now or datetime.now(timezone.utc)


def classify_telemetry_event(event: dict[str, Any]) -> dict[str, Any]:
    event_type = str(event.get("eventType") or event.get("type") or "").strip() or "progress_update"
    runner_id = str(event.get("runnerId") or "").strip()
    task_id = str(event.get("taskId") or "").strip()
    scope = str(event.get("scope") or ("task" if task_id else "runner" if runner_id else "global"))
    event_time = str(event.get("eventTime") or event.get("timestamp") or utc_now())
    source_ref = str(event.get("sourceRef") or "").strip()
    retention_class = _retention_class(event_type, event)
    protected_candidate = retention_class in PROTECTED_EVENT_CLASSES or bool(event.get("protectedCandidate"))
    routes = _routes_for(event_type, retention_class)
    normalized = {
        "eventId": str(event.get("eventId") or _stable_event_id(event_type, runner_id, task_id, event_time, event)),
        "eventType": event_type,
        "scope": scope,
        "runnerId": runner_id,
        "taskId": task_id,
        "retentionClass": retention_class,
        "protectedCandidate": protected_candidate,
        "sensitivity": str(event.get("sensitivity") or "internal"),
        "dedupeKey": str(event.get("dedupeKey") or _dedupe_key(event_type, runner_id, task_id, event)),
        "eventTime": event_time,
        "sourceRef": source_ref,
        "routes": routes,
        "payloadSafe": _redact(event),
    }
    if _is_learning_signal(event_type, event):
        normalized["retentionClass"] = "learning_signal"
        normalized["routes"] = sorted(set(routes + ["learning"]))
        normalized["learningReason"] = str(event.get("learningReason") or event.get("reason") or event_type)
    return normalized


def ingest_telemetry_event(bundle: Bundle, event: dict[str, Any], config: TelemetryRetentionConfig | None = None) -> dict[str, Any]:
    config = config or TelemetryRetentionConfig()
    normalized = classify_telemetry_event(event)
    store = _store_root(bundle)
    ensure_dir(_events_dir(bundle))
    event_path = _events_dir(bundle) / f"{slug(normalized['eventId'])}.json"
    _write_json(event_path, normalized)
    if "current_state" in normalized["routes"]:
        _upsert_current_state(bundle, normalized, config)
    if "timeline" in normalized["routes"]:
        _append_timeline(bundle, normalized, config)
    if "metrics" in normalized["routes"]:
        _update_hot_metrics(bundle, normalized)
    ensure_dir(store)
    return {"event": normalized, "eventRef": rel(event_path, bundle.root)}


class TelemetryRetentionWorker:
    def __init__(self, bundle: Bundle, config: TelemetryRetentionConfig | None = None):
        self.bundle = bundle
        self.config = config or TelemetryRetentionConfig()

    def dry_run(self) -> dict[str, Any]:
        return _retention_plan(self.bundle, self.config, "dry-run")

    def apply(self) -> dict[str, Any]:
        return apply_telemetry_retention(self.bundle, self.config)


def apply_telemetry_retention(bundle: Bundle, config: TelemetryRetentionConfig | None = None) -> dict[str, Any]:
    config = config or TelemetryRetentionConfig()
    plan = _retention_plan(bundle, config, "apply")
    batch_ref = _write_batch_manifest(bundle, plan)
    promotion_refs = _promote_learning_signals(bundle, plan, config)
    summary_refs = _compact_timelines(bundle, plan, config)
    rollup_ref = _write_metrics_rollup(bundle, plan, batch_ref, summary_refs, promotion_refs, config)
    deleted_refs = _delete_eligible_events(bundle, plan)
    report = {
        **plan,
        "mode": "apply",
        "batchRef": batch_ref,
        "deletedRefs": deleted_refs,
        "summaryRefs": summary_refs,
        "rollupRef": rollup_ref,
        "promotionRefs": promotion_refs,
    }
    report["auditRef"] = _write_batch_audit(bundle, report, config)
    return report


def _retention_plan(bundle: Bundle, config: TelemetryRetentionConfig, mode: str) -> dict[str, Any]:
    events = _load_events(bundle)
    protected_refs = _protected_ref_text(bundle)
    deletes: list[dict[str, str]] = []
    protected_skips: list[dict[str, str]] = []
    learning_candidates: list[dict[str, str]] = []
    for event_ref, event in events:
        reason = _protected_reason(event_ref, event, protected_refs)
        if reason:
            protected_skips.append({"eventRef": event_ref, "reason": reason})
            continue
        if event.get("retentionClass") == "learning_signal":
            learning_candidates.append({"eventRef": event_ref, "reason": str(event.get("learningReason") or "learning_signal")})
            protected_skips.append({"eventRef": event_ref, "reason": "learning_signal_requires_promotion"})
            continue
        delete_reason = _delete_reason(event, config)
        if delete_reason:
            deletes.append({"eventRef": event_ref, "reason": delete_reason})
    return _build_plan_report(bundle, config, mode, deletes, protected_skips, learning_candidates)


def _build_plan_report(
    bundle: Bundle,
    config: TelemetryRetentionConfig,
    mode: str,
    deletes: list[dict[str, str]],
    protected_skips: list[dict[str, str]],
    learning_candidates: list[dict[str, str]],
) -> dict[str, Any]:
    compact_tasks = _compact_task_candidates(bundle, config)
    counts = {
        "eventsScanned": len(_load_events(bundle)),
        "deleteCandidates": len(deletes),
        "protectedSkips": len(protected_skips),
        "learningCandidates": len(learning_candidates),
        "compactTasks": len(compact_tasks),
    }
    report = {
        "mode": mode,
        "generatedAt": config.clock().isoformat(),
        "counts": counts,
        "deleteCandidates": sorted(deletes, key=lambda item: item["eventRef"]),
        "protectedSkips": sorted(protected_skips, key=lambda item: (item["eventRef"], item["reason"])),
        "learningCandidates": sorted(learning_candidates, key=lambda item: item["eventRef"]),
        "compactTasks": sorted(compact_tasks),
        "rollup": {"willWriteMetricsReport": bool(counts["eventsScanned"] or compact_tasks)},
    }
    report["digest"] = _digest(report)
    return report


def _delete_reason(event: dict[str, Any], config: TelemetryRetentionConfig) -> str:
    retention_class = str(event.get("retentionClass") or "")
    age = config.clock() - _parse_time(str(event.get("eventTime") or ""))
    if retention_class == "ephemeral_state" and age >= timedelta(hours=config.ephemeral_ttl_hours):
        return "expired_ephemeral_state"
    if retention_class == "hot_task" and age >= timedelta(hours=config.hot_ttl_hours):
        return "expired_hot_task_after_compaction"
    return ""


def _compact_task_candidates(bundle: Bundle, config: TelemetryRetentionConfig) -> list[str]:
    candidates: list[str] = []
    for path in sorted(_timelines_dir(bundle).glob("*.json")):
        timeline = _read_json(path, {})
        task_id = str(timeline.get("taskId") or path.stem)
        if _task_terminal(bundle, task_id) or _timeline_expired(timeline, config):
            candidates.append(task_id)
    return candidates


def _write_batch_manifest(bundle: Bundle, plan: dict[str, Any]) -> str:
    batch_id = unique_time_id("telemetry-retention-batch")
    path = _batches_dir(bundle) / f"{batch_id}.json"
    ensure_dir(path.parent)
    _write_json(path, {"batchId": batch_id, "dryRunDigest": plan["digest"], "plan": plan})
    return rel(path, bundle.root)


def _promote_learning_signals(bundle: Bundle, plan: dict[str, Any], config: TelemetryRetentionConfig) -> list[str]:
    refs: list[str] = []
    for item in plan["learningCandidates"]:
        event_path = bundle.root / item["eventRef"]
        event = _read_json(event_path, {})
        refs.extend(_promote_learning_event(bundle, event, event_path, item["reason"], config.actor))
    return sorted(set(refs))


def _compact_timelines(bundle: Bundle, plan: dict[str, Any], config: TelemetryRetentionConfig) -> list[str]:
    refs: list[str] = []
    for task_id in plan["compactTasks"]:
        timeline_path = _timelines_dir(bundle) / f"{slug(task_id)}.json"
        timeline = _read_json(timeline_path, {})
        if not timeline:
            continue
        refs.append(_write_task_summary(bundle, timeline_path, timeline, task_id, config))
    return refs


def _write_task_summary(bundle: Bundle, timeline_path: Path, timeline: dict[str, Any], task_id: str, config: TelemetryRetentionConfig) -> str:
    summary_path = _summaries_dir(bundle) / f"{slug(task_id)}.json"
    ensure_dir(summary_path.parent)
    entries = list(timeline.get("entries") or [])
    summary = {
        "type": "TaskExecutionSummary",
        "taskId": task_id,
        "generatedAt": config.clock().isoformat(),
        "eventCount": len(entries),
        "phaseTrail": _unique([str(item.get("phase") or "") for item in entries if item.get("phase")]),
        "notableEvents": entries[-10:],
        "sourceTimelineRef": rel(timeline_path, bundle.root),
    }
    _write_json(summary_path, summary)
    _write_json(timeline_path, {**timeline, "entries": entries[-config.max_timeline_entries :], "compactedAt": summary["generatedAt"], "summaryRef": rel(summary_path, bundle.root)})
    return rel(summary_path, bundle.root)


def _write_metrics_rollup(bundle: Bundle, plan: dict[str, Any], batch_ref: str, summary_refs: list[str], promotion_refs: list[str], config: TelemetryRetentionConfig) -> str:
    report_id = unique_time_id("telemetry-retention-metrics")
    path = bundle.root / "knowledge" / "metrics" / f"{report_id}.md"
    frontmatter = _metrics_rollup_frontmatter(report_id, plan, batch_ref, config)
    body = "\n".join(
        ["## Summary", "", f"- batch: {batch_ref}", f"- summaries: {len(summary_refs)}", f"- promotions: {len(promotion_refs)}", f"- dryRunDigest: {plan['digest']}", ""]
    )
    ensure_dir(path.parent)
    write_text(path, render_doc(frontmatter, body))
    return rel(path, bundle.root)


def _metrics_rollup_frontmatter(report_id: str, plan: dict[str, Any], batch_ref: str, config: TelemetryRetentionConfig) -> dict[str, Any]:
    return {
        "type": "MetricsReport",
        "title": report_id,
        "description": "Execution telemetry retention cleanup rollup.",
        "timestamp": utc_now(),
        "reportId": report_id,
        "owner": config.actor,
        "status": "verified",
        "telemetryRetentionBatchRef": batch_ref,
        "eventsScanned": plan["counts"]["eventsScanned"],
        "deleteCandidates": plan["counts"]["deleteCandidates"],
        "protectedSkips": plan["counts"]["protectedSkips"],
        "learningCandidates": plan["counts"]["learningCandidates"],
        "compactTasks": plan["counts"]["compactTasks"],
    }


def _delete_eligible_events(bundle: Bundle, plan: dict[str, Any]) -> list[str]:
    deleted: list[str] = []
    for item in plan["deleteCandidates"]:
        path = bundle.root / item["eventRef"]
        if path.exists() and ".zhenzhi" in path.parts:
            path.unlink()
            deleted.append(item["eventRef"])
    return sorted(deleted)


def _write_batch_audit(bundle: Bundle, report: dict[str, Any], config: TelemetryRetentionConfig) -> str:
    details = json.dumps(_audit_details(report), ensure_ascii=False, sort_keys=True)
    audit = create_audit_log(
        bundle,
        config.actor,
        "telemetry.retention.apply",
        report["batchRef"],
        after=f"deleted={len(report['deletedRefs'])};protected={report['counts']['protectedSkips']}",
        policy_result="batch_summary",
        details=details,
    )
    return rel(audit, bundle.root)


def _audit_details(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "batchRef": report["batchRef"],
        "dryRunDigest": report["digest"],
        "counts": report["counts"],
        "deletedRefs": report["deletedRefs"],
        "protectedSkips": report["protectedSkips"],
        "summaryRefs": report["summaryRefs"],
        "rollupRef": report["rollupRef"],
        "promotionRefs": report["promotionRefs"],
    }


def _retention_class(event_type: str, event: dict[str, Any]) -> str:
    explicit = str(event.get("retentionClass") or "").strip()
    if explicit:
        return explicit
    if bool(event.get("protectedCandidate")):
        return "protected_core_ref"
    if event_type == "heartbeat":
        return "ephemeral_state"
    if event_type == "lease_update":
        return "hot_task" if str(event.get("leaseStatus") or event.get("status") or "active") == "active" else "closeout_summary"
    if event_type == "progress_update":
        return "hot_task"
    if event_type in {"tool_usage", "model_usage"}:
        return "diagnostic_metric"
    if event_type == "result_writeback":
        return "protected_result_ref"
    if event_type == "error_report":
        return "learning_signal" if _is_learning_signal(event_type, event) else "hot_task"
    return "hot_task"


def _routes_for(event_type: str, retention_class: str) -> list[str]:
    routes: list[str] = []
    if event_type in CURRENT_STATE_EVENTS:
        routes.append("current_state")
    if event_type in TIMELINE_EVENTS:
        routes.append("timeline")
    if event_type in METRIC_EVENTS or retention_class == "diagnostic_metric":
        routes.append("metrics")
    if retention_class in PROTECTED_EVENT_CLASSES:
        routes.append("protected")
    return sorted(set(routes))


def _is_learning_signal(event_type: str, event: dict[str, Any]) -> bool:
    if bool(event.get("learningSignal")):
        return True
    reason = str(event.get("learningReason") or event.get("reason") or event.get("errorClass") or "").lower()
    return event_type == "error_report" and any(trigger in reason for trigger in LEARNING_TRIGGERS)


def _upsert_current_state(bundle: Bundle, event: dict[str, Any], config: TelemetryRetentionConfig) -> None:
    path = _current_state_path(bundle)
    state = _read_json(path, {"states": {}})
    key = _state_key(event)
    existing = dict(state["states"].get(key) or {})
    state["states"][key] = {
        **existing,
        "key": key,
        "runnerId": event.get("runnerId", ""),
        "taskId": event.get("taskId", ""),
        "scope": event.get("scope", ""),
        "currentPhase": event["payloadSafe"].get("phase", existing.get("currentPhase", "")),
        "lastStep": event["payloadSafe"].get("step", event["payloadSafe"].get("message", existing.get("lastStep", ""))),
        "load": event["payloadSafe"].get("load", existing.get("load", "")),
        "lease": event["payloadSafe"].get("leaseStatus", event["payloadSafe"].get("status", existing.get("lease", ""))),
        "lastErrorSummary": event["payloadSafe"].get("errorSummary", existing.get("lastErrorSummary", "")),
        "lastEventRef": f"{rel(_events_dir(bundle), bundle.root)}/{slug(event['eventId'])}.json",
        "updatedAt": config.clock().isoformat(),
    }
    ensure_dir(path.parent)
    _write_json(path, state)


def _append_timeline(bundle: Bundle, event: dict[str, Any], config: TelemetryRetentionConfig) -> None:
    task_id = str(event.get("taskId") or "global")
    path = _timelines_dir(bundle) / f"{slug(task_id)}.json"
    timeline = _read_json(path, {"taskId": task_id, "entries": []})
    entry = {
        "eventRef": f"{rel(_events_dir(bundle), bundle.root)}/{slug(event['eventId'])}.json",
        "eventType": event["eventType"],
        "eventTime": event["eventTime"],
        "phase": event["payloadSafe"].get("phase", ""),
        "summary": event["payloadSafe"].get("message", event["payloadSafe"].get("errorSummary", "")),
        "retentionClass": event["retentionClass"],
    }
    entries = list(timeline.get("entries") or [])
    if not entries or entries[-1].get("eventType") != entry["eventType"] or entries[-1].get("summary") != entry["summary"]:
        entries.append(entry)
    timeline["entries"] = entries[-config.max_timeline_entries :]
    timeline["updatedAt"] = config.clock().isoformat()
    ensure_dir(path.parent)
    _write_json(path, timeline)


def _update_hot_metrics(bundle: Bundle, event: dict[str, Any]) -> None:
    path = _store_root(bundle) / "metrics-hot.json"
    metrics = _read_json(path, {"countsByEventType": {}, "countsByRetentionClass": {}, "toolUsage": {}, "modelUsage": {}})
    _increment(metrics["countsByEventType"], str(event["eventType"]))
    _increment(metrics["countsByRetentionClass"], str(event["retentionClass"]))
    if event["eventType"] == "tool_usage":
        _increment(metrics["toolUsage"], str(event["payloadSafe"].get("tool") or "unknown"))
    if event["eventType"] == "model_usage":
        _increment(metrics["modelUsage"], str(event["payloadSafe"].get("model") or "unknown"))
    ensure_dir(path.parent)
    _write_json(path, metrics)


def _promote_learning_event(bundle: Bundle, event: dict[str, Any], event_path: Path, reason: str, actor: str) -> list[str]:
    task_id = str(event.get("taskId") or "unknown-task")
    event_ref = rel(event_path, bundle.root)
    eval_id = unique_time_id(f"eval-telemetry-{slug(task_id)}")
    proposal_id = unique_time_id("agent-improvement")
    eval_path = bundle.root / "knowledge" / "evals" / f"{eval_id}.md"
    proposal_path = bundle.root / "knowledge" / "agent-improvements" / f"{proposal_id}.md"
    ensure_dir(eval_path.parent)
    ensure_dir(proposal_path.parent)
    eval_fm = {
        "type": "EvalCase",
        "title": f"Telemetry learning signal for {task_id}",
        "description": "Draft eval candidate promoted before telemetry cleanup.",
        "timestamp": utc_now(),
        "evalId": eval_id,
        "owner": actor,
        "status": "draft",
        "targetRef": event_ref,
        "taskId": task_id,
        "projectId": str(event.get("payloadSafe", {}).get("projectId") or ""),
        "expected": "Future execution should avoid the captured failure pattern.",
    }
    proposal_fm = {
        "type": "AgentImprovementProposal",
        "title": f"Telemetry improvement candidate for {task_id}",
        "description": "Draft improvement candidate promoted before telemetry cleanup.",
        "timestamp": utc_now(),
        "proposalId": proposal_id,
        "owner": actor,
        "status": "draft",
        "taskId": task_id,
        "resultRef": event_ref,
        "trigger": "telemetry_retention_learning_signal",
        "failureReasons": [reason],
        "evalCaseRefs": [rel(eval_path, bundle.root)],
    }
    write_text(eval_path, render_doc(eval_fm, f"## Source\n\n- telemetryRef: {event_ref}\n- reason: {reason}\n"))
    write_text(proposal_path, render_doc(proposal_fm, f"## Source\n\n- telemetryRef: {event_ref}\n- reason: {reason}\n"))
    return [rel(eval_path, bundle.root), rel(proposal_path, bundle.root)]


def _protected_ref_text(bundle: Bundle) -> str:
    roots = ["task-results", "knowledge", "projects", "runs", "sources", "reviews", "defects"]
    chunks: list[str] = []
    for root_name in roots:
        root = bundle.root / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            if ".zhenzhi" in path.parts:
                continue
            try:
                chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    return "\n".join(chunks)


def _protected_reason(event_ref: str, event: dict[str, Any], protected_text: str) -> str:
    if str(event.get("retentionClass") or "") in PROTECTED_EVENT_CLASSES:
        return "protected_retention_class"
    source_ref = str(event.get("sourceRef") or "")
    if event_ref and event_ref in protected_text:
        return "cited_by_protected_ref"
    if source_ref and source_ref in protected_text:
        return "source_ref_cited_by_protected_ref"
    return ""


def _task_terminal(bundle: Bundle, task_id: str) -> bool:
    for task_root in [bundle.root / "projects", bundle.root / "tasks"]:
        if not task_root.exists():
            continue
        for path in task_root.rglob("*.md"):
            try:
                fm = load_object(path)
            except Exception:
                continue
            if str(fm.get("taskId") or "") == task_id:
                return str(fm.get("status") or "") in TERMINAL_STATUSES
    return False


def _timeline_expired(timeline: dict[str, Any], config: TelemetryRetentionConfig) -> bool:
    updated = _parse_time(str(timeline.get("updatedAt") or ""))
    return config.clock() - updated >= timedelta(hours=config.hot_ttl_hours)


def _load_events(bundle: Bundle) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(_events_dir(bundle).glob("*.json")):
        event = _read_json(path, {})
        if event:
            rows.append((rel(path, bundle.root), event))
    return rows


def _store_root(bundle: Bundle) -> Path:
    return bundle.root / ".zhenzhi" / "telemetry"


def _events_dir(bundle: Bundle) -> Path:
    return _store_root(bundle) / "events"


def _timelines_dir(bundle: Bundle) -> Path:
    return _store_root(bundle) / "timelines"


def _summaries_dir(bundle: Bundle) -> Path:
    return _store_root(bundle) / "summaries"


def _batches_dir(bundle: Bundle) -> Path:
    return _store_root(bundle) / "batches"


def _current_state_path(bundle: Bundle) -> Path:
    return _store_root(bundle) / "current-state.json"


def _state_key(event: dict[str, Any]) -> str:
    return ":".join([str(event.get("scope") or "global"), str(event.get("runnerId") or ""), str(event.get("taskId") or "")])


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stable_event_id(event_type: str, runner_id: str, task_id: str, event_time: str, event: dict[str, Any]) -> str:
    return "telemetry-" + hashlib.sha256(json.dumps([event_type, runner_id, task_id, event_time, event], sort_keys=True, default=str).encode("utf-8")).hexdigest()[:20]


def _dedupe_key(event_type: str, runner_id: str, task_id: str, event: dict[str, Any]) -> str:
    phase = str(event.get("phase") or "")
    source_ref = str(event.get("sourceRef") or "")
    return "|".join([event_type, runner_id, task_id, phase, source_ref])


def _digest(payload: Any) -> str:
    clone = json.loads(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str))
    clone.pop("generatedAt", None)
    clone.pop("digest", None)
    return "sha256:" + hashlib.sha256(json.dumps(clone, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _parse_time(value: str) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower()
            result[key] = "[redacted]" if any(secret in normalized for secret in SECRET_KEYS) else _redact(item)
        return result
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _increment(mapping: dict[str, int], key: str) -> None:
    mapping[key] = int(mapping.get(key) or 0) + 1


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
