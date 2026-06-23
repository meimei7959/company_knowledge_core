from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .core import (
    Bundle,
    KnowledgeError,
    PMControlLeaseError,
    accept_project_task_result,
    acquire_pm_control_lease,
    cancel_project_task,
    claim_project_task,
    create_agent_capability_report,
    build_task_fact_view,
    create_metrics_report,
    create_bugfix_task,
    create_defect,
    create_discussion_session,
    create_project_task,
    create_receiver_review,
    create_source_material,
    api_error_response,
    disable_governed_asset,
    discussion_session_status,
    export_api_snapshot,
    export_graph_snapshot,
    finish_project_task,
    finalize_discussion_session,
    gateway_context,
    graph_impact,
    heartbeat_agent_runner,
    heartbeat_pm_control_lease,
    heartbeat_project_task_lease,
    manual_handoff_project_task,
    ensure_database_schema,
    invoke_tool,
    list_notifications,
    list_project_tasks,
    load_object,
    mark_notification_delivery,
    mark_access_credential_ready,
    apply_knowledge_review_result,
    normalize_command_envelope,
    publish_knowledge_bundle,
    project_task_context_payload,
    project_task_status,
    pm_control_lease_read_model,
    register_agent_runner,
    create_runner_invitation,
    create_tool_registration_request,
    create_workbench_project,
    register_workbench_tool,
    retry_project_task,
    release_pm_control_lease,
    runner_registry_for_workbench,
    requirement_tree_workbench_read_model,
    review_path,
    search_audit_logs,
    search_retrieval,
    search_index,
    scheduler_workbench_read_model,
    submit_discussion_turn,
    takeover_pm_control_lease,
    validate_bundle,
    stable_error_code,
    submit_runner_registration,
    workbench_project_execution_read_model,
)
from .feishu import handle_feishu_event, run_knowledge_query, update_knowledge_query_log_delivery
from .operational_store import ensure_operational_schema, operational_store_status, record_api_command_envelope


class KnowledgeHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], bundle: Bundle, api_token: str = ""):
        ensure_database_schema()
        ensure_operational_schema("api-server-start")
        self.bundle = bundle
        self.api_token = api_token
        super().__init__(server_address, KnowledgeHandler)


class KnowledgeHandler(BaseHTTPRequestHandler):
    server: KnowledgeHTTPServer

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, status: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)
        self.close_connection = True

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _authorized(self) -> bool:
        token = self.server.api_token
        if not token:
            return True
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return False
        supplied = header.removeprefix("Bearer ").strip()
        return hmac.compare_digest(supplied, token)

    def _reject_unauthorized(self) -> None:
        record_api_command_envelope(self.path, {}, "rejected", permission_decision="denied")
        self._json(
            401,
            api_error_response(
                "UNAUTHORIZED",
                "Unauthorized request.",
                blocker_reason="missing_or_invalid_api_token",
                next_action="Use a valid Bearer token for this API profile.",
            ),
        )

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                problems = validate_bundle(self.server.bundle)
                try:
                    operational = operational_store_status()
                except Exception as exc:
                    operational = {"ok": False, "error": str(exc)}
                    problems = [*problems, f"operational store unavailable: {exc}"]
                self._json(200 if not problems else 500, {"ok": not problems, "problems": problems, "operationalStore": operational})
            elif not self._authorized():
                self._reject_unauthorized()
            elif parsed.path == "/v0/snapshot":
                self._json(200, export_api_snapshot(self.server.bundle))
            elif parsed.path == "/v0/objects":
                query = parse_qs(parsed.query)
                filters = {
                    "type": first(query, "type"),
                    "status": first(query, "status"),
                    "projectId": first(query, "projectId"),
                    "agentId": first(query, "agentId"),
                    "toolId": first(query, "toolId"),
                    "riskLevel": first(query, "riskLevel"),
                    "text": first(query, "text"),
                }
                self._json(200, {"apiVersion": "v0.1", "kind": "ObjectList", "objects": search_index(self.server.bundle, filters)})
            elif parsed.path == "/v0/rag/search":
                query = parse_qs(parsed.query)
                rows = search_retrieval(
                    self.server.bundle,
                    first(query, "query"),
                    project_id=first(query, "projectId"),
                    scopes=query.get("scope") or [],
                    limit=int(first(query, "limit") or "5"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "RetrievalResult", "chunks": rows})
            elif parsed.path == "/v0/audit":
                query = parse_qs(parsed.query)
                rows = search_audit_logs(
                    self.server.bundle,
                    project_id=first(query, "projectId"),
                    agent_id=first(query, "agentId"),
                    tool_id=first(query, "toolId"),
                    target=first(query, "target"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "AuditLogList", "auditLogs": rows})
            elif parsed.path == "/v0/tasks":
                query = parse_qs(parsed.query)
                rows = list_project_tasks(
                    self.server.bundle,
                    status=first(query, "status"),
                    assignee=first(query, "assignee"),
                    project_id=first(query, "projectId"),
                    task_type=first(query, "taskType"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "TaskList", "tasks": rows})
            elif parsed.path.startswith("/v0/projects/") and parsed.path.endswith("/fact-view"):
                parts = [part for part in parsed.path.split("/") if part]
                if len(parts) != 6 or parts[0] != "v0" or parts[1] != "projects" or parts[3] != "tasks" or parts[5] != "fact-view":
                    raise KnowledgeError("invalid task fact view route")
                self._json(200, build_task_fact_view(self.server.bundle, parts[2], parts[4]))
            elif parsed.path == "/v0/defects":
                query = parse_qs(parsed.query)
                project_id = first(query, "projectId")
                roots = [self.server.bundle.root / "defects"]
                if project_id:
                    roots.insert(0, self.server.bundle.root / "projects" / project_id / "defects")
                rows = []
                seen = set()
                for root in roots:
                    if not root.exists():
                        continue
                    for path in sorted(root.glob("*.md")):
                        if path.name in {"index.md", "log.md"}:
                            continue
                        obj = load_object(path)
                        if obj.get("type") != "Defect":
                            continue
                        if project_id and str(obj.get("projectId") or "") != project_id:
                            continue
                        ref = str(path.relative_to(self.server.bundle.root))
                        if ref in seen:
                            continue
                        seen.add(ref)
                        obj["path"] = ref
                        rows.append(obj)
                self._json(200, {"apiVersion": "v0.1", "kind": "DefectList", "defects": rows})
            elif parsed.path == "/v0/receiver-reviews":
                query = parse_qs(parsed.query)
                project_id = first(query, "projectId")
                roots = [self.server.bundle.root / "receiver-reviews"]
                if project_id:
                    roots.insert(0, self.server.bundle.root / "projects" / project_id / "receiver-reviews")
                rows = []
                seen = set()
                for root in roots:
                    if not root.exists():
                        continue
                    for path in sorted(root.glob("*.md")):
                        if path.name in {"index.md", "log.md"}:
                            continue
                        obj = load_object(path)
                        if obj.get("type") != "ReceiverReview":
                            continue
                        if project_id and str(obj.get("projectId") or "") != project_id:
                            continue
                        ref = str(path.relative_to(self.server.bundle.root))
                        if ref in seen:
                            continue
                        seen.add(ref)
                        obj["path"] = ref
                        rows.append(obj)
                self._json(200, {"apiVersion": "v0.1", "kind": "ReceiverReviewList", "receiverReviews": rows})
            elif parsed.path == "/v0/runners":
                query = parse_qs(parsed.query)
                self._json(200, {"apiVersion": "v0.1", "kind": "RunnerRegistry", "runners": runner_registry_for_workbench(self.server.bundle, first(query, "projectId"))})
            elif parsed.path == "/v0/notifications":
                query = parse_qs(parsed.query)
                rows = list_notifications(
                    self.server.bundle,
                    status=first(query, "status"),
                    recipient=first(query, "recipient"),
                    channel=first(query, "channel"),
                    message_type=first(query, "messageType"),
                    project_id=first(query, "projectId"),
                    task_id=first(query, "taskId"),
                    discussion_id=first(query, "discussionId"),
                    limit=int(first(query, "limit") or "50"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "NotificationList", "notifications": rows})
            elif parsed.path == "/v0/scheduler/workbench":
                query = parse_qs(parsed.query)
                self._json(200, scheduler_workbench_read_model(self.server.bundle, first(query, "projectId"), first(query, "taskId")))
            elif parsed.path == "/v0/pm-control-lease/status":
                query = parse_qs(parsed.query)
                self._json(200, {"apiVersion": "v0.1", "kind": "PMControlLeaseReadModel", "pmControl": pm_control_lease_read_model(self.server.bundle, first(query, "projectId"))})
            elif parsed.path.startswith("/v0/workbench/projects/") and parsed.path.endswith("/execution-read-model"):
                query = parse_qs(parsed.query)
                project_id = parsed.path.removeprefix("/v0/workbench/projects/").removesuffix("/execution-read-model").strip("/")
                self._json(200, workbench_project_execution_read_model(self.server.bundle, project_id, first(query, "taskId")))
            elif parsed.path == "/v0/requirement-tree/workbench":
                query = parse_qs(parsed.query)
                self._json(200, requirement_tree_workbench_read_model(self.server.bundle, first(query, "projectId"), first(query, "tree")))
            elif parsed.path.startswith("/v0/tasks/"):
                task_id = parsed.path.removeprefix("/v0/tasks/").strip("/")
                self._json(200, {"apiVersion": "v0.1", "kind": "Task", "task": project_task_status(self.server.bundle, task_id)})
            elif parsed.path.startswith("/v0/discussions/"):
                discussion_id = parsed.path.removeprefix("/v0/discussions/").strip("/")
                self._json(200, {"apiVersion": "v0.1", "kind": "DiscussionSession", "discussion": discussion_session_status(self.server.bundle, discussion_id)})
            else:
                self._json(404, api_error_response("NOT_FOUND", "API route not found.", object_ref=parsed.path, next_action="Use a documented /v0 endpoint."))
        except PMControlLeaseError as exc:
            self._json(exc.http_status, api_error_response(exc.error_code, str(exc), blocker_reason=str(exc), next_action=exc.next_action, audit_ref=exc.audit_ref))
        except KnowledgeError as exc:
            self._json(400, api_error_response(stable_error_code(str(exc)), str(exc), blocker_reason=str(exc), next_action="Fix the request and retry."))

    def do_POST(self) -> None:
        payload: dict = {}
        try:
            if self.path == "/integrations/feishu/events":
                payload = self._read_json()
                self._json(200, handle_feishu_event(self.server.bundle, payload))
                return
            if not self._authorized():
                self._reject_unauthorized()
                return
            payload = self._read_json()
            record_api_command_envelope(self.path, payload, "received", permission_decision="allowed")
            if self.path == "/v0/gateway/context":
                result = gateway_context(
                    self.server.bundle,
                    require(payload, "projectId"),
                    require(payload, "agentId"),
                    require(payload, "task"),
                )
                self._json(200, result)
            elif self.path == "/v0/knowledge/query":
                incoming = {
                    "messageId": str(payload.get("messageId", "")),
                    "chatId": str(payload.get("chatId", "")),
                    "chatType": str(payload.get("chatType", "api")),
                    "text": require(payload, "query"),
                    "openId": str(payload.get("openId", payload.get("actor", ""))),
                    "userId": str(payload.get("userId", "")),
                    "mentionedOpenIds": "",
                    "mentionedUserIds": "",
                }
                result = run_knowledge_query(
                    self.server.bundle,
                    incoming,
                    require(payload, "query"),
                    project_query=str(payload.get("projectName", payload.get("projectId", ""))),
                )
                update_knowledge_query_log_delivery(self.server.bundle, str(result.get("logRef", "")), "http", "returned", sent=True)
                response = {
                    key: value
                    for key, value in result.items()
                    if key not in {"incoming", "chunks", "rejectedCandidates"}
                }
                response["citations"] = [
                    {
                        "path": row.get("path", ""),
                        "title": row.get("title", ""),
                        "status": row.get("status", ""),
                        "sourceRef": row.get("sourceRef", ""),
                        "score": row.get("score", 0),
                    }
                    for row in result.get("chunks", [])[:5]
                ]
                self._json(200, response)
            elif self.path == "/v0/workbench/projects":
                result = create_workbench_project(
                    self.server.bundle,
                    project_id=require(payload, "projectId"),
                    name=require(payload, "name"),
                    owner=require(payload, "owner"),
                    source_mode=str(payload.get("sourceMode", "local_repo")),
                    repository_refs=list_field(payload, "repositoryRefs"),
                    default_assignees=list_field(payload, "defaultAssignees"),
                    visibility=list_field(payload, "visibility"),
                    sensitivity=str(payload.get("sensitivity", "internal")),
                    actor=str(payload.get("actor", payload.get("owner", ""))),
                    idempotency_key=require(payload, "idempotencyKey"),
                    permissions=list_field(payload, "permissions") if "permissions" in payload else None,
                )
                self._json(200, result)
            elif self.path == "/v0/workbench/runner-invitations":
                result = create_runner_invitation(
                    self.server.bundle,
                    project_id=require(payload, "projectId"),
                    runner_label=require(payload, "runnerLabel"),
                    requested_capabilities=list_field(payload, "requestedCapabilities"),
                    expires_in_seconds=int(payload.get("expiresInSeconds", 900)),
                    runner_owner=str(payload.get("runnerOwner", payload.get("owner", ""))),
                    data_scopes=list_field(payload, "dataScopes"),
                    actor=str(payload.get("actor", payload.get("owner", ""))),
                    idempotency_key=require(payload, "idempotencyKey"),
                    permissions=list_field(payload, "permissions") if "permissions" in payload else None,
                    registration_url=str(payload.get("runnerRegistrationUrl", "/v0/runners/register")),
                )
                self._json(200, result)
            elif self.path == "/v0/workbench/tools":
                result = register_workbench_tool(
                    self.server.bundle,
                    project_id=require(payload, "projectId"),
                    tool_name=require(payload, "toolName"),
                    tool_type=require(payload, "toolType"),
                    risk_level=str(payload.get("riskLevel", "low")),
                    allowed_operations=list_field(payload, "allowedOperations"),
                    runner_scopes=list_field(payload, "runnerScopes"),
                    owner=str(payload.get("owner", "")),
                    actor=str(payload.get("actor", payload.get("owner", ""))),
                    idempotency_key=require(payload, "idempotencyKey"),
                    permissions=list_field(payload, "permissions") if "permissions" in payload else None,
                )
                self._json(200, result)
            elif self.path == "/v0/workbench/tool-registration-requests":
                result = create_tool_registration_request(
                    self.server.bundle,
                    project_id=require(payload, "projectId"),
                    tool_name=require(payload, "toolName"),
                    tool_type=require(payload, "toolType"),
                    risk_level=str(payload.get("riskLevel", "high")),
                    requested_operations=list_field(payload, "requestedOperations"),
                    credential_policy=str(payload.get("credentialPolicy", "")),
                    owner=str(payload.get("owner", "")),
                    justification=require(payload, "justification"),
                    data_scopes=list_field(payload, "dataScopes"),
                    runner_scopes=list_field(payload, "runnerScopes"),
                    actor=str(payload.get("actor", payload.get("owner", ""))),
                    idempotency_key=require(payload, "idempotencyKey"),
                    permissions=list_field(payload, "permissions") if "permissions" in payload else None,
                )
                self._json(200, result)
            elif self.path == "/v0/pm-control-lease/acquire":
                self._json(
                    200,
                    acquire_pm_control_lease(
                        self.server.bundle,
                        require(payload, "projectId"),
                        require(payload, "pmAgentId"),
                        runner_id=str(payload.get("runnerId", "")),
                        device_id=str(payload.get("deviceId", "")),
                        lease_seconds=int(payload.get("leaseSeconds", 900)),
                        idempotency_key=str(payload.get("idempotencyKey", "")),
                        source_channel="api",
                    ),
                )
            elif self.path == "/v0/pm-control-lease/heartbeat":
                self._json(
                    200,
                    heartbeat_pm_control_lease(
                        self.server.bundle,
                        require(payload, "projectId"),
                        require(payload, "pmAgentId"),
                        require(payload, "leaseId"),
                        require(payload, "pmLeaseToken"),
                        str(payload.get("leaseGeneration") or payload.get("fencingToken") or ""),
                        int(payload.get("leaseSeconds", 900)),
                        "api",
                    ),
                )
            elif self.path == "/v0/pm-control-lease/release":
                self._json(
                    200,
                    release_pm_control_lease(
                        self.server.bundle,
                        require(payload, "projectId"),
                        require(payload, "pmAgentId"),
                        require(payload, "leaseId"),
                        require(payload, "pmLeaseToken"),
                        str(payload.get("leaseGeneration") or payload.get("fencingToken") or ""),
                        str(payload.get("reason", "")),
                        "api",
                    ),
                )
            elif self.path == "/v0/pm-control-lease/takeover":
                self._json(
                    200,
                    takeover_pm_control_lease(
                        self.server.bundle,
                        require(payload, "projectId"),
                        require(payload, "toPmAgentId"),
                        str(payload.get("operator", payload.get("toPmAgentId", ""))),
                        require(payload, "reason"),
                        runner_id=str(payload.get("runnerId", "")),
                        device_id=str(payload.get("deviceId", "")),
                        lease_seconds=int(payload.get("leaseSeconds", 900)),
                        confirm_healthy=bool(payload.get("confirmHealthy", False)),
                        source_channel="api",
                    ),
                )
            elif self.path == "/v0/tasks/create":
                path = create_project_task(
                    self.server.bundle,
                    require(payload, "title"),
                    require(payload, "projectId"),
                    require(payload, "requester"),
                    require(payload, "assignee"),
                    str(payload.get("taskType", "knowledge_capture")),
                    str(payload.get("taskId", "")),
                    str(payload.get("priority", "normal")),
                    str(payload.get("dueAt", "")),
                    list_field(payload, "sourceMaterialRefs"),
                    list_field(payload, "expectedOutput"),
                    work_source_type=str(payload.get("workSourceType", "")),
                    requirement_refs=list_field(payload, "requirementRefs"),
                    requirement_object_refs=list_field(payload, "requirementObjectRefs"),
                    acceptance_criteria_refs=list_field(payload, "acceptanceCriteriaRefs"),
                    defect_refs=list_field(payload, "defectRefs"),
                    defect_object_refs=list_field(payload, "defectObjectRefs"),
                    incident_refs=list_field(payload, "incidentRefs"),
                    operation_refs=list_field(payload, "operationRefs"),
                    knowledge_task_refs=list_field(payload, "knowledgeTaskRefs"),
                    research_question=str(payload.get("researchQuestion", "")),
                    source_reason=str(payload.get("sourceReason", "")),
                    pm_agent_id=str(payload.get("pmAgentId", "")),
                    pm_lease_id=str(payload.get("leaseId", "")),
                    pm_fencing_token=str(payload.get("leaseGeneration") or payload.get("fencingToken") or ""),
                    pm_source_channel="api",
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "ProjectTask", "taskRef": str(path.relative_to(self.server.bundle.root)), "task": load_object(path)})
            elif self.path == "/v0/defects":
                path = create_defect(
                    self.server.bundle,
                    title=require(payload, "title"),
                    project_id=require(payload, "projectId"),
                    reporter=require(payload, "reporter"),
                    severity=str(payload.get("severity", "medium")),
                    defect_id=str(payload.get("defectId", "")),
                    requirement_refs=list_field(payload, "requirementRefs"),
                    source_task_ref=str(payload.get("sourceTaskRef", "")),
                    source_result_ref=str(payload.get("sourceResultRef", "")),
                    evidence_refs=list_field(payload, "evidenceRefs"),
                    expected_behavior=str(payload.get("expectedBehavior", "")),
                    actual_behavior=str(payload.get("actualBehavior", "")),
                    reproduction_steps=list_field(payload, "reproductionSteps"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "Defect", "defectRef": str(path.relative_to(self.server.bundle.root)), "defect": load_object(path)})
            elif self.path == "/v0/defects/create-fix-task":
                path = create_bugfix_task(
                    self.server.bundle,
                    defect_id=require(payload, "defectId"),
                    title=str(payload.get("title", "")),
                    requester=require(payload, "requester"),
                    assignee=require(payload, "assignee"),
                    task_type=str(payload.get("taskType", "development")),
                    priority=str(payload.get("priority", "high")),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "ProjectTask", "taskRef": str(path.relative_to(self.server.bundle.root)), "task": load_object(path)})
            elif self.path == "/v0/receiver-reviews":
                path = create_receiver_review(
                    self.server.bundle,
                    project_id=require(payload, "projectId"),
                    upstream_ref=require(payload, "upstreamRef"),
                    receiver_agent=require(payload, "receiverAgent"),
                    reviewer_agent=str(payload.get("reviewerAgent", "")),
                    decision=require(payload, "decision"),
                    artifact_refs=list_field(payload, "artifactRefs"),
                    checklist=list_field(payload, "checklist"),
                    issues=list_field(payload, "issues"),
                    assumptions=list_field(payload, "assumptions"),
                    review_id=str(payload.get("reviewId", "")),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "ReceiverReview", "receiverReviewRef": str(path.relative_to(self.server.bundle.root)), "receiverReview": load_object(path)})
            elif self.path == "/v0/review/update":
                audit_path = review_path(
                    self.server.bundle,
                    Path(require(payload, "target")),
                    require(payload, "status"),
                    require(payload, "reviewer"),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "ReviewResult", "auditRef": str(audit_path)})
            elif self.path == "/v0/task/accept":
                result = accept_project_task_result(
                    self.server.bundle,
                    require(payload, "taskId"),
                    require(payload, "decision"),
                    require(payload, "reviewer"),
                    reason=str(payload.get("reason", "")),
                    human=bool(payload.get("human", False)),
                )
                self._json(200, result)
            elif self.path == "/v0/discussions/create":
                result = create_discussion_session(
                    self.server.bundle,
                    require(payload, "title"),
                    str(payload.get("projectId", "")),
                    require(payload, "requester"),
                    require(payload, "topic"),
                    list_field(payload, "participantAgents") if "participantAgents" in payload else None,
                    str(payload.get("relatedTaskId", "")),
                    str(payload.get("facilitatorAgent", "agent.company.project-manager")),
                    int(payload.get("maxRounds", 1)),
                    bool(payload.get("humanVisible", True)),
                )
                self._json(200, result)
            elif self.path == "/v0/discussions/turn":
                result = submit_discussion_turn(
                    self.server.bundle,
                    require(payload, "discussionId"),
                    require(payload, "agentId"),
                    str(payload.get("role", "")),
                    require(payload, "content"),
                    str(payload.get("stance", "")),
                    list_field(payload, "concerns"),
                    list_field(payload, "recommendations"),
                    list_field(payload, "evidenceRefs"),
                )
                self._json(200, result)
            elif self.path == "/v0/discussions/finalize":
                result = finalize_discussion_session(
                    self.server.bundle,
                    require(payload, "discussionId"),
                    require(payload, "facilitator"),
                    require(payload, "summary"),
                    str(payload.get("consensus", "")),
                    str(payload.get("decision", "")),
                    list_field(payload, "openQuestions"),
                    bool(payload.get("humanDecisionRequired", False)),
                    str(payload.get("followupTaskTitle", "")),
                    str(payload.get("followupAssignee", "")),
                )
                self._json(200, result)
            elif self.path == "/v0/notifications/delivery":
                result = mark_notification_delivery(
                    self.server.bundle,
                    require(payload, "notificationId"),
                    require(payload, "status"),
                    require(payload, "actor"),
                    str(payload.get("failureReason", "")),
                    str(payload.get("deliveryRef", "")),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "NotificationRecord", "notification": result})
            elif self.path == "/v0/agents/report":
                path = create_agent_capability_report(
                    self.server.bundle,
                    agent_id=require(payload, "agentId"),
                    owner=str(payload.get("owner", "api")),
                    project_id=str(payload.get("projectId", "")),
                    period=str(payload.get("period", "")),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "AgentCapabilityReport", "reportRef": str(path.relative_to(self.server.bundle.root))})
            elif self.path == "/v0/review/finish":
                result = apply_knowledge_review_result(
                    self.server.bundle,
                    review_task_id=require(payload, "reviewTaskId"),
                    outcome=require(payload, "outcome"),
                    reviewer=require(payload, "reviewer"),
                    summary=require(payload, "summary"),
                    target_refs=[str(item) for item in payload.get("targetRefs", [])],
                )
                self._json(200, result)
            elif self.path == "/v0/publish/rebuild":
                result = publish_knowledge_bundle(
                    self.server.bundle,
                    actor=str(payload.get("actor", "api")),
                    reason=str(payload.get("reason", "api publish rebuild")),
                    rebuild_graph=bool(payload.get("rebuildGraph", False)),
                )
                self._json(200, result)
            elif self.path == "/v0/tool/invoke":
                result = invoke_tool(
                    self.server.bundle,
                    require(payload, "toolId"),
                    require(payload, "projectId"),
                    require(payload, "agentId"),
                    str(payload.get("input", "")),
                    bool(payload.get("execute", False)),
                )
                self._json(200, result)
            elif self.path == "/v0/runners/register":
                if not payload.get("idempotencyKey") and not payload.get("pairingCode"):
                    path = register_agent_runner(
                        self.server.bundle,
                        runner_id=require(payload, "runnerId"),
                        name=require(payload, "name"),
                        host_type=str(payload.get("hostType", "")),
                        mode=str(payload.get("mode", "unattended")),
                        agents=list_field(payload, "agents"),
                        capabilities=list_field(payload, "capabilities"),
                        available_projects=list_field(payload, "availableProjects"),
                        repo_access=list_field(payload, "repoAccess"),
                        data_scopes=list_field(payload, "dataScopes"),
                        ring_version=str(payload.get("ringVersion", "0.1.0")),
                    )
                    self._json(200, {"apiVersion": "v0.1", "kind": "Runner", "runnerRef": str(path.relative_to(self.server.bundle.root))})
                else:
                    result = submit_runner_registration(
                        self.server.bundle,
                        runner_id=require(payload, "runnerId"),
                        name=require(payload, "name"),
                        pairing_code=str(payload.get("pairingCode", "")),
                        host_type=str(payload.get("hostType", "")),
                        mode=str(payload.get("mode", "unattended")),
                        agents=list_field(payload, "agents"),
                        capabilities=list_field(payload, "capabilities"),
                        available_projects=list_field(payload, "availableProjects"),
                        repo_access=list_field(payload, "repoAccess"),
                        data_scopes=list_field(payload, "dataScopes"),
                        ring_version=str(payload.get("ringVersion", "0.1.0")),
                        tools=payload.get("tools") if isinstance(payload.get("tools"), list) else None,
                        models=payload.get("models") if isinstance(payload.get("models"), list) else None,
                        owner=str(payload.get("owner", "")),
                        idempotency_key=str(payload.get("idempotencyKey", "")),
                    )
                    self._json(200, result)
            elif self.path == "/v0/runners/heartbeat":
                path = heartbeat_agent_runner(
                    self.server.bundle,
                    runner_id=require(payload, "runnerId"),
                    status=str(payload.get("status", "online")),
                    load=str(payload.get("load", "")),
                    capabilities=list_field(payload, "capabilities") if "capabilities" in payload else None,
                    available_projects=list_field(payload, "availableProjects") if "availableProjects" in payload else None,
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "RunnerHeartbeat", "runnerRef": str(path.relative_to(self.server.bundle.root))})
            elif self.path == "/v0/credentials/ready":
                path = mark_access_credential_ready(
                    self.server.bundle,
                    request_id=require(payload, "requestId"),
                    secret_ref=require(payload, "secretRef"),
                    actor=str(payload.get("actor", "agent-ring")),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "CredentialReady", "credentialRef": str(path.relative_to(self.server.bundle.root))})
            elif self.path == "/v0/tasks/claim":
                self._json(
                    200,
                    {
                        "apiVersion": "v0.1",
                        "kind": "TaskClaim",
                        **claim_project_task(
                            self.server.bundle,
                            require(payload, "taskId"),
                            require(payload, "runnerId"),
                            int(payload["expectedVersion"]) if payload.get("expectedVersion") is not None else None,
                            int(payload.get("leaseSeconds", 600)),
                        ),
                    },
                )
            elif self.path == "/v0/tasks/heartbeat":
                task = heartbeat_project_task_lease(
                    self.server.bundle,
                    require(payload, "taskId"),
                    require(payload, "runnerId"),
                    require(payload, "leaseToken"),
                    int(payload.get("leaseSeconds", 600)),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "TaskHeartbeat", "task": task})
            elif self.path == "/v0/tasks/cancel":
                result = cancel_project_task(
                    self.server.bundle,
                    require(payload, "taskId"),
                    str(payload.get("actor", "agent-ring")),
                    require(payload, "reason"),
                    runner_id=str(payload.get("runnerId", "")),
                    lease_token=str(payload.get("leaseToken", "")),
                )
                self._json(200, result)
            elif self.path == "/v0/tasks/retry":
                result = retry_project_task(
                    self.server.bundle,
                    require(payload, "taskId"),
                    str(payload.get("actor", "agent-ring")),
                    require(payload, "reason"),
                    runner_id=str(payload.get("runnerId", "")),
                    lease_token=str(payload.get("leaseToken", "")),
                    preferred_runner=str(payload.get("preferredRunner", "")),
                )
                self._json(200, result)
            elif self.path == "/v0/tasks/handoff":
                result = manual_handoff_project_task(
                    self.server.bundle,
                    require(payload, "taskId"),
                    str(payload.get("actor", "agent-ring")),
                    require(payload, "handoffTo"),
                    require(payload, "summary"),
                    runner_id=str(payload.get("runnerId", "")),
                    lease_token=str(payload.get("leaseToken", "")),
                    evidence_refs=list_field(payload, "evidenceRefs"),
                    artifact_refs=list_field(payload, "artifactRefs"),
                    next_action=str(payload.get("nextAction", "")),
                    preferred_runner=str(payload.get("preferredRunner", "")),
                )
                self._json(200, result)
            elif self.path == "/v0/tasks/pull":
                self._json(
                    200,
                    project_task_context_payload(
                        self.server.bundle,
                        require(payload, "taskId"),
                        str(payload.get("runnerId", "")),
                        str(payload.get("leaseToken", "")),
                    ),
                )
            elif self.path == "/v0/tasks/finish":
                result_path = finish_project_task(
                    self.server.bundle,
                    require(payload, "taskId"),
                    str(payload.get("result", "done")),
                    require(payload, "summary"),
                    output_refs=list_field(payload, "outputRefs"),
                    knowledge_refs=list_field(payload, "knowledgeRefs"),
                    evidence_refs=list_field(payload, "evidenceRefs"),
                    next_actions=list_field(payload, "nextActions"),
                    runner_id=str(payload.get("runnerId", "")),
                    lease_token=str(payload.get("leaseToken", "")),
                    executor_agent=str(payload.get("executorAgent", "")),
                    tests_or_checks=list_field(payload, "testsOrChecks"),
                    knowledge_draft=payload.get("knowledgeDraft") if isinstance(payload.get("knowledgeDraft"), dict) else None,
                    handoff_to=str(payload.get("handoffTo", "")),
                    handoff_summary=str(payload.get("handoffSummary", "")),
                    artifact_refs=list_field(payload, "artifactRefs"),
                    open_risks=list_field(payload, "openRisks"),
                    next_suggested_task=str(payload.get("nextSuggestedTask", "")),
                    blockers=list_field(payload, "blockers"),
                    approval_request=payload.get("approvalRequest") if isinstance(payload.get("approvalRequest"), dict) else None,
                )
                task = project_task_status(self.server.bundle, require(payload, "taskId"))
                task_result = load_object(result_path)
                self._json(
                    200,
                    {
                        "apiVersion": "v0.1",
                        "kind": "TaskResult",
                        "task": task,
                        "taskResult": task_result,
                        "resultRef": str(result_path.relative_to(self.server.bundle.root)),
                    },
                )
            elif self.path == "/v0/materials/ingest":
                result = create_source_material(
                    self.server.bundle,
                    title=str(payload.get("title", "")),
                    source_ref=str(payload.get("sourceRef", "")),
                    submitter=require(payload, "submitter"),
                    project_id=str(payload.get("projectId", "")),
                    material_type=str(payload.get("materialType", "")),
                    storage_ref=str(payload.get("storageRef", "")),
                    content=str(payload.get("content", "")),
                    license_hint=str(payload.get("license", "")),
                    sensitivity=str(payload.get("sensitivity", "internal")),
                    extraction_tool=str(payload.get("extractionTool", "api")),
                    extraction_status=str(payload.get("extractionStatus", "registered")),
                    create_task_flag=bool(payload.get("createTask", False)),
                    assignee=str(payload.get("assignee", "agent.company-knowledge-core.knowledge-engineering")),
                )
                self._json(200, {"apiVersion": "v0.1", "kind": "SourceMaterialIngest", **result})
            elif self.path == "/v0/graph/export":
                actor = str(payload.get("actor", "api"))
                self._json(200, export_graph_snapshot(self.server.bundle, actor))
            elif self.path == "/v0/graph/impact":
                actor = str(payload.get("actor", "api"))
                self._json(200, graph_impact(self.server.bundle, require(payload, "ref"), actor, bool(payload.get("rebuild", False))))
            elif self.path == "/v0/command/validate":
                envelope = normalize_command_envelope(payload, str(payload.get("commandType", "update")), require_idempotency=True)
                self._json(200, {"apiVersion": "v0.1", "kind": "CommandEnvelope", "commandEnvelope": envelope})
            elif self.path == "/v0/admin/disable":
                envelope = normalize_command_envelope(
                    payload,
                    "admin.disable",
                    actor_ref=str(payload.get("actor", "")),
                    object_ref=f"{payload.get('objectType', payload.get('type', 'asset'))}:{payload.get('objectId', payload.get('id', ''))}",
                    project_ref=str(payload.get("projectId", "")),
                    require_idempotency=True,
                )
                result = disable_governed_asset(
                    self.server.bundle,
                    str(payload.get("objectType") or payload.get("type") or ""),
                    str(payload.get("objectId") or payload.get("id") or ""),
                    envelope["actorRef"],
                    envelope["reason"] or require(payload, "reason"),
                    bool(payload.get("reassign", False)),
                )
                result["commandEnvelope"] = envelope
                self._json(200, result)
            elif self.path == "/v0/metrics/report":
                envelope = normalize_command_envelope(payload, "create", actor_ref=str(payload.get("owner", "api")), require_idempotency=False)
                path = create_metrics_report(self.server.bundle, envelope["actorRef"])
                self._json(200, {"apiVersion": "v0.1", "kind": "MetricsReport", "reportRef": str(path.relative_to(self.server.bundle.root)), "commandEnvelope": envelope})
            else:
                self._json(404, api_error_response("NOT_FOUND", "API route not found.", object_ref=self.path, next_action="Use a documented /v0 endpoint."))
        except PMControlLeaseError as exc:
            if self.path.startswith("/v0/"):
                record_api_command_envelope(self.path, payload, "failed", permission_decision="allowed", response={"error": str(exc), "auditRef": exc.audit_ref})
            self._json(exc.http_status, api_error_response(exc.error_code, str(exc), blocker_reason=str(exc), next_action=exc.next_action, audit_ref=exc.audit_ref))
        except (KnowledgeError, KeyError, json.JSONDecodeError) as exc:
            if self.path.startswith("/v0/"):
                record_api_command_envelope(self.path, payload, "failed", permission_decision="allowed", response={"error": str(exc)})
            self._json(400, api_error_response(stable_error_code(str(exc)), str(exc), blocker_reason=str(exc), next_action="Fix the request and retry."))


def first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key) or [""]
    return values[0]


def require(payload: dict, key: str) -> str:
    value = payload.get(key)
    if not value:
        raise KnowledgeError(f"missing required field: {key}")
    return str(value)


def list_field(payload: dict, key: str) -> list[str]:
    value = payload.get(key, [])
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def serve(bundle: Bundle, host: str, port: int) -> None:
    httpd = KnowledgeHTTPServer((host, port), bundle, os.environ.get("ZHENZHI_KNOWLEDGE_API_TOKEN", ""))
    print(f"zhenzhi-knowledge API listening on http://{host}:{httpd.server_port}")
    httpd.serve_forever()
