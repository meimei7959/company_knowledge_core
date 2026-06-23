from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from zhenzhi_knowledge.core import (
    Bundle,
    COLLECTION_NAMES,
    KnowledgeError,
    as_list,
    load_object,
    rel,
    slug,
)


SENSITIVE_FACT_KEY_PATTERN = re.compile(r"(token|password|secret|credential|api[_-]?key|leaseToken)", re.IGNORECASE)
SENSITIVE_FACT_VALUE_PATTERN = re.compile(r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9_-]{12,}|(?:token|secret|api[_-]?key)[_-][A-Za-z0-9][A-Za-z0-9_-]{5,})", re.IGNORECASE)


def _task_fact_roots(bundle: Bundle, project_id: str = "") -> list[Path]:
    roots = [bundle.root / "tasks"]
    if project_id:
        roots.insert(0, bundle.root / "projects" / slug(project_id) / "tasks")
    else:
        project_root = bundle.root / "projects"
        if project_root.exists():
            roots.extend(project_root.glob("*/tasks"))
    return roots


def _find_task_fact_path(bundle: Bundle, project_id: str, task_id: str) -> Path:
    wanted = slug(task_id)
    for root in _task_fact_roots(bundle, project_id):
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            task = load_object(path)
            if task.get("type") not in {"ProjectTask", "KnowledgeTask"}:
                continue
            if str(task.get("taskId") or path.stem) == task_id or slug(str(task.get("taskId") or path.stem)) == wanted:
                return path
    raise KnowledgeError(f"task not found: {task_id}")


def _load_ref_object(bundle: Bundle, object_ref: str) -> tuple[dict[str, Any] | None, str]:
    ref_value = str(object_ref or "").strip()
    if not ref_value:
        return None, ""
    candidates = [bundle.root / ref_value]
    if not ref_value.endswith(".md"):
        candidates.extend(
            [
                bundle.root / "task-results" / f"{slug(ref_value)}.md",
                bundle.root / "runners" / f"{slug(ref_value)}.md",
                bundle.root / "notifications" / f"{slug(ref_value)}.md",
                bundle.root / "knowledge" / "audit" / f"{slug(ref_value)}.md",
            ]
        )
    for path in candidates:
        if path.exists():
            obj = load_object(path)
            obj["path"] = rel(path, bundle.root)
            return obj, rel(path, bundle.root)
    return None, ref_value


def _redact_fact_value(key: str, value: Any) -> tuple[Any, bool]:
    if value is None or value == "" or value == [] or value == {}:
        return value, False
    if SENSITIVE_FACT_KEY_PATTERN.search(str(key)):
        if isinstance(value, list):
            return ["[redacted]"] if value else [], bool(value)
        if isinstance(value, dict):
            return {"redacted": True}, True
        return "[redacted]", True
    if isinstance(value, str) and SENSITIVE_FACT_VALUE_PATTERN.search(value):
        return "[redacted]", True
    if isinstance(value, list):
        redacted_items: list[Any] = []
        redacted_any = False
        for item in value:
            redacted_item, item_redacted = _redact_fact_value(key, item)
            redacted_items.append(redacted_item)
            redacted_any = redacted_any or item_redacted
        return redacted_items, redacted_any
    if isinstance(value, dict):
        redacted_dict: dict[str, Any] = {}
        redacted_any = False
        for item_key, item_value in value.items():
            redacted_item, item_redacted = _redact_fact_value(str(item_key), item_value)
            redacted_dict[str(item_key)] = redacted_item
            redacted_any = redacted_any or item_redacted
        return redacted_dict, redacted_any
    return value, False


def _redacted_fields(source: dict[str, Any], keys: list[str]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    fields: dict[str, Any] = {}
    redactions: list[dict[str, str]] = []
    for key in keys:
        value, redacted = _redact_fact_value(key, source.get(key))
        fields[key] = value
        if redacted:
            redactions.append({"field": key, "reason": "sensitive fact redacted"})
    return fields, redactions


def _task_fact_gap(gap_type: str, field: str, message: str, reason: str = "") -> dict[str, str]:
    gap = {"type": gap_type, "field": field, "message": message}
    if reason:
        gap["reason"] = reason
    return gap


def _task_fact_has_v1_fields(task: dict[str, Any], result: dict[str, Any] | None) -> bool:
    v1_task_fields = [
        "agentTeamCapabilityVersionRef",
        "requiredAgentTeamCapabilityVersionRef",
        "capabilityVersionRef",
        "pmAgentId",
        "projectManagerAgent",
        "controllerAgent",
        "workerTaskRefs",
        "childTaskRefs",
        "workerResultRefs",
        "parentTaskId",
        "parentTaskRef",
        "workerRole",
        "growthSignalRequired",
        "agentImprovementProposalRefs",
        "improvementProposalRefs",
        "growthSignalRefs",
        "evalCaseRefs",
        "multiComputerExecutionMode",
        "sameProjectMultiComputerExecution",
    ]
    v1_result_fields = [
        "agentImprovementProposalRefs",
        "improvementProposalRefs",
        "growthSignalRefs",
        "evalCaseRefs",
        "qualitySignals",
        "workerResultRefs",
        "consolidatedWorkerResultRefs",
    ]
    return any(task.get(field) not in (None, "", [], {}) for field in v1_task_fields) or any((result or {}).get(field) not in (None, "", [], {}) for field in v1_result_fields)


def _task_fact_ref_summary(bundle: Bundle, object_ref: str, keys: list[str]) -> tuple[dict[str, Any], list[dict[str, str]], str]:
    obj, path = _load_ref_object(bundle, object_ref)
    if obj is None:
        return {"ref": object_ref, "path": path, "found": False}, [], ""
    fields, redactions = _redacted_fields(obj, keys)
    fields["ref"] = object_ref
    fields["path"] = path
    fields["found"] = True
    fields["type"] = obj.get("type")
    return fields, redactions, path


def _load_task_fact_task_ref(bundle: Bundle, project_id: str, task_ref: str) -> tuple[dict[str, Any] | None, str]:
    ref_value = str(task_ref or "").strip()
    if not ref_value:
        return None, ""
    direct = bundle.root / ref_value
    if direct.exists():
        obj = load_object(direct)
        obj["path"] = rel(direct, bundle.root)
        return obj, rel(direct, bundle.root)
    try:
        path = _find_task_fact_path(bundle, project_id, ref_value)
    except KnowledgeError:
        return None, ref_value
    obj = load_object(path)
    obj["path"] = rel(path, bundle.root)
    return obj, rel(path, bundle.root)


def _find_child_task_fact_refs(bundle: Bundle, project_id: str, parent_task_id: str, parent_task_ref: str) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for root in _task_fact_roots(bundle, project_id):
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            task = load_object(path)
            if task.get("type") not in {"ProjectTask", "KnowledgeTask"}:
                continue
            if str(task.get("parentTaskId") or "") != parent_task_id and str(task.get("parentTaskRef") or "") != parent_task_ref:
                continue
            ref = rel(path, bundle.root)
            if ref not in seen:
                refs.append(ref)
                seen.add(ref)
    return refs


def _task_fact_growth_refs(task: dict[str, Any], result: dict[str, Any] | None) -> tuple[list[Any], list[Any]]:
    proposal_refs: list[Any] = []
    eval_case_refs: list[Any] = []
    for source in [task, result or {}]:
        for key in ["agentImprovementProposalRefs", "improvementProposalRefs", "growthSignalRefs"]:
            proposal_refs.extend(as_list(source.get(key)))
        eval_case_refs.extend(as_list(source.get("evalCaseRefs")))
    return proposal_refs, eval_case_refs


def _quality_requires_growth_signal(task: dict[str, Any], result: dict[str, Any] | None) -> bool:
    if bool(task.get("growthSignalRequired")):
        return True
    if not result:
        return False
    quality = result.get("qualityEvaluation")
    if isinstance(quality, dict) and quality.get("passed") is False:
        return True
    status = str(result.get("status") or result.get("result") or "")
    if status in {"blocked", "rejected", "failed", "needs_rework", "rework"}:
        return True
    signals = as_list(result.get("qualitySignals"))
    return any(str(signal).lower() in {"failed_quality", "rework", "manual_correction", "repeated_blocker", "role_boundary_violation"} for signal in signals)


def _task_fact_status(task: dict[str, Any], result: dict[str, Any] | None) -> dict[str, str]:
    raw = str(task.get("status") or "unknown")
    labels = {
        "pending": ("任务已创建，还没进入执行。", "补条件、分配 Runner 或人工确认。"),
        "waiting_runner": ("任务正在等待可用 Runner。", "展示缺少能力、权限、在线 Runner、租约或匹配条件。"),
        "processing": ("Runner 或 Agent 正在执行。", "展示 executorAgent、runner/host、当前阶段和最近心跳。"),
        "blocked": ("任务无法继续。", "展示阻塞原因、owner 和恢复动作。"),
        "waiting_acceptance": ("任务已有结果，等待验收。", "展示 acceptanceOwner、resultRef、验收标准和 evidenceRefs。"),
        "done": ("任务完成。", "展示 resultRef、证据、验收记录和完成时间；缺证据时标记缺口。"),
        "failed": ("执行失败。", "展示失败原因、是否可重试、下一责任人和相关审计。"),
        "cancelled": ("任务已取消。", "展示取消原因、取消人和审计记录。"),
    }
    explanation, next_step = labels.get(raw, ("状态无法识别。", "展示 raw status、来源对象和数据修复建议。"))
    next_owner = str(task.get("assignee") or task.get("executorAgent") or task.get("requester") or "")
    if raw == "waiting_acceptance" and result:
        policy = result.get("acceptancePolicy") if isinstance(result.get("acceptancePolicy"), dict) else {}
        next_owner = str(policy.get("acceptanceOwner") or policy.get("reviewer") or policy.get("projectManager") or policy.get("humanReviewer") or task.get("requester") or next_owner)
    return {"raw": raw, "explanation": explanation, "nextStep": next_step, "nextStepOwner": next_owner or "unknown"}


def _load_task_and_result(
    bundle: Bundle,
    project_id: str,
    task_id: str,
) -> tuple[Path, dict[str, Any], dict[str, Any] | None, str, str, list[str]]:
    task_path = _find_task_fact_path(bundle, project_id, task_id)
    task = load_object(task_path)
    task["path"] = rel(task_path, bundle.root)
    result: dict[str, Any] | None = None
    result_ref = str(task.get("resultRef") or "")
    result_path = ""
    dangling_refs: list[str] = []
    if result_ref:
        result, result_path = _load_ref_object(bundle, result_ref)
        if result is None:
            dangling_refs.append(result_ref)
    return task_path, task, result, result_ref, result_path, dangling_refs


def _build_result_fields(
    result: dict[str, Any] | None,
    result_ref: str,
    result_path: str,
    redactions: list[dict[str, str]],
) -> dict[str, Any]:
    result_fields: dict[str, Any] = {"resultRef": result_ref}
    if not result:
        return result_fields
    result_fields, result_redactions = _redacted_fields(
        result,
        [
            "resultId",
            "status",
            "summary",
            "outputRefs",
            "evidenceRefs",
            "testsOrChecks",
            "qualityEvaluation",
            "commonRulesEvaluation",
            "operatingRuleRefs",
            "acceptancePolicy",
            "completedAt",
            "workerResultRefs",
            "consolidatedWorkerResultRefs",
            "agentImprovementProposalRefs",
            "improvementProposalRefs",
            "growthSignalRefs",
            "evalCaseRefs",
            "qualitySignals",
        ],
    )
    result_fields["resultRef"] = result_ref
    result_fields["path"] = result_path
    redactions.extend(result_redactions)
    return result_fields


def _append_base_gaps(
    task: dict[str, Any],
    result: dict[str, Any] | None,
    result_ref: str,
    gaps: list[dict[str, str]],
) -> None:
    task_age_gap = "legacy gap" if not task.get("updatedAt") else "current gap"
    task_status = str(task.get("status") or "")
    if task.get("workSourceType") == "feature" and not as_list(task.get("requirementRefs")):
        gaps.append(_task_fact_gap(task_age_gap, "requirementRefs", "feature task lacks requirementRefs"))
    if task_status in {"done", "waiting_acceptance"} and not result_ref:
        gaps.append(_task_fact_gap("current gap", "resultRef", "task status requires a visible TaskResult"))
    if result_ref and result is None:
        gaps.append(_task_fact_gap("dangling ref", "resultRef", result_ref))
    if task_status == "done" and not as_list((result or {}).get("evidenceRefs")):
        gaps.append(_task_fact_gap("current gap", "evidenceRefs", "done task lacks visible evidenceRefs"))
    if task_status == "done" and result and not as_list((result or {}).get("testsOrChecks")):
        gaps.append(_task_fact_gap("current gap", "testsOrChecks", "done task lacks testsOrChecks"))
    if result and not result.get("qualityEvaluation"):
        gaps.append(_task_fact_gap(task_age_gap, "qualityEvaluation", "TaskResult lacks qualityEvaluation"))
    if result and not result.get("commonRulesEvaluation"):
        gaps.append(_task_fact_gap(task_age_gap, "commonRulesEvaluation", "TaskResult lacks commonRulesEvaluation"))
    if task_status == "waiting_runner" and not (task.get("runnerRequirementReason") or task.get("blockerReason") or task.get("blockedReason") or task.get("sourceReason")):
        gaps.append(_task_fact_gap("current gap", "waitingRunnerReason", "waiting_runner lacks runner wait reason"))
    if task_status == "waiting_acceptance":
        policy = result.get("acceptancePolicy") if result and isinstance(result.get("acceptancePolicy"), dict) else {}
        if not (policy.get("acceptanceOwner") or policy.get("reviewer") or policy.get("projectManager") or policy.get("humanReviewer") or task.get("acceptanceOwner")):
            gaps.append(_task_fact_gap("current gap", "acceptanceOwner", "waiting_acceptance lacks acceptance owner"))
    if result and task_status == "done" and str(result.get("status") or result.get("result") or "") in {"blocked", "rejected", "failed"}:
        gaps.append(_task_fact_gap("status/result mismatch", "status", "task status conflicts with TaskResult status"))


def _build_receiver_review_block(
    bundle: Bundle,
    task: dict[str, Any],
    schema_version: str,
    redactions: list[dict[str, str]],
    source_refs: list[str],
    dangling_refs: list[str],
    gaps: list[dict[str, str]],
) -> dict[str, Any]:
    receiver_review_refs = as_list(task.get("receiverReviewRefs"))
    receiver_reviews: list[dict[str, Any]] = []
    for review_ref in receiver_review_refs:
        review, review_redactions, review_path = _task_fact_ref_summary(bundle, str(review_ref), ["reviewId", "status", "decision", "receiverAgent", "reviewerAgent", "artifactRefs", "issues", "assumptions", "timestamp"])
        receiver_reviews.append(review)
        redactions.extend(review_redactions)
        if review_path:
            source_refs.append(review_path)
        if not review.get("found"):
            dangling_refs.append(str(review_ref))
    if schema_version == "task-fact-view.v1" and not receiver_review_refs:
        gaps.append(_task_fact_gap("receiver review gap", "receiverReviewRefs", "V1 task lacks ReceiverReview refs", "missing_receiver_review"))
    return {
        "refs": receiver_review_refs,
        "reviews": receiver_reviews,
        "latestDecision": str(receiver_reviews[-1].get("decision") or receiver_reviews[-1].get("status") or "") if receiver_reviews else "",
    }


def _resolve_worker_task_refs(bundle: Bundle, task: dict[str, Any], project_id_value: str, task_id: str, task_ref: str) -> list[str]:
    worker_task_refs = as_list(task.get("workerTaskRefs")) + as_list(task.get("childTaskRefs"))
    if worker_task_refs:
        return worker_task_refs
    return _find_child_task_fact_refs(bundle, project_id_value, str(task.get("taskId") or task_id), task_ref)


def _build_worker_entry(
    bundle: Bundle,
    project_id_value: str,
    worker_ref: str,
    redactions: list[dict[str, str]],
    source_refs: list[str],
    dangling_refs: list[str],
    gaps: list[dict[str, str]],
    worker_result_refs: list[str],
) -> dict[str, Any]:
    worker_task, worker_path = _load_task_fact_task_ref(bundle, project_id_value, str(worker_ref))
    if worker_task is None:
        dangling_refs.append(str(worker_ref))
        gaps.append(_task_fact_gap("worker trace gap", "workerTaskRefs", f"worker task ref not found: {worker_ref}", "missing_worker_review"))
        return {"taskRef": str(worker_ref), "found": False}
    source_refs.append(worker_path)
    worker_identity, worker_redactions = _redacted_fields(worker_task, ["taskId", "title", "assignee", "workerRole", "status", "workSourceType", "receiverReviewRefs", "resultRef"])
    redactions.extend(worker_redactions)
    worker_result_ref = str(worker_task.get("resultRef") or "")
    worker_result: dict[str, Any] | None = None
    if worker_result_ref:
        worker_result, worker_result_path = _load_ref_object(bundle, worker_result_ref)
        if worker_result is None:
            dangling_refs.append(worker_result_ref)
            gaps.append(_task_fact_gap("worker trace gap", "worker.resultRef", f"worker TaskResult ref not found: {worker_result_ref}", "missing_worker_result"))
        else:
            source_refs.append(worker_result_path)
            worker_result_refs.append(worker_result_ref)
    if not as_list(worker_task.get("receiverReviewRefs")):
        gaps.append(_task_fact_gap("worker trace gap", "worker.receiverReviewRefs", f"worker task lacks ReceiverReview refs: {worker_identity.get('taskId')}", "missing_worker_review"))
    if not worker_result_ref:
        gaps.append(_task_fact_gap("worker trace gap", "worker.resultRef", f"worker task lacks TaskResult ref: {worker_identity.get('taskId')}", "missing_worker_result"))
    if worker_result and not as_list(worker_result.get("evidenceRefs")):
        gaps.append(_task_fact_gap("result evidence gap", "worker.evidenceRefs", f"worker TaskResult lacks evidenceRefs: {worker_result_ref}", "missing_worker_result"))
    return {
        "taskRef": worker_path,
        "found": True,
        "task": worker_identity,
        "resultRef": worker_result_ref,
        "resultStatus": str((worker_result or {}).get("status") or ""),
        "evidenceRefs": as_list((worker_result or {}).get("evidenceRefs")),
        "outputRefs": as_list((worker_result or {}).get("outputRefs")),
        "receiverReviewRefs": as_list(worker_task.get("receiverReviewRefs")),
    }


def _build_worker_participation(
    bundle: Bundle,
    task: dict[str, Any],
    result: dict[str, Any] | None,
    project_id_value: str,
    task_id: str,
    task_ref: str,
    schema_version: str,
    redactions: list[dict[str, str]],
    source_refs: list[str],
    dangling_refs: list[str],
    gaps: list[dict[str, str]],
) -> dict[str, Any]:
    parent_task_ref = str(task.get("parentTaskRef") or task.get("parentTaskId") or "")
    worker_task_refs = _resolve_worker_task_refs(bundle, task, project_id_value, task_id, task_ref)
    worker_result_refs = as_list((result or {}).get("workerResultRefs")) + as_list((result or {}).get("consolidatedWorkerResultRefs")) + as_list(task.get("workerResultRefs"))
    workers = [_build_worker_entry(bundle, project_id_value, str(worker_ref), redactions, source_refs, dangling_refs, gaps, worker_result_refs) for worker_ref in worker_task_refs]
    if schema_version == "task-fact-view.v1" and (task.get("pmAgentId") or task.get("projectManagerAgent") or task.get("controllerAgent")) and not worker_task_refs:
        gaps.append(_task_fact_gap("worker trace gap", "workerTaskRefs", "PM-controlled V1 task lacks worker task refs", "missing_worker_review"))
    if schema_version == "task-fact-view.v1" and not (task.get("pmAgentId") or task.get("projectManagerAgent") or task.get("controllerAgent") or parent_task_ref):
        gaps.append(_task_fact_gap("worker trace gap", "pmAgentId", "V1 task lacks PM controller or parent task link", "missing_pm_controller"))
    return {
        "pmController": str(task.get("pmAgentId") or task.get("projectManagerAgent") or task.get("controllerAgent") or ""),
        "parentTaskRef": parent_task_ref,
        "workerTaskRefs": worker_task_refs,
        "workers": workers,
        "consolidationRefs": worker_result_refs,
    }


def _build_growth_signals(
    task: dict[str, Any],
    result: dict[str, Any] | None,
    result_fields: dict[str, Any],
    schema_version: str,
    gaps: list[dict[str, str]],
) -> dict[str, Any]:
    proposal_refs, eval_case_refs = _task_fact_growth_refs(task, result)
    growth_requires_signal = _quality_requires_growth_signal(task, result)
    if schema_version == "task-fact-view.v1" and growth_requires_signal and not (proposal_refs or eval_case_refs):
        gaps.append(_task_fact_gap("learning loop gap", "growthSignals", "quality or blocker signal lacks draft AgentImprovementProposal/EvalCase refs", "growth_signal_gap"))
    return {
        "signalRequired": growth_requires_signal,
        "proposalRefs": proposal_refs,
        "evalCaseRefs": eval_case_refs,
        "qualityEvaluation": result_fields.get("qualityEvaluation", {}),
        "qualitySignals": as_list((result or {}).get("qualitySignals")),
    }


def _build_audit_notification(
    bundle: Bundle,
    task: dict[str, Any],
    schema_version: str,
    redactions: list[dict[str, str]],
    source_refs: list[str],
    gaps: list[dict[str, str]],
) -> dict[str, Any]:
    audit_refs = as_list(task.get("auditRefs"))
    notification_refs = as_list(task.get("notificationRefs"))
    audit_records: list[dict[str, Any]] = []
    notification_records: list[dict[str, Any]] = []
    for audit_ref in audit_refs:
        audit_record, audit_redactions, audit_path = _task_fact_ref_summary(bundle, str(audit_ref), ["action", "actor", "targetRef", "summary", "timestamp"])
        audit_records.append(audit_record)
        redactions.extend(audit_redactions)
        if audit_path:
            source_refs.append(audit_path)
    for notification_ref in notification_refs:
        notification_record, notification_redactions, notification_path = _task_fact_ref_summary(bundle, str(notification_ref), ["notificationId", "status", "channel", "recipient", "targetRef", "summary", "timestamp"])
        notification_records.append(notification_record)
        redactions.extend(notification_redactions)
        if notification_path:
            source_refs.append(notification_path)
    if schema_version == "task-fact-view.v1" and not audit_refs:
        gaps.append(_task_fact_gap("audit gap", "auditRefs", "V1 task lacks audit refs", "missing_audit"))
    return {
        "auditRefs": audit_refs,
        "auditRecords": audit_records,
        "notificationRefs": notification_refs,
        "notificationRecords": notification_records,
    }


def _build_capability_version(
    bundle: Bundle,
    task: dict[str, Any],
    result: dict[str, Any] | None,
    schema_version: str,
    source_refs: list[str],
    dangling_refs: list[str],
    gaps: list[dict[str, str]],
) -> dict[str, Any]:
    required_capability = str(task.get("agentTeamCapabilityVersionRef") or task.get("requiredAgentTeamCapabilityVersionRef") or task.get("capabilityVersionRef") or "")
    runner_ref = str(task.get("assignedRunner") or task.get("runnerId") or (result or {}).get("runner") or "")
    runner_record: dict[str, Any] | None = None
    if runner_ref:
        runner_record, runner_path = _load_ref_object(bundle, runner_ref)
        if runner_record is None:
            dangling_refs.append(runner_ref)
        elif runner_path:
            source_refs.append(runner_path)
    runner_capability = str((runner_record or {}).get("agentTeamCapabilityVersionRef") or (runner_record or {}).get("capabilityVersionRef") or "")
    capability_match = bool(required_capability and runner_capability and required_capability == runner_capability)
    execution_mode = str(task.get("multiComputerExecutionMode") or "")
    same_project_multi_computer = bool(task.get("sameProjectMultiComputerExecution")) or execution_mode in {"same_project_coexecution", "same_project_racing", "coexecution", "racing"}
    if schema_version == "task-fact-view.v1":
        if same_project_multi_computer:
            gaps.append(_task_fact_gap("capability version gap", "multiComputerExecutionMode", "same-project multi-computer execution is unsupported in V1", "unsupported_multi_computer_project_execution"))
        if not required_capability:
            gaps.append(_task_fact_gap("capability version gap", "agentTeamCapabilityVersionRef", "V1 task lacks required capability version ref", "capability_version_mismatch"))
        elif not runner_capability:
            gaps.append(_task_fact_gap("capability version gap", "runnerCapabilityVersionRef", "runner lacks capability version ref", "capability_version_mismatch"))
        elif required_capability != runner_capability:
            gaps.append(_task_fact_gap("capability version gap", "agentTeamCapabilityVersionRef", "required and runner capability versions differ", "capability_version_mismatch"))
    return {
        "requiredRef": required_capability,
        "runnerRef": runner_ref,
        "runnerCapabilityVersionRef": runner_capability,
        "match": capability_match if required_capability or runner_capability else None,
        "projectIsolation": "single_project_execution" if not same_project_multi_computer else "unsupported_same_project_multi_computer_execution",
    }


def _build_facts(
    schema_version: str,
    identity: dict[str, Any],
    source_fields: dict[str, Any],
    status: dict[str, str],
    execution: dict[str, Any],
    result_fields: dict[str, Any],
    task: dict[str, Any],
    result: dict[str, Any] | None,
    v1_blocks: dict[str, Any],
) -> dict[str, Any]:
    audit_refs = as_list(task.get("auditRefs"))
    notification_refs = as_list(task.get("notificationRefs"))
    facts = {
        "identity": identity,
        "source": source_fields,
        "status": status,
        "execution": execution,
        "result": result_fields,
        "auditRefs": audit_refs,
        "notificationRefs": notification_refs,
    }
    if schema_version != "task-fact-view.v1":
        return facts
    acceptance_policy = result.get("acceptancePolicy") if result and isinstance(result.get("acceptancePolicy"), dict) else {}
    facts.update(v1_blocks)
    facts["resultEvidence"] = result_fields
    facts["acceptance"] = {
        "policy": result_fields.get("acceptancePolicy", {}),
        "acceptanceOwner": str(acceptance_policy.get("acceptanceOwner") or acceptance_policy.get("reviewer") or acceptance_policy.get("projectManager") or acceptance_policy.get("humanReviewer") or task.get("acceptanceOwner") or ""),
        "criteriaRefs": source_fields.get("acceptanceCriteriaRefs", []),
    }
    return facts


def build_task_fact_view(bundle: Bundle, project_id: str, task_id: str) -> dict[str, Any]:
    task_path, task, result, result_ref, result_path, dangling_refs = _load_task_and_result(bundle, project_id, task_id)
    project_id_value = str(task.get("projectId") or project_id or "")
    identity, redactions = _redacted_fields(task, ["taskId", "title", "projectId", "workSourceType", "priority", "status", "timestamp", "createdAt", "updatedAt"])
    source_fields, source_redactions = _redacted_fields(task, ["requirementRefs", "requirementObjectRefs", "acceptanceCriteriaRefs", "sourceMaterialRefs", "receiverReviewRefs", "sourceReason"])
    execution, execution_redactions = _redacted_fields(task, ["assignee", "executorAgent", "assignedRunner", "runnerId", "leaseOwner", "leaseTokenHash", "leaseIssuedAt", "leaseExpiresAt", "leaseHeartbeatAt", "heartbeatAt", "executionPhase"])
    redactions.extend(source_redactions)
    redactions.extend(execution_redactions)
    result_fields = _build_result_fields(result, result_ref, result_path, redactions)
    gaps: list[dict[str, str]] = []
    _append_base_gaps(task, result, result_ref, gaps)
    status = _task_fact_status(task, result)
    task_ref = rel(task_path, bundle.root)
    source_refs = [task_ref, *([result_path] if result_path else [])]
    schema_version = "task-fact-view.v1" if _task_fact_has_v1_fields(task, result) else "task-fact-view.v0"
    receiver_review_block = _build_receiver_review_block(bundle, task, schema_version, redactions, source_refs, dangling_refs, gaps)
    worker_participation = _build_worker_participation(bundle, task, result, project_id_value, task_id, task_ref, schema_version, redactions, source_refs, dangling_refs, gaps)
    growth_signals = _build_growth_signals(task, result, result_fields, schema_version, gaps)
    audit_notification = _build_audit_notification(bundle, task, schema_version, redactions, source_refs, gaps)
    capability_version = _build_capability_version(bundle, task, result, schema_version, source_refs, dangling_refs, gaps)
    facts = _build_facts(
        schema_version,
        identity,
        source_fields,
        status,
        execution,
        result_fields,
        task,
        result,
        {
            "receiverReview": receiver_review_block,
            "workerParticipation": worker_participation,
            "growthSignals": growth_signals,
            "auditNotification": audit_notification,
            "capabilityVersion": capability_version,
        },
    )
    return {
        "apiVersion": "v0.1",
        "kind": "TaskFactView",
        "schemaVersion": schema_version,
        "sourceOfTruth": "existing-records",
        "readOnly": True,
        "projectId": project_id_value,
        "taskId": str(task.get("taskId") or task_id),
        "taskRef": task_ref,
        "facts": facts,
        "statusExplanation": status,
        "gaps": gaps,
        "redactions": redactions,
        "danglingRefs": dangling_refs,
        "sourceRefs": list(dict.fromkeys(source_refs)),
    }
