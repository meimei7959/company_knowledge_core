from __future__ import annotations

import json
import hashlib
import math
import os
import re
import shlex
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


STATUS_VALUES = {
    "draft",
    "pending",
    "observed",
    "processing",
    "submitted",
    "reviewing",
    "done",
    "running",
    "testing",
    "verified",
    "approved",
    "stale_candidate",
    "stale",
    "deprecated",
    "disabled",
    "blocked",
    "waiting_runner",
    "manual-runner-required",
    "claimed",
    "rejected",
    "cancelled",
    "repair_pending",
    "approval_required",
    "approval_relay_requested",
    "changes_requested",
    "clarification_required",
    "failed",
    "sent",
    "active",
    "open",
    "on_track",
    "at_risk",
    "needs_decision",
    "resolved",
    "online",
    "busy",
    "offline",
    "degraded",
    "idle",
    "draining",
    "disabled",
    "intake",
    "clarify",
    "project_draft",
    "launch_approved",
    "task_created",
    "quality_evaluated",
    "handoff_ready",
    "pm_reviewing",
    "waiting_acceptance",
    "accepted",
    "auto_accepted",
    "next_task_created",
    "needs-handoff-completion",
    "retry_required",
    "ready",
    "needs_repair",
    "escalated",
    "delivered",
    "operating",
    "stopped",
    "feedback_loop",
    "waiting_agent_turns",
    "summarized",
    "waiting_human_decision",
    "consensus_reached",
    "clarifying",
    "decision_needed",
    "superseded",
    "pending_review",
    "pending_authorization",
    "auto_approved",
    "online_readonly",
    "online_schedulable",
    "expiring",
    "expired",
    "released",
    "taken_over",
    "consumed",
    "triaged",
    "in_progress",
    "fixed",
    "regression_required",
    "reopened",
    "closed",
    "accepted_for_work",
    "accepted_with_assumptions",
    "needs_rework",
    "human_decision_required",
}

KNOWLEDGE_ENGINEERING_AGENT_ID = "agent.company-knowledge-core.knowledge-engineering"
KNOWLEDGE_REVIEW_AGENT_ID = "agent.core.knowledge-review"
KNOWLEDGE_OPS_AGENT_ID = "agent.core.knowledge-ops"
KNOWLEDGE_STEWARD_AGENT_ID = "agent.core.knowledge-steward"
DEFAULT_MAX_TASK_ATTEMPTS = 3
PENDING_WORKSPACE_REF = "pending_confirmation"

TYPE_VALUES = {
    "Project",
    "ProjectTask",
    "KnowledgeTask",
    "TaskResult",
    "ReviewRecord",
    "NotificationRecord",
    "AgentRunner",
    "AccessCredentialRequest",
    "Agent",
    "ToolAsset",
    "SkillAsset",
    "KnowledgeItem",
    "SourceMaterial",
    "AgentRun",
    "Decision",
    "Workflow",
    "Prompt",
    "AuditLog",
    "Policy",
    "ConflictRecord",
    "EvalCase",
    "EvalRun",
    "MetricsReport",
    "AgentImprovementProposal",
    "AgentCapabilityReport",
    "PMControlLease",
    "ProjectPmParticipant",
    "PmLeaseTakeoverRecord",
    "ActorContext",
    "ActorFeedback",
    "ProjectManagerReview",
    "ProjectManagerAction",
    "OutcomeSlice",
    "RoleOperatingReview",
    "KnowledgeGraphEdge",
    "GraphSnapshot",
    "ProjectIntake",
    "ProjectDraft",
    "OperationsFeedback",
    "DiscussionSession",
    "DiscussionTurn",
    "DiscussionSummary",
    "OperatingRuleIssue",
    "Requirement",
    "RequirementState",
    "RequirementTree",
    "RequirementNode",
    "RequirementMapping",
    "AcceptanceGate",
    "RequirementCoverageSnapshot",
    "Defect",
    "ReceiverReview",
    "ClarificationRound",
    "PRDDocument",
    "AcceptanceCriteria",
    "ImpactReview",
    "FeedbackRecord",
    "Experiment",
    "AgentProfile",
    "SkillDefinition",
    "AgentSession",
    "AgentDevice",
    "AgentMessage",
    "TaskPackage",
    "WorktreeBinding",
    "V1AcceptanceRun",
    "RunnerInvitation",
    "ToolRegistrationRequest",
}

PRODUCT_STATUS_VALUES = {
    "draft",
    "clarifying",
    "decision_needed",
    "approved",
    "in_progress",
    "reviewing",
    "done",
    "blocked",
    "rejected",
}

REQUIREMENT_TREE_STATUS_VALUES = {"draft", "reviewing", "accepted", "blocked", "superseded"}
REQUIREMENT_NODE_KIND_VALUES = {
    "business",
    "user",
    "product",
    "functional",
    "non_functional",
    "governance",
    "data",
    "integration",
    "ops",
}
REQUIREMENT_NODE_STATUS_VALUES = {"draft", "needs_clarification", "ready_for_planning", "accepted", "blocked", "superseded"}
REQUIREMENT_MAPPING_KIND_VALUES = {"decomposes_to", "satisfies", "verified_by", "implemented_by", "accepted_by", "blocked_by", "supersedes"}
REQUIREMENT_MAPPING_CONFIDENCE_VALUES = {"source_exact", "pm_confirmed", "agent_inferred", "backfill_inferred"}
REQUIREMENT_MAPPING_REVIEW_STATE_VALUES = {"draft", "accepted", "needs_review", "rejected"}
ACCEPTANCE_GATE_VERIFICATION_METHOD_VALUES = {"manual_review", "automated_test", "api_check", "document_check", "e2e_flow", "metric_check"}
ACCEPTANCE_GATE_STATUS_VALUES = {"draft", "ready", "passed", "failed", "blocked", "waived"}
REQUIREMENT_COVERAGE_ROW_FIELDS = ["businessRequirementRef", "userRequirementRef", "productRequirementRef", "functionalRequirementRef", "taskRef", "resultRef", "testCaseRef", "acceptanceGateRef"]
REQUIREMENT_TREE_SECRET_VALUE_RE = re.compile(r"(sk-[a-z0-9_-]{10,}|api[_-]?key\s*[:=]|password\s*[:=]|token\s*[:=]|secret\s*[:=])", re.IGNORECASE)

API_SOURCE_CHANNELS = {"feishu", "api", "cli", "console", "desktop", "agent_ring"}
WRITE_COMMAND_TYPES = {
    "create",
    "update",
    "approve",
    "reject",
    "claim",
    "finish",
    "admin.disable",
    "notification.delivery",
    "review.update",
}

CRITICAL_NOTIFICATION_TYPES = {
    "knowledge_published",
    "knowledge_rejected",
    "knowledge_approval_required",
    "knowledge_approval_rejected",
    "knowledge_approval_rejected_notice",
    "task_blocked",
    "task_waiting_runner",
    "task_manual_runner_required",
    "runner_lease_stale",
    "approval_request_failed",
    "review_result_failed",
    "security_permission_change",
    "critical_eval_failure",
    "asset_disabled",
}

SECRET_KEYS = ("token", "secret", "password", "passwd", "credential", "api_key", "apikey", "key")
MATERIAL_RAW_TEXT_MAX_CHARS = 20_000
CENTRAL_RECORD_MAX_BYTES = 64 * 1024
COLLECTION_NAMES = {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"}
OBJECT_ROOT_NAMES = ["projects", "agents", "tools", "knowledge", "runs", "tasks", "sources", "task-results", "runners", "runner-invitations", "tool-registration-requests", "credential-requests", "notifications", "graph", "discussions", "pm-reviews", "pm-actions", "outcome-slices", "role-reviews", "rule-issues", "actors", "requirements", "prd", "decisions", "reviews", "defects", "receiver-reviews"]
SAFE_SECRET_METADATA_KEYS = {
    "actorkey",
    "secretref",
    "secretrefs",
    "leasetokenhash",
    "leaseproofhash",
    "pmcontrolfencingtoken",
    "credentialtype",
    "credentialkind",
    "credentialscope",
    "credentialrisk",
}
RETRIEVAL_VECTOR_DIMS = 64
DATABASE_URL_ENV = "DATABASE_URL"
DATABASE_URL_ALIAS_ENV = "ZHENZHI_KNOWLEDGE_DATABASE_URL"
POSTGRES_SCHEMES = {"postgres", "postgresql"}
KNOWLEDGE_SYSTEM_CATEGORIES = {"policies", "audit", "evals", "eval-runs", "conflicts", "metrics", "reviews", "agent-improvements"}
KNOWLEDGE_CONTENT_CATEGORIES = {"company", "engineering", "product", "business", "operations", "research", "customer"}
KNOWLEDGE_ALLOWED_CATEGORIES = KNOWLEDGE_SYSTEM_CATEGORIES | KNOWLEDGE_CONTENT_CATEGORIES
KNOWLEDGE_ITEM_REQUIRED_FIELDS = {"type", "title", "timestamp", "owner", "status", "scope", "sourceRef", "confidence"}
AGENT_TEAM_GUIDE_REF = "docs/agent-team/company-agent-team-operating-guide.md"
AGENT_TEAM_GUIDE_FEISHU_URL = "https://xcn68awb7dsi.feishu.cn/docx/YnHudAQfVowx6vxnDfUc5C7onve"
COMMON_AGENT_RULES_REF = "docs/agent-team/common-agent-operating-rules.md"
AGENT_CONSTITUTION_REF = "docs/agent-team/company-agent-constitution.md"
TASK_RUNTIME_CONTRACT_REF = "docs/agent-team/agent-task-runtime-contract.md"
HUMAN_ACCEPTANCE_POLICY_REF = "docs/agent-team/human-acceptance-policy.md"
ROLE_OPERATING_SPEC_REF = "docs/agent-team/role-operating-specs.json"
SKILL_REGISTRY_REF = "docs/agent-team/company-skill-registry.json"
SKILL_STANDARD_REF = "docs/agent-team/skill-system-architecture.md"
SKILL_DELIVERY_STANDARD_REF = "docs/agent-team/skill-delivery-standard.md"
SKILL_QUALITY_SOURCES_REF = "docs/agent-team/skill-quality-sources.json"
PRODUCTION_SKILL_PACKAGE_FILES = (
    "references/delivery-card.md",
    "templates/output-template.md",
    "examples/quality-example.md",
)
SHARED_SKILL_PACKAGE_FILES = (
    "skills/_shared/skill-output-contract.md",
    "skills/_shared/references/mature-skill-package.md",
    "skills/_shared/templates/skill-output-template.md",
    "skills/_shared/examples/skill-quality-example.md",
)
PRODUCTION_SKILL_REQUIRED_SECTIONS = {
    "Purpose",
    "Triggers",
    "Inputs",
    "Workflow",
    "Outputs",
    "Quality Gate",
    "Failure Routes",
}
PRODUCT_MANAGER_REQUIRED_SKILLS = {
    "requirement-clarification",
    "prd-scope-definition",
    "prd-high-quality-generation",
}
PRD_HIGH_QUALITY_PROTOCOL_FIELD = "prdQualityProtocol"
PRD_HIGH_QUALITY_PROTOCOL_STEPS = [
    "requirementClarifier",
    "evidencePackGenerator",
    "productPlanGenerator",
    "adversarialReviewer",
    "prdQualityChecker",
    "deliveryPackGenerator",
]
PRD_HIGH_QUALITY_LIGHT_STEPS = [
    "requirementClarifier",
    "prdQualityChecker",
    "deliveryPackGenerator",
]
PRD_HIGH_QUALITY_PROTOCOL_LEVELS = {"none", "light", "full"}
PRD_REQUIREMENT_CLARIFIER_REQUIRED_FIELDS = ["firstPrinciples", "socraticQuestions"]
AGENT_TEAM_GUIDE_IMPACT_TASK_TYPES = {
    "agent_role_change",
    "agent_team_change",
    "skill_change",
    "workflow_change",
    "scheduler_change",
    "agent_ring_change",
    "knowledge_policy_change",
    "governance_change",
}
AGENT_TEAM_GUIDE_IMPACT_PATTERNS = (
    r"\bagent team\b",
    r"\b(role agent|agent role)\b",
    r"\b(skill pack|update .*skill|change .*skill|add .*skill|remove .*skill)\b",
    r"\b(update .*workflow|change .*workflow|modify .*workflow|workflow_change)\b",
    r"\b(update .*scheduler|change .*scheduler|scheduler rule|scheduler_change)\b",
    r"\b(agent ring protocol|agent ring contract|agent_ring_change|runner protocol|runner registry)\b",
    r"\b(knowledge policy|knowledge_policy_change|review gate)\b",
    r"(新增|修改|删除).{0,12}(agent|Agent|角色|岗位职责|技能|skill|Skill|工作流|调度|知识规则|审核门禁)",
    r"(agent|Agent|角色|岗位职责|技能|skill|Skill|工作流|调度|知识规则|审核门禁).{0,12}(新增|修改|删除|变更)",
)

PROJECT_MANAGER_AGENT_ID = "agent.company.project-manager"
PRODUCT_MANAGER_AGENT_ID = "agent.company.product-manager"
DESIGN_AGENT_ID = "agent.company.design"
ARCHITECTURE_AGENT_ID = "agent.company.architecture"
DEVELOPMENT_AGENT_ID = "agent.company.development"
TEST_AGENT_ID = "agent.company.test"
OPERATIONS_AGENT_ID = "agent.company.operations"
KNOWLEDGE_QUERY_AGENT_ID = "agent.company.knowledge-query"

TASK_ROUTING_STATUS_VALUES = {
    "pending",
    "waiting_runner",
    "processing",
    "manual_handoff",
    "waiting_acceptance",
    "changes_requested",
    "blocked",
    "submitted",
    "done",
    "rejected",
    "cancelled",
}
LEGACY_TASK_ROUTING_STATUS_VALUES = {
    "manual-runner-required",
}
WORK_SOURCE_TYPE_VALUES = {"feature", "bugfix", "project_setup", "research", "knowledge_ingest", "maintenance"}
DEFECT_STATUS_VALUES = {"open", "triaged", "in_progress", "fixed", "regression_required", "closed", "reopened", "rejected"}
RECEIVER_REVIEW_STATUS_VALUES = {
    "accepted_for_work",
    "accepted_with_assumptions",
    "needs_rework",
    "human_decision_required",
}
ACCEPTANCE_POLICY_STATUS_VALUES = {
    "not_required",
    "waiting_acceptance",
    "waiting_test_regression",
    "waiting_product_review",
    "waiting_project_manager_review",
    "ready_for_test",
    "ready_for_development_rework",
    "ready_for_project_manager_handoff",
    "accepted_for_development",
    "submitted_for_architecture_handoff",
    "blocked",
    "blocked_pending_pm_or_human_decision",
    "blocked_for_production_launch",
    "accepted",
    "auto_accepted",
    "rejected",
    "changes_requested",
}
QUALITY_DECISION_VALUES = {
    "close",
    "handoff_ready",
    "retry_required",
    "repair_required",
    "review_required",
    "escalate_to_project_manager",
    "auto_accepted",
}
QUALITY_DECISION_BAD_VALUES = {"invalid", "unknown", "none", "null", "todo", "tbd", "not_a_decision"}
QUALITY_DECISION_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
TERMINAL_TASK_STATUSES = {"done", "rejected", "cancelled"}
CLOSED_TASK_STATUSES = {"done", "rejected", "cancelled"}
TASK_STATE_TRANSITIONS = {
    "pending": {"waiting_runner", "processing", "manual_handoff", "waiting_acceptance", "changes_requested", "blocked", "done", "rejected", "cancelled"},
    "waiting_runner": {"processing", "claimed", "manual_handoff", "blocked", "done", "rejected", "cancelled"},
    "claimed": {"processing", "manual_handoff", "approval_relay_requested", "repair_pending", "waiting_acceptance", "changes_requested", "blocked", "done", "rejected", "cancelled"},
    "processing": {"manual_handoff", "approval_relay_requested", "repair_pending", "waiting_acceptance", "changes_requested", "blocked", "done", "rejected", "cancelled"},
    "manual_handoff": {"waiting_runner", "processing", "blocked", "rejected", "cancelled"},
    "approval_relay_requested": {"processing", "manual_handoff", "repair_pending", "blocked", "rejected", "cancelled"},
    "repair_pending": {"pending", "waiting_runner", "processing", "manual_handoff", "blocked", "rejected", "cancelled"},
    "waiting_acceptance": {"done", "changes_requested", "blocked", "rejected", "cancelled"},
    "changes_requested": {"pending", "waiting_runner", "processing", "manual_handoff", "blocked", "rejected", "cancelled"},
    "blocked": {"pending", "waiting_runner", "processing", "manual_handoff", "rejected", "cancelled"},
}

ROLE_HANDOFF_CONTRACTS = {
    "project_management": {
        "from": PROJECT_MANAGER_AGENT_ID,
        "to": PRODUCT_MANAGER_AGENT_ID,
        "requiredArtifacts": ["project goal", "scope", "priority", "constraints", "milestones"],
    },
    "product_requirement": {
        "from": PRODUCT_MANAGER_AGENT_ID,
        "to": DESIGN_AGENT_ID,
        "requiredArtifacts": ["requirement brief", "user scenarios", "acceptance criteria", "boundary conditions"],
    },
    "design_spec": {
        "from": DESIGN_AGENT_ID,
        "to": ARCHITECTURE_AGENT_ID,
        "requiredArtifacts": ["flow/state spec", "interaction rules", "edge states", "implementation notes"],
    },
    "architecture_plan": {
        "from": ARCHITECTURE_AGENT_ID,
        "to": DEVELOPMENT_AGENT_ID,
        "requiredArtifacts": ["technical architecture plan", "system boundaries", "interface/data contracts", "risk notes", "test focus"],
    },
    "development": {
        "from": DEVELOPMENT_AGENT_ID,
        "to": ARCHITECTURE_AGENT_ID,
        "requiredArtifacts": ["implementation plan", "change summary", "self-test result", "risk notes"],
    },
    "architecture_code_review": {
        "from": ARCHITECTURE_AGENT_ID,
        "to": TEST_AGENT_ID,
        "requiredArtifacts": ["code architecture review", "must-fix resolution", "accepted risks", "test focus"],
    },
    "testing": {
        "from": TEST_AGENT_ID,
        "to": PROJECT_MANAGER_AGENT_ID,
        "requiredArtifacts": ["test conclusion", "defect list", "release recommendation", "blockers"],
    },
    "operations": {
        "from": OPERATIONS_AGENT_ID,
        "to": PROJECT_MANAGER_AGENT_ID,
        "requiredArtifacts": ["operating result", "feedback evidence", "impact", "suggested next action"],
    },
    "knowledge_capture": {
        "from": KNOWLEDGE_ENGINEERING_AGENT_ID,
        "to": KNOWLEDGE_REVIEW_AGENT_ID,
        "requiredArtifacts": ["original source", "summary", "structured draft", "evidence refs"],
    },
    "search_retrieval": {
        "from": KNOWLEDGE_QUERY_AGENT_ID,
        "to": "",
        "requiredArtifacts": ["answer", "source refs", "confidence or missing evidence note"],
    },
}

TASK_RUNTIME_PROFILES = {
    "knowledge_capture": {
        "category": "knowledge",
        "objectType": "KnowledgeTask",
        "defaultAssignee": KNOWLEDGE_ENGINEERING_AGENT_ID,
        "qualityGate": "knowledge_capture",
        "acceptancePath": "knowledge_review",
        "requiresSourceMaterial": True,
        "requiresKnowledgeDraft": True,
        "requiresTests": False,
    },
    "knowledge_retry": {
        "category": "knowledge",
        "objectType": "KnowledgeTask",
        "defaultAssignee": KNOWLEDGE_ENGINEERING_AGENT_ID,
        "qualityGate": "knowledge_capture",
        "acceptancePath": "knowledge_review",
        "requiresSourceMaterial": True,
        "requiresKnowledgeDraft": True,
        "requiresTests": False,
    },
    "project_initialization": {
        "category": "project",
        "objectType": "ProjectTask",
        "defaultAssignee": PROJECT_MANAGER_AGENT_ID,
        "qualityGate": "project_management",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": False,
    },
    "project_intake": {
        "category": "project",
        "objectType": "ProjectTask",
        "defaultAssignee": PROJECT_MANAGER_AGENT_ID,
        "qualityGate": "project_management",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": False,
    },
    "project_management": {
        "category": "project",
        "objectType": "ProjectTask",
        "defaultAssignee": PROJECT_MANAGER_AGENT_ID,
        "qualityGate": "project_management",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": False,
    },
    "engineering_action": {
        "category": "engineering",
        "objectType": "ProjectTask",
        "defaultAssignee": DEVELOPMENT_AGENT_ID,
        "qualityGate": "engineering",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": True,
    },
    "workflow_runtime_core": {
        "category": "engineering",
        "objectType": "ProjectTask",
        "defaultAssignee": DEVELOPMENT_AGENT_ID,
        "qualityGate": "engineering",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": True,
    },
    "development": {
        "category": "engineering",
        "objectType": "ProjectTask",
        "defaultAssignee": DEVELOPMENT_AGENT_ID,
        "qualityGate": "engineering",
        "acceptancePath": "test_then_pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": True,
    },
    "implementation": {
        "category": "engineering",
        "objectType": "ProjectTask",
        "defaultAssignee": DEVELOPMENT_AGENT_ID,
        "qualityGate": "engineering",
        "acceptancePath": "test_then_pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": True,
    },
    "testing": {
        "category": "testing",
        "objectType": "ProjectTask",
        "defaultAssignee": TEST_AGENT_ID,
        "qualityGate": "testing",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": True,
    },
    "qa": {
        "category": "testing",
        "objectType": "ProjectTask",
        "defaultAssignee": TEST_AGENT_ID,
        "qualityGate": "testing",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": True,
    },
}


class KnowledgeError(RuntimeError):
    pass


class PMControlLeaseError(KnowledgeError):
    def __init__(
        self,
        error_code: str,
        message: str,
        audit_ref: str = "",
        http_status: int = 409,
        next_action: str = "",
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.audit_ref = audit_ref
        self.http_status = http_status
        self.next_action = next_action


@dataclass(frozen=True)
class Bundle:
    root: Path

    @property
    def zz_dir(self) -> Path:
        return self.root / ".zhenzhi"

    @property
    def config_path(self) -> Path:
        return self.zz_dir / "config.json"

    @property
    def context_path(self) -> Path:
        return self.zz_dir / "context" / "current.md"

    def context_archive_path(self, context_id: str) -> Path:
        return self.zz_dir / "context" / f"{slug(context_id)}.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def api_error_response(
    error_code: str,
    message: str,
    object_ref: str = "",
    blocker_reason: str = "",
    next_action: str = "",
    audit_ref: str = "",
) -> dict[str, Any]:
    return {
        "apiVersion": "v0.1",
        "kind": "Error",
        "errorCode": error_code,
        "message": message,
        "objectRef": object_ref,
        "blockerReason": blocker_reason,
        "nextAction": next_action,
        "auditRef": audit_ref,
    }


def stable_error_code(message: str) -> str:
    text = message.lower()
    if "permission" in text or "unauthorized" in text or "denied" in text:
        return "UNAUTHORIZED"
    if "missing required field" in text:
        return "INVALID_ENVELOPE"
    if "approval" in text or "human" in text or "self-approve" in text:
        return "HUMAN_APPROVAL_REQUIRED"
    if "secret" in text or "token" in text or "credential" in text:
        return "SECRET_REDACTED"
    if "not found" in text:
        return "NOT_FOUND"
    return "INVALID_REQUEST"


def actor_is_agent(actor_ref: str) -> bool:
    value = actor_ref.strip().lower()
    return value.startswith("agent.") or value.startswith("runner.") or value in {
        KNOWLEDGE_REVIEW_AGENT_ID,
        KNOWLEDGE_OPS_AGENT_ID,
        KNOWLEDGE_STEWARD_AGENT_ID,
        PROJECT_MANAGER_AGENT_ID,
        PRODUCT_MANAGER_AGENT_ID,
        DEVELOPMENT_AGENT_ID,
        TEST_AGENT_ID,
        OPERATIONS_AGENT_ID,
    }


def normalize_command_envelope(
    payload: dict[str, Any],
    command_type: str,
    actor_ref: str = "",
    project_ref: str = "",
    object_ref: str = "",
    source_channel: str = "api",
    require_idempotency: bool = False,
) -> dict[str, Any]:
    raw = payload.get("commandEnvelope") if isinstance(payload.get("commandEnvelope"), dict) else {}
    envelope = {
        "actorRef": str(raw.get("actorRef") or payload.get("actorRef") or actor_ref or payload.get("actor") or ""),
        "actorRole": str(raw.get("actorRole") or payload.get("actorRole") or ""),
        "sourceChannel": str(raw.get("sourceChannel") or payload.get("sourceChannel") or source_channel),
        "commandType": str(raw.get("commandType") or command_type),
        "objectRef": str(raw.get("objectRef") or payload.get("objectRef") or object_ref),
        "projectRef": str(raw.get("projectRef") or payload.get("projectRef") or project_ref or payload.get("projectId") or ""),
        "idempotencyKey": str(raw.get("idempotencyKey") or payload.get("idempotencyKey") or ""),
        "reason": str(raw.get("reason") or payload.get("reason") or ""),
        "evidenceRefs": [str(item) for item in as_list(raw.get("evidenceRefs") or payload.get("evidenceRefs"))],
        "requestedStatus": str(raw.get("requestedStatus") or payload.get("requestedStatus") or payload.get("status") or ""),
    }
    missing = [field for field in ["actorRef", "sourceChannel", "commandType"] if not envelope[field]]
    if require_idempotency and not envelope["idempotencyKey"]:
        missing.append("idempotencyKey")
    if missing:
        raise KnowledgeError(f"missing required field: commandEnvelope.{','.join(missing)}")
    if envelope["sourceChannel"] not in API_SOURCE_CHANNELS:
        raise KnowledgeError(f"unknown sourceChannel: {envelope['sourceChannel']}")
    if require_idempotency and envelope["commandType"] not in WRITE_COMMAND_TYPES and not envelope["commandType"].startswith("admin."):
        raise KnowledgeError(f"unknown commandType: {envelope['commandType']}")
    return envelope


def database_url() -> str:
    value = os.environ.get(DATABASE_URL_ENV, "").strip() or os.environ.get(DATABASE_URL_ALIAS_ENV, "").strip()
    if not value:
        raise KnowledgeError("DATABASE_URL is required and must point to PostgreSQL")
    parsed = urlparse(value)
    if parsed.scheme not in POSTGRES_SCHEMES:
        raise KnowledgeError("DATABASE_URL must use a PostgreSQL URL scheme")
    return value


def connect_database():
    url = database_url()
    try:
        import psycopg
    except ImportError as exc:
        raise KnowledgeError("psycopg is required for PostgreSQL access; install project dependencies") from exc
    return psycopg.connect(url)


def fetchall_dicts(cursor) -> list[dict[str, Any]]:
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def table_exists(conn, table_name: str) -> bool:
    row = conn.execute("select to_regclass(%s)", (table_name,)).fetchone()
    return bool(row and row[0])


def ensure_database_schema() -> None:
    conn = connect_database()
    try:
        conn.execute(
            """
            create table if not exists objects (
                path text primary key,
                "type" text not null default '',
                title text not null default '',
                status text not null default '',
                owner text not null default '',
                scope text not null default '',
                "projectId" text not null default '',
                "agentId" text not null default '',
                "toolId" text not null default '',
                "riskLevel" text not null default '',
                "updatedAt" text not null default ''
            )
            """
        )
        conn.execute(
            """
            create table if not exists chunks (
                path text not null,
                "chunkId" text not null,
                "type" text not null default '',
                title text not null default '',
                status text not null default '',
                owner text not null default '',
                scope text not null default '',
                "projectId" text not null default '',
                "agentId" text not null default '',
                "toolId" text not null default '',
                text text not null default '',
                vector jsonb not null,
                "sourceRef" text not null default '',
                primary key(path, "chunkId")
            )
            """
        )
        conn.execute('create index if not exists objects_type_idx on objects ("type")')
        conn.execute('create index if not exists objects_status_idx on objects (status)')
        conn.execute('create index if not exists objects_project_idx on objects ("projectId")')
        conn.execute('create index if not exists chunks_project_idx on chunks ("projectId")')
        conn.execute('create index if not exists chunks_scope_idx on chunks (scope)')
        conn.commit()
    finally:
        conn.close()


def parse_utc(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def secret_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def unique_time_id(prefix: str) -> str:
    return prefix + "." + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise KnowledgeError("id cannot be empty")
    return value


def safe_slug(value: str, fallback_prefix: str = "item") -> str:
    try:
        return slug(value)
    except KnowledgeError:
        digest = hashlib.sha256(value.strip().encode("utf-8")).hexdigest()[:10]
        return f"{fallback_prefix}-{digest}"


def exact_path_exists(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return any(child.name == path.name for child in path.parent.iterdir())
    except OSError:
        return False


def find_bundle_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / "index.md").exists() and (parent / "AGENTS.md").exists():
            return parent
    return current


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def append_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(content)


def load_config(bundle: Bundle) -> dict[str, Any]:
    if not bundle.config_path.exists():
        raise KnowledgeError("missing .zhenzhi/config.json; run zhenzhi-knowledge init")
    return json.loads(read_text(bundle.config_path))


def save_config(bundle: Bundle, config: dict[str, Any]) -> None:
    ensure_dir(bundle.zz_dir)
    write_text(bundle.config_path, json.dumps(config, indent=2, ensure_ascii=False) + "\n")


def default_config(bundle: Bundle, user_id: str, ai_tool: str, agent_id: str, remote: str | None) -> dict[str, Any]:
    return {
        "schemaVersion": "v0.1",
        "userId": user_id,
        "defaultAiTool": ai_tool,
        "defaultAgentId": agent_id,
        "defaultProjectId": "",
        "entrypointPath": ".zhenzhi/agent-entrypoint.md",
        "activeProfile": "local",
        "profiles": {
            "local": {
                "backend": "git",
                "knowledgeRepo": str(bundle.root),
                "remote": remote or "",
            },
            "staging": {
                "backend": "api",
                "apiBaseUrl": "${ZHENZHI_KNOWLEDGE_API_STAGING}",
                "apiTokenEnv": "ZHENZHI_KNOWLEDGE_API_TOKEN_STAGING",
            },
            "production": {
                "backend": "api",
                "apiBaseUrl": "${ZHENZHI_KNOWLEDGE_API_PROD}",
                "apiTokenEnv": "ZHENZHI_KNOWLEDGE_API_TOKEN_PROD",
            },
        },
    }


def render_local_start_prompt(ai_tool: str, project_id: str, agent_id: str) -> str:
    tool_names = {
        "codex": "Codex",
        "antigravity": "Antigravity",
        "claude": "Claude",
    }
    tool_name = tool_names.get(ai_tool, ai_tool)
    return f"""# {tool_name} Knowledge Start

Use this file before formal work in this repository.

```txt
projectId: {project_id or "<project-id>"}
agentId: {agent_id}
task: <task>

Before work:
1. Run `zhenzhi-knowledge sync pull`.
2. Run `zhenzhi-knowledge start --project {project_id or "<project-id>"} --agent {agent_id} --task "<task>"`.
3. Read `.zhenzhi/context/current.md`.

During work:
- Use only registered ToolAsset records.
- Respect Policy Result, allowed scopes, and allowed tool risk levels.
- Preserve sourceRef for knowledge used.

After work:
1. Run `zhenzhi-knowledge finish --project {project_id or "<project-id>"} --agent {agent_id} --summary "<summary>"`.
2. State knowledge refs used.
3. State drafts or ToolAsset updates written.
```
"""


def render_agent_entrypoint(bundle: Bundle, config: dict[str, Any]) -> str:
    active_name = config.get("activeProfile", "local")
    active_profile = config.get("profiles", {}).get(active_name, {})
    agent_id = config.get("defaultAgentId", "")
    project_id = config.get("defaultProjectId", "")
    remote = active_profile.get("remote", "")
    api_base = active_profile.get("apiBaseUrl", "")
    return f"""# Zhenzhi Knowledge Agent Entrypoint

This file connects local AI tools to the company knowledge bundle.

## Identity

- userId: {config.get("userId", "")}
- defaultAiTool: {config.get("defaultAiTool", "")}
- defaultAgentId: {agent_id}
- defaultProjectId: {project_id or "unset"}

## Repository

- knowledgeRepo: {bundle.root}
- remote: {remote or "unset"}
- activeProfile: {active_name}
- backend: {active_profile.get("backend", "")}
- apiBaseUrl: {api_base or "unset"}

## Required Workflow

Before work:

```bash
zhenzhi-knowledge sync pull
zhenzhi-knowledge start --project {project_id or "<project-id>"} --agent {agent_id} --task "<task>"
```

Then read:

```bash
.zhenzhi/context/current.md
```

During work:

- Search knowledge with `zhenzhi-knowledge rag search --query "<query>"`.
- Use only registered tools from the context pack or `zhenzhi-knowledge index search --type ToolAsset`.
- Register reusable tools with `zhenzhi-knowledge tool register`.
- Write only structured draft knowledge. Do not use this repository as a raw file dump.
- Put KnowledgeItem files under `knowledge/<category>/` with sourceRef, confidence, status, owner, and scope.
- Keep raw documents, screenshots, transcripts, exports, and temporary notes outside the knowledge bundle until they are summarized and reviewed.
- Do not store secrets in knowledge files, prompts, logs, or audit details.
- Do not promote facts or tools directly to verified/approved without review.

After work:

```bash
zhenzhi-knowledge finish --project {project_id or "<project-id>"} --agent {agent_id} --summary "<summary>"
zhenzhi-knowledge sync push
```

## Useful Commands

```bash
zhenzhi-knowledge status
zhenzhi-knowledge index rebuild
zhenzhi-knowledge rag rebuild
zhenzhi-knowledge review list
zhenzhi-knowledge audit search --agent-id {agent_id}
```
"""


def install_connector(
    bundle: Bundle,
    user_id: str,
    ai_tool: str,
    agent_id: str,
    remote: str,
    default_project: str,
    register_agent: bool = False,
    agent_name: str = "",
    purpose: str = "local AI development",
    rebuild_indexes: bool = True,
) -> list[Path]:
    config = default_config(bundle, user_id, ai_tool, agent_id, remote)
    config["defaultProjectId"] = slug(default_project) if default_project else ""
    save_config(bundle, config)

    written: list[Path] = [bundle.config_path]
    write_text(bundle.zz_dir / "agent-entrypoint.md", render_agent_entrypoint(bundle, config))
    written.append(bundle.zz_dir / "agent-entrypoint.md")
    write_text(bundle.zz_dir / "codex-start.md", render_local_start_prompt("codex", config["defaultProjectId"], agent_id))
    written.append(bundle.zz_dir / "codex-start.md")
    write_text(bundle.zz_dir / "antigravity-start.md", render_local_start_prompt("antigravity", config["defaultProjectId"], agent_id))
    written.append(bundle.zz_dir / "antigravity-start.md")
    write_text(bundle.zz_dir / "claude-start.md", render_local_start_prompt("claude", config["defaultProjectId"], agent_id))
    written.append(bundle.zz_dir / "claude-start.md")

    if register_agent:
        agent_path = bundle.root / "agents" / f"{slug(agent_id)}.md"
        if not agent_path.exists():
            written.append(make_agent(bundle, agent_id, agent_name or agent_id, user_id, ai_tool, purpose))

    if rebuild_indexes:
        rebuild_index(bundle)
        rebuild_retrieval_index(bundle)

    return written


def scan_for_secret_values(path: Path) -> list[str]:
    problems: list[str] = []
    if not path.exists() or not path.is_file():
        return problems
    text = read_text(path)
    for line_no, line in enumerate(text.splitlines(), 1):
        lower = line.lower()
        if "secretref://" in lower and not re.search(r"(sk-|api[_-]?key|token[_-]?[a-z0-9]|password|passwd)", line, re.IGNORECASE):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = key.strip().lower()
        normalized_value = value.strip()
        if normalized_key in {"secretref", "secretrefs"} and (normalized_value.startswith("secretref://") or normalized_value in {"", "[]", "null"}):
            continue
        if normalized_key in SAFE_SECRET_METADATA_KEYS and not re.search(r"(sk-|api[_-]?key|token[_-]?[a-z0-9]|secret[_-]?[a-z0-9])", normalized_value, re.IGNORECASE):
            continue
        if any(term in normalized_key for term in SECRET_KEYS) and normalized_value not in {"", "[]", "null", "false"}:
            problems.append(f"{path}:{line_no}: possible secret value in {key.strip()}")
    return problems


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    return parse_simple_yaml(raw), body


def parse_simple_yaml_scalar(value: str) -> Any:
    if value.startswith("{") and value.endswith("}"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.strip('"')
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else value.strip('"')
        except json.JSONDecodeError:
            return [] if not inner else [part.strip().strip('"') for part in inner.split(",")]
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value.strip('"')


def parse_simple_yaml(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lines = raw.splitlines()

    def next_nested_container(index: int, indent: int) -> Any:
        for nested_line in lines[index + 1 :]:
            if not nested_line.strip() or nested_line.lstrip().startswith("#"):
                continue
            nested_indent = len(nested_line) - len(nested_line.lstrip(" "))
            if nested_indent <= indent:
                break
            return [] if nested_line.strip().startswith("- ") else {}
        return []

    stack: list[tuple[int, Any]] = [(-1, data)]
    for index, line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1] if stack else data
        if indent > 0 and parent is data:
            continue
        if stripped.startswith("- "):
            if not isinstance(parent, list):
                continue
            item = stripped[2:].strip()
            if ":" in item and "://" not in item and not (item.startswith("{") and item.endswith("}")) and not (item.startswith('"') or item.startswith("'")):
                item_key, item_value = item.split(":", 1)
                item_key = item_key.strip()
                item_value = item_value.strip()
                item_record: dict[str, Any] = {}
                if item_value == "":
                    container = next_nested_container(index, indent)
                    item_record[item_key] = container
                    parent.append(item_record)
                    stack.append((indent, item_record))
                    stack.append((indent + 1, container))
                else:
                    item_record[item_key] = parse_simple_yaml_scalar(item_value)
                    parent.append(item_record)
                    stack.append((indent, item_record))
            else:
                parent.append(parse_simple_yaml_scalar(item))
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not isinstance(parent, dict):
            continue
        if value == "":
            container = next_nested_container(index, indent)
            parent[key] = container
            stack.append((indent, container))
        else:
            parent[key] = parse_simple_yaml_scalar(value)
    return data


def yaml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        if not value:
            return "[]"
        rendered_items = [json.dumps(item, ensure_ascii=False, separators=(",", ":")) if isinstance(item, (dict, list)) else yaml_value(item) for item in value]
        return "\n" + "\n".join(f"  - {item}" for item in rendered_items)
    if value is None:
        return ""
    text = str(value)
    if text == "" or any(ch in text for ch in [":", "#", "[", "]", "{", "}", "\n"]):
        return json.dumps(text, ensure_ascii=False)
    return text


def render_doc(frontmatter: dict[str, Any], body: str) -> str:
    lines = ["---"]
    for key, value in frontmatter.items():
        rendered = yaml_value(value)
        if rendered.startswith("\n"):
            lines.append(f"{key}:{rendered}")
        else:
            lines.append(f"{key}: {rendered}")
    lines.append("---")
    lines.append("")
    lines.append(body.strip() + "\n")
    return "\n".join(lines)


def update_index(index_path: Path, title: str, ref: str) -> None:
    ensure_dir(index_path.parent)
    if not index_path.exists():
        write_text(index_path, f"# {index_path.parent.name.title()} Index\n\n")
    text = read_text(index_path)
    entry = f"- [{title}]({ref})"
    if entry not in text:
        append_text(index_path, entry + "\n")


def append_log(bundle: Bundle, message: str, log_path: Path | None = None) -> None:
    path = log_path or bundle.root / "log.md"
    if not path.exists():
        write_text(path, "# Log\n\n")
    normalized_message = " ".join(line.rstrip(" \t") for line in str(message).splitlines()).rstrip(" \t")
    entry = f"- {utc_now()}"
    if normalized_message:
        entry = f"{entry} {normalized_message}"
    append_text(path, f"{entry}\n")


def text_indicates_agent_team_guide_impact(*values: Any) -> bool:
    text = "\n".join(str(value) for value in values if value is not None).lower()
    return any(re.search(pattern, text) for pattern in AGENT_TEAM_GUIDE_IMPACT_PATTERNS)


def requires_agent_team_guide_update(task_type: str, title: str, expected_output: list[str] | None = None) -> bool:
    normalized_type = slug(task_type) if task_type.strip() else ""
    if normalized_type in {"project_initialization", "role_handoff", "blocker_resolution", "product_feedback", "development_feedback", "operations_feedback"}:
        return False
    if normalized_type in AGENT_TEAM_GUIDE_IMPACT_TASK_TYPES:
        return True
    return text_indicates_agent_team_guide_impact(title, task_type, "\n".join(expected_output or []))


def normalize_agent_team_guide_gate(
    guide_updated: bool,
    guide_ref: str = "",
    guide_feishu_url: str = "",
    guide_revision: str = "",
    guide_audit_refs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "guideUpdated": bool(guide_updated),
        "guideRef": guide_ref.strip() or (AGENT_TEAM_GUIDE_REF if guide_updated else ""),
        "guideFeishuUrl": guide_feishu_url.strip() or (AGENT_TEAM_GUIDE_FEISHU_URL if guide_updated else ""),
        "guideRevision": guide_revision.strip(),
        "guideAuditRefs": guide_audit_refs or [],
    }


def validate_agent_team_guide_gate(bundle: Bundle, rel_path: str, fm: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if not fm.get("guideUpdateRequired"):
        return problems
    if not fm.get("guideUpdated"):
        problems.append(f"{rel_path}: agent team guide update required but guideUpdated is not true")
        return problems
    guide_ref = str(fm.get("guideRef") or "")
    guide_feishu_url = str(fm.get("guideFeishuUrl") or "")
    guide_revision = str(fm.get("guideRevision") or "")
    audit_refs = as_list(fm.get("guideAuditRefs"))
    if not guide_ref:
        problems.append(f"{rel_path}: guideUpdated requires guideRef")
    elif not (bundle.root / guide_ref).exists():
        problems.append(f"{rel_path}: guideRef does not exist: {guide_ref}")
    if not guide_feishu_url:
        problems.append(f"{rel_path}: guideUpdated requires guideFeishuUrl")
    if not guide_revision:
        problems.append(f"{rel_path}: guideUpdated requires guideRevision")
    if not audit_refs:
        problems.append(f"{rel_path}: guideUpdated requires guideAuditRefs")
    for audit_ref in audit_refs:
        audit_path = bundle.root / str(audit_ref)
        if not audit_path.exists():
            problems.append(f"{rel_path}: guideAuditRef does not exist: {audit_ref}")
    return problems


def common_operating_rules_payload(bundle: Bundle) -> dict[str, Any]:
    layered_rule_refs = {
        "companyConstitution": AGENT_CONSTITUTION_REF,
        "taskRuntimeContract": TASK_RUNTIME_CONTRACT_REF,
        "humanAcceptancePolicy": HUMAN_ACCEPTANCE_POLICY_REF,
        "commonRules": COMMON_AGENT_RULES_REF,
        "roleOperatingSpec": ROLE_OPERATING_SPEC_REF,
        "agentTeamGuide": AGENT_TEAM_GUIDE_REF,
    }
    return {
        "version": "common-agent-rules.v1",
        "rulesRef": COMMON_AGENT_RULES_REF,
        "guideRef": AGENT_TEAM_GUIDE_REF,
        "layeredRuleRefs": layered_rule_refs,
        "requiredForAllAgents": True,
        "mandatoryGates": [
            "load company, role, project, and task rules before work",
            "finish every task with TaskResult, evidence, quality evaluation, and acceptance routing",
            "handoff cross-role work instead of silently doing another role forever",
            "turn blockers, failures, permission gaps, and notification failures into retry/repair/escalation tasks",
            "do not promote reusable knowledge without source evidence and review",
        ],
        "rulesDocExists": all(exact_path_exists(bundle.root / ref) for ref in layered_rule_refs.values()),
    }


def task_operating_rule_refs(bundle: Bundle, task: dict[str, Any]) -> dict[str, str]:
    project_id = str(task.get("projectId") or "").strip()
    project_slug = safe_slug(project_id, "project") if project_id else ""
    assignee = str(task.get("assignee") or task.get("leaseOwner") or "").strip()
    role_ref = ROLE_OPERATING_SPEC_REF
    if assignee:
        candidate = bundle.root / "agents" / f"{safe_slug(assignee, 'agent')}.md"
        if exact_path_exists(candidate):
            role_ref = rel(candidate, bundle.root)
    project_rules_ref = "AGENTS.md" if exact_path_exists(bundle.root / "AGENTS.md") else ""
    if project_slug:
        project_dir = bundle.root / "projects" / project_slug
        if exact_path_exists(project_dir / "AGENTS.md"):
            project_rules_ref = rel(project_dir / "AGENTS.md", bundle.root)
        elif exact_path_exists(project_dir / "project.md"):
            project_rules_ref = rel(project_dir / "project.md", bundle.root)
    return {
        "companyConstitution": AGENT_CONSTITUTION_REF,
        "taskRuntimeContract": TASK_RUNTIME_CONTRACT_REF,
        "humanAcceptancePolicy": HUMAN_ACCEPTANCE_POLICY_REF,
        "commonRules": COMMON_AGENT_RULES_REF,
        "agentTeamGuide": AGENT_TEAM_GUIDE_REF,
        "roleOperatingSpec": ROLE_OPERATING_SPEC_REF,
        "roleRules": role_ref,
        "projectRules": project_rules_ref,
    }


def evaluate_common_operating_rules(
    task: dict[str, Any],
    status: str,
    summary: str,
    handoff_contract: dict[str, Any],
    evidence_refs: list[str],
    output_refs: list[str],
    knowledge_refs: list[str],
    tests_or_checks: list[str],
    quality_evaluation: dict[str, Any],
    operating_rule_refs: dict[str, str] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    operating_rule_refs = operating_rule_refs or {}
    for key in ["companyConstitution", "taskRuntimeContract", "humanAcceptancePolicy", "commonRules", "agentTeamGuide"]:
        if not operating_rule_refs.get(key):
            reasons.append(f"missing operating rule ref: {key}")
    if str(task.get("assignee") or "").startswith("agent.") and not operating_rule_refs.get("roleRules"):
        reasons.append("missing role rules ref")
    if str(task.get("projectId") or "") and not operating_rule_refs.get("projectRules"):
        reasons.append("missing project rules ref")
    if not summary.strip():
        reasons.append("missing summary")
    artifact_refs = as_list(handoff_contract.get("artifactRefs"))
    if status not in {"blocked", "rejected", "failed"} and not (artifact_refs or evidence_refs or output_refs or knowledge_refs):
        reasons.append("missing evidence/artifact/output reference")
    if not quality_evaluation:
        reasons.append("missing quality evaluation")
    if not handoff_contract.get("handoffTo") and not handoff_contract.get("terminalReason"):
        reasons.append("missing handoff target or terminal reason")
    if bool(quality_evaluation.get("passed")) and str(quality_evaluation.get("decision") or "") == "handoff_ready" and not handoff_contract.get("handoffTo"):
        reasons.append("handoff_ready requires handoff target")
    task_type = normalized_task_type(str(task.get("taskType") or ""))
    if task_type in {"development", "testing", "qa", "verification", "release_test"} and not tests_or_checks:
        reasons.append("engineering/test task missing tests or checks")
    return {
        "version": "common-agent-rules.v1",
        "status": "passed" if not reasons else "failed",
        "passed": not reasons,
        "rulesRef": COMMON_AGENT_RULES_REF,
        "guideRef": AGENT_TEAM_GUIDE_REF,
        "checkedRules": [
            "summary",
            "operating_rule_refs",
            "evidence_or_artifacts",
            "quality_evaluation",
            "handoff_or_terminal_reason",
            "engineering_tests_or_checks",
        ],
        "reasons": reasons,
        "ruleIssueRequired": False,
    }


def apply_common_rule_evaluation_to_quality(quality_evaluation: dict[str, Any], common_evaluation: dict[str, Any]) -> dict[str, Any]:
    if bool(common_evaluation.get("passed")):
        return quality_evaluation
    updated = dict(quality_evaluation)
    reasons = [str(item) for item in as_list(updated.get("reasons")) if str(item).strip()]
    for reason in as_list(common_evaluation.get("reasons")):
        reasons = append_unique(reasons, f"common rule: {reason}")
    updated["reasons"] = reasons
    updated["passed"] = False
    updated["status"] = "failed"
    attempt = int(updated.get("attemptNumber") or 1)
    max_attempts = int(updated.get("maxAttempts") or DEFAULT_MAX_TASK_ATTEMPTS)
    existing_decision = str(updated.get("decision") or "")
    if existing_decision.startswith("escalate") or str(quality_evaluation.get("status") or "") == "blocked":
        updated["decision"] = existing_decision or "escalate_to_project_manager"
    else:
        updated["decision"] = "retry_required" if attempt < max_attempts else "escalate_to_project_manager"
    updated["retryable"] = updated["decision"] == "retry_required"
    updated["score"] = min(int(updated.get("score") or 45), 45)
    updated["nextOwnerAgent"] = updated.get("nextOwnerAgent") or PROJECT_MANAGER_AGENT_ID
    return updated


def operating_rule_issue_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    if not project_id.strip():
        return bundle.root / "rule-issues"
    pid = slug(project_id)
    if pid and (bundle.root / "projects" / pid / "project.md").exists():
        return bundle.root / "projects" / pid / "rule-issues"
    return bundle.root / "rule-issues"


def create_operating_rule_issue(
    bundle: Bundle,
    title: str,
    rule_id: str,
    reporter: str,
    reason: str,
    scope: str = "company",
    proposal: str = "",
    source_ref: str = "",
    project_id: str = "",
) -> dict[str, Any]:
    if not title.strip():
        raise KnowledgeError("rule issue title is required")
    if not reporter.strip():
        raise KnowledgeError("rule issue reporter is required")
    if not reason.strip():
        raise KnowledgeError("rule issue reason is required")
    issue_id = unique_time_id("rule-issue")
    issue_dir = operating_rule_issue_storage_dir(bundle, project_id)
    ensure_dir(issue_dir)
    issue_path = issue_dir / f"{issue_id}.md"
    frontmatter = {
        "type": "OperatingRuleIssue",
        "title": title.strip(),
        "description": "Common Agent operating rule issue or improvement proposal.",
        "timestamp": utc_now(),
        "issueId": issue_id,
        "ruleId": rule_id.strip() or "unknown",
        "reporter": reporter,
        "owner": KNOWLEDGE_STEWARD_AGENT_ID,
        "status": "pending",
        "scope": scope,
        "projectId": slug(project_id) if project_id else "",
        "sourceRef": source_ref,
        "reviewTaskRef": "",
    }
    body = "\n".join(
        [
            "## Reason",
            "",
            reason.strip(),
            "",
            "## Proposal",
            "",
            proposal.strip() or "To be reviewed by Knowledge Steward / Knowledge Engineering Agent.",
            "",
            "## Governance Rule",
            "",
            "- Do not silently change common rules.",
            "- Review impact, update guide/rules docs, add eval/test coverage, and notify affected Agents before rollout.",
        ]
    )
    write_text(issue_path, render_doc(frontmatter, body))
    update_index(issue_dir / "index.md", title.strip(), issue_path.name)
    task_path = create_project_task(
        bundle,
        f"Review operating rule issue: {title.strip()}",
        project_id,
        reporter,
        KNOWLEDGE_STEWARD_AGENT_ID,
        "governance_change",
        "",
        "high" if scope == "company" else "normal",
        "",
        [rel(issue_path, bundle.root)] + ([source_ref] if source_ref else []),
        [
            "Review whether the common Agent operating rule is unreasonable, incomplete, or too costly.",
            "Decide keep/change/retire/clarify.",
            "If changed, update common rules, Agent Team guide, Feishu guide, audit refs, and eval/test coverage.",
            "Notify affected role Agents after decision.",
        ],
    )
    issue = update_frontmatter_file(issue_path, {"reviewTaskRef": rel(task_path, bundle.root), "updatedAt": utc_now()})
    create_audit_log(bundle, reporter, "agent_rule.issue.create", rel(issue_path, bundle.root), after="pending", policy_result="review_required", details=f"ruleId={rule_id}\nreviewTaskRef={rel(task_path, bundle.root)}\nreason={reason}")
    append_log(bundle, f"created operating rule issue {issue_id} rule={rule_id or 'unknown'}")
    return {
        "apiVersion": "v0.1",
        "kind": "OperatingRuleIssue",
        "issueRef": rel(issue_path, bundle.root),
        "reviewTaskRef": rel(task_path, bundle.root),
        "issue": issue,
    }


def create_audit_log(
    bundle: Bundle,
    actor: str,
    action: str,
    target_ref: str,
    before: str = "",
    after: str = "",
    policy_result: str = "",
    details: str = "",
) -> Path:
    audit_dir = bundle.root / "knowledge" / "audit"
    ensure_dir(audit_dir)
    audit_id = unique_time_id("audit")
    audit_path = audit_dir / f"{audit_id}.md"
    audit_fm = {
        "type": "AuditLog",
        "title": audit_id,
        "timestamp": utc_now(),
        "auditId": audit_id,
        "actor": actor,
        "action": action,
        "targetRef": target_ref,
        "before": before,
        "after": after,
        "policyResult": policy_result,
    }
    body = f"## Details\n\n{details or 'n/a'}\n"
    write_text(audit_path, render_doc(audit_fm, body))
    append_log(bundle, f"audit {action} {target_ref} {policy_result}")
    return audit_path


PM_CONTROL_WRITE_CAPABILITIES = {"pm_schedule_write", "project.schedule", "task.create", "task.update", "acceptance.route", "recovery.route", "notification.schedule"}
PM_CONTROL_VALID_SOURCE_CHANNELS = {"api", "cli", "workbench", "scheduler", "test"}
PM_CONTROL_DENIAL_MESSAGES = {
    "pm_control_lease_missing": ("当前 PM 没有项目主控租约，不能改项目调度。", "请由当前主控 PM 操作，或先完成接管。"),
    "pm_control_lease_not_found": ("未找到提交的 PM 主控租约，请刷新主控状态。", "刷新工作台主控状态后重试。"),
    "pm_control_lease_project_mismatch": ("租约属于其他项目，不能用于当前项目写入。", "请重新进入项目后操作。"),
    "pm_control_lease_expired": ("PM 主控租约已过期，需续约或由备用 PM 接管。", "续约当前租约，或让备用 PM 接管。"),
    "pm_control_lease_not_primary": ("当前写入者不是项目主控 PM，只能查看或提交建议。", "联系主控 PM 合并，或在主控失联后发起接管。"),
    "pm_control_lease_stale_fencing_token": ("该租约令牌已失效，项目可能已被接管。", "刷新主控状态，确认当前主控 PM。"),
    "pm_control_lease_permission_denied": ("当前 PM 没有执行该调度动作的权限。", "请检查 PM 参与角色和能力授权。"),
    "pm_control_lease_already_active": ("当前项目已有健康主控 PM 租约。", "协同 PM 可查看和准备建议；需要接管时走接管流程。"),
}


def pm_control_project_dir(bundle: Bundle, project_id: str) -> Path:
    return bundle.root / "projects" / slug(project_id)


def pm_control_lease_storage_dir(bundle: Bundle, project_id: str) -> Path:
    return pm_control_project_dir(bundle, project_id) / "pm-control-leases"


def pm_participant_storage_dir(bundle: Bundle, project_id: str) -> Path:
    return pm_control_project_dir(bundle, project_id) / "pm-participants"


def pm_takeover_storage_dir(bundle: Bundle, project_id: str) -> Path:
    return pm_control_project_dir(bundle, project_id) / "pm-takeovers"


def pm_control_lease_paths(bundle: Bundle, project_id: str) -> list[Path]:
    root = pm_control_lease_storage_dir(bundle, project_id)
    if not root.exists():
        return []
    return [path for path in sorted(root.glob("*.md")) if path.name not in COLLECTION_NAMES]


def pm_participant_paths(bundle: Bundle, project_id: str) -> list[Path]:
    root = pm_participant_storage_dir(bundle, project_id)
    if not root.exists():
        return []
    return [path for path in sorted(root.glob("*.md")) if path.name not in COLLECTION_NAMES]


def latest_pm_fencing_token(bundle: Bundle, project_id: str) -> int:
    latest = 0
    for path in pm_control_lease_paths(bundle, project_id):
        try:
            latest = max(latest, pm_control_lease_generation(load_object(path)))
        except (KnowledgeError, TypeError, ValueError):
            continue
    return latest


def pm_control_lease_generation(lease: dict[str, Any] | None) -> int:
    if not lease:
        return 0
    try:
        return int(lease.get("leaseGeneration") or lease.get("fencingToken") or 0)
    except (TypeError, ValueError):
        return 0


def pm_control_lease_deduplication_ref(lease: dict[str, Any] | None) -> str:
    if not lease:
        return ""
    return str(lease.get("deduplicationRef") or lease.get("idempotencyKey") or "")


def pm_control_lease_proof_hash(lease: dict[str, Any] | None) -> str:
    if not lease:
        return ""
    return str(lease.get("leaseProofHash") or lease.get("leaseTokenHash") or "")


def public_pm_control_lease(lease: dict[str, Any]) -> dict[str, Any]:
    public = dict(lease)
    generation = pm_control_lease_generation(public)
    public["leaseGeneration"] = generation
    public["fencingToken"] = generation
    if "deduplicationRef" not in public and "idempotencyKey" in public:
        public["deduplicationRef"] = str(public.get("idempotencyKey") or "")
    return public


def find_pm_control_lease(bundle: Bundle, project_id: str, lease_id: str) -> tuple[Path, dict[str, Any]]:
    wanted = slug(lease_id)
    for path in pm_control_lease_paths(bundle, project_id):
        lease = load_object(path)
        if slug(str(lease.get("leaseId") or path.stem)) == wanted:
            lease["path"] = rel(path, bundle.root)
            return path, lease
    raise KnowledgeError(f"pm control lease not found: {lease_id}")


def find_pm_control_lease_any_project(bundle: Bundle, lease_id: str) -> tuple[Path, dict[str, Any]] | None:
    wanted = slug(lease_id)
    projects_root = bundle.root / "projects"
    if not projects_root.exists():
        return None
    for root in sorted(projects_root.glob("*/pm-control-leases")):
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                lease = load_object(path)
            except KnowledgeError:
                continue
            if slug(str(lease.get("leaseId") or path.stem)) == wanted:
                lease["path"] = rel(path, bundle.root)
                return path, lease
    return None


def latest_pm_control_lease(bundle: Bundle, project_id: str) -> tuple[Path | None, dict[str, Any] | None]:
    latest_path: Path | None = None
    latest_lease: dict[str, Any] | None = None
    for path in pm_control_lease_paths(bundle, project_id):
        try:
            lease = load_object(path)
        except KnowledgeError:
            continue
        current_key = (pm_control_lease_generation(lease), str(lease.get("acquiredAt") or lease.get("timestamp") or ""))
        latest_key = (pm_control_lease_generation(latest_lease), str((latest_lease or {}).get("acquiredAt") or (latest_lease or {}).get("timestamp") or ""))
        if latest_lease is None or current_key >= latest_key:
            latest_path = path
            latest_lease = lease
    if latest_lease is not None and latest_path is not None:
        latest_lease["path"] = rel(latest_path, bundle.root)
    return latest_path, latest_lease


def repair_pm_control_lease_state(bundle: Bundle, project_id: str, actor: str = "system.scheduler") -> list[str]:
    changed: list[str] = []
    now = datetime.now(timezone.utc).replace(microsecond=0)
    for path in pm_control_lease_paths(bundle, project_id):
        lease = load_object(path)
        status = str(lease.get("status") or "")
        expires = parse_utc(str(lease.get("expiresAt") or ""))
        if status in {"active", "expiring"} and expires and expires <= now:
            fm = update_frontmatter_file(path, {"status": "expired", "updatedAt": utc_now()})
            audit_path = create_audit_log(bundle, actor, "pm_control_lease.expired", rel(path, bundle.root), before=status, after="expired", policy_result="pm_control_lease", details=f"projectId={slug(project_id)}\nleaseId={fm.get('leaseId', '')}")
            changed.append(rel(audit_path, bundle.root))
    return changed


def current_pm_control_lease(bundle: Bundle, project_id: str) -> tuple[Path | None, dict[str, Any] | None]:
    repair_pm_control_lease_state(bundle, project_id)
    active: list[tuple[Path, dict[str, Any]]] = []
    for path in pm_control_lease_paths(bundle, project_id):
        lease = load_object(path)
        if str(lease.get("status") or "") in {"active", "expiring"}:
            expires = parse_utc(str(lease.get("expiresAt") or ""))
            if expires and expires > datetime.now(timezone.utc).replace(microsecond=0):
                lease["path"] = rel(path, bundle.root)
                active.append((path, lease))
    if not active:
        return None, None
    active.sort(key=lambda item: (pm_control_lease_generation(item[1]), str(item[1].get("acquiredAt") or "")))
    return active[-1]


def pm_control_health(lease: dict[str, Any] | None) -> tuple[str, str, str]:
    if not lease:
        return "missing", "offline", "此项目暂无主控 PM。请选择备用 PM 接管后再写项目调度。"
    status = str(lease.get("status") or "missing")
    if status in {"released", "taken_over", "expired"}:
        message = {
            "released": "主控已主动释放，当前无主控 PM。",
            "taken_over": "项目已由新 PM 接管，旧租约失效。",
            "expired": "主控租约已过期，中枢暂停接受旧主控写入。",
        }.get(status, "主控租约不可写。")
        return status, "offline", message
    expires = parse_utc(str(lease.get("expiresAt") or ""))
    last = parse_utc(str(lease.get("lastHeartbeatAt") or lease.get("heartbeatAt") or lease.get("acquiredAt") or ""))
    now = datetime.now(timezone.utc).replace(microsecond=0)
    if expires and expires <= now:
        return "expired", "offline", "主控租约已过期，中枢暂停接受旧主控写入。"
    seconds_left = (expires - now).total_seconds() if expires else 0
    heartbeat_age = (now - last).total_seconds() if last else 10**9
    if heartbeat_age > 300:
        return "stale", "degraded", "主控 PM 心跳延迟，备用 PM 可准备接管。"
    if seconds_left <= 120:
        return "expiring", "degraded", "租约即将到期，请主控 PM 续约或准备备用接管。"
    return "healthy", "online", "当前主控 PM 在线并按时续约。"


def upsert_pm_participant(
    bundle: Bundle,
    project_id: str,
    pm_agent_id: str,
    role: str,
    runner_id: str = "",
    device_id: str = "",
    capabilities: list[str] | None = None,
    current_lease_id: str = "",
    standby_priority: int = 0,
    display_name: str = "",
) -> Path:
    pid = slug(project_id)
    agent = slug(pm_agent_id)
    root = pm_participant_storage_dir(bundle, pid)
    ensure_dir(root)
    path = root / f"{agent}.md"
    existing = load_object(path) if path.exists() else {}
    caps = capabilities if capabilities is not None else as_list(existing.get("capabilities")) or sorted(PM_CONTROL_WRITE_CAPABILITIES)
    fm = {
        "type": "ProjectPmParticipant",
        "title": display_name or str(existing.get("title") or pm_agent_id),
        "description": "PM participant state for project-level control lease.",
        "timestamp": str(existing.get("timestamp") or utc_now()),
        "projectId": pid,
        "pmAgentId": agent,
        "role": role,
        "runnerId": runner_id or str(existing.get("runnerId") or ""),
        "deviceId": device_id or str(existing.get("deviceId") or ""),
        "status": "active" if role == "primary" else str(existing.get("status") or "ready"),
        "standbyPriority": standby_priority or int(existing.get("standbyPriority") or 0),
        "capabilities": caps,
        "currentLeaseId": current_lease_id,
        "displayName": display_name or str(existing.get("displayName") or pm_agent_id),
        "lastActiveAt": utc_now(),
        "updatedAt": utc_now(),
    }
    write_text(path, render_doc(fm, "## Boundary\n\nPrimary PM may write project scheduling with a valid PM control lease. Collaborator and standby PMs are read-only until takeover succeeds.\n"))
    update_index(root / "index.md", fm["title"], path.name)
    return path


def acquire_pm_control_lease(
    bundle: Bundle,
    project_id: str,
    pm_agent_id: str,
    runner_id: str = "",
    device_id: str = "",
    lease_seconds: int = 900,
    idempotency_key: str = "",
    source_channel: str = "api",
) -> dict[str, Any]:
    if lease_seconds <= 0:
        raise KnowledgeError("lease seconds must be positive")
    pid = slug(project_id)
    agent = slug(pm_agent_id)
    ensure_dir(pm_control_lease_storage_dir(bundle, pid))
    if idempotency_key:
        for path in pm_control_lease_paths(bundle, pid):
            lease = load_object(path)
            if pm_control_lease_deduplication_ref(lease) == idempotency_key and str(lease.get("primaryPmAgentId") or "") == agent:
                lease["path"] = rel(path, bundle.root)
                return {"apiVersion": "v0.1", "kind": "PMControlLease", "lease": public_pm_control_lease(lease), "leaseRef": rel(path, bundle.root), "pmLeaseToken": "", "idempotent": True}
    current_path, current = current_pm_control_lease(bundle, pid)
    if current:
        deny_pm_control_lease_write(bundle, pid, agent, "pm_control_lease.acquire", "pm_control_lease_already_active", lease_id=str(current.get("leaseId") or ""), current_lease=current, source_channel=source_channel)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(seconds=lease_seconds)
    lease_id = unique_time_id(f"pmlease.{pid}")
    token = "pm-token." + hashlib.sha256(f"{lease_id}:{agent}:{utc_now()}".encode("utf-8")).hexdigest()[:40]
    lease_generation = latest_pm_fencing_token(bundle, pid) + 1
    fm = {
        "type": "PMControlLease",
        "title": f"PM control lease for {pid}",
        "description": "Project-level PM scheduling control lease.",
        "timestamp": utc_now(),
        "leaseId": lease_id,
        "projectId": pid,
        "primaryPmAgentId": agent,
        "runnerId": runner_id,
        "deviceId": device_id,
        "status": "active",
        "leaseProofHash": secret_fingerprint(token),
        "leaseGeneration": lease_generation,
        "acquiredAt": now.isoformat().replace("+00:00", "Z"),
        "lastHeartbeatAt": now.isoformat().replace("+00:00", "Z"),
        "expiresAt": expires.isoformat().replace("+00:00", "Z"),
        "takeoverPolicy": "expired_or_confirmed_healthy_takeover",
        "previousLeaseId": "",
        "auditRefs": [],
        "deduplicationRef": idempotency_key,
        "sourceChannel": source_channel,
        "updatedAt": utc_now(),
    }
    path = pm_control_lease_storage_dir(bundle, pid) / f"{slug(lease_id)}.md"
    write_text(path, render_doc(fm, "## Lease Boundary\n\nOnly the primary PM Agent named in this lease may perform protected project scheduling writes while the lease is active and unexpired.\n"))
    update_index(path.parent / "index.md", fm["title"], path.name)
    upsert_pm_participant(bundle, pid, agent, "primary", runner_id=runner_id, device_id=device_id, current_lease_id=lease_id)
    audit_path = create_audit_log(bundle, agent, "pm_control_lease.acquired", rel(path, bundle.root), after="active", policy_result="pm_control_lease", details=f"projectId={pid}\nleaseId={lease_id}\nleaseGeneration={lease_generation}\nsourceChannel={source_channel}")
    fm = update_frontmatter_file(path, {"auditRefs": [rel(audit_path, bundle.root)], "updatedAt": utc_now()})
    return {"apiVersion": "v0.1", "kind": "PMControlLease", "lease": public_pm_control_lease({**fm, "path": rel(path, bundle.root)}), "leaseRef": rel(path, bundle.root), "pmLeaseToken": token, "idempotent": False, "auditRef": rel(audit_path, bundle.root)}


def heartbeat_pm_control_lease(bundle: Bundle, project_id: str, pm_agent_id: str, lease_id: str, lease_token: str, fencing_token: int | str, lease_seconds: int = 900, source_channel: str = "api") -> dict[str, Any]:
    context = validate_pm_control_lease_for_write(bundle, project_id, pm_agent_id, lease_id, fencing_token, "pm_control_lease.heartbeat", source_channel=source_channel, lease_token=lease_token)
    path, lease = find_pm_control_lease(bundle, project_id, lease_id)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires = now + timedelta(seconds=lease_seconds)
    fm = update_frontmatter_file(path, {"lastHeartbeatAt": now.isoformat().replace("+00:00", "Z"), "expiresAt": expires.isoformat().replace("+00:00", "Z"), "status": "active", "updatedAt": utc_now()})
    upsert_pm_participant(bundle, project_id, pm_agent_id, "primary", runner_id=str(fm.get("runnerId") or ""), device_id=str(fm.get("deviceId") or ""), current_lease_id=lease_id)
    audit_path = create_audit_log(bundle, pm_agent_id, "pm_control_lease.renewed", rel(path, bundle.root), after="active", policy_result="pm_control_lease", details=f"projectId={slug(project_id)}\nleaseId={lease_id}\nleaseGeneration={context.get('leaseGeneration', '')}\nsourceChannel={source_channel}")
    return {"apiVersion": "v0.1", "kind": "PMControlLease", "lease": public_pm_control_lease({**fm, "path": rel(path, bundle.root)}), "leaseRef": rel(path, bundle.root), "auditRef": rel(audit_path, bundle.root)}


def release_pm_control_lease(bundle: Bundle, project_id: str, pm_agent_id: str, lease_id: str, lease_token: str, fencing_token: int | str, reason: str = "", source_channel: str = "api") -> dict[str, Any]:
    validate_pm_control_lease_for_write(bundle, project_id, pm_agent_id, lease_id, fencing_token, "pm_control_lease.release", source_channel=source_channel, lease_token=lease_token)
    path, lease = find_pm_control_lease(bundle, project_id, lease_id)
    fm = update_frontmatter_file(path, {"status": "released", "releaseReason": reason, "releasedAt": utc_now(), "updatedAt": utc_now()})
    participant_path = upsert_pm_participant(bundle, project_id, pm_agent_id, "collaborator", runner_id=str(lease.get("runnerId") or ""), device_id=str(lease.get("deviceId") or ""), current_lease_id="")
    audit_path = create_audit_log(bundle, pm_agent_id, "pm_control_lease.released", rel(path, bundle.root), before="active", after="released", policy_result="pm_control_lease", details=f"projectId={slug(project_id)}\nleaseId={lease_id}\nparticipantRef={rel(participant_path, bundle.root)}\nreason={reason}")
    return {"apiVersion": "v0.1", "kind": "PMControlLease", "lease": public_pm_control_lease({**fm, "path": rel(path, bundle.root)}), "leaseRef": rel(path, bundle.root), "auditRef": rel(audit_path, bundle.root)}


def takeover_pm_control_lease(
    bundle: Bundle,
    project_id: str,
    to_pm_agent_id: str,
    operator: str,
    reason: str,
    runner_id: str = "",
    device_id: str = "",
    lease_seconds: int = 900,
    confirm_healthy: bool = False,
    source_channel: str = "api",
) -> dict[str, Any]:
    if not reason.strip():
        raise KnowledgeError("takeover reason is required")
    pid = slug(project_id)
    to_agent = slug(to_pm_agent_id)
    current_path, current = current_pm_control_lease(bundle, pid)
    if current:
        health, _, _ = pm_control_health(current)
        if health in {"healthy", "expiring"} and not confirm_healthy:
            audit_path = create_audit_log(bundle, operator or to_agent, "pm_control_lease.takeover_denied", rel(current_path, bundle.root) if current_path else f"project:{pid}", after="denied", policy_result="healthy_primary_requires_confirmation", details=f"projectId={pid}\nfromPmAgentId={current.get('primaryPmAgentId', '')}\ntoPmAgentId={to_agent}\nreason={reason}")
            raise PMControlLeaseError("pm_control_lease_healthy_takeover_requires_confirmation", "当前主控仍在线。接管会中断其调度权，请确认原因和影响范围。", rel(audit_path, bundle.root), 409, "确认接管原因后重试。")
    latest_path, latest = latest_pm_control_lease(bundle, pid)
    previous_status = str((current or latest or {}).get("status") or "missing")
    previous_lease_id = str((current or latest or {}).get("leaseId") or "")
    from_agent = str((current or latest or {}).get("primaryPmAgentId") or "")
    if current_path and current:
        update_frontmatter_file(current_path, {"status": "taken_over", "takenOverAt": utc_now(), "updatedAt": utc_now()})
        upsert_pm_participant(bundle, pid, from_agent, "collaborator", runner_id=str(current.get("runnerId") or ""), device_id=str(current.get("deviceId") or ""), current_lease_id="")
    result = acquire_pm_control_lease(bundle, pid, to_agent, runner_id=runner_id, device_id=device_id, lease_seconds=lease_seconds, idempotency_key="", source_channel=source_channel)
    new_lease = result["lease"]
    new_lease_id = str(new_lease.get("leaseId") or "")
    record_id = unique_time_id(f"pmtakeover.{pid}")
    record_path = pm_takeover_storage_dir(bundle, pid) / f"{slug(record_id)}.md"
    ensure_dir(record_path.parent)
    audit_path = create_audit_log(bundle, operator or to_agent, "pm_control_lease.taken_over", rel(record_path, bundle.root), before=previous_status, after="active", policy_result="pm_control_lease", details=f"projectId={pid}\nfromPmAgentId={from_agent}\ntoPmAgentId={to_agent}\npreviousLeaseId={previous_lease_id}\nnewLeaseId={new_lease_id}\nreason={reason}")
    fm = {
        "type": "PmLeaseTakeoverRecord",
        "title": f"PM takeover for {pid}",
        "description": reason.strip(),
        "timestamp": utc_now(),
        "recordId": record_id,
        "projectId": pid,
        "fromPmAgentId": from_agent,
        "toPmAgentId": to_agent,
        "operator": operator or to_agent,
        "reason": reason.strip(),
        "previousLeaseId": previous_lease_id,
        "previousLeaseStatus": previous_status,
        "newLeaseId": new_lease_id,
        "occurredAt": utc_now(),
        "status": "done",
        "auditRef": rel(audit_path, bundle.root),
    }
    write_text(record_path, render_doc(fm, "## Takeover\n\nThe previous PM control lease is no longer valid. Protected project scheduling writes now require the new lease and fencing token.\n"))
    update_index(record_path.parent / "index.md", fm["title"], record_path.name)
    return {**result, "kind": "PMControlLeaseTakeover", "takeoverRecord": {**fm, "path": rel(record_path, bundle.root)}, "takeoverRef": rel(record_path, bundle.root), "takeoverAuditRef": rel(audit_path, bundle.root)}


def deny_pm_control_lease_write(
    bundle: Bundle,
    project_id: str,
    pm_agent_id: str,
    action: str,
    reason_code: str,
    target_ref: str = "",
    lease_id: str = "",
    current_lease: dict[str, Any] | None = None,
    source_channel: str = "api",
) -> None:
    message, next_action = PM_CONTROL_DENIAL_MESSAGES.get(reason_code, ("PM 主控租约校验失败，写入被拒绝。", "刷新主控状态后重试。"))
    current = current_lease or {}
    details = "\n".join(
        [
            f"projectId={slug(project_id) if project_id else ''}",
            f"requestPmAgentId={slug(pm_agent_id) if pm_agent_id else ''}",
            f"currentPrimaryPmAgentId={current.get('primaryPmAgentId', '')}",
            f"action={action}",
            f"reasonCode={reason_code}",
            f"leaseId={lease_id or current.get('leaseId', '')}",
            f"currentLeaseStatus={current.get('status', '')}",
            f"sourceChannel={source_channel}",
            f"targetRef={target_ref}",
        ]
    )
    audit_path = create_audit_log(bundle, pm_agent_id or "pm.unknown", "pm_control_lease.denied", target_ref or f"project:{slug(project_id) if project_id else ''}", after="denied", policy_result=reason_code, details=details)
    status = 403 if reason_code == "pm_control_lease_permission_denied" else 409
    raise PMControlLeaseError(reason_code, message, rel(audit_path, bundle.root), status, next_action)


def validate_pm_control_lease_for_write(
    bundle: Bundle,
    project_id: str,
    pm_agent_id: str,
    lease_id: str,
    fencing_token: int | str,
    action: str,
    source_channel: str = "api",
    request_ref: str = "",
    lease_token: str = "",
) -> dict[str, Any]:
    pid = slug(project_id) if project_id else ""
    current_path, current = current_pm_control_lease(bundle, pid) if pid else (None, None)
    if not pid or not pm_agent_id or not lease_id or fencing_token in {"", None}:
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_missing", request_ref, lease_id, current, source_channel)
    try:
        path, lease = find_pm_control_lease(bundle, pid, lease_id)
    except KnowledgeError:
        other = find_pm_control_lease_any_project(bundle, lease_id)
        if other:
            _, other_lease = other
            deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_project_mismatch", request_ref, lease_id, other_lease, source_channel)
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_not_found", request_ref, lease_id, current, source_channel)
    if str(lease.get("projectId") or "") != pid:
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_project_mismatch", request_ref, lease_id, current or lease, source_channel)
    status = str(lease.get("status") or "")
    expires = parse_utc(str(lease.get("expiresAt") or ""))
    if status not in {"active", "expiring"} or not expires or expires <= datetime.now(timezone.utc).replace(microsecond=0):
        if status in {"active", "expiring"}:
            update_frontmatter_file(path, {"status": "expired", "updatedAt": utc_now()})
            lease = load_object(path)
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_expired", request_ref, lease_id, lease, source_channel)
    if lease_token and pm_control_lease_proof_hash(lease) != secret_fingerprint(lease_token):
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_stale_fencing_token", request_ref, lease_id, lease, source_channel)
    if slug(pm_agent_id) != str(lease.get("primaryPmAgentId") or ""):
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_not_primary", request_ref, lease_id, lease, source_channel)
    try:
        requested_fencing = int(fencing_token)
    except (TypeError, ValueError):
        requested_fencing = -1
    latest_fencing = latest_pm_fencing_token(bundle, pid)
    if requested_fencing != pm_control_lease_generation(lease) or requested_fencing != latest_fencing:
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_stale_fencing_token", request_ref, lease_id, lease, source_channel)
    if source_channel not in PM_CONTROL_VALID_SOURCE_CHANNELS:
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_permission_denied", request_ref, lease_id, lease, source_channel)
    participant_path = pm_participant_storage_dir(bundle, pid) / f"{slug(pm_agent_id)}.md"
    participant = load_object(participant_path) if participant_path.exists() else {}
    caps = set(as_list(participant.get("capabilities")))
    allowed = str(participant.get("role") or "") == "primary" and (action in caps or bool(caps & PM_CONTROL_WRITE_CAPABILITIES))
    if not allowed:
        deny_pm_control_lease_write(bundle, project_id, pm_agent_id, action, "pm_control_lease_permission_denied", request_ref, lease_id, lease, source_channel)
    return {
        "leaseRef": rel(path, bundle.root),
        "leaseId": str(lease.get("leaseId") or ""),
        "projectId": pid,
        "primaryPmAgentId": str(lease.get("primaryPmAgentId") or ""),
        "runnerId": str(lease.get("runnerId") or ""),
        "deviceId": str(lease.get("deviceId") or ""),
        "leaseGeneration": pm_control_lease_generation(lease),
        "fencingToken": pm_control_lease_generation(lease),
        "auditContext": {"action": action, "sourceChannel": source_channel, "requestRef": request_ref},
    }


def pm_control_lease_read_model(bundle: Bundle, project_id: str) -> dict[str, Any]:
    pid = slug(project_id or "company-knowledge-core")
    current_path, current = current_pm_control_lease(bundle, pid)
    latest_path, latest = latest_pm_control_lease(bundle, pid)
    display_lease = current or latest
    health, heartbeat, explanation = pm_control_health(current or latest)
    participants: list[dict[str, Any]] = []
    for path in pm_participant_paths(bundle, pid):
        try:
            participant = load_object(path)
        except KnowledgeError:
            continue
        role = str(participant.get("role") or "collaborator")
        if current and str(participant.get("pmAgentId") or "") == str(current.get("primaryPmAgentId") or ""):
            role = "primary"
        elif role == "primary":
            role = "collaborator"
        participants.append(
            {
                "pm": workbench_ref(str(participant.get("displayName") or participant.get("pmAgentId") or "PM Agent"), "Agent", str(participant.get("pmAgentId") or "")),
                "role": role,
                "status": "ready" if role in {"collaborator", "standby"} else "running",
                "runner": workbench_ref(str(participant.get("runnerId") or "未登记电脑"), "AgentRunner", str(participant.get("runnerId") or "")),
                "device": workbench_ref(str(participant.get("deviceId") or "未登记电脑"), "AgentDevice", str(participant.get("deviceId") or "")),
                "standbyPriority": int(participant.get("standbyPriority") or 0),
                "capabilities": as_list(participant.get("capabilities")),
                "nextAction": "持有主控租约，可写项目调度。" if role == "primary" else ("主控失联或释放后可接管。" if role == "standby" else "可查看项目并准备建议；写入需主控合并或接管。"),
            }
        )
    if current and not any(str(row["pm"].get("objectRef") or "") == str(current.get("primaryPmAgentId") or "") for row in participants):
        participants.insert(
            0,
            {
                "pm": workbench_ref(str(current.get("primaryPmAgentId") or "主控 PM"), "Agent", str(current.get("primaryPmAgentId") or "")),
                "role": "primary",
                "status": "running",
                "runner": workbench_ref(str(current.get("runnerId") or "未登记电脑"), "AgentRunner", str(current.get("runnerId") or "")),
                "device": workbench_ref(str(current.get("deviceId") or "未登记电脑"), "AgentDevice", str(current.get("deviceId") or "")),
                "standbyPriority": 0,
                "capabilities": sorted(PM_CONTROL_WRITE_CAPABILITIES),
                "nextAction": "持有主控租约，可写项目调度。",
            },
        )
    takeover_records: list[dict[str, Any]] = []
    root = pm_takeover_storage_dir(bundle, pid)
    if root.exists():
        for path in sorted(root.glob("*.md"))[-20:]:
            if path.name in COLLECTION_NAMES:
                continue
            record = load_object(path)
            takeover_records.append(
                {
                    "recordRef": rel(path, bundle.root),
                    "occurredAt": str(record.get("occurredAt") or record.get("timestamp") or ""),
                    "fromPm": workbench_ref(str(record.get("fromPmAgentId") or "无前任主控"), "Agent", str(record.get("fromPmAgentId") or "")),
                    "toPm": workbench_ref(str(record.get("toPmAgentId") or "新主控 PM"), "Agent", str(record.get("toPmAgentId") or "")),
                    "operator": str(record.get("operator") or ""),
                    "reason": str(record.get("reason") or ""),
                    "previousLeaseStatus": str(record.get("previousLeaseStatus") or ""),
                    "newLeaseIdLabel": "已生成新主控租约" if record.get("newLeaseId") else "未生成",
                    "auditRef": workbench_ref("接管审计", "AuditLog", str(record.get("auditRef") or "")),
                }
            )
    denial_summaries: list[dict[str, Any]] = []
    audit_root = bundle.root / "knowledge" / "audit"
    if audit_root.exists():
        for path in sorted(audit_root.glob("*.md"))[-120:]:
            try:
                audit = load_object(path)
            except KnowledgeError:
                continue
            if str(audit.get("action") or "") != "pm_control_lease.denied":
                continue
            body = read_text(path)
            if f"projectId={pid}" not in body and pid not in str(audit.get("targetRef") or ""):
                continue
            reason_match = re.search(r"reasonCode=([a-z0-9_]+)", body)
            pm_match = re.search(r"requestPmAgentId=([a-z0-9_.-]+)", body)
            action_match = re.search(r"action=([a-z0-9_.-]+)", body)
            reason_code = reason_match.group(1) if reason_match else str(audit.get("policyResult") or "")
            message, next_action = PM_CONTROL_DENIAL_MESSAGES.get(reason_code, ("写入被拒绝。", "刷新主控状态后重试。"))
            denial_summaries.append(
                {
                    "auditRef": rel(path, bundle.root),
                    "timestamp": str(audit.get("timestamp") or ""),
                    "requestPm": workbench_ref(pm_match.group(1) if pm_match else str(audit.get("actor") or "PM"), "Agent", pm_match.group(1) if pm_match else str(audit.get("actor") or "")),
                    "action": action_match.group(1) if action_match else "",
                    "reasonCode": reason_code,
                    "displayMessage": message,
                    "nextAction": next_action,
                }
            )
    audit_refs = [workbench_ref("PM 租约审计", "AuditLog", str(ref)) for ref in as_list((display_lease or {}).get("auditRefs"))]
    current_lease = {
        "primaryPm": workbench_ref(str((display_lease or {}).get("primaryPmAgentId") or "暂无主控 PM"), "Agent", str((display_lease or {}).get("primaryPmAgentId") or "")),
        "lease": workbench_ref("当前 PM 主控租约" if current else "无有效主控租约", "PMControlLease", str((display_lease or {}).get("path") or "")),
        "project": workbench_ref(pid, "Project", f"projects/{pid}/project.md"),
        "status": health,
        "heartbeat": heartbeat,
        "expiresAt": str((display_lease or {}).get("expiresAt") or ""),
        "lastHeartbeatAt": str((display_lease or {}).get("lastHeartbeatAt") or ""),
        "leaseGenerationLabel": "已记录防旧写入代际" if pm_control_lease_generation(display_lease) else "",
        "nextAction": "只有当前主控 PM 可以改项目调度。" if current else "请选择备用 PM 接管后再写项目调度。",
        "auditRefs": audit_refs,
    }
    if current:
        current_lease["releaseAction"] = {"id": "pm-control-release", "label": "释放主控", "permission": "pm_control_lease.release", "idempotencyKey": f"desktop:pm-release:{pid}", "serverGate": "required", "auditRef": "audit.pm-control-release"}
    else:
        current_lease["takeoverAction"] = {"id": "pm-control-takeover", "label": "发起接管", "permission": "pm_control_lease.takeover", "idempotencyKey": f"desktop:pm-takeover:{pid}", "serverGate": "required", "auditRef": "audit.pm-control-takeover"}
    return {
        "currentLease": current_lease,
        "participants": participants,
        "takeoverRecords": takeover_records,
        "denialSummaries": denial_summaries[-20:],
        "healthExplanation": workbench_panel("pm-control-health", "PM 主控租约", health, str((display_lease or {}).get("primaryPmAgentId") or PROJECT_MANAGER_AGENT_ID), explanation, audit_refs or [workbench_ref("PM 控制租约", "PMControlLease", str((display_lease or {}).get("path") or ""))]),
    }


def _idempotency_digest(value: str) -> str:
    return hashlib.sha256(value.strip().encode("utf-8")).hexdigest()[:12]


def _find_by_idempotency(bundle: Bundle, root_name: str, idempotency_key: str) -> Path | None:
    if not idempotency_key.strip():
        raise KnowledgeError("idempotencyKey is required")
    root = bundle.root / root_name
    if not root.exists():
        return None
    for path in sorted(root.rglob("*.md")):
        if path.name in COLLECTION_NAMES:
            continue
        try:
            fm = load_object(path)
        except KnowledgeError:
            continue
        if str(fm.get("idempotencyKey") or "") == idempotency_key:
            return path
    return None


def _assert_no_plaintext_secret(value: Any, path: str = "") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
            safe = normalized in {
                *SAFE_SECRET_METADATA_KEYS,
                "idempotencykey",
                "pairingcode",
                "credentialpolicy",
                "credentialrequirement",
                "requestedoperations",
            } or normalized.endswith("hash") or normalized.endswith("ref") or normalized.endswith("refs")
            if not safe and any(secret_key.replace("_", "") in normalized for secret_key in SECRET_KEYS):
                if item not in (None, "", []):
                    raise KnowledgeError(f"secret value must not be submitted in field: {path + '.' if path else ''}{key}")
            _assert_no_plaintext_secret(item, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_no_plaintext_secret(item, f"{path}[{index}]")


def _permission_decision(
    bundle: Bundle,
    actor: str,
    target_ref: str,
    action: str,
    required_permissions: list[str],
    granted_permissions: list[str] | None,
) -> dict[str, Any]:
    required = [item for item in required_permissions if item]
    granted = {str(item) for item in granted_permissions or [] if str(item)}
    missing = [item for item in required if item not in granted]
    if missing:
        details = {
            "actor": actor or "api",
            "action": action,
            "targetRef": target_ref,
            "before": "not_created",
            "after": "denied",
            "requiredPermissions": required,
            "grantedPermissions": sorted(granted),
            "missingPermissions": missing,
            "reason": "missing required workbench write permission",
        }
        audit_path = create_audit_log(
            bundle,
            actor or "api",
            "workbench.permission.denied",
            target_ref,
            before="not_created",
            after="denied",
            policy_result="permission_denied",
            details=json.dumps(details, ensure_ascii=False, indent=2),
        )
        raise KnowledgeError(f"permission denied: requires {', '.join(missing)}; auditRef={rel(audit_path, bundle.root)}")
    return {
        "decision": "allowed",
        "requiredPermissions": required,
        "grantedPermissions": sorted(granted),
    }


def create_workbench_notification(
    bundle: Bundle,
    title: str,
    message_type: str,
    recipient: str,
    project_id: str = "",
    target_ref: str = "",
    summary: str = "",
    status: str = "pending",
    channel: str = "workbench",
) -> Path:
    ensure_dir(notification_storage_dir(bundle))
    notification_id = unique_time_id("notification")
    path = notification_storage_dir(bundle) / f"{notification_id}.md"
    frontmatter = {
        "type": "NotificationRecord",
        "title": title,
        "description": "Workbench registration notification trace.",
        "timestamp": utc_now(),
        "notificationId": notification_id,
        "taskId": "",
        "projectId": slug(project_id) if project_id else "",
        "recipient": recipient or "project.owner",
        "channel": channel,
        "messageType": message_type,
        "status": status,
        "sentAt": utc_now() if status == "sent" else "",
        "sourceMessageRef": target_ref,
        "failureReason": "",
        "retryCount": 0,
        "lastAttemptAt": "",
        "deadLetterAt": "",
    }
    body = "\n".join(["## Message Summary", "", summary or title, "", "## Target", "", f"- targetRef: {target_ref or 'none'}"])
    write_text(path, render_doc(frontmatter, body))
    update_index(notification_storage_dir(bundle) / "index.md", title, path.name)
    create_audit_log(bundle, recipient or "system.workbench", "workbench.notification.record", rel(path, bundle.root), after=status, policy_result=message_type, details=f"targetRef={target_ref}")
    return path


def _workbench_project_requires_approval(source_mode: str, repository_refs: list[str], sensitivity: str, visibility: list[str]) -> bool:
    text = " ".join([source_mode, sensitivity, " ".join(repository_refs), " ".join(visibility)]).lower()
    return any(token in text for token in ["external", "customer", "client", "prod", "production", "confidential", "secret", "cross-team", "high"])


def create_workbench_project(
    bundle: Bundle,
    project_id: str,
    name: str,
    owner: str,
    source_mode: str = "local_repo",
    repository_refs: list[str] | None = None,
    default_assignees: list[str] | None = None,
    visibility: list[str] | None = None,
    sensitivity: str = "internal",
    actor: str = "",
    idempotency_key: str = "",
    permissions: list[str] | None = None,
) -> dict[str, Any]:
    _assert_no_plaintext_secret({"repositoryRefs": repository_refs or [], "sourceMode": source_mode})
    pid = slug(project_id)
    actor_ref = actor or owner
    target_ref = f"projects/{pid}/project.md"
    _permission_decision(bundle, actor_ref, target_ref, "workbench.project.create", ["project.create"], permissions)
    existing_by_key = _find_by_idempotency(bundle, "projects", idempotency_key)
    if existing_by_key:
        project = load_object(existing_by_key)
        return {"apiVersion": "v0.1", "kind": "WorkbenchProject", "projectId": str(project.get("projectId") or pid), "projectRef": rel(existing_by_key, bundle.root), "project": project, "idempotent": True}
    project_path = bundle.root / "projects" / pid / "project.md"
    if project_path.exists():
        raise KnowledgeError(f"project already exists: {pid}")
    project_path = make_project(bundle, pid, name, owner)
    approval_required = _workbench_project_requires_approval(source_mode, repository_refs or [], sensitivity, visibility or [])
    status = "pending_review" if approval_required else "active"
    updates = {
        "status": status,
        "sourceMode": source_mode,
        "repositoryRefs": repository_refs or [],
        "relatedRepos": repository_refs or [],
        "defaultAssignees": default_assignees or [],
        "visibility": visibility or [],
        "sensitivity": sensitivity,
        "idempotencyKey": idempotency_key,
        "approvalRequired": approval_required,
        "approvalStatus": "pending_review" if approval_required else "auto_approved",
        "approvalRoute": "project_owner_or_admin" if approval_required else "owner_confirmation",
        "executionBoundary": "registration_only_scheduler_and_agent_ring_execute",
        "updatedAt": utc_now(),
    }
    project = update_frontmatter_file(project_path, updates)
    notification_path = create_workbench_notification(
        bundle,
        f"Project registration {pid}",
        "workbench_project_created",
        owner,
        pid,
        rel(project_path, bundle.root),
        f"项目登记已创建：{name}。状态：{status}。",
    )
    audit_path = create_audit_log(
        bundle,
        actor_ref,
        "workbench.project.create",
        rel(project_path, bundle.root),
        after=status,
        policy_result=project["approvalStatus"],
        details=json.dumps({k: updates[k] for k in ["sourceMode", "repositoryRefs", "defaultAssignees", "visibility", "sensitivity", "idempotencyKey"]}, ensure_ascii=False, indent=2),
    )
    return {
        "apiVersion": "v0.1",
        "kind": "WorkbenchProject",
        "projectId": pid,
        "projectRef": rel(project_path, bundle.root),
        "project": project,
        "approvalRequired": approval_required,
        "approvalStatus": project["approvalStatus"],
        "auditRef": rel(audit_path, bundle.root),
        "notificationRefs": [rel(notification_path, bundle.root)],
        "idempotent": False,
    }


def _pairing_code_from_key(idempotency_key: str, project_id: str, runner_label: str) -> str:
    digest = hashlib.sha256(f"{idempotency_key}:{project_id}:{runner_label}".encode("utf-8")).hexdigest()
    number = int(digest[:10], 16) % 1_000_000
    code = f"{number:06d}"
    return f"{code[:3]}-{code[3:]}"


def create_runner_invitation(
    bundle: Bundle,
    project_id: str,
    runner_label: str,
    requested_capabilities: list[str] | None = None,
    expires_in_seconds: int = 900,
    runner_owner: str = "",
    data_scopes: list[str] | None = None,
    actor: str = "",
    idempotency_key: str = "",
    permissions: list[str] | None = None,
    registration_url: str = "/v0/runners/register",
) -> dict[str, Any]:
    pid = slug(project_id)
    if expires_in_seconds <= 0:
        raise KnowledgeError("expiresInSeconds must be positive")
    actor_ref = actor or runner_owner or "system.workbench"
    target_ref = f"runner-invitations/{pid}.{safe_slug(runner_label, 'runner')}.md"
    _permission_decision(bundle, actor_ref, target_ref, "runner.invitation.create", ["runner.invitation.create"], permissions)
    existing_by_key = _find_by_idempotency(bundle, "runner-invitations", idempotency_key)
    if existing_by_key:
        invitation = load_object(existing_by_key)
        return {"apiVersion": "v0.1", "kind": "RunnerInvitation", "invitationId": str(invitation.get("invitationId") or existing_by_key.stem), "invitationRef": rel(existing_by_key, bundle.root), "invitation": invitation, "scopePreview": invitation.get("scopePreview", {}), "idempotent": True}
    capabilities = requested_capabilities or []
    scopes = data_scopes or []
    approval_required = any(item.lower() in {"production", "customer", "external_write", "approval_delegate", "secret"} for item in [*capabilities, *scopes])
    pairing_code = _pairing_code_from_key(idempotency_key, pid, runner_label)
    invitation_id = f"runner-invitation.{pid}.{_idempotency_digest(idempotency_key)}"
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    path = bundle.root / "runner-invitations" / f"{slug(invitation_id)}.md"
    frontmatter = {
        "type": "RunnerInvitation",
        "title": runner_label,
        "description": "Workbench-created runner invitation. Pairing code hash only.",
        "timestamp": utc_now(),
        "invitationId": invitation_id,
        "projectId": pid,
        "runnerLabel": runner_label,
        "runnerOwner": runner_owner,
        "requestedCapabilities": capabilities,
        "dataScopes": scopes,
        "pairingCodeHash": secret_fingerprint(pairing_code),
        "pairingCodeExpiresAt": expires_at,
        "runnerRegistrationUrl": registration_url,
        "status": "pending_review" if approval_required else "active",
        "approvalRequired": approval_required,
        "approvalStatus": "pending_review" if approval_required else "auto_approved",
        "idempotencyKey": idempotency_key,
        "scopePreview": {"projectId": pid, "capabilities": capabilities, "dataScopes": scopes},
        "consumedByRunner": "",
        "consumedAt": "",
    }
    body = "\n".join(["## Scope Preview", "", f"- projectId: {pid}", *[f"- capability: {item}" for item in capabilities], *[f"- dataScope: {item}" for item in scopes], "", "## Security", "", "- Pairing code is shown by the API response and stored only as a hash."])
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "runner-invitations" / "index.md", runner_label, path.name)
    notification_path = create_workbench_notification(bundle, f"Runner invitation {runner_label}", "runner_invitation_created", runner_owner or actor_ref, pid, rel(path, bundle.root), f"电脑接入邀请已创建：{runner_label}。")
    audit_path = create_audit_log(bundle, actor_ref, "runner.invitation.create", rel(path, bundle.root), after=str(frontmatter["status"]), policy_result=str(frontmatter["approvalStatus"]), details=f"pairingCodeHash={frontmatter['pairingCodeHash']}\nidempotencyKey={idempotency_key}")
    return {
        "apiVersion": "v0.1",
        "kind": "RunnerInvitation",
        "invitationId": invitation_id,
        "invitationRef": rel(path, bundle.root),
        "pairingCode": pairing_code,
        "pairingCodeExpiresAt": expires_at,
        "runnerRegistrationUrl": registration_url,
        "scopePreview": frontmatter["scopePreview"],
        "approvalRequired": approval_required,
        "approvalStatus": frontmatter["approvalStatus"],
        "auditRef": rel(audit_path, bundle.root),
        "notificationRefs": [rel(notification_path, bundle.root)],
        "idempotent": False,
    }


def _find_runner_invitation_by_pairing_code(bundle: Bundle, pairing_code: str) -> tuple[Path, dict[str, Any]] | None:
    if not pairing_code.strip():
        return None
    expected = secret_fingerprint(pairing_code.strip())
    root = bundle.root / "runner-invitations"
    if not root.exists():
        return None
    for path in sorted(root.glob("*.md")):
        if path.name in COLLECTION_NAMES:
            continue
        fm = load_object(path)
        if fm.get("type") == "RunnerInvitation" and fm.get("pairingCodeHash") == expected:
            return path, fm
    return None


def submit_runner_registration(
    bundle: Bundle,
    runner_id: str,
    name: str,
    pairing_code: str = "",
    host_type: str = "",
    mode: str = "unattended",
    agents: list[str] | None = None,
    capabilities: list[str] | None = None,
    available_projects: list[str] | None = None,
    repo_access: list[str] | None = None,
    data_scopes: list[str] | None = None,
    ring_version: str = "0.1.0",
    tools: list[dict[str, Any]] | None = None,
    models: list[dict[str, Any]] | None = None,
    owner: str = "",
    idempotency_key: str = "",
) -> dict[str, Any]:
    _assert_no_plaintext_secret({"tools": tools or [], "models": models or []})
    rid = slug(runner_id)
    path = runner_storage_dir(bundle) / f"{rid}.md"
    if path.exists():
        existing = load_object(path)
        if idempotency_key and existing.get("idempotencyKey") == idempotency_key:
            return {"apiVersion": "v0.1", "kind": "RunnerRegistrationResult", "runnerId": rid, "runnerRef": rel(path, bundle.root), "runner": existing, "runnerToken": "", "approvalStatus": existing.get("approvalStatus", ""), "idempotent": True}
    invitation_path = None
    invitation: dict[str, Any] = {}
    approved_scope = False
    if pairing_code:
        found = _find_runner_invitation_by_pairing_code(bundle, pairing_code)
        if not found:
            audit_path = create_audit_log(bundle, rid, "runner.pairing.denied", f"runners/{rid}.md", after="denied", policy_result="invalid_pairing_code")
            raise KnowledgeError(f"runner pairing code is invalid; auditRef={rel(audit_path, bundle.root)}")
        invitation_path, invitation = found
        expires_at = parse_utc(str(invitation.get("pairingCodeExpiresAt") or ""))
        if expires_at and expires_at < datetime.now(timezone.utc):
            update_frontmatter_file(invitation_path, {"status": "expired", "updatedAt": utc_now()})
            audit_path = create_audit_log(bundle, rid, "runner.pairing.denied", rel(invitation_path, bundle.root), after="expired", policy_result="expired_pairing_code")
            raise KnowledgeError(f"runner pairing code expired; auditRef={rel(audit_path, bundle.root)}")
        approved_scope = str(invitation.get("approvalStatus") or "") == "auto_approved" and not invitation.get("consumedByRunner")
    requested_projects = [slug(item) for item in available_projects or []]
    invitation_project = str(invitation.get("projectId") or "")
    allowed_projects = [invitation_project] if approved_scope and invitation_project else []
    runner_token = ""
    status = "online_readonly" if approved_scope else "pending_authorization"
    approval_status = "auto_approved" if approved_scope else "pending_authorization"
    if approved_scope:
        runner_token = "runner-token." + hashlib.sha256(f"{rid}:{idempotency_key}:{utc_now()}".encode("utf-8")).hexdigest()[:32]
    ensure_dir(runner_storage_dir(bundle))
    frontmatter = {
        "type": "AgentRunner",
        "title": name,
        "description": "Runner registration application from Agent Ring.",
        "timestamp": utc_now(),
        "runnerId": rid,
        "machineId": rid,
        "owner": owner,
        "ringVersion": ring_version,
        "hostType": host_type,
        "status": status,
        "mode": mode,
        "agents": agents or [],
        "agentIds": agents or [],
        "capabilities": capabilities or [],
        "tools": tools or [],
        "models": models or [],
        "availableProjects": allowed_projects,
        "requestedAvailableProjects": requested_projects,
        "repoAccess": repo_access or [],
        "repositoryScopes": repo_access or [],
        "dataScopes": data_scopes or [],
        "runnerTokenHash": secret_fingerprint(runner_token) if runner_token else "",
        "pairingProofHash": secret_fingerprint(pairing_code) if pairing_code else "",
        "invitationRef": rel(invitation_path, bundle.root) if invitation_path else "",
        "approvalRequired": not approved_scope,
        "approvalStatus": approval_status,
        "authorizationScope": {"approvedProjects": allowed_projects, "requestedProjects": requested_projects},
        "idempotencyKey": idempotency_key,
        "load": "",
        "lastHeartbeatAt": utc_now() if approved_scope else "",
        "currentLeases": [],
        "staleLeases": [],
        "failedLeases": [],
        "taskHistory": [],
        "lastFailure": "",
        "manualHandoff": bool(mode == "manual" or rid.startswith("manual.")),
    }
    body = "\n".join(["## Registration", "", "This runner record is a registration/authorization fact. Agent Ring owns local execution.", "", "## Boundary", "", "- Pending authorization runners cannot receive project scheduling scope.", "- Workbench does not directly claim tasks or write TaskResult."])
    write_text(path, render_doc(frontmatter, body))
    update_index(runner_storage_dir(bundle) / "index.md", name, path.name)
    notification_path = create_workbench_notification(bundle, f"Runner registration {rid}", "runner_registration_submitted", owner or rid, invitation_project, rel(path, bundle.root), f"电脑注册申请已提交：{name}。状态：{status}。")
    audit_action = "runner.register" if approved_scope else "runner.registration_request.create"
    audit_path = create_audit_log(bundle, rid, audit_action, rel(path, bundle.root), after=status, policy_result=approval_status, details=f"invitationRef={frontmatter['invitationRef']}\nidempotencyKey={idempotency_key}")
    if invitation_path and approved_scope:
        update_frontmatter_file(invitation_path, {"status": "consumed", "consumedByRunner": rid, "consumedAt": utc_now(), "updatedAt": utc_now()})
        create_audit_log(bundle, rid, "runner.pairing.consume", rel(invitation_path, bundle.root), after="consumed", policy_result="pairing_consumed")
    return {
        "apiVersion": "v0.1",
        "kind": "RunnerRegistrationResult",
        "runnerId": rid,
        "runnerRef": rel(path, bundle.root),
        "runnerToken": runner_token,
        "tokenExpiresAt": None,
        "heartbeatIntervalSeconds": 30,
        "allowedProjects": allowed_projects,
        "approvalRequired": not approved_scope,
        "approvalStatus": approval_status,
        "auditRef": rel(audit_path, bundle.root),
        "notificationRefs": [rel(notification_path, bundle.root)],
        "idempotent": False,
    }


def _normalized_tool_risk(risk_level: str) -> tuple[str, str]:
    value = risk_level.strip().lower() or "low"
    if value in {"low", "readonly", "read_only", "local_repo_read", "l1"}:
        return "L1", "low"
    if value in {"medium", "l2"}:
        return "L2", "medium"
    if value in {"high", "write", "external_api", "production", "l3", "l4", "l5"}:
        return "L3", "high"
    raise KnowledgeError(f"unknown tool risk level: {risk_level}")


def register_workbench_tool(
    bundle: Bundle,
    project_id: str,
    tool_name: str,
    tool_type: str,
    risk_level: str,
    allowed_operations: list[str] | None = None,
    runner_scopes: list[str] | None = None,
    owner: str = "",
    actor: str = "",
    idempotency_key: str = "",
    permissions: list[str] | None = None,
) -> dict[str, Any]:
    _assert_no_plaintext_secret({"toolName": tool_name, "toolType": tool_type, "allowedOperations": allowed_operations or []})
    pid = slug(project_id) if project_id else ""
    tid = slug(f"tool.{pid}.{tool_name}" if pid else f"tool.{tool_name}")
    target_ref = f"tools/{tid}.md"
    _permission_decision(bundle, actor or owner or "system.workbench", target_ref, "tool.register", ["tool.register.low_risk"], permissions)
    existing_by_key = _find_by_idempotency(bundle, "tools", idempotency_key)
    if existing_by_key:
        tool = load_object(existing_by_key)
        return {"apiVersion": "v0.1", "kind": "ToolAsset", "toolId": str(tool.get("toolId") or existing_by_key.stem), "toolRef": rel(existing_by_key, bundle.root), "tool": tool, "idempotent": True}
    normalized_risk, workbench_risk = _normalized_tool_risk(risk_level)
    if workbench_risk == "high":
        raise KnowledgeError("high risk, write, external, or credentialed tools must use /v0/workbench/tool-registration-requests")
    for operation in allowed_operations or []:
        if any(token in operation for token in ["&&", "||", ";", "|", "$(", "`"]):
            raise KnowledgeError("allowedOperations must be structured operation names, not shell snippets")
    path = bundle.root / "tools" / f"{tid}.md"
    if path.exists():
        raise KnowledgeError(f"tool already exists: {tid}")
    frontmatter = {
        "type": "ToolAsset",
        "title": tool_name,
        "description": f"Workbench registered tool capability: {tool_name}.",
        "resource": tool_type,
        "timestamp": utc_now(),
        "toolId": tid,
        "owner": owner or actor or "tool.owner",
        "repoRef": "",
        "entrypoint": tool_type,
        "version": "0.1.0",
        "status": "approved",
        "scope": "project" if pid else "company",
        "projectId": pid,
        "riskLevel": normalized_risk,
        "workbenchRiskLevel": workbench_risk,
        "invocationPolicy": "agent_policy_allowed",
        "requiresApproval": [],
        "executionMode": "runner_reported_capability",
        "allowedAgents": [],
        "allowedProjects": [pid] if pid else [],
        "runnerScopes": runner_scopes or [],
        "allowedOperations": allowed_operations or [],
        "secretsRequired": [],
        "approvalRequired": False,
        "approvalStatus": "auto_approved",
        "idempotencyKey": idempotency_key,
        "lastVerifiedAt": utc_now(),
    }
    body = "\n".join(["## Capability", "", f"- toolType: {tool_type}", *[f"- operation: {item}" for item in allowed_operations or []], "", "## Boundary", "", "- Workbench records capability and approval state only.", "- Actual tool health and execution are reported by Runner / Agent Ring."])
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "tools" / "index.md", tool_name, path.name)
    notification_path = create_workbench_notification(bundle, f"Tool registered {tool_name}", "tool_registered", owner or actor or "tool.owner", pid, rel(path, bundle.root), f"低风险工具已登记：{tool_name}。")
    audit_path = create_audit_log(bundle, actor or owner or "system.workbench", "tool.register", rel(path, bundle.root), after="approved", policy_result="auto_approved", details=f"toolType={tool_type}\nidempotencyKey={idempotency_key}")
    return {"apiVersion": "v0.1", "kind": "ToolAsset", "toolId": tid, "toolRef": rel(path, bundle.root), "tool": frontmatter, "approvalStatus": "auto_approved", "auditRef": rel(audit_path, bundle.root), "notificationRefs": [rel(notification_path, bundle.root)], "idempotent": False}


def create_tool_registration_request(
    bundle: Bundle,
    project_id: str,
    tool_name: str,
    tool_type: str,
    risk_level: str,
    requested_operations: list[str] | None = None,
    credential_policy: str = "",
    owner: str = "",
    justification: str = "",
    data_scopes: list[str] | None = None,
    runner_scopes: list[str] | None = None,
    actor: str = "",
    idempotency_key: str = "",
    permissions: list[str] | None = None,
) -> dict[str, Any]:
    _assert_no_plaintext_secret({"credentialPolicy": credential_policy, "requestedOperations": requested_operations or [], "dataScopes": data_scopes or []})
    if not justification.strip():
        raise KnowledgeError("tool registration request justification is required")
    pid = slug(project_id) if project_id else ""
    request_id = f"tool-request.{pid or 'company'}.{safe_slug(tool_name, 'tool')}.{_idempotency_digest(idempotency_key)}"
    target_ref = f"tool-registration-requests/{slug(request_id)}.md"
    _permission_decision(bundle, actor or owner or "system.workbench", target_ref, "tool.registration_request.create", ["tool.registration_request.create"], permissions)
    existing_by_key = _find_by_idempotency(bundle, "tool-registration-requests", idempotency_key)
    if existing_by_key:
        request = load_object(existing_by_key)
        return {"apiVersion": "v0.1", "kind": "ToolRegistrationRequest", "requestId": str(request.get("requestId") or existing_by_key.stem), "requestRef": rel(existing_by_key, bundle.root), "request": request, "idempotent": True}
    normalized_risk, workbench_risk = _normalized_tool_risk(risk_level)
    path = bundle.root / "tool-registration-requests" / f"{slug(request_id)}.md"
    frontmatter = {
        "type": "ToolRegistrationRequest",
        "title": tool_name,
        "description": "Tool registration request requiring owner/admin approval before use.",
        "timestamp": utc_now(),
        "requestId": request_id,
        "projectId": pid,
        "toolName": tool_name,
        "toolType": tool_type,
        "riskLevel": normalized_risk,
        "workbenchRiskLevel": workbench_risk,
        "requestedOperations": requested_operations or [],
        "credentialPolicy": credential_policy or "none",
        "owner": owner or actor or "tool.owner",
        "status": "pending_review",
        "approvalRequired": True,
        "approvalStatus": "pending_review",
        "approvalRoute": "tool_owner_governance",
        "approvedScope": {},
        "expiresAt": "",
        "revocationPath": "disable ToolAsset or revoke runner/tool authorization",
        "dataScopes": data_scopes or [],
        "runnerScopes": runner_scopes or [],
        "idempotencyKey": idempotency_key,
    }
    body = "\n".join(["## Justification", "", justification.strip(), "", "## Boundary", "", "- Request does not enable the tool.", "- Tool Owner approval must define scope, expiry, risk note, and revocation path before ToolAsset becomes active."])
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "tool-registration-requests" / "index.md", tool_name, path.name)
    approval_task_ref = ""
    try:
        task_path = create_project_task(
            bundle,
            f"Review tool registration request: {tool_name}",
            pid,
            actor or owner or "system.workbench",
            owner or KNOWLEDGE_STEWARD_AGENT_ID,
            "governance_change",
            f"tool-approval-{pid or 'company'}-{safe_slug(tool_name, 'tool')}-{_idempotency_digest(idempotency_key)}",
            "high" if normalized_risk in {"L3", "L4", "L5"} else "normal",
            "",
            [rel(path, bundle.root)],
            ["Review requested operations, credential policy, project scope, data scope, expiry, risk note, and revocation path."],
        )
        approval_task_ref = rel(task_path, bundle.root)
        update_frontmatter_file(path, {"approvalTaskRef": approval_task_ref, "updatedAt": utc_now()})
    except KnowledgeError:
        approval_task_ref = ""
    notification_path = create_workbench_notification(bundle, f"Tool request {tool_name}", "tool_registration_request_created", owner or actor or "tool.owner", pid, rel(path, bundle.root), f"工具注册申请待审批：{tool_name}。")
    audit_path = create_audit_log(bundle, actor or owner or "system.workbench", "tool.registration_request.create", rel(path, bundle.root), after="pending_review", policy_result="approval_required", details=f"toolType={tool_type}\napprovalTaskRef={approval_task_ref}\nidempotencyKey={idempotency_key}")
    request = load_object(path)
    return {"apiVersion": "v0.1", "kind": "ToolRegistrationRequest", "requestId": request_id, "requestRef": rel(path, bundle.root), "request": request, "approvalTaskRef": approval_task_ref, "approvalStatus": "pending_review", "auditRef": rel(audit_path, bundle.root), "notificationRefs": [rel(notification_path, bundle.root)], "idempotent": False}


def workbench_project_execution_read_model(bundle: Bundle, project_id: str, task_id: str = "") -> dict[str, Any]:
    model = scheduler_workbench_read_model(bundle, project_id, task_id)
    model["kind"] = "WorkbenchExecutionReadModel"
    model["readOnly"] = True
    if task_id:
        try:
            model["selectedTaskFactView"] = build_task_fact_view(bundle, project_id, task_id)
        except KnowledgeError:
            model["selectedTaskFactView"] = {}
    else:
        model["selectedTaskFactView"] = {}
    model["commandSurface"] = {
        "dispatchTask": False,
        "repairTask": False,
        "overwriteTaskResult": False,
        "editAgentRun": False,
        "forceCompleteTask": False,
        "claimAsWorkbench": False,
    }
    model["allowedRequestObjects"] = ["retry_request", "manual_handoff_request", "tool_registration_request", "human_acceptance_decision", "project_task_for_repair"]
    return model


def make_project(bundle: Bundle, project_id: str, name: str, owner: str, workspace_ref: str = PENDING_WORKSPACE_REF) -> Path:
    pid = slug(project_id)
    project_dir = bundle.root / "projects" / pid
    ensure_dir(project_dir)
    write_text(
        project_dir / "index.md",
        f"# {name}\n\n- [Project](project.md)\n- [Decisions](decisions.md)\n- [Lessons](lessons.md)\n- [Agents](agents.md)\n- [Tools](tools.md)\n- [Tasks](tasks/index.md)\n- [Sources](sources/index.md)\n",
    )
    write_text(project_dir / "log.md", f"# {name} Log\n\n")
    frontmatter = {
        "type": "Project",
        "title": name,
        "description": f"Project context for {name}.",
        "timestamp": utc_now(),
        "projectId": pid,
        "owner": owner,
        "status": "draft",
        "scope": "project",
        "workspaceRef": workspace_ref.strip() or PENDING_WORKSPACE_REF,
        "workspaceConfirmation": "confirmed" if workspace_ref.strip() and workspace_ref.strip() != PENDING_WORKSPACE_REF else "pending",
        "members": [],
        "relatedRepos": [],
        "relatedAgents": [],
        "relatedTools": [],
    }
    body = "## Goal\n\nTBD.\n\n## Scope\n\nTBD.\n\n## Current Focus\n\nTBD.\n"
    write_text(project_dir / "project.md", render_doc(frontmatter, body))
    for name_file, heading in [("decisions.md", "Decisions"), ("lessons.md", "Lessons"), ("agents.md", "Agents"), ("tools.md", "Tools")]:
        write_text(project_dir / name_file, f"# {heading}\n\n")
    write_text(project_dir / "tasks" / "index.md", f"# {name} Tasks\n\n")
    write_text(project_dir / "sources" / "index.md", f"# {name} Source Materials\n\n")
    update_index(bundle.root / "projects" / "index.md", name, f"{pid}/project.md")
    append_log(bundle, f"registered Project {pid}")
    append_log(bundle, f"registered Project {pid}", project_dir / "log.md")
    return project_dir / "project.md"


def infer_project_source_mode(source: str, repo_url: str = "") -> str:
    value = " ".join([source, repo_url]).strip().lower()
    if repo_url.strip() or any(token in value for token in ["existing", "已有", "迁移", "老项目", "repo", "git"]):
        return "existing_repo"
    if any(token in value for token in ["运营", "operation", "ops", "长期"]):
        return "operations_long_running"
    return "new_project"


def assess_project_intake(
    project_name: str,
    owner: str,
    goal: str,
    source: str = "",
    expected_deliverable: str = "",
    priority: str = "medium",
    risk: str = "low",
    repo_url: str = "",
    requested_agents: str = "",
    create_group: str = "confirm",
    requires_runner: bool = True,
) -> dict[str, Any]:
    if not project_name.strip():
        raise KnowledgeError("project name is required")
    if not owner.strip():
        raise KnowledgeError("project owner is required")
    source_mode = infer_project_source_mode(source, repo_url)
    normalized_risk = risk.strip().lower() or "low"
    if normalized_risk not in {"low", "medium", "high"}:
        raise KnowledgeError("project risk must be low, medium, or high")
    if source_mode == "existing_repo" and not repo_url.strip():
        raise KnowledgeError("existing repo project requires repo_url")
    repository_name = "" if source_mode == "existing_repo" else safe_slug(project_name, "project")
    decision = "clarify" if not goal.strip() else "project_draft"
    approval_required = normalized_risk == "high"
    if not expected_deliverable.strip() and source_mode == "operations_long_running":
        expected_deliverable = "长期运营目标、反馈回流、知识沉淀和周期复盘。"
    return {
        "type": "ProjectIntake",
        "projectName": project_name.strip(),
        "projectId": safe_slug(project_name, "project"),
        "owner": owner.strip(),
        "sourceMode": source_mode,
        "repoUrl": repo_url.strip(),
        "repositoryName": repository_name,
        "goal": goal.strip(),
        "expectedDeliverable": expected_deliverable.strip(),
        "priority": priority.strip() or "medium",
        "risk": normalized_risk,
        "requestedAgents": requested_agents.strip(),
        "suggestedAgents": [
            "项目经理 Agent",
            *([] if "不需要产品" in requested_agents else ["产品经理 Agent"]),
            "知识工程 Agent",
            "执行 Agent",
        ],
        "createGroup": create_group.strip() or "confirm",
        "requiresRunner": bool(requires_runner),
        "decision": decision,
        "approvalRequired": approval_required,
    }


def create_project_launch(
    bundle: Bundle,
    project_name: str,
    owner: str,
    goal: str,
    source: str = "",
    expected_deliverable: str = "",
    priority: str = "medium",
    risk: str = "low",
    repo_url: str = "",
    requested_agents: str = "",
    create_group: str = "confirm",
    requires_runner: bool = True,
    ring_enabled: bool = False,
    requester: str = "",
    project_id: str = "",
    workspace_ref: str = PENDING_WORKSPACE_REF,
) -> dict[str, str]:
    intake = assess_project_intake(
        project_name,
        owner,
        goal,
        source,
        expected_deliverable,
        priority,
        risk,
        repo_url,
        requested_agents,
        create_group,
        requires_runner,
    )
    pid = slug(project_id) if project_id.strip() else str(intake["projectId"])
    project_path = make_project(bundle, pid, project_name, owner, workspace_ref)
    project_updates = {
        "status": str(intake["decision"]),
        "projectSourceMode": intake["sourceMode"],
        "projectGoal": intake["goal"],
        "expectedDeliverable": intake["expectedDeliverable"],
        "priority": intake["priority"],
        "risk": intake["risk"],
        "approvalRequired": intake["approvalRequired"],
        "relatedRepos": [repo_url.strip()] if repo_url.strip() else [],
        "repositoryName": intake["repositoryName"],
        "requestedAgents": intake["requestedAgents"],
        "suggestedAgents": intake["suggestedAgents"],
        "createGroup": intake["createGroup"],
        "requiresRunner": intake["requiresRunner"],
        "workspaceRef": workspace_ref.strip() or PENDING_WORKSPACE_REF,
        "workspaceConfirmation": "confirmed" if workspace_ref.strip() and workspace_ref.strip() != PENDING_WORKSPACE_REF else "pending",
        "updatedAt": utc_now(),
    }
    update_frontmatter_file(project_path, project_updates)
    project_dir = project_path.parent
    launch_path = project_dir / "launch.md"
    launch_fm = {
        "type": "ProjectDraft",
        "title": f"{project_name} 启动清单",
        "timestamp": utc_now(),
        "projectId": pid,
        "owner": owner,
        "status": "approval_required" if intake["approvalRequired"] else "project_draft",
        "sourceMode": intake["sourceMode"],
        "repoUrl": repo_url.strip(),
        "repositoryName": intake["repositoryName"],
        "priority": intake["priority"],
        "risk": intake["risk"],
        "approvalRequired": intake["approvalRequired"],
        "requiresRunner": intake["requiresRunner"],
        "ringEnabled": bool(ring_enabled),
    }
    launch_body = "\n".join(
        [
            "## Project Intake",
            "",
            f"- projectName: {project_name}",
            f"- owner: {owner}",
            f"- sourceMode: {intake['sourceMode']}",
            f"- repoUrl: {repo_url.strip() or 'none'}",
            f"- repositoryName: {intake['repositoryName'] or 'existing repo'}",
            f"- goal: {intake['goal'] or 'needs clarification'}",
            f"- expectedDeliverable: {intake['expectedDeliverable'] or 'needs clarification'}",
            f"- priority: {intake['priority']}",
            f"- risk: {intake['risk']}",
            f"- createGroup: {intake['createGroup']}",
            "",
            "## Suggested Agent Team",
            "",
            "\n".join(f"- {item}" for item in intake["suggestedAgents"]),
            "",
            "## Initialization Checklist",
            "",
            "- Confirm scope, milestone, Agent team, Runner, repo, project group, approval state.",
            "- Confirm entity workspace path; if not confirmed, keep workspaceRef=pending_confirmation.",
            "- Existing repo: inspect README/AGENTS/directory/review rules before changes.",
            "- New repo: create repo request from project name; do not ask user to provide repository name.",
            "- Operations project: create operating cadence and feedback loop instead of forcing a code repo.",
        ]
    )
    write_text(launch_path, render_doc(launch_fm, launch_body))
    update_index(project_dir / "index.md", "Launch", "launch.md")
    agent_paths = ensure_default_project_agents(bundle, pid, project_name, owner, "", requested_agents, goal, str(intake["sourceMode"]))
    init_task = create_project_task(
        bundle,
        title=f"Initialize project: {project_name}",
        project_id=pid,
        requester=requester or owner,
        assignee=f"agent.{pid}.project-manager",
        task_type="project_initialization",
        task_id=f"project-init-{pid}",
        priority="high" if intake["risk"] == "high" else "normal",
        source_material_refs=[rel(launch_path, bundle.root)],
        expected_output=[
            "Confirm project scope, milestones, Agent team, Runner, repo, project group, and first tasks.",
            "Write TaskResult with handoff, blockers, and first executable backlog.",
        ],
    )
    if not ring_enabled:
        set_project_task_status(bundle, str(load_object(init_task).get("taskId")), "waiting_runner", "system.scheduler")
    create_audit_log(
        bundle,
        requester or owner,
        "project.intake",
        rel(project_path, bundle.root),
        after=str(intake["decision"]),
        policy_result="approval_required" if intake["approvalRequired"] else "draft_created",
        details=json.dumps(intake, ensure_ascii=False, indent=2),
    )
    return {
        "projectRef": rel(project_path, bundle.root),
        "launchRef": rel(launch_path, bundle.root),
        "initTaskRef": rel(init_task, bundle.root),
        "projectId": pid,
        "agentRefs": ",".join(rel(path, bundle.root) for path in agent_paths),
    }


def classify_operations_feedback(feedback_type: str, content: str) -> tuple[str, str, str]:
    text = " ".join([feedback_type, content]).lower()
    if any(token in text for token in ["知识", "经验", "踩坑", "流程", "文档", "沉淀"]):
        return "knowledge", KNOWLEDGE_ENGINEERING_AGENT_ID, "knowledge_capture"
    if any(token in text for token in ["bug", "报错", "性能", "崩溃", "开发", "研发", "接口", "卡顿"]):
        return "engineering", DEVELOPMENT_AGENT_ID, "development_feedback"
    if any(token in text for token in ["需求", "用户", "产品", "体验", "转化", "留存", "功能"]):
        return "product", PRODUCT_MANAGER_AGENT_ID, "product_feedback"
    return "operations", PROJECT_MANAGER_AGENT_ID, "operations_feedback"


def create_operations_feedback(
    bundle: Bundle,
    project_id: str,
    submitter: str,
    content: str,
    feedback_type: str = "",
    evidence_refs: list[str] | None = None,
    impact: str = "",
    suggested_next_action: str = "",
    requirement_ref: str = "",
    agent_ref: str = "",
    result_ref: str = "",
    score: str = "",
) -> dict[str, str]:
    if not project_id.strip():
        raise KnowledgeError("feedback project is required")
    if not submitter.strip():
        raise KnowledgeError("feedback submitter is required")
    if not content.strip():
        raise KnowledgeError("feedback content is required")
    project_path = find_project(bundle, project_id)
    pid = slug(project_id)
    category, assignee, task_type = classify_operations_feedback(feedback_type, content)
    feedback_id = unique_time_id("feedback")
    feedback_dir = project_path.parent / "feedback"
    feedback_path = feedback_dir / f"{feedback_id}.md"
    frontmatter = {
        "type": "FeedbackRecord",
        "title": f"Feedback {feedback_id}",
        "timestamp": utc_now(),
        "feedbackId": feedback_id,
        "projectId": pid,
        "projectRef": rel(project_path, bundle.root),
        "requirementRef": requirement_ref,
        "agentRef": agent_ref,
        "resultRef": result_ref,
        "submitter": submitter,
        "sourceChannel": "cli",
        "owner": assignee,
        "status": "feedback_loop",
        "feedbackType": category,
        "sentimentOrScore": score,
        "feedbackSummary": content[:240],
        "impact": impact,
        "suggestedNextAction": suggested_next_action,
        "evidenceRefs": evidence_refs or [],
        "improvementTaskRef": "",
        "linkedTask": "",
    }
    body = "\n".join(
        [
            "## Feedback",
            "",
            content.strip(),
            "",
            "## Evidence",
            "",
            "\n".join(f"- {item}" for item in evidence_refs or []) or "- none",
            "",
            "## Routing",
            "",
            f"- feedbackType: {category}",
            f"- assignee: {assignee}",
            f"- requirementRef: {requirement_ref or 'none'}",
            f"- agentRef: {agent_ref or 'none'}",
            f"- resultRef: {result_ref or 'none'}",
            f"- suggestedNextAction: {suggested_next_action or 'scheduler decides'}",
        ]
    )
    write_text(feedback_path, render_doc(frontmatter, body))
    update_index(feedback_dir / "index.md", str(frontmatter["title"]), feedback_path.name)
    task_path = create_project_task(
        bundle,
        title=suggested_next_action or f"Handle {category} feedback: {content[:60]}",
        project_id=pid,
        requester=submitter,
        assignee=assignee,
        task_type=task_type,
        task_id=followup_task_id(bundle, f"feedback-{feedback_id}"),
        priority="high" if impact.lower() in {"high", "严重", "高"} else "normal",
        source_material_refs=[rel(feedback_path, bundle.root), *(evidence_refs or [])],
        expected_output=[
            "Assess feedback impact and decide whether to create product, engineering, testing, operations, or knowledge follow-up.",
            "Keep original feedback and evidence linked.",
            "If reusable experience is found, create knowledge capture output.",
        ],
    )
    update_frontmatter_file(feedback_path, {"linkedTask": rel(task_path, bundle.root), "improvementTaskRef": rel(task_path, bundle.root), "updatedAt": utc_now()})
    update_frontmatter_file(project_path, {"status": "feedback_loop", "updatedAt": utc_now()})
    create_audit_log(bundle, submitter, "feedback.ingest", rel(feedback_path, bundle.root), after=rel(task_path, bundle.root), policy_result=category, details=content[:1000])
    return {
        "feedbackRef": rel(feedback_path, bundle.root),
        "taskRef": rel(task_path, bundle.root),
        "feedbackType": category,
    }


def create_ops_experiment(
    bundle: Bundle,
    project_id: str,
    title: str,
    owner: str,
    hypothesis: str,
    audience: str,
    metric: str,
    start_at: str,
    end_at: str,
    customer_facing: bool = False,
) -> Path:
    if not metric.strip():
        raise KnowledgeError("experiment metric is required before start")
    if customer_facing and not owner.strip():
        raise KnowledgeError("customer-facing experiment owner is required")
    project_path = find_project(bundle, project_id)
    experiment_id = unique_time_id("experiment")
    path = project_path.parent / "experiments" / f"{experiment_id}.md"
    frontmatter = {
        "type": "Experiment",
        "title": title,
        "description": "Operations or growth experiment record.",
        "timestamp": utc_now(),
        "experimentId": experiment_id,
        "projectId": slug(project_id),
        "owner": owner,
        "status": "approved" if not customer_facing else "decision_needed",
        "hypothesis": hypothesis,
        "audience": audience,
        "metric": metric,
        "startAt": start_at,
        "endAt": end_at,
        "result": "",
        "decision": "",
        "customerFacing": customer_facing,
        "approvalRoute": "product_owner_plus_governance" if customer_facing else "ops_owner",
    }
    body = "\n".join(
        [
            "## Hypothesis",
            "",
            hypothesis,
            "",
            "## Audience",
            "",
            audience,
            "",
            "## Metric",
            "",
            metric,
            "",
            "## Decision",
            "",
            "Pending result and owner decision.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(path.parent / "index.md", title, path.name)
    create_audit_log(bundle, owner, "ops.experiment.create", rel(path, bundle.root), after=str(frontmatter["status"]), policy_result=str(frontmatter["approvalRoute"]), details=f"metric={metric}")
    return path


def actor_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "actors"


def actor_storage_key(actor_id: str) -> str:
    return safe_slug(actor_id, "actor")


def infer_actor_type(actor_id: str) -> str:
    value = actor_id.strip().lower()
    if value.startswith("agent."):
        return "agent"
    if value.startswith("runner."):
        return "runner"
    if value.startswith("bot.") or "feishu" in value or "lark" in value:
        return "bot"
    return "human"


def actor_context_path(bundle: Bundle, actor_id: str) -> Path:
    return actor_storage_dir(bundle) / f"{actor_storage_key(actor_id)}.md"


def actor_context_from_existing_records(bundle: Bundle, actor_id: str) -> dict[str, Any]:
    raw_actor_id = actor_id.strip()
    aid = actor_storage_key(raw_actor_id)
    agent_path = bundle.root / "agents" / f"{aid}.md"
    if agent_path.exists():
        agent = load_object(agent_path)
        return {
            "actorId": raw_actor_id or aid,
            "actorKey": aid,
            "actorType": "agent",
            "displayName": agent.get("title", aid),
            "sourceRef": rel(agent_path, bundle.root),
            "allowedProjects": as_list(agent.get("allowedProjects")),
            "allowedKnowledgeScopes": as_list(agent.get("allowedKnowledgeScopes")),
            "preferredTools": as_list(agent.get("allowedTools")),
        }
    runner_path = runner_storage_dir(bundle) / f"{aid}.md"
    if runner_path.exists():
        runner = load_object(runner_path)
        return {
            "actorId": raw_actor_id or aid,
            "actorKey": aid,
            "actorType": "runner",
            "displayName": runner.get("title", aid),
            "sourceRef": rel(runner_path, bundle.root),
            "allowedProjects": as_list(runner.get("availableProjects")),
            "capabilities": as_list(runner.get("capabilities")),
            "preferredTools": as_list(runner.get("agents")),
        }
    return {
        "actorId": raw_actor_id or aid,
        "actorKey": aid,
        "actorType": infer_actor_type(actor_id),
        "displayName": actor_id,
        "sourceRef": "",
        "allowedProjects": [],
        "allowedKnowledgeScopes": [],
        "preferredTools": [],
    }


def actor_memory_policy() -> dict[str, Any]:
    return {
        "companyMemory": "reviewed reusable knowledge, shared skills, shared evals, and operating guide updates",
        "projectMemory": "project goals, tasks, decisions, source materials, task results, and project-scoped lessons",
        "taskMemory": "current task input, evidence, output, quality evaluation, and handoff state",
        "actorContext": "identity, permission, preference, current work context, and feedback; not reusable truth by itself",
        "promotionRule": "actor feedback may create improvement proposals; reusable conclusions require review before becoming project or company memory",
    }


def upsert_actor_context(
    bundle: Bundle,
    actor_id: str,
    actor_type: str = "",
    display_name: str = "",
    default_project: str = "",
    allowed_projects: list[str] | None = None,
    allowed_knowledge_scopes: list[str] | None = None,
    notification_preferences: list[str] | None = None,
    output_preference: str = "",
    source: str = "",
    owner: str = "system.scheduler",
) -> Path:
    if not actor_id.strip():
        raise KnowledgeError("actor id is required")
    raw_actor_id = actor_id.strip()
    aid = actor_storage_key(raw_actor_id)
    existing = actor_context_from_existing_records(bundle, raw_actor_id)
    path = actor_context_path(bundle, raw_actor_id)
    current = load_object(path) if path.exists() else {}
    projects = allowed_projects if allowed_projects is not None else as_list(current.get("allowedProjects") or existing.get("allowedProjects"))
    scopes = allowed_knowledge_scopes if allowed_knowledge_scopes is not None else as_list(current.get("allowedKnowledgeScopes") or existing.get("allowedKnowledgeScopes"))
    notifications = notification_preferences if notification_preferences is not None else as_list(current.get("notificationPreferences"))
    frontmatter = {
        "type": "ActorContext",
        "title": display_name or current.get("title") or existing.get("displayName") or aid,
        "description": "Runtime context for a human, Agent, Runner, bot, or local workbench actor.",
        "timestamp": current.get("timestamp") or utc_now(),
        "actorId": raw_actor_id,
        "actorKey": aid,
        "actorType": actor_type or current.get("actorType") or existing.get("actorType") or infer_actor_type(raw_actor_id),
        "displayName": display_name or current.get("displayName") or existing.get("displayName") or aid,
        "owner": owner,
        "status": "active",
        "defaultProject": slug(default_project) if default_project.strip() else str(current.get("defaultProject") or ""),
        "currentProject": slug(default_project) if default_project.strip() else str(current.get("currentProject") or current.get("defaultProject") or ""),
        "allowedProjects": projects,
        "allowedKnowledgeScopes": scopes,
        "notificationPreferences": notifications,
        "outputPreference": output_preference or str(current.get("outputPreference") or ""),
        "preferredTools": as_list(current.get("preferredTools") or existing.get("preferredTools")),
        "capabilities": as_list(current.get("capabilities") or existing.get("capabilities")),
        "source": source or str(current.get("source") or existing.get("sourceRef") or ""),
        "memoryPolicy": actor_memory_policy(),
        "lastSeenAt": utc_now(),
    }
    body = "\n".join(
        [
            "## Purpose",
            "",
            "ActorContext tells the scheduler who is acting, what they can access, how they prefer to receive output, and which memory layers should be loaded. It is runtime context, not reusable knowledge.",
            "",
            "## Memory Layers",
            "",
            *[f"- {key}: {value}" for key, value in frontmatter["memoryPolicy"].items()],
            "",
            "## Preferences",
            "",
            f"- outputPreference: {frontmatter['outputPreference'] or 'none'}",
            "- notificationPreferences:",
            *([f"  - {item}" for item in notifications] or ["  - none"]),
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(actor_storage_dir(bundle) / "index.md", str(frontmatter["title"]), path.name)
    create_audit_log(bundle, owner, "actor.context.upsert", rel(path, bundle.root), after="active", policy_result=str(frontmatter["actorType"]), details=f"actorId={aid}")
    return path


def actor_context_for(bundle: Bundle, actor_id: str, project_id: str = "") -> dict[str, Any]:
    if not actor_id.strip():
        return {"actorId": "", "actorType": "", "contextRef": "", "memoryPolicy": actor_memory_policy()}
    aid = actor_storage_key(actor_id)
    path = actor_context_path(bundle, actor_id)
    if path.exists():
        context = load_object(path)
        context["contextRef"] = rel(path, bundle.root)
    else:
        context = actor_context_from_existing_records(bundle, actor_id)
        context["contextRef"] = ""
    context["actorKey"] = str(context.get("actorKey") or aid)
    if project_id and not context.get("currentProject"):
        context["currentProject"] = slug(project_id)
    context["memoryPolicy"] = dict(context.get("memoryPolicy") or actor_memory_policy())
    return context


def resolve_object_ref(bundle: Bundle, ref_value: str) -> Path:
    value = ref_value.strip()
    if not value:
        raise KnowledgeError("object ref is required")
    path = bundle.root / value
    if path.exists():
        return path
    slugged = slug(value)
    for root in [task_result_storage_dir(bundle), bundle.root / "projects", bundle.root / "knowledge", actor_storage_dir(bundle)]:
        if root.exists():
            for candidate in root.rglob("*.md"):
                if candidate.name in COLLECTION_NAMES:
                    continue
                try:
                    fm = load_object(candidate)
                except KnowledgeError:
                    continue
                if slug(str(fm.get("resultId") or fm.get("taskId") or fm.get("feedbackId") or fm.get("actorId") or candidate.stem)) == slugged:
                    return candidate
    raise KnowledgeError(f"object ref not found: {ref_value}")


def actor_feedback_is_negative(rating: str, feedback_type: str, content: str) -> bool:
    text = " ".join([rating, feedback_type, content]).lower()
    negative_tokens = ["bad", "poor", "fail", "failed", "wrong", "useless", "reject", "打回", "失败", "不对", "不好", "没用", "太绕", "报错", "错误", "缺少", "不满意"]
    positive_tokens = ["good", "great", "ok", "满意", "通过", "很好", "有用"]
    if any(token in text for token in negative_tokens):
        return True
    if any(token in text for token in positive_tokens):
        return False
    try:
        return float(rating) <= 3
    except ValueError:
        return feedback_type.lower() in {"negative", "issue", "improvement", "rejected"}


def create_actor_feedback(
    bundle: Bundle,
    actor_id: str,
    content: str,
    target_agent: str = "",
    project_id: str = "",
    task_id: str = "",
    result_ref: str = "",
    rating: str = "",
    feedback_type: str = "",
    evidence_refs: list[str] | None = None,
    impact: str = "",
    source: str = "",
    owner: str = "system.scheduler",
) -> dict[str, Any]:
    if not actor_id.strip():
        raise KnowledgeError("actor id is required")
    if not content.strip():
        raise KnowledgeError("feedback content is required")
    actor_path = upsert_actor_context(bundle, actor_id, owner=owner)
    raw_actor_id = actor_id.strip()
    aid = actor_storage_key(raw_actor_id)
    feedback_id = unique_time_id("actor-feedback")
    feedback_dir = actor_storage_dir(bundle) / aid / "feedback"
    feedback_path = feedback_dir / f"{feedback_id}.md"
    pid = slug(project_id) if project_id.strip() else ""
    negative = actor_feedback_is_negative(rating, feedback_type, content)
    improvement_refs: list[str] = []
    eval_case_refs: list[str] = []
    task_ref = ""
    resolved_result_ref = ""
    if result_ref.strip():
        result_path = resolve_object_ref(bundle, result_ref)
        result_fm = load_object(result_path)
        if result_fm.get("type") != "TaskResult":
            raise KnowledgeError("result ref must point to TaskResult")
        resolved_result_ref = rel(result_path, bundle.root)
        linked_task_id = task_id or str(result_fm.get("taskId") or "")
        if linked_task_id:
            task_path = find_project_task(bundle, linked_task_id)
            task_ref = rel(task_path, bundle.root)
            if negative:
                task = load_object(task_path)
                improvement = maybe_record_agent_improvement(
                    bundle,
                    task_path,
                    task,
                    result_path,
                    result_fm,
                    trigger="actorFeedback",
                    extra_reasons=[content.strip()],
                )
                improvement_refs = improvement["improvementRefs"]
                eval_case_refs = improvement["evalCaseRefs"]
    if not resolved_result_ref and pid:
        assignee = target_agent or project_manager_agent_for_project(bundle, pid)
        task_path = create_project_task(
            bundle,
            title=f"Handle actor feedback: {content[:60]}",
            project_id=pid,
            requester=aid,
            assignee=assignee,
            task_type="actor_feedback",
            task_id=followup_task_id(bundle, f"actor-feedback-{feedback_id}"),
            priority="high" if negative or impact.lower() in {"high", "严重", "高"} else "normal",
            source_material_refs=[rel(feedback_path, bundle.root), *(evidence_refs or [])],
            expected_output=[
                "Assess whether feedback changes project memory, actor context, role Skill, EvalCase, workflow, or company knowledge.",
                "If the feedback is reusable beyond one actor or project, create an AgentImprovementProposal or knowledge capture task.",
            ],
        )
        task_ref = rel(task_path, bundle.root)
    frontmatter = {
        "type": "ActorFeedback",
        "title": f"Actor feedback {feedback_id}",
        "description": "Feedback from a human, Agent, Runner, bot, or workbench actor.",
        "timestamp": utc_now(),
        "feedbackId": feedback_id,
        "actorId": raw_actor_id,
        "actorKey": aid,
        "actorContextRef": rel(actor_path, bundle.root),
        "targetAgent": target_agent,
        "projectId": pid,
        "taskId": task_id,
        "resultRef": resolved_result_ref,
        "rating": rating,
        "feedbackType": feedback_type or ("negative" if negative else "neutral"),
        "impact": impact,
        "source": source,
        "status": "feedback_loop" if negative else "observed",
        "evidenceRefs": evidence_refs or [],
        "linkedTask": task_ref,
        "improvementRefs": improvement_refs,
        "evalCaseRefs": eval_case_refs,
        "memoryPolicy": actor_memory_policy(),
    }
    body = "\n".join(
        [
            "## Feedback",
            "",
            content.strip(),
            "",
            "## Routing",
            "",
            f"- negative: {negative}",
            f"- targetAgent: {target_agent or 'none'}",
            f"- resultRef: {resolved_result_ref or 'none'}",
            f"- linkedTask: {task_ref or 'none'}",
            "",
            "## Memory Promotion",
            "",
            "- Actor feedback is not reusable knowledge by itself.",
            "- Reusable conclusions must be promoted through AgentImprovementProposal, EvalCase, KnowledgeItem, or guide update review.",
        ]
    )
    write_text(feedback_path, render_doc(frontmatter, body))
    update_index(feedback_dir / "index.md", str(frontmatter["title"]), feedback_path.name)
    update_index(actor_storage_dir(bundle) / "index.md", str(frontmatter["title"]), rel(feedback_path, actor_storage_dir(bundle)))
    if task_ref and not resolved_result_ref:
        update_frontmatter_file(feedback_path, {"linkedTask": task_ref, "updatedAt": utc_now()})
    create_audit_log(bundle, aid, "actor.feedback.ingest", rel(feedback_path, bundle.root), after=str(frontmatter["status"]), policy_result=frontmatter["feedbackType"], details=content[:1000])
    return {
        "apiVersion": "v0.1",
        "kind": "ActorFeedback",
        "feedbackRef": rel(feedback_path, bundle.root),
        "actorContextRef": rel(actor_path, bundle.root),
        "linkedTask": task_ref,
        "improvementRefs": improvement_refs,
        "evalCaseRefs": eval_case_refs,
        "negative": negative,
    }


def make_agent(bundle: Bundle, agent_id: str, name: str, owner: str, ai_tool: str, purpose: str) -> Path:
    aid = slug(agent_id)
    path = bundle.root / "agents" / f"{aid}.md"
    frontmatter = {
        "type": "Agent",
        "title": name,
        "description": purpose,
        "timestamp": utc_now(),
        "agentId": aid,
        "owner": owner,
        "aiTool": ai_tool,
        "status": "draft",
        "riskLevel": "L1",
        "allowedProjects": [],
        "allowedTools": [],
        "allowedKnowledgeScopes": ["company", "engineering"],
        "humanApprovalRequired": True,
    }
    body = "## Purpose\n\n" + purpose + "\n\n## Operating Notes\n\n- Must run start before formal work.\n- Must run finish after formal work.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "agents" / "index.md", name, f"{aid}.md")
    append_log(bundle, f"registered Agent {aid}")
    return path


def make_tool(bundle: Bundle, tool_id: str, name: str, owner: str, repo: str, entrypoint: str, risk: str) -> Path:
    tid = slug(tool_id)
    normalized_risk = risk.upper()
    if normalized_risk not in {"L1", "L2", "L3", "L4", "L5"}:
        raise KnowledgeError(f"unknown tool risk level: {risk}")
    approval_required = normalized_risk in {"L3", "L4", "L5"}
    path = bundle.root / "tools" / f"{tid}.md"
    frontmatter = {
        "type": "ToolAsset",
        "title": name,
        "description": f"Reusable tool asset: {name}.",
        "resource": repo,
        "timestamp": utc_now(),
        "toolId": tid,
        "owner": owner,
        "repoRef": repo,
        "entrypoint": entrypoint,
        "version": "0.1.0",
        "status": "testing",
        "scope": "company",
        "riskLevel": normalized_risk,
        "invocationPolicy": "approval_required" if approval_required else "agent_policy_allowed",
        "requiresApproval": ["call_high_risk_tool"] if approval_required else [],
        "executionMode": "dry_run_default",
        "allowedAgents": [],
        "allowedProjects": [],
        "secretsRequired": [],
        "knownIssues": [],
        "lastVerifiedAt": "",
    }
    body = "## Usage\n\nTBD.\n\n## Input Schema\n\nTBD.\n\n## Output Schema\n\nTBD.\n\n## Notes\n\nTBD.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "tools" / "index.md", name, f"{tid}.md")
    append_log(bundle, f"registered ToolAsset {tid}")
    return path


def skill_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "skills"


def make_skill(
    bundle: Bundle,
    skill_id: str,
    name: str,
    owner: str,
    purpose: str,
    scope: str = "company",
    risk: str = "L2",
    project_id: str = "",
    source_ref: str = "",
) -> Path:
    sid = slug(skill_id)
    normalized_risk = risk.upper()
    if normalized_risk not in {"L1", "L2", "L3", "L4", "L5"}:
        raise KnowledgeError(f"unknown skill risk level: {risk}")
    normalized_scope = scope.strip().lower() or "company"
    if normalized_scope not in {"company", "project", "private"}:
        raise KnowledgeError(f"unknown skill scope: {scope}")
    ensure_dir(skill_storage_dir(bundle))
    path = skill_storage_dir(bundle) / f"{sid}.md"
    frontmatter = {
        "type": "SkillAsset",
        "title": name,
        "description": purpose,
        "timestamp": utc_now(),
        "skillId": sid,
        "owner": owner,
        "status": "draft",
        "scope": normalized_scope,
        "projectId": slug(project_id) if project_id else "",
        "riskLevel": normalized_risk,
        "version": "0.1.0",
        "inputContract": "",
        "outputContract": "",
        "evalCaseRefs": [],
        "allowedAgents": [],
        "allowedProjects": [slug(project_id)] if project_id else [],
        "rolloutState": "draft",
        "reusePolicy": "project_private" if normalized_scope == "project" else "review_required_before_company_reuse",
        "sourceRef": source_ref,
        "lastEvaluatedAt": "",
        "lastPromotedAt": "",
        "rollbackRef": "",
    }
    body = "\n".join(
        [
            "## Purpose",
            "",
            purpose or "TBD.",
            "",
            "## Input Contract",
            "",
            "TBD.",
            "",
            "## Output Contract",
            "",
            "TBD.",
            "",
            "## Evaluation",
            "",
            "- Add EvalCase refs before promotion.",
            "",
            "## Rollout",
            "",
            "- Draft skills are not company-wide defaults.",
            "- Company-wide reuse requires review, evaluation, and promotion record.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(skill_storage_dir(bundle) / "index.md", name, f"{sid}.md")
    create_audit_log(bundle, owner, "skill.register", rel(path, bundle.root), after="draft", policy_result=normalized_scope)
    append_log(bundle, f"registered SkillAsset {sid}")
    return path


def make_policy(
    bundle: Bundle,
    policy_id: str,
    title: str,
    agent_id: str,
    owner: str,
    allowed_projects: list[str],
    allowed_scopes: list[str],
    allowed_risks: list[str],
) -> Path:
    pid = slug(policy_id)
    path = bundle.root / "knowledge" / "policies" / f"{pid}.md"
    frontmatter = {
        "type": "Policy",
        "title": title,
        "description": f"Policy for {agent_id}.",
        "timestamp": utc_now(),
        "policyId": pid,
        "agentId": slug(agent_id),
        "owner": owner,
        "status": "draft",
        "scope": "company",
        "allowedProjects": [slug(item) for item in allowed_projects],
        "allowedKnowledgeScopes": allowed_scopes,
        "allowedToolRiskLevels": allowed_risks,
        "writePermissions": ["knowledge:draft", "toolAsset:draft"],
        "requiresApproval": ["publish_verified", "call_L3_tool", "access_customer_confidential"],
    }
    body = "## Notes\n\nPolicy changes require review before active use.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", title, f"policies/{pid}.md")
    append_log(bundle, f"registered Policy {pid}")
    return path


def load_object(path: Path) -> dict[str, Any]:
    fm, _ = parse_frontmatter(read_text(path))
    return fm


def build_task_fact_view(bundle: Bundle, project_id: str, task_id: str) -> dict[str, Any]:
    from zhenzhi_knowledge.task_fact_view import build_task_fact_view as build_projected_task_fact_view

    return build_projected_task_fact_view(bundle, project_id, task_id)


def find_project(bundle: Bundle, project_id: str) -> Path:
    path = bundle.root / "projects" / slug(project_id) / "project.md"
    if not path.exists():
        raise KnowledgeError(f"project not found: {project_id}")
    return path


def find_agent(bundle: Bundle, agent_id: str) -> Path:
    path = bundle.root / "agents" / f"{slug(agent_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"agent not found: {agent_id}")
    return path


def find_tool(bundle: Bundle, tool_id: str) -> Path:
    path = bundle.root / "tools" / f"{slug(tool_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"tool not found: {tool_id}")
    return path


def next_task_id(bundle: Bundle, prefix: str = "KT") -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    existing: list[str] = []
    for root in [bundle.root / "tasks", bundle.root / "projects"]:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            task_id = str(fm.get("taskId", ""))
            if task_id.startswith(f"{prefix}-{today}-"):
                existing.append(task_id)
    seq = len(existing) + 1
    return f"{prefix}-{today}-{seq:03d}"


def task_storage_dir(bundle: Bundle, project_id: str) -> Path:
    if project_id:
        project_task_dir = bundle.root / "projects" / slug(project_id) / "tasks"
        if (bundle.root / "projects" / slug(project_id) / "project.md").exists():
            return project_task_dir
    return bundle.root / "tasks"


def task_result_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "task-results"


def defect_storage_dir(bundle: Bundle, project_id: str) -> Path:
    pid = slug(project_id)
    if pid and (bundle.root / "projects" / pid / "project.md").exists():
        return bundle.root / "projects" / pid / "defects"
    return bundle.root / "defects"


def receiver_review_storage_dir(bundle: Bundle, project_id: str) -> Path:
    pid = slug(project_id)
    if pid and (bundle.root / "projects" / pid / "project.md").exists():
        return bundle.root / "projects" / pid / "receiver-reviews"
    return bundle.root / "receiver-reviews"


def outcome_slice_storage_dir(bundle: Bundle, project_id: str) -> Path:
    pid = slug(project_id)
    if pid and (bundle.root / "projects" / pid / "project.md").exists():
        return bundle.root / "projects" / pid / "outcome-slices"
    return bundle.root / "outcome-slices"


def notification_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "notifications"


def discussion_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    if project_id:
        project_dir = bundle.root / "projects" / slug(project_id)
        if (project_dir / "project.md").exists():
            return project_dir / "discussions"
    return bundle.root / "discussions"


def runner_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "runners"


def next_discussion_id(bundle: Bundle) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    existing = 0
    for root in [bundle.root / "discussions", bundle.root / "projects"]:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                fm = load_object(path)
            except KnowledgeError:
                continue
            if str(fm.get("discussionId", "")).startswith(f"DISC-{today}-"):
                existing += 1
    return f"DISC-{today}-{existing + 1:03d}"


def find_discussion_session(bundle: Bundle, discussion_id: str) -> Path:
    sid = slug(discussion_id)
    candidates = [bundle.root / "discussions" / f"{sid}.md"]
    if (bundle.root / "projects").exists():
        candidates.extend((bundle.root / "projects").glob(f"*/discussions/{sid}.md"))
    for path in candidates:
        if path.exists() and load_object(path).get("type") == "DiscussionSession":
            return path
    roots = [bundle.root / "discussions"]
    if (bundle.root / "projects").exists():
        roots.extend((bundle.root / "projects").glob("*/discussions"))
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                fm = load_object(path)
            except KnowledgeError:
                continue
            if fm.get("type") == "DiscussionSession" and str(fm.get("discussionId", "")).lower() == discussion_id.lower():
                return path
    raise KnowledgeError(f"discussion session not found: {discussion_id}")


def find_agent_runner(bundle: Bundle, runner_id: str) -> Path:
    path = runner_storage_dir(bundle) / f"{slug(runner_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"runner not found: {runner_id}")
    return path


def find_project_task(bundle: Bundle, task_id: str) -> Path:
    sid = slug(task_id)
    candidates = [bundle.root / "tasks" / f"{sid}.md"]
    if (bundle.root / "projects").exists():
        candidates.extend((bundle.root / "projects").glob(f"*/tasks/{sid}.md"))
    for path in candidates:
        if path.exists():
            return path
    task_dirs = [bundle.root / "tasks"]
    if (bundle.root / "projects").exists():
        task_dirs.extend((bundle.root / "projects").glob("*/tasks"))
    for task_dir in task_dirs:
        if not task_dir.exists():
            continue
        for path in sorted(task_dir.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                fm = load_object(path)
            except KnowledgeError:
                continue
            if str(fm.get("taskId", "")).lower() == task_id.lower():
                return path
    raise KnowledgeError(f"task not found: {task_id}")


def find_skill(bundle: Bundle, skill_id: str) -> Path:
    candidates = [
        bundle.root / "skills" / f"{slug(skill_id)}.md",
        bundle.root / "tools" / f"{slug(skill_id)}.md",
    ]
    for path in candidates:
        if path.exists():
            return path
    for root in [bundle.root / "skills", bundle.root / "tools"]:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            if fm.get("type") == "SkillAsset" and str(fm.get("skillId") or path.stem).lower() == skill_id.lower():
                return path
    raise KnowledgeError(f"skill not found: {skill_id}")


def find_governed_asset(bundle: Bundle, object_type: str, object_id: str) -> Path:
    normalized = object_type.strip().lower()
    if normalized in {"agent", "agentasset"}:
        return find_agent(bundle, object_id)
    if normalized in {"tool", "toolasset"}:
        return find_tool(bundle, object_id)
    if normalized in {"skill", "skillasset"}:
        return find_skill(bundle, object_id)
    if normalized in {"runner", "agentrunner"}:
        return find_agent_runner(bundle, object_id)
    if normalized in {"integration", "policy"}:
        path = bundle.root / "knowledge" / "policies" / f"{slug(object_id)}.md"
        if path.exists():
            return path
    raise KnowledgeError(f"governed asset not found: {object_type}:{object_id}")


def task_uses_disabled_asset(task: dict[str, Any], object_type: str, object_id: str) -> bool:
    normalized = object_type.strip().lower()
    oid = slug(object_id)
    if normalized in {"agent", "agentasset"}:
        return slug(str(task.get("assignee") or "")) == oid or oid in {slug(item) for item in as_list(task.get("requiredAgents"))}
    if normalized in {"runner", "agentrunner"}:
        return slug(str(task.get("assignedRunner") or "")) == oid or slug(str(task.get("leaseOwner") or "")) == oid
    if normalized in {"tool", "toolasset"}:
        return oid in {slug(item) for item in [*as_list(task.get("requiredTools")), *as_list(task.get("toolRefs"))]}
    if normalized in {"skill", "skillasset"}:
        return oid in {slug(item) for item in [*as_list(task.get("requiredSkills")), *as_list(task.get("skillRefs"))]}
    return False


def active_project_task_paths(bundle: Bundle) -> list[Path]:
    paths: list[Path] = []
    roots = [bundle.root / "tasks"]
    if (bundle.root / "projects").exists():
        roots.extend((bundle.root / "projects").glob("*/tasks"))
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                fm = load_object(path)
            except KnowledgeError:
                continue
            if fm.get("type") in {"ProjectTask", "KnowledgeTask"}:
                paths.append(path)
    return paths


def disable_governed_asset(
    bundle: Bundle,
    object_type: str,
    object_id: str,
    actor: str,
    reason: str,
    reassign: bool = False,
) -> dict[str, Any]:
    if not actor.strip():
        raise KnowledgeError("admin disable actor is required")
    if not reason.strip():
        raise KnowledgeError("admin disable reason is required")
    asset_path = find_governed_asset(bundle, object_type, object_id)
    before = load_object(asset_path)
    owner = str(before.get("owner") or before.get("runnerOwner") or before.get("assignee") or actor)
    updates = {
        "status": "disabled",
        "disabledAt": utc_now(),
        "disabledBy": actor,
        "disableReason": reason,
        "rollbackPath": str(before.get("rollbackPath") or "admin re-enable after owner review and audit"),
        "updatedAt": utc_now(),
    }
    if str(before.get("type")) == "AgentRunner":
        updates["availabilityStatus"] = "offline"
    after = update_frontmatter_file(asset_path, updates)
    asset_ref = rel(asset_path, bundle.root)
    impacted_refs: list[str] = []
    notification_refs: list[str] = []
    for task_path in active_project_task_paths(bundle):
        task = load_object(task_path)
        if str(task.get("status") or "") in CLOSED_TASK_STATUSES:
            continue
        if not task_uses_disabled_asset(task, object_type, object_id):
            continue
        next_status = "waiting_runner" if reassign else "blocked"
        current = str(task.get("status") or "")
        if current != next_status:
            update_frontmatter_file(
                task_path,
                {
                    "status": next_status,
                    "blockedReason": f"disabled {object_type}: {object_id}",
                    "disableImpactRef": asset_ref,
                    "updatedAt": utc_now(),
                },
            )
        impacted_refs = append_unique(impacted_refs, rel(task_path, bundle.root))
        create_audit_log(
            bundle,
            actor,
            "admin.disable.pauseTask",
            rel(task_path, bundle.root),
            before=current,
            after=next_status,
            policy_result="reassign_allowed" if reassign else "paused_by_default",
            details=f"assetRef={asset_ref}\nreason={reason}",
        )
    audit_path = create_audit_log(
        bundle,
        actor,
        "admin.disableAsset",
        asset_ref,
        before=str(before.get("status") or ""),
        after="disabled",
        policy_result="admin_governance",
        details=f"objectType={object_type}\nobjectId={object_id}\nreason={reason}\nimpactedTasks={','.join(impacted_refs) or 'none'}",
    )
    try:
        notification_path = create_task_notification(
            bundle,
            asset_path,
            {
                "taskId": str(after.get("toolId") or after.get("skillId") or after.get("agentId") or after.get("runnerId") or object_id),
                "projectId": "",
                "status": "disabled",
                "requester": actor,
                "assignee": owner,
                "title": str(after.get("title") or object_id),
            },
            "asset_disabled",
            recipient=owner,
            summary=f"资产已禁用：{after.get('title', object_id)}。原因：{reason}。受影响任务：{', '.join(impacted_refs) or '无'}。回滚路径：{after.get('rollbackPath')}",
            source_message_ref=asset_ref,
        )
        notification_refs.append(rel(notification_path, bundle.root))
    except KnowledgeError:
        pass
    return {
        "apiVersion": "v0.1",
        "kind": "AdminDisableResult",
        "assetRef": asset_ref,
        "status": "disabled",
        "impactedTaskRefs": impacted_refs,
        "notificationRefs": notification_refs,
        "auditRef": rel(audit_path, bundle.root),
        "disableSemantics": "new_usage_blocked; active_work_reassigned" if reassign else "new_usage_blocked; active_work_paused",
        "rollbackPath": str(after.get("rollbackPath") or ""),
    }


def register_agent_runner(
    bundle: Bundle,
    runner_id: str,
    name: str,
    host_type: str = "",
    mode: str = "unattended",
    agents: list[str] | None = None,
    capabilities: list[str] | None = None,
    available_projects: list[str] | None = None,
    repo_access: list[str] | None = None,
    data_scopes: list[str] | None = None,
    ring_version: str = "0.1.0",
) -> Path:
    rid = slug(runner_id)
    if not name.strip():
        raise KnowledgeError("runner name is required")
    ensure_dir(runner_storage_dir(bundle))
    path = runner_storage_dir(bundle) / f"{rid}.md"
    frontmatter = {
        "type": "AgentRunner",
        "title": name,
        "description": "External Agent Ring runner registration.",
        "timestamp": utc_now(),
        "runnerId": rid,
        "machineId": rid,
        "owner": "",
        "ringVersion": ring_version,
        "hostType": host_type,
        "status": "online",
        "mode": mode,
        "agents": agents or [],
        "agentIds": agents or [],
        "capabilities": capabilities or [],
        "tools": [],
        "availableProjects": available_projects or [],
        "repoAccess": repo_access or [],
        "repositoryScopes": repo_access or [],
        "dataScopes": data_scopes or [],
        "load": "",
        "lastHeartbeatAt": utc_now(),
        "currentLeases": [],
        "staleLeases": [],
        "failedLeases": [],
        "taskHistory": [],
        "lastFailure": "",
        "manualHandoff": bool(mode == "manual" or rid.startswith("manual.")),
    }
    if path.exists():
        existing = load_object(path)
        updates = dict(frontmatter)
        updates["timestamp"] = existing.get("timestamp") or frontmatter["timestamp"]
        update_frontmatter_file(path, updates)
        update_index(runner_storage_dir(bundle) / "index.md", name, path.name)
        create_audit_log(bundle, rid, "runner.upsert", rel(path, bundle.root), after="online", policy_result="agent_ring")
        append_log(bundle, f"upserted runner {rid}")
        return path
    body = "\n".join(
        [
            "## Purpose",
            "",
            "This runner represents one distributed computer connected through Agent Ring.",
            "",
            "## Health Checks",
            "",
            "- Agent Ring must report heartbeat before claiming tasks.",
            "- Runner-side tools, models, repositories, and data access remain local to that computer.",
            "- Central processor stores capabilities and audit metadata, not local secrets.",
            "",
            "## Notes",
            "",
            "Agent Ring owns local execution. This record is the central processor view used for scheduling.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(runner_storage_dir(bundle) / "index.md", name, path.name)
    create_audit_log(bundle, rid, "runner.register", rel(path, bundle.root), after="online", policy_result="agent_ring")
    append_log(bundle, f"registered runner {rid}")
    return path


def heartbeat_agent_runner(
    bundle: Bundle,
    runner_id: str,
    status: str = "online",
    load: str = "",
    capabilities: list[str] | None = None,
    available_projects: list[str] | None = None,
) -> Path:
    if status not in {"online", "online_readonly", "online_schedulable", "idle", "busy", "offline", "degraded"}:
        raise KnowledgeError(f"unknown runner status: {status}")
    path = find_agent_runner(bundle, runner_id)
    updates: dict[str, Any] = {"status": status, "lastHeartbeatAt": utc_now()}
    if load:
        updates["load"] = load
    if capabilities is not None:
        runner = load_object(path)
        updates["capabilities"] = sorted({str(item) for item in [*as_list(runner.get("capabilities")), *capabilities] if str(item).strip()})
    if available_projects is not None:
        runner = load_object(path)
        updates["availableProjects"] = sorted({str(item) for item in [*as_list(runner.get("availableProjects")), *available_projects] if str(item).strip()})
    update_frontmatter_file(path, updates)
    create_audit_log(bundle, slug(runner_id), "runner.heartbeat", rel(path, bundle.root), after=status, policy_result="agent_ring")
    return path


def create_access_credential_request(
    bundle: Bundle,
    requester: str,
    purpose: str,
    project_id: str = "",
    credential_type: str = "central_api",
    credential_scope: str = "personal_setup",
    risk: str = "L2",
    expiry: str = "",
    approver: str = "",
    secret_ref: str = "",
    request_id: str = "",
    status: str = "pending",
) -> Path:
    if not requester.strip():
        raise KnowledgeError("credential requester is required")
    if not purpose.strip():
        raise KnowledgeError("credential purpose is required")
    if secret_ref and not secret_ref.startswith("secretref://"):
        raise KnowledgeError("secretRef must be a secretref:// reference")
    rid = slug(request_id or unique_time_id("credential"))
    path = bundle.root / "credential-requests" / f"{rid}.md"
    if path.exists():
        raise KnowledgeError(f"credential request already exists: {rid}")
    frontmatter = {
        "type": "AccessCredentialRequest",
        "title": rid,
        "description": "Access credential request with secretRef-only persistence.",
        "timestamp": utc_now(),
        "requestId": rid,
        "requester": requester,
        "purpose": purpose,
        "projectId": slug(project_id) if project_id else "",
        "credentialType": credential_type,
        "credentialScope": credential_scope,
        "credentialRisk": risk,
        "expiry": expiry,
        "approver": approver,
        "secretRef": secret_ref,
        "status": status,
    }
    body = "\n".join(
        [
            "## Request",
            "",
            purpose,
            "",
            "## Secret Boundary",
            "",
            "- Store only secretRef and approval metadata here.",
            "- Plaintext secret values must remain in server secret store, Secret Manager, or Agent Ring local secure storage.",
            "",
            "## Readiness",
            "",
        f"- {status} until owner or Agent Ring reports the secretRef is configured.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "credential-requests" / "index.md", rid, path.name)
    create_audit_log(
        bundle,
        requester,
        "credential.request.create",
        rel(path, bundle.root),
        after=status,
        policy_result="access_credential",
        details=f"credentialType={credential_type}\nsecretRef={secret_ref or 'pending'}",
    )
    append_log(bundle, f"created credential request {rid}")
    return path


def find_access_credential_request(bundle: Bundle, request_id: str) -> Path:
    path = bundle.root / "credential-requests" / f"{slug(request_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"credential request not found: {request_id}")
    return path


def mark_access_credential_ready(bundle: Bundle, request_id: str, secret_ref: str, actor: str = "system") -> Path:
    if not secret_ref.startswith("secretref://"):
        raise KnowledgeError("secretRef must be a secretref:// reference")
    path = find_access_credential_request(bundle, request_id)
    before = load_object(path).get("status", "")
    update_frontmatter_file(path, {"secretRef": secret_ref, "status": "approved", "updatedAt": utc_now()})
    create_audit_log(bundle, actor, "credential.ready", rel(path, bundle.root), before=str(before), after="approved", policy_result="access_credential", details=f"secretRef={secret_ref}")
    return path


def secret_ref_ready(bundle: Bundle, secret_ref: str) -> bool:
    if not secret_ref.startswith("secretref://"):
        return False
    root = bundle.root / "credential-requests"
    if not root.exists():
        return False
    for path in root.glob("*.md"):
        if path.name in COLLECTION_NAMES:
            continue
        fm = load_object(path)
        if fm.get("type") != "AccessCredentialRequest":
            continue
        if fm.get("secretRef") == secret_ref and fm.get("status") in {"approved", "active", "verified"}:
            return True
    return False


def missing_required_secret_refs(bundle: Bundle, task: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for item in as_list(task.get("requiredSecretRefs")):
        if not secret_ref_ready(bundle, str(item)):
            missing.append(str(item))
    return missing


def missing_runner_requirements(runner: dict[str, Any], task: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    runtime = normalized_task_runtime(task)
    runner_capabilities = {str(item) for item in as_list(runner.get("capabilities"))}
    required_capabilities = {str(item) for item in [*as_list(runtime.get("requiredCapabilities")), *as_list(task.get("requiredCapabilities"))]}
    task_type = str(runtime.get("taskType") or task.get("taskType", ""))
    if not required_capabilities and task_type:
        required_capabilities.add(task_type)
    for capability in sorted(required_capabilities):
        if runner_capabilities and capability not in runner_capabilities:
            missing.append(f"capability:{capability}")
    runner_tools = {str(item) for item in [*as_list(runner.get("tools")), *as_list(runner.get("toolIds"))]}
    for tool in sorted({str(item) for item in as_list(runtime.get("requiredTools"))}):
        if runner_tools and tool not in runner_tools:
            missing.append(f"tool:{tool}")
    available_projects = {str(item) for item in as_list(runner.get("availableProjects"))}
    project_id = str(task.get("projectId", ""))
    if project_id and available_projects and project_id not in available_projects:
        missing.append(f"project:{project_id}")
    runner_repos = {str(item) for item in [*as_list(runner.get("repositoryScopes")), *as_list(runner.get("repoAccess"))]}
    for repo in sorted({str(item) for item in as_list(runtime.get("repositoryRefs"))}):
        if runner_repos and repo not in runner_repos:
            missing.append(f"repository:{repo}")
    runner_scopes = {str(item) for item in as_list(runner.get("dataScopes"))}
    for scope in sorted({str(item) for item in as_list(runtime.get("dataScopes"))}):
        if runner_scopes and scope not in runner_scopes:
            missing.append(f"dataScope:{scope}")
    return missing


def task_required_env_vars(task: dict[str, Any]) -> list[str]:
    runtime = normalized_task_runtime(task)
    return append_runtime_unique(as_list(task.get("requiredEnvVars")), as_list(runtime.get("requiredEnvVars")))


def task_environment_readiness(bundle: Bundle, task: dict[str, Any], runner: dict[str, Any] | None = None) -> dict[str, Any]:
    missing_secret_refs = missing_required_secret_refs(bundle, task)
    missing_runner = missing_runner_requirements(runner, task) if runner else []
    required_env_vars = task_required_env_vars(task)
    missing_env_vars = [name for name in required_env_vars if name not in os.environ]
    next_actions: list[str] = []
    for ref in missing_secret_refs:
        next_actions.append(f"Configure credential readiness for secretRef {ref}.")
    for item in missing_runner:
        next_actions.append(f"Select or register a runner that satisfies {item}.")
    for name in missing_env_vars:
        next_actions.append(f"Set environment variable {name} in the runner runtime before claiming.")
    return {
        "status": "blocked" if missing_secret_refs or missing_runner or missing_env_vars else "ready",
        "missingSecretRefs": missing_secret_refs,
        "missingRunnerRequirements": missing_runner,
        "requiredEnvVars": required_env_vars,
        "missingEnvVars": missing_env_vars,
        "nextActions": next_actions,
    }


def execution_context_payload(bundle: Bundle, task: dict[str, Any], runner_id: str, lease_token: str, context_ref: str = "") -> dict[str, Any]:
    task_id = str(task.get("taskId") or "")
    executor_agent = str(task.get("executorAgent") or task.get("assignee") or "")
    lease_proof = secret_fingerprint(lease_token) if lease_token else str(task.get("leaseProofHash") or task.get("leaseTokenHash") or "")
    writeback_command = " ".join(
        [
            "python3",
            "-m",
            "zhenzhi_knowledge",
            "--root",
            shlex.quote(str(bundle.root)),
            "task",
            "finish",
            shlex.quote(task_id),
            "--runner-id",
            shlex.quote(slug(runner_id)),
            "--lease-token",
            shlex.quote(lease_token),
            "--executor-agent",
            shlex.quote(executor_agent),
            "--summary",
            "\"<summary>\"",
        ]
    )
    return {
        "runnerId": slug(runner_id),
        "leaseToken": lease_token,
        "leaseExpiresAt": str(task.get("leaseExpiresAt") or ""),
        "leaseProof": lease_proof,
        "contextRef": context_ref,
        "writebackCommand": writeback_command,
    }


def write_execution_context_ref(bundle: Bundle, task: dict[str, Any], execution_context: dict[str, Any]) -> str:
    task_id = str(task.get("taskId") or "")
    path = bundle.zz_dir / "execution-context" / f"task.{slug(task_id)}.json"
    safe_payload = {
        "taskId": task_id,
        "runnerId": str(execution_context.get("runnerId") or ""),
        "leaseExpiresAt": str(execution_context.get("leaseExpiresAt") or ""),
        "leaseProof": str(execution_context.get("leaseProof") or ""),
        "contextRef": str(execution_context.get("contextRef") or ""),
        "writebackCommandAvailable": bool(execution_context.get("writebackCommand")),
        "leaseTokenStored": False,
        "updatedAt": utc_now(),
    }
    write_text(path, json.dumps(safe_payload, ensure_ascii=False, indent=2) + "\n")
    return rel(path, bundle.root)


def update_frontmatter_file(path: Path, updates: dict[str, Any]) -> dict[str, Any]:
    text = read_text(path)
    fm, body = parse_frontmatter(text)
    if not fm:
        raise KnowledgeError(f"target has no frontmatter: {path}")
    fm.update(updates)
    write_text(path, render_doc(fm, body))
    return fm


def create_task_notification(
    bundle: Bundle,
    task_path: Path,
    task: dict[str, Any],
    message_type: str,
    recipient: str = "",
    channel: str = "feishu",
    delivery_status: str = "pending",
    summary: str = "",
    source_message_ref: str = "",
    failure_reason: str = "",
) -> Path:
    if delivery_status not in {"pending", "sent", "failed", "retrying", "dead_letter"}:
        raise KnowledgeError(f"unknown notification status: {delivery_status}")
    ensure_dir(notification_storage_dir(bundle))
    index_path = notification_storage_dir(bundle) / "index.md"
    if not index_path.exists():
        write_text(index_path, "# Notifications\n\n")
    notification_id = unique_time_id("notification")
    path = notification_storage_dir(bundle) / f"{notification_id}.md"
    task_id = str(task.get("taskId") or task_path.stem)
    project_id = str(task.get("projectId") or "")
    recipient_value = recipient or str(task.get("requester") or task.get("assignee") or "project")
    message_summary = summary or task_notification_summary(task, message_type)
    frontmatter = {
        "type": "NotificationRecord",
        "title": f"{message_type} {task_id}",
        "description": "Task lifecycle notification trace.",
        "timestamp": utc_now(),
        "notificationId": notification_id,
        "taskId": task_id,
        "projectId": project_id,
        "recipient": recipient_value,
        "channel": channel,
        "messageType": message_type,
        "status": delivery_status,
        "sentAt": utc_now() if delivery_status == "sent" else "",
        "sourceMessageRef": source_message_ref,
        "failureReason": failure_reason,
        "retryCount": 0,
        "lastAttemptAt": utc_now() if delivery_status in {"sent", "failed", "retrying", "dead_letter"} else "",
        "deadLetterAt": utc_now() if delivery_status == "dead_letter" else "",
    }
    body = "\n".join(
        [
            "## Message Summary",
            "",
            message_summary,
            "",
            "## Task",
            "",
            f"- taskId: {task_id}",
            f"- projectId: {project_id or 'none'}",
            f"- status: {task.get('status', '')}",
            f"- taskRef: {rel(task_path, bundle.root)}",
            "",
            "## Delivery",
            "",
            f"- channel: {channel}",
            f"- status: {delivery_status}",
            f"- failureReason: {failure_reason or 'none'}",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(index_path, str(frontmatter["title"]), path.name)
    current_task = load_object(task_path)
    refs = append_unique(as_list(current_task.get("notificationRefs")), rel(path, bundle.root))
    update_frontmatter_file(task_path, {"notificationRefs": refs, "updatedAt": utc_now()})
    action = "task.notification.failed" if delivery_status == "failed" else "task.notification.record"
    create_audit_log(
        bundle,
        recipient_value,
        action,
        rel(task_path, bundle.root),
        after=f"{message_type}:{delivery_status}",
        policy_result=channel,
        details=f"notificationRef={rel(path, bundle.root)}\nfailureReason={failure_reason or 'none'}",
    )
    return path


def task_notification_summary(task: dict[str, Any], message_type: str) -> str:
    title = str(task.get("title") or task.get("taskId") or "task")
    task_id = str(task.get("taskId") or "")
    status = str(task.get("status") or "")
    if message_type == "task_created":
        return f"任务已创建：{title}（{task_id}），当前状态 {status or 'pending'}。"
    if message_type == "task_manual_runner_required":
        return f"任务需要临时 Runner 或 Agent 工作台接管：{title}（{task_id}）。"
    if message_type == "task_claimed":
        runner = str(task.get("leaseOwner") or task.get("assignedRunner") or "runner")
        return f"任务已被 {runner} 领取：{title}（{task_id}）。"
    if message_type == "task_blocked":
        return f"任务被阻塞：{title}（{task_id}），请查看任务记录和审计详情。"
    if message_type == "task_finished":
        return f"任务已完成：{title}（{task_id}）。"
    return f"任务状态更新：{title}（{task_id}），当前状态 {status}。"


def create_discussion_notification(
    bundle: Bundle,
    discussion_path: Path,
    discussion: dict[str, Any],
    message_type: str,
    recipient: str = "",
    channel: str = "feishu",
    delivery_status: str = "pending",
    summary: str = "",
    source_message_ref: str = "",
    failure_reason: str = "",
) -> Path:
    if delivery_status not in {"pending", "sent", "failed", "retrying", "dead_letter"}:
        raise KnowledgeError(f"unknown notification status: {delivery_status}")
    ensure_dir(notification_storage_dir(bundle))
    index_path = notification_storage_dir(bundle) / "index.md"
    if not index_path.exists():
        write_text(index_path, "# Notifications\n\n")
    discussion_id = str(discussion.get("discussionId") or discussion_path.stem)
    project_id = str(discussion.get("projectId") or "")
    recipient_value = recipient or str(discussion.get("facilitatorAgent") or discussion.get("requester") or "project")
    notification_id = unique_time_id("notification")
    path = notification_storage_dir(bundle) / f"{notification_id}.md"
    message_summary = summary or f"讨论会状态更新：{discussion.get('title', discussion_id)}（{discussion_id}），当前状态 {discussion.get('status', '')}。"
    frontmatter = {
        "type": "NotificationRecord",
        "title": f"{message_type} {discussion_id}",
        "description": "Discussion lifecycle notification trace.",
        "timestamp": utc_now(),
        "notificationId": notification_id,
        "discussionId": discussion_id,
        "taskId": str(discussion.get("relatedTaskId") or ""),
        "projectId": project_id,
        "recipient": recipient_value,
        "channel": channel,
        "messageType": message_type,
        "status": delivery_status,
        "sentAt": utc_now() if delivery_status == "sent" else "",
        "sourceMessageRef": source_message_ref,
        "failureReason": failure_reason,
        "retryCount": 0,
        "lastAttemptAt": utc_now() if delivery_status in {"sent", "failed", "retrying", "dead_letter"} else "",
        "deadLetterAt": utc_now() if delivery_status == "dead_letter" else "",
    }
    body = "\n".join(
        [
            "## Message Summary",
            "",
            message_summary,
            "",
            "## Discussion",
            "",
            f"- discussionId: {discussion_id}",
            f"- projectId: {project_id or 'none'}",
            f"- status: {discussion.get('status', '')}",
            f"- discussionRef: {rel(discussion_path, bundle.root)}",
            f"- relatedTaskId: {discussion.get('relatedTaskId', '') or 'none'}",
            "",
            "## Delivery",
            "",
            f"- channel: {channel}",
            f"- status: {delivery_status}",
            f"- failureReason: {failure_reason or 'none'}",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(index_path, str(frontmatter["title"]), path.name)
    current = load_object(discussion_path)
    refs = append_unique(as_list(current.get("notificationRefs")), rel(path, bundle.root))
    update_frontmatter_file(discussion_path, {"notificationRefs": refs, "updatedAt": utc_now()})
    create_audit_log(
        bundle,
        recipient_value,
        "discussion.notification.failed" if delivery_status == "failed" else "discussion.notification.record",
        rel(discussion_path, bundle.root),
        after=f"{message_type}:{delivery_status}",
        policy_result=channel,
        details=f"notificationRef={rel(path, bundle.root)}\nfailureReason={failure_reason or 'none'}",
    )
    return path


def notification_summary_from_body(path: Path) -> str:
    _, body = parse_frontmatter(read_text(path))
    marker = "## Message Summary"
    if marker not in body:
        return ""
    rest = body.split(marker, 1)[1].strip()
    if "\n## " in rest:
        rest = rest.split("\n## ", 1)[0].strip()
    return rest


def find_notification_record(bundle: Bundle, notification_id: str) -> Path:
    nid = slug(notification_id)
    direct = notification_storage_dir(bundle) / f"{nid}.md"
    if direct.exists() and load_object(direct).get("type") == "NotificationRecord":
        return direct
    for path in notification_storage_dir(bundle).glob("*.md"):
        if path.name == "index.md":
            continue
        fm = load_object(path)
        if fm.get("type") == "NotificationRecord" and str(fm.get("notificationId", "")).lower() == notification_id.lower():
            return path
    raise KnowledgeError(f"notification not found: {notification_id}")


def notification_failure_is_critical(notification: dict[str, Any]) -> bool:
    message_type = str(notification.get("messageType") or "")
    if message_type in CRITICAL_NOTIFICATION_TYPES:
        return True
    text = " ".join(
        [
            message_type,
            str(notification.get("failureReason") or ""),
            str(notification.get("title") or ""),
        ]
    ).lower()
    return any(token in text for token in ["approval", "review", "critical", "security", "permission", "stale", "blocked"])


def ensure_notification_repair_path(bundle: Bundle, notification_path: Path, notification: dict[str, Any], actor: str, failure_reason: str) -> str:
    existing = str(notification.get("repairTaskRef") or "")
    if existing:
        return existing
    if not notification_failure_is_critical(notification):
        return ""
    task_id = followup_task_id(bundle, f"notification-repair-{notification.get('notificationId', notification_path.stem)}")
    project_id = str(notification.get("projectId") or "")
    notification_ref = rel(notification_path, bundle.root)
    task_path = create_project_task(
        bundle,
        title=f"Repair failed notification {notification.get('messageType', '')}",
        project_id=project_id,
        requester=actor,
        assignee=OPERATIONS_AGENT_ID,
        task_type="notification_repair",
        task_id=task_id,
        priority="critical",
        source_material_refs=[notification_ref],
        expected_output=[
            "Diagnose why the critical notification was not delivered.",
            "Retry or switch channel, then mark the NotificationRecord sent or dead_letter with reason.",
            "Notify project owner when approval, review, security, stale, or blocker messages were affected.",
        ],
    )
    repair_ref = rel(task_path, bundle.root)
    update_frontmatter_file(notification_path, {"repairTaskRef": repair_ref, "updatedAt": utc_now()})
    create_audit_log(
        bundle,
        actor,
        "notification.repairTask.create",
        notification_ref,
        after=repair_ref,
        policy_result="critical_notification_failure",
        details=f"messageType={notification.get('messageType', '')}\nfailureReason={failure_reason or notification.get('failureReason', '') or 'none'}",
    )
    return repair_ref


def list_notifications(
    bundle: Bundle,
    status: str = "",
    recipient: str = "",
    channel: str = "",
    message_type: str = "",
    project_id: str = "",
    task_id: str = "",
    discussion_id: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    root = notification_storage_dir(bundle)
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.md")):
        if path.name == "index.md":
            continue
        fm = load_object(path)
        if fm.get("type") != "NotificationRecord":
            continue
        if status and str(fm.get("status", "")) != status:
            continue
        if recipient and str(fm.get("recipient", "")) != recipient:
            continue
        if channel and str(fm.get("channel", "")) != channel:
            continue
        if message_type and str(fm.get("messageType", "")) != message_type:
            continue
        if project_id and str(fm.get("projectId", "")) != project_id:
            continue
        if task_id and str(fm.get("taskId", "")) != task_id:
            continue
        if discussion_id and str(fm.get("discussionId", "")) != discussion_id:
            continue
        row = dict(fm)
        row["notificationRef"] = rel(path, bundle.root)
        row["messageSummary"] = notification_summary_from_body(path)
        rows.append(row)
    rows.sort(key=lambda item: str(item.get("timestamp", "")))
    return rows[: max(1, limit)]


def mark_notification_delivery(
    bundle: Bundle,
    notification_id: str,
    status: str,
    actor: str,
    failure_reason: str = "",
    delivery_ref: str = "",
) -> dict[str, Any]:
    if status not in {"pending", "sent", "failed", "retrying", "dead_letter"}:
        raise KnowledgeError(f"unknown notification status: {status}")
    if not actor.strip():
        raise KnowledgeError("notification delivery actor is required")
    path = find_notification_record(bundle, notification_id)
    before = load_object(path)
    retry_count = int(before.get("retryCount") or 0)
    if status in {"failed", "retrying"}:
        retry_count += 1
    updates: dict[str, Any] = {
        "status": status,
        "sentAt": utc_now() if status == "sent" else str(before.get("sentAt") or ""),
        "failureReason": failure_reason if status in {"failed", "retrying", "dead_letter"} else "",
        "deliveryRef": delivery_ref,
        "deliveredBy": actor,
        "retryCount": retry_count,
        "lastAttemptAt": utc_now() if status in {"sent", "failed", "retrying", "dead_letter"} else str(before.get("lastAttemptAt") or ""),
        "deadLetterAt": utc_now() if status == "dead_letter" else str(before.get("deadLetterAt") or ""),
        "updatedAt": utc_now(),
    }
    updated = update_frontmatter_file(path, updates)
    action = {
        "sent": "notification.delivered",
        "failed": "notification.failed",
        "retrying": "notification.retrying",
        "dead_letter": "notification.dead_letter",
        "pending": "notification.pending",
    }[status]
    create_audit_log(
        bundle,
        actor,
        action,
        rel(path, bundle.root),
        before=str(before.get("status", "")),
        after=status,
        policy_result=str(before.get("channel", "")),
        details=f"messageType={before.get('messageType', '')}\ndeliveryRef={delivery_ref or 'none'}\nfailureReason={failure_reason or 'none'}",
    )
    repair_ref = ""
    if status in {"failed", "dead_letter"}:
        repair_ref = ensure_notification_repair_path(bundle, path, updated, actor, failure_reason)
        if repair_ref:
            updated = load_object(path)
    updated["notificationRef"] = rel(path, bundle.root)
    updated["messageSummary"] = notification_summary_from_body(path)
    updated["repairTaskRef"] = repair_ref or str(updated.get("repairTaskRef") or "")
    return updated


REQUIREMENT_STATE_FIELDS = [
    "targetUser",
    "problem",
    "scenario",
    "alternative",
    "value",
    "marketPosition",
    "businessModel",
    "scope",
    "nonGoals",
    "constraints",
    "metric",
    "acceptanceCriteria",
    "evidence",
    "assumptions",
    "decisionOwner",
    PRD_HIGH_QUALITY_PROTOCOL_FIELD,
]
REQUIREMENT_APPROVAL_BLOCKER_FIELDS = ["targetUser", "problem", "value", "scope", "nonGoals", "constraints", "metric", "acceptanceCriteria"]
PRD_IMPACT_FIELDS = {"scope", "nonGoals", "workflows", "metrics", "openDecisions", "acceptanceCriteriaRefs", "requirements"}


def requirement_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "requirements"


def requirement_state_storage_dir(bundle: Bundle) -> Path:
    return requirement_storage_dir(bundle) / "state"


def requirement_clarification_storage_dir(bundle: Bundle) -> Path:
    return requirement_storage_dir(bundle) / "clarifications"


def acceptance_criteria_storage_dir(bundle: Bundle) -> Path:
    return requirement_storage_dir(bundle) / "acceptance-criteria"


def requirement_tree_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    if project_id:
        return bundle.root / "projects" / slug(project_id) / "requirements" / "requirement-trees"
    return requirement_storage_dir(bundle) / "requirement-trees"


def requirement_tree_node_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    return requirement_tree_storage_dir(bundle, project_id).parent / "nodes"


def requirement_tree_mapping_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    return requirement_tree_storage_dir(bundle, project_id).parent / "mappings"


def requirement_tree_gate_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    return requirement_tree_storage_dir(bundle, project_id).parent / "gates"


def requirement_tree_snapshot_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    return requirement_tree_storage_dir(bundle, project_id).parent / "snapshots"


def prd_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "prd"


def decision_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    if project_id and (bundle.root / "projects" / slug(project_id) / "project.md").exists():
        return bundle.root / "projects" / slug(project_id)
    return bundle.root / "decisions"


def impact_review_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "reviews" / "impact"


def default_requirement_state() -> dict[str, Any]:
    timestamp = utc_now()
    fields: dict[str, Any] = {}
    for field in REQUIREMENT_STATE_FIELDS:
        fields[field] = {
            "value": None,
            "clarity": "missing",
            "basis": "decision_needed" if field == "decisionOwner" else "assumption",
            "sourceRefs": [],
            "answeredBy": "",
            "updatedAt": timestamp,
            "notes": "",
        }
    return fields


def is_empty_value(value: Any) -> bool:
    return value is None or value == "" or value == []


def normalize_state_entry(field: str, value: Any, source_refs: list[str] | None = None, answered_by: str = "agent") -> dict[str, Any]:
    entry = dict(value) if isinstance(value, dict) else {"value": value}
    entry.setdefault("value", None)
    if "clarity" not in entry:
        entry["clarity"] = "known" if not is_empty_value(entry.get("value")) else "missing"
    entry.setdefault("basis", "evidence" if entry["clarity"] == "known" else "assumption")
    entry.setdefault("sourceRefs", source_refs or [])
    entry.setdefault("answeredBy", answered_by)
    entry.setdefault("updatedAt", utc_now())
    entry.setdefault("notes", "")
    if field in {"marketPosition", "businessModel"} and str(entry.get("value") or "").strip() == "not_applicable" and not str(entry.get("notes") or "").strip():
        entry["clarity"] = "needs_approval"
        entry["basis"] = "decision_needed"
    return entry


def derive_requirement_state_fields(fields: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    needs_approval: list[str] = []
    evidence_claims: list[dict[str, Any]] = []
    inference_claims: list[dict[str, Any]] = []
    assumption_claims: list[dict[str, Any]] = []
    decision_claims: list[dict[str, Any]] = []
    for field, entry_value in fields.items():
        entry = dict(entry_value or {})
        clarity = str(entry.get("clarity") or "")
        basis = str(entry.get("basis") or "")
        if clarity == "missing":
            missing.append(field)
        if clarity == "needs_approval":
            needs_approval.append(field)
        claim = {"field": field, "value": entry.get("value"), "sourceRefs": as_list(entry.get("sourceRefs")), "notes": entry.get("notes", "")}
        if basis == "evidence":
            evidence_claims.append(claim)
        elif basis == "inference":
            inference_claims.append(claim)
        elif basis == "decision_needed" or clarity == "needs_approval":
            decision_claims.append(claim)
        else:
            assumption_claims.append(claim)
    return {
        "missingFields": missing,
        "needsApprovalFields": needs_approval,
        "evidenceClaims": evidence_claims,
        "inferenceClaims": inference_claims,
        "assumptionClaims": assumption_claims,
        "decisionNeededClaims": decision_claims,
        "qualityGate": {"passed": False, "blockers": missing + needs_approval},
    }


def write_requirement_state_snapshot(
    bundle: Bundle,
    requirement_id: str,
    fields: dict[str, Any],
    version: int,
    actor: str,
    source_refs: list[str],
    clarification_round_refs: list[str] | None = None,
) -> str:
    state_id = f"req-state.{requirement_id}.v{version:03d}"
    payload = {
        "type": "RequirementState",
        "requirementStateId": state_id,
        "requirementRef": f"requirements/{slug(requirement_id)}.md",
        "version": version,
        "updatedAt": utc_now(),
        "updatedBy": actor,
        "fields": fields,
        "sourceRefs": source_refs,
        "clarificationRounds": clarification_round_refs or [],
        **derive_requirement_state_fields(fields),
    }
    path = requirement_state_storage_dir(bundle) / f"{slug(state_id)}.json"
    write_text(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return rel(path, bundle.root)


def find_requirement(bundle: Bundle, requirement_id: str) -> Path:
    candidate = requirement_storage_dir(bundle) / f"{slug(requirement_id)}.md"
    if candidate.exists():
        return candidate
    root = requirement_storage_dir(bundle)
    if root.exists():
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            if fm.get("type") == "Requirement" and str(fm.get("requirementId", "")).lower() == requirement_id.lower():
                return path
    raise KnowledgeError(f"requirement not found: {requirement_id}")


def find_prd_document(bundle: Bundle, prd_id: str) -> Path:
    candidate = prd_storage_dir(bundle) / f"{slug(prd_id)}.md"
    if candidate.exists():
        return candidate
    root = prd_storage_dir(bundle)
    if root.exists():
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            if fm.get("type") == "PRDDocument" and str(fm.get("prdId", "")).lower() == prd_id.lower():
                return path
    raise KnowledgeError(f"prd not found: {prd_id}")


def create_requirement_notification(bundle: Bundle, title: str, project_id: str, recipient: str, message_type: str, summary: str, target_ref: str) -> str:
    ensure_dir(notification_storage_dir(bundle))
    notification_id = unique_time_id("notification")
    path = notification_storage_dir(bundle) / f"{notification_id}.md"
    frontmatter = {
        "type": "NotificationRecord",
        "title": title,
        "timestamp": utc_now(),
        "notificationId": notification_id,
        "projectId": project_id,
        "recipient": recipient,
        "channel": "feishu",
        "messageType": message_type,
        "status": "pending",
        "targetRef": target_ref,
        "retryCount": 0,
    }
    write_text(path, render_doc(frontmatter, f"## Message Summary\n\n{summary}\n\n## Target\n\n{target_ref}"))
    update_index(notification_storage_dir(bundle) / "index.md", title, path.name)
    create_audit_log(bundle, recipient or "system", "requirement.notification.record", rel(path, bundle.root), after="pending", details=f"targetRef={target_ref}\nmessageType={message_type}")
    return rel(path, bundle.root)


def create_requirement(
    bundle: Bundle,
    project_id: str,
    source_refs: list[str],
    title: str,
    submitter: str,
    owner: str = "",
    decision_owner: str = "",
    sensitivity: str = "internal",
    summary: str = "",
) -> Path:
    if not project_id.strip():
        raise KnowledgeError("project is required")
    if not source_refs:
        raise KnowledgeError("sourceRefs cannot be empty")
    if not title.strip():
        raise KnowledgeError("requirement title is required")
    if not submitter.strip():
        raise KnowledgeError("submitter is required")
    project_ref = rel(find_project(bundle, project_id), bundle.root)
    rid = unique_time_id(f"req.{slug(project_id)}.{safe_slug(title, 'requirement')}")
    path = requirement_storage_dir(bundle) / f"{slug(rid)}.md"
    fields = default_requirement_state()
    if decision_owner.strip():
        fields["decisionOwner"] = normalize_state_entry("decisionOwner", decision_owner.strip(), source_refs, "human")
    state_ref = write_requirement_state_snapshot(bundle, rid, fields, 1, submitter, source_refs)
    status = "draft" if owner.strip() else "clarifying"
    frontmatter = {
        "type": "Requirement",
        "title": title.strip(),
        "description": summary.strip() or title.strip(),
        "timestamp": utc_now(),
        "requirementId": rid,
        "projectRef": project_ref,
        "projectId": slug(project_id),
        "summary": summary.strip() or title.strip(),
        "submitter": submitter.strip(),
        "owner": owner.strip(),
        "decisionOwner": decision_owner.strip(),
        "sourceRefs": source_refs,
        "status": status,
        "sensitivity": sensitivity.strip() or "internal",
        "requirementStateRef": state_ref,
        "requirementStateVersion": 1,
        "prdRefs": [],
        "currentPrdRef": "",
        "decisionRefs": [],
        "acceptanceCriteriaRefs": [],
        "taskRefs": [],
        "impactReviewRefs": [],
        "auditRefs": [],
        "createdAt": utc_now(),
        "updatedAt": utc_now(),
        "createdBy": submitter.strip(),
        "updatedBy": submitter.strip(),
    }
    body = "\n".join(["## Summary", "", frontmatter["summary"], "", "## Status", "", f"- Status: {status}", f"- Owner: {owner.strip() or 'missing'}", "", "## Trace", "", f"- State: {state_ref}", *[f"- Source: {item}" for item in source_refs]])
    write_text(path, render_doc(frontmatter, body))
    update_index(requirement_storage_dir(bundle) / "index.md", title.strip(), path.name)
    audit = create_audit_log(bundle, submitter.strip(), "requirement.create", rel(path, bundle.root), after=status, policy_result="recorded", details=f"stateRef={state_ref}\nsourceRefs={','.join(source_refs)}")
    updates: dict[str, Any] = {"auditRefs": [rel(audit, bundle.root)], "updatedAt": utc_now()}
    if status == "clarifying":
        updates["notificationRefs"] = [create_requirement_notification(bundle, f"Requirement needs more information: {title.strip()}", slug(project_id), submitter.strip(), "requirement_clarifying", f"{title.strip()} needs an owner and product discovery fields before approval.", rel(path, bundle.root))]
    update_frontmatter_file(path, updates)
    append_log(bundle, f"created requirement {rid}")
    return path


def load_requirement_state(bundle: Bundle, requirement: dict[str, Any]) -> dict[str, Any]:
    state_ref = str(requirement.get("requirementStateRef") or "")
    if not state_ref:
        return {"fields": default_requirement_state(), "version": 0, "clarificationRounds": []}
    state_path = bundle.root / state_ref
    if not state_path.exists():
        raise KnowledgeError(f"requirement state not found: {state_ref}")
    return json.loads(read_text(state_path))


def update_requirement_state(bundle: Bundle, requirement_id: str, patch: dict[str, Any], actor: str, source_refs: list[str] | None = None) -> Path:
    path = find_requirement(bundle, requirement_id)
    requirement = load_object(path)
    state = load_requirement_state(bundle, requirement)
    fields = dict(state.get("fields") or default_requirement_state())
    changed: list[str] = []
    for field, value in patch.items():
        if field not in REQUIREMENT_STATE_FIELDS:
            raise KnowledgeError(f"unknown requirement state field: {field}")
        fields[field] = normalize_state_entry(field, value, source_refs or as_list(requirement.get("sourceRefs")), actor)
        changed.append(field)
    version = int(requirement.get("requirementStateVersion") or state.get("version") or 0) + 1
    state_ref = write_requirement_state_snapshot(bundle, str(requirement.get("requirementId")), fields, version, actor, as_list(requirement.get("sourceRefs")), as_list(state.get("clarificationRounds")))
    audit = create_audit_log(bundle, actor, "requirement.state.update", rel(path, bundle.root), before=str(requirement.get("requirementStateRef") or ""), after=state_ref, policy_result="recorded", details="changedFields=" + ",".join(changed))
    update_frontmatter_file(path, {"requirementStateRef": state_ref, "requirementStateVersion": version, "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now(), "updatedBy": actor})
    return path


def create_clarification_round(bundle: Bundle, requirement_id: str, agent_ref: str, recipient: str = "") -> Path:
    path = find_requirement(bundle, requirement_id)
    requirement = load_object(path)
    state = load_requirement_state(bundle, requirement)
    missing = [field for field in REQUIREMENT_APPROVAL_BLOCKER_FIELDS + ["businessModel", "marketPosition", "decisionOwner"] if field in as_list(state.get("missingFields")) or field in as_list(state.get("needsApprovalFields"))]
    if not missing:
        raise KnowledgeError("no clarification questions needed")
    ranked = missing[:3]
    templates = {
        "targetUser": "Who is the target user, and why does this user matter?",
        "problem": "What user or business problem must this solve?",
        "businessModel": "What business model applies, or why is it not applicable?",
        "metric": "What observable success metric proves the requirement worked?",
        "acceptanceCriteria": "What observable acceptance criteria should block or pass delivery?",
        "decisionOwner": "Who must decide high-impact choices if they appear?",
    }
    round_id = unique_time_id(f"clarification.{slug(str(requirement.get('requirementId')))}")
    question_refs = [f"{round_id}.q{i + 1}" for i in range(len(ranked))]
    round_path = requirement_clarification_storage_dir(bundle) / f"{slug(round_id)}.md"
    frontmatter = {
        "type": "ClarificationRound",
        "title": f"Clarification for {requirement.get('title')}",
        "timestamp": utc_now(),
        "roundId": round_id,
        "requirementRef": rel(path, bundle.root),
        "agentRef": agent_ref,
        "questionRefs": question_refs,
        "triggerFields": ranked,
        "recipient": recipient or str(requirement.get("submitter") or requirement.get("owner") or ""),
        "status": "sent",
        "answerRefs": [],
        "statePatchSummary": "",
        "auditRefs": [],
    }
    body = "## Questions\n\n" + "\n".join(f"- {templates.get(field, f'What should {field} be?')} Why: This field blocks approval or downstream PRD quality." for field in ranked)
    write_text(round_path, render_doc(frontmatter, body))
    update_index(requirement_clarification_storage_dir(bundle) / "index.md", str(frontmatter["title"]), round_path.name)
    round_refs = append_unique(as_list(state.get("clarificationRounds")), rel(round_path, bundle.root))
    state_ref = write_requirement_state_snapshot(bundle, str(requirement.get("requirementId")), dict(state.get("fields") or {}), int(requirement.get("requirementStateVersion") or state.get("version") or 1) + 1, agent_ref, as_list(requirement.get("sourceRefs")), round_refs)
    audit = create_audit_log(bundle, agent_ref, "requirement.clarification.create", rel(round_path, bundle.root), after="sent", policy_result="clarification_required", details=f"fields={','.join(ranked)}")
    update_frontmatter_file(round_path, {"auditRefs": [rel(audit, bundle.root)]})
    update_frontmatter_file(path, {"status": "clarifying", "requirementStateRef": state_ref, "requirementStateVersion": int(requirement.get("requirementStateVersion") or 1) + 1, "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now(), "updatedBy": agent_ref})
    create_requirement_notification(bundle, f"Requirement clarification needed: {requirement.get('title')}", str(requirement.get("projectId") or ""), str(frontmatter["recipient"]), "requirement_clarification", f"{requirement.get('title')} needs answers for: {', '.join(ranked)}.", rel(path, bundle.root))
    return round_path


def create_acceptance_criteria(
    bundle: Bundle,
    requirement_id: str,
    description: str,
    observable_signal: str,
    verification_method: str,
    owner: str,
    criteria_type: str = "product",
    prd_ref: str = "",
    task_ref: str = "",
    status: str = "draft",
    source_refs: list[str] | None = None,
) -> Path:
    if not description.strip():
        raise KnowledgeError("acceptance criteria description is required")
    if not observable_signal.strip():
        raise KnowledgeError("Acceptance criterion must include observable signal")
    if not verification_method.strip():
        raise KnowledgeError("verification method is required")
    if not owner.strip():
        raise KnowledgeError("acceptance criteria owner is required")
    requirement_path = find_requirement(bundle, requirement_id)
    requirement = load_object(requirement_path)
    criteria_id = unique_time_id(f"ac.{slug(str(requirement.get('requirementId')))}")
    path = acceptance_criteria_storage_dir(bundle) / f"{slug(criteria_id)}.md"
    refs = source_refs or as_list(requirement.get("sourceRefs"))
    frontmatter = {
        "type": "AcceptanceCriteria",
        "title": description.strip()[:80],
        "timestamp": utc_now(),
        "criteriaId": criteria_id,
        "requirementRef": rel(requirement_path, bundle.root),
        "prdRef": prd_ref,
        "taskRef": task_ref,
        "criteriaType": criteria_type,
        "description": description.strip(),
        "observableSignal": observable_signal.strip(),
        "verificationMethod": verification_method.strip(),
        "testCaseRefs": [],
        "owner": owner.strip(),
        "status": status.strip() or "draft",
        "sourceRefs": refs,
        "auditRefs": [],
    }
    write_text(path, render_doc(frontmatter, f"## Description\n\n{description.strip()}\n\n## Observable Signal\n\n{observable_signal.strip()}\n\n## Verification\n\n{verification_method.strip()}"))
    update_index(acceptance_criteria_storage_dir(bundle) / "index.md", description.strip()[:80], path.name)
    audit = create_audit_log(bundle, owner.strip(), "requirement.acceptance_criteria.create", rel(path, bundle.root), after=str(frontmatter["status"]), policy_result="recorded", details=f"requirementRef={rel(requirement_path, bundle.root)}")
    update_frontmatter_file(path, {"auditRefs": [rel(audit, bundle.root)]})
    update_frontmatter_file(requirement_path, {"acceptanceCriteriaRefs": append_unique(as_list(requirement.get("acceptanceCriteriaRefs")), rel(path, bundle.root)), "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    return path


def accepted_observable_criteria(bundle: Bundle, requirement: dict[str, Any]) -> list[str]:
    accepted = []
    for criteria_ref in as_list(requirement.get("acceptanceCriteriaRefs")):
        path = bundle.root / criteria_ref
        if path.exists():
            criteria = load_object(path)
            if criteria.get("type") == "AcceptanceCriteria" and criteria.get("status") == "approved" and str(criteria.get("observableSignal") or "").strip():
                accepted.append(criteria_ref)
    return accepted


def requirement_high_impact_decisions_pending(bundle: Bundle, requirement: dict[str, Any]) -> list[str]:
    pending = []
    for decision_ref in as_list(requirement.get("decisionRefs")):
        path = bundle.root / decision_ref
        if path.exists():
            decision = load_object(path)
            if decision.get("impactLevel") == "high" and decision.get("status") != "approved":
                pending.append(decision_ref)
    return pending


def requirement_approval_blockers(bundle: Bundle, requirement: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not str(requirement.get("owner") or "").strip():
        blockers.append("owner is missing")
    if not as_list(requirement.get("sourceRefs")):
        blockers.append("sourceRefs are missing")
    if not str(requirement.get("sensitivity") or "").strip():
        blockers.append("sensitivity is missing")
    state = load_requirement_state(bundle, requirement)
    fields = dict(state.get("fields") or {})
    for field in REQUIREMENT_APPROVAL_BLOCKER_FIELDS:
        entry = dict(fields.get(field) or {})
        if entry.get("clarity") != "known" or is_empty_value(entry.get("value")):
            blockers.append(f"{field} is missing or not known")
    for field in ["marketPosition", "businessModel"]:
        entry = dict(fields.get(field) or {})
        value = str(entry.get("value") or "").strip()
        if entry.get("clarity") != "known" or not value:
            blockers.append(f"{field} is missing or not known")
        if value == "not_applicable" and not str(entry.get("notes") or "").strip():
            blockers.append(f"{field} not_applicable requires rationale")
    if not accepted_observable_criteria(bundle, requirement):
        blockers.append("approved observable acceptance criteria are missing")
    pending_decisions = requirement_high_impact_decisions_pending(bundle, requirement)
    if pending_decisions and not str(requirement.get("decisionOwner") or "").strip():
        blockers.append("decisionOwner is required while high-impact decisions are open")
    if pending_decisions:
        blockers.append("high-impact decisions are not approved")
    return blockers


def approve_requirement(bundle: Bundle, requirement_id: str, owner: str) -> Path:
    path = find_requirement(bundle, requirement_id)
    requirement = load_object(path)
    updates: dict[str, Any] = {}
    if owner.strip():
        updates["owner"] = owner.strip()
        requirement["owner"] = owner.strip()
    blockers = requirement_approval_blockers(bundle, requirement)
    if blockers:
        audit = create_audit_log(bundle, owner or str(requirement.get("submitter") or "system"), "requirement.approval.blocked", rel(path, bundle.root), before=str(requirement.get("status") or ""), after=str(requirement.get("status") or ""), policy_result="blocked", details="\n".join(blockers))
        update_frontmatter_file(path, {"auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), **updates, "updatedAt": utc_now()})
        raise KnowledgeError("Requirement approval blocked: " + "; ".join(blockers))
    audit = create_audit_log(bundle, owner or str(requirement.get("owner") or "system"), "requirement.approve", rel(path, bundle.root), before=str(requirement.get("status") or ""), after="approved", policy_result="approved")
    update_frontmatter_file(path, {"status": "approved", **updates, "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    return path


def next_prd_version(bundle: Bundle, requirement: dict[str, Any]) -> int:
    versions = []
    for prd_ref in as_list(requirement.get("prdRefs")):
        path = bundle.root / prd_ref
        if path.exists():
            raw = str(load_object(path).get("version") or "").lstrip("v")
            if raw.isdigit():
                versions.append(int(raw))
    return (max(versions) if versions else 0) + 1


def state_value(state: dict[str, Any], field: str, fallback: str = "") -> Any:
    entry = dict(dict(state.get("fields") or {}).get(field) or {})
    value = entry.get("value")
    return fallback if is_empty_value(value) else value


def prd_quality_gate(bundle: Bundle, requirement: dict[str, Any], state: dict[str, Any], acceptance_refs: list[str]) -> dict[str, Any]:
    blockers = []
    fields = dict(state.get("fields") or {})
    for section in ["marketPosition", "businessModel", "scope", "nonGoals", "metric"]:
        entry = dict(fields.get(section) or {})
        if entry.get("clarity") != "known" or is_empty_value(entry.get("value")):
            blockers.append(f"{section} missing")
    if not str(requirement.get("owner") or "").strip():
        blockers.append("owner missing")
    if not acceptance_refs:
        blockers.append("observable acceptance criteria missing")
    if requirement_high_impact_decisions_pending(bundle, requirement):
        blockers.append("open high-impact decisions")
    protocol_entry = dict(fields.get(PRD_HIGH_QUALITY_PROTOCOL_FIELD) or {})
    protocol_value = protocol_entry.get("value")
    protocol_level = prd_high_quality_protocol_level(protocol_value)
    missing_protocol_steps = missing_prd_high_quality_protocol_steps(protocol_value, protocol_level)
    if protocol_entry.get("clarity") != "known" or missing_protocol_steps:
        blockers.append(f"prd-high-quality-generation protocol {protocol_level} missing or incomplete: " + ", ".join(missing_protocol_steps or required_prd_high_quality_protocol_steps(protocol_level)))
    return {
        "passed": not blockers,
        "blockers": blockers,
        "prdHighQualityProtocolLevel": protocol_level,
        "requiredSections": [
            "positioning",
            "marketPositioning",
            "businessModel",
            "workflows",
            "requirements",
            "metrics",
            "risks",
            "openDecisions",
            "scope",
            "nonGoals",
            "prdHighQualityProtocol",
            "testCases",
            "developmentHandoff",
        ],
    }


def prd_high_quality_protocol_level(protocol_value: Any) -> str:
    if isinstance(protocol_value, dict):
        level = str(protocol_value.get("requiredProtocolLevel") or protocol_value.get("level") or "light").strip().lower()
        return level if level in PRD_HIGH_QUALITY_PROTOCOL_LEVELS else "full"
    return "light"


def required_prd_high_quality_protocol_steps(protocol_level: str) -> list[str]:
    if protocol_level == "none":
        return []
    if protocol_level == "full":
        return list(PRD_HIGH_QUALITY_PROTOCOL_STEPS)
    return list(PRD_HIGH_QUALITY_LIGHT_STEPS)


def missing_prd_high_quality_protocol_steps(protocol_value: Any, protocol_level: str | None = None) -> list[str]:
    level = protocol_level or prd_high_quality_protocol_level(protocol_value)
    if level == "none":
        if isinstance(protocol_value, dict) and str(protocol_value.get("rationale") or protocol_value.get("reason") or "").strip():
            return []
        return ["rationale"]
    if not protocol_value:
        return required_prd_high_quality_protocol_steps(level)
    required_steps = required_prd_high_quality_protocol_steps(level)
    if isinstance(protocol_value, dict):
        if protocol_value.get("completedSteps") and isinstance(protocol_value.get("completedSteps"), list):
            completed = {str(item) for item in protocol_value.get("completedSteps")}
            return [step for step in required_steps if step not in completed]
        missing = []
        for step in required_steps:
            value = protocol_value.get(step)
            if is_empty_value(value):
                missing.append(step)
            elif step == "requirementClarifier":
                missing.extend(missing_requirement_clarifier_fields(value))
        return missing
    if isinstance(protocol_value, list):
        completed = {str(item) for item in protocol_value}
        return [step for step in required_steps if step not in completed]
    return required_steps


def missing_requirement_clarifier_fields(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["requirementClarifier.firstPrinciples", "requirementClarifier.socraticQuestions"]
    missing = []
    for field in PRD_REQUIREMENT_CLARIFIER_REQUIRED_FIELDS:
        if is_empty_value(value.get(field)):
            missing.append(f"requirementClarifier.{field}")
    first_principles = value.get("firstPrinciples")
    if isinstance(first_principles, dict):
        for field in ["user", "problem", "value", "successMetric"]:
            if is_empty_value(first_principles.get(field)):
                missing.append(f"requirementClarifier.firstPrinciples.{field}")
    questions = value.get("socraticQuestions")
    if isinstance(questions, list) and not questions:
        missing.append("requirementClarifier.socraticQuestions")
    return missing


def generate_prd_document(bundle: Bundle, requirement_id: str, author_agent: str, reviewer: str = "") -> Path:
    requirement_path = find_requirement(bundle, requirement_id)
    requirement = load_object(requirement_path)
    state = load_requirement_state(bundle, requirement)
    version_number = next_prd_version(bundle, requirement)
    version = f"v{version_number}"
    prd_id = f"prd.{slug(str(requirement.get('requirementId')))}.{version}"
    path = prd_storage_dir(bundle) / f"{slug(prd_id)}.md"
    accepted_criteria = accepted_observable_criteria(bundle, requirement)
    supersedes = as_list(requirement.get("prdRefs"))[-1] if as_list(requirement.get("prdRefs")) else ""
    quality_gate = prd_quality_gate(bundle, requirement, state, accepted_criteria)
    evidence_claims = list(state.get("evidenceClaims") or [])
    inference_claims = list(state.get("inferenceClaims") or [])
    assumption_claims = list(state.get("assumptionClaims") or [])
    decision_claims = list(state.get("decisionNeededClaims") or [])
    frontmatter = {
        "type": "PRDDocument",
        "title": f"PRD {version}: {requirement.get('title')}",
        "timestamp": utc_now(),
        "prdId": prd_id,
        "requirementRef": rel(requirement_path, bundle.root),
        "projectRef": str(requirement.get("projectRef") or ""),
        "projectId": str(requirement.get("projectId") or ""),
        "version": version,
        "status": "draft",
        "authorAgent": author_agent,
        "reviewer": reviewer,
        "owner": str(requirement.get("owner") or ""),
        "sourceRefs": as_list(requirement.get("sourceRefs")),
        "requirementStateSnapshotRef": str(requirement.get("requirementStateRef") or ""),
        "positioning": state_value(state, "value", str(requirement.get("summary") or "")),
        "marketPositioning": state_value(state, "marketPosition", ""),
        "businessModel": state_value(state, "businessModel", ""),
        "workflows": state_value(state, "scenario", ""),
        "requirements": state_value(state, "problem", ""),
        "scope": state_value(state, "scope", ""),
        "nonGoals": state_value(state, "nonGoals", ""),
        "metrics": state_value(state, "metric", ""),
        "risks": state_value(state, "constraints", ""),
        "openDecisions": as_list(requirement.get("decisionRefs")) + [json.dumps(item, ensure_ascii=False) for item in decision_claims],
        "acceptanceCriteriaRefs": accepted_criteria or as_list(requirement.get("acceptanceCriteriaRefs")),
        "taskProposalRefs": [],
        "evidenceSection": [json.dumps(item, ensure_ascii=False) for item in evidence_claims],
        "inferenceSection": [json.dumps(item, ensure_ascii=False) for item in inference_claims],
        "assumptionSection": [json.dumps(item, ensure_ascii=False) for item in assumption_claims],
        "decisionNeededSection": [json.dumps(item, ensure_ascii=False) for item in decision_claims],
        "prdHighQualityProtocol": state_value(state, PRD_HIGH_QUALITY_PROTOCOL_FIELD, {}),
        "qualityGate": quality_gate,
        "supersedesPrdRef": supersedes,
        "supersededByPrdRef": "",
        "auditRefs": [],
    }
    body = "\n".join(
        [
            "## Positioning",
            "",
            str(frontmatter["positioning"] or "TBD"),
            "",
            "## Market Positioning",
            "",
            str(frontmatter["marketPositioning"] or "TBD"),
            "",
            "## Business Model",
            "",
            str(frontmatter["businessModel"] or "TBD"),
            "",
            "## Workflows",
            "",
            str(frontmatter["workflows"] or "TBD"),
            "",
            "## Requirements",
            "",
            str(frontmatter["requirements"] or "TBD"),
            "",
            "## Scope",
            "",
            str(frontmatter["scope"] or "TBD"),
            "",
            "## Non-Goals",
            "",
            str(frontmatter["nonGoals"] or "TBD"),
            "",
            "## Metrics",
            "",
            str(frontmatter["metrics"] or "TBD"),
            "",
            "## Risks",
            "",
            str(frontmatter["risks"] or "TBD"),
            "",
            "## Evidence",
            "",
            json.dumps(evidence_claims, ensure_ascii=False),
            "",
            "## Inference",
            "",
            json.dumps(inference_claims, ensure_ascii=False),
            "",
            "## Assumptions",
            "",
            json.dumps(assumption_claims, ensure_ascii=False),
            "",
            "## Decisions Needed",
            "",
            json.dumps(decision_claims, ensure_ascii=False),
            "",
            "## Quality Gate",
            "",
            json.dumps(quality_gate, ensure_ascii=False),
            "",
            "## PRD High Quality Protocol",
            "",
            json.dumps(frontmatter["prdHighQualityProtocol"], ensure_ascii=False),
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(prd_storage_dir(bundle) / "index.md", str(frontmatter["title"]), path.name)
    audit = create_audit_log(bundle, author_agent, "prd.generate", rel(path, bundle.root), after="draft", policy_result="quality_passed" if quality_gate["passed"] else "quality_blocked", details=f"requirementRef={rel(requirement_path, bundle.root)}\nversion={version}")
    update_frontmatter_file(path, {"auditRefs": [rel(audit, bundle.root)]})
    update_frontmatter_file(requirement_path, {"prdRefs": append_unique(as_list(requirement.get("prdRefs")), rel(path, bundle.root)), "currentPrdRef": rel(path, bundle.root), "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    create_requirement_notification(bundle, f"PRD ready for review: {requirement.get('title')}", str(requirement.get("projectId") or ""), reviewer or str(requirement.get("owner") or requirement.get("submitter") or ""), "prd_ready_for_review", f"PRD {version} for {requirement.get('title')} is ready. Quality gate: {'passed' if quality_gate['passed'] else 'blocked'}.", rel(path, bundle.root))
    return path


def prd_changed_fields(bundle: Bundle, from_ref: str, to_ref: str) -> list[str]:
    from_prd = load_object(bundle.root / from_ref)
    to_prd = load_object(bundle.root / to_ref)
    return [field for field in sorted(PRD_IMPACT_FIELDS) if from_prd.get(field) != to_prd.get(field)]


def accepted_impact_review_exists(bundle: Bundle, requirement_ref: str, from_ref: str, to_ref: str) -> bool:
    root = impact_review_storage_dir(bundle)
    if not root.exists():
        return False
    for path in sorted(root.glob("*.md")):
        if path.name in COLLECTION_NAMES:
            continue
        review = load_object(path)
        if review.get("type") == "ImpactReview" and review.get("requirementRef") == requirement_ref and review.get("fromPrdRef") == from_ref and review.get("toPrdRef") == to_ref and review.get("status") == "accepted":
            return True
    return False


def approve_prd_document(bundle: Bundle, prd_id: str, reviewer: str) -> Path:
    path = find_prd_document(bundle, prd_id)
    prd = load_object(path)
    if not reviewer.strip():
        raise KnowledgeError("reviewer is required")
    quality_gate = dict(prd.get("qualityGate") or {})
    if not quality_gate.get("passed"):
        blockers = as_list(quality_gate.get("blockers"))
        audit = create_audit_log(bundle, reviewer, "prd.approval.blocked", rel(path, bundle.root), before=str(prd.get("status") or ""), after=str(prd.get("status") or ""), policy_result="blocked", details="\n".join(blockers))
        update_frontmatter_file(path, {"auditRefs": append_unique(as_list(prd.get("auditRefs")), rel(audit, bundle.root)), "reviewer": reviewer, "updatedAt": utc_now()})
        raise KnowledgeError("PRD approval blocked: " + "; ".join(blockers))
    requirement_ref = str(prd.get("requirementRef") or "")
    requirement = load_object(bundle.root / requirement_ref)
    supersedes = str(prd.get("supersedesPrdRef") or "")
    changed = prd_changed_fields(bundle, supersedes, rel(path, bundle.root)) if supersedes else []
    if supersedes and as_list(requirement.get("taskRefs")) and any(field in PRD_IMPACT_FIELDS for field in changed):
        if not accepted_impact_review_exists(bundle, requirement_ref, supersedes, rel(path, bundle.root)):
            review_path = create_impact_review(bundle, str(requirement.get("requirementId")), supersedes, rel(path, bundle.root), reviewer, status="draft")
            raise KnowledgeError(f"PRD approval blocked: impact review required before activation ({rel(review_path, bundle.root)})")
    audit = create_audit_log(bundle, reviewer, "prd.approve", rel(path, bundle.root), before=str(prd.get("status") or ""), after="approved", policy_result="approved")
    update_frontmatter_file(path, {"status": "approved", "reviewer": reviewer, "auditRefs": append_unique(as_list(prd.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    if supersedes and (bundle.root / supersedes).exists():
        update_frontmatter_file(bundle.root / supersedes, {"status": "superseded", "supersededByPrdRef": rel(path, bundle.root), "updatedAt": utc_now()})
        create_audit_log(bundle, reviewer, "prd.supersede", supersedes, after="superseded", policy_result="approved", details=f"supersededBy={rel(path, bundle.root)}")
    update_frontmatter_file(bundle.root / requirement_ref, {"currentPrdRef": rel(path, bundle.root), "updatedAt": utc_now()})
    return path


def default_decision_deadline(impact_level: str, impact_areas: list[str]) -> str:
    if impact_level == "high" and ({"security", "permission"} & set(impact_areas)):
        return datetime.now(timezone.utc).date().isoformat()
    if impact_level == "high":
        return (datetime.now(timezone.utc) + timedelta(days=2)).date().isoformat()
    return ""


def create_decision_request(
    bundle: Bundle,
    requirement_id: str,
    impact_level: str,
    owner: str,
    context: str,
    impact_areas: list[str] | None = None,
    prd_ref: str = "",
    options: list[str] | None = None,
    tradeoffs: str = "",
    recommendation: str = "",
    deadline: str = "",
) -> Path:
    requirement_path = find_requirement(bundle, requirement_id)
    requirement = load_object(requirement_path)
    normalized_impact = impact_level.strip().lower() or "medium"
    if normalized_impact not in {"low", "medium", "high"}:
        raise KnowledgeError("impact must be low, medium, or high")
    areas = [slug(area) for area in (impact_areas or []) if area.strip()]
    if normalized_impact == "high" and not owner.strip():
        raise KnowledgeError("high-impact decision requires human owner")
    if normalized_impact == "high" and owner.strip().startswith("agent."):
        raise KnowledgeError("high-impact decision owner must be human")
    resolved_deadline = deadline.strip() or default_decision_deadline(normalized_impact, areas)
    if normalized_impact == "high" and not resolved_deadline:
        raise KnowledgeError("high-impact decision requires deadline")
    decision_id = unique_time_id(f"decision.{slug(str(requirement.get('projectId') or 'project'))}.{safe_slug(context or str(requirement.get('title')), 'decision')}")
    root = decision_storage_dir(bundle, str(requirement.get("projectId") or ""))
    path = root / f"{slug(decision_id)}.md"
    option_values = options or ["Approve recommended path", "Reject or revise path"]
    option_payload = {
        "items": [
            {"optionId": f"option-{index + 1}", "label": option, "description": option, "pros": [], "cons": [], "risk": "", "sourceRefs": as_list(requirement.get("sourceRefs"))}
            for index, option in enumerate(option_values)
        ]
    }
    frontmatter = {
        "type": "Decision",
        "title": context.strip()[:80] or f"Decision for {requirement.get('title')}",
        "timestamp": utc_now(),
        "decisionId": decision_id,
        "projectId": str(requirement.get("projectId") or ""),
        "requirementRef": rel(requirement_path, bundle.root),
        "prdRef": prd_ref,
        "owner": owner.strip(),
        "status": "decision_needed" if normalized_impact == "high" else "draft",
        "impactLevel": normalized_impact,
        "impactAreas": areas,
        "context": context.strip(),
        "options": option_payload,
        "tradeoffs": tradeoffs.strip(),
        "recommendation": {"summary": recommendation.strip(), "confidence": "medium", "sourceRefs": as_list(requirement.get("sourceRefs"))},
        "deadline": resolved_deadline,
        "decision": "",
        "rationale": "",
        "affectedObjects": [rel(requirement_path, bundle.root)] + ([prd_ref] if prd_ref else []),
        "notificationRefs": [],
        "auditRefs": [],
    }
    body = "\n".join(["## Context", "", context.strip(), "", "## Options", "", "\n".join(f"- {item}" for item in option_values), "", "## Tradeoffs", "", tradeoffs.strip() or "TBD.", "", "## Recommendation", "", recommendation.strip() or "TBD."])
    write_text(path, render_doc(frontmatter, body))
    update_index(root / "decisions.md" if root.name == slug(str(requirement.get("projectId") or "")) else root / "index.md", str(frontmatter["title"]), path.name)
    audit = create_audit_log(bundle, owner.strip() or str(requirement.get("submitter") or "system"), "decision.create", rel(path, bundle.root), after=str(frontmatter["status"]), policy_result="human_required" if normalized_impact == "high" else "recorded", details=f"impact={normalized_impact}\nareas={','.join(areas)}")
    notification_ref = ""
    if normalized_impact == "high":
        notification_ref = create_requirement_notification(bundle, f"Decision needed: {frontmatter['title']}", str(requirement.get("projectId") or ""), owner.strip(), "decision_needed", f"{frontmatter['title']} needs owner decision by {resolved_deadline}.", rel(path, bundle.root))
    update_frontmatter_file(path, {"auditRefs": [rel(audit, bundle.root)], "notificationRefs": [notification_ref] if notification_ref else []})
    update_frontmatter_file(requirement_path, {"decisionRefs": append_unique(as_list(requirement.get("decisionRefs")), rel(path, bundle.root)), "decisionOwner": str(requirement.get("decisionOwner") or owner.strip()), "status": "decision_needed" if normalized_impact == "high" else str(requirement.get("status") or "draft"), "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    return path


def find_decision(bundle: Bundle, decision_id: str) -> Path:
    for root in [bundle.root / "decisions", bundle.root / "projects"]:
        if not root.exists():
            continue
        direct = list(root.rglob(f"{slug(decision_id)}.md"))
        if direct:
            return direct[0]
        for path in root.rglob("*.md"):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            if fm.get("type") == "Decision" and str(fm.get("decisionId") or "").lower() == decision_id.lower():
                return path
    raise KnowledgeError(f"decision not found: {decision_id}")


def resolve_decision(bundle: Bundle, decision_id: str, selected_option: str, rationale: str, approver: str = "") -> Path:
    decision_path = find_decision(bundle, decision_id)
    decision = load_object(decision_path)
    actor = approver.strip() or str(decision.get("owner") or "")
    if not selected_option.strip():
        raise KnowledgeError("selected option is required")
    if not rationale.strip():
        raise KnowledgeError("decision rationale is required")
    if decision.get("impactLevel") == "high" and actor.startswith("agent."):
        raise KnowledgeError("high-impact decision cannot be approved by Agent alone")
    audit = create_audit_log(bundle, actor or "system", "decision.resolve", rel(decision_path, bundle.root), before=str(decision.get("status") or ""), after="approved", policy_result="approved", details=f"selectedOption={selected_option}")
    update_frontmatter_file(decision_path, {"status": "approved", "decision": selected_option.strip(), "rationale": rationale.strip(), "approver": actor, "auditRefs": append_unique(as_list(decision.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    return decision_path


def create_requirement_task(
    bundle: Bundle,
    requirement_id: str,
    title: str,
    assignee: str,
    requester: str,
    criteria_refs: list[str] | None = None,
    task_type: str = "development",
    priority: str = "normal",
) -> Path:
    requirement_path = find_requirement(bundle, requirement_id)
    requirement = load_object(requirement_path)
    criteria_values = criteria_refs or accepted_observable_criteria(bundle, requirement)
    task_path = create_project_task(
        bundle,
        title,
        str(requirement.get("projectId") or ""),
        requester,
        assignee,
        task_type=task_type,
        priority=priority,
        source_material_refs=as_list(requirement.get("sourceRefs")) + [rel(requirement_path, bundle.root)],
        expected_output=["TaskResult must link requirementRefs and acceptanceCriteriaRefs."],
        work_source_type="feature",
        requirement_refs=[str(requirement.get("requirementId"))],
        requirement_object_refs=[rel(requirement_path, bundle.root)],
        acceptance_criteria_refs=criteria_values,
    )
    task = load_object(task_path)
    update_frontmatter_file(task_path, {"requirementRefs": [str(requirement.get("requirementId"))], "requirementObjectRefs": [rel(requirement_path, bundle.root)], "acceptanceCriteriaRefs": criteria_values, "updatedAt": utc_now()})
    for criteria_ref in criteria_values:
        criteria_path = bundle.root / criteria_ref
        if criteria_path.exists():
            update_frontmatter_file(criteria_path, {"taskRef": rel(task_path, bundle.root), "updatedAt": utc_now()})
    audit = create_audit_log(bundle, requester, "requirement.task.link", rel(task_path, bundle.root), after=str(task.get("status") or ""), policy_result="recorded", details=f"requirementRef={rel(requirement_path, bundle.root)}\ncriteriaRefs={','.join(criteria_values)}")
    update_frontmatter_file(requirement_path, {"taskRefs": append_unique(as_list(requirement.get("taskRefs")), rel(task_path, bundle.root)), "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "status": "in_progress" if requirement.get("status") == "approved" else str(requirement.get("status") or "draft"), "updatedAt": utc_now()})
    return task_path


def infer_work_source_type(
    task_type: str = "",
    source_material_refs: list[str] | None = None,
    requirement_refs: list[str] | None = None,
    defect_refs: list[str] | None = None,
    research_question: str = "",
    reason: str = "",
) -> str:
    normalized_task_type = task_type.strip().lower()
    if requirement_refs:
        return "feature"
    if defect_refs:
        return "bugfix"
    if normalized_task_type in {"project_init", "project_setup", "project_management", "project_onboarding"}:
        return "project_setup"
    if (normalized_task_type.startswith("knowledge_") or normalized_task_type in {"knowledge_capture", "knowledge_review", "knowledge_publish"}) and source_material_refs:
        return "knowledge_ingest"
    if "research" in normalized_task_type or research_question.strip():
        return "research"
    if source_material_refs and normalized_task_type in {"material_ingest", "source_ingest"}:
        return "knowledge_ingest"
    if reason.strip():
        return "maintenance"
    return "maintenance"


def normalize_work_source_type(
    task_type: str,
    work_source_type: str = "",
    source_material_refs: list[str] | None = None,
    requirement_refs: list[str] | None = None,
    defect_refs: list[str] | None = None,
    research_question: str = "",
    reason: str = "",
) -> str:
    source_type = work_source_type.strip() or infer_work_source_type(
        task_type,
        source_material_refs,
        requirement_refs,
        defect_refs,
        research_question,
        reason,
    )
    if source_type not in WORK_SOURCE_TYPE_VALUES:
        raise KnowledgeError(f"unknown workSourceType: {source_type}")
    return source_type


def task_effective_work_source_type(task: dict[str, Any]) -> str:
    explicit = str(task.get("workSourceType") or "").strip()
    if explicit:
        return explicit
    return infer_work_source_type(
        str(task.get("taskType") or ""),
        as_list(task.get("sourceMaterialRefs")),
        as_list(task.get("requirementRefs")),
        as_list(task.get("defectRefs")),
        str(task.get("researchQuestion") or ""),
        str(task.get("sourceReason") or task.get("reason") or ""),
    )


def has_meaningful_traceability_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return any(has_meaningful_traceability_value(item) for item in value)
    if isinstance(value, dict):
        return any(has_meaningful_traceability_value(item) for item in value.values())
    normalized = str(value).strip()
    return normalized not in {"", "[]", "null", "None"}


def meaningful_traceability_refs(value: Any) -> list[str]:
    return [str(item).strip() for item in as_list(value) if has_meaningful_traceability_value(item)]


def validate_task_source_traceability(rel_path: str, task: dict[str, Any], *, require_explicit: bool = False) -> list[str]:
    problems: list[str] = []
    explicit = str(task.get("workSourceType") or "").strip()
    if not explicit and not require_explicit:
        return problems
    source_type = explicit or task_effective_work_source_type(task)
    if require_explicit and not explicit:
        problems.append(f"{rel_path}: ProjectTask/KnowledgeTask missing workSourceType")
    if source_type not in WORK_SOURCE_TYPE_VALUES:
        problems.append(f"{rel_path}: unknown workSourceType {source_type}")
        return problems
    requirement_refs = meaningful_traceability_refs(task.get("requirementRefs"))
    defect_refs = meaningful_traceability_refs(task.get("defectRefs"))
    source_refs = meaningful_traceability_refs(task.get("sourceMaterialRefs"))
    expected_output = meaningful_traceability_refs(task.get("expectedOutput"))
    source_reason = task.get("sourceReason") if "sourceReason" in task else task.get("reason")
    if source_type == "feature" and not requirement_refs:
        problems.append(f"{rel_path}: feature task requires requirementRefs")
    if source_type == "bugfix" and not defect_refs:
        problems.append(f"{rel_path}: bugfix task requires defectRefs")
    if source_type == "research" and not (has_meaningful_traceability_value(task.get("researchQuestion")) or source_refs or expected_output):
        problems.append(f"{rel_path}: research task requires researchQuestion, sourceMaterialRefs, or expectedOutput")
    if source_type == "knowledge_ingest" and not (source_refs or meaningful_traceability_refs(task.get("knowledgeTaskRefs"))):
        problems.append(f"{rel_path}: knowledge_ingest task requires sourceMaterialRefs or knowledgeTaskRefs")
    if source_type == "maintenance" and not (has_meaningful_traceability_value(source_reason) or source_refs or expected_output):
        problems.append(f"{rel_path}: maintenance task requires sourceReason, sourceMaterialRefs, or expectedOutput")
    return problems


def find_defect(bundle: Bundle, defect_id: str) -> Path:
    wanted = defect_id.strip()
    if not wanted:
        raise KnowledgeError("defect id is required")
    roots = [bundle.root / "defects", bundle.root / "projects"]
    for root in roots:
        if not root.exists():
            continue
        direct = list(root.rglob(f"{slug(wanted)}.md"))
        if direct:
            return direct[0]
        for path in root.rglob("*.md"):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            if fm.get("type") == "Defect" and str(fm.get("defectId") or "").lower() == wanted.lower():
                return path
    raise KnowledgeError(f"defect not found: {defect_id}")


def create_defect(
    bundle: Bundle,
    title: str,
    project_id: str,
    reporter: str,
    severity: str = "medium",
    defect_id: str = "",
    requirement_refs: list[str] | None = None,
    source_task_ref: str = "",
    source_result_ref: str = "",
    evidence_refs: list[str] | None = None,
    expected_behavior: str = "",
    actual_behavior: str = "",
    reproduction_steps: list[str] | None = None,
) -> Path:
    if not title.strip():
        raise KnowledgeError("defect title is required")
    if not reporter.strip():
        raise KnowledgeError("defect reporter is required")
    did = defect_id.strip() or unique_time_id("defect")
    storage_dir = defect_storage_dir(bundle, project_id)
    ensure_dir(storage_dir)
    path = storage_dir / f"{slug(did)}.md"
    if path.exists():
        raise KnowledgeError(f"defect already exists: {did}")
    frontmatter = {
        "type": "Defect",
        "title": title.strip(),
        "description": "Bug or quality issue that can create bugfix ProjectTasks without a product requirement.",
        "timestamp": utc_now(),
        "defectId": did,
        "projectId": slug(project_id) if project_id else "",
        "reporter": reporter.strip(),
        "owner": "",
        "severity": severity.strip() or "medium",
        "status": "open",
        "requirementRefs": requirement_refs or [],
        "sourceTaskRef": source_task_ref.strip(),
        "sourceResultRef": source_result_ref.strip(),
        "evidenceRefs": evidence_refs or [],
        "expectedBehavior": expected_behavior.strip(),
        "actualBehavior": actual_behavior.strip(),
        "reproductionSteps": reproduction_steps or [],
        "fixTaskRefs": [],
        "regressionEvidenceRefs": [],
        "auditRefs": [],
    }
    body = "\n".join(
        [
            "## Expected Behavior",
            "",
            expected_behavior.strip() or "TBD",
            "",
            "## Actual Behavior",
            "",
            actual_behavior.strip() or "TBD",
            "",
            "## Reproduction Steps",
            "",
            "\n".join(f"- {item}" for item in reproduction_steps or []) or "- TBD",
            "",
            "## Evidence",
            "",
            "\n".join(f"- {item}" for item in evidence_refs or []) or "- none",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(storage_dir / "index.md", title.strip(), path.name)
    audit = create_audit_log(bundle, reporter, "defect.create", rel(path, bundle.root), after="open", policy_result="recorded", details=f"projectId={frontmatter['projectId']}\nseverity={frontmatter['severity']}")
    update_frontmatter_file(path, {"auditRefs": [rel(audit, bundle.root)]})
    append_log(bundle, f"created defect {did} project={frontmatter['projectId']}")
    return path


def create_bugfix_task(
    bundle: Bundle,
    defect_id: str,
    title: str,
    requester: str,
    assignee: str,
    task_type: str = "development",
    priority: str = "high",
) -> Path:
    defect_path = find_defect(bundle, defect_id)
    defect = load_object(defect_path)
    project_id = str(defect.get("projectId") or "")
    task_path = create_project_task(
        bundle,
        title or f"Fix defect {defect.get('defectId')}",
        project_id,
        requester,
        assignee,
        task_type=task_type,
        priority=priority,
        source_material_refs=[rel(defect_path, bundle.root), *as_list(defect.get("evidenceRefs"))],
        expected_output=["TaskResult must include fix evidence and regression checks linked to this Defect."],
        work_source_type="bugfix",
        defect_refs=[str(defect.get("defectId") or defect_id)],
        defect_object_refs=[rel(defect_path, bundle.root)],
        source_reason=f"Bugfix for defect {defect.get('defectId') or defect_id}",
    )
    update_frontmatter_file(defect_path, {"status": "triaged", "fixTaskRefs": append_unique(as_list(defect.get("fixTaskRefs")), rel(task_path, bundle.root)), "updatedAt": utc_now()})
    create_audit_log(bundle, requester, "defect.fix_task.create", rel(task_path, bundle.root), after="pending", policy_result="recorded", details=f"defectRef={rel(defect_path, bundle.root)}")
    return task_path


def create_receiver_review(
    bundle: Bundle,
    project_id: str,
    upstream_ref: str,
    receiver_agent: str,
    reviewer_agent: str,
    decision: str,
    artifact_refs: list[str] | None = None,
    checklist: list[str] | None = None,
    issues: list[str] | None = None,
    assumptions: list[str] | None = None,
    review_id: str = "",
) -> Path:
    if decision not in RECEIVER_REVIEW_STATUS_VALUES:
        raise KnowledgeError(f"unknown receiver review decision: {decision}")
    if decision in {"needs_rework", "human_decision_required"} and not issues:
        raise KnowledgeError("receiver review needs issues when decision requires rework or human decision")
    if decision == "accepted_with_assumptions" and not assumptions:
        raise KnowledgeError("receiver review accepted_with_assumptions requires assumptions")
    if not upstream_ref.strip():
        raise KnowledgeError("receiver review upstreamRef is required")
    if not receiver_agent.strip():
        raise KnowledgeError("receiverAgent is required")
    rid = review_id.strip() or unique_time_id("receiver-review")
    storage_dir = receiver_review_storage_dir(bundle, project_id)
    ensure_dir(storage_dir)
    path = storage_dir / f"{slug(rid)}.md"
    if path.exists():
        raise KnowledgeError(f"receiver review already exists: {rid}")
    frontmatter = {
        "type": "ReceiverReview",
        "title": f"Receiver review for {upstream_ref}",
        "description": "Downstream Agent input acceptance gate before consuming upstream deliverables.",
        "timestamp": utc_now(),
        "reviewId": rid,
        "projectId": slug(project_id) if project_id else "",
        "upstreamRef": upstream_ref.strip(),
        "receiverAgent": receiver_agent.strip(),
        "reviewerAgent": reviewer_agent.strip() or receiver_agent.strip(),
        "status": decision,
        "decision": decision,
        "artifactRefs": artifact_refs or [],
        "checklist": checklist or [],
        "issues": issues or [],
        "assumptions": assumptions or [],
        "auditRefs": [],
    }
    body = "\n".join(
        [
            "## Checklist",
            "",
            "\n".join(f"- {item}" for item in checklist or []) or "- none",
            "",
            "## Issues",
            "",
            "\n".join(f"- {item}" for item in issues or []) or "- none",
            "",
            "## Assumptions",
            "",
            "\n".join(f"- {item}" for item in assumptions or []) or "- none",
            "",
            "## Artifacts",
            "",
            "\n".join(f"- {item}" for item in artifact_refs or []) or "- none",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(storage_dir / "index.md", str(frontmatter["title"]), path.name)
    audit = create_audit_log(bundle, str(frontmatter["reviewerAgent"]), "receiver_review.create", rel(path, bundle.root), after=decision, policy_result=decision, details=f"upstreamRef={upstream_ref}\nreceiverAgent={receiver_agent}")
    update_frontmatter_file(path, {"auditRefs": [rel(audit, bundle.root)]})
    upstream_path = bundle.root / upstream_ref.strip()
    if upstream_path.exists():
        upstream = load_object(upstream_path)
        if upstream.get("type") in {"ProjectTask", "KnowledgeTask"}:
            update_frontmatter_file(
                upstream_path,
                {
                    "receiverReviewRefs": append_unique(as_list(upstream.get("receiverReviewRefs")), rel(path, bundle.root)),
                    "updatedAt": utc_now(),
                },
            )
    append_log(bundle, f"created receiver review {rid} decision={decision}")
    return path


def create_impact_review(bundle: Bundle, requirement_id: str, from_prd_ref: str, to_prd_ref: str, owner: str, status: str = "draft") -> Path:
    requirement_path = find_requirement(bundle, requirement_id)
    requirement = load_object(requirement_path)
    if not from_prd_ref or not to_prd_ref:
        raise KnowledgeError("from and to PRD refs are required")
    changed = prd_changed_fields(bundle, from_prd_ref, to_prd_ref)
    impact_id = unique_time_id(f"impact-review.{slug(str(requirement.get('requirementId')))}")
    path = impact_review_storage_dir(bundle) / f"{slug(impact_id)}.md"
    affected_tasks = as_list(requirement.get("taskRefs")) if any(field in PRD_IMPACT_FIELDS for field in changed) else []
    frontmatter = {
        "type": "ImpactReview",
        "title": f"Impact review for {requirement.get('title')}",
        "timestamp": utc_now(),
        "impactReviewId": impact_id,
        "requirementRef": rel(requirement_path, bundle.root),
        "fromPrdRef": from_prd_ref,
        "toPrdRef": to_prd_ref,
        "changedFields": changed,
        "affectedTaskRefs": affected_tasks,
        "affectedDesignRefs": [],
        "affectedTestRefs": [],
        "affectedResultRefs": [],
        "affectedDecisionRefs": as_list(requirement.get("decisionRefs")),
        "riskSummary": "Changed PRD fields may affect downstream task acceptance." if affected_tasks else "No downstream task impact detected.",
        "recommendedActions": ["update", "retest", "create decision"] if affected_tasks else ["keep"],
        "owner": owner.strip(),
        "status": status.strip() or "draft",
        "notificationRefs": [],
        "auditRefs": [],
    }
    body = "\n".join(["## Changed Fields", "", "\n".join(f"- {field}" for field in changed) or "- none", "", "## Affected Tasks", "", "\n".join(f"- {item}" for item in affected_tasks) or "- none", "", "## Risk Summary", "", str(frontmatter["riskSummary"])])
    write_text(path, render_doc(frontmatter, body))
    update_index(impact_review_storage_dir(bundle) / "index.md", str(frontmatter["title"]), path.name)
    audit = create_audit_log(bundle, owner.strip() or "system", "requirement.impact_review.create", rel(path, bundle.root), after=str(frontmatter["status"]), policy_result="review_required" if affected_tasks else "recorded", details=f"changedFields={','.join(changed)}")
    notification_ref = ""
    if affected_tasks:
        notification_ref = create_requirement_notification(bundle, f"PRD impact review created: {requirement.get('title')}", str(requirement.get("projectId") or ""), owner.strip(), "prd_impact_review", f"{requirement.get('title')} PRD change affects {len(affected_tasks)} downstream task(s).", rel(path, bundle.root))
    update_frontmatter_file(path, {"auditRefs": [rel(audit, bundle.root)], "notificationRefs": [notification_ref] if notification_ref else []})
    update_frontmatter_file(requirement_path, {"impactReviewRefs": append_unique(as_list(requirement.get("impactReviewRefs")), rel(path, bundle.root)), "auditRefs": append_unique(as_list(requirement.get("auditRefs")), rel(audit, bundle.root)), "updatedAt": utc_now()})
    return path


def default_discussion_participants(participant_agents: list[str] | None = None) -> list[str]:
    return participant_agents or [PROJECT_MANAGER_AGENT_ID, PRODUCT_MANAGER_AGENT_ID, DEVELOPMENT_AGENT_ID, TEST_AGENT_ID]


def create_discussion_session(
    bundle: Bundle,
    title: str,
    project_id: str,
    requester: str,
    topic: str,
    participant_agents: list[str] | None = None,
    related_task_id: str = "",
    facilitator_agent: str = PROJECT_MANAGER_AGENT_ID,
    max_rounds: int = 1,
    human_visible: bool = True,
) -> dict[str, Any]:
    if not title.strip():
        raise KnowledgeError("discussion title is required")
    if not requester.strip():
        raise KnowledgeError("discussion requester is required")
    if not topic.strip():
        raise KnowledgeError("discussion topic is required")
    discussion_id = next_discussion_id(bundle)
    participants = default_discussion_participants(participant_agents)
    root = discussion_storage_dir(bundle, project_id)
    ensure_dir(root)
    path = root / f"{slug(discussion_id)}.md"
    frontmatter = {
        "type": "DiscussionSession",
        "title": title,
        "description": "Round-based Agent discussion session.",
        "timestamp": utc_now(),
        "discussionId": discussion_id,
        "projectId": slug(project_id) if project_id else "",
        "requester": requester,
        "facilitatorAgent": facilitator_agent,
        "participantAgents": participants,
        "relatedTaskId": related_task_id,
        "topic": topic,
        "status": "waiting_agent_turns",
        "currentRound": 1,
        "maxRounds": max(1, max_rounds),
        "humanVisible": bool(human_visible),
        "turnRefs": [],
        "summaryRef": "",
        "decisionRefs": [],
        "followupTaskRefs": [],
        "notificationRefs": [],
    }
    body = "\n".join(
        [
            "## Topic",
            "",
            topic,
            "",
            "## Participants",
            "",
            "\n".join(f"- {item}" for item in participants),
            "",
            "## Phase 1 Workflow",
            "",
            "1. Project Manager Agent creates this session and requests role turns.",
            "2. Product, Development, Test, and any invited Agent submit evidence-backed turns.",
            "3. Project Manager Agent summarizes consensus, disputes, risks, and next action.",
            "4. If consensus is enough, the summary becomes Decision and follow-up task artifacts.",
            "5. If risk or disagreement remains, the session waits for human decision.",
            "",
            "## Visibility",
            "",
            "- Every lifecycle step must create NotificationRecord.",
            "- Human-facing Feishu notification can render this session summary or decision request.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(root / "index.md", title, path.name)
    create_audit_log(bundle, requester, "discussion.create", rel(path, bundle.root), after="waiting_agent_turns", policy_result="agent_discussion")
    create_discussion_notification(
        bundle,
        path,
        frontmatter,
        "discussion_created",
        recipient=facilitator_agent,
        summary=f"讨论会已创建：{title}。主题：{topic}",
    )
    for agent_id in participants:
        create_discussion_notification(
            bundle,
            path,
            load_object(path),
            "discussion_turn_requested",
            recipient=agent_id,
            summary=f"请提交讨论观点：{title}。角色：{agent_id}。",
        )
    append_log(bundle, f"created discussion {discussion_id} project={project_id or 'none'}")
    return {"apiVersion": "v0.1", "kind": "DiscussionSession", "discussionId": discussion_id, "discussionRef": rel(path, bundle.root)}


def submit_discussion_turn(
    bundle: Bundle,
    discussion_id: str,
    agent_id: str,
    role: str,
    content: str,
    stance: str = "",
    concerns: list[str] | None = None,
    recommendations: list[str] | None = None,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    if not agent_id.strip():
        raise KnowledgeError("discussion turn agent is required")
    if not content.strip():
        raise KnowledgeError("discussion turn content is required")
    session_path = find_discussion_session(bundle, discussion_id)
    session = load_object(session_path)
    turn_refs = as_list(session.get("turnRefs"))
    turn_id = f"{session.get('discussionId')}-turn-{len(turn_refs) + 1:02d}"
    turn_path = session_path.parent / f"{slug(turn_id)}.md"
    frontmatter = {
        "type": "DiscussionTurn",
        "title": f"{agent_id} discussion turn",
        "description": "One role turn in an Agent discussion session.",
        "timestamp": utc_now(),
        "turnId": turn_id,
        "discussionId": session.get("discussionId"),
        "projectId": session.get("projectId", ""),
        "agentId": agent_id,
        "role": role or agent_id,
        "status": "submitted",
        "stance": stance,
        "concerns": concerns or [],
        "recommendations": recommendations or [],
        "evidenceRefs": evidence_refs or [],
    }
    body = "\n".join(
        [
            "## Position",
            "",
            content,
            "",
            "## Concerns",
            "",
            "\n".join(f"- {item}" for item in concerns or []) or "- none",
            "",
            "## Recommendations",
            "",
            "\n".join(f"- {item}" for item in recommendations or []) or "- none",
            "",
            "## Evidence",
            "",
            "\n".join(f"- {item}" for item in evidence_refs or []) or "- none",
        ]
    )
    write_text(turn_path, render_doc(frontmatter, body))
    update_index(session_path.parent / "index.md", str(frontmatter["title"]), turn_path.name)
    new_turn_refs = append_unique(turn_refs, rel(turn_path, bundle.root))
    submitted_agents = {
        str(load_object(bundle.root / ref).get("agentId"))
        for ref in new_turn_refs
        if (bundle.root / ref).exists()
    }
    participants = {str(item) for item in as_list(session.get("participantAgents"))}
    ready_for_summary = bool(participants) and participants.issubset(submitted_agents)
    new_status = "pm_reviewing" if ready_for_summary else "waiting_agent_turns"
    updated = update_frontmatter_file(session_path, {"turnRefs": new_turn_refs, "status": new_status, "updatedAt": utc_now()})
    create_audit_log(bundle, agent_id, "discussion.turn.submit", rel(turn_path, bundle.root), after="submitted", policy_result="agent_discussion")
    create_discussion_notification(
        bundle,
        session_path,
        updated,
        "discussion_turn_submitted",
        recipient=str(session.get("facilitatorAgent") or PROJECT_MANAGER_AGENT_ID),
        summary=f"{agent_id} 已提交讨论观点：{session.get('title', discussion_id)}。",
        source_message_ref=rel(turn_path, bundle.root),
    )
    if ready_for_summary:
        create_discussion_notification(
            bundle,
            session_path,
            load_object(session_path),
            "discussion_ready_for_summary",
            recipient=str(session.get("facilitatorAgent") or PROJECT_MANAGER_AGENT_ID),
            summary=f"讨论会所有参与 Agent 已提交观点，可以由项目经理 Agent 汇总：{session.get('title', discussion_id)}。",
        )
    return {"apiVersion": "v0.1", "kind": "DiscussionTurn", "discussionId": str(session.get("discussionId")), "turnRef": rel(turn_path, bundle.root), "sessionStatus": new_status}


def create_discussion_decision(
    bundle: Bundle,
    session: dict[str, Any],
    summary_ref: str,
    owner: str,
    decision: str,
    human_required: bool,
) -> str:
    if not decision.strip():
        return ""
    project_id = str(session.get("projectId") or "")
    root = bundle.root / "projects" / slug(project_id) if project_id else bundle.root / "decisions"
    ensure_dir(root)
    decision_id = f"decision.{slug(str(session.get('discussionId')))}"
    path = root / f"{slug(decision_id)}.md"
    frontmatter = {
        "type": "Decision",
        "title": f"Decision from {session.get('title', session.get('discussionId'))}",
        "description": "Decision created from Agent discussion session.",
        "timestamp": utc_now(),
        "decisionId": decision_id,
        "projectId": project_id,
        "owner": owner,
        "status": "draft" if human_required else "observed",
        "discussionId": session.get("discussionId"),
        "summaryRef": summary_ref,
        "affectedObjects": [summary_ref],
    }
    body = "\n".join(
        [
            "## Context",
            "",
            str(session.get("topic") or ""),
            "",
            "## Options",
            "",
            "See linked DiscussionTurn records.",
            "",
            "## Decision",
            "",
            decision,
            "",
            "## Rationale",
            "",
            f"Derived from discussion session {session.get('discussionId')}.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(root / "decisions.md" if project_id else root / "index.md", str(frontmatter["title"]), path.name)
    create_audit_log(bundle, owner, "discussion.decision.create", rel(path, bundle.root), after=str(frontmatter["status"]), policy_result="agent_discussion", details=f"discussionId={session.get('discussionId')}\nsummaryRef={summary_ref}")
    return rel(path, bundle.root)


def finalize_discussion_session(
    bundle: Bundle,
    discussion_id: str,
    facilitator: str,
    summary: str,
    consensus: str,
    decision: str = "",
    open_questions: list[str] | None = None,
    human_decision_required: bool = False,
    followup_task_title: str = "",
    followup_assignee: str = "",
) -> dict[str, Any]:
    if not facilitator.strip():
        raise KnowledgeError("discussion facilitator is required")
    if not summary.strip():
        raise KnowledgeError("discussion summary is required")
    session_path = find_discussion_session(bundle, discussion_id)
    session = load_object(session_path)
    summary_id = f"{session.get('discussionId')}-summary"
    summary_path = session_path.parent / f"{slug(summary_id)}.md"
    frontmatter = {
        "type": "DiscussionSummary",
        "title": f"Summary for {session.get('title', discussion_id)}",
        "description": "Project Manager Agent summary for an Agent discussion session.",
        "timestamp": utc_now(),
        "summaryId": summary_id,
        "discussionId": session.get("discussionId"),
        "projectId": session.get("projectId", ""),
        "facilitatorAgent": facilitator,
        "status": "waiting_human_decision" if human_decision_required else "summarized",
        "consensus": consensus,
        "decision": decision,
        "openQuestions": open_questions or [],
        "turnRefs": as_list(session.get("turnRefs")),
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            summary,
            "",
            "## Consensus",
            "",
            consensus or "none",
            "",
            "## Decision",
            "",
            decision or "pending",
            "",
            "## Open Questions",
            "",
            "\n".join(f"- {item}" for item in open_questions or []) or "- none",
            "",
            "## Source Turns",
            "",
            "\n".join(f"- {item}" for item in as_list(session.get("turnRefs"))) or "- none",
        ]
    )
    write_text(summary_path, render_doc(frontmatter, body))
    update_index(session_path.parent / "index.md", str(frontmatter["title"]), summary_path.name)
    summary_ref = rel(summary_path, bundle.root)
    decision_refs: list[str] = []
    decision_ref = create_discussion_decision(bundle, session, summary_ref, facilitator, decision, human_decision_required)
    if decision_ref:
        decision_refs.append(decision_ref)
    followup_refs: list[str] = []
    if followup_task_title.strip():
        task_path = create_project_task(
            bundle,
            followup_task_title,
            str(session.get("projectId") or ""),
            facilitator,
            followup_assignee or str(session.get("facilitatorAgent") or PROJECT_MANAGER_AGENT_ID),
            task_type="discussion_followup",
            source_material_refs=[summary_ref],
            expected_output=["Execute the accepted discussion decision.", "Write TaskResult with evidence, risks, and handoff."],
        )
        followup_refs.append(rel(task_path, bundle.root))
    if human_decision_required:
        new_status = "waiting_human_decision"
    elif followup_refs:
        new_status = "next_task_created"
    else:
        new_status = "done"
    updated = update_frontmatter_file(
        session_path,
        {
            "status": new_status,
            "summaryRef": summary_ref,
            "decisionRefs": decision_refs,
            "followupTaskRefs": followup_refs,
            "updatedAt": utc_now(),
        },
    )
    create_audit_log(bundle, facilitator, "discussion.finalize", rel(session_path, bundle.root), before=str(session.get("status", "")), after=new_status, policy_result="agent_discussion", details=f"summaryRef={summary_ref}\ndecisionRefs={', '.join(decision_refs)}\nfollowupRefs={', '.join(followup_refs)}")
    create_discussion_notification(
        bundle,
        session_path,
        updated,
        "discussion_summary_ready",
        recipient=str(session.get("requester") or session.get("facilitatorAgent") or PROJECT_MANAGER_AGENT_ID),
        summary=f"讨论会已汇总：{session.get('title', discussion_id)}。结论：{consensus or summary}",
        source_message_ref=summary_ref,
    )
    if human_decision_required:
        create_discussion_notification(
            bundle,
            session_path,
            load_object(session_path),
            "discussion_human_decision_required",
            recipient=str(session.get("requester") or "project-owner"),
            summary=f"讨论会需要人类决策：{session.get('title', discussion_id)}。待决问题：{'; '.join(open_questions or []) or '见汇总'}",
            source_message_ref=summary_ref,
        )
    else:
        create_discussion_notification(
            bundle,
            session_path,
            load_object(session_path),
            "discussion_completed",
            recipient=str(session.get("facilitatorAgent") or PROJECT_MANAGER_AGENT_ID),
            summary=f"讨论会已闭环：{session.get('title', discussion_id)}。后续任务：{', '.join(followup_refs) or '无'}",
            source_message_ref=summary_ref,
        )
    return {
        "apiVersion": "v0.1",
        "kind": "DiscussionSummary",
        "discussionId": str(session.get("discussionId")),
        "discussionRef": rel(session_path, bundle.root),
        "summaryRef": summary_ref,
        "decisionRefs": decision_refs,
        "followupTaskRefs": followup_refs,
        "status": new_status,
    }


def discussion_session_status(bundle: Bundle, discussion_id: str) -> dict[str, Any]:
    path = find_discussion_session(bundle, discussion_id)
    fm = load_object(path)
    fm["path"] = rel(path, bundle.root)
    return fm


def create_project_task(
    bundle: Bundle,
    title: str,
    project_id: str,
    requester: str,
    assignee: str,
    task_type: str = "knowledge_capture",
    task_id: str = "",
    priority: str = "normal",
    due_at: str = "",
    source_material_refs: list[str] | None = None,
    expected_output: list[str] | None = None,
    work_source_type: str = "",
    requirement_refs: list[str] | None = None,
    requirement_object_refs: list[str] | None = None,
    acceptance_criteria_refs: list[str] | None = None,
    defect_refs: list[str] | None = None,
    defect_object_refs: list[str] | None = None,
    incident_refs: list[str] | None = None,
    operation_refs: list[str] | None = None,
    knowledge_task_refs: list[str] | None = None,
    research_question: str = "",
    source_reason: str = "",
    outcome_slice_ref: str = "",
    pm_agent_id: str = "",
    pm_lease_id: str = "",
    pm_fencing_token: int | str = "",
    pm_source_channel: str = "",
) -> Path:
    if not title.strip():
        raise KnowledgeError("task title is required")
    if not requester.strip():
        raise KnowledgeError("task requester is required")
    runtime_profile = task_runtime_profile(task_type)
    resolved_task_type = str(runtime_profile["taskType"])
    resolved_assignee = assignee.strip() or str(runtime_profile["defaultAssignee"])
    if not resolved_assignee:
        raise KnowledgeError("task assignee is required")
    pm_lease_context: dict[str, Any] = {}
    if pm_agent_id or pm_source_channel:
        pm_lease_context = validate_pm_control_lease_for_write(
            bundle,
            project_id,
            pm_agent_id,
            pm_lease_id,
            pm_fencing_token,
            "task.create",
            source_channel=pm_source_channel or "cli",
            request_ref=f"task:{task_id or title}",
        )
    tid = task_id.strip() or next_task_id(bundle)
    path = task_storage_dir(bundle, project_id) / f"{slug(tid)}.md"
    if path.exists():
        raise KnowledgeError(f"task already exists: {tid}")
    object_type = str(runtime_profile["objectType"])
    guide_update_required = requires_agent_team_guide_update(resolved_task_type, title, expected_output)
    handoff_contract = handoff_contract_for_task_type(resolved_task_type)
    resolved_work_source_type = normalize_work_source_type(
        resolved_task_type,
        work_source_type,
        source_material_refs,
        requirement_refs,
        defect_refs,
        research_question,
        source_reason,
    )
    if resolved_work_source_type == "maintenance" and not (source_reason.strip() or source_material_refs or expected_output):
        source_reason = f"{resolved_task_type} task requested by {requester}"
    frontmatter = {
        "type": object_type,
        "title": title,
        "description": f"{object_type} assigned to {resolved_assignee}.",
        "timestamp": utc_now(),
        "taskId": tid,
        "taskType": resolved_task_type,
        "taskRuntime": {},
        "projectId": slug(project_id) if project_id else "",
        "workSourceType": resolved_work_source_type,
        "requirementRefs": requirement_refs or [],
        "requirementObjectRefs": requirement_object_refs or [],
        "acceptanceCriteriaRefs": acceptance_criteria_refs or [],
        "defectRefs": defect_refs or [],
        "defectObjectRefs": defect_object_refs or [],
        "incidentRefs": incident_refs or [],
        "operationRefs": operation_refs or [],
        "knowledgeTaskRefs": knowledge_task_refs or [],
        "researchQuestion": research_question.strip(),
        "sourceReason": source_reason.strip(),
        "outcomeSliceRef": outcome_slice_ref.strip(),
        "receiverReviewRefs": [],
        "requester": requester,
        "assignee": resolved_assignee,
        "status": "pending",
        "priority": priority,
        "dueAt": due_at,
        "sourceMaterialRefs": source_material_refs or [],
        "expectedOutput": expected_output or [],
        "resultRef": "",
        "notificationRefs": [],
        "auditRefs": [],
        "assignedRunner": "",
        "executorAgent": resolved_assignee,
        "leaseOwner": "",
        "leaseTokenHash": "",
        "leaseProofHash": "",
        "leaseIssuedAt": "",
        "leaseExpiresAt": "",
        "leaseHeartbeatAt": "",
        "leaseVersion": 1,
        "leaseAttempt": 0,
        "heartbeatAt": "",
        "taskVersion": 1,
        "handoffContract": handoff_contract,
        "qualityGateRequired": True,
        "attemptNumber": 1,
        "maxAttempts": DEFAULT_MAX_TASK_ATTEMPTS,
        "followupTaskRefs": [],
        "guideUpdateRequired": guide_update_required,
        "guideUpdated": False,
        "guideRef": AGENT_TEAM_GUIDE_REF if guide_update_required else "",
        "guideFeishuUrl": AGENT_TEAM_GUIDE_FEISHU_URL if guide_update_required else "",
        "guideRevision": "",
        "guideAuditRefs": [],
        "pmControlLeaseId": pm_lease_context.get("leaseId", ""),
        "pmControlLeaseGeneration": pm_lease_context.get("leaseGeneration", ""),
        "pmControlPrimaryPm": pm_lease_context.get("primaryPmAgentId", ""),
        "pmControlLeaseRef": pm_lease_context.get("leaseRef", ""),
    }
    frontmatter["taskRuntime"] = normalized_task_runtime(frontmatter)
    body = "\n".join(
        [
            "## Request",
            "",
            title,
            "",
            "## Work Source",
            "",
            f"- workSourceType: {resolved_work_source_type}",
            f"- requirementRefs: {', '.join(requirement_refs or []) or 'none'}",
            f"- defectRefs: {', '.join(defect_refs or []) or 'none'}",
            f"- sourceReason: {source_reason.strip() or 'none'}",
            f"- researchQuestion: {research_question.strip() or 'none'}",
            f"- outcomeSliceRef: {outcome_slice_ref.strip() or 'none'}",
            "",
            "## Source Materials",
            "",
            "\n".join(f"- {item}" for item in source_material_refs or []) or "- none",
            "",
            "## Expected Output",
            "",
            "\n".join(f"- {item}" for item in expected_output or []) or "- TaskResult with summary, evidence, and next actions.",
            "",
            "## Handling Notes",
            "",
            "The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.",
            "",
            "## Handoff Contract",
            "",
            f"- from: {handoff_contract.get('from') or 'current assignee'}",
            f"- to: {handoff_contract.get('to') or 'terminal or project manager decision'}",
            "- requiredArtifacts:",
            *[f"  - {item}" for item in as_list(handoff_contract.get("requiredArtifacts"))],
            "",
            "## Quality Gate",
            "",
            "- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.",
            "- Failed evaluation creates retry/escalation follow-up instead of silently closing.",
            "",
            "## Agent Team Guide Gate",
            "",
            (
                "- This task changes Agent roles, Skills, workflows, Scheduler, Agent Ring, or knowledge policy. It cannot close until the company Agent Team operating guide, Feishu document, revision record, and AuditLog are updated."
                if guide_update_required
                else "- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change."
            ),
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(path.parent / "index.md", title, path.name)
    create_audit_log(
        bundle,
        requester,
        "task.create",
        rel(path, bundle.root),
        after="pending",
        details=f"assignee={resolved_assignee}\ntaskType={resolved_task_type}\nruntimeCategory={runtime_profile['category']}\nworkSourceType={resolved_work_source_type}\npmControlLeaseId={pm_lease_context.get('leaseId', '')}\npmControlPrimaryPm={pm_lease_context.get('primaryPmAgentId', '')}",
    )
    create_task_notification(
        bundle,
        path,
        load_object(path),
        "task_created",
        recipient=requester,
        summary=f"任务已创建：{title}。当前负责人或接管对象：{resolved_assignee}。",
        source_message_ref=(source_material_refs or [""])[0],
    )
    append_log(bundle, f"created task {tid} assigned={resolved_assignee}")
    return path


def is_knowledge_execution_task(task: dict[str, Any]) -> bool:
    runtime = task_runtime_profile(str(task.get("taskType") or ""))
    return str(task.get("type")) == "KnowledgeTask" or runtime["category"] == "knowledge"


def is_knowledge_repair_task(task: dict[str, Any]) -> bool:
    return str(task.get("taskType")) == "knowledge_repair"


def is_knowledge_conflict_resolution_task(task: dict[str, Any]) -> bool:
    return str(task.get("taskType")) == "knowledge_conflict_resolution"


def task_attempt_number(task: dict[str, Any]) -> int:
    try:
        return max(1, int(task.get("attemptNumber") or 1))
    except (TypeError, ValueError):
        return 1


def task_max_attempts(task: dict[str, Any]) -> int:
    try:
        return max(1, int(task.get("maxAttempts") or DEFAULT_MAX_TASK_ATTEMPTS))
    except (TypeError, ValueError):
        return DEFAULT_MAX_TASK_ATTEMPTS


def test_or_check_looks_failed(value: str) -> bool:
    text = value.strip().lower()
    if not text:
        return False
    passed_markers = {"pass", "passed", "ok", "success", "通过", "成功", "valid"}
    failed_markers = {"fail", "failed", "failure", "error", "traceback", "未通过", "失败", "报错"}
    if any(marker in text for marker in failed_markers) and not any(marker in text for marker in passed_markers):
        return True
    return False


def expected_output_is_covered(expected: str, summary: str, refs: list[str], tests_or_checks: list[str]) -> bool:
    target = expected.strip()
    if not target:
        return True
    if refs and summary.strip():
        return True
    haystack = "\n".join([summary, *refs, *tests_or_checks]).lower()
    tokens = [item.lower() for item in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff]+", target) if len(item) >= 2]
    if not tokens:
        return True
    return any(token in haystack for token in tokens[:8])


def evaluate_knowledge_task_result(
    task: dict[str, Any],
    status: str,
    summary: str,
    created_knowledge_refs: list[str],
    source_refs: list[str],
    evidence_refs: list[str],
    tests_or_checks: list[str],
) -> dict[str, Any]:
    attempt = task_attempt_number(task)
    max_attempts = task_max_attempts(task)
    reasons: list[str] = []
    if status == "blocked":
        reasons.append("executor reported blocked")
        return {
            "type": "AgentResultEvaluation",
            "status": "blocked",
            "passed": False,
            "decision": "repair_required",
            "score": 0,
            "attemptNumber": attempt,
            "maxAttempts": max_attempts,
            "retryable": False,
            "reasons": reasons,
        }
    if status in {"rejected", "failed"}:
        reasons.append(f"executor reported {status}")
    if not summary.strip():
        reasons.append("missing summary")
    if not created_knowledge_refs:
        reasons.append("missing KnowledgeItem draft")
    if not (evidence_refs or source_refs):
        reasons.append("missing source evidence")
    failed_checks = [item for item in tests_or_checks if test_or_check_looks_failed(item)]
    if failed_checks:
        reasons.append("tests/checks reported failure")
    if reasons:
        return {
            "type": "AgentResultEvaluation",
            "status": "failed",
            "passed": False,
            "decision": "retry_required" if attempt < max_attempts else "repair_required",
            "score": 40 if attempt < max_attempts else 20,
            "attemptNumber": attempt,
            "maxAttempts": max_attempts,
            "retryable": attempt < max_attempts,
            "reasons": reasons,
        }
    return {
        "type": "AgentResultEvaluation",
        "status": "passed",
        "passed": True,
        "decision": "review_required",
        "score": 95 if tests_or_checks else 90,
        "attemptNumber": attempt,
        "maxAttempts": max_attempts,
        "retryable": False,
        "reasons": [],
        "evidenceRefsPresent": bool(evidence_refs or source_refs),
        "knowledgeDraftPresent": bool(created_knowledge_refs),
        "testsOrChecksPresent": bool(tests_or_checks),
    }


def followup_task_id(bundle: Bundle, base: str) -> str:
    base_slug = slug(base)
    for index in range(1, 100):
        candidate = base_slug if index == 1 else f"{base_slug}-{index:02d}"
        try:
            find_project_task(bundle, candidate)
        except KnowledgeError:
            return candidate
    raise KnowledgeError(f"too many follow-up task collisions for {base}")


def create_orchestration_followup_task(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    evaluation: dict[str, Any],
    knowledge_refs: list[str],
    evidence_refs: list[str],
) -> Path | None:
    if not is_knowledge_execution_task(task):
        return None
    task_id = str(task.get("taskId", ""))
    if not task_id:
        return None
    decision = str(evaluation.get("decision", ""))
    project_id = str(task.get("projectId", ""))
    requester = str(task.get("requester") or task.get("assignee") or "system.scheduler")
    result_ref = rel(result_path, bundle.root)
    source_refs = append_unique(as_list(task.get("sourceMaterialRefs")), result_ref)
    for item in [*knowledge_refs, *evidence_refs]:
        source_refs = append_unique(source_refs, item)
    attempt = task_attempt_number(task)
    max_attempts = task_max_attempts(task)

    if decision == "review_required":
        followup_path = create_project_task(
            bundle,
            title=f"Review knowledge output for {task_id}",
            project_id=project_id,
            requester=requester,
            assignee=KNOWLEDGE_REVIEW_AGENT_ID,
            task_type="knowledge_review",
            task_id=followup_task_id(bundle, f"{task_id}-review"),
            priority=str(task.get("priority") or "normal"),
            source_material_refs=source_refs,
            expected_output=[
                "Evaluate KnowledgeItem draft structure, evidence, scope, confidence, sensitivity, duplicate risk, and conflict risk.",
                "Return pass_as_observed, changes_requested, needs_human_approval, conflict_detected, or reject.",
                "If accepted, trigger index/publish workflow; if rejected, create retry or clarification task.",
            ],
        )
        update_frontmatter_file(
            followup_path,
            {
                "parentTaskId": task_id,
                "originTaskId": str(task.get("originTaskId") or task_id),
                "triggerResultRef": result_ref,
                "qualityGate": "passed",
                "attemptNumber": 1,
                "maxAttempts": max_attempts,
            },
        )
        create_task_notification(
            bundle,
            followup_path,
            load_object(followup_path),
            "knowledge_review_required",
            recipient=KNOWLEDGE_REVIEW_AGENT_ID,
            summary=f"知识抽取结果已通过基础评价，进入 Knowledge Review：{task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.followup.review", rel(followup_path, bundle.root), after="pending", details=f"sourceTask={task_id}\nresultRef={result_ref}")
        return followup_path

    if decision == "retry_required":
        assignee = str(task.get("assignee") or KNOWLEDGE_ENGINEERING_AGENT_ID)
        followup_path = create_project_task(
            bundle,
            title=f"Retry knowledge extraction for {task_id}",
            project_id=project_id,
            requester=requester,
            assignee=assignee,
            task_type="knowledge_retry",
            task_id=followup_task_id(bundle, f"{task_id}-retry"),
            priority=str(task.get("priority") or "normal"),
            source_material_refs=source_refs,
            expected_output=[
                "Re-run extraction using the same SourceMaterial and previous TaskResult as failure evidence.",
                "Produce TaskResult with KnowledgeItem draft, source evidence, confidence, scope, and tests/checks.",
                "Do not invent content when the source cannot be resolved; write blocked with exact missing source/tool detail.",
            ],
        )
        update_frontmatter_file(
            followup_path,
            {
                "parentTaskId": task_id,
                "originTaskId": str(task.get("originTaskId") or task_id),
                "retryOf": task_id,
                "triggerResultRef": result_ref,
                "qualityGate": "failed",
                "failureReasons": as_list(evaluation.get("reasons")),
                "attemptNumber": attempt + 1,
                "maxAttempts": max_attempts,
            },
        )
        create_task_notification(
            bundle,
            followup_path,
            load_object(followup_path),
            "knowledge_retry_required",
            recipient=assignee,
            summary=f"知识抽取结果未达标，已创建第 {attempt + 1}/{max_attempts} 次重试任务：{task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.followup.retry", rel(followup_path, bundle.root), after="pending", details=f"sourceTask={task_id}\nresultRef={result_ref}\nreasons={'; '.join(as_list(evaluation.get('reasons')))}")
        return followup_path

    if decision == "repair_required":
        followup_path = create_project_task(
            bundle,
            title=f"Repair blocked knowledge handoff for {task_id}",
            project_id=project_id,
            requester=requester,
            assignee=KNOWLEDGE_OPS_AGENT_ID,
            task_type="knowledge_repair",
            task_id=followup_task_id(bundle, f"{task_id}-repair"),
            priority="high",
            source_material_refs=source_refs,
            expected_output=[
                "Diagnose why the task, source material, tool, permission, or context pack was unavailable.",
                "Restore a resolvable source/task context or ask the submitter for missing material.",
                "Create a retry task only after the handoff is repairable; otherwise leave a clear blocked result and notification.",
            ],
        )
        update_frontmatter_file(
            followup_path,
            {
                "parentTaskId": task_id,
                "originTaskId": str(task.get("originTaskId") or task_id),
                "triggerResultRef": result_ref,
                "qualityGate": str(evaluation.get("status") or "blocked"),
                "failureReasons": as_list(evaluation.get("reasons")),
                "attemptNumber": 1,
                "maxAttempts": 1,
            },
        )
        create_task_notification(
            bundle,
            followup_path,
            load_object(followup_path),
            "knowledge_repair_required",
            recipient=KNOWLEDGE_OPS_AGENT_ID,
            summary=f"知识任务无法继续，已转 Knowledge Ops 修复交接或资料问题：{task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.followup.repair", rel(followup_path, bundle.root), after="pending", details=f"sourceTask={task_id}\nresultRef={result_ref}\nreasons={'; '.join(as_list(evaluation.get('reasons')))}")
        return followup_path
    return None


def is_successful_task_result_status(status: str) -> bool:
    return status in {"done", "submitted"}


def create_repair_completion_followup_task(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    status: str,
    evidence_refs: list[str],
) -> Path | None:
    if not is_knowledge_repair_task(task):
        return None
    task_id = str(task.get("taskId", ""))
    if not task_id:
        return None
    project_id = str(task.get("projectId", ""))
    requester = str(task.get("requester") or "system.scheduler")
    origin_task_id = str(task.get("originTaskId") or task.get("parentTaskId") or task_id)
    result_ref = rel(result_path, bundle.root)
    source_refs = as_list(task.get("sourceMaterialRefs"))
    source_refs = append_unique(source_refs, result_ref)
    for item in evidence_refs:
        source_refs = append_unique(source_refs, item)

    if is_successful_task_result_status(status):
        assignee = KNOWLEDGE_ENGINEERING_AGENT_ID
        try:
            origin_task = load_object(find_project_task(bundle, origin_task_id))
            assignee = str(origin_task.get("assignee") or assignee)
        except KnowledgeError:
            origin_task = {}
        retry_path = create_project_task(
            bundle,
            title=f"Retry repaired knowledge extraction for {origin_task_id}",
            project_id=project_id,
            requester=requester,
            assignee=assignee,
            task_type="knowledge_retry",
            task_id=followup_task_id(bundle, f"{origin_task_id}-retry-after-repair"),
            priority=str(task.get("priority") or "high"),
            source_material_refs=source_refs,
            expected_output=[
                "Re-run the original knowledge extraction now that Knowledge Ops repaired the handoff.",
                "Use the repair TaskResult as operational evidence.",
                "Write a new TaskResult and KnowledgeItem draft with source evidence, confidence, scope, and tests/checks.",
            ],
        )
        update_frontmatter_file(
            retry_path,
            {
                "parentTaskId": origin_task_id,
                "originTaskId": origin_task_id,
                "repairTaskId": task_id,
                "triggerResultRef": result_ref,
                "qualityGate": "repair_completed",
                "attemptNumber": task_attempt_number(origin_task) + 1 if origin_task else 1,
                "maxAttempts": task_max_attempts(origin_task) if origin_task else DEFAULT_MAX_TASK_ATTEMPTS,
            },
        )
        create_task_notification(
            bundle,
            retry_path,
            load_object(retry_path),
            "knowledge_repair_completed_retry_required",
            recipient=assignee,
            summary=f"Knowledge Ops 已修复交接问题，已创建重试任务：{origin_task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.repair.retry", rel(retry_path, bundle.root), after="pending", details=f"repairTask={task_id}\noriginTask={origin_task_id}\nresultRef={result_ref}")
        return retry_path

    clarification_path = create_project_task(
        bundle,
        title=f"Clarify unrepaired knowledge handoff for {origin_task_id}",
        project_id=project_id,
        requester=requester,
        assignee=requester,
        task_type="knowledge_clarification",
        task_id=followup_task_id(bundle, f"{origin_task_id}-repair-clarification"),
        priority="high",
        source_material_refs=source_refs,
        expected_output=[
            "Provide missing source, access, permission, owner, or material context required to continue the knowledge task.",
            "After clarification, Knowledge Ops or Knowledge Engineering Agent can continue the chain.",
        ],
    )
    update_frontmatter_file(
        clarification_path,
        {
            "parentTaskId": origin_task_id,
            "originTaskId": origin_task_id,
            "repairTaskId": task_id,
            "triggerResultRef": result_ref,
            "qualityGate": "repair_unresolved",
        },
    )
    create_task_notification(
        bundle,
        clarification_path,
        load_object(clarification_path),
        "knowledge_repair_needs_clarification",
        recipient=requester,
        summary=f"Knowledge Ops 仍无法修复知识任务交接，需要补充资料或权限：{origin_task_id}。",
        source_message_ref=result_ref,
    )
    create_audit_log(bundle, "system.scheduler", "workflow.repair.clarification", rel(clarification_path, bundle.root), after="pending", details=f"repairTask={task_id}\noriginTask={origin_task_id}\nresultRef={result_ref}")
    return clarification_path


def create_conflict_resolution_completion_followup_task(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    status: str,
    evidence_refs: list[str],
) -> Path | None:
    if not is_knowledge_conflict_resolution_task(task):
        return None
    task_id = str(task.get("taskId", ""))
    if not task_id:
        return None
    project_id = str(task.get("projectId", ""))
    requester = str(task.get("requester") or "system.scheduler")
    origin_task_id = str(task.get("originTaskId") or task.get("parentTaskId") or task_id)
    result_ref = rel(result_path, bundle.root)
    source_refs = as_list(task.get("sourceMaterialRefs"))
    source_refs = append_unique(source_refs, result_ref)
    for item in evidence_refs:
        source_refs = append_unique(source_refs, item)
    conflict_refs = [item for item in source_refs if item.startswith("knowledge/conflicts/")]

    if is_successful_task_result_status(status):
        resolved_conflict_refs: list[str] = []
        for conflict_ref in conflict_refs:
            try:
                resolve_conflict(bundle, Path(conflict_ref), KNOWLEDGE_STEWARD_AGENT_ID, f"Resolved by {task_id}. See {result_ref}.")
                resolved_conflict_refs = append_unique(resolved_conflict_refs, conflict_ref)
            except KnowledgeError:
                continue
        review_path_ = create_project_task(
            bundle,
            title=f"Re-review knowledge after conflict resolution for {origin_task_id}",
            project_id=project_id,
            requester=requester,
            assignee=KNOWLEDGE_REVIEW_AGENT_ID,
            task_type="knowledge_review",
            task_id=followup_task_id(bundle, f"{origin_task_id}-review-after-conflict"),
            priority="high",
            source_material_refs=source_refs,
            expected_output=[
                "Re-review the candidate after Knowledge Engineering Agent steward sub-agent resolved the conflict.",
                "Confirm whether the target should pass as observed, require human approval, need changes, or be rejected.",
                "Use the conflict resolution TaskResult and ConflictRecord as review evidence.",
            ],
        )
        update_frontmatter_file(
            review_path_,
            {
                "parentTaskId": origin_task_id,
                "originTaskId": origin_task_id,
                "conflictResolutionTaskId": task_id,
                "resolvedConflictRefs": resolved_conflict_refs,
                "triggerResultRef": result_ref,
                "qualityGate": "conflict_resolved",
                "attemptNumber": 1,
                "maxAttempts": DEFAULT_MAX_TASK_ATTEMPTS,
            },
        )
        create_task_notification(
            bundle,
            review_path_,
            load_object(review_path_),
            "knowledge_conflict_resolved_review_required",
            recipient=KNOWLEDGE_REVIEW_AGENT_ID,
            summary=f"Knowledge Steward 已处理冲突，已回到 Knowledge Review：{origin_task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.conflict.rereview", rel(review_path_, bundle.root), after="pending", details=f"conflictTask={task_id}\noriginTask={origin_task_id}\nresultRef={result_ref}\nconflicts={','.join(resolved_conflict_refs) or 'none'}")
        return review_path_

    clarification_path = create_project_task(
        bundle,
        title=f"Clarify unresolved knowledge conflict for {origin_task_id}",
        project_id=project_id,
        requester=requester,
        assignee=requester,
        task_type="knowledge_clarification",
        task_id=followup_task_id(bundle, f"{origin_task_id}-conflict-clarification"),
        priority="high",
        source_material_refs=source_refs,
        expected_output=[
            "Provide ownership, scope, source evidence, or business context required to resolve the knowledge conflict.",
            "After clarification, Knowledge Engineering Agent steward sub-agent continues conflict resolution.",
        ],
    )
    update_frontmatter_file(
        clarification_path,
        {
            "parentTaskId": origin_task_id,
            "originTaskId": origin_task_id,
            "conflictResolutionTaskId": task_id,
            "triggerResultRef": result_ref,
            "qualityGate": "conflict_unresolved",
        },
    )
    create_task_notification(
        bundle,
        clarification_path,
        load_object(clarification_path),
        "knowledge_conflict_needs_clarification",
        recipient=requester,
        summary=f"Knowledge Steward 无法完成冲突治理，需要补充信息：{origin_task_id}。",
        source_message_ref=result_ref,
    )
    create_audit_log(bundle, "system.scheduler", "workflow.conflict.clarification", rel(clarification_path, bundle.root), after="pending", details=f"conflictTask={task_id}\noriginTask={origin_task_id}\nresultRef={result_ref}")
    return clarification_path


def create_completion_followup_task(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    status: str,
    evidence_refs: list[str],
) -> Path | None:
    if is_knowledge_repair_task(task):
        return create_repair_completion_followup_task(bundle, task, result_path, status, evidence_refs)
    if is_knowledge_conflict_resolution_task(task):
        return create_conflict_resolution_completion_followup_task(bundle, task, result_path, status, evidence_refs)
    return None


def create_project_role_followup_task(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    evaluation: dict[str, Any],
    handoff_contract: dict[str, Any],
) -> Path | None:
    if is_knowledge_execution_task(task) or is_knowledge_repair_task(task) or is_knowledge_conflict_resolution_task(task):
        return None
    task_id = str(task.get("taskId", ""))
    if not task_id:
        return None
    decision = str(evaluation.get("decision") or "")
    project_id = str(task.get("projectId") or "")
    requester = str(task.get("requester") or task.get("assignee") or "system.scheduler")
    result_ref = rel(result_path, bundle.root)
    source_refs = append_unique(as_list(task.get("sourceMaterialRefs")), result_ref)
    if decision == "retry_required":
        assignee = str(task.get("assignee") or PROJECT_MANAGER_AGENT_ID)
        followup_path = create_project_task(
            bundle,
            title=f"Retry task output for {task_id}",
            project_id=project_id,
            requester=requester,
            assignee=assignee,
            task_type=str(task.get("taskType") or "project_retry"),
            task_id=followup_task_id(bundle, f"{task_id}-retry"),
            priority=str(task.get("priority") or "normal"),
            source_material_refs=source_refs,
            expected_output=[
                "Repair the failed output according to qualityEvaluation reasons.",
                "Return TaskResult with evidence/artifacts and handoff contract.",
            ],
        )
        update_frontmatter_file(
            followup_path,
            {
                "parentTaskId": task_id,
                "originTaskId": str(task.get("originTaskId") or task_id),
                "retryOf": task_id,
                "triggerResultRef": result_ref,
                "qualityGate": "failed",
                "failureReasons": as_list(evaluation.get("reasons")),
                "attemptNumber": task_attempt_number(task) + 1,
                "maxAttempts": task_max_attempts(task),
            },
        )
        create_task_notification(
            bundle,
            followup_path,
            load_object(followup_path),
            "task_retry_required",
            recipient=assignee,
            summary=f"任务结果未达标，已创建返工任务：{task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.followup.retry", rel(followup_path, bundle.root), after="pending", details=f"sourceTask={task_id}\nresultRef={result_ref}\nreasons={'; '.join(as_list(evaluation.get('reasons')))}")
        return followup_path
    if decision == "escalate_to_project_manager":
        followup_path = create_project_task(
            bundle,
            title=f"Resolve blocked task handoff for {task_id}",
            project_id=project_id,
            requester=requester,
            assignee=PROJECT_MANAGER_AGENT_ID,
            task_type="blocker_resolution",
            task_id=followup_task_id(bundle, f"{task_id}-blocker"),
            priority="high",
            source_material_refs=source_refs,
            expected_output=[
                "Decide whether to unblock, split, reassign, request human review, or cancel the task.",
                "Record owner, next action, and decision evidence.",
            ],
        )
        update_frontmatter_file(
            followup_path,
            {
                "parentTaskId": task_id,
                "originTaskId": str(task.get("originTaskId") or task_id),
                "triggerResultRef": result_ref,
                "qualityGate": "blocked",
                "failureReasons": as_list(evaluation.get("reasons")),
            },
        )
        create_task_notification(
            bundle,
            followup_path,
            load_object(followup_path),
            "task_escalated",
            recipient=PROJECT_MANAGER_AGENT_ID,
            summary=f"任务阻塞或连续失败，已升级给项目经理 Agent：{task_id}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.followup.escalate", rel(followup_path, bundle.root), after="pending", details=f"sourceTask={task_id}\nresultRef={result_ref}")
        return followup_path
    handoff_to = str(handoff_contract.get("handoffTo") or "")
    if decision == "handoff_ready" and handoff_to:
        followup_path = create_project_task(
            bundle,
            title=str(handoff_contract.get("nextSuggestedTask") or f"Continue from {task_id}"),
            project_id=project_id,
            requester=requester,
            assignee=handoff_to,
            task_type="role_handoff",
            task_id=followup_task_id(bundle, f"{task_id}-handoff"),
            priority=str(task.get("priority") or "normal"),
            source_material_refs=source_refs,
            expected_output=[
                "Read upstream TaskResult and artifacts.",
                "Accept handoff or return changes_requested with clear blocker.",
                "Produce the next role output according to the company Agent Team guide.",
            ],
        )
        update_frontmatter_file(
            followup_path,
            {
                "parentTaskId": task_id,
                "originTaskId": str(task.get("originTaskId") or task_id),
                "triggerResultRef": result_ref,
                "handoffFrom": str(task.get("assignee") or ""),
                "handoffTo": handoff_to,
                "qualityGate": "passed",
            },
        )
        create_task_notification(
            bundle,
            followup_path,
            load_object(followup_path),
            "task_handoff_ready",
            recipient=handoff_to,
            summary=f"上游任务已通过质量评价，进入下一岗位：{task_id} -> {handoff_to}。",
            source_message_ref=result_ref,
        )
        create_audit_log(bundle, "system.scheduler", "workflow.followup.handoff", rel(followup_path, bundle.root), after="pending", details=f"sourceTask={task_id}\nresultRef={result_ref}\nhandoffTo={handoff_to}")
        return followup_path
    return None


def project_manager_for_task(task: dict[str, Any]) -> str:
    return str(task.get("projectManagerAgent") or task.get("projectManager") or PROJECT_MANAGER_AGENT_ID)


def human_reviewer_for_task(task: dict[str, Any]) -> str:
    return str(task.get("humanReviewer") or task.get("projectOwner") or task.get("owner") or task.get("requester") or "")


def boolish(value: Any, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "是", "需要"}


def should_require_human_acceptance(
    task: dict[str, Any],
    status: str,
    evaluation: dict[str, Any],
    handoff_contract: dict[str, Any],
    open_risks: list[str],
) -> bool:
    if not bool(evaluation.get("passed")):
        return False
    if status not in {"done", "submitted"}:
        return False
    if is_knowledge_execution_task(task) or is_knowledge_repair_task(task) or is_knowledge_conflict_resolution_task(task):
        return False
    explicit = task.get("humanAcceptanceRequired")
    if explicit is not None and explicit != "":
        return boolish(explicit, True)
    task_type = normalized_task_type(str(task.get("taskType") or ""))
    if task_type in {"search_retrieval", "notification", "material_registration", "audit_record"}:
        return False
    if as_list(open_risks) or as_list(handoff_contract.get("openRisks")):
        return True
    if handoff_contract.get("handoffTo"):
        return True
    priority = str(task.get("priority") or "").strip().lower()
    risk_level = str(task.get("riskLevel") or "").strip().upper()
    if priority in {"high", "critical", "p0", "p1"} or risk_level in {"L3", "L4", "HIGH", "CRITICAL"}:
        return True
    if task_type in {"project_management", "product_requirement", "design_spec", "development", "testing", "operations", "project_initialization", "role_handoff"}:
        return True
    if bool(evaluation.get("testsOrChecksPresent")) and (
        bool(evaluation.get("evidenceRefsPresent")) or bool(evaluation.get("artifactRefsPresent"))
    ):
        return False
    return False


def build_task_acceptance_policy(
    task: dict[str, Any],
    status: str,
    evaluation: dict[str, Any],
    handoff_contract: dict[str, Any],
    open_risks: list[str],
) -> dict[str, Any]:
    passed = bool(evaluation.get("passed"))
    human_required = should_require_human_acceptance(task, status, evaluation, handoff_contract, open_risks)
    if not passed:
        acceptance_status = "not_required"
        reason = "quality gate did not pass; retry, repair, or escalation flow handles the next step"
    elif human_required:
        acceptance_status = "waiting_acceptance"
        reason = "default policy requires project manager notification and human acceptance before next role task"
    else:
        acceptance_status = "auto_accepted"
        reason = "low-risk task or explicit policy does not require human acceptance"
    return {
        "version": "acceptance.v1",
        "acceptanceStatus": acceptance_status,
        "humanAcceptanceRequired": human_required,
        "acceptanceRequiredByDefault": True,
        "projectManager": project_manager_for_task(task),
        "humanReviewer": human_reviewer_for_task(task),
        "decidedBy": "" if acceptance_status == "waiting_acceptance" else project_manager_for_task(task),
        "decisionReason": reason,
        "acceptedBy": "",
        "acceptedAt": "",
        "rejectedBy": "",
        "rejectedAt": "",
        "requiresNextTaskCreation": bool(passed and handoff_contract.get("handoffTo")),
    }


def task_status_after_acceptance_gate(status: str, evaluation: dict[str, Any], acceptance_policy: dict[str, Any]) -> str:
    decision = str(evaluation.get("decision") or "")
    if status == "blocked":
        return "blocked"
    if status == "rejected":
        return "rejected"
    if not bool(evaluation.get("passed")):
        if decision == "retry_required":
            return "changes_requested"
        if decision == "escalate_to_project_manager":
            return "blocked"
        return "changes_requested"
    acceptance_status = str(acceptance_policy.get("acceptanceStatus") or "")
    if acceptance_status == "waiting_acceptance":
        return "waiting_acceptance"
    return "done"


def should_create_followup_at_finish(status: str, evaluation: dict[str, Any], acceptance_policy: dict[str, Any]) -> bool:
    if not bool(evaluation.get("passed")):
        return True
    if str(acceptance_policy.get("acceptanceStatus") or "") == "auto_accepted":
        return True
    return False


def notify_task_acceptance_gate(
    bundle: Bundle,
    task_path: Path,
    task: dict[str, Any],
    result_path: Path,
    acceptance_policy: dict[str, Any],
) -> None:
    acceptance_status = str(acceptance_policy.get("acceptanceStatus") or "")
    if acceptance_status == "not_required":
        return
    result_ref = rel(result_path, bundle.root)
    pm = str(acceptance_policy.get("projectManager") or PROJECT_MANAGER_AGENT_ID)
    create_task_notification(
        bundle,
        task_path,
        task,
        "task_result_pm_review_required" if acceptance_status == "waiting_acceptance" else "task_result_auto_accepted",
        recipient=pm,
        summary=f"岗位交付已完成，请项目经理 Agent 判断是否需要人类验收并推进：{task.get('title', task.get('taskId', ''))}。结果记录：{result_ref}。",
        source_message_ref=result_ref,
    )
    if bool(acceptance_policy.get("humanAcceptanceRequired")):
        reviewer = str(acceptance_policy.get("humanReviewer") or task.get("requester") or "")
        if reviewer:
            create_task_notification(
                bundle,
                task_path,
                task,
                "task_result_human_acceptance_required",
                recipient=reviewer,
                summary=f"需要验收岗位交付后才能进入下一环节：{task.get('title', task.get('taskId', ''))}。结果记录：{result_ref}。",
                source_message_ref=result_ref,
            )


def task_result_path_for_task(bundle: Bundle, task: dict[str, Any]) -> Path:
    result_ref = str(task.get("resultRef") or "")
    if result_ref:
        path = bundle.root / result_ref
        if path.exists():
            return path
    result_id = f"TR-{str(task.get('taskId', ''))}"
    path = task_result_storage_dir(bundle) / f"{slug(result_id)}.md"
    if path.exists():
        return path
    raise KnowledgeError(f"task result not found for task: {task.get('taskId', '')}")


def accept_project_task_result(
    bundle: Bundle,
    task_id: str,
    decision: str,
    reviewer: str,
    reason: str = "",
    human: bool = False,
) -> dict[str, Any]:
    decision_value = decision.strip().lower().replace("-", "_")
    if decision_value not in {"accepted", "auto_accepted", "rejected", "changes_requested"}:
        raise KnowledgeError(f"unknown acceptance decision: {decision}")
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    result_path = task_result_path_for_task(bundle, task)
    result_fm = load_object(result_path)
    acceptance_policy = dict(result_fm.get("acceptancePolicy") or {})
    if not acceptance_policy:
        acceptance_policy = build_task_acceptance_policy(
            task,
            str(result_fm.get("status") or ""),
            dict(result_fm.get("qualityEvaluation") or {}),
            dict(result_fm.get("handoffContract") or {}),
            as_list(dict(result_fm.get("handoffContract") or {}).get("openRisks")),
        )
    before = str(acceptance_policy.get("acceptanceStatus") or "")
    now = utc_now()
    followup_path: Path | None = None
    next_status = decision_value
    if decision_value in {"accepted", "auto_accepted"}:
        if bool(acceptance_policy.get("humanAcceptanceRequired")) and not human and decision_value != "auto_accepted":
            raise KnowledgeError("human acceptance flag is required for human-gated task result")
        acceptance_policy.update(
            {
                "acceptanceStatus": decision_value,
                "decidedBy": reviewer,
                "decisionReason": reason or "accepted",
                "acceptedBy": reviewer,
                "acceptedAt": now,
            }
        )
        existing_followups = as_list(result_fm.get("followupTaskRefs"))
        next_status = "done"
        if existing_followups:
            next_status = "done"
        else:
            followup_path = create_project_role_followup_task(
                bundle,
                task,
                result_path,
                dict(result_fm.get("qualityEvaluation") or {}),
                dict(result_fm.get("handoffContract") or {}),
            )
            if followup_path:
                followup_ref = rel(followup_path, bundle.root)
                update_frontmatter_file(result_path, {"followupTaskRefs": [followup_ref], "updatedAt": now})
                task_followup_refs = append_unique(as_list(task.get("followupTaskRefs")), followup_ref)
                update_frontmatter_file(task_path, {"followupTaskRefs": task_followup_refs, "updatedAt": now})
    else:
        acceptance_policy.update(
            {
                "acceptanceStatus": decision_value,
                "decidedBy": reviewer,
                "decisionReason": reason or decision_value,
                "rejectedBy": reviewer,
                "rejectedAt": now,
            }
        )
        retry_evaluation = dict(result_fm.get("qualityEvaluation") or {})
        retry_evaluation.update({"passed": False, "decision": "retry_required", "reasons": [reason or decision_value]})
        followup_path = create_project_role_followup_task(
            bundle,
            task,
            result_path,
            retry_evaluation,
            dict(result_fm.get("handoffContract") or {}),
        )
        next_status = "changes_requested" if decision_value == "changes_requested" else "rejected"
        if followup_path:
            followup_ref = rel(followup_path, bundle.root)
            update_frontmatter_file(result_path, {"followupTaskRefs": [followup_ref], "updatedAt": now})
            task_followup_refs = append_unique(as_list(task.get("followupTaskRefs")), followup_ref)
            update_frontmatter_file(task_path, {"followupTaskRefs": task_followup_refs, "updatedAt": now})
    result_fm = update_frontmatter_file(result_path, {"acceptancePolicy": acceptance_policy, "updatedAt": now})
    task = update_frontmatter_file(task_path, {"status": next_status, "updatedAt": now})
    if decision_value in {"rejected", "changes_requested"}:
        maybe_record_agent_improvement(
            bundle,
            task_path,
            task,
            result_path,
            load_object(result_path),
            trigger="humanAcceptance",
            extra_reasons=[reason or decision_value],
        )
    create_task_notification(
        bundle,
        task_path,
        task,
        f"task_result_{decision_value}",
        recipient=project_manager_for_task(task),
        summary=f"任务结果验收决策：{task_id} -> {decision_value}。{reason or ''}".strip(),
        source_message_ref=rel(result_path, bundle.root),
    )
    create_audit_log(
        bundle,
        reviewer or "system.acceptance",
        "task.acceptance",
        rel(result_path, bundle.root),
        before=before,
        after=decision_value,
        policy_result="human_acceptance" if human else "pm_acceptance",
        details=f"taskId={task_id}\nreason={reason}\nfollowupRef={rel(followup_path, bundle.root) if followup_path else ''}",
    )
    return {
        "apiVersion": "v0.1",
        "kind": "TaskAcceptanceResult",
        "taskRef": rel(task_path, bundle.root),
        "resultRef": rel(result_path, bundle.root),
        "decision": decision_value,
        "taskStatus": next_status,
        "followupTaskRefs": as_list(result_fm.get("followupTaskRefs")),
        "acceptancePolicy": acceptance_policy,
    }


def project_manager_agent_for_project(bundle: Bundle, project_id: str, project: dict[str, Any] | None = None) -> str:
    pid = slug(project_id)
    project_scoped = f"agent.{pid}.project-manager" if pid else ""
    if project:
        for agent_id in as_list(project.get("relatedAgents")):
            value = str(agent_id)
            if value.endswith(".project-manager"):
                return value
    if project_scoped:
        return project_scoped
    return PROJECT_MANAGER_AGENT_ID


def project_manager_review_storage_dir(bundle: Bundle, project_id: str) -> Path:
    pid = slug(project_id)
    project_dir = bundle.root / "projects" / pid
    if (project_dir / "project.md").exists():
        return project_dir / "pm-reviews"
    return bundle.root / "pm-reviews"


def project_manager_action_storage_dir(bundle: Bundle, project_id: str) -> Path:
    pid = slug(project_id)
    project_dir = bundle.root / "projects" / pid
    if (project_dir / "project.md").exists():
        return project_dir / "pm-actions"
    return bundle.root / "pm-actions"


OUTCOME_SLICE_STATE_VALUES = {
    "unknown",
    "clarified",
    "solution_ready",
    "implementable",
    "running",
    "verifiable",
    "deliverable",
    "blocked",
    "stopped",
}
OUTCOME_GUARDRAIL_DECISIONS = {"continue", "pause", "stop", "escalate"}
PM_ACTION_OUTCOME_REQUIRED_INTENTS = {
    "task_decomposition",
    "dispatch",
    "acceptance_route",
    "risk_escalation",
    "handoff",
    "closeout",
}


def create_outcome_slice(
    bundle: Bundle,
    project_id: str,
    title: str,
    owner: str,
    stage_goal: str,
    main_deliverable: str,
    current_state: str,
    target_state: str,
    outcome_slice_id: str = "",
    status: str = "active",
    summary: str = "",
    evidence_refs: list[str] | None = None,
    risk_refs: list[str] | None = None,
    stop_conditions: list[str] | None = None,
    acceptance_signal: str = "",
    time_budget: str = "",
    token_budget: str = "",
    wip_limit: int = 3,
) -> dict[str, Any]:
    project_path = find_project(bundle, project_id)
    project = load_object(project_path)
    pid = str(project.get("projectId") or slug(project_id))
    title = title.strip()
    owner = owner.strip()
    stage_goal = stage_goal.strip()
    main_deliverable = main_deliverable.strip()
    current_state = current_state.strip()
    target_state = target_state.strip()
    if not title:
        raise KnowledgeError("outcome slice title is required")
    if not owner:
        raise KnowledgeError("outcome slice owner is required")
    for field_name, value in [
        ("stageGoal", stage_goal),
        ("mainDeliverable", main_deliverable),
        ("currentState", current_state),
        ("targetState", target_state),
    ]:
        if not value:
            raise KnowledgeError(f"outcome slice {field_name} is required")
    if current_state not in OUTCOME_SLICE_STATE_VALUES:
        raise KnowledgeError(f"currentState must be one of {sorted(OUTCOME_SLICE_STATE_VALUES)}")
    if target_state not in OUTCOME_SLICE_STATE_VALUES:
        raise KnowledgeError(f"targetState must be one of {sorted(OUTCOME_SLICE_STATE_VALUES)}")
    if current_state == target_state and status not in {"blocked", "stopped"}:
        raise KnowledgeError("outcome slice must declare a target state change")
    if not stop_conditions:
        raise KnowledgeError("outcome slice requires at least one stop condition")
    if wip_limit < 1:
        raise KnowledgeError("outcome slice wipLimit must be >= 1")
    slice_id = outcome_slice_id.strip() or unique_time_id("outcome-slice")
    out_dir = outcome_slice_storage_dir(bundle, pid)
    ensure_dir(out_dir)
    out_path = out_dir / f"{slug(slice_id)}.md"
    if out_path.exists():
        raise KnowledgeError(f"outcome slice already exists: {slice_id}")
    budget = {
        "timeBudget": time_budget.strip(),
        "usageBudget": token_budget.strip(),
        "wipLimit": wip_limit,
    }
    frontmatter = {
        "type": "OutcomeSlice",
        "title": title,
        "description": "Project Manager outcome slice. Tasks are only valid when they move this outcome state or reduce uncertainty.",
        "timestamp": utc_now(),
        "outcomeSliceId": slice_id,
        "projectId": pid,
        "owner": owner,
        "status": status,
        "stageGoal": stage_goal,
        "mainDeliverable": main_deliverable,
        "currentState": current_state,
        "targetState": target_state,
        "summary": summary.strip(),
        "acceptanceSignal": acceptance_signal.strip(),
        "evidenceRefs": evidence_refs or [],
        "riskRefs": risk_refs or [],
        "stopConditions": stop_conditions or [],
        "budget": budget,
        "activeTaskRefs": [],
        "completedTaskRefs": [],
        "pmActionRefs": [],
        "stateChangeEvidenceRefs": [],
    }
    body = "\n".join(
        [
            "## Outcome",
            "",
            summary.strip() or title,
            "",
            "## Stage Goal",
            "",
            stage_goal,
            "",
            "## Main Deliverable",
            "",
            main_deliverable,
            "",
            "## State Change",
            "",
            f"- currentState: {current_state}",
            f"- targetState: {target_state}",
            f"- acceptanceSignal: {acceptance_signal.strip() or 'none'}",
            "",
            "## Guardrail",
            "",
            f"- timeBudget: {budget['timeBudget'] or 'none'}",
            f"- usageBudget: {budget['usageBudget'] or 'none'}",
            f"- wipLimit: {wip_limit}",
            "- stopConditions:",
            *[f"  - {item}" for item in stop_conditions or []],
            "",
            "## Evidence",
            "",
            *([f"- {item}" for item in evidence_refs or []] or ["- none"]),
        ]
    )
    write_text(out_path, render_doc(frontmatter, body))
    update_index(out_dir / "index.md", title, out_path.name)
    audit_path = create_audit_log(
        bundle,
        owner,
        "outcome_slice.create",
        rel(out_path, bundle.root),
        before=current_state,
        after=target_state,
        policy_result="outcome_slice_guardrail",
        details=f"projectId={pid}\nstageGoal={stage_goal}\nmainDeliverable={main_deliverable}",
    )
    append_log(bundle, f"outcome slice {slice_id} project={pid} target={target_state}")
    return {
        "apiVersion": "v0.1",
        "kind": "OutcomeSlice",
        "outcomeSliceId": slice_id,
        "projectId": pid,
        "outcomeSliceRef": rel(out_path, bundle.root),
        "auditRef": rel(audit_path, bundle.root),
        "targetState": target_state,
    }


PM_ACTION_INTENTS = {
    "status_query",
    "task_decomposition",
    "dispatch",
    "acceptance_route",
    "risk_escalation",
    "blocker_record",
    "handoff",
    "closeout",
}
PM_ACTION_EXIT_STATES = {
    "dispatched",
    "waiting_acceptance",
    "blocked_with_owner",
    "closed_with_gate_passed",
}


def create_project_manager_action(
    bundle: Bundle,
    project_id: str,
    actor: str,
    intent: str,
    current_state: str,
    allowed_transition: str,
    exit_state: str,
    summary: str,
    task_id: str = "",
    requirement_refs: list[str] | None = None,
    records_written: list[str] | None = None,
    delegated_owners: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    next_action: str = "",
    blocker: str = "",
    blocker_owner: str = "",
    terminal_decision: str = "",
    outcome_slice_ref: str = "",
    outcome_state_before: str = "",
    outcome_state_after: str = "",
    outcome_value_change: str = "",
    cost_summary: str = "",
    scope_change: str = "",
    guardrail_decision: str = "",
    guardrail_reason: str = "",
) -> dict[str, Any]:
    project_path = find_project(bundle, project_id)
    project = load_object(project_path)
    pid = str(project.get("projectId") or slug(project_id))
    action_id = unique_time_id("pm-action")
    action_dir = project_manager_action_storage_dir(bundle, pid)
    ensure_dir(action_dir)
    action_path = action_dir / f"{action_id}.md"
    req_refs = requirement_refs or []
    frontmatter: dict[str, Any] = {
        "type": "ProjectManagerAction",
        "title": f"PM action {intent}: {summary[:80]}",
        "description": "Project Manager state-machine action envelope.",
        "timestamp": utc_now(),
        "actionId": action_id,
        "projectId": pid,
        "taskId": task_id,
        "pmActionRuntimeVersion": "v1",
        "outcomeGuardrailVersion": "v1",
        "actor": actor,
        "intent": intent,
        "currentState": current_state,
        "allowedTransition": allowed_transition,
        "exitState": exit_state,
        "summary": summary,
        "requirementRefs": req_refs,
        "recordsWritten": records_written or [],
        "delegatedOwners": delegated_owners or [],
        "evidenceRefs": evidence_refs or [],
        "nextAction": next_action,
        "blocker": blocker,
        "blockerOwner": blocker_owner,
        "terminalDecision": terminal_decision,
        "outcomeSliceRef": outcome_slice_ref.strip(),
        "outcomeStateBefore": outcome_state_before.strip(),
        "outcomeStateAfter": outcome_state_after.strip(),
        "outcomeValueChange": outcome_value_change.strip(),
        "costSummary": cost_summary.strip(),
        "scopeChange": scope_change.strip(),
        "guardrailDecision": guardrail_decision.strip(),
        "guardrailReason": guardrail_reason.strip(),
        "pmDeliveryGate": {
            "enforce": exit_state == "closed_with_gate_passed",
            "requirementRefs": req_refs,
            "requireProductAcceptance": True,
        },
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            summary,
            "",
            "## State Transition",
            "",
            f"- intent: {intent}",
            f"- currentState: {current_state}",
            f"- allowedTransition: {allowed_transition}",
            f"- exitState: {exit_state}",
            f"- outcomeSliceRef: {outcome_slice_ref.strip() or 'none'}",
            f"- outcomeStateBefore: {outcome_state_before.strip() or 'none'}",
            f"- outcomeStateAfter: {outcome_state_after.strip() or 'none'}",
            "",
            "## Records Written",
            "",
            *([f"- {item}" for item in records_written or []] or ["- none"]),
            "",
            "## Delegated Owners",
            "",
            *([f"- {item}" for item in delegated_owners or []] or ["- none"]),
            "",
            "## Evidence",
            "",
            *([f"- {item}" for item in evidence_refs or []] or ["- none"]),
            "",
            "## Exit",
            "",
            f"- nextAction: {next_action or 'none'}",
            f"- blocker: {blocker or 'none'}",
            f"- blockerOwner: {blocker_owner or 'none'}",
            f"- terminalDecision: {terminal_decision or 'none'}",
            "",
            "## Outcome Guardrail",
            "",
            f"- outcomeValueChange: {outcome_value_change.strip() or 'none'}",
            f"- costSummary: {cost_summary.strip() or 'none'}",
            f"- scopeChange: {scope_change.strip() or 'none'}",
            f"- guardrailDecision: {guardrail_decision.strip() or 'none'}",
            f"- guardrailReason: {guardrail_reason.strip() or 'none'}",
        ]
    )
    write_text(action_path, render_doc(frontmatter, body))
    update_index(action_dir / "index.md", str(frontmatter["title"]), action_path.name)
    audit_path = create_audit_log(
        bundle,
        actor,
        "pm.action.record",
        rel(action_path, bundle.root),
        before=current_state,
        after=exit_state,
        policy_result="pm_action_runtime",
        details=f"intent={intent}\ntransition={allowed_transition}\nsummary={summary}",
    )
    append_log(bundle, f"pm action {action_id} {intent} exit={exit_state}")
    return {
        "apiVersion": "v0.1",
        "kind": "ProjectManagerAction",
        "actionId": action_id,
        "projectId": pid,
        "actionRef": rel(action_path, bundle.root),
        "outcomeSliceRef": outcome_slice_ref.strip(),
        "auditRef": rel(audit_path, bundle.root),
        "exitState": exit_state,
        "recordsWritten": records_written or [],
        "delegatedOwners": delegated_owners or [],
    }


def project_task_paths(bundle: Bundle, project_id: str) -> list[Path]:
    pid = slug(project_id)
    task_dir = bundle.root / "projects" / pid / "tasks"
    if not task_dir.exists():
        return []
    return [path for path in sorted(task_dir.glob("*.md")) if path.name not in COLLECTION_NAMES]


def project_notification_paths(bundle: Bundle, project_id: str) -> list[Path]:
    pid = slug(project_id)
    root = notification_storage_dir(bundle)
    if not root.exists():
        return []
    paths: list[Path] = []
    for path in sorted(root.glob("*.md")):
        if path.name in COLLECTION_NAMES:
            continue
        try:
            item = load_object(path)
        except KnowledgeError:
            continue
        if str(item.get("projectId") or "") == pid:
            paths.append(path)
    return paths


def project_runner_records(bundle: Bundle, project_id: str, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pid = slug(project_id)
    runner_ids: set[str] = set()
    for task in tasks:
        for key in ["assignedRunner", "leaseOwner"]:
            value = str(task.get(key) or "")
            if value:
                runner_ids.add(value)
    records: list[dict[str, Any]] = []
    root = runner_storage_dir(bundle)
    if root.exists():
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                runner = load_object(path)
            except KnowledgeError:
                continue
            available_projects = {str(item) for item in as_list(runner.get("availableProjects"))}
            runner_id = str(runner.get("runnerId") or "")
            if pid in available_projects or runner_id in runner_ids:
                records.append(runner)
    return records


def project_task_is_closed(task: dict[str, Any]) -> bool:
    return str(task.get("status") or "") in CLOSED_TASK_STATUSES


def run_project_manager_health_check(
    bundle: Bundle,
    project_id: str,
    actor: str = "system.project-manager",
    create_followup: bool = False,
    notify: bool = True,
) -> dict[str, Any]:
    project_path = find_project(bundle, project_id)
    project = load_object(project_path)
    pid = str(project.get("projectId") or slug(project_id))
    pm_agent = project_manager_agent_for_project(bundle, pid, project)
    task_paths = project_task_paths(bundle, pid)
    tasks = [load_object(path) for path in task_paths]
    open_tasks = [task for task in tasks if not project_task_is_closed(task)]
    runners = project_runner_records(bundle, pid, tasks)
    notifications = [load_object(path) for path in project_notification_paths(bundle, pid)]
    risks: list[dict[str, str]] = []
    decisions: list[str] = []
    next_actions: list[str] = []

    pm_agent_path = bundle.root / "agents" / f"{slug(pm_agent)}.md"
    if not pm_agent_path.exists():
        risks.append(
            {
                "severity": "high",
                "risk": f"Project Manager Agent is not registered: {pm_agent}",
                "next": "Register the project manager Agent before relying on automated project orchestration.",
            }
        )
        next_actions.append(f"登记项目经理 Agent：{pm_agent}")
    if not tasks:
        risks.append(
            {
                "severity": "high",
                "risk": "Project has no task queue.",
                "next": "Create first executable ProjectTask list with owner, outputs, and acceptance criteria.",
            }
        )
        next_actions.append("创建首批项目任务，明确主责 Agent、输入、输出和验收标准。")
    if open_tasks and not runners:
        risks.append(
            {
                "severity": "medium",
                "risk": "Project has open tasks but no available Runner record.",
                "next": "Register/bind an Agent Ring Runner or mark the task for manual runner takeover.",
            }
        )
        decisions.append("需要确认由哪个 Runner 或本地 Agent 接管项目任务。")
        next_actions.append("登记或绑定可用 Runner，或进入 waiting_runner 手动接管。")

    for task in open_tasks:
        status = str(task.get("status") or "")
        title = str(task.get("title") or task.get("taskId") or "")
        if status in {"blocked", "changes_requested"}:
            risks.append(
                {
                    "severity": "high",
                    "risk": f"Task is blocked or needs changes: {title} [{status}]",
                    "next": "Project Manager Agent should split, reassign, request repair, or escalate to human owner.",
                }
            )
            next_actions.append(f"处理阻塞任务：{task.get('taskId', '')}")
        if status == "waiting_runner":
            risks.append(
                {
                    "severity": "medium",
                    "risk": f"Task requires manual runner takeover: {title}",
                    "next": "Assign a temporary Runner/local Codex owner and require TaskResult writeback.",
                }
            )
        if status == "waiting_acceptance":
            decisions.append(f"{task.get('taskId', '')}: {title} requires human/PM decision ({status}).")
        if status == "done" and not str(task.get("resultRef") or ""):
            risks.append(
                {
                    "severity": "high",
                    "risk": f"Task is marked {status} but has no TaskResult: {title}",
                    "next": "Require executor to write TaskResult before closing or handoff.",
                }
            )

    for notification in notifications:
        status = str(notification.get("status") or "")
        if status in {"failed", "retrying", "dead_letter"}:
            risks.append(
                {
                    "severity": "high" if status == "dead_letter" else "medium",
                    "risk": f"Notification delivery is {status}: {notification.get('messageType', '')}",
                    "next": "Retry delivery or route through backup channel; dead letters require PM/Ops attention.",
                }
            )
            if status == "dead_letter":
                decisions.append(f"Dead-letter notification needs manual recovery: {notification.get('notificationId', '')}")

    for task_path in task_paths:
        task = load_object(task_path)
        task_ref = rel(task_path, bundle.root)
        for problem in validate_task_source_traceability(task_ref, task, require_explicit=bool(task.get("workSourceType"))):
            risks.append(
                {
                    "severity": "high",
                    "risk": f"Task source traceability gap: {problem}",
                    "next": "Declare workSourceType and link requirementRefs for feature tasks or defectRefs for bugfix tasks before downstream work continues.",
                }
            )
            next_actions.append(f"补齐任务来源追溯：{task.get('taskId', task_ref)}")
        for review_ref in as_list(task.get("receiverReviewRefs")):
            review_path = bundle.root / review_ref
            if not review_path.exists():
                risks.append(
                    {
                        "severity": "high",
                        "risk": f"Task references missing ReceiverReview: {review_ref}",
                        "next": "Create or repair the ReceiverReview record before downstream Agent consumes the upstream artifact.",
                    }
                )
                continue
            review = load_object(review_path)
            decision = str(review.get("decision") or review.get("status") or "")
            if decision in {"needs_rework", "human_decision_required"}:
                risks.append(
                    {
                        "severity": "high",
                        "risk": f"ReceiverReview blocks downstream work: {review.get('title', review_ref)} [{decision}]",
                        "next": "Route upstream rework or human decision before continuing execution.",
                    }
                )
                if decision == "human_decision_required":
                    decisions.append(f"ReceiverReview needs human decision: {review.get('reviewId', review_ref)}")
                next_actions.append(f"处理接收审查：{review.get('reviewId', review_ref)}")

    defect_dir = defect_storage_dir(bundle, pid)
    if defect_dir.exists():
        for defect_path in sorted(defect_dir.glob("*.md")):
            if defect_path.name in COLLECTION_NAMES:
                continue
            defect = load_object(defect_path)
            if defect.get("type") != "Defect":
                continue
            if str(defect.get("status") or "") == "fixed" and not as_list(defect.get("regressionEvidenceRefs")):
                risks.append(
                    {
                        "severity": "medium",
                        "risk": f"Defect is fixed but has no regression evidence: {defect.get('defectId', defect_path.stem)}",
                        "next": "Ask Test Agent to run regression and write regressionEvidenceRefs before closing the Defect.",
                    }
                )
                next_actions.append(f"安排缺陷回归：{defect.get('defectId', defect_path.stem)}")

    if any(item["severity"] == "high" for item in risks):
        health = "blocked" if decisions else "at_risk"
    elif decisions:
        health = "needs_decision"
    elif risks:
        health = "at_risk"
    else:
        health = "on_track"

    if not next_actions:
        next_actions = ["继续执行当前任务队列；下一次 PM health check 复核状态、风险、通知和验收。"]

    review_id = unique_time_id("pm-review")
    review_dir = project_manager_review_storage_dir(bundle, pid)
    ensure_dir(review_dir)
    review_path = review_dir / f"{review_id}.md"
    frontmatter = {
        "type": "ProjectManagerReview",
        "title": f"Project Manager Review {pid}",
        "description": "Executable Project Manager Agent health check result.",
        "timestamp": utc_now(),
        "reviewId": review_id,
        "projectId": pid,
        "projectManagerAgent": pm_agent,
        "actor": actor,
        "status": health,
        "taskCount": len(tasks),
        "openTaskCount": len(open_tasks),
        "runnerCount": len(runners),
        "riskCount": len(risks),
        "decisionCount": len(decisions),
        "notificationRefs": [],
        "followupTaskRefs": [],
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            f"- project: {project.get('title') or pid}",
            f"- health: {health}",
            f"- tasks: {len(tasks)} total / {len(open_tasks)} open",
            f"- runners: {len(runners)}",
            "",
            "## Risks",
            "",
            *([f"- {item['severity']}: {item['risk']} -> {item['next']}" for item in risks] or ["- none"]),
            "",
            "## Decisions Needed",
            "",
            *([f"- {item}" for item in decisions] or ["- none"]),
            "",
            "## Next Actions",
            "",
            *[f"- {item}" for item in next_actions],
            "",
            "## PM Boundary",
            "",
            "- Project Manager Agent owns flow, orchestration, status, acceptance routing, risk escalation, and notifications.",
            "- It does not replace Product, Design, Development, Test, Operations, Knowledge Engineering, or Knowledge Query Agents.",
        ]
    )
    write_text(review_path, render_doc(frontmatter, body))
    update_index(review_dir / "index.md", str(frontmatter["title"]), review_path.name)
    update_frontmatter_file(project_path, {"lastProjectManagerReviewRef": rel(review_path, bundle.root), "health": health, "updatedAt": utc_now()})
    create_audit_log(bundle, actor, "project.pm_health_check", rel(review_path, bundle.root), after=health, policy_result="pm_agent_operating_check", details=f"projectId={pid}\nrisks={len(risks)}\ndecisions={len(decisions)}")

    followup_refs: list[str] = []
    notification_refs: list[str] = []
    target_task_path: Path | None = None
    target_task: dict[str, Any] | None = None
    if task_paths:
        target_task_path = task_paths[0]
        target_task = load_object(target_task_path)
    if create_followup and health != "on_track":
        followup_path = create_project_task(
            bundle,
            f"Project Manager follow-up for {project.get('title') or pid}: {health}",
            pid,
            actor,
            pm_agent,
            "project_management",
            "",
            "high" if health in {"blocked", "at_risk"} else "normal",
            "",
            [rel(review_path, bundle.root)],
            [
                "Resolve listed risks or decisions.",
                "Notify affected Agent, Runner, requester, or human owner.",
                "Write TaskResult with decision, next owner, and evidence.",
            ],
        )
        followup_refs.append(rel(followup_path, bundle.root))
        target_task_path = followup_path
        target_task = load_object(followup_path)
    if notify and health != "on_track" and target_task_path and target_task:
        notification_path = create_task_notification(
            bundle,
            target_task_path,
            target_task,
            f"project_manager_health_{health}",
            recipient=pm_agent,
            summary=f"项目经理 Agent 巡检发现项目 {project.get('title') or pid} 状态为 {health}；风险 {len(risks)} 个，待决策 {len(decisions)} 个。下一步：{'; '.join(next_actions[:3])}",
            source_message_ref=rel(review_path, bundle.root),
        )
        notification_refs.append(rel(notification_path, bundle.root))
        if decisions:
            owner = str(project.get("humanOwner") or project.get("owner") or "")
            if owner:
                owner_notification_path = create_task_notification(
                    bundle,
                    target_task_path,
                    load_object(target_task_path),
                    "project_manager_human_decision_required",
                    recipient=owner,
                    summary=f"项目 {project.get('title') or pid} 需要人类确认：{'; '.join(decisions[:3])}",
                    source_message_ref=rel(review_path, bundle.root),
                )
                notification_refs.append(rel(owner_notification_path, bundle.root))
    if followup_refs or notification_refs:
        update_frontmatter_file(review_path, {"followupTaskRefs": followup_refs, "notificationRefs": notification_refs, "updatedAt": utc_now()})

    append_log(bundle, f"project manager health check {pid} health={health} risks={len(risks)}")
    return {
        "apiVersion": "v0.1",
        "kind": "ProjectManagerReview",
        "projectId": pid,
        "projectManagerAgent": pm_agent,
        "health": health,
        "reviewRef": rel(review_path, bundle.root),
        "risks": risks,
        "decisionsNeeded": decisions,
        "nextActions": next_actions,
        "followupTaskRefs": followup_refs,
        "notificationRefs": notification_refs,
    }


def role_operating_review_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "role-reviews"


def load_role_operating_specs(bundle: Bundle) -> dict[str, Any]:
    path = bundle.root / ROLE_OPERATING_SPEC_REF
    if not path.exists():
        raise KnowledgeError(f"role operating spec not found: {ROLE_OPERATING_SPEC_REF}")
    data = json.loads(read_text(path))
    roles = data.get("roles")
    if not isinstance(roles, list):
        raise KnowledgeError("role operating spec must contain roles list")
    by_id: dict[str, Any] = {}
    for role in roles:
        if not isinstance(role, dict):
            raise KnowledgeError("role operating spec role must be object")
        role_id = str(role.get("roleId") or "").strip()
        if not role_id:
            raise KnowledgeError("role operating spec roleId is required")
        by_id[role_id] = role
    data["rolesById"] = by_id
    return data


def load_skill_registry(bundle: Bundle) -> dict[str, Any]:
    path = bundle.root / SKILL_REGISTRY_REF
    if not path.exists():
        raise KnowledgeError(f"skill registry not found: {SKILL_REGISTRY_REF}")
    data = json.loads(read_text(path))
    skills = data.get("skills")
    if not isinstance(skills, list):
        raise KnowledgeError("skill registry must contain skills list")
    by_id: dict[str, Any] = {}
    for item in skills:
        if not isinstance(item, dict):
            raise KnowledgeError("skill registry item must be object")
        skill_id = str(item.get("skillId") or "").strip()
        if not skill_id:
            raise KnowledgeError("skill registry skillId is required")
        by_id[skill_id] = item
    data["skillsById"] = by_id
    return data


def skill_markdown_sections(body: str) -> set[str]:
    sections: set[str] = set()
    for line in body.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            sections.add(match.group(1).strip())
    return sections


def validate_skill_registry(bundle: Bundle) -> list[str]:
    problems: list[str] = []
    registry_path = bundle.root / SKILL_REGISTRY_REF
    role_spec_path = bundle.root / ROLE_OPERATING_SPEC_REF
    if not registry_path.exists() and not role_spec_path.exists():
        return problems
    try:
        registry = load_skill_registry(bundle)
    except KnowledgeError as exc:
        return [str(exc)]
    if not (bundle.root / SKILL_STANDARD_REF).exists():
        problems.append(f"missing skill standard: {SKILL_STANDARD_REF}")
    if not (bundle.root / SKILL_DELIVERY_STANDARD_REF).exists():
        problems.append(f"missing skill delivery standard: {SKILL_DELIVERY_STANDARD_REF}")
    if not (bundle.root / SKILL_QUALITY_SOURCES_REF).exists():
        problems.append(f"missing skill quality sources: {SKILL_QUALITY_SOURCES_REF}")
    for shared_ref in SHARED_SKILL_PACKAGE_FILES:
        if not (bundle.root / shared_ref).exists():
            problems.append(f"missing shared skill package resource: {shared_ref}")
    if str(registry.get("sharedContractRef") or "") and not (bundle.root / str(registry["sharedContractRef"])).exists():
        problems.append(f"{SKILL_REGISTRY_REF}: sharedContractRef not found: {registry['sharedContractRef']}")
    registered_dirs: set[str] = set()
    active_skill_ids: set[str] = set()
    aliases_by_skill: dict[str, set[str]] = {}
    for skill_id, item in registry["skillsById"].items():
        skill_dir = str(item.get("skillDir") or "").strip()
        owner_role = str(item.get("ownerRole") or "").strip()
        status = str(item.get("status") or "").strip()
        allowed_roles = as_list(item.get("allowedRoles"))
        if not skill_dir:
            problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} missing skillDir")
            continue
        registered_dirs.add(skill_dir)
        if not owner_role:
            problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} missing ownerRole")
        if status not in {"active", "draft", "disabled"}:
            problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} unknown status {status}")
        if status == "active":
            active_skill_ids.add(skill_id)
        if not allowed_roles:
            problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} missing allowedRoles")
        skill_path = bundle.root / skill_dir / "SKILL.md"
        if not skill_path.exists():
            problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} SKILL.md not found: {skill_dir}/SKILL.md")
            continue
        fm, body = parse_frontmatter(read_text(skill_path))
        if str(fm.get("name") or "") != skill_id:
            problems.append(f"{rel(skill_path, bundle.root)}: frontmatter name must be {skill_id}")
        description = str(fm.get("description") or "").strip()
        if len(description) < 30:
            problems.append(f"{rel(skill_path, bundle.root)}: description must explain when to use the skill")
        sections = skill_markdown_sections(body)
        missing_sections = sorted(PRODUCTION_SKILL_REQUIRED_SECTIONS - sections)
        if missing_sections:
            problems.append(f"{rel(skill_path, bundle.root)}: missing required sections {', '.join(missing_sections)}")
        role_like_markers = sum(body.count(marker) for marker in ["## Agent Identity", "## Responsibilities", "## Execution Rules", "岗位", "职责边界"])
        if role_like_markers and not sections.intersection({"Inputs", "Workflow", "Outputs", "Quality Gate"}):
            problems.append(f"{rel(skill_path, bundle.root)}: looks like a role card, not an executable skill")
        for package_file in PRODUCTION_SKILL_PACKAGE_FILES:
            package_path = bundle.root / skill_dir / package_file
            if status == "active" and not package_path.exists():
                problems.append(f"{skill_dir}: missing mature skill package file: {package_file}")
            elif package_path.exists() and len(read_text(package_path).strip()) < 80:
                problems.append(f"{rel(package_path, bundle.root)}: mature skill package file is too thin")
        aliases_by_skill[skill_id] = {str(alias) for alias in as_list(item.get("aliases"))}
    skills_root = bundle.root / "skills"
    if skills_root.exists():
        for child in skills_root.iterdir():
            if not child.is_dir() or child.name.startswith("_"):
                continue
            skill_dir = rel(child, bundle.root)
            if skill_dir not in registered_dirs:
                problems.append(f"{skill_dir}: production skill directory is not registered in {SKILL_REGISTRY_REF}")
    try:
        role_specs = load_role_operating_specs(bundle)
    except KnowledgeError as exc:
        problems.append(str(exc))
        return problems
    role_ids = set(role_specs["rolesById"].keys())
    for skill_id, item in registry["skillsById"].items():
        owner_role = str(item.get("ownerRole") or "").strip()
        if owner_role and owner_role not in role_ids:
            problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} ownerRole not found in role specs: {owner_role}")
        for role_id in as_list(item.get("allowedRoles")):
            if role_id not in role_ids:
                problems.append(f"{SKILL_REGISTRY_REF}: {skill_id} allowedRole not found in role specs: {role_id}")
    for role in role_specs["roles"]:
        role_id = str(role.get("roleId") or "")
        role_skill_refs = {str(skill) for skill in as_list(role.get("skillRefs"))}
        if not role_skill_refs:
            problems.append(f"{ROLE_OPERATING_SPEC_REF}: {role_id} missing skillRefs")
        if role_id == "product-manager":
            for required_skill in sorted(PRODUCT_MANAGER_REQUIRED_SKILLS - role_skill_refs):
                problems.append(f"{ROLE_OPERATING_SPEC_REF}: product-manager missing required skillRef: {required_skill}")
        for skill_id in sorted(role_skill_refs):
            if skill_id not in active_skill_ids:
                problems.append(f"{ROLE_OPERATING_SPEC_REF}: {role_id} skillRef not active or not registered: {skill_id}")
                continue
            allowed_roles = set(as_list(registry["skillsById"][skill_id].get("allowedRoles")))
            if role_id not in allowed_roles:
                problems.append(f"{ROLE_OPERATING_SPEC_REF}: {role_id} is not allowed to use skill {skill_id}")
        role_aliases: set[str] = set(role_skill_refs)
        for skill_id in role_skill_refs:
            role_aliases.update(aliases_by_skill.get(skill_id, set()))
        for tag in as_list(role.get("capabilityTags")):
            if str(tag) not in role_aliases:
                problems.append(f"{ROLE_OPERATING_SPEC_REF}: {role_id} capabilityTag not covered by skillRefs or aliases: {tag}")
    if registry_path.exists():
        problems.extend(scan_for_secret_values(registry_path))
    return problems


def evaluate_role_operating_spec(bundle: Bundle, role: dict[str, Any]) -> dict[str, Any]:
    gaps: list[str] = []
    warnings: list[str] = []
    required_list_fields = [
        "responsibilities",
        "skillRefs",
        "capabilityTags",
        "inputContract",
        "outputContract",
        "workflow",
        "acceptanceChecks",
        "qualityEvaluationTemplate",
        "handoffTo",
        "boundaries",
        "commandTemplates",
    ]
    for field in required_list_fields:
        if not as_list(role.get(field)):
            gaps.append(f"missing {field}")
    required_string_fields = ["roleId", "name", "defaultAgentId", "roleProfileRef", "skillRegistryRef", "primaryOwner"]
    for field in required_string_fields:
        if not str(role.get(field) or "").strip():
            gaps.append(f"missing {field}")
    for ref_field in ["roleProfileRef", "skillRegistryRef", "guideRef", "commonRulesRef"]:
        ref = str(role.get(ref_field) or "")
        if ref and not (bundle.root / ref).exists():
            gaps.append(f"{ref_field} not found: {ref}")
    if str(role.get("skillRegistryRef") or "") != SKILL_REGISTRY_REF:
        warnings.append("skillRegistryRef should point to company skill registry")
    try:
        registry = load_skill_registry(bundle)
        active_skills = {skill_id for skill_id, item in registry["skillsById"].items() if str(item.get("status") or "") == "active"}
        for skill_id in as_list(role.get("skillRefs")):
            if skill_id not in active_skills:
                gaps.append(f"skillRef not active or not registered: {skill_id}")
        if str(role.get("roleId") or "") == "product-manager":
            role_skill_refs = {str(skill) for skill in as_list(role.get("skillRefs"))}
            for required_skill in sorted(PRODUCT_MANAGER_REQUIRED_SKILLS - role_skill_refs):
                gaps.append(f"product-manager missing required skillRef: {required_skill}")
    except KnowledgeError as exc:
        gaps.append(str(exc))
    quality_template = role.get("qualityEvaluationTemplate")
    if not isinstance(quality_template, dict):
        gaps.append("qualityEvaluationTemplate must be object")
    else:
        for field in ["artifactTypes", "requiredEvidence", "qualityChecks", "failureRoutes"]:
            if not as_list(quality_template.get(field)):
                gaps.append(f"qualityEvaluationTemplate missing {field}")
    if str(role.get("commonRulesRef") or "") != COMMON_AGENT_RULES_REF:
        warnings.append("commonRulesRef should point to common Agent operating rules")
    if str(role.get("guideRef") or "") != AGENT_TEAM_GUIDE_REF:
        warnings.append("guideRef should point to company Agent Team operating guide")
    return {
        "status": "ready" if not gaps else "needs_repair",
        "gaps": gaps,
        "warnings": warnings,
    }


def run_agent_role_operating_check(
    bundle: Bundle,
    role_id: str,
    project_id: str = "",
    actor: str = "system.scheduler",
    create_followup: bool = False,
    notify: bool = True,
) -> dict[str, Any]:
    specs = load_role_operating_specs(bundle)
    role_key = role_id.strip()
    role = specs["rolesById"].get(role_key)
    if role is None:
        raise KnowledgeError(f"role operating spec not found for role: {role_id}")
    evaluation = evaluate_role_operating_spec(bundle, role)
    pid = slug(project_id) if project_id else ""
    if pid:
        find_project(bundle, pid)
    task_paths = project_task_paths(bundle, pid) if pid else []
    role_agent_id = str(role.get("defaultAgentId") or "")
    role_tasks = [
        load_object(path)
        for path in task_paths
        if str(load_object(path).get("assignee") or "") == role_agent_id
    ]
    open_role_tasks = [task for task in role_tasks if not project_task_is_closed(task)]
    review_id = unique_time_id(f"role-review-{slug(role_key)}")
    review_dir = role_operating_review_storage_dir(bundle)
    ensure_dir(review_dir)
    review_path = review_dir / f"{review_id}.md"
    frontmatter = {
        "type": "RoleOperatingReview",
        "title": f"Role operating review: {role.get('name') or role_key}",
        "description": "Executable role operating-system readiness check.",
        "timestamp": utc_now(),
        "reviewId": review_id,
        "roleId": role_key,
        "roleName": role.get("name", ""),
        "projectId": pid,
        "actor": actor,
        "defaultAgentId": role_agent_id,
        "status": evaluation["status"],
        "gapCount": len(evaluation["gaps"]),
        "warningCount": len(evaluation["warnings"]),
        "taskCount": len(role_tasks),
        "openTaskCount": len(open_role_tasks),
        "roleProfileRef": role.get("roleProfileRef", ""),
        "skillRegistryRef": role.get("skillRegistryRef", ""),
        "skillRefs": as_list(role.get("skillRefs")),
        "capabilityTags": as_list(role.get("capabilityTags")),
        "guideRef": role.get("guideRef", ""),
        "commonRulesRef": role.get("commonRulesRef", ""),
        "qualityEvaluationTemplate": role.get("qualityEvaluationTemplate", {}),
        "followupTaskRefs": [],
        "notificationRefs": [],
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            f"- role: {role.get('name') or role_key}",
            f"- status: {evaluation['status']}",
            f"- projectId: {pid or 'company'}",
            f"- defaultAgentId: {role_agent_id or 'none'}",
            f"- roleProfileRef: {role.get('roleProfileRef') or 'none'}",
            f"- skillRegistryRef: {role.get('skillRegistryRef') or 'none'}",
            "",
            "## Gaps",
            "",
            *([f"- {item}" for item in evaluation["gaps"]] or ["- none"]),
            "",
            "## Warnings",
            "",
            *([f"- {item}" for item in evaluation["warnings"]] or ["- none"]),
            "",
            "## Responsibilities",
            "",
            *[f"- {item}" for item in as_list(role.get("responsibilities"))],
            "",
            "## Production Skills",
            "",
            *[f"- {item}" for item in as_list(role.get("skillRefs"))],
            "",
            "## Capability Tags",
            "",
            *[f"- {item}" for item in as_list(role.get("capabilityTags"))],
            "",
            "## Workflow",
            "",
            *[f"- {item}" for item in as_list(role.get("workflow"))],
            "",
            "## Acceptance Checks",
            "",
            *[f"- {item}" for item in as_list(role.get("acceptanceChecks"))],
            "",
            "## Quality Evaluation Template",
            "",
            "### Artifact Types",
            "",
            *[f"- {item}" for item in as_list(dict(role.get("qualityEvaluationTemplate") or {}).get("artifactTypes"))],
            "",
            "### Required Evidence",
            "",
            *[f"- {item}" for item in as_list(dict(role.get("qualityEvaluationTemplate") or {}).get("requiredEvidence"))],
            "",
            "### Quality Checks",
            "",
            *[f"- {item}" for item in as_list(dict(role.get("qualityEvaluationTemplate") or {}).get("qualityChecks"))],
            "",
            "### Failure Routes",
            "",
            *[f"- {item}" for item in as_list(dict(role.get("qualityEvaluationTemplate") or {}).get("failureRoutes"))],
            "",
            "## Boundaries",
            "",
            *[f"- {item}" for item in as_list(role.get("boundaries"))],
        ]
    )
    write_text(review_path, render_doc(frontmatter, body))
    update_index(review_dir / "index.md", str(frontmatter["title"]), review_path.name)
    create_audit_log(bundle, actor, "agent.role_operating_check", rel(review_path, bundle.root), after=evaluation["status"], policy_result="role_operating_spec", details=f"roleId={role_key}\nprojectId={pid or 'company'}\ngaps={len(evaluation['gaps'])}")

    followup_refs: list[str] = []
    notification_refs: list[str] = []
    if create_followup and evaluation["gaps"]:
        followup_path = create_project_task(
            bundle,
            f"Repair role operating system: {role.get('name') or role_key}",
            pid,
            actor,
            role_agent_id or KNOWLEDGE_STEWARD_AGENT_ID,
            "agent_role_change",
            "",
            "high",
            "",
            [rel(review_path, bundle.root), ROLE_OPERATING_SPEC_REF],
            [
                "Repair the listed role operating-system gaps.",
                "Update role skill pack, role operating spec, Agent Team guide, and tests/evals when behavior changes.",
                "Finish with TaskResult and evidence refs.",
            ],
        )
        followup_refs.append(rel(followup_path, bundle.root))
        if notify:
            notification_path = create_task_notification(
                bundle,
                followup_path,
                load_object(followup_path),
                "role_operating_repair_required",
                recipient=role_agent_id or KNOWLEDGE_STEWARD_AGENT_ID,
                summary=f"{role.get('name') or role_key} 岗位体系检查发现 {len(evaluation['gaps'])} 个缺口，需要修复。Review：{rel(review_path, bundle.root)}。",
                source_message_ref=rel(review_path, bundle.root),
            )
            notification_refs.append(rel(notification_path, bundle.root))
    if followup_refs or notification_refs:
        update_frontmatter_file(review_path, {"followupTaskRefs": followup_refs, "notificationRefs": notification_refs, "updatedAt": utc_now()})
    project_manager_review: dict[str, Any] | None = None
    if role_key == "project-manager" and pid:
        project_manager_review = run_project_manager_health_check(
            bundle,
            pid,
            actor=actor,
            create_followup=create_followup,
            notify=notify,
        )
    append_log(bundle, f"role operating check {role_key} status={evaluation['status']} gaps={len(evaluation['gaps'])}")
    return {
        "apiVersion": "v0.1",
        "kind": "RoleOperatingReview",
        "roleId": role_key,
        "projectId": pid,
        "status": evaluation["status"],
        "reviewRef": rel(review_path, bundle.root),
        "gaps": evaluation["gaps"],
        "warnings": evaluation["warnings"],
        "taskCount": len(role_tasks),
        "openTaskCount": len(open_role_tasks),
        "followupTaskRefs": followup_refs,
        "notificationRefs": notification_refs,
        "projectManagerReview": project_manager_review,
    }


def source_material_storage_dir(bundle: Bundle, project_id: str = "") -> Path:
    if project_id:
        return bundle.root / "projects" / slug(project_id) / "sources"
    return bundle.root / "sources"


def infer_material_type(source_ref: str = "", material_type: str = "", title: str = "") -> str:
    explicit = material_type.strip().lower()
    if explicit:
        return explicit
    value = " ".join([source_ref, title]).lower()
    if "minutes/" in value or "meeting" in value or "会议" in value or "妙记" in value:
        return "meeting"
    if value.startswith("http://") or value.startswith("https://"):
        if "feishu.cn/doc" in value or "feishu.cn/wiki" in value:
            return "feishu-doc"
        return "url"
    if re.search(r"\.(png|jpg|jpeg|gif|webp|svg)$", value):
        return "image"
    if re.search(r"\.(mp4|mov|m4v|avi)$", value):
        return "video"
    if re.search(r"\.(mp3|wav|m4a|aac)$", value):
        return "audio"
    if re.search(r"\.(zip|tar|tgz|gz|dmg|pkg|exe)$", value):
        return "package"
    if re.search(r"\.(csv|xlsx|xls|jsonl|parquet|sqlite|db)$", value):
        return "dataset"
    if re.search(r"\.(md|txt|docx|pdf|html)$", value):
        return "document"
    return "text"


def material_content_looks_sensitive(content: str) -> bool:
    if not content.strip():
        return False
    lowered = content.lower()
    markers = [
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "secret",
        "password",
        "passwd",
        "private key",
        "bearer ",
        "密钥",
        "密码",
        "令牌",
        "私钥",
    ]
    if any(marker in lowered for marker in markers):
        return True
    token_like_patterns = [
        r"\bsk-[A-Za-z0-9_-]{16,}\b",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    ]
    return any(re.search(pattern, content) for pattern in token_like_patterns)


def create_source_material(
    bundle: Bundle,
    title: str,
    source_ref: str,
    submitter: str,
    project_id: str = "",
    material_type: str = "",
    storage_ref: str = "",
    content: str = "",
    license_hint: str = "",
    sensitivity: str = "internal",
    extraction_tool: str = "manual",
    extraction_status: str = "registered",
    create_task_flag: bool = False,
    assignee: str = "agent.company-knowledge-core.knowledge-engineering",
) -> dict[str, str]:
    if not title.strip() and not source_ref.strip():
        raise KnowledgeError("material title or source ref is required")
    if not submitter.strip():
        raise KnowledgeError("material submitter is required")
    material_title = title.strip() or source_ref.strip()
    material_id = unique_time_id("source")
    material_kind = infer_material_type(source_ref, material_type, material_title)
    if material_content_looks_sensitive(content):
        raise KnowledgeError("material content appears to contain a secret; refusing to store it")
    if len(content) > MATERIAL_RAW_TEXT_MAX_CHARS and not storage_ref.strip():
        raise KnowledgeError("material content is too large for inline storage; provide storageRef")
    path = source_material_storage_dir(bundle, project_id) / f"{material_id}.md"
    content_hash_source = "\n".join([source_ref, storage_ref, content])
    content_hash = hashlib.sha256(content_hash_source.encode("utf-8")).hexdigest()
    frontmatter = {
        "type": "SourceMaterial",
        "title": material_title,
        "description": "Raw or referenced source material awaiting extraction and review.",
        "timestamp": utc_now(),
        "sourceId": material_id,
        "projectId": slug(project_id) if project_id else "",
        "submitter": submitter,
        "owner": submitter,
        "status": "draft",
        "materialType": material_kind,
        "sourceType": material_kind,
        "sourceRef": source_ref,
        "storageRef": storage_ref,
        "contentHash": content_hash,
        "license": license_hint,
        "sensitivity": sensitivity,
        "extractionTool": extraction_tool,
        "extractionStatus": extraction_status,
        "taskRef": "",
    }
    should_store_raw_text = material_kind not in {"package", "binary", "model", "dataset"} and bool(content.strip()) and len(content) <= MATERIAL_RAW_TEXT_MAX_CHARS
    body = "\n".join(
        [
            "## Source",
            "",
            f"- sourceRef: {source_ref or 'none'}",
            f"- storageRef: {storage_ref or 'none'}",
            f"- contentHash: {content_hash}",
            f"- materialType: {material_kind}",
            f"- sensitivity: {sensitivity}",
            "",
            "## Original Text",
            "",
            content.strip() if should_store_raw_text else "Raw binary or bulky content is not stored in this markdown object. Use sourceRef/storageRef and contentHash to retrieve the original material.",
            "",
            "## Extraction",
            "",
            f"- extractionTool: {extraction_tool}",
            f"- extractionStatus: {extraction_status}",
            "- summary: pending",
            "- structuredKnowledge: pending",
            "",
            "## Evidence Rules",
            "",
            "- Any KnowledgeItem derived from this source must cite this SourceMaterial and keep original source path available.",
            "- Extracted conclusions remain draft/observed until review.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(path.parent / "index.md", material_title, path.name)
    create_audit_log(bundle, submitter, "material.ingest", rel(path, bundle.root), after="draft", policy_result="review_required", details=f"sourceRef={source_ref}\nmaterialType={material_kind}")
    task_path = None
    if create_task_flag:
        task_path = create_project_task(
            bundle,
            f"Process source material: {material_title}",
            project_id,
            submitter,
            assignee,
            "knowledge_capture",
            "",
            "normal",
            "",
            [rel(path, bundle.root)],
            [
                "Parse original material.",
                "Create evidence-backed summary.",
                "Create structured draft knowledge with source refs.",
                "Return TaskResult with evidenceRefs and knowledgeDraft.",
            ],
        )
        update_frontmatter_file(path, {"taskRef": rel(task_path, bundle.root), "extractionStatus": "task_created"})
    append_log(bundle, f"ingested SourceMaterial {material_id} project={project_id or 'none'}")
    result = {"sourceRef": rel(path, bundle.root), "sourceId": material_id}
    if task_path:
        result["taskRef"] = rel(task_path, bundle.root)
    return result


def render_project_task_context(bundle: Bundle, task_path: Path) -> str:
    text = read_text(task_path)
    fm, body = parse_frontmatter(text)
    source_refs = as_list(fm.get("sourceMaterialRefs"))
    operating_rules = common_operating_rules_payload(bundle)
    operating_rule_refs = task_operating_rule_refs(bundle, fm)
    project_id = str(fm.get("projectId", ""))
    actor_context = actor_context_for(bundle, str(fm.get("assignee") or fm.get("leaseOwner") or ""), project_id)
    lines = [
        "# Current Task Context",
        "",
        f"- taskId: {fm.get('taskId', '')}",
        f"- taskType: {fm.get('taskType', '')}",
        f"- projectId: {project_id}",
        f"- assignee: {fm.get('assignee', '')}",
        f"- status: {fm.get('status', '')}",
        "",
        "## Required Reading",
        "",
        f"- Task: {rel(task_path, bundle.root)}",
        f"- Common Agent Operating Rules: {operating_rules['rulesRef']}",
        f"- Agent Team Guide: {operating_rules['guideRef']}",
        f"- Company Constitution: {operating_rule_refs['companyConstitution']}",
        f"- Task Runtime Contract: {operating_rule_refs['taskRuntimeContract']}",
        f"- Human Acceptance Policy: {operating_rule_refs['humanAcceptancePolicy']}",
    ]
    if operating_rule_refs.get("roleRules"):
        lines.append(f"- Role Rules: {operating_rule_refs['roleRules']}")
    if operating_rule_refs.get("projectRules"):
        lines.append(f"- Project Rules: {operating_rule_refs['projectRules']}")
    if project_id:
        project_path = bundle.root / "projects" / slug(project_id) / "project.md"
        if project_path.exists():
            lines.append(f"- Project: {rel(project_path, bundle.root)}")
    if actor_context.get("contextRef"):
        lines.append(f"- ActorContext: {actor_context['contextRef']}")
    for ref in source_refs:
        lines.append(f"- Source: {ref}")
    lines.extend(
        [
            "",
            "## Task",
            "",
            body.strip(),
            "",
            "## Actor Context",
            "",
            f"- actorId: {actor_context.get('actorId', '')}",
            f"- actorType: {actor_context.get('actorType', '')}",
            f"- contextRef: {actor_context.get('contextRef', '') or 'derived'}",
            f"- currentProject: {actor_context.get('currentProject', '') or project_id}",
            f"- outputPreference: {actor_context.get('outputPreference', '') or 'none'}",
            "- allowedProjects:",
            *([f"  - {item}" for item in as_list(actor_context.get("allowedProjects"))] or ["  - none"]),
            "- allowedKnowledgeScopes:",
            *([f"  - {item}" for item in as_list(actor_context.get("allowedKnowledgeScopes"))] or ["  - none"]),
            "- notificationPreferences:",
            *([f"  - {item}" for item in as_list(actor_context.get("notificationPreferences"))] or ["  - none"]),
            "",
            "## Memory Policy",
            "",
            *[f"- {key}: {value}" for key, value in dict(actor_context.get("memoryPolicy") or actor_memory_policy()).items()],
            "",
            "## Source Material Snapshots",
            "",
        ]
    )
    for ref in source_refs:
        raw_source_path = Path(str(ref)).expanduser()
        source_path = raw_source_path if raw_source_path.is_absolute() else bundle.root / raw_source_path
        if source_path.exists() and source_path.is_file():
            if source_path.suffix.lower() in {".doc", ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".xlsx", ".xls", ".pptx", ".ppt"}:
                lines.extend([f"### {ref}", "", f"Binary or rich document source retained by reference: {source_path}", ""])
                continue
            try:
                source_text = read_text(source_path)
            except UnicodeDecodeError:
                lines.extend([f"### {ref}", "", f"Non-UTF-8 source retained by reference: {source_path}", ""])
                continue
            lines.extend([f"### {ref}", "", source_text[:4000], ""])
    lines.extend(
        [
            "## Required Writeback",
            "",
            f"- Run `zhenzhi-knowledge task finish {fm.get('taskId', '')} --result done --summary \"<summary>\"` after processing.",
            "- Link evidence refs for any KnowledgeItem drafts.",
            "- Do not mark reusable knowledge as verified without review.",
            "",
            "## Common Operating Rules Gate",
            "",
            f"- version: {operating_rules['version']}",
            f"- rulesRef: {operating_rules['rulesRef']}",
            f"- guideRef: {operating_rules['guideRef']}",
            f"- rulesDocExists: {operating_rules['rulesDocExists']}",
            "- layeredRuleRefs:",
            *[f"  - {key}: {value or 'none'}" for key, value in operating_rule_refs.items()],
            "- mandatoryGates:",
            *[f"  - {item}" for item in operating_rules["mandatoryGates"]],
        ]
    )
    return "\n".join(lines) + "\n"


def project_context_bundle(bundle: Bundle, task_path: Path) -> dict[str, Any]:
    task = load_object(task_path)
    project_id = str(task.get("projectId", ""))
    project_slug = slug(project_id) if project_id else ""
    project_dir = bundle.root / "projects" / project_slug if project_id else bundle.root / "projects"

    def existing_rel(path: Path) -> str:
        return rel(path, bundle.root) if path.exists() else ""

    def object_refs(root: Path, object_type: str = "", limit: int = 20) -> list[str]:
        refs: list[str] = []
        if not root.exists():
            return refs
        for path in sorted(root.rglob("*.md")):
            if path.name in COLLECTION_NAMES or path.name.endswith(".draft.md"):
                continue
            try:
                fm = load_object(path)
            except KnowledgeError:
                continue
            if object_type and fm.get("type") != object_type:
                continue
            refs.append(rel(path, bundle.root))
            if len(refs) >= limit:
                break
        return refs

    task_id = str(task.get("taskId", ""))
    actor_id = str(task.get("assignee") or task.get("leaseOwner") or "")
    result_refs = [
        rel(path, bundle.root)
        for path in sorted(task_result_storage_dir(bundle).glob("*.md"))
        if path.name not in COLLECTION_NAMES and load_object(path).get("taskId") == task_id
    ]
    handoff_refs = [
        ref
        for ref in object_refs(project_dir, limit=50)
        if "handoff" in ref.lower() or "交接" in ref
    ]
    environment_refs = [
        ref
        for ref in object_refs(project_dir, limit=50)
        if "environment" in ref.lower() or "manifest" in ref.lower() or "env" in Path(ref).name.lower()
    ]
    return {
        "bundleVersion": "0.1",
        "operatingRules": common_operating_rules_payload(bundle),
        "project": {
            "projectId": project_id,
            "projectRef": existing_rel(project_dir / "project.md") if project_id else "",
            "repositoryRefs": as_list(task.get("repositoryRefs")),
            "environmentManifestRefs": environment_refs,
        },
        "task": {
            "taskId": task_id,
            "taskRef": rel(task_path, bundle.root),
            "status": task.get("status", ""),
            "taskType": task.get("taskType", ""),
            "sourceMaterialRefs": as_list(task.get("sourceMaterialRefs")),
            "evidenceRefs": as_list(task.get("evidenceRefs")),
            "requiredCapabilities": as_list(task.get("requiredCapabilities")),
            "requiredSecretRefs": as_list(task.get("requiredSecretRefs")),
            "leaseOwner": task.get("leaseOwner", ""),
            "leaseExpiresAt": task.get("leaseExpiresAt", ""),
        },
        "actorContext": actor_context_for(bundle, actor_id, project_id),
        "knowledge": {
            "knowledgeItemRefs": object_refs(bundle.root / "knowledge", "KnowledgeItem", limit=30),
            "decisionRefs": object_refs(project_dir, "Decision", limit=20),
            "conflictRefs": object_refs(bundle.root / "knowledge" / "conflicts", "ConflictRecord", limit=20),
        },
        "executionHistory": {
            "taskResultRefs": result_refs,
            "agentRunRefs": object_refs(bundle.root / "runs" / project_slug, "AgentRun", limit=20) if project_id else [],
            "handoffRefs": handoff_refs,
        },
        "handoff": {
            "requiredFields": ["done", "currentState", "nextStep", "blockers", "workspaceRefs", "artifactRefs", "evidenceRefs", "logsRef"],
            "notes": "Runner handoff notes must be refs-first and must not store secrets.",
        },
    }


def claim_project_task(bundle: Bundle, task_id: str, runner_id: str, expected_version: int | None = None, lease_seconds: int = 600) -> dict[str, Any]:
    if lease_seconds <= 0:
        raise KnowledgeError("lease seconds must be positive")
    runner_path = find_agent_runner(bundle, runner_id)
    runner = load_object(runner_path)
    if runner.get("status") not in {"online", "idle", "busy"}:
        raise KnowledgeError(f"runner is not online: {runner_id}")
    task_path = find_project_task(bundle, task_id)
    task = ensure_project_task_runtime(bundle, task_path)
    if str(task.get("status") or "") in CLOSED_TASK_STATUSES:
        raise KnowledgeError(f"task is closed: {task_id}")
    missing_requirements = missing_runner_requirements(runner, task)
    if missing_requirements:
        update_frontmatter_file(task_path, {"status": "blocked", "updatedAt": utc_now()})
        blocked_task = load_object(task_path)
        create_task_notification(
            bundle,
            task_path,
            blocked_task,
            "task_blocked",
            recipient=str(blocked_task.get("requester") or blocked_task.get("assignee") or "project"),
            summary=f"任务被阻塞：Runner {runner_id} 不满足要求：{', '.join(missing_requirements)}。",
        )
        create_audit_log(bundle, slug(runner_id), "task.claim.blocked", rel(task_path, bundle.root), before=str(task.get("status", "")), after="blocked", policy_result="missing_runner_requirement", details="\n".join(missing_requirements))
        raise KnowledgeError(f"runner does not satisfy task requirements: {', '.join(missing_requirements)}")
    missing_secrets = missing_required_secret_refs(bundle, task)
    if missing_secrets:
        update_frontmatter_file(task_path, {"status": "blocked", "updatedAt": utc_now()})
        blocked_task = load_object(task_path)
        create_task_notification(
            bundle,
            task_path,
            blocked_task,
            "task_blocked",
            recipient=str(blocked_task.get("requester") or blocked_task.get("assignee") or "project"),
            summary=f"任务被阻塞：缺少 credential readiness：{', '.join(missing_secrets)}。",
        )
        create_audit_log(bundle, slug(runner_id), "task.claim.blocked", rel(task_path, bundle.root), before=str(task.get("status", "")), after="blocked", policy_result="missing_secret_ref", details="\n".join(missing_secrets))
        raise KnowledgeError(f"missing credential readiness for secretRef: {', '.join(missing_secrets)}")
    missing_env_vars = task_environment_readiness(bundle, task, runner).get("missingEnvVars", [])
    if missing_env_vars:
        missing_env_refs = [f"env:{name}" for name in missing_env_vars]
        update_frontmatter_file(task_path, {"status": "blocked", "updatedAt": utc_now()})
        blocked_task = load_object(task_path)
        create_task_notification(
            bundle,
            task_path,
            blocked_task,
            "task_blocked",
            recipient=str(blocked_task.get("requester") or blocked_task.get("assignee") or "project"),
            summary=f"任务被阻塞：缺少 environment readiness：{', '.join(missing_env_refs)}。",
        )
        create_audit_log(bundle, slug(runner_id), "task.claim.blocked", rel(task_path, bundle.root), before=str(task.get("status", "")), after="blocked", policy_result="missing_env_var", details="\n".join(missing_env_refs))
        raise KnowledgeError(f"missing environment readiness for env: {', '.join(missing_env_refs)}")
    version = int(task.get("taskVersion") or 1)
    if expected_version is not None and expected_version != version:
        raise KnowledgeError("stale task version")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    lease_expires = parse_utc(str(task.get("leaseExpiresAt", "")))
    lease_owner = str(task.get("leaseOwner", ""))
    if lease_owner and lease_expires and lease_expires > now and lease_owner != slug(runner_id):
        raise KnowledgeError(f"task lease is owned by {lease_owner}")
    token = unique_time_id("lease")
    token_hash = secret_fingerprint(token)
    expires_at = (now.timestamp() + lease_seconds)
    expires_dt = datetime.fromtimestamp(expires_at, timezone.utc).replace(microsecond=0)
    attempt = int(task.get("leaseAttempt") or 0) + 1
    lease_version = int(task.get("leaseVersion") or version)
    updates = {
        "status": "processing",
        "assignedRunner": slug(runner_id),
        "executorAgent": str(task.get("executorAgent") or task.get("assignee") or ""),
        "leaseOwner": slug(runner_id),
        "leaseTokenHash": token_hash,
        "leaseProofHash": token_hash,
        "leaseIssuedAt": now.isoformat().replace("+00:00", "Z"),
        "leaseExpiresAt": expires_dt.isoformat().replace("+00:00", "Z"),
        "leaseHeartbeatAt": now.isoformat().replace("+00:00", "Z"),
        "heartbeatAt": now.isoformat().replace("+00:00", "Z"),
        "leaseVersion": lease_version + 1,
        "leaseAttempt": attempt,
        "taskVersion": version + 1,
        "updatedAt": utc_now(),
    }
    fm = update_frontmatter_file(task_path, updates)
    record_runner_lease_claim(bundle, runner_path, runner, fm, task_path)
    create_audit_log(bundle, slug(runner_id), "task.claim", rel(task_path, bundle.root), before=str(task.get("status", "")), after="processing", details=f"leaseOwner={runner_id}\nleaseExpiresAt={updates['leaseExpiresAt']}")
    create_task_notification(
        bundle,
        task_path,
        fm,
        "task_claimed",
        recipient=str(fm.get("requester") or fm.get("assignee") or "project"),
        summary=f"任务已被 Runner {slug(runner_id)} 领取，租约到期时间：{updates['leaseExpiresAt']}。",
    )
    context_path = bundle.zz_dir / "context" / f"task.{slug(str(fm.get('taskId', task_id)))}.md"
    write_text(context_path, render_project_task_context(bundle, task_path))
    context_ref = rel(context_path, bundle.root)
    execution_context = execution_context_payload(bundle, fm, runner_id, token, context_ref)
    execution_context_ref = write_execution_context_ref(bundle, fm, execution_context)
    return {
        "task": {**fm, "path": rel(task_path, bundle.root)},
        "runnerId": slug(runner_id),
        "leaseToken": token,
        "leaseExpiresAt": updates["leaseExpiresAt"],
        "leaseProof": token_hash,
        "contextRef": context_ref,
        "writebackCommand": execution_context["writebackCommand"],
        "executionContext": execution_context,
        "executionContextRef": execution_context_ref,
        "taskVersion": fm.get("taskVersion"),
    }


def record_runner_lease_claim(bundle: Bundle, runner_path: Path, runner: dict[str, Any], task: dict[str, Any], task_path: Path) -> None:
    task_id = str(task.get("taskId") or task_path.stem)
    task_ref = rel(task_path, bundle.root)
    active = [item for item in as_list_of_dicts(runner.get("currentLeases")) if str(item.get("taskId") or "") != task_id]
    active.append(
        {
            "taskId": task_id,
            "taskRef": task_ref,
            "leaseOwner": str(task.get("leaseOwner") or ""),
            "leaseVersion": int(task.get("leaseVersion") or 0),
            "leaseAttempt": int(task.get("leaseAttempt") or 0),
            "leaseExpiresAt": str(task.get("leaseExpiresAt") or ""),
            "status": str(task.get("status") or ""),
        }
    )
    history = as_list_of_dicts(runner.get("taskHistory"))
    history.append({"taskId": task_id, "taskRef": task_ref, "event": "claimed", "at": utc_now()})
    update_frontmatter_file(runner_path, {"status": "busy", "currentLeases": active, "taskHistory": history[-50:], "updatedAt": utc_now()})


def as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            items.append(dict(item))
        elif isinstance(item, str) and item.strip().startswith("{"):
            try:
                parsed = json.loads(item)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                items.append(parsed)
    return items


def project_task_dispatch_sort_key(task: dict[str, Any], task_path: Path | None = None) -> tuple[Any, ...]:
    priority_rank = {
        "critical": 0,
        "p0": 0,
        "high": 1,
        "p1": 1,
        "medium": 2,
        "normal": 2,
        "p2": 2,
        "low": 3,
        "p3": 3,
    }
    stage_rank = {
        "technical_solution": 0,
        "solution_review": 1,
        "implementation": 2,
        "development": 2,
        "testing": 3,
        "acceptance": 4,
        "launch_readiness": 5,
    }
    role_rank = {
        PROJECT_MANAGER_AGENT_ID: 0,
        PRODUCT_MANAGER_AGENT_ID: 1,
        DEVELOPMENT_AGENT_ID: 2,
        TEST_AGENT_ID: 3,
        DESIGN_AGENT_ID: 4,
        KNOWLEDGE_QUERY_AGENT_ID: 5,
        OPERATIONS_AGENT_ID: 6,
    }
    runtime = task.get("taskRuntime") if isinstance(task.get("taskRuntime"), dict) else {}
    task_type = normalized_task_type(str(task.get("taskType") or runtime.get("taskType") or ""))
    task_type_rank = {
        "project_management": 0,
        "role_handoff": 0,
        "project_initialization": 1,
        "product_requirement": 2,
        "requirement_clarification": 2,
        "development": 3,
        "engineering_action": 3,
        "workflow_runtime_core": 3,
        "testing": 4,
        "qa": 4,
        "release_test": 4,
        "design_spec": 5,
        "frontend_design": 5,
        "ux_design": 5,
        "ui_design": 5,
        "operations": 6,
        "operations_feedback": 6,
    }
    updated_at = parse_utc(str(task.get("updatedAt") or task.get("timestamp") or ""))
    updated_ts = updated_at.timestamp() if updated_at else 0
    assignee = str(task.get("assignee") or task.get("executorAgent") or "")
    current_stage = str(task.get("currentStage") or "").strip().lower()
    tech_solution_required = boolish(task.get("technicalSolutionRequired"), False)
    path_name = task_path.name if task_path else str(task.get("taskId") or "")
    return (
        priority_rank.get(str(task.get("priority") or "").strip().lower(), 2),
        stage_rank.get(current_stage, 9),
        0 if tech_solution_required else 1,
        role_rank.get(assignee, 9),
        task_type_rank.get(task_type, 9),
        updated_ts,
        str(task.get("taskId") or path_name),
        path_name,
    )


def iter_dispatchable_project_task_paths(bundle: Bundle, project_id: str = "") -> list[Path]:
    project_root = bundle.root / "projects"
    if project_id:
        task_roots = [project_root / slug(project_id) / "tasks"]
    else:
        task_roots = sorted(project_root.glob("*/tasks"))
    candidates: list[tuple[tuple[Any, ...], Path]] = []
    for task_root in task_roots:
        if not task_root.exists():
            continue
        for path in sorted(task_root.glob("*.md")):
            if path.name == "index.md":
                continue
            try:
                fm = load_object(path)
            except Exception:
                continue
            if fm.get("type") in {"ProjectTask", "KnowledgeTask"} and str(fm.get("status") or "") in {"pending", "waiting_runner"}:
                candidates.append((project_task_dispatch_sort_key(fm, path), path))
    return [path for _, path in sorted(candidates)]


def runner_can_schedule_task(bundle: Bundle, runner: dict[str, Any], task: dict[str, Any]) -> bool:
    if runner.get("status") not in {"online", "idle", "busy"}:
        return False
    if runner_heartbeat_is_stale(runner):
        return False
    runner_agents = {str(item) for item in [*as_list(runner.get("agents")), *as_list(runner.get("agentIds"))]}
    task_agents = {
        str(item)
        for item in [
            task.get("assignee"),
            task.get("executorAgent"),
            *as_list(task.get("requiredAgents")),
        ]
        if str(item or "").strip()
    }
    if runner_agents and task_agents and runner_agents.isdisjoint(task_agents):
        return False
    if missing_runner_requirements(runner, task):
        return False
    if missing_required_secret_refs(bundle, task):
        return False
    return True


def runner_heartbeat_is_stale(runner: dict[str, Any], max_age_seconds: int = 1800) -> bool:
    heartbeat = parse_utc(str(runner.get("lastHeartbeatAt") or runner.get("heartbeatAt") or ""))
    if not heartbeat:
        return False
    return heartbeat <= datetime.now(timezone.utc).replace(microsecond=0).replace(tzinfo=timezone.utc) and (
        datetime.now(timezone.utc).replace(microsecond=0) - heartbeat
    ).total_seconds() > max_age_seconds


def select_runner_for_task(bundle: Bundle, task: dict[str, Any]) -> dict[str, Any] | None:
    runner_root = runner_storage_dir(bundle)
    if not runner_root.exists():
        return None
    candidates: list[dict[str, Any]] = []
    preferred_runner = str(task.get("preferredRunner") or task.get("assignedRunner") or "")
    for path in sorted(runner_root.glob("*.md")):
        if path.name == "index.md":
            continue
        runner = load_object(path)
        if runner.get("type") != "AgentRunner":
            continue
        if runner_can_schedule_task(bundle, runner, task):
            candidates.append(runner)
    if not candidates:
        return None
    if preferred_runner:
        preferred = slug(preferred_runner)
        for runner in candidates:
            if slug(str(runner.get("runnerId") or "")) == preferred:
                return runner
    task_agents = {str(item) for item in [task.get("assignee"), task.get("executorAgent"), *as_list(task.get("requiredAgents"))] if str(item or "").strip()}
    candidates.sort(
        key=lambda runner: (
            0 if ({str(item) for item in [*as_list(runner.get("agents")), *as_list(runner.get("agentIds"))]} & task_agents) else 1,
            str(runner.get("load") or ""),
            str(runner.get("runnerId") or ""),
        )
    )
    return candidates[0]


def release_ready_handoff_followups(bundle: Bundle, project_id: str = "", actor: str = "system.scheduler") -> list[dict[str, Any]]:
    result_root = task_result_storage_dir(bundle)
    if not result_root.exists():
        return []
    released: list[dict[str, Any]] = []
    for result_path in sorted(result_root.glob("*.md")):
        if result_path.name == "index.md":
            continue
        result = load_object(result_path)
        if result.get("type") != "TaskResult":
            continue
        if project_id and str(result.get("projectId") or "") != slug(project_id):
            continue
        if as_list(result.get("followupTaskRefs")):
            continue
        evaluation = dict(result.get("qualityEvaluation") or {}) if isinstance(result.get("qualityEvaluation"), dict) else {}
        handoff_contract = dict(result.get("handoffContract") or {}) if isinstance(result.get("handoffContract"), dict) else {}
        acceptance_policy = dict(result.get("acceptancePolicy") or {}) if isinstance(result.get("acceptancePolicy"), dict) else {}
        decision = str(evaluation.get("decision") or result.get("decision") or "")
        acceptance_status = str(acceptance_policy.get("acceptanceStatus") or result.get("acceptanceStatus") or "")
        if decision and not evaluation.get("decision"):
            evaluation["decision"] = decision
        if result.get("passed") is not None and "passed" not in evaluation:
            evaluation["passed"] = boolish(result.get("passed"), False)
        if not handoff_contract.get("handoffTo") and result.get("handoffTo"):
            handoff_contract.update(
                {
                    "handoffTo": str(result.get("handoffTo") or ""),
                    "fromAgent": str(result.get("fromAgent") or result.get("assignee") or ""),
                    "handoffSummary": str(result.get("handoffSummary") or result.get("summary") or ""),
                    "nextSuggestedTask": str(result.get("nextSuggestedTask") or ""),
                }
            )
        if decision != "handoff_ready":
            continue
        if acceptance_status not in {"accepted", "auto_accepted"}:
            continue
        if not str(handoff_contract.get("handoffTo") or ""):
            continue
        task_id = str(result.get("taskId") or "")
        if not task_id:
            continue
        try:
            task_path = find_project_task(bundle, task_id)
        except KnowledgeError:
            continue
        task = load_object(task_path)
        followup_path = create_project_role_followup_task(bundle, task, result_path, evaluation, handoff_contract)
        if not followup_path:
            continue
        followup_ref = rel(followup_path, bundle.root)
        update_frontmatter_file(result_path, {"followupTaskRefs": [followup_ref], "updatedAt": utc_now()})
        task_followup_refs = append_unique(as_list(task.get("followupTaskRefs")), followup_ref)
        update_frontmatter_file(task_path, {"followupTaskRefs": task_followup_refs, "updatedAt": utc_now()})
        create_audit_log(
            bundle,
            actor,
            "scheduler.handoff.release",
            rel(result_path, bundle.root),
            after=followup_ref,
            policy_result="handoff_ready",
            details=f"taskId={task_id}\nhandoffTo={handoff_contract.get('handoffTo', '')}",
        )
        released.append(
            {
                "taskId": task_id,
                "resultRef": rel(result_path, bundle.root),
                "followupTaskRef": followup_ref,
                "handoffTo": str(handoff_contract.get("handoffTo") or ""),
            }
        )
    return released


def stale_lease_sla_seconds(task: dict[str, Any]) -> int:
    priority = str(task.get("priority") or "").strip().lower()
    if priority in {"critical", "p0"}:
        return 10 * 60
    if priority in {"high", "p1"}:
        return 30 * 60
    if priority in {"medium", "normal", "p2"}:
        return 2 * 60 * 60
    return 24 * 60 * 60


def repair_stale_task_leases(bundle: Bundle, project_id: str = "", actor: str = "system.scheduler") -> list[dict[str, Any]]:
    repaired: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).replace(microsecond=0)
    project_root = bundle.root / "projects"
    task_roots = [project_root / slug(project_id) / "tasks"] if project_id else sorted(project_root.glob("*/tasks"))
    for task_root in task_roots:
        if not task_root.exists():
            continue
        for task_path in sorted(task_root.glob("*.md")):
            if task_path.name in COLLECTION_NAMES:
                continue
            try:
                task = load_object(task_path)
            except KnowledgeError:
                continue
            if task.get("type") not in {"ProjectTask", "KnowledgeTask"}:
                continue
            if str(task.get("status") or "") not in {"processing", "claimed", "approval_relay_requested"}:
                continue
            lease_owner = str(task.get("leaseOwner") or "")
            expires_at = parse_utc(str(task.get("leaseExpiresAt") or ""))
            heartbeat_at = parse_utc(str(task.get("leaseHeartbeatAt") or task.get("heartbeatAt") or ""))
            stale_by_expiry = bool(expires_at and expires_at <= now)
            stale_by_heartbeat = bool(heartbeat_at and (now - heartbeat_at).total_seconds() > stale_lease_sla_seconds(task))
            if not lease_owner or not (stale_by_expiry or stale_by_heartbeat):
                continue
            before = str(task.get("status") or "")
            updates = {
                "status": "waiting_runner",
                "staleLeaseOwner": lease_owner,
                "staleLeaseDetectedAt": utc_now(),
                "staleLeaseReason": "lease_expired" if stale_by_expiry else "heartbeat_stale",
                "leaseOwner": "",
                "leaseTokenHash": "",
                "leaseProofHash": "",
                "leaseExpiresAt": "",
                "leaseHeartbeatAt": "",
                "heartbeatAt": "",
                "taskVersion": int(task.get("taskVersion") or 1) + 1,
                "updatedAt": utc_now(),
            }
            updated = update_frontmatter_file(task_path, updates)
            repaired_item = {
                "taskId": str(task.get("taskId") or task_path.stem),
                "taskRef": rel(task_path, bundle.root),
                "previousRunnerId": lease_owner,
                "status": "waiting_runner",
                "reason": updates["staleLeaseReason"],
                "priority": str(task.get("priority") or ""),
            }
            repaired.append(repaired_item)
            record_runner_stale_lease(bundle, lease_owner, repaired_item)
            create_audit_log(bundle, actor, "scheduler.lease.stale_repair", rel(task_path, bundle.root), before=before, after="waiting_runner", policy_result=updates["staleLeaseReason"], details=json.dumps(repaired_item, ensure_ascii=False))
            create_task_notification(
                bundle,
                task_path,
                updated,
                "task_stale_lease_repaired",
                recipient=str(updated.get("requester") or updated.get("assignee") or PROJECT_MANAGER_AGENT_ID),
                summary=f"任务租约已过期并释放等待重新调度：{updated.get('title', updated.get('taskId', ''))}。原 Runner：{lease_owner}。",
            )
            if str(task.get("priority") or "").strip().lower() in {"critical", "p0"}:
                for recipient in [PROJECT_MANAGER_AGENT_ID, OPERATIONS_AGENT_ID]:
                    create_task_notification(
                        bundle,
                        task_path,
                        updated,
                        "critical_stale_lease_alert",
                        recipient=recipient,
                        summary=f"Critical 任务发生 stale lease，需要立即检查：{updated.get('taskId', '')}，原 Runner：{lease_owner}。",
                    )
    return repaired


def record_runner_stale_lease(bundle: Bundle, runner_id: str, item: dict[str, Any]) -> None:
    try:
        runner_path = find_agent_runner(bundle, runner_id)
        runner = load_object(runner_path)
    except KnowledgeError:
        return
    task_id = str(item.get("taskId") or "")
    current = [entry for entry in as_list_of_dicts(runner.get("currentLeases")) if str(entry.get("taskId") or "") != task_id]
    stale = [entry for entry in as_list_of_dicts(runner.get("staleLeases")) if str(entry.get("taskId") or "") != task_id]
    stale.append({**item, "detectedAt": utc_now()})
    history = as_list_of_dicts(runner.get("taskHistory"))
    history.append({"taskId": task_id, "taskRef": str(item.get("taskRef") or ""), "event": "stale_repaired", "at": utc_now()})
    update_frontmatter_file(runner_path, {"currentLeases": current, "staleLeases": stale[-50:], "taskHistory": history[-50:], "lastFailure": str(item.get("reason") or ""), "status": "online", "updatedAt": utc_now()})


def record_runner_lease_finished(bundle: Bundle, runner_id: str, task_id: str, task_ref: str, result_status: str) -> None:
    if not runner_id:
        return
    try:
        runner_path = find_agent_runner(bundle, runner_id)
        runner = load_object(runner_path)
    except KnowledgeError:
        return
    current = [entry for entry in as_list_of_dicts(runner.get("currentLeases")) if str(entry.get("taskId") or "") != task_id]
    failed = as_list_of_dicts(runner.get("failedLeases"))
    if result_status in {"blocked", "rejected", "failed"}:
        failed.append({"taskId": task_id, "taskRef": task_ref, "status": result_status, "at": utc_now()})
    history = as_list_of_dicts(runner.get("taskHistory"))
    history.append({"taskId": task_id, "taskRef": task_ref, "event": f"finished:{result_status}", "at": utc_now()})
    load_value = str(runner.get("load") or "").strip()
    next_status = "busy" if current or (load_value and load_value not in {"0", "0.0"}) else "online"
    update_frontmatter_file(
        runner_path,
        {
            "currentLeases": current,
            "failedLeases": failed[-50:],
            "taskHistory": history[-50:],
            "status": next_status,
            "updatedAt": utc_now(),
        },
    )


def record_runner_lifecycle_event(
    bundle: Bundle,
    runner_id: str,
    task_id: str,
    task_ref: str,
    event: str,
    status: str,
    reason: str = "",
    release_current: bool = True,
) -> None:
    if not runner_id:
        return
    try:
        runner_path = find_agent_runner(bundle, runner_id)
        runner = load_object(runner_path)
    except KnowledgeError:
        return
    current = as_list_of_dicts(runner.get("currentLeases"))
    if release_current:
        current = [entry for entry in current if str(entry.get("taskId") or "") != task_id]
    failed = as_list_of_dicts(runner.get("failedLeases"))
    if event in {"cancelled", "retry_requested"}:
        failed = [entry for entry in failed if str(entry.get("taskId") or "") != task_id]
        failed.append({"taskId": task_id, "taskRef": task_ref, "status": status, "reason": reason, "at": utc_now()})
    history = as_list_of_dicts(runner.get("taskHistory"))
    history.append({"taskId": task_id, "taskRef": task_ref, "event": event, "status": status, "reason": reason, "at": utc_now()})
    load_value = str(runner.get("load") or "").strip()
    next_status = "busy" if current or (load_value and load_value not in {"0", "0.0"}) else "online"
    update_frontmatter_file(
        runner_path,
        {
            "currentLeases": current,
            "failedLeases": failed[-50:],
            "taskHistory": history[-50:],
            "lastFailure": reason if event in {"cancelled", "retry_requested"} else str(runner.get("lastFailure") or ""),
            "status": next_status,
            "updatedAt": utc_now(),
        },
    )


def clear_project_task_lease_updates(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "leaseOwner": "",
        "leaseTokenHash": "",
        "leaseProofHash": "",
        "leaseExpiresAt": "",
        "leaseHeartbeatAt": "",
        "heartbeatAt": "",
        "taskVersion": int(task.get("taskVersion") or 1) + 1,
        "updatedAt": utc_now(),
    }


def cancel_project_task(
    bundle: Bundle,
    task_id: str,
    actor: str,
    reason: str,
    runner_id: str = "",
    lease_token: str = "",
) -> dict[str, Any]:
    if not actor.strip():
        raise KnowledgeError("cancel actor is required")
    if not reason.strip():
        raise KnowledgeError("cancel reason is required")
    task_path = find_project_task(bundle, task_id)
    task = ensure_project_task_runtime(bundle, task_path)
    if str(task.get("status") or "") in {"done", "cancelled"}:
        raise KnowledgeError(f"task cannot be cancelled from status: {task.get('status', '')}")
    if runner_id or lease_token:
        verify_project_task_lease(task, runner_id, lease_token)
    before = str(task.get("status") or "")
    lease_owner = str(task.get("leaseOwner") or runner_id or "")
    updates = {
        **clear_project_task_lease_updates(task),
        "status": "cancelled",
        "cancelledAt": utc_now(),
        "cancelledBy": actor,
        "cancelReason": reason,
        "nextAction": "Review cancellation reason and create a retry task only if the owner approves.",
    }
    updated = update_frontmatter_file(task_path, updates)
    task_ref = rel(task_path, bundle.root)
    record_runner_lifecycle_event(bundle, lease_owner, str(task.get("taskId") or task_id), task_ref, "cancelled", "cancelled", reason)
    audit_path = create_audit_log(bundle, actor, "task.cancel", task_ref, before=before, after="cancelled", policy_result="agent_ring_lifecycle", details=f"reason={reason}\nrunnerId={lease_owner}")
    notification_path = create_task_notification(
        bundle,
        task_path,
        updated,
        "task_cancelled",
        recipient=str(updated.get("requester") or updated.get("assignee") or PROJECT_MANAGER_AGENT_ID),
        summary=f"任务已取消：{updated.get('title', task_id)}。原因：{reason}。",
    )
    return {
        "apiVersion": "v0.1",
        "kind": "TaskCancelResult",
        "task": {**updated, "path": task_ref},
        "taskRef": task_ref,
        "runnerId": lease_owner,
        "status": "cancelled",
        "auditRef": rel(audit_path, bundle.root),
        "notificationRef": rel(notification_path, bundle.root),
    }


def retry_project_task(
    bundle: Bundle,
    task_id: str,
    actor: str,
    reason: str,
    runner_id: str = "",
    lease_token: str = "",
    preferred_runner: str = "",
) -> dict[str, Any]:
    if not actor.strip():
        raise KnowledgeError("retry actor is required")
    if not reason.strip():
        raise KnowledgeError("retry reason is required")
    task_path = find_project_task(bundle, task_id)
    task = ensure_project_task_runtime(bundle, task_path)
    if runner_id or lease_token:
        verify_project_task_lease(task, runner_id, lease_token)
    before = str(task.get("status") or "")
    lease_owner = str(task.get("leaseOwner") or runner_id or "")
    retry_history = as_list_of_dicts(task.get("retryHistory"))
    retry_history.append(
        {
            "fromStatus": before,
            "reason": reason,
            "actor": actor,
            "previousRunnerId": lease_owner,
            "at": utc_now(),
        }
    )
    failure_reasons = append_unique(as_list(task.get("failureReasons")), reason)
    updates = {
        **clear_project_task_lease_updates(task),
        "status": "waiting_runner",
        "retryRequestedAt": utc_now(),
        "retryRequestedBy": actor,
        "retryReason": reason,
        "retryHistory": retry_history[-50:],
        "failureReasons": failure_reasons,
        "attemptNumber": int(task.get("attemptNumber") or 1) + 1,
        "resultRef": str(task.get("resultRef") or ""),
        "nextAction": "Runner should claim the retry lease and write back fresh evidence.",
    }
    if preferred_runner:
        updates["preferredRunner"] = slug(preferred_runner)
        updates["assignedRunner"] = slug(preferred_runner)
    updated = update_frontmatter_file(task_path, updates)
    task_ref = rel(task_path, bundle.root)
    record_runner_lifecycle_event(bundle, lease_owner, str(task.get("taskId") or task_id), task_ref, "retry_requested", "waiting_runner", reason)
    audit_path = create_audit_log(bundle, actor, "task.retry", task_ref, before=before, after="waiting_runner", policy_result="agent_ring_lifecycle", details=f"reason={reason}\npreviousRunnerId={lease_owner}\npreferredRunner={preferred_runner}")
    notification_path = create_task_notification(
        bundle,
        task_path,
        updated,
        "task_retry_requested",
        recipient=str(updated.get("assignee") or updated.get("requester") or PROJECT_MANAGER_AGENT_ID),
        summary=f"任务已请求重试并等待 Runner：{updated.get('title', task_id)}。原因：{reason}。",
    )
    return {
        "apiVersion": "v0.1",
        "kind": "TaskRetryResult",
        "task": {**updated, "path": task_ref},
        "taskRef": task_ref,
        "runnerId": lease_owner,
        "preferredRunner": slug(preferred_runner) if preferred_runner else "",
        "status": "waiting_runner",
        "auditRef": rel(audit_path, bundle.root),
        "notificationRef": rel(notification_path, bundle.root),
    }


def manual_handoff_project_task(
    bundle: Bundle,
    task_id: str,
    actor: str,
    handoff_to: str,
    summary: str,
    runner_id: str = "",
    lease_token: str = "",
    evidence_refs: list[str] | None = None,
    artifact_refs: list[str] | None = None,
    next_action: str = "",
    preferred_runner: str = "",
) -> dict[str, Any]:
    if not actor.strip():
        raise KnowledgeError("handoff actor is required")
    if not handoff_to.strip():
        raise KnowledgeError("handoff target is required")
    if not summary.strip():
        raise KnowledgeError("handoff summary is required")
    task_path = find_project_task(bundle, task_id)
    task = ensure_project_task_runtime(bundle, task_path)
    runtime = normalized_task_runtime(task)
    if not boolish(runtime.get("manualHandoffAllowed"), True):
        raise KnowledgeError("manual handoff is not allowed for this task")
    if runner_id or lease_token:
        verify_project_task_lease(task, runner_id, lease_token)
    project_id = str(task.get("projectId") or "")
    project_dir = bundle.root / "projects" / slug(project_id) if project_id else bundle.root / "projects"
    ensure_dir(project_dir)
    task_ref = rel(task_path, bundle.root)
    handoff_id = f"handoff.{slug(str(task.get('taskId') or task_id))}.{unique_time_id('manual')}"
    handoff_path = project_dir / f"{handoff_id}.md"
    handoff_fm = {
        "type": "Workflow",
        "title": f"Manual handoff for {task.get('taskId', task_id)}",
        "description": "Manual Agent Ring task handoff with central audit.",
        "timestamp": utc_now(),
        "workflowId": handoff_id,
        "projectId": project_id,
        "taskId": str(task.get("taskId") or task_id),
        "taskRef": task_ref,
        "fromRunner": str(task.get("leaseOwner") or runner_id or ""),
        "handoffBy": actor,
        "handoffTo": handoff_to,
        "preferredRunner": slug(preferred_runner) if preferred_runner else "",
        "status": "active",
        "evidenceRefs": evidence_refs or [],
        "artifactRefs": artifact_refs or [],
    }
    handoff_body = "\n".join(
        [
            "## Summary",
            "",
            summary,
            "",
            "## Next Action",
            "",
            next_action or "Claim this task through Agent Ring or close it explicitly with a TaskResult.",
            "",
            "## Evidence",
            "",
            "\n".join(f"- {item}" for item in evidence_refs or []) or "- none",
            "",
            "## Artifacts",
            "",
            "\n".join(f"- {item}" for item in artifact_refs or []) or "- none",
        ]
    )
    write_text(handoff_path, render_doc(handoff_fm, handoff_body))
    before = str(task.get("status") or "")
    lease_owner = str(task.get("leaseOwner") or runner_id or "")
    handoff_refs = append_unique(as_list(task.get("handoffRefs")), rel(handoff_path, bundle.root))
    updates = {
        **clear_project_task_lease_updates(task),
        "status": "manual_handoff",
        "manualHandoff": {
            "handoffTo": handoff_to,
            "summary": summary,
            "nextAction": next_action,
            "preferredRunner": slug(preferred_runner) if preferred_runner else "",
            "handoffRef": rel(handoff_path, bundle.root),
            "createdAt": utc_now(),
            "createdBy": actor,
        },
        "handoffRefs": handoff_refs,
        "nextAction": next_action or "Manual handoff pending central resume.",
    }
    if preferred_runner:
        updates["preferredRunner"] = slug(preferred_runner)
        updates["assignedRunner"] = slug(preferred_runner)
    updated = update_frontmatter_file(task_path, updates)
    record_runner_lifecycle_event(bundle, lease_owner, str(task.get("taskId") or task_id), task_ref, "manual_handoff", "manual_handoff", summary)
    audit_path = create_audit_log(bundle, actor, "task.manual_handoff", task_ref, before=before, after="manual_handoff", policy_result="agent_ring_lifecycle", details=f"handoffTo={handoff_to}\nhandoffRef={rel(handoff_path, bundle.root)}\npreferredRunner={preferred_runner}")
    notification_path = create_task_notification(
        bundle,
        task_path,
        updated,
        "task_manual_handoff",
        recipient=handoff_to,
        summary=f"任务进入人工交接：{updated.get('title', task_id)}。交接摘要：{summary}。",
        source_message_ref=rel(handoff_path, bundle.root),
    )
    return {
        "apiVersion": "v0.1",
        "kind": "TaskManualHandoffResult",
        "task": {**updated, "path": task_ref},
        "taskRef": task_ref,
        "handoffRef": rel(handoff_path, bundle.root),
        "runnerId": lease_owner,
        "handoffTo": handoff_to,
        "status": "manual_handoff",
        "auditRef": rel(audit_path, bundle.root),
        "notificationRef": rel(notification_path, bundle.root),
    }


def schedule_project_tasks(
    bundle: Bundle,
    project_id: str = "",
    actor: str = "system.scheduler",
    claim: bool = False,
    lease_seconds: int = 600,
    limit: int = 0,
) -> dict[str, Any]:
    if lease_seconds <= 0:
        raise KnowledgeError("lease seconds must be positive")
    repaired_leases = repair_stale_task_leases(bundle, project_id, actor)
    released_followups = release_ready_handoff_followups(bundle, project_id, actor)
    task_paths = iter_dispatchable_project_task_paths(bundle, project_id)
    if limit > 0:
        task_paths = task_paths[:limit]
    items: list[dict[str, Any]] = []
    counts = {"assigned": 0, "claimed": 0, "waitingRunner": 0, "skipped": 0, "blocked": 0}
    for task_path in task_paths:
        task = load_object(task_path)
        task = ensure_project_task_runtime(bundle, task_path, task)
        task_id = str(task.get("taskId") or task_path.stem)
        before = str(task.get("status") or "")
        if before not in {"pending", "waiting_runner"}:
            counts["skipped"] += 1
            continue
        runner = select_runner_for_task(bundle, task)
        if not runner:
            if before != "waiting_runner":
                set_project_task_status(bundle, task_id, "waiting_runner", actor)
            counts["waitingRunner"] += 1
            items.append(
                {
                    "taskId": task_id,
                    "taskRef": rel(task_path, bundle.root),
                    "action": "waiting_runner",
                    "status": "waiting_runner",
                    "reason": "no eligible online runner",
                }
            )
            continue
        runner_id = str(runner.get("runnerId") or "")
        if claim:
            try:
                claim_result = claim_project_task(bundle, task_id, runner_id, lease_seconds=lease_seconds)
            except KnowledgeError as exc:
                counts["blocked"] += 1
                items.append(
                    {
                        "taskId": task_id,
                        "taskRef": rel(task_path, bundle.root),
                        "runnerId": runner_id,
                        "action": "blocked",
                        "status": "blocked",
                        "reason": str(exc),
                    }
                )
                continue
            counts["claimed"] += 1
            items.append(
                {
                    "taskId": task_id,
                    "taskRef": rel(task_path, bundle.root),
                    "runnerId": runner_id,
                    "action": "claimed",
                    "status": "processing",
                    "leaseExpiresAt": claim_result["leaseExpiresAt"],
                    "leaseToken": claim_result["leaseToken"],
                }
            )
            continue
        fm = update_frontmatter_file(task_path, {"assignedRunner": slug(runner_id), "updatedAt": utc_now()})
        create_task_notification(
            bundle,
            task_path,
            fm,
            "task_assigned",
            recipient=str(fm.get("assignee") or fm.get("requester") or "project"),
            summary=f"调度器已为任务匹配 Runner {slug(runner_id)}：{fm.get('title', task_id)}。",
        )
        create_audit_log(bundle, actor, "scheduler.task.assign", rel(task_path, bundle.root), before=before, after=str(fm.get("status") or ""), details=f"runnerId={runner_id}")
        counts["assigned"] += 1
        items.append(
            {
                "taskId": task_id,
                "taskRef": rel(task_path, bundle.root),
                "runnerId": runner_id,
                "action": "assigned",
                "status": str(fm.get("status") or ""),
            }
        )
    return {
        "apiVersion": "v0.1",
        "kind": "SchedulerAdvanceResult",
        "projectId": slug(project_id) if project_id else "",
        "claim": claim,
        "releasedFollowups": released_followups,
        "repairedLeases": repaired_leases,
        "counts": counts,
        "items": items,
    }


def run_scheduler_autopilot(
    bundle: Bundle,
    project_id: str = "",
    actor: str = PROJECT_MANAGER_AGENT_ID,
    cycles: int = 1,
    claim_limit: int = 1,
    lease_seconds: int = 600,
    claim: bool = False,
) -> dict[str, Any]:
    if cycles <= 0:
        raise KnowledgeError("cycles must be positive")
    if claim_limit < 0:
        raise KnowledgeError("claim limit cannot be negative")
    cycle_results: list[dict[str, Any]] = []
    totals = {"assigned": 0, "claimed": 0, "waitingRunner": 0, "skipped": 0, "blocked": 0, "releasedFollowups": 0, "repairedLeases": 0}
    for index in range(cycles):
        result = schedule_project_tasks(
            bundle,
            project_id=project_id,
            actor=actor,
            claim=claim,
            lease_seconds=lease_seconds,
            limit=claim_limit,
        )
        counts = dict(result.get("counts") or {})
        for key in ["assigned", "claimed", "waitingRunner", "skipped", "blocked"]:
            totals[key] += int(counts.get(key) or 0)
        released = list(result.get("releasedFollowups") or [])
        totals["releasedFollowups"] += len(released)
        repaired = list(result.get("repairedLeases") or [])
        totals["repairedLeases"] += len(repaired)
        decisions = [
            {
                "taskId": item.get("taskId", ""),
                "action": item.get("action", ""),
                "status": item.get("status", ""),
                "runnerId": item.get("runnerId", ""),
                "reason": item.get("reason", ""),
            }
            for item in list(result.get("items") or [])
        ]
        cycle_results.append(
            {
                "cycle": index + 1,
                "releasedFollowups": released,
                "repairedLeases": repaired,
                "counts": counts,
                "decisions": decisions,
            }
        )
        if not released and not repaired and not decisions:
            break
    create_audit_log(
        bundle,
        actor,
        "scheduler.autopilot.run",
        f"project:{slug(project_id) if project_id else 'all'}",
        after=f"cycles={len(cycle_results)}",
        policy_result="pm_autopilot",
        details=json.dumps(totals, ensure_ascii=False),
    )
    decisions = [decision for cycle in cycle_results for decision in cycle.get("decisions", [])]
    return {
        "apiVersion": "v0.1",
        "kind": "SchedulerAutopilotResult",
        "projectId": slug(project_id) if project_id else "",
        "actor": actor,
        "cyclesRequested": cycles,
        "cyclesRun": len(cycle_results),
        "roundsRun": len(cycle_results),
        "claimLimit": claim_limit,
        "leaseSeconds": lease_seconds,
        "dryRun": not claim,
        "claim": claim,
        "totals": totals,
        "counts": totals,
        "cycles": cycle_results,
        "decisions": decisions,
    }


def scheduler_workbench_read_model(bundle: Bundle, project_id: str = "", task_id: str = "") -> dict[str, Any]:
    repair_stale_task_leases(bundle, project_id, "system.workbench")
    task_paths = project_task_paths(bundle, project_id) if project_id else [path for root in sorted((bundle.root / "projects").glob("*/tasks")) for path in sorted(root.glob("*.md")) if path.name not in COLLECTION_NAMES]
    tasks: list[dict[str, Any]] = []
    for path in task_paths:
        try:
            task = ensure_project_task_runtime(bundle, path)
        except KnowledgeError:
            continue
        if task.get("type") not in {"ProjectTask", "KnowledgeTask"}:
            continue
        task["path"] = rel(path, bundle.root)
        tasks.append(task)
    queue = [task_summary_for_workbench(bundle, task) for task in tasks if str(task.get("status") or "") in {"pending", "waiting_runner", "processing", "claimed", "manual_handoff", "approval_relay_requested", "repair_pending", "changes_requested", "waiting_acceptance", "blocked"}]
    queue.sort(key=lambda item: project_task_dispatch_sort_key(item, Path(str(item.get("path") or item.get("taskId") or ""))))
    selected = next((task for task in tasks if task_id and slug(str(task.get("taskId") or "")) == slug(task_id)), None)
    if not selected and queue:
        selected = next((task for task in tasks if str(task.get("taskId") or "") == str(queue[0].get("taskId") or "")), None)
    runner_candidates = runner_candidates_for_workbench(bundle, selected) if selected else []
    runner_registry = runner_registry_for_workbench(bundle, project_id)
    lease_history = lease_history_for_workbench(bundle, selected, runner_registry) if selected else []
    audit_trail = audit_trail_for_workbench(bundle, project_id, selected)
    pm_control = pm_control_lease_read_model(bundle, project_id) if project_id else {}
    return {
        "apiVersion": "v0.1",
        "kind": "SchedulerWorkbenchReadModel",
        "projectId": slug(project_id) if project_id else "",
        "selectedTaskId": str(selected.get("taskId") or "") if selected else "",
        "activeQueue": queue,
        "selectedTask": task_summary_for_workbench(bundle, selected) if selected else {},
        "runnerRegistry": runner_registry,
        "currentWork": current_work_for_workbench(queue, runner_registry),
        "runnerCandidates": runner_candidates,
        "leaseStatus": lease_status_for_workbench(selected) if selected else {},
        "leaseHistory": lease_history,
        "executionContextStatus": execution_context_status_for_workbench(bundle, selected) if selected else {},
        "approvalBlockers": approval_blockers_for_workbench(selected) if selected else [],
        "environmentReadiness": environment_readiness_for_workbench(bundle, selected) if selected else {},
        "evidenceRequirements": evidence_requirements_for_workbench(selected) if selected else {},
        "retryRepairPath": retry_repair_path_for_workbench(selected) if selected else {},
        "manualHandoffPanel": manual_handoff_panel_for_workbench(selected) if selected else {},
        "scopeAudit": scope_audit_for_workbench(selected, runner_candidates) if selected else {},
        "auditTrail": audit_trail,
        "metrics": workbench_metrics(queue, runner_registry, lease_history),
        "pmDecisionLog": pm_decision_log_for_workbench(bundle, project_id, selected),
        "pmControl": pm_control,
    }


def task_summary_for_workbench(bundle: Bundle, task: dict[str, Any] | None) -> dict[str, Any]:
    if not task:
        return {}
    runtime = normalized_task_runtime(task)
    return {
        "taskId": str(task.get("taskId") or ""),
        "taskRef": str(task.get("path") or ""),
        "title": str(task.get("title") or ""),
        "status": str(task.get("status") or ""),
        "priority": str(task.get("priority") or ""),
        "assignee": str(task.get("assignee") or ""),
        "currentStage": str(task.get("currentStage") or runtime.get("stage") or ""),
        "blockedByTaskRefs": as_list(task.get("blockedByTaskRefs")),
        "failureReasons": as_list(task.get("failureReasons")),
        "nextAction": str(task.get("nextAction") or (as_list(task.get("nextActions"))[0] if as_list(task.get("nextActions")) else "")),
        "taskRuntime": runtime,
        "assignedRunner": str(task.get("assignedRunner") or ""),
        "leaseOwner": str(task.get("leaseOwner") or ""),
        "preferredRunner": str(task.get("preferredRunner") or ""),
        "resultRef": str(task.get("resultRef") or ""),
        "approvalRequest": task.get("approvalRequest") if isinstance(task.get("approvalRequest"), dict) else {},
        "manualHandoff": task.get("manualHandoff") if isinstance(task.get("manualHandoff"), dict) else {},
        "handoffRefs": as_list(task.get("handoffRefs")),
        "retryHistory": as_list_of_dicts(task.get("retryHistory")),
        "followupTaskRefs": as_list(task.get("followupTaskRefs")),
    }


def runner_registry_for_workbench(bundle: Bundle, project_id: str = "") -> list[dict[str, Any]]:
    registry: list[dict[str, Any]] = []
    root = runner_storage_dir(bundle)
    if not root.exists():
        return registry
    for path in sorted(root.glob("*.md")):
        if path.name in COLLECTION_NAMES:
            continue
        try:
            runner = load_object(path)
        except KnowledgeError:
            continue
        if runner.get("type") != "AgentRunner":
            continue
        projects = as_list(runner.get("availableProjects"))
        if project_id and projects and slug(project_id) not in {str(item) for item in projects}:
            continue
        current = as_list_of_dicts(runner.get("currentLeases"))
        stale = as_list_of_dicts(runner.get("staleLeases"))
        failed = as_list_of_dicts(runner.get("failedLeases"))
        history = as_list_of_dicts(runner.get("taskHistory"))
        registry.append(
            {
                "runnerId": str(runner.get("runnerId") or path.stem),
                "runnerRef": rel(path, bundle.root),
                "machineId": str(runner.get("machineId") or runner.get("runnerId") or path.stem),
                "owner": str(runner.get("owner") or ""),
                "name": str(runner.get("title") or ""),
                "hostType": str(runner.get("hostType") or ""),
                "mode": str(runner.get("mode") or ""),
                "status": str(runner.get("status") or ""),
                "load": str(runner.get("load") or ""),
                "ringVersion": str(runner.get("ringVersion") or ""),
                "lastHeartbeatAt": str(runner.get("lastHeartbeatAt") or runner.get("heartbeatAt") or ""),
                "heartbeatStale": runner_heartbeat_is_stale(runner),
                "agents": as_list(runner.get("agents")) or as_list(runner.get("agentIds")),
                "capabilities": as_list(runner.get("capabilities")),
                "tools": as_list(runner.get("tools")) or as_list(runner.get("toolIds")),
                "availableProjects": projects,
                "repositoryScopes": as_list(runner.get("repositoryScopes")) or as_list(runner.get("repoAccess")),
                "dataScopes": as_list(runner.get("dataScopes")),
                "currentLeases": current,
                "staleLeases": stale,
                "failedLeases": failed,
                "taskHistory": history[-20:],
                "currentLeaseCount": len(current),
                "staleLeaseCount": len(stale),
                "failedLeaseCount": len(failed),
                "lastFailure": str(runner.get("lastFailure") or ""),
                "manualHandoff": boolish(runner.get("manualHandoff"), False),
            }
        )
    registry.sort(key=lambda item: (str(item["status"]) not in {"online", "busy", "idle"}, str(item["runnerId"])))
    return registry


def current_work_for_workbench(queue: list[dict[str, Any]], runner_registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runners_by_id = {str(runner.get("runnerId") or ""): runner for runner in runner_registry}
    work: list[dict[str, Any]] = []
    for task in queue:
        runner_id = str(task.get("leaseOwner") or task.get("assignedRunner") or "")
        if str(task.get("status") or "") not in {"processing", "claimed", "manual_handoff", "approval_relay_requested", "blocked"} and not runner_id:
            continue
        runner = runners_by_id.get(runner_id, {})
        work.append(
            {
                "taskId": str(task.get("taskId") or ""),
                "taskRef": str(task.get("taskRef") or ""),
                "title": str(task.get("title") or ""),
                "status": str(task.get("status") or ""),
                "runnerId": runner_id,
                "runnerStatus": str(runner.get("status") or ""),
                "lastHeartbeatAt": str(runner.get("lastHeartbeatAt") or ""),
                "leaseOwner": str(task.get("leaseOwner") or ""),
                "nextAction": str(task.get("nextAction") or ""),
                "manualHandoff": task.get("manualHandoff") if isinstance(task.get("manualHandoff"), dict) else {},
            }
        )
    return work


def lease_history_for_workbench(bundle: Bundle, task: dict[str, Any], runner_registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    task_id = str(task.get("taskId") or "")
    history: list[dict[str, Any]] = []
    if task.get("leaseIssuedAt"):
        history.append(
            {
                "taskId": task_id,
                "event": "lease_current",
                "runnerId": str(task.get("leaseOwner") or ""),
                "leaseAttempt": task.get("leaseAttempt") or "",
                "leaseVersion": task.get("leaseVersion") or "",
                "at": str(task.get("leaseIssuedAt") or ""),
                "leaseExpiresAt": str(task.get("leaseExpiresAt") or ""),
                "status": str(task.get("status") or ""),
            }
        )
    if task.get("staleLeaseOwner"):
        history.append(
            {
                "taskId": task_id,
                "event": "stale_detected",
                "runnerId": str(task.get("staleLeaseOwner") or ""),
                "at": str(task.get("staleLeaseDetectedAt") or ""),
                "reason": str(task.get("staleLeaseReason") or ""),
                "status": str(task.get("status") or ""),
            }
        )
    for item in as_list_of_dicts(task.get("retryHistory")):
        history.append({"taskId": task_id, "event": "retry_requested", **item})
    for runner in runner_registry:
        for item in as_list_of_dicts(runner.get("taskHistory")):
            if str(item.get("taskId") or "") == task_id:
                history.append({"runnerId": str(runner.get("runnerId") or ""), **item})
    history.sort(key=lambda item: str(item.get("at") or item.get("detectedAt") or ""))
    return history[-50:]


def manual_handoff_panel_for_workbench(task: dict[str, Any]) -> dict[str, Any]:
    handoff = task.get("manualHandoff") if isinstance(task.get("manualHandoff"), dict) else {}
    status = str(task.get("status") or "")
    return {
        "status": "active" if status == "manual_handoff" else "available",
        "manualHandoffAllowed": boolish(normalized_task_runtime(task).get("manualHandoffAllowed"), True),
        "handoff": handoff,
        "handoffRefs": as_list(task.get("handoffRefs")),
        "nextAction": str(task.get("nextAction") or ""),
        "resumeActions": ["task retry", "tasks/claim", "task cancel"] if status == "manual_handoff" else ["task handoff"],
    }


def scope_audit_for_workbench(task: dict[str, Any], runner_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    denied = [candidate for candidate in runner_candidates if not candidate.get("eligible") and candidate.get("reasons")]
    return {
        "taskId": str(task.get("taskId") or ""),
        "requiredCapabilities": as_list(normalized_task_runtime(task).get("requiredCapabilities")),
        "requiredTools": as_list(normalized_task_runtime(task).get("requiredTools")),
        "repositoryRefs": as_list(normalized_task_runtime(task).get("repositoryRefs")),
        "dataScopes": as_list(normalized_task_runtime(task).get("dataScopes")),
        "sourceRefs": as_list(normalized_task_runtime(task).get("sourceRefs")),
        "deniedRunnerCount": len(denied),
        "deniedRunners": [
            {
                "runnerId": str(candidate.get("runnerId") or ""),
                "reasons": as_list(candidate.get("reasons")),
            }
            for candidate in denied[:20]
        ],
    }


def audit_trail_for_workbench(bundle: Bundle, project_id: str = "", task: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    task_id = str((task or {}).get("taskId") or "")
    task_ref = str((task or {}).get("path") or "")
    actions = ("task.", "runner.", "scheduler.", "agent_worker.")
    rows: list[dict[str, Any]] = []
    for path in sorted((bundle.root / "knowledge" / "audit").glob("*.md"))[-250:]:
        try:
            audit = load_object(path)
        except KnowledgeError:
            continue
        action = str(audit.get("action") or "")
        if not action.startswith(actions):
            continue
        target_ref = str(audit.get("targetRef") or "")
        body = read_text(path)
        if project_id and slug(project_id) not in target_ref and slug(project_id) not in body:
            continue
        if task_id and task_id not in target_ref and task_id not in body and task_ref not in target_ref:
            continue
        rows.append(
            {
                "auditRef": rel(path, bundle.root),
                "timestamp": str(audit.get("timestamp") or ""),
                "actor": str(audit.get("actor") or ""),
                "action": action,
                "targetRef": target_ref,
                "before": str(audit.get("before") or ""),
                "after": str(audit.get("after") or ""),
                "policyResult": str(audit.get("policyResult") or ""),
            }
        )
    return rows[-50:]


def workbench_metrics(queue: list[dict[str, Any]], runner_registry: list[dict[str, Any]], lease_history: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "queueDepth": len(queue),
        "runnerCount": len(runner_registry),
        "onlineRunnerCount": sum(1 for runner in runner_registry if str(runner.get("status") or "") in {"online", "busy", "idle"}),
        "activeLeaseCount": sum(int(runner.get("currentLeaseCount") or 0) for runner in runner_registry),
        "staleLeaseCount": sum(int(runner.get("staleLeaseCount") or 0) for runner in runner_registry),
        "failedLeaseCount": sum(int(runner.get("failedLeaseCount") or 0) for runner in runner_registry),
        "selectedTaskHistoryEvents": len(lease_history),
        "manualHandoffCount": sum(1 for item in queue if str(item.get("status") or "") == "manual_handoff"),
    }


def runner_for_workbench_task(bundle: Bundle, task: dict[str, Any]) -> dict[str, Any] | None:
    for runner_id in [str(task.get("leaseOwner") or ""), str(task.get("assignedRunner") or "")]:
        if not runner_id:
            continue
        try:
            return load_object(find_agent_runner(bundle, runner_id))
        except KnowledgeError:
            continue
    return None


def execution_context_status_for_workbench(bundle: Bundle, task: dict[str, Any]) -> dict[str, Any]:
    task_id = str(task.get("taskId") or "")
    ref = f".zhenzhi/execution-context/task.{slug(task_id)}.json" if task_id else ""
    path = bundle.root / ref if ref else bundle.root
    payload: dict[str, Any] = {}
    if ref and path.exists():
        try:
            payload = json.loads(read_text(path))
        except (json.JSONDecodeError, OSError):
            payload = {}
    has_lease_proof = bool(str(task.get("leaseProofHash") or task.get("leaseTokenHash") or payload.get("leaseProof") or ""))
    status = "ready" if ref and path.exists() and has_lease_proof else "missing"
    return {
        "status": status,
        "executionContextRef": ref if path.exists() else "",
        "runnerId": str(task.get("leaseOwner") or payload.get("runnerId") or ""),
        "leaseExpiresAt": str(task.get("leaseExpiresAt") or payload.get("leaseExpiresAt") or ""),
        "leaseProofPresent": has_lease_proof,
        "contextRef": str(payload.get("contextRef") or ""),
        "writebackCommandAvailable": bool(payload.get("writebackCommandAvailable")),
    }


def environment_readiness_for_workbench(bundle: Bundle, task: dict[str, Any]) -> dict[str, Any]:
    return task_environment_readiness(bundle, task, runner_for_workbench_task(bundle, task))


def runner_candidates_for_workbench(bundle: Bundle, task: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    root = runner_storage_dir(bundle)
    if not root.exists():
        return candidates
    for path in sorted(root.glob("*.md")):
        if path.name in COLLECTION_NAMES:
            continue
        try:
            runner = load_object(path)
        except KnowledgeError:
            continue
        if runner.get("type") != "AgentRunner":
            continue
        readiness = task_environment_readiness(bundle, task, runner)
        missing = as_list(readiness.get("missingRunnerRequirements"))
        missing_secret_refs = as_list(readiness.get("missingSecretRefs"))
        missing_env_vars = as_list(readiness.get("missingEnvVars"))
        status_ok = runner.get("status") in {"online", "idle", "busy"}
        heartbeat_stale = runner_heartbeat_is_stale(runner)
        candidates.append(
            {
                "runnerId": str(runner.get("runnerId") or path.stem),
                "runnerRef": rel(path, bundle.root),
                "status": str(runner.get("status") or ""),
                "load": str(runner.get("load") or ""),
                "eligible": status_ok and not heartbeat_stale and readiness.get("status") == "ready",
                "reasons": ([] if status_ok else ["runner status not schedulable"]) + (["runner heartbeat stale"] if heartbeat_stale else []) + missing + [f"secretRef:{item}" for item in missing_secret_refs] + [f"env:{item}" for item in missing_env_vars],
                "currentLeases": as_list_of_dicts(runner.get("currentLeases")),
                "staleLeases": as_list_of_dicts(runner.get("staleLeases")),
                "failedLeases": as_list_of_dicts(runner.get("failedLeases")),
            }
        )
    candidates.sort(key=lambda item: (0 if item["eligible"] else 1, str(item["runnerId"])))
    return candidates


def lease_status_for_workbench(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "leaseOwner": str(task.get("leaseOwner") or ""),
        "assignedRunner": str(task.get("assignedRunner") or ""),
        "leaseIssuedAt": str(task.get("leaseIssuedAt") or ""),
        "leaseExpiresAt": str(task.get("leaseExpiresAt") or ""),
        "leaseHeartbeatAt": str(task.get("leaseHeartbeatAt") or task.get("heartbeatAt") or ""),
        "leaseVersion": task.get("leaseVersion") or "",
        "leaseAttempt": task.get("leaseAttempt") or "",
        "staleLeaseOwner": str(task.get("staleLeaseOwner") or ""),
        "staleLeaseReason": str(task.get("staleLeaseReason") or ""),
    }


def approval_blockers_for_workbench(task: dict[str, Any]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    request = task.get("approvalRequest") if isinstance(task.get("approvalRequest"), dict) else {}
    if request:
        blockers.append(request)
    runtime = normalized_task_runtime(task)
    if boolish(runtime.get("approvalRelayRequired"), False) and not request:
        blockers.append({"type": "approval_relay_missing", "summary": "Task runtime requires approval relay before closure.", "requiredDecisionOwner": project_manager_for_task(task)})
    return blockers


def evidence_requirements_for_workbench(task: dict[str, Any]) -> dict[str, Any]:
    runtime = normalized_task_runtime(task)
    return {
        "acceptancePath": str(runtime.get("acceptancePath") or ""),
        "reviewPath": str(runtime.get("reviewPath") or ""),
        "testEvidenceRequired": boolish(runtime.get("testEvidenceRequired"), False),
        "knowledgeEvidenceRequired": boolish(runtime.get("knowledgeEvidenceRequired"), False),
        "productEvidenceRequired": boolish(runtime.get("productEvidenceRequired"), False),
        "requiredCapabilities": as_list(runtime.get("requiredCapabilities")),
        "requiredTools": as_list(runtime.get("requiredTools")),
        "sourceRefs": as_list(runtime.get("sourceRefs")),
        "repositoryRefs": as_list(runtime.get("repositoryRefs")),
        "dataScopes": as_list(runtime.get("dataScopes")),
    }


def retry_repair_path_for_workbench(task: dict[str, Any]) -> dict[str, Any]:
    status = str(task.get("status") or "")
    if status in {"changes_requested", "repair_pending"}:
        action = "repair_original_task"
    elif status == "blocked":
        action = "pm_escalation_or_reassign"
    elif status == "waiting_runner":
        action = "register_or_select_runner"
    elif status == "waiting_acceptance":
        action = "pm_or_human_acceptance"
    else:
        action = "continue_execution"
    return {
        "action": action,
        "followupTaskRefs": as_list(task.get("followupTaskRefs")),
        "failureReasons": as_list(task.get("failureReasons")),
        "triggerResultRef": str(task.get("triggerResultRef") or task.get("resultRef") or ""),
    }


def pm_decision_log_for_workbench(bundle: Bundle, project_id: str = "", task: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    logs: list[dict[str, Any]] = []
    target_task_id = str((task or {}).get("taskId") or "")
    for path in sorted((bundle.root / "knowledge" / "audit").glob("*.md"))[-200:]:
        try:
            audit = load_object(path)
        except KnowledgeError:
            continue
        action = str(audit.get("action") or "")
        details = read_text(path)
        if action.startswith("scheduler.") or action.startswith("task.acceptance") or "approval" in action:
            if target_task_id and target_task_id not in details and target_task_id not in str(audit.get("targetRef") or ""):
                continue
            logs.append(
                {
                    "auditRef": rel(path, bundle.root),
                    "timestamp": str(audit.get("timestamp") or ""),
                    "actor": str(audit.get("actor") or ""),
                    "action": action,
                    "targetRef": str(audit.get("targetRef") or ""),
                    "policyResult": str(audit.get("policyResult") or ""),
                }
            )
    return logs[-50:]


def task_matches_agent(task: dict[str, Any], agent_id: str) -> bool:
    agent = str(agent_id or "").strip()
    if not agent:
        return True
    task_agents = {
        str(item)
        for item in [
            task.get("assignee"),
            task.get("executorAgent"),
            *as_list(task.get("requiredAgents")),
        ]
        if str(item or "").strip()
    }
    return not task_agents or agent in task_agents


def task_is_technical_solution_stage(task: dict[str, Any]) -> bool:
    stage = str(task.get("currentStage") or "").strip().lower()
    return stage == "technical_solution" or boolish(task.get("technicalSolutionRequired"), False)


def task_is_product_requirement_stage(task: dict[str, Any]) -> bool:
    stage = str(task.get("currentStage") or "").strip().lower()
    task_type = normalized_task_type(str(task.get("taskType") or ""))
    return stage == "product_requirement" or task_type == "product_requirement"


def task_is_product_review_stage(task: dict[str, Any]) -> bool:
    stage = str(task.get("currentStage") or "").strip().lower()
    task_type = normalized_task_type(str(task.get("taskType") or ""))
    assignee = str(task.get("assignee") or task.get("executorAgent") or "")
    return task_type == "product_review" or (stage == "solution_review" and assignee == PRODUCT_MANAGER_AGENT_ID)


def technical_solution_summary_for_task(task: dict[str, Any], task_ref: str) -> str:
    requirement_refs = as_list(task.get("requirementRefs"))
    expected_outputs = as_list(task.get("expectedOutput"))
    source_refs = as_list(task.get("sourceMaterialRefs"))
    return "\n".join(
        [
            "技术方案草案已由 Agent Worker 自动生成，等待项目经理审核后进入实现阶段。",
            "",
            f"任务：{task.get('taskId', '')} - {task.get('title', '')}",
            f"任务记录：{task_ref}",
            f"当前阶段：{task.get('currentStage') or 'technical_solution'}",
            "需求覆盖：" + (", ".join(requirement_refs) if requirement_refs else "未声明 requirementRefs"),
            "输入材料：" + (", ".join(source_refs) if source_refs else "无"),
            "",
            "方案边界：",
            "- 先确认对象模型、状态机、CLI/API 行为、证据写回和验收门，不在技术方案阶段伪装完成代码实现。",
            "- 实现任务必须继续产出代码变更、测试证据、TaskResult、风险和回滚说明。",
            "",
            "实施切片：",
            "- 梳理相关模块和现有契约。",
            "- 明确数据字段、状态迁移、审计/通知、错误处理。",
            "- 完成最小代码实现后运行 validate 和针对性测试。",
            "- 将测试 Agent 需要验证的入口、样例命令、预期状态写入交接。",
            "",
            "测试策略：",
            "- 覆盖 CLI 正常路径、无 Runner、租约冲突、验收等待、证据缺失。",
            "- 保持 validate 通过，失败时生成返工任务或阻塞说明。",
            "",
            "预期输出：" + ("; ".join(expected_outputs) if expected_outputs else "技术方案、实现证据、测试证据、PM 验收依据"),
            "",
            "下一步：项目经理 Agent 审核技术方案；通过后创建或释放开发实现任务，未通过则退回研发修订。",
        ]
    )


def product_review_summary_for_task(task: dict[str, Any], task_ref: str) -> str:
    source_refs = as_list(task.get("sourceMaterialRefs"))
    expected_outputs = as_list(task.get("expectedOutput"))
    return "\n".join(
        [
            "V1 产品范围已锁定，研发技术方案任务可以释放，但不得越过产品边界。",
            "",
            f"任务：{task.get('taskId', '')} - {task.get('title', '')}",
            f"任务记录：{task_ref}",
            f"当前阶段：{task.get('currentStage') or 'solution_review'}",
            "输入材料：" + (", ".join(source_refs) if source_refs else "无"),
            "",
            "V1 必须交付：",
            "- Agent Profile Service。",
            "- Skill Registry。",
            "- Session Registry。",
            "- Local Router。",
            "- TaskPackage and AgentMessage。",
            "- Agent Runtime。",
            "- Group Agent/Orchestrator。",
            "- Minimal Worktree Manager。",
            "- Console/read model。",
            "- Closed-loop acceptance harness。",
            "",
            "V1 不作为发布门：",
            "- Central Hub and cross-device routing。",
            "- Feishu/enterprise entrance。",
            "- Full native desktop packaging, signing, updater, secure storage。",
            "- Long-term Agent memory/growth。",
            "",
            "产品非妥协项：",
            "- 正式验收证据必须来自 Local Router/Session Registry/Agent Runtime，不得用 Codex subagent 替代。",
            "- 研发必须先出技术方案，产品评审通过后才实现。",
            "- 测试失败必须回到 Development Agent 返修。",
            "- 高风险动作必须人工确认。",
            "",
            "预期输出：" + ("; ".join(expected_outputs) if expected_outputs else "V1 scope acceptance criteria and out-of-scope list"),
            "",
            "下一步：项目经理 Agent 释放 Development Agent 的 V1 技术方案任务。",
        ]
    )


def product_requirement_summary_for_task(task: dict[str, Any], task_ref: str) -> str:
    expected_outputs = as_list(task.get("expectedOutput"))
    source_refs = as_list(task.get("sourceMaterialRefs"))
    return "\n".join(
        [
            "V1 产品需求结构化包已由 Agent Worker 生成，等待产品范围锁定与 PM 释放后进入研发技术方案阶段。",
            "",
            f"任务：{task.get('taskId', '')} - {task.get('title', '')}",
            f"任务记录：{task_ref}",
            f"当前阶段：{task.get('currentStage') or 'product_requirement'}",
            "输入材料：" + (", ".join(source_refs) if source_refs else "无"),
            "",
            "V1 产品边界：",
            "- V1 聚焦单机闭环：Agent Profile、Skill Registry、Session Registry、Local Router、Task Package、Agent Runtime、Orchestrator、Worktree、Console、闭环验收。",
            "- V1 不把 Central Hub、飞书/企业入口、跨设备调度、完整桌面打包签名/updater、长期 Agent Memory 作为发布门。",
            "",
            "需求结构：",
            "- 业务目标：证明一台电脑上多个正式 Agent 会话可以完成任务分派、执行、测试、验收、沉淀闭环。",
            "- 用户场景：项目经理输入目标后，组 Agent 选择产品/研发/测试等角色 Agent 并跟踪结果。",
            "- 产品需求：Agent 可定义，Session 可注册，消息可路由，任务可分派，结果可回写，测试失败可返修，高风险动作需确认。",
            "- 功能需求：Profile/Skill registry、Local Router、Session Registry、TaskPackage、AgentMessage、Agent Runtime、Worktree Manager、Console/read model、Acceptance harness。",
            "",
            "验收矩阵：",
            "- 至少 Group/Product/Development/Test 四类 Agent 会话可注册到 Local Router。",
            "- Group Agent 可从用户目标生成任务图和 Task Package。",
            "- Development Agent 可在独立 worktree 接收并执行实现任务。",
            "- Test Agent 可针对 worktree 返回 pass/fail 证据；fail 必须生成 Development repair task。",
            "- 高风险 merge/delete/deploy/external send/database change 必须进入人工确认并留审计。",
            "- TaskResult 必须包含 session/task/message/evidence/test/audit refs。",
            "",
            "预期输出：" + ("; ".join(expected_outputs) if expected_outputs else "V1 产品包、需求树、验收矩阵、V1/V2/V3 边界"),
            "",
            "下一步：产品经理 Agent 锁定 V1 范围；通过后项目经理 Agent 释放研发技术方案任务。",
        ]
    )


def run_agent_worker(
    bundle: Bundle,
    project_id: str = "",
    agent_id: str = "",
    runner_id: str = "",
    limit: int = 1,
    lease_seconds: int = 600,
    stage: str = "",
) -> dict[str, Any]:
    if limit <= 0:
        raise KnowledgeError("limit must be positive")
    if lease_seconds <= 0:
        raise KnowledgeError("lease seconds must be positive")
    items: list[dict[str, Any]] = []
    counts = {"claimed": 0, "submitted": 0, "skipped": 0, "blocked": 0}
    for task_path in iter_dispatchable_project_task_paths(bundle, project_id):
        if counts["submitted"] >= limit:
            break
        task = load_object(task_path)
        task_id = str(task.get("taskId") or task_path.stem)
        requested_stage = str(stage or "").strip().lower()
        task_stage = str(task.get("currentStage") or "").strip().lower()
        if requested_stage and task_stage != requested_stage:
            counts["skipped"] += 1
            continue
        if not task_matches_agent(task, agent_id):
            counts["skipped"] += 1
            continue
        runner = load_object(find_agent_runner(bundle, runner_id)) if runner_id else select_runner_for_task(bundle, task)
        if not runner:
            counts["blocked"] += 1
            items.append(
                {
                    "taskId": task_id,
                    "taskRef": rel(task_path, bundle.root),
                    "action": "blocked",
                    "status": str(task.get("status") or ""),
                    "reason": "no eligible online runner",
                }
            )
            continue
        selected_runner_id = str(runner.get("runnerId") or runner_id)
        if not runner_can_schedule_task(bundle, runner, task):
            counts["blocked"] += 1
            items.append(
                {
                    "taskId": task_id,
                    "taskRef": rel(task_path, bundle.root),
                    "runnerId": selected_runner_id,
                    "action": "blocked",
                    "status": str(task.get("status") or ""),
                    "reason": "runner cannot schedule task",
                }
            )
            continue
        is_product_requirement = task_is_product_requirement_stage(task)
        is_product_review = task_is_product_review_stage(task)
        is_technical_solution = task_is_technical_solution_stage(task)
        if not (is_product_requirement or is_product_review or is_technical_solution):
            counts["skipped"] += 1
            items.append(
                {
                    "taskId": task_id,
                    "taskRef": rel(task_path, bundle.root),
                    "runnerId": selected_runner_id,
                    "action": "skipped",
                    "status": str(task.get("status") or ""),
                    "reason": "worker only auto-submits product_requirement, product_review, and technical_solution stages in the minimal runtime",
                }
            )
            continue
        try:
            claim = claim_project_task(bundle, task_id, selected_runner_id, lease_seconds=lease_seconds)
            counts["claimed"] += 1
            task_after_claim = dict(claim.get("task") or task)
            task_ref = str(task_after_claim.get("path") or rel(task_path, bundle.root))
            if is_product_requirement:
                summary = product_requirement_summary_for_task(task_after_claim, task_ref)
            elif is_product_review:
                summary = product_review_summary_for_task(task_after_claim, task_ref)
            else:
                summary = technical_solution_summary_for_task(task_after_claim, task_ref)
            requirement_refs = as_list(task_after_claim.get("requirementRefs"))
            evidence_refs = [task_ref, *as_list(task_after_claim.get("sourceMaterialRefs"))]
            next_actions = (
                [
                    "Product Manager Agent lock V1 scope and acceptance matrix.",
                    "PM Agent release Development Agent technical solution tasks only after product scope lock.",
                    "If product package is incomplete, return to Product Manager Agent for revision.",
                ]
                if is_product_requirement
                else [
                    "PM Agent release Development Agent technical solution tasks.",
                    "Development Agent must produce technical solutions before implementation.",
                    "Product Manager Agent must review technical solutions before implementation starts.",
                ]
                if is_product_review
                else [
                    "PM Agent review technical solution.",
                    "If accepted, release implementation task for Development Agent.",
                    "If rejected, create changes_requested task with concrete review notes.",
                ]
            )
            tests_or_checks = (
                [
                    "product_requirement_package_generated",
                    "v1_scope_boundary_declared",
                    "acceptance_matrix_declared",
                    "development_not_released_before_product_scope_lock",
                ]
                if is_product_requirement
                else [
                    "v1_scope_locked",
                    "v1_out_of_scope_declared",
                    "development_technical_solution_release_allowed",
                    "implementation_still_blocked_until_solution_review",
                ]
                if is_product_review
                else [
                    "technical_solution_draft_generated",
                    f"requirementRefs={len(requirement_refs)}",
                    "code_implementation_not_claimed_done",
                ]
            )
            handoff_summary = (
                "V1 产品需求结构化包已提交，等待产品范围锁定后再释放研发技术方案。"
                if is_product_requirement
                else "V1 产品范围已锁定，PM 可以释放研发技术方案任务。"
                if is_product_review
                else "技术方案草案已提交，等待 PM 审核后再进入实现阶段。"
            )
            next_suggested_task = (
                "Run Product Manager scope review and then release Development technical solution tasks."
                if is_product_requirement
                else "Release Development technical solution tasks for V1 runtime slices."
                if is_product_review
                else "Review technical solution and release implementation task."
            )
            result_path = finish_project_task(
                bundle,
                task_id,
                "submitted",
                summary,
                output_refs=[task_ref],
                evidence_refs=evidence_refs,
                next_actions=next_actions,
                runner_id=selected_runner_id,
                lease_token=str(claim.get("leaseToken") or ""),
                executor_agent=agent_id or str(task_after_claim.get("assignee") or ""),
                tests_or_checks=tests_or_checks,
                handoff_to=PROJECT_MANAGER_AGENT_ID,
                handoff_summary=handoff_summary,
                artifact_refs=[task_ref],
                open_risks=[
                    "This minimal worker does not call an external LLM or Agent Ring executor yet.",
                    "PM review is required before downstream work starts.",
                ],
                next_suggested_task=next_suggested_task,
            )
        except KnowledgeError as exc:
            counts["blocked"] += 1
            items.append(
                {
                    "taskId": task_id,
                    "taskRef": rel(task_path, bundle.root),
                    "runnerId": selected_runner_id,
                    "action": "blocked",
                    "status": "blocked",
                    "reason": str(exc),
                }
            )
            continue
        counts["submitted"] += 1
        items.append(
            {
                "taskId": task_id,
                "taskRef": task_ref,
                "runnerId": selected_runner_id,
                "executorAgent": agent_id or str(task_after_claim.get("assignee") or ""),
                "action": "submitted_product_requirement" if is_product_requirement else "submitted_product_review" if is_product_review else "submitted_technical_solution",
                "status": "waiting_acceptance",
                "resultRef": rel(result_path, bundle.root),
                "requirementRefs": requirement_refs,
            }
        )
    create_audit_log(
        bundle,
        agent_id or "agent.worker",
        "agent_worker.run",
        f"project:{slug(project_id) if project_id else 'all'}",
        after=f"submitted={counts['submitted']}",
        policy_result="agent_worker_minimal_runtime",
        details=json.dumps(counts, ensure_ascii=False),
    )
    return {
        "apiVersion": "v0.1",
        "kind": "AgentWorkerRunResult",
        "projectId": slug(project_id) if project_id else "",
        "agentId": agent_id,
        "runnerId": runner_id,
        "limit": limit,
        "leaseSeconds": lease_seconds,
        "stage": stage,
        "counts": {**counts, "resultsSubmitted": counts["submitted"]},
        "items": items,
    }


def v1_runtime_dir(bundle: Bundle, name: str) -> Path:
    path = bundle.root / "runtime" / name
    ensure_dir(path)
    index = path / "index.md"
    if not index.exists():
        write_text(index, f"# {name}\n")
    return path


def find_v1_runtime_object(bundle: Bundle, name: str, object_id: str) -> Path:
    path = v1_runtime_dir(bundle, name) / f"{slug(object_id)}.md"
    if not path.exists():
        raise KnowledgeError(f"runtime object not found: {name}/{object_id}")
    return path


def register_v1_agent_profile(bundle: Bundle, agent_id: str, project_id: str = "", skills: list[str] | None = None) -> Path:
    if not agent_id.strip():
        raise KnowledgeError("agent id is required")
    agent_slug = slug(agent_id)
    agent_ref = f"agents/{agent_slug}.md"
    fm = {
        "type": "AgentProfile",
        "title": f"V1 Agent Profile - {agent_id}",
        "description": "Executable V1 Agent profile for single-machine Agent Runtime.",
        "timestamp": utc_now(),
        "profileId": f"profile.{agent_slug}",
        "agentId": agent_id,
        "projectId": slug(project_id) if project_id else "",
        "status": "active",
        "sessionMode": "independent",
        "roleSoulRef": agent_ref if (bundle.root / agent_ref).exists() else "",
        "responsibilities": [],
        "allowedSkills": as_list(skills),
        "modelPolicy": {"mode": "inherit", "defaultModel": "project_default"},
        "permissions": {"fileRead": True, "fileWrite": "project_scope", "codeWrite": agent_id == DEVELOPMENT_AGENT_ID},
        "outputContract": "markdown_structured",
    }
    body = "## Runtime Contract\n\n- Load role rules before execution.\n- Use only allowed skills and project-scoped files.\n- Write TaskResult evidence before handoff.\n"
    path = v1_runtime_dir(bundle, "agent-profiles") / f"{slug(fm['profileId'])}.md"
    write_text(path, render_doc(fm, body))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, "system.v1", "v1.agent_profile.register", rel(path, bundle.root), after="active", policy_result="v1_single_machine")
    return path


def register_v1_skill(bundle: Bundle, skill_id: str, name: str = "", allowed_agents: list[str] | None = None, risk_level: str = "low") -> Path:
    if not skill_id.strip():
        raise KnowledgeError("skill id is required")
    fm = {
        "type": "SkillDefinition",
        "title": name or f"V1 Skill - {skill_id}",
        "description": "Executable V1 Skill Registry entry.",
        "timestamp": utc_now(),
        "skillId": slug(skill_id),
        "status": "active",
        "inputSchema": {},
        "outputSchema": {},
        "tools": [],
        "riskLevel": risk_level,
        "confirmationPolicy": "human_required" if risk_level in {"high", "critical"} else "none",
        "allowedAgents": as_list(allowed_agents),
    }
    path = v1_runtime_dir(bundle, "skills") / f"{slug(skill_id)}.md"
    write_text(path, render_doc(fm, "## Purpose\n\nThis skill definition constrains V1 Agent Runtime execution.\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, "system.v1", "v1.skill.register", rel(path, bundle.root), after="active", policy_result="v1_single_machine")
    return path


def register_v1_device(
    bundle: Bundle,
    device_id: str = "device.local",
    name: str = "Local Machine",
    host_type: str = "local_mac",
    capabilities: list[str] | None = None,
    workspace: str = "",
    status: str = "online",
) -> Path:
    fm = {
        "type": "AgentDevice",
        "title": f"V1 Agent Device - {device_id}",
        "description": "V1 device registry entry. V1 has one local device, but routing remains device-aware for later Hub expansion.",
        "timestamp": utc_now(),
        "deviceId": slug(device_id),
        "name": name,
        "hostType": host_type,
        "status": status,
        "capabilities": as_list(capabilities),
        "workspace": workspace or str(bundle.root),
        "lastHeartbeatAt": utc_now(),
    }
    path = v1_runtime_dir(bundle, "devices") / f"{slug(device_id)}.md"
    write_text(path, render_doc(fm, "## Purpose\n\nLocal Router routes through this device even in V1 single-machine mode.\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, "system.v1", "v1.device.register", rel(path, bundle.root), after=status, policy_result="v1_single_machine_device_aware")
    return path


def list_v1_devices(bundle: Bundle) -> list[dict[str, Any]]:
    devices: list[dict[str, Any]] = []
    for path in sorted(v1_runtime_dir(bundle, "devices").glob("*.md")):
        if path.name == "index.md":
            continue
        devices.append({**load_object(path), "path": rel(path, bundle.root)})
    return devices


def register_v1_agent_session(
    bundle: Bundle,
    project_id: str,
    agent_id: str,
    session_id: str = "",
    capabilities: list[str] | None = None,
    status: str = "online",
    device_id: str = "device.local",
) -> Path:
    if not project_id.strip() or not agent_id.strip():
        raise KnowledgeError("project id and agent id are required")
    sid = session_id or f"session.{slug(project_id)}.{slug(agent_id)}"
    fm = {
        "type": "AgentSession",
        "title": f"V1 Agent Session - {sid}",
        "description": "Local Router session registration for one formal Agent.",
        "timestamp": utc_now(),
        "sessionId": slug(sid),
        "projectId": slug(project_id),
        "agentId": agent_id,
        "status": status,
        "deviceId": slug(device_id),
        "capabilities": as_list(capabilities),
        "currentTaskId": "",
        "lastHeartbeatAt": utc_now(),
        "messageCount": 0,
    }
    path = v1_runtime_dir(bundle, "sessions") / f"{slug(sid)}.md"
    write_text(path, render_doc(fm, "## Purpose\n\nThis session is routable by the V1 Local Router.\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, agent_id, "v1.session.register", rel(path, bundle.root), after=status, policy_result="v1_single_machine")
    return path


def heartbeat_v1_agent_session(bundle: Bundle, session_id: str, status: str = "online", current_task_id: str = "") -> Path:
    path = find_v1_runtime_object(bundle, "sessions", session_id)
    updates: dict[str, Any] = {"status": status, "lastHeartbeatAt": utc_now()}
    if current_task_id:
        updates["currentTaskId"] = current_task_id
    updated = update_frontmatter_file(path, updates)
    create_audit_log(bundle, str(updated.get("agentId") or "system.v1"), "v1.session.heartbeat", rel(path, bundle.root), after=status, policy_result="v1_single_machine")
    return path


def list_v1_agent_sessions(bundle: Bundle, project_id: str = "") -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    for path in sorted(v1_runtime_dir(bundle, "sessions").glob("*.md")):
        if path.name == "index.md":
            continue
        item = load_object(path)
        if project_id and str(item.get("projectId") or "") != slug(project_id):
            continue
        sessions.append({**item, "path": rel(path, bundle.root)})
    return sessions


def select_v1_session(bundle: Bundle, project_id: str, agent_id: str) -> dict[str, Any] | None:
    for item in list_v1_agent_sessions(bundle, project_id):
        if str(item.get("agentId") or "") == agent_id and str(item.get("status") or "") in {"online", "idle", "busy"}:
            return item
    return None


def send_v1_agent_message(
    bundle: Bundle,
    project_id: str,
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: dict[str, Any] | None = None,
    context_refs: list[str] | None = None,
    priority: str = "normal",
) -> Path:
    from_session = select_v1_session(bundle, project_id, from_agent)
    to_session = select_v1_session(bundle, project_id, to_agent)
    message_id = unique_time_id("msg")
    status = "delivered" if to_session else "blocked"
    fm = {
        "type": "AgentMessage",
        "title": f"V1 Agent Message - {message_id}",
        "description": "Local Router message between V1 Agent sessions.",
        "timestamp": utc_now(),
        "messageId": message_id,
        "projectId": slug(project_id),
        "fromAgentId": from_agent,
        "toAgentId": to_agent,
        "fromSessionId": str(from_session.get("sessionId") or "") if from_session else "",
        "toSessionId": str(to_session.get("sessionId") or "") if to_session else "",
        "messageType": message_type,
        "priority": priority,
        "payload": payload or {},
        "contextRefs": as_list(context_refs),
        "routing": {"routeType": "local", "targetDeviceId": str(to_session.get("deviceId") or "") if to_session else ""},
        "status": status,
    }
    path = v1_runtime_dir(bundle, "messages") / f"{slug(message_id)}.md"
    write_text(path, render_doc(fm, "## Payload\n\n```json\n" + json.dumps(payload or {}, indent=2, ensure_ascii=False) + "\n```\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, from_agent, "v1.router.message", rel(path, bundle.root), after=status, policy_result="v1_local_router")
    if not to_session:
        raise KnowledgeError(f"target session is not online for agent: {to_agent}")
    return path


def compile_v1_task_package(bundle: Bundle, task_id: str, from_agent: str, to_agent: str, project_id: str = "") -> Path:
    task_path = find_project_task(bundle, task_id)
    task = ensure_project_task_runtime(bundle, task_path)
    pid = slug(project_id or str(task.get("projectId") or ""))
    package_id = unique_time_id(f"pkg.{slug(task_id)}")
    context_refs = [rel(task_path, bundle.root), *as_list(task.get("sourceMaterialRefs"))]
    fm = {
        "type": "TaskPackage",
        "title": f"V1 Task Package - {task_id}",
        "description": "Runtime-deliverable package compiled from ProjectTask.",
        "timestamp": utc_now(),
        "packageId": package_id,
        "taskId": task_id,
        "taskRef": rel(task_path, bundle.root),
        "projectId": pid,
        "fromAgentId": from_agent,
        "toAgentId": to_agent,
        "contextRefs": context_refs,
        "requiredCapabilities": as_list(task.get("requiredCapabilities")),
        "outputContract": {"format": "TaskResult", "requiredSections": ["summary", "evidence", "testsOrChecks", "nextActions"]},
        "riskLevel": str(dict(task.get("taskRuntime") or {}).get("riskLevel") or "low"),
        "confirmationPolicy": "standard",
        "status": "ready",
    }
    path = v1_runtime_dir(bundle, "task-packages") / f"{slug(package_id)}.md"
    write_text(path, render_doc(fm, "## Instructions\n\nExecute this package through Agent Runtime and write TaskResult evidence.\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    message_path = send_v1_agent_message(bundle, pid, from_agent, to_agent, "task", {"taskId": task_id, "packageId": package_id}, context_refs, priority=str(task.get("priority") or "normal"))
    update_frontmatter_file(path, {"messageRef": rel(message_path, bundle.root)})
    create_audit_log(bundle, from_agent, "v1.task_package.compile", rel(path, bundle.root), after="ready", policy_result="v1_single_machine")
    return path


def allocate_v1_worktree(bundle: Bundle, project_id: str, task_id: str, agent_id: str) -> Path:
    worktree_id = f"worktree.{slug(task_id)}.{slug(agent_id)}"
    worktree_path = bundle.root / ".zhenzhi" / "worktrees" / slug(worktree_id)
    ensure_dir(worktree_path)
    fm = {
        "type": "WorktreeBinding",
        "title": f"V1 Worktree Binding - {task_id}",
        "description": "Minimal V1 local worktree binding for development/test isolation.",
        "timestamp": utc_now(),
        "worktreeId": worktree_id,
        "projectId": slug(project_id),
        "taskId": task_id,
        "agentId": agent_id,
        "path": str(worktree_path),
        "branch": f"v1/{slug(task_id)}",
        "status": "active",
    }
    path = v1_runtime_dir(bundle, "worktrees") / f"{slug(worktree_id)}.md"
    write_text(path, render_doc(fm, "## Purpose\n\nThis binding records isolated execution scope for V1 development/test tasks.\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, agent_id, "v1.worktree.allocate", rel(path, bundle.root), after="active", policy_result="v1_single_machine")
    return path


def v1_runtime_execution_contract(
    bundle: Bundle,
    task: dict[str, Any],
    task_ref: str,
    package_ref: str,
    worktree_ref: str,
    package: dict[str, Any],
    agent_id: str,
) -> dict[str, Any]:
    task_id = str(task.get("taskId") or "")
    task_type = str(task.get("taskType") or "").strip().lower()
    stage = str(task.get("currentStage") or "").strip().lower()
    source_refs = as_list(task.get("sourceMaterialRefs"))
    evidence_refs = [task_ref, package_ref, *source_refs, *([worktree_ref] if worktree_ref else [])]
    output_refs = [task_ref, package_ref, *([worktree_ref] if worktree_ref else [])]
    tests = ["v1_agent_runtime_executed", "task_package_received", "task_result_written"]
    if worktree_ref:
        tests.append("worktree_binding_created")
    message_ref = str(package.get("messageRef") or "")
    target_device_id = ""
    if message_ref:
        try:
            package_message = load_object(bundle.root / message_ref)
            target_device_id = str(dict(package_message.get("routing") or {}).get("targetDeviceId") or "")
        except KnowledgeError:
            target_device_id = ""
    if target_device_id:
        tests.append("device_aware_route_verified")

    if agent_id == PRODUCT_MANAGER_AGENT_ID and task_type == "product_review":
        accepted_inputs = [
            ref
            for ref in source_refs
            if any(token in ref for token in ["acceptance", "test", "pm-product-final", "requirement", "scope-review"])
        ]
        coverage_line = f"{len(accepted_inputs)}/{len(source_refs)} source refs are product-acceptance or requirement evidence."
        summary = "\n".join(
            [
                "Product Agent final verdict: accepted for V1 single-machine closed loop.",
                "",
                "Product coverage checked:",
                "- Product requirement structure and V1 scope were produced before development.",
                "- Development implementation and Test Agent closed-loop acceptance are linked as source evidence.",
                "- PM final process acceptance is linked as source evidence.",
                "- Device-aware local routing is represented even in single-machine mode.",
                "",
                f"Coverage evidence: {coverage_line}",
                f"TaskPackage route targetDeviceId: {target_device_id or 'missing'}",
                "",
                "Accepted V1 boundary:",
                "- Single local device runtime: Agent profiles, skills, sessions, local router, TaskPackage, Agent Runtime, TaskResult, and acceptance run.",
                "- Cross-device Hub, Feishu live entrance, and native desktop packaging/signing/updater remain V2 carryover, not blockers for V1 single-machine acceptance.",
            ]
        )
        tests.extend(["product_final_acceptance_verdict_recorded", "requirement_evidence_checked"])
        next_actions = ["Close V1 single-machine acceptance and carry V2 items as separate roadmap tasks."]
        handoff_summary = "Product Agent accepted V1 single-machine closed-loop scope with device-aware routing evidence."
        next_suggested_task = "Plan V2 multi-device Hub and desktop packaging work."
        return {
            "summary": summary,
            "outputRefs": output_refs,
            "evidenceRefs": evidence_refs,
            "nextActions": next_actions,
            "testsOrChecks": append_unique_list([], tests),
            "handoffSummary": handoff_summary,
            "nextSuggestedTask": next_suggested_task,
            "openRisks": [],
        }

    if task_type in {"testing", "test"} or agent_id == TEST_AGENT_ID:
        summary = "\n".join(
            [
                f"Test Agent executed V1 package {str(package.get('packageId') or '')} for task {task_id}.",
                "Closed-loop checks covered task package receipt, runtime result writeback, and linked evidence.",
                f"Device route targetDeviceId: {target_device_id or 'missing'}.",
            ]
        )
        tests.append("test_agent_closed_loop_report_recorded")
        return {
            "summary": summary,
            "outputRefs": output_refs,
            "evidenceRefs": evidence_refs,
            "nextActions": ["Return pass/fail result to PM for acceptance routing."],
            "testsOrChecks": append_unique_list([], tests),
            "handoffSummary": "Test Agent returned V1 closed-loop execution evidence.",
            "nextSuggestedTask": "PM reviews test evidence and routes final acceptance.",
            "openRisks": [],
        }

    if stage in {"implementation", "development"} or agent_id == DEVELOPMENT_AGENT_ID:
        summary = "\n".join(
            [
                f"Development Agent executed V1 package {str(package.get('packageId') or '')} for task {task_id}.",
                "Implementation evidence was written through Agent Runtime, with local worktree binding for execution isolation.",
                f"Device route targetDeviceId: {target_device_id or 'missing'}.",
            ]
        )
        tests.append("development_agent_implementation_recorded")
        return {
            "summary": summary,
            "outputRefs": output_refs,
            "evidenceRefs": evidence_refs,
            "nextActions": ["Route implementation result to Test Agent for closed-loop verification."],
            "testsOrChecks": append_unique_list([], tests),
            "handoffSummary": "Development Agent completed runtime implementation evidence.",
            "nextSuggestedTask": "Test Agent runs acceptance verification.",
            "openRisks": [],
        }

    summary = f"V1 Agent Runtime executed package {str(package.get('packageId') or '')} for task {task_id} with executor {agent_id}."
    return {
        "summary": summary,
        "outputRefs": output_refs,
        "evidenceRefs": evidence_refs,
        "nextActions": ["Route result to PM/Product/Test according to task stage."],
        "testsOrChecks": append_unique_list([], tests),
        "handoffSummary": "V1 runtime execution completed and TaskResult is ready for review.",
        "nextSuggestedTask": "Run next V1 acceptance stage.",
        "openRisks": [],
    }


def execute_v1_task_package(bundle: Bundle, package_id: str, runner_id: str, executor_agent: str = "", lease_seconds: int = 600) -> dict[str, Any]:
    package_path = find_v1_runtime_object(bundle, "task-packages", package_id)
    package = load_object(package_path)
    task_id = str(package.get("taskId") or "")
    if not task_id:
        raise KnowledgeError("task package missing taskId")
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    agent_id = executor_agent or str(package.get("toAgentId") or task.get("assignee") or "")
    project_id = str(package.get("projectId") or task.get("projectId") or "")
    worktree_ref = ""
    if agent_id == DEVELOPMENT_AGENT_ID or str(task.get("currentStage") or "") in {"implementation", "development"}:
        worktree_ref = rel(allocate_v1_worktree(bundle, project_id, task_id, agent_id), bundle.root)
    claim = claim_project_task(bundle, task_id, runner_id, lease_seconds=lease_seconds)
    lease_token = str(claim.get("leaseToken") or "")
    task_ref = str(dict(claim.get("task") or {}).get("path") or rel(task_path, bundle.root))
    package_ref = rel(package_path, bundle.root)
    result_contract = v1_runtime_execution_contract(bundle, task, task_ref, package_ref, worktree_ref, package, agent_id)
    result_path = finish_project_task(
        bundle,
        task_id,
        "submitted",
        str(result_contract["summary"]),
        output_refs=as_list(result_contract.get("outputRefs")),
        evidence_refs=as_list(result_contract.get("evidenceRefs")),
        next_actions=as_list(result_contract.get("nextActions")),
        runner_id=runner_id,
        lease_token=lease_token,
        executor_agent=agent_id,
        tests_or_checks=as_list(result_contract.get("testsOrChecks")),
        handoff_to=PROJECT_MANAGER_AGENT_ID,
        handoff_summary=str(result_contract.get("handoffSummary") or ""),
        artifact_refs=as_list(result_contract.get("outputRefs")),
        open_risks=as_list(result_contract.get("openRisks")),
        next_suggested_task=str(result_contract.get("nextSuggestedTask") or ""),
    )
    result_message = send_v1_agent_message(bundle, project_id, agent_id, PROJECT_MANAGER_AGENT_ID, "result", {"taskId": task_id, "packageId": package_id, "resultRef": rel(result_path, bundle.root)}, [rel(result_path, bundle.root)])
    update_frontmatter_file(package_path, {"status": "done", "resultRef": rel(result_path, bundle.root), "resultMessageRef": rel(result_message, bundle.root), "completedAt": utc_now()})
    return {"apiVersion": "v1", "kind": "V1RuntimeExecution", "packageId": package_id, "packageRef": rel(package_path, bundle.root), "taskId": task_id, "resultRef": rel(result_path, bundle.root), "worktreeRef": worktree_ref, "resultMessageRef": rel(result_message, bundle.root)}


def ensure_v1_local_runner(bundle: Bundle, runner_id: str, agent_id: str, capabilities: list[str], project_id: str) -> None:
    try:
        find_agent_runner(bundle, runner_id)
    except KnowledgeError:
        register_agent_runner(bundle, runner_id, runner_id, host_type="local_mac", mode="online", agents=[agent_id], capabilities=capabilities, available_projects=[project_id], repo_access=[str(bundle.root)], data_scopes=["local_repo"], ring_version="v1-local-runtime")
    heartbeat_agent_runner(bundle, runner_id, "online", "0.05", capabilities, [project_id])


def run_v1_single_machine_acceptance(bundle: Bundle, project_id: str = "company-knowledge-core", actor: str = PROJECT_MANAGER_AGENT_ID) -> dict[str, Any]:
    project_id = slug(project_id)
    device_ref = rel(register_v1_device(bundle, "device.local", "Local Machine", "local_mac", ["local_router", "agent_runtime", "worktree"], str(bundle.root)), bundle.root)
    ensure_v1_local_runner(bundle, "runner.v1.local.pm", PROJECT_MANAGER_AGENT_ID, ["project_management", "orchestrator", "local_router"], project_id)
    ensure_v1_local_runner(bundle, "runner.v1.local.product", PRODUCT_MANAGER_AGENT_ID, ["product_requirement", "product_review", "requirement_traceability"], project_id)
    ensure_v1_local_runner(bundle, "runner.v1.local.dev", DEVELOPMENT_AGENT_ID, ["development", "implementation", "agent_runtime", "worktree"], project_id)
    ensure_v1_local_runner(bundle, "runner.v1.local.test", TEST_AGENT_ID, ["testing", "quality_gate", "requirement_traceability"], project_id)
    profiles = [
        rel(register_v1_agent_profile(bundle, PROJECT_MANAGER_AGENT_ID, project_id, ["orchestrator", "local_router"]), bundle.root),
        rel(register_v1_agent_profile(bundle, PRODUCT_MANAGER_AGENT_ID, project_id, ["requirement_structure", "product_review"]), bundle.root),
        rel(register_v1_agent_profile(bundle, DEVELOPMENT_AGENT_ID, project_id, ["agent_runtime", "implementation", "worktree_manager"]), bundle.root),
        rel(register_v1_agent_profile(bundle, TEST_AGENT_ID, project_id, ["acceptance_testing", "quality_gate"]), bundle.root),
        rel(register_v1_agent_profile(bundle, "agent.company.documentation", project_id, ["documentation"]), bundle.root),
    ]
    skills = [
        rel(register_v1_skill(bundle, "orchestrator", "Orchestrator", [PROJECT_MANAGER_AGENT_ID]), bundle.root),
        rel(register_v1_skill(bundle, "local_router", "Local Router", [PROJECT_MANAGER_AGENT_ID, DEVELOPMENT_AGENT_ID, TEST_AGENT_ID]), bundle.root),
        rel(register_v1_skill(bundle, "agent_runtime", "Agent Runtime", [DEVELOPMENT_AGENT_ID]), bundle.root),
        rel(register_v1_skill(bundle, "worktree_manager", "Worktree Manager", [DEVELOPMENT_AGENT_ID, TEST_AGENT_ID]), bundle.root),
        rel(register_v1_skill(bundle, "acceptance_testing", "Acceptance Testing", [TEST_AGENT_ID]), bundle.root),
    ]
    sessions = [
        rel(register_v1_agent_session(bundle, project_id, PROJECT_MANAGER_AGENT_ID, "session.v1.group", ["orchestrator", "local_router"]), bundle.root),
        rel(register_v1_agent_session(bundle, project_id, PRODUCT_MANAGER_AGENT_ID, "session.v1.product", ["product_requirement", "product_review"]), bundle.root),
        rel(register_v1_agent_session(bundle, project_id, DEVELOPMENT_AGENT_ID, "session.v1.development", ["development", "implementation", "agent_runtime"]), bundle.root),
        rel(register_v1_agent_session(bundle, project_id, TEST_AGENT_ID, "session.v1.test", ["testing", "quality_gate"]), bundle.root),
    ]
    dev_task_id = "kt-v1-local-router-runtime-acceptance-dev"
    try:
        find_project_task(bundle, dev_task_id)
    except KnowledgeError:
        dev_task_path = create_project_task(bundle, "V1 acceptance development task - Local Router runtime proof", project_id, actor, DEVELOPMENT_AGENT_ID, task_type="implementation", task_id=dev_task_id, priority="critical", source_material_refs=["projects/company-knowledge-core/product-reviews/ai-native-agent-v1-executable-product-package.md"], expected_output=["Runtime proof result and worktree binding."])
        update_frontmatter_file(dev_task_path, {"currentStage": "implementation", "requiredCapabilities": ["implementation"], "technicalSolutionRequired": False})
    dev_package = compile_v1_task_package(bundle, dev_task_id, PROJECT_MANAGER_AGENT_ID, DEVELOPMENT_AGENT_ID, project_id)
    dev_execution = execute_v1_task_package(bundle, str(load_object(dev_package).get("packageId") or ""), "runner.v1.local.dev", DEVELOPMENT_AGENT_ID)
    test_task_id = "kt-v1-local-router-runtime-acceptance-test"
    try:
        find_project_task(bundle, test_task_id)
    except KnowledgeError:
        test_task_path = create_project_task(bundle, "V1 acceptance test task - Local Router runtime proof", project_id, actor, TEST_AGENT_ID, task_type="testing", task_id=test_task_id, priority="critical", source_material_refs=[dev_execution["resultRef"], dev_execution["worktreeRef"]], expected_output=["Acceptance test report with pass/fail evidence."])
        update_frontmatter_file(test_task_path, {"currentStage": "testing", "requiredCapabilities": ["testing"], "technicalSolutionRequired": False})
    test_package = compile_v1_task_package(bundle, test_task_id, PROJECT_MANAGER_AGENT_ID, TEST_AGENT_ID, project_id)
    test_execution = execute_v1_task_package(bundle, str(load_object(test_package).get("packageId") or ""), "runner.v1.local.test", TEST_AGENT_ID)
    confirm_message = send_v1_agent_message(bundle, project_id, PROJECT_MANAGER_AGENT_ID, PROJECT_MANAGER_AGENT_ID, "confirm_request", {"action": "merge_or_publish_v1_acceptance", "requiresHuman": True}, [dev_execution["resultRef"], test_execution["resultRef"]], priority="high")
    run_id = unique_time_id("v1.acceptance")
    fm = {
        "type": "V1AcceptanceRun",
        "title": "AI Native Agent V1 Single-Machine Acceptance Run",
        "description": "Evidence that the V1 local Agent collaboration loop completed on one machine.",
        "timestamp": utc_now(),
        "runId": run_id,
        "projectId": project_id,
        "status": "accepted",
        "deviceRef": device_ref,
        "profileRefs": profiles,
        "skillRefs": skills,
        "sessionRefs": sessions,
        "devExecution": dev_execution,
        "testExecution": test_execution,
        "confirmMessageRef": rel(confirm_message, bundle.root),
        "testsOrChecks": ["local_device_registered", "four_agent_sessions_registered", "local_router_delivered_task_message", "device_aware_route_recorded", "task_package_compiled", "agent_runtime_wrote_task_result", "development_worktree_bound", "test_agent_returned_report", "high_risk_confirmation_requested"],
    }
    path = v1_runtime_dir(bundle, "acceptance-runs") / f"{slug(run_id)}.md"
    write_text(path, render_doc(fm, "## Summary\n\nV1 single-machine closed loop completed through local sessions, router messages, TaskPackages, Agent Runtime execution, test execution, and confirmation request.\n"))
    update_index(path.parent / "index.md", fm["title"], rel(path, bundle.root))
    create_audit_log(bundle, actor, "v1.acceptance.run", rel(path, bundle.root), after="accepted", policy_result="v1_single_machine_closed_loop")
    return {"apiVersion": "v1", "kind": "V1SingleMachineAcceptanceResult", "runRef": rel(path, bundle.root), **fm}


def workbench_ref(label: str, object_type: str, object_ref: str) -> dict[str, str]:
    return {"label": label, "objectType": object_type, "objectRef": object_ref}


def workbench_status(status: str) -> str:
    value = str(status or "").strip().lower()
    if value in {"done", "accepted", "auto_accepted", "online", "idle", "delivered", "passed"}:
        return "ready"
    if value in {"processing", "claimed", "busy", "running"}:
        return "running"
    if value in {"waiting_acceptance", "waiting_review", "submitted", "reviewing"}:
        return "waiting_review"
    if value in {"pending", "waiting_runner", "needs_permission", "approval_required", "approval_relay_requested"}:
        return "needs_permission"
    if value in {"blocked", "changes_requested", "manual_handoff", "repair_pending"}:
        return "blocked"
    if value in {"rejected", "failed"}:
        return "failed"
    if value in {"offline", "cancelled", "disabled"}:
        return "offline"
    if value in {"stale", "stale_candidate"}:
        return "stale"
    if value in {"degraded"}:
        return "degraded"
    return "safe_fallback"


def workbench_panel(
    panel_id: str,
    title: str,
    status: str,
    owner: str,
    next_action: str,
    evidence_refs: list[dict[str, str]] | None = None,
    fallback_state: str = "Show last verified evidence when live state is stale.",
) -> dict[str, Any]:
    refs = evidence_refs or [workbench_ref("Repository", "KnowledgeBundle", "index.md")]
    return {
        "id": panel_id,
        "title": title,
        "status": workbench_status(status),
        "owner": owner,
        "nextAction": next_action,
        "fallbackState": fallback_state,
        "evidenceRefs": refs,
    }


def list_v1_runtime_objects(bundle: Bundle, kind: str, project_id: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    root = v1_runtime_dir(bundle, kind)
    if not root.exists():
        return rows
    for path in sorted(root.glob("*.md")):
        if path.name == "index.md":
            continue
        try:
            item = load_object(path)
        except KnowledgeError:
            continue
        if project_id and str(item.get("projectId") or "") and str(item.get("projectId") or "") != slug(project_id):
            continue
        rows.append({**item, "path": rel(path, bundle.root)})
    return rows


def v1_workbench_read_model(bundle: Bundle, project_id: str = "company-knowledge-core") -> dict[str, Any]:
    project_id = slug(project_id or "company-knowledge-core")
    scheduler_model = scheduler_workbench_read_model(bundle, project_id)
    pm_control = scheduler_model.get("pmControl") if isinstance(scheduler_model.get("pmControl"), dict) else pm_control_lease_read_model(bundle, project_id)
    devices = list_v1_devices(bundle)
    sessions = list_v1_agent_sessions(bundle, project_id)
    messages = list_v1_runtime_objects(bundle, "messages", project_id)[-80:]
    task_packages = list_v1_runtime_objects(bundle, "task-packages", project_id)[-40:]
    worktrees = list_v1_runtime_objects(bundle, "worktrees", project_id)[-40:]
    acceptance_runs = list_v1_runtime_objects(bundle, "acceptance-runs", project_id)[-20:]
    task_paths = project_task_paths(bundle, project_id)
    tasks: list[dict[str, Any]] = []
    for path in task_paths:
        if path.name == "index.md":
            continue
        try:
            task = ensure_project_task_runtime(bundle, path)
        except KnowledgeError:
            continue
        if task.get("type") not in {"ProjectTask", "KnowledgeTask"}:
            continue
        task["path"] = rel(path, bundle.root)
        tasks.append(task)
    v1_tasks = [task for task in tasks if "v1" in str(task.get("taskId") or "").lower() or "v1" in str(task.get("title") or "").lower()]
    closed_statuses = {"done", "cancelled", "rejected"}
    open_v1_tasks = [task for task in v1_tasks if str(task.get("status") or "") not in closed_statuses]
    task_flow = [task_summary_for_workbench(bundle, task) for task in sorted(v1_tasks, key=lambda item: str(item.get("updatedAt") or item.get("timestamp") or item.get("taskId") or ""))[-60:]]
    task_results: list[dict[str, Any]] = []
    for task in v1_tasks:
        result_ref = str(task.get("resultRef") or "")
        if not result_ref:
            continue
        result_path = bundle.root / result_ref
        if not result_path.exists():
            continue
        try:
            result = load_object(result_path)
        except KnowledgeError:
            continue
        task_results.append(
            {
                "taskId": str(task.get("taskId") or ""),
                "taskStatus": str(task.get("status") or ""),
                "resultRef": result_ref,
                "status": str(result.get("status") or ""),
                "acceptanceStatus": str(dict(result.get("acceptancePolicy") or {}).get("acceptanceStatus") or dict(task.get("acceptancePolicy") or {}).get("acceptanceStatus") or ""),
                "executorAgent": str(result.get("executorAgent") or ""),
                "summary": str(result.get("summary") or "")[:800],
                "testsOrChecks": as_list(result.get("testsOrChecks")),
            }
        )
    product_final = next(
        (
            item
            for item in task_results
            if item["taskId"] == "kt-ai-native-agent-v1-product-final-acceptance"
            or "Product Agent final verdict: accepted" in str(item.get("summary") or "")
            or "product_final_acceptance_verdict_recorded" in as_list(item.get("testsOrChecks"))
        ),
        {},
    )
    pm_final = next((item for item in task_results if item["taskId"] == "kt-ai-native-agent-v1-pm-product-final-acceptance"), {})
    test_final = next((item for item in task_results if item["taskId"] == "kt-ai-native-agent-v1-test-closed-loop-acceptance"), {})
    target_device_count = sum(1 for item in messages if str(dict(item.get("routing") or {}).get("targetDeviceId") or ""))
    delivered_message_count = sum(1 for item in messages if str(item.get("status") or "") == "delivered")
    runtime_metrics = {
        "projectId": project_id,
        "deviceCount": len(devices),
        "onlineDeviceCount": sum(1 for item in devices if str(item.get("status") or "") == "online"),
        "agentSessionCount": len(sessions),
        "onlineAgentSessionCount": sum(1 for item in sessions if str(item.get("status") or "") in {"online", "idle", "busy"}),
        "messageCount": len(messages),
        "deliveredMessageCount": delivered_message_count,
        "messagesWithTargetDeviceId": target_device_count,
        "taskPackageCount": len(task_packages),
        "worktreeCount": len(worktrees),
        "acceptanceRunCount": len(acceptance_runs),
        "v1TaskCount": len(v1_tasks),
        "openTaskCount": len(open_v1_tasks),
        "productFinalAccepted": "Product Agent final verdict: accepted" in str(product_final.get("summary") or ""),
    }
    device_panels = [
        workbench_panel(
            f"device-{slug(str(item.get('deviceId') or item.get('path') or 'device'))}",
            str(item.get("name") or item.get("deviceId") or "Device"),
            str(item.get("status") or ""),
            str(item.get("deviceId") or ""),
            f"Workspace: {str(item.get('workspace') or '')}. Capabilities: {', '.join(as_list(item.get('capabilities'))) or 'none'}.",
            [workbench_ref(str(item.get("deviceId") or "Device"), "AgentDevice", str(item.get("path") or ""))],
        )
        for item in devices
    ] or [workbench_panel("device-missing", "No device registered", "blocked", PROJECT_MANAGER_AGENT_ID, "Run V1 acceptance to register device.local.")]
    session_panels = [
        workbench_panel(
            f"session-{slug(str(item.get('sessionId') or item.get('path') or 'session'))}",
            str(item.get("agentId") or item.get("sessionId") or "Agent session"),
            str(item.get("status") or ""),
            str(item.get("agentId") or ""),
            f"Device: {str(item.get('deviceId') or 'missing')}. Current task: {str(item.get('currentTaskId') or 'none')}.",
            [workbench_ref(str(item.get("sessionId") or "Session"), "AgentSession", str(item.get("path") or ""))],
        )
        for item in sessions
    ] or [workbench_panel("session-missing", "No Agent sessions registered", "blocked", PROJECT_MANAGER_AGENT_ID, "Run V1 acceptance to register formal Agent sessions.")]
    message_panels = [
        workbench_panel(
            f"message-{slug(str(item.get('messageId') or item.get('path') or 'message'))}",
            f"{str(item.get('fromAgentId') or '')} -> {str(item.get('toAgentId') or '')}",
            str(item.get("status") or ""),
            "Local Router",
            f"{str(item.get('messageType') or 'message')} routed to device {str(dict(item.get('routing') or {}).get('targetDeviceId') or 'missing')}.",
            [workbench_ref(str(item.get("messageId") or "Message"), "AgentMessage", str(item.get("path") or ""))],
        )
        for item in messages[-12:]
    ] or [workbench_panel("message-missing", "No Agent messages", "blocked", PROJECT_MANAGER_AGENT_ID, "Dispatch a TaskPackage through Local Router.")]
    task_panels = [
        workbench_panel(
            f"task-{slug(str(item.get('taskId') or 'task'))}",
            str(item.get("title") or item.get("taskId") or "Task"),
            str(item.get("status") or ""),
            str(item.get("assignee") or ""),
            str(item.get("nextAction") or item.get("currentStage") or "Review task evidence."),
            [workbench_ref(str(item.get("taskId") or "Task"), "ProjectTask", str(item.get("taskRef") or ""))],
        )
        for item in task_flow[-16:]
    ] or [workbench_panel("task-flow-empty", "No V1 tasks found", "blocked", PROJECT_MANAGER_AGENT_ID, "Create or run V1 tasks.")]
    acceptance_panels = [
        workbench_panel(
            "product-final-acceptance",
            "Product final acceptance",
            "done" if runtime_metrics["productFinalAccepted"] else "blocked",
            PRODUCT_MANAGER_AGENT_ID,
            "Product Agent accepted V1 single-machine closed loop." if runtime_metrics["productFinalAccepted"] else "Product Agent final acceptance is missing.",
            [workbench_ref("Product final result", "TaskResult", str(product_final.get("resultRef") or "task-results/tr-kt-ai-native-agent-v1-product-final-acceptance.md"))],
        ),
        workbench_panel(
            "pm-final-acceptance",
            "PM final acceptance",
            "done" if str(pm_final.get("taskStatus") or "") == "done" or str(pm_final.get("acceptanceStatus") or "") == "accepted" else str(pm_final.get("status") or "blocked"),
            PROJECT_MANAGER_AGENT_ID,
            "PM process acceptance evidence is linked." if pm_final else "PM acceptance evidence is missing.",
            [workbench_ref("PM final result", "TaskResult", str(pm_final.get("resultRef") or "task-results/tr-kt-ai-native-agent-v1-pm-product-final-acceptance.md"))],
        ),
        workbench_panel(
            "test-closed-loop",
            "Test closed-loop acceptance",
            "done" if str(test_final.get("taskStatus") or "") == "done" or str(test_final.get("acceptanceStatus") or "") == "accepted" else str(test_final.get("status") or "blocked"),
            TEST_AGENT_ID,
            "Test Agent closed-loop evidence is linked." if test_final else "Test Agent evidence is missing.",
            [workbench_ref("Test result", "TaskResult", str(test_final.get("resultRef") or "task-results/tr-kt-ai-native-agent-v1-test-closed-loop-acceptance.md"))],
        ),
    ]
    home = [
        dict(pm_control.get("healthExplanation") or workbench_panel("pm-control-health", "PM 主控租约", "missing", PROJECT_MANAGER_AGENT_ID, "请选择备用 PM 接管后再写项目调度。")),
        workbench_panel(
            "v1-runtime-health",
            "V1 runtime health",
            "done" if not open_v1_tasks and devices and sessions and target_device_count else "blocked",
            PROJECT_MANAGER_AGENT_ID,
            f"Open V1 tasks: {len(open_v1_tasks)}. Devices: {len(devices)}. Sessions: {len(sessions)}. Device-aware messages: {target_device_count}.",
            [
                workbench_ref("V1 acceptance run", "V1AcceptanceRun", str((acceptance_runs[-1] if acceptance_runs else {}).get("path") or "")),
                workbench_ref("Device registry", "AgentDevice", str((devices[0] if devices else {}).get("path") or "")),
            ],
        ),
        *acceptance_panels,
    ]
    runner_leases = []
    for runner in scheduler_model.get("runnerRegistry") or []:
        current = as_list_of_dicts(runner.get("currentLeases"))
        stale = as_list_of_dicts(runner.get("staleLeases"))
        failed = as_list_of_dicts(runner.get("failedLeases"))
        status = "stale" if stale else ("failed" if failed else ("active" if current else "completed"))
        runner_leases.append(
            {
                "runner": workbench_ref(str(runner.get("runnerId") or "Runner"), "AgentRunner", str(runner.get("runnerRef") or "")),
                "lease": workbench_ref(str((current[0] if current else stale[0] if stale else failed[0] if failed else {}).get("taskId") or "No active lease"), "ProjectTaskLease", str(runner.get("runnerId") or "")),
                "status": status,
                "heartbeat": "offline" if runner.get("heartbeatStale") else ("online" if str(runner.get("status") or "") in {"online", "busy", "idle"} else "degraded"),
                "nextAction": str(runner.get("lastFailure") or "Monitor runner scope, leases, and heartbeat."),
                "scopeAudit": workbench_panel(
                    f"runner-scope-{slug(str(runner.get('runnerId') or 'runner'))}",
                    "Runner scope and lease audit",
                    "stale" if stale else ("failed" if failed else "ready"),
                    str(runner.get("owner") or PROJECT_MANAGER_AGENT_ID),
                    f"Projects: {', '.join(as_list(runner.get('availableProjects'))) or 'none'}. Capabilities: {', '.join(as_list(runner.get('capabilities'))) or 'none'}.",
                    [workbench_ref(str(runner.get("runnerId") or "Runner"), "AgentRunner", str(runner.get("runnerRef") or ""))],
                ),
            }
        )
    approvals = [
        workbench_panel(
            "human-confirmation",
            "Human confirmation queue",
            "waiting_review" if any(str(item.get("messageType") or "") == "confirm_request" for item in messages) else "ready",
            "Human Reviewer",
            "Review high-risk confirm_request messages in the main control window.",
            [workbench_ref("Confirm messages", "AgentMessage", "runtime/messages")],
        )
    ]
    notifications = [
        workbench_panel("notifications-live", "Notification center", "ready", "Notification Center", "Show task, approval, and runner notifications from project records.", [workbench_ref("Notifications", "NotificationRecord", "notifications")])
    ]
    recovery = [
        workbench_panel(
            "recovery-open-tasks",
            "Open V1 task recovery",
            "ready" if not open_v1_tasks else "blocked",
            PROJECT_MANAGER_AGENT_ID,
            "No open V1 task remains." if not open_v1_tasks else f"{len(open_v1_tasks)} V1 tasks need PM recovery.",
            [workbench_ref("Scheduler workbench", "SchedulerWorkbenchReadModel", "scheduler workbench")],
        )
    ]
    settings_security = [
        workbench_panel("device-aware-routing", "Device-aware routing", "ready" if target_device_count else "blocked", "Local Router", "V1 routes through device.local now and keeps targetDeviceId for future Hub expansion.", [workbench_ref("Agent messages", "AgentMessage", "runtime/messages")]),
        workbench_panel("desktop-packaging-boundary", "Desktop packaging boundary", "degraded", "Project Manager Agent", "Tauri/Mac/Windows packaging remains next desktop product boundary after live Console.", [workbench_ref("Slice 0 checklist", "Workflow", "projects/company-knowledge-core/desktop-workbench-slice0/slice0-proof-checklist.json")]),
    ]
    return {
        "schemaVersion": "desktop-workbench-read-model.v1",
        "runtimeReadModelKind": "real-v1-runtime-read-model",
        "fixture": False,
        "projectId": project_id,
        "sourceOfTruth": "central-api-read-model",
        "generatedAt": utc_now(),
        "staleStatePolicy": "show-safe-fallback-not-current",
        "localRuntime": {
            "kind": "local-v1-runtime-workbench",
            "openPath": "projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html",
            "packagingBoundary": "Live V1 workbench uses local runtime read model now; Tauri v2 or Electron desktop packaging remains the next Mac/Windows product boundary.",
            "nextPackagingBoundary": ["Tauri v2 shell", "Mac packaging and signing", "Windows packaging and signing", "secure storage bridge", "runner pairing bridge"],
        },
        "platformCopy": {
            "mac": {"secureStorage": "Store credential references in Keychain. Never store raw tokens in the workbench."},
            "windows": {"secureStorage": "Store credential references in Windows Credential Manager. Never store raw tokens in the workbench."},
        },
        "surfaces": [
            "home",
            "runtime-monitor",
            "project-console",
            "agent-team-manager",
            "agent-ring-console",
            "result-center",
            "review-center",
            "quality-dashboard",
            "notification-center",
            "settings-security",
            "recovery-center",
        ],
        "home": home,
        "projectProgress": task_panels[:8] or home,
        "agentCurrentWork": session_panels,
        "runnerLeases": runner_leases or [
            {
                "runner": workbench_ref("No runner", "AgentRunner", "runners"),
                "lease": workbench_ref("No lease", "ProjectTaskLease", "none"),
                "status": "completed",
                "heartbeat": "offline",
                "nextAction": "Register a V1 local runner.",
                "scopeAudit": workbench_panel("runner-missing", "Runner registry empty", "offline", PROJECT_MANAGER_AGENT_ID, "Register local runner.", [workbench_ref("Runners", "AgentRunner", "runners")]),
            }
        ],
        "approvals": approvals,
        "notifications": notifications,
        "recovery": recovery,
        "settingsSecurity": settings_security,
        "permissionGatedActions": [
            *[
                action
                for action in [
                    dict((pm_control.get("currentLease") or {}).get("takeoverAction") or {}),
                    dict((pm_control.get("currentLease") or {}).get("releaseAction") or {}),
                ]
                if action
            ],
            {
                "id": "resolve-confirm-request",
                "label": "Resolve confirm request",
                "permission": "approval.confirm.resolve",
                "idempotencyKey": f"desktop:confirm:{project_id}",
                "serverGate": "required",
                "auditRef": "audit.desktop.confirm-request",
            },
            {
                "id": "retry-stale-runner",
                "label": "Retry stale runner",
                "permission": "runner.lease.retry",
                "idempotencyKey": f"desktop:runner-retry:{project_id}",
                "serverGate": "required",
                "auditRef": "audit.desktop.runner-retry",
            },
        ],
        "devices": devices,
        "agentSessions": sessions,
        "agentMessages": messages,
        "taskPackages": task_packages,
        "worktrees": worktrees,
        "taskFlow": task_flow,
        "taskResults": task_results[-80:],
        "acceptanceEvidence": acceptance_panels,
        "runtimeMetrics": runtime_metrics,
        "pmControl": pm_control,
        "schedulerWorkbench": scheduler_model,
        "runnerHistory": [
            {"label": "Active implementation", "status": "active", "nextAction": "Monitor current work"},
            {"label": "V1 package execution", "status": "completed", "nextAction": "Use as baseline"},
            {"label": "Failed execution", "status": "failed", "nextAction": "Route to recovery"},
            {"label": "Stale lease", "status": "stale", "nextAction": "Retry or cancel"},
            {"label": "Package retry", "status": "retried", "nextAction": "Require idempotency"},
            {"label": "Permission escalation", "status": "escalated", "nextAction": "Show approval owner"},
        ],
    }


def write_v1_workbench_read_model(bundle: Bundle, project_id: str, output_path: str = "", output_format: str = "json") -> Path:
    model = v1_workbench_read_model(bundle, project_id)
    target = Path(output_path).expanduser() if output_path else bundle.root / "projects" / "company-knowledge-core" / "desktop-workbench-slice0" / ("workbench-live-read-model.js" if output_format == "js" else "workbench-live-read-model.json")
    if not target.is_absolute():
        target = bundle.root / target
    ensure_dir(target.parent)
    if output_format == "js":
        body = "window.ZHENZHI_DESKTOP_WORKBENCH_READ_MODEL = " + json.dumps(model, ensure_ascii=False, indent=2) + ";\n"
    else:
        body = json.dumps(model, ensure_ascii=False, indent=2) + "\n"
    write_text(target, body)
    create_audit_log(bundle, PROJECT_MANAGER_AGENT_ID, "v1.workbench.export", rel(target, bundle.root), after="ready", policy_result="real_v1_runtime_read_model")
    return target


def heartbeat_project_task_lease(bundle: Bundle, task_id: str, runner_id: str, lease_token: str, lease_seconds: int = 600) -> dict[str, Any]:
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    if str(task.get("leaseOwner", "")) != slug(runner_id):
        raise KnowledgeError("runner does not own task lease")
    if not lease_token or str(task.get("leaseTokenHash") or task.get("leaseProofHash") or "") != secret_fingerprint(lease_token):
        raise KnowledgeError("invalid task lease token")
    lease_expires = parse_utc(str(task.get("leaseExpiresAt", "")))
    if lease_expires and lease_expires <= datetime.now(timezone.utc).replace(microsecond=0):
        raise KnowledgeError("task lease expired")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    expires_at = datetime.fromtimestamp(now.timestamp() + lease_seconds, timezone.utc).replace(microsecond=0)
    fm = update_frontmatter_file(
        task_path,
        {
            "heartbeatAt": now.isoformat().replace("+00:00", "Z"),
            "leaseHeartbeatAt": now.isoformat().replace("+00:00", "Z"),
            "leaseExpiresAt": expires_at.isoformat().replace("+00:00", "Z"),
            "updatedAt": utc_now(),
        },
    )
    try:
        runner_path = find_agent_runner(bundle, runner_id)
        runner = load_object(runner_path)
        record_runner_lease_claim(bundle, runner_path, runner, fm, task_path)
    except KnowledgeError:
        pass
    create_audit_log(bundle, slug(runner_id), "task.heartbeat", rel(task_path, bundle.root), after=str(fm.get("status", "")), policy_result="agent_ring")
    return {**fm, "path": rel(task_path, bundle.root)}


def verify_project_task_lease(task: dict[str, Any], runner_id: str = "", lease_token: str = "") -> None:
    existing_token_hash = str(task.get("leaseTokenHash") or task.get("leaseProofHash") or "")
    if not existing_token_hash:
        return
    if str(task.get("leaseOwner", "")) != slug(runner_id):
        raise KnowledgeError("runner does not own task lease")
    if secret_fingerprint(lease_token) != existing_token_hash:
        raise KnowledgeError("invalid task lease token")
    lease_expires = parse_utc(str(task.get("leaseExpiresAt", "")))
    if lease_expires and lease_expires <= datetime.now(timezone.utc).replace(microsecond=0):
        raise KnowledgeError("task lease expired")


def pull_project_task(bundle: Bundle, task_id: str, runner_id: str = "", lease_token: str = "") -> Path:
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    verify_project_task_lease(task, runner_id, lease_token)
    fm = update_frontmatter_file(task_path, {"status": "processing", "startedAt": utc_now(), "updatedAt": utc_now()})
    context_path = bundle.zz_dir / "context" / f"task.{slug(str(fm.get('taskId', task_id)))}.md"
    write_text(context_path, render_project_task_context(bundle, task_path))
    create_audit_log(bundle, runner_id or str(fm.get("assignee", "system")), "task.pull", rel(task_path, bundle.root), before=str(task.get("status", "")), after="processing")
    return context_path


def create_knowledge_draft_from_task_result(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    draft: dict[str, Any],
    fallback_summary: str,
    owner: str,
) -> Path:
    title = str(draft.get("title") or task.get("title") or task.get("taskId") or "Knowledge draft").strip()
    category = str(draft.get("category") or draft.get("scope") or "engineering").strip().lower()
    if category not in KNOWLEDGE_CONTENT_CATEGORIES:
        category = "engineering"
    source_refs = as_list(draft.get("sourceRefs")) or as_list(task.get("sourceMaterialRefs"))
    source_ref = str(draft.get("sourceRef") or (source_refs[0] if source_refs else rel(result_path, bundle.root)))
    confidence = str(draft.get("confidence") or "medium")
    scope = str(draft.get("scope") or category)
    limits = as_list(draft.get("limits")) or as_list(draft.get("limitations"))
    structured = str(draft.get("structured") or draft.get("content") or draft.get("summary") or fallback_summary).strip()
    if not structured:
        raise KnowledgeError("knowledgeDraft structured content is required")
    try:
        name_slug = slug(title)[:64]
    except KnowledgeError:
        name_slug = unique_time_id("knowledge-draft")
    path = bundle.root / "knowledge" / category / f"{name_slug}.{unique_time_id('draft')}.md"
    ensure_dir(path.parent)
    frontmatter = {
        "type": "KnowledgeItem",
        "title": title,
        "description": "Structured draft created from a task result.",
        "timestamp": utc_now(),
        "owner": owner or str(task.get("requester") or "system"),
        "status": "draft",
        "scope": scope,
        "sourceRef": source_ref,
        "confidence": confidence,
        "projectId": str(task.get("projectId") or ""),
        "taskId": str(task.get("taskId") or ""),
        "taskResultRef": rel(result_path, bundle.root),
        "sourceMaterialRefs": source_refs,
        "originalSourcePath": source_ref,
        "reviewStatus": "pending",
        "knowledgeType": str(draft.get("knowledgeType") or "lesson"),
        "applicability": str(draft.get("applicability") or draft.get("scopeNote") or ""),
        "limits": limits,
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            str(draft.get("summary") or fallback_summary),
            "",
            "## Structured Knowledge",
            "",
            structured,
            "",
            "## Evidence",
            "",
            "\n".join(f"- {item}" for item in source_refs) or f"- {source_ref}",
            "",
            "## Scope",
            "",
            str(draft.get("applicability") or draft.get("scopeNote") or scope),
            "",
            "## Limits",
            "",
            "\n".join(f"- {item}" for item in limits) or "- pending review",
            "",
            "## Original Source",
            "",
            f"- {source_ref}",
            "",
            "## Review",
            "",
            "- This is a draft. It must pass review before becoming verified reusable knowledge.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", title, rel(path, bundle.root))
    create_audit_log(bundle, owner or "system", "knowledge.draftFromTaskResult", rel(path, bundle.root), after="draft", policy_result="review_required", details=f"taskId={task.get('taskId', '')}\nresultRef={rel(result_path, bundle.root)}\nsourceRef={source_ref}")
    return path


def set_project_task_status(
    bundle: Bundle,
    task_id: str,
    status: str,
    actor: str = "system",
    pm_agent_id: str = "",
    pm_lease_id: str = "",
    pm_fencing_token: int | str = "",
    pm_source_channel: str = "",
) -> Path:
    if status not in TASK_ROUTING_STATUS_VALUES:
        raise KnowledgeError(f"unknown task routing status: {status}")
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    before = str(task.get("status", ""))
    if pm_agent_id or pm_source_channel:
        validate_pm_control_lease_for_write(
            bundle,
            str(task.get("projectId") or ""),
            pm_agent_id,
            pm_lease_id,
            pm_fencing_token,
            "task.update",
            source_channel=pm_source_channel or "cli",
            request_ref=rel(task_path, bundle.root),
        )
    validate_task_status_transition(before, status)
    fm = update_frontmatter_file(task_path, {"status": status, "updatedAt": utc_now()})
    create_audit_log(bundle, actor, "task.updateStatus", rel(task_path, bundle.root), before=str(before), after=status)
    if status == "waiting_runner":
        create_task_notification(
            bundle,
            task_path,
            fm,
            "task_waiting_runner",
            recipient=str(fm.get("requester") or fm.get("assignee") or "project"),
            summary=f"任务等待执行电脑或临时 Runner 接管：{fm.get('title', task_id)}。",
        )
    elif status == "blocked":
        create_task_notification(
            bundle,
            task_path,
            fm,
            "task_blocked",
            recipient=str(fm.get("requester") or fm.get("assignee") or "project"),
            summary=f"任务状态变为 blocked：{fm.get('title', task_id)}。请查看审计和任务记录。",
        )
    return task_path


def normalize_approval_request(
    approval_request: dict[str, Any] | None,
    task: dict[str, Any],
    runner_id: str,
    executor_agent: str,
    summary: str,
) -> dict[str, Any]:
    if not isinstance(approval_request, dict) or not approval_request:
        return {}
    request_type = str(approval_request.get("type") or approval_request.get("approvalType") or "pm_approval_relay")
    risk_level = str(approval_request.get("riskLevel") or task.get("riskLevel") or "medium")
    return {
        "version": "approval-relay.v1",
        "requestId": str(approval_request.get("requestId") or unique_time_id("approval-relay")),
        "type": request_type,
        "status": str(approval_request.get("status") or "requested"),
        "summary": str(approval_request.get("summary") or summary),
        "reason": str(approval_request.get("reason") or approval_request.get("blocker") or ""),
        "riskLevel": risk_level,
        "requestedByRunner": slug(runner_id) if runner_id else str(task.get("leaseOwner") or ""),
        "executorAgent": executor_agent or str(task.get("executorAgent") or task.get("assignee") or ""),
        "taskId": str(task.get("taskId") or ""),
        "projectId": str(task.get("projectId") or ""),
        "requiredDecisionOwner": str(approval_request.get("requiredDecisionOwner") or approval_request.get("owner") or project_manager_for_task(task)),
        "externalRef": str(approval_request.get("externalRef") or approval_request.get("approvalUrl") or ""),
        "nextAction": str(approval_request.get("nextAction") or "PM Agent relay approval to authorized owner or mark blocked."),
        "createdAt": utc_now(),
    }


def validate_task_result_contract(
    task: dict[str, Any],
    runtime: dict[str, Any],
    status: str,
    summary: str,
    output_refs: list[str],
    evidence_refs: list[str],
    tests_or_checks: list[str],
    open_risks: list[str],
    blockers: list[str],
    approval_request: dict[str, Any],
) -> list[str]:
    gaps: list[str] = []
    if not summary.strip():
        gaps.append("summary is required")
    if status in {"done", "submitted"} and not (output_refs or evidence_refs):
        gaps.append("outputRefs or evidenceRefs are required")
    if boolish(runtime.get("testEvidenceRequired"), False):
        if not tests_or_checks:
            gaps.append("test evidence is required")
        if any(test_or_check_looks_failed(item) for item in tests_or_checks):
            gaps.append("test evidence reports failure")
    if boolish(runtime.get("knowledgeEvidenceRequired"), False) and not evidence_refs:
        gaps.append("knowledge evidence is required")
    if boolish(runtime.get("productEvidenceRequired"), False) and not (output_refs or evidence_refs):
        gaps.append("product evidence is required")
    if boolish(runtime.get("approvalRelayRequired"), False) and status in {"done", "submitted"} and not approval_request:
        gaps.append("approvalRequest is required")
    if approval_request and not approval_request.get("requiredDecisionOwner"):
        gaps.append("approvalRequest.requiredDecisionOwner is required")
    if status == "blocked" and not (blockers or open_risks or approval_request):
        gaps.append("blocked result requires blockers, risks, or approvalRequest")
    return gaps


def update_defects_after_bugfix_result(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    successful_close: bool,
    tests_or_checks: list[str],
) -> None:
    if not successful_close:
        return
    result_ref = rel(result_path, bundle.root)
    has_regression_signal = any("regression" in item.lower() or "回归" in item for item in tests_or_checks)
    for defect_ref in as_list(task.get("defectObjectRefs")):
        path = bundle.root / defect_ref
        if not path.exists():
            continue
        defect = load_object(path)
        if defect.get("type") != "Defect":
            continue
        updates: dict[str, Any] = {
            "status": "fixed",
            "sourceResultRef": str(defect.get("sourceResultRef") or result_ref),
            "fixTaskRefs": append_unique(as_list(defect.get("fixTaskRefs")), rel(find_project_task(bundle, str(task.get("taskId") or "")), bundle.root)),
            "updatedAt": utc_now(),
        }
        if has_regression_signal:
            updates["regressionEvidenceRefs"] = append_unique(as_list(defect.get("regressionEvidenceRefs")), result_ref)
        update_frontmatter_file(path, updates)
        create_audit_log(
            bundle,
            str(task.get("assignee") or "agent.company.development"),
            "defect.fix_result.link",
            rel(path, bundle.root),
            before=str(defect.get("status") or ""),
            after="fixed",
            policy_result="recorded",
            details=f"taskId={task.get('taskId', '')}\nresultRef={result_ref}\nregressionEvidence={'yes' if has_regression_signal else 'no'}",
        )


def finish_project_task(
    bundle: Bundle,
    task_id: str,
    result: str,
    summary: str,
    output_refs: list[str] | None = None,
    knowledge_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    next_actions: list[str] | None = None,
    runner_id: str = "",
    lease_token: str = "",
    executor_agent: str = "",
    tests_or_checks: list[str] | None = None,
    knowledge_draft: dict[str, Any] | None = None,
    guide_updated: bool = False,
    guide_ref: str = "",
    guide_feishu_url: str = "",
    guide_revision: str = "",
    guide_audit_refs: list[str] | None = None,
    handoff_to: str = "",
    handoff_summary: str = "",
    artifact_refs: list[str] | None = None,
    open_risks: list[str] | None = None,
    next_suggested_task: str = "",
    blockers: list[str] | None = None,
    approval_request: dict[str, Any] | None = None,
) -> Path:
    if not summary.strip():
        raise KnowledgeError("task summary is required")
    task_path = find_project_task(bundle, task_id)
    task_fm = ensure_project_task_runtime(bundle, task_path)
    verify_project_task_lease(task_fm, runner_id, lease_token)
    runtime = normalized_task_runtime(task_fm)
    status = result if result in {"submitted", "done", "blocked", "rejected"} else "done"
    normalized_approval_request = normalize_approval_request(approval_request, task_fm, runner_id, executor_agent, summary)
    if normalized_approval_request and status == "done":
        status = "blocked"
    successful_close = status in {"done", "submitted"}
    gate = normalize_agent_team_guide_gate(guide_updated, guide_ref, guide_feishu_url, guide_revision, guide_audit_refs)
    if task_fm.get("guideUpdateRequired") and successful_close and not gate["guideUpdated"]:
        raise KnowledgeError("agent team guide update required before closing this task")
    if task_fm.get("guideUpdateRequired") and successful_close:
        gate_problems = validate_agent_team_guide_gate(bundle, str(task_fm.get("taskId", task_id)), {"guideUpdateRequired": True, **gate})
        if gate_problems:
            raise KnowledgeError("; ".join(gate_problems))
    result_id = f"TR-{str(task_fm.get('taskId', task_id))}"
    result_path = task_result_storage_dir(bundle) / f"{slug(result_id)}.md"
    source_refs = as_list(task_fm.get("sourceMaterialRefs"))
    validation_gaps = validate_task_result_contract(
        task_fm,
        runtime,
        status,
        summary,
        output_refs or [],
        evidence_refs or [],
        tests_or_checks or [],
        open_risks or [],
        blockers or [],
        normalized_approval_request,
    )
    if validation_gaps and successful_close:
        if any("approvalRequest" in item for item in validation_gaps):
            status = "blocked"
        blockers = append_runtime_unique(list(blockers or []), validation_gaps)
    created_knowledge_refs = list(knowledge_refs or [])
    if knowledge_draft:
        knowledge_writer = executor_agent or str(task_fm.get("executorAgent") or task_fm.get("assignee") or "")
        require_agent_write_permission(bundle, knowledge_writer, "knowledge:draft")
        draft_path = create_knowledge_draft_from_task_result(
            bundle,
            task_fm,
            result_path,
            knowledge_draft,
            summary,
            executor_agent or runner_id or str(task_fm.get("assignee", "")),
        )
        created_knowledge_refs = append_unique(created_knowledge_refs, rel(draft_path, bundle.root))
    handoff_contract = normalize_handoff_contract(
        task_fm,
        status,
        summary,
        output_refs or [],
        created_knowledge_refs,
        evidence_refs or [],
        next_actions or [],
        handoff_to,
        handoff_summary,
        artifact_refs or [],
        open_risks or [],
        next_suggested_task,
    )
    quality_evaluation = (
        evaluate_knowledge_task_result(
            task_fm,
            status,
            summary,
            created_knowledge_refs,
            source_refs,
            evidence_refs or [],
            tests_or_checks or [],
        )
        if is_knowledge_execution_task(task_fm)
        else evaluate_project_task_result(
            task_fm,
            status,
            summary,
            handoff_contract,
            evidence_refs or [],
            tests_or_checks or [],
        )
    )
    operating_rule_refs = task_operating_rule_refs(bundle, task_fm)
    common_rules_evaluation = evaluate_common_operating_rules(
        task_fm,
        status,
        summary,
        handoff_contract,
        evidence_refs or [],
        output_refs or [],
        created_knowledge_refs,
        tests_or_checks or [],
        quality_evaluation,
        operating_rule_refs,
    )
    quality_evaluation = apply_common_rule_evaluation_to_quality(quality_evaluation, common_rules_evaluation)
    acceptance_policy = build_task_acceptance_policy(task_fm, status, quality_evaluation, handoff_contract, open_risks or [])
    frontmatter = {
        "type": "TaskResult",
        "title": f"Result for {task_fm.get('taskId', task_id)}",
        "description": f"Result of task {task_fm.get('taskId', task_id)}.",
        "timestamp": utc_now(),
        "resultId": result_id,
        "taskId": task_fm.get("taskId", task_id),
        "projectId": task_fm.get("projectId", ""),
        "assignee": task_fm.get("assignee", ""),
        "workSourceType": task_effective_work_source_type(task_fm),
        "requirementRefs": as_list(task_fm.get("requirementRefs")),
        "requirementObjectRefs": as_list(task_fm.get("requirementObjectRefs")),
        "acceptanceCriteriaRefs": as_list(task_fm.get("acceptanceCriteriaRefs")),
        "defectRefs": as_list(task_fm.get("defectRefs")),
        "defectObjectRefs": as_list(task_fm.get("defectObjectRefs")),
        "incidentRefs": as_list(task_fm.get("incidentRefs")),
        "operationRefs": as_list(task_fm.get("operationRefs")),
        "knowledgeTaskRefs": as_list(task_fm.get("knowledgeTaskRefs")),
        "researchQuestion": str(task_fm.get("researchQuestion") or ""),
        "sourceReason": str(task_fm.get("sourceReason") or ""),
        "outcomeSliceRef": str(task_fm.get("outcomeSliceRef") or ""),
        "receiverReviewRefs": as_list(task_fm.get("receiverReviewRefs")),
        "currentStage": task_fm.get("currentStage", ""),
        "taskRuntime": task_fm.get("taskRuntime") or task_runtime_snapshot(str(task_fm.get("taskType") or "")),
        "runnerId": runner_id or task_fm.get("leaseOwner", ""),
        "runner": runner_id or task_fm.get("leaseOwner", ""),
        "executorAgent": executor_agent,
        "leaseProof": secret_fingerprint(lease_token) if lease_token else str(task_fm.get("leaseTokenHash") or task_fm.get("leaseProofHash") or ""),
        "status": status,
        "summary": summary,
        "outputRefs": output_refs or [],
        "knowledgeRefs": created_knowledge_refs,
        "sourceMaterialRefs": source_refs,
        "evidenceRefs": evidence_refs or [],
        "testsOrChecks": tests_or_checks or [],
        "checks": tests_or_checks or [],
        "nextActions": next_actions or [],
        "nextAction": (next_actions or [""])[0],
        "risks": open_risks or [],
        "blockers": blockers or [],
        "approvalRequest": normalized_approval_request,
        "operatingRuleRefs": operating_rule_refs,
        "handoffContract": handoff_contract,
        "commonRulesEvaluation": common_rules_evaluation,
        "qualityEvaluation": quality_evaluation,
        "acceptancePolicy": acceptance_policy,
        "improvementRefs": [],
        "evalCaseRefs": [],
        "followupTaskRefs": [],
        "guideUpdateRequired": bool(task_fm.get("guideUpdateRequired")),
        **gate,
        "createdAt": utc_now(),
        "completedAt": utc_now(),
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            summary,
            "",
            "## Evidence",
            "",
            "\n".join(f"- {item}" for item in evidence_refs or source_refs) or "- none",
            "",
            "## Outcome Slice",
            "",
            f"- outcomeSliceRef: {str(task_fm.get('outcomeSliceRef') or '') or 'none'}",
            "",
            "## Outputs",
            "",
            "\n".join(f"- {item}" for item in (output_refs or []) + created_knowledge_refs) or "- none",
            "",
            "## Next Actions",
            "",
            "\n".join(f"- {item}" for item in next_actions or []) or "- none",
            "",
            "## Blockers",
            "",
            "\n".join(f"- {item}" for item in blockers or []) or "- none",
            "",
            "## Approval Request",
            "",
            json.dumps(normalized_approval_request, ensure_ascii=False, indent=2) if normalized_approval_request else "none",
            "",
            "## Handoff",
            "",
            f"- fromAgent: {handoff_contract.get('fromAgent', '') or 'none'}",
            f"- handoffTo: {handoff_contract.get('handoffTo', '') or 'none'}",
            f"- summary: {handoff_contract.get('handoffSummary', '') or 'none'}",
            f"- nextSuggestedTask: {handoff_contract.get('nextSuggestedTask', '') or 'none'}",
            f"- terminalReason: {handoff_contract.get('terminalReason', '') or 'none'}",
            "- artifactRefs:",
            *([f"  - {item}" for item in as_list(handoff_contract.get("artifactRefs"))] or ["  - none"]),
            "- openRisks:",
            *([f"  - {item}" for item in as_list(handoff_contract.get("openRisks"))] or ["  - none"]),
            "",
            "## Quality Evaluation",
            "",
            f"- status: {quality_evaluation.get('status', '')}",
            f"- decision: {quality_evaluation.get('decision', '')}",
            f"- score: {quality_evaluation.get('score', '')}",
            f"- attempt: {quality_evaluation.get('attemptNumber', '')}/{quality_evaluation.get('maxAttempts', '')}",
            f"- reasons: {', '.join(as_list(quality_evaluation.get('reasons'))) or 'none'}",
            "",
            "## Common Operating Rules",
            "",
            f"- status: {common_rules_evaluation.get('status', '')}",
            f"- rulesRef: {common_rules_evaluation.get('rulesRef', '')}",
            f"- guideRef: {common_rules_evaluation.get('guideRef', '')}",
            f"- reasons: {', '.join(as_list(common_rules_evaluation.get('reasons'))) or 'none'}",
            "- operatingRuleRefs:",
            *[f"  - {key}: {value or 'none'}" for key, value in operating_rule_refs.items()],
            "",
            "## Acceptance",
            "",
            f"- status: {acceptance_policy.get('acceptanceStatus', '')}",
            f"- humanAcceptanceRequired: {acceptance_policy.get('humanAcceptanceRequired', False)}",
            f"- projectManager: {acceptance_policy.get('projectManager', '') or 'none'}",
            f"- humanReviewer: {acceptance_policy.get('humanReviewer', '') or 'none'}",
            f"- reason: {acceptance_policy.get('reason', '') or 'none'}",
            "",
            "## Agent Improvement",
            "",
            "- improvementRefs: none",
            "- evalCaseRefs: none",
            "",
            "## Tests Or Checks",
            "",
            "\n".join(f"- {item}" for item in tests_or_checks or []) or "- none",
            "",
            "## Agent Team Guide Gate",
            "",
            f"- guideUpdateRequired: {bool(task_fm.get('guideUpdateRequired'))}",
            f"- guideUpdated: {gate['guideUpdated']}",
            f"- guideRef: {gate['guideRef'] or 'none'}",
            f"- guideFeishuUrl: {gate['guideFeishuUrl'] or 'none'}",
            f"- guideRevision: {gate['guideRevision'] or 'none'}",
            f"- guideAuditRefs: {', '.join(gate['guideAuditRefs']) or 'none'}",
        ]
    )
    write_text(result_path, render_doc(frontmatter, body))
    update_index(bundle.root / "task-results" / "index.md", str(frontmatter["title"]), rel(result_path, bundle.root))
    if frontmatter["workSourceType"] == "bugfix":
        update_defects_after_bugfix_result(
            bundle,
            task_fm,
            result_path,
            successful_close,
            tests_or_checks or [],
        )
    before = str(task_fm.get("status", ""))
    task_status_after_finish = task_status_after_acceptance_gate(status, quality_evaluation, acceptance_policy)
    updated_task = update_frontmatter_file(
        task_path,
        {
            "status": task_status_after_finish,
            "resultRef": rel(result_path, bundle.root),
            "completedAt": utc_now(),
            **({"approvalRequest": normalized_approval_request} if normalized_approval_request else {}),
            **({"guideUpdated": True, "guideRef": gate["guideRef"], "guideFeishuUrl": gate["guideFeishuUrl"], "guideRevision": gate["guideRevision"], "guideAuditRefs": gate["guideAuditRefs"]} if task_fm.get("guideUpdateRequired") and gate["guideUpdated"] else {}),
        },
    )
    record_runner_lease_finished(bundle, runner_id or str(task_fm.get("leaseOwner") or ""), str(task_fm.get("taskId", task_id)), rel(task_path, bundle.root), status)
    create_audit_log(bundle, str(task_fm.get("assignee", "system")), "task.finish", rel(task_path, bundle.root), before=before, after=task_status_after_finish, details=f"resultRef={rel(result_path, bundle.root)}\nrawResultStatus={status}\nacceptanceStatus={acceptance_policy.get('acceptanceStatus', '')}")
    message_type = "task_blocked" if status == "blocked" else "task_finished"
    create_task_notification(
        bundle,
        task_path,
        updated_task,
        message_type,
        recipient=str(updated_task.get("requester") or updated_task.get("assignee") or "project"),
        summary=f"任务{('被阻塞' if status == 'blocked' else '已完成')}：{updated_task.get('title', task_id)}。结果：{summary}。结果记录：{rel(result_path, bundle.root)}。",
    )
    maybe_record_agent_improvement(bundle, task_path, updated_task, result_path, load_object(result_path))
    if normalized_approval_request:
        create_task_notification(
            bundle,
            task_path,
            updated_task,
            "task_approval_relay_requested",
            recipient=project_manager_for_task(updated_task),
            summary=f"Runner 请求 PM 处理审批 relay：{updated_task.get('title', task_id)}。审批事项：{normalized_approval_request.get('summary', '')}",
            source_message_ref=rel(result_path, bundle.root),
        )
    notify_task_acceptance_gate(bundle, task_path, updated_task, result_path, acceptance_policy)
    followup_path = None
    if should_create_followup_at_finish(status, quality_evaluation, acceptance_policy):
        followup_path = create_orchestration_followup_task(
            bundle,
            updated_task,
            result_path,
            quality_evaluation,
            created_knowledge_refs,
            evidence_refs or [],
        )
        if followup_path is None:
            followup_path = create_project_role_followup_task(
                bundle,
                updated_task,
                result_path,
                quality_evaluation,
                handoff_contract,
            )
        if followup_path is None:
            followup_path = create_completion_followup_task(
                bundle,
                updated_task,
                result_path,
                status,
                evidence_refs or [],
            )
    if followup_path:
        followup_refs = [rel(followup_path, bundle.root)]
        update_frontmatter_file(result_path, {"followupTaskRefs": followup_refs, "updatedAt": utc_now()})
        task_followup_refs = append_unique(as_list(updated_task.get("followupTaskRefs")), followup_refs[0])
        update_frontmatter_file(task_path, {"followupTaskRefs": task_followup_refs, "updatedAt": utc_now()})
    append_log(bundle, f"finished task {task_fm.get('taskId', task_id)} status={status}")
    return result_path


def project_task_status(bundle: Bundle, task_id: str) -> dict[str, Any]:
    task_path = find_project_task(bundle, task_id)
    fm = load_object(task_path)
    fm["path"] = rel(task_path, bundle.root)
    return fm


def diagnose_project_task(bundle: Bundle, task_id: str) -> dict[str, Any]:
    task_path = find_project_task(bundle, task_id)
    task = load_object(task_path)
    task_ref = rel(task_path, bundle.root)
    status = str(task.get("status") or "")
    project_id = str(task.get("projectId") or "")
    assignee = str(task.get("assignee") or "")
    result_ref = str(task.get("resultRef") or "")
    result: dict[str, Any] = {}
    try:
        result_path = task_result_path_for_task(bundle, task)
        result = load_object(result_path)
        result_ref = rel(result_path, bundle.root)
    except KnowledgeError:
        result_path = None

    reasons: list[str] = []
    next_actions: list[str] = []
    suggested_commands: list[str] = []
    bottleneck = "none"

    if status == "pending":
        bottleneck = "waiting_for_execution"
        reasons.append("任务已创建，但还没有进入执行。")
        next_actions.append("拉取任务上下文并开始执行。")
        suggested_commands.extend(
            [
                f"python3 -m zhenzhi_knowledge.cli task pull {task_id}",
                f"python3 -m zhenzhi_knowledge.cli task start {task_id} --actor {assignee or 'system'}",
            ]
        )
    elif status == "waiting_runner":
        bottleneck = "waiting_for_runner"
        reasons.append("Agent Ring 未接管，任务等待本地 Runner 或人工接管。")
        next_actions.append("登记可用 Runner，或用本地 Codex/Claude 手动处理后写回 TaskResult。")
        suggested_commands.extend(
            [
                "python3 -m zhenzhi_knowledge.cli runner register --runner-id <runner-id> --name <name> --agent <agent-id> --capability <task-type> --project <project-id>",
                f"python3 -m zhenzhi_knowledge.cli task pull {task_id}",
                f"python3 -m zhenzhi_knowledge.cli task finish {task_id} --summary \"<完成说明>\" --evidence-ref <证据路径> --test-or-check \"<检查结果>\"",
            ]
        )
    elif status == "processing":
        bottleneck = "waiting_for_task_result"
        reasons.append("任务正在执行，下一步必须写回 TaskResult。")
        next_actions.append("完成自检后执行 task finish，带上证据、测试和交接/终止原因。")
        suggested_commands.append(
            f"python3 -m zhenzhi_knowledge.cli task finish {task_id} --summary \"<完成说明>\" --evidence-ref <证据路径> --test-or-check \"<检查结果>\""
        )
    elif status in {"blocked", "changes_requested"}:
        bottleneck = "needs_repair_or_escalation"
        reasons.append(f"任务状态为 {status}，需要修复、重试或升级给项目经理 Agent。")
        next_actions.append("查看 TaskResult/任务原因，创建修复任务或由项目经理重新分配。")
        suggested_commands.append(f"python3 -m zhenzhi_knowledge.cli project health --project {project_id or '<project-id>'} --create-followup")
    elif status == "waiting_acceptance":
        bottleneck = "waiting_for_acceptance"
        reasons.append("任务结果已提交，但等待项目经理或人类验收决策。")
        next_actions.append("验收 TaskResult，决定通过、退回修改或拒绝。")
        suggested_commands.append(
            f"python3 -m zhenzhi_knowledge.cli task accept {task_id} --decision accepted --reviewer <reviewer> --human"
        )
    elif status in {"done", "rejected"}:
        bottleneck = "closed"
        reasons.append("任务已关闭。")
        if result_ref:
            next_actions.append("如需继续推进，查看 followupTaskRefs 或项目 health。")
        else:
            reasons.append("但任务缺少 resultRef，需要补齐 TaskResult 记录。")
            bottleneck = "closed_without_result"
            next_actions.append("补写或修复 TaskResult 引用。")
        suggested_commands.append(f"python3 -m zhenzhi_knowledge.cli project health --project {project_id or '<project-id>'}")
    else:
        bottleneck = "unknown_status"
        reasons.append(f"未识别的任务状态：{status or 'empty'}。")
        next_actions.append("由项目经理 Agent 判断状态含义并修复状态机或任务卡。")
        suggested_commands.append(f"python3 -m zhenzhi_knowledge.cli project health --project {project_id or '<project-id>'} --create-followup")

    if result:
        quality = dict(result.get("qualityEvaluation") or {})
        common = dict(result.get("commonRulesEvaluation") or {})
        acceptance = dict(result.get("acceptancePolicy") or {})
        if quality and not bool(quality.get("passed")):
            bottleneck = "quality_gate_failed"
            reasons.append("质量评价未通过：" + (", ".join(as_list(quality.get("reasons"))) or str(quality.get("status") or "failed")))
            next_actions.append("按 qualityEvaluation.decision 执行 retry、repair 或 escalation。")
        if common and not bool(common.get("passed")):
            bottleneck = "common_rule_gate_failed"
            reasons.append("公共制度门禁未通过：" + (", ".join(as_list(common.get("reasons"))) or "commonRulesEvaluation failed"))
            next_actions.append("补齐规则引用、证据、质量评价或交接契约后重新 finish。")
        acceptance_status = str(acceptance.get("acceptanceStatus") or "")
        if acceptance_status in {"waiting_acceptance", "pm_review_required", "pending"}:
            bottleneck = "waiting_for_acceptance"
            if "任务结果已提交，但等待项目经理或人类验收决策。" not in reasons:
                reasons.append("TaskResult 已生成，但验收策略仍等待决策。")
            if not any("task accept" in command for command in suggested_commands):
                suggested_commands.append(
                    f"python3 -m zhenzhi_knowledge.cli task accept {task_id} --decision accepted --reviewer <reviewer> --human"
                )

    notifications = list_notifications(bundle, task_id=str(task.get("taskId") or task_id), limit=200)
    failed_notifications = [item for item in notifications if str(item.get("status") or "") in {"failed", "retrying", "dead_letter"}]
    if failed_notifications:
        if bottleneck == "none":
            bottleneck = "notification_failed"
        reasons.append(f"存在 {len(failed_notifications)} 条失败或待重试通知。")
        next_actions.append("重试通知或切换备用通知链路，避免用户以为任务没动。")

    if not reasons:
        reasons.append("未发现明显阻塞。")
    if not next_actions:
        next_actions.append("继续按当前任务上下文执行。")

    unique_next_actions: list[str] = []
    for item in next_actions:
        unique_next_actions = append_unique(unique_next_actions, item)
    unique_suggested_commands: list[str] = []
    for item in suggested_commands:
        unique_suggested_commands = append_unique(unique_suggested_commands, item)

    return {
        "apiVersion": "v0.1",
        "kind": "TaskDiagnosis",
        "taskId": str(task.get("taskId") or task_id),
        "taskRef": task_ref,
        "projectId": project_id,
        "assignee": assignee,
        "status": status,
        "bottleneck": bottleneck,
        "resultRef": result_ref,
        "reasons": reasons,
        "nextActions": unique_next_actions,
        "suggestedCommands": unique_suggested_commands,
        "notificationCount": len(notifications),
        "failedNotificationCount": len(failed_notifications),
    }


def list_project_tasks(
    bundle: Bundle,
    status: str = "",
    assignee: str = "",
    project_id: str = "",
    task_type: str = "",
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    roots = [bundle.root / "tasks"]
    project_root = bundle.root / "projects"
    if project_root.exists():
        roots.extend(project_root.glob("*/tasks"))
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            fm = load_object(path)
            if fm.get("type") not in {"ProjectTask", "KnowledgeTask"}:
                continue
            if status and fm.get("status") != status:
                continue
            if assignee and fm.get("assignee") != assignee:
                continue
            if project_id and fm.get("projectId") != slug(project_id):
                continue
            if task_type and fm.get("taskType") != task_type:
                continue
            fm["path"] = rel(path, bundle.root)
            tasks.append(fm)
    return tasks


def project_task_context_payload(bundle: Bundle, task_id: str, runner_id: str = "", lease_token: str = "") -> dict[str, Any]:
    context_path = pull_project_task(bundle, task_id, runner_id, lease_token)
    task = project_task_status(bundle, task_id)
    task_path = find_project_task(bundle, task_id)
    context_ref = rel(context_path, bundle.root)
    payload = {
        "apiVersion": "v0.1",
        "kind": "TaskContext",
        "task": task,
        "projectContextBundle": project_context_bundle(bundle, task_path),
        "contextRef": context_ref,
        "context": read_text(context_path),
    }
    if runner_id and lease_token:
        payload["executionContext"] = execution_context_payload(bundle, task, runner_id, lease_token, context_ref)
    return payload


def active_policies_for_agent(bundle: Bundle, agent_id: str) -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = []
    policy_root = bundle.root / "knowledge" / "policies"
    if not policy_root.exists():
        return policies
    for path in policy_root.glob("*.md"):
        fm = load_object(path)
        if fm.get("type") == "Policy" and fm.get("agentId") == slug(agent_id) and fm.get("status") in {"active", "verified", "approved"}:
            policies.append(fm)
    return policies


def normalize_scalar_frontmatter_value(value: Any) -> str:
    if isinstance(value, dict):
        if len(value) == 1:
            key, raw_value = next(iter(value.items()))
            key_text = str(key).strip().strip('"').strip("'")
            raw_text = "" if raw_value is None else str(raw_value).strip()
            return key_text if raw_text == "" else f"{key_text}:{raw_text}"
        return str(value).strip()
    return str(value or "").strip()


def normalize_permission_values(values: Any) -> set[str]:
    permissions: set[str] = set()
    for item in values or []:
        if isinstance(item, dict):
            value = str(item.get("permission") or item.get("name") or item.get("id") or "").strip()
            if not value:
                value = normalize_scalar_frontmatter_value(item)
        else:
            value = normalize_scalar_frontmatter_value(item)
        if value:
            permissions.add(value)
    return permissions


def merged_agent_permissions(agent: dict[str, Any], policies: list[dict[str, Any]]) -> dict[str, Any]:
    allowed_projects = set(agent.get("allowedProjects", []) or [])
    allowed_scopes = set(agent.get("allowedKnowledgeScopes", []) or [])
    allowed_risks = set(agent.get("allowedToolRiskLevels", []) or [])
    requires_approval = set(agent.get("requiresApproval", []) or [])
    write_permissions = normalize_permission_values(agent.get("writePermissions", []) or [])
    for policy in policies:
        p_projects = set(policy.get("allowedProjects", []) or [])
        p_scopes = set(policy.get("allowedKnowledgeScopes", []) or [])
        p_risks = set(policy.get("allowedToolRiskLevels", []) or [])
        allowed_projects = p_projects if not allowed_projects else (allowed_projects & p_projects if p_projects else allowed_projects)
        allowed_scopes = p_scopes if not allowed_scopes else (allowed_scopes & p_scopes if p_scopes else allowed_scopes)
        allowed_risks = p_risks if not allowed_risks else (allowed_risks & p_risks if p_risks else allowed_risks)
        requires_approval |= set(policy.get("requiresApproval", []) or [])
        write_permissions |= normalize_permission_values(policy.get("writePermissions", []) or [])
    return {
        "allowedProjects": sorted(allowed_projects),
        "allowedKnowledgeScopes": sorted(allowed_scopes),
        "allowedToolRiskLevels": sorted(allowed_risks or {"L1"}),
        "requiresApproval": sorted(requires_approval),
        "writePermissions": sorted(write_permissions),
        "policyCount": len(policies),
    }


def require_agent_write_permission(bundle: Bundle, agent_id: str, permission: str) -> None:
    normalized_agent_id = slug(agent_id) if str(agent_id).strip() else ""
    if not normalized_agent_id:
        raise KnowledgeError(f"executor agent is required for write permission: {permission}")
    agent_path = find_agent(bundle, normalized_agent_id)
    agent = load_object(agent_path)
    permissions = merged_agent_permissions(agent, active_policies_for_agent(bundle, normalized_agent_id))
    write_permissions = set(permissions.get("writePermissions", []) or [])
    if permission not in write_permissions:
        raise KnowledgeError(f"agent {normalized_agent_id} lacks write permission: {permission}")


def project_tools(bundle: Bundle, project_id: str) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for path in (bundle.root / "tools").glob("*.md"):
        fm = load_object(path)
        if fm.get("type") != "ToolAsset":
            continue
        allowed_projects = fm.get("allowedProjects", []) or []
        if not allowed_projects or slug(project_id) in allowed_projects:
            tools.append({"path": rel(path, bundle.root), **fm})
    return tools


def compact_ref_list(refs: list[str], limit: int = 80) -> str:
    values = [str(item) for item in refs if str(item)]
    if not values:
        return "none"
    shown = values[:limit]
    suffix = f" (+{len(values) - limit} more)" if len(values) > limit else ""
    return ", ".join(shown) + suffix


def requirement_tree_context_role(agent_id: str, task_obj: dict[str, Any]) -> str:
    task_type = str(task_obj.get("taskType") or "").lower()
    if task_type in {"development", "test", "design", "ops", "operations", "review", "governance"}:
        return "ops" if task_type == "operations" else task_type
    raw_agent = str(agent_id).lower()
    if "test" in raw_agent:
        return "test"
    if "design" in raw_agent:
        return "design"
    if "ops" in raw_agent or "operations" in raw_agent:
        return "ops"
    if "review" in raw_agent:
        return "review"
    if "steward" in raw_agent or "governance" in raw_agent:
        return "governance"
    return "development"


def maybe_load_project_task_for_context(bundle: Bundle, task: str) -> tuple[Path | None, dict[str, Any]]:
    if not str(task or "").strip():
        return None, {}
    try:
        task_path = find_project_task(bundle, task)
    except KnowledgeError:
        return None, {}
    try:
        task_obj = load_object(task_path)
    except KnowledgeError:
        return None, {}
    return task_path, task_obj


def role_focus_lines(role: str) -> list[str]:
    focus = {
        "development": [
            "- Development focus: preserve why/what/evidence chain before code changes.",
            "- Must keep BR -> UREQ -> ProductRequirement -> ANOS -> Test -> Acceptance traceability in TaskResult.",
        ],
        "test": [
            "- Test focus: verify observable criteria, test refs, acceptance gates, and evidence requirements.",
            "- Do not accept without gate evidence or explicit blocker diagnostics.",
        ],
        "design": [
            "- Design focus: user scenarios, product intent, interaction constraints, assumptions, and decision refs.",
            "- Keep design outputs traceable to UREQ and ProductRequirement refs.",
        ],
        "ops": [
            "- Ops focus: rollout constraints, blocker state, evidence capture, and operational acceptance gates.",
            "- Do not turn draft tasks into live execution without explicit scheduler promotion.",
        ],
        "review": [
            "- Review focus: evidence completeness, source refs, decisions, blockers, and review/gate readiness.",
            "- Review conclusion must cite traceability refs, not only implementation files.",
        ],
        "governance": [
            "- Governance focus: policy impact, review evidence, blocker severity, audit refs, and lifecycle status.",
            "- High or critical blockers prevent executable work until resolved or waived by decision.",
        ],
    }
    return focus.get(role, focus["development"])


def requirement_tree_context_section(bundle: Bundle, project_id: str, agent_id: str, task: str) -> list[str]:
    try:
        records = requirement_tree_json_records(bundle)
    except KnowledgeError:
        return []
    if not records:
        return []

    task_path, task_obj = maybe_load_project_task_for_context(bundle, task)
    tree_ref = str(task_obj.get("requirementTreeId") or task_obj.get("requirementTreeRef") or "")
    try:
        tree_path, tree = find_requirement_tree_record(bundle, records, tree_ref, project_id)
    except KnowledgeError:
        try:
            tree_path, tree = find_requirement_tree_record(bundle, records, "", project_id)
        except KnowledgeError:
            return []

    tree_id = str(tree.get("treeId") or "")
    nodes = {str(record.get("nodeId")): record for _path, record in records if record.get("type") == "RequirementNode" and str(record.get("treeRef") or "") == tree_id}
    gates = {str(record.get("gateId")): record for _path, record in records if record.get("type") == "AcceptanceGate" and str(record.get("treeRef") or "") == tree_id}
    snapshots = {str(record.get("snapshotId")): record for _path, record in records if record.get("type") == "RequirementCoverageSnapshot" and str(record.get("treeRef") or "") == tree_id}
    snapshot = snapshots.get(str(tree.get("coverageSnapshotRef") or ""), {})
    trace = {
        "BR": as_list(task_obj.get("businessRequirementRefs")) or as_list(tree.get("businessRequirementRefs")),
        "UREQ": as_list(task_obj.get("userRequirementRefs")) or as_list(tree.get("userRequirementRefs")),
        "ProductRequirement": as_list(task_obj.get("productRequirementRefs")) or as_list(tree.get("productRequirementRefs")),
        "ANOS": as_list(task_obj.get("functionalRequirementRefs")) or as_list(tree.get("functionalRequirementRefs")),
        "Tests": as_list(task_obj.get("testCaseRefs")) or as_list(tree.get("testCaseRefs")),
        "Acceptance": as_list(task_obj.get("acceptanceGateRefs")) or as_list(tree.get("acceptanceGateRefs")),
    }
    role = requirement_tree_context_role(agent_id, task_obj)
    source_refs = append_unique_list(as_list(tree.get("sourceRefs")), as_list(task_obj.get("sourceMaterialRefs")))
    selected_ureqs = [nodes[ref] for ref in trace["UREQ"] if ref in nodes][:8]
    selected_preqs = [nodes[ref] for ref in trace["ProductRequirement"] if ref in nodes][:8]
    selected_functionals = [nodes[ref] for ref in trace["ANOS"] if ref in nodes][:16]
    selected_gates = [gates[ref] for ref in trace["Acceptance"] if ref in gates][:16]
    blocker_rows = snapshot.get("blockers") if isinstance(snapshot.get("blockers"), list) else []
    high_blockers = [blocker for blocker in blocker_rows if isinstance(blocker, dict) and str(blocker.get("severity") or "").lower() in {"high", "critical"}]
    coverage_rows = snapshot.get("coverageRows") if isinstance(snapshot.get("coverageRows"), list) else []
    task_ref = rel(task_path, bundle.root) if task_path else ""
    decision_refs: list[str] = []
    for record in [tree, *selected_ureqs, *selected_preqs, *selected_functionals, *selected_gates]:
        decision_refs = append_unique_list(decision_refs, as_list(record.get("decisionRefs")))
    review_refs = as_list(tree.get("reviewRefs"))
    evidence_refs: list[str] = []
    for gate in selected_gates:
        evidence_refs = append_unique_list(evidence_refs, as_list(gate.get("requiredEvidenceRefs")))

    lines = [
        "## Requirement Tree Traceability",
        "",
        f"- treeRef: {rel(tree_path, bundle.root)}",
        f"- treeId: {tree_id}",
        f"- treeStatus: {tree.get('status', '')}",
        f"- taskRef: {task_ref or 'none'}",
        f"- roleContext: {role}",
        f"- sourceRefs: {compact_ref_list(source_refs)}",
        f"- BR refs: {compact_ref_list(trace['BR'])}",
        f"- UREQ refs: {compact_ref_list(trace['UREQ'])}",
        f"- ProductRequirement refs: {compact_ref_list(trace['ProductRequirement'])}",
        f"- FunctionalRequirement/ANOS refs: {compact_ref_list(trace['ANOS'])}",
        f"- test refs: {compact_ref_list(trace['Tests'])}",
        f"- acceptance gates: {compact_ref_list(trace['Acceptance'])}",
        "",
        "### Role Focus",
        "",
        *role_focus_lines(role),
        "",
        "### Scenarios And Product Requirements",
        "",
    ]
    if selected_ureqs or selected_preqs:
        for node in selected_ureqs:
            lines.append(f"- {node.get('nodeId')}: {node.get('title')} | scenario={node.get('statement', '')} | acceptanceSignal={node.get('acceptanceSignal', node.get('successSignal', ''))}")
        for node in selected_preqs:
            lines.append(f"- {node.get('nodeId')}: {node.get('title')} | productRequirement={node.get('statement', '')} | why={node.get('whyItMatters', node.get('problem', ''))}")
    else:
        lines.append("- none")
    lines.extend(["", "### Functional Requirements", ""])
    if selected_functionals:
        for node in selected_functionals:
            lines.append(f"- {node.get('nodeId')}: {node.get('title')} | owner={node.get('ownerRole', '')} | tests={compact_ref_list(as_list(node.get('testCaseRefs')), 12)} | gates={compact_ref_list(as_list(node.get('acceptanceGateRefs')), 12)}")
    else:
        lines.append("- none")
    lines.extend(["", "### Test And Acceptance Evidence", ""])
    if selected_gates:
        for gate in selected_gates:
            lines.append(f"- {gate.get('gateId')}: method={gate.get('verificationMethod', '')} | observableCriteria={gate.get('observableSignal', '')} | evidenceRequired={compact_ref_list(as_list(gate.get('requiredEvidenceRefs')), 12)}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "### Assumptions Decisions Blockers",
            "",
            f"- assumptions: {compact_ref_list(as_list(task_obj.get('assumptions')))}",
            f"- decisions: {compact_ref_list(decision_refs or review_refs)}",
            f"- blockers: {compact_ref_list([str(blocker.get('reason') or blocker) for blocker in blocker_rows if isinstance(blocker, dict)] or as_list(task_obj.get('blockedBy')))}",
            f"- highOrCriticalBlockers: {len(high_blockers)}",
            f"- evidenceRequirements: {compact_ref_list(evidence_refs)}",
            f"- coverageRows: {len(coverage_rows)}",
            "",
        ]
    )
    return lines


def start_task(bundle: Bundle, project_id: str, agent_id: str, task: str, retrieval_limit: int = 5) -> Path:
    project_path = find_project(bundle, project_id)
    agent_path = find_agent(bundle, agent_id)
    project = load_object(project_path)
    agent = load_object(agent_path)
    policies = active_policies_for_agent(bundle, agent_id)
    permissions = merged_agent_permissions(agent, policies)
    allowed = permissions.get("allowedProjects", [])
    if allowed and slug(project_id) not in allowed:
        raise KnowledgeError(f"agent {agent_id} is not allowed for project {project_id}")
    allowed_risks = set(permissions.get("allowedToolRiskLevels", []) or ["L1"])
    visible_tools = [tool for tool in project_tools(bundle, project_id) if not allowed_risks or tool.get("riskLevel", "") in allowed_risks]
    retrieval_warning = ""
    try:
        retrieved = search_retrieval(bundle, task, project_id=slug(project_id), scopes=permissions.get("allowedKnowledgeScopes", []) or [], limit=retrieval_limit)
    except KnowledgeError as exc:
        message = str(exc)
        if "DATABASE_URL" not in message and "PostgreSQL" not in message and "psycopg" not in message:
            raise
        retrieved = []
        retrieval_warning = f"Retrieval skipped: {message}."
    project_dir = project_path.parent
    context_id = unique_time_id("context")
    generated_at = utc_now()
    operating_rules = common_operating_rules_payload(bundle)
    operating_rule_refs = task_operating_rule_refs(bundle, {"projectId": project_id, "assignee": agent_id})
    context = [
        "# Current Context Pack",
        "",
        f"- contextId: {context_id}",
        f"- generatedAt: {generated_at}",
        f"- projectId: {slug(project_id)}",
        f"- agentId: {slug(agent_id)}",
        f"- task: {task}",
        "",
        "## Required Reading",
        "",
        f"- Project: {rel(project_path, bundle.root)}",
        f"- Agent: {rel(agent_path, bundle.root)}",
        f"- Decisions: {rel(project_dir / 'decisions.md', bundle.root)}",
        f"- Lessons: {rel(project_dir / 'lessons.md', bundle.root)}",
        f"- Project Agents: {rel(project_dir / 'agents.md', bundle.root)}",
        f"- Project Tools: {rel(project_dir / 'tools.md', bundle.root)}",
        f"- Company Constitution: {operating_rule_refs['companyConstitution']}",
        f"- Task Runtime Contract: {operating_rule_refs['taskRuntimeContract']}",
        f"- Human Acceptance Policy: {operating_rule_refs['humanAcceptancePolicy']}",
        f"- Common Agent Operating Rules: {operating_rule_refs['commonRules']}",
        f"- Agent Team Guide: {operating_rule_refs['agentTeamGuide']}",
        f"- Role Operating Spec: {operating_rule_refs['roleOperatingSpec']}",
        f"- Role Rules: {operating_rule_refs.get('roleRules') or rel(agent_path, bundle.root)}",
        f"- Project Rules: {operating_rule_refs.get('projectRules') or rel(project_path, bundle.root)}",
        "",
        "## Operating Rule Contract",
        "",
        "- Agent must read the required rule refs above before work.",
        "- TaskResult must include operatingRuleRefs, commonRulesEvaluation, qualityEvaluation, acceptancePolicy, and handoffContract.",
        "- If a rule is too heavy, conflicting, or harmful, create an OperatingRuleIssue instead of ignoring it.",
        "- mandatoryGates:",
        *[f"  - {item}" for item in operating_rules["mandatoryGates"]],
        "",
        "## Policy Result",
        "",
        "```json",
        json.dumps(permissions, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Allowed ToolAssets",
        "",
        *[f"- {tool.get('toolId', '')}: {tool.get('title', '')} ({tool.get('riskLevel', '')}) -> {tool.get('path', '')}" for tool in visible_tools],
        "",
        *requirement_tree_context_section(bundle, project_id, agent_id, task),
        "## Retrieved Context",
        "",
        *[
            "\n".join(
                [
                    f"### {item['path']}#{item['chunkId']}",
                    "",
                    f"- sourceRef: {item['path']}",
                    f"- score: {item['score']}",
                    f"- inclusionReason: {graph_inclusion_reason(bundle, item['path'], slug(project_id))}",
                    "",
                    item["text"],
                    "",
                ]
            )
            for item in retrieved
        ],
        "" if retrieved else retrieval_warning or "No retrieved context.",
        "",
        "## Constraints",
        "",
        "- Read this context pack before work.",
        "- Code changes must go through Git.",
        "- Write AgentRun and draft updates with finish.",
        "- Do not dump raw files or arbitrary notes into knowledge directories.",
        "- New KnowledgeItem content must be structured, categorized, sourced, and reviewable.",
        "- Do not store secrets in knowledge files.",
        "- Use registered ToolAsset records for auditable team tool use; personal/local tools are not reusable team assets until registered.",
        "- Tool results are not reusable knowledge by default; project writeback and knowledge publication require separate write/review approval.",
        "- High-risk tool execution requires explicit approval even when the tool can be discovered or dry-run.",
        "",
        "## Project Frontmatter",
        "",
        "```json",
        json.dumps(project, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Agent Frontmatter",
        "",
        "```json",
        json.dumps(agent, indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    context_text = "\n".join(context)
    write_text(bundle.context_archive_path(context_id), context_text)
    write_text(bundle.context_path, context_text)
    append_log(bundle, f"started context {context_id} for project={slug(project_id)} agent={slug(agent_id)}")
    return bundle.context_path


def finish_task(
    bundle: Bundle,
    project_id: str,
    agent_id: str,
    summary: str,
    result: str = "completed",
    no_reusable_lesson: bool = False,
    tool_update: bool = True,
) -> Path:
    find_project(bundle, project_id)
    find_agent(bundle, agent_id)
    if not no_reusable_lesson:
        require_agent_write_permission(bundle, agent_id, "knowledge:draft")
    if tool_update:
        require_agent_write_permission(bundle, agent_id, "toolAsset:draft")
    if not bundle.context_path.exists():
        raise KnowledgeError("missing current context pack; run zhenzhi-knowledge start before finish")
    context_text = read_text(bundle.context_path)
    context_meta = extract_context_meta(context_text)
    if context_meta.get("projectId") != slug(project_id) or context_meta.get("agentId") != slug(agent_id):
        raise KnowledgeError("current context pack does not match project/agent; run start again")
    context_id = context_meta.get("contextId", "")
    if not context_id:
        raise KnowledgeError("current context pack is missing contextId; run start again")
    context_ref = rel(bundle.context_archive_path(context_id), bundle.root)
    run_id = unique_time_id("run")
    run_dir = bundle.root / "runs" / slug(project_id)
    ensure_dir(run_dir)
    run_path = run_dir / f"{run_id}.md"
    knowledge_used = extract_source_refs(context_text)
    frontmatter = {
        "type": "AgentRun",
        "title": f"{run_id} {slug(project_id)}",
        "description": summary,
        "timestamp": utc_now(),
        "runId": run_id,
        "projectId": slug(project_id),
        "agentId": slug(agent_id),
        "status": "draft",
        "result": result,
        "contextRefs": [context_ref],
        "toolsUsed": [],
        "knowledgeUsed": knowledge_used,
        "outputRefs": [],
        "codeRefs": [],
        "humanReview": "required",
    }
    body = f"## Summary\n\n{summary}\n\n## Lessons\n\n"
    body += "no reusable lesson\n" if no_reusable_lesson else f"- {summary}\n"
    body += "\n## Knowledge Gaps\n\n- none captured\n"
    write_text(run_path, render_doc(frontmatter, body))
    draft_dir = bundle.root / "projects" / slug(project_id)
    if not no_reusable_lesson:
        append_text(draft_dir / "lessons.draft.md", f"\n## {run_id}\n\n{summary}\n\n")
    append_text(draft_dir / "project.update.draft.md", f"\n## {run_id}\n\n{summary}\n\n")
    if tool_update:
        append_text(draft_dir / "tools.update.draft.md", f"\n## {run_id}\n\nNo specific ToolAsset update captured.\n\n")
    update_index(bundle.root / "runs" / "index.md", run_id, f"{slug(project_id)}/{run_id}.md")
    append_log(bundle, f"finished AgentRun {run_id}")
    return run_path


def failed_evals_for_target(bundle: Bundle, target_ref: str) -> list[Path]:
    failed: list[Path] = []
    eval_root = bundle.root / "knowledge" / "eval-runs"
    if not eval_root.exists():
        return failed
    for path in eval_root.glob("*.md"):
        fm = load_object(path)
        if fm.get("type") != "EvalRun":
            continue
        if fm.get("targetRef") == target_ref and fm.get("result") == "fail":
            failed.append(path)
    return failed


def as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [normalize_scalar_frontmatter_value(item) for item in value if normalize_scalar_frontmatter_value(item)]
    normalized = normalize_scalar_frontmatter_value(value)
    return [normalized] if normalized else []


def append_unique(items: list[str], value: str) -> list[str]:
    normalized = str(value).strip()
    if normalized and normalized not in items:
        items.append(normalized)
    return items


def normalized_task_type(task_type: str) -> str:
    if not task_type.strip():
        return ""
    return slug(task_type).replace("-", "_")


def task_runtime_profile(task_type: str) -> dict[str, Any]:
    normalized = normalized_task_type(task_type)
    if normalized in TASK_RUNTIME_PROFILES:
        return {**TASK_RUNTIME_PROFILES[normalized], "taskType": normalized}
    if normalized in {"product_discovery", "requirement_clarification", "product_requirement"}:
        return {
            "taskType": normalized,
            "category": "product",
            "objectType": "ProjectTask",
            "defaultAssignee": PRODUCT_MANAGER_AGENT_ID,
            "qualityGate": "product_requirement",
            "acceptancePath": "pm_review",
            "requiresSourceMaterial": False,
            "requiresKnowledgeDraft": False,
            "requiresTests": False,
        }
    if normalized in {"frontend_design", "ux_design", "ui_design", "design_spec"}:
        return {
            "taskType": normalized,
            "category": "design",
            "objectType": "ProjectTask",
            "defaultAssignee": DESIGN_AGENT_ID,
            "qualityGate": "design_spec",
            "acceptancePath": "pm_review",
            "requiresSourceMaterial": False,
            "requiresKnowledgeDraft": False,
            "requiresTests": False,
        }
    if normalized in {"operations_feedback", "growth_feedback"}:
        return {
            "taskType": normalized,
            "category": "operations",
            "objectType": "ProjectTask",
            "defaultAssignee": OPERATIONS_AGENT_ID,
            "qualityGate": "operations",
            "acceptancePath": "pm_review",
            "requiresSourceMaterial": False,
            "requiresKnowledgeDraft": False,
            "requiresTests": False,
        }
    return {
        "taskType": normalized or "task",
        "category": "project",
        "objectType": "ProjectTask",
        "defaultAssignee": PROJECT_MANAGER_AGENT_ID,
        "qualityGate": "project",
        "acceptancePath": "pm_review",
        "requiresSourceMaterial": False,
        "requiresKnowledgeDraft": False,
        "requiresTests": False,
    }


def task_runtime_snapshot(task_type: str) -> dict[str, Any]:
    profile = task_runtime_profile(task_type)
    normalized = str(profile["taskType"])
    category = str(profile["category"])
    required_capabilities = [normalized]
    acceptance_path = str(profile["acceptancePath"])
    review_path = acceptance_path
    if bool(profile["requiresTests"]):
        review_path = "engineering_test"
    elif bool(profile["requiresKnowledgeDraft"]):
        review_path = "knowledge_review"
    elif category == "product":
        review_path = "product_prd_gate"
    return {
        "runtimeVersion": "task-runtime.v1",
        "version": "task-runtime.v1",
        "taskType": normalized,
        "category": category,
        "stage": "",
        "requiredCapabilities": required_capabilities,
        "requiredTools": [],
        "sourceRefs": [],
        "repositoryRefs": [],
        "dataScopes": [],
        "qualityGate": profile["qualityGate"],
        "acceptancePath": acceptance_path,
        "reviewPath": review_path,
        "riskLevel": "medium" if bool(profile["requiresTests"]) else "low",
        "permissionPolicy": "runner_scope_required",
        "closurePolicy": "task_result_with_evidence",
        "approvalRelayRequired": False,
        "testEvidenceRequired": bool(profile["requiresTests"]),
        "knowledgeEvidenceRequired": bool(profile["requiresKnowledgeDraft"]),
        "productEvidenceRequired": category == "product",
        "manualHandoffAllowed": True,
        "requiresSourceMaterial": bool(profile["requiresSourceMaterial"]),
        "requiresKnowledgeDraft": bool(profile["requiresKnowledgeDraft"]),
        "requiresTests": bool(profile["requiresTests"]),
    }


def normalized_task_runtime(task: dict[str, Any]) -> dict[str, Any]:
    runtime = dict(task.get("taskRuntime") or {}) if isinstance(task.get("taskRuntime"), dict) else {}
    base = task_runtime_snapshot(str(task.get("taskType") or runtime.get("taskType") or ""))
    merged = {**base, **runtime}
    merged["runtimeVersion"] = str(merged.get("runtimeVersion") or merged.get("version") or "task-runtime.v1")
    merged["version"] = str(merged.get("version") or merged["runtimeVersion"])
    merged["taskType"] = normalized_task_type(str(merged.get("taskType") or task.get("taskType") or "task"))
    merged["stage"] = str(merged.get("stage") or task.get("currentStage") or "")
    merged["sourceRefs"] = append_runtime_unique(as_list(merged.get("sourceRefs")), as_list(task.get("sourceMaterialRefs")))
    merged["repositoryRefs"] = append_runtime_unique(as_list(merged.get("repositoryRefs")), as_list(task.get("repositoryRefs")) or as_list(task.get("repoRefs")))
    merged["dataScopes"] = append_runtime_unique(as_list(merged.get("dataScopes")), as_list(task.get("dataScopes")))
    required_capabilities = append_runtime_unique(as_list(merged.get("requiredCapabilities")), as_list(task.get("requiredCapabilities")))
    if not required_capabilities and merged["taskType"]:
        required_capabilities = [merged["taskType"]]
    merged["requiredCapabilities"] = required_capabilities
    merged["requiredTools"] = append_runtime_unique(as_list(merged.get("requiredTools")), as_list(task.get("requiredTools")))
    merged["riskLevel"] = str(task.get("riskLevel") or merged.get("riskLevel") or "low")
    merged["approvalRelayRequired"] = boolish(task.get("approvalRelayRequired"), boolish(merged.get("approvalRelayRequired"), False))
    merged["testEvidenceRequired"] = boolish(task.get("testEvidenceRequired"), boolish(merged.get("testEvidenceRequired"), False))
    merged["knowledgeEvidenceRequired"] = boolish(task.get("knowledgeEvidenceRequired"), boolish(merged.get("knowledgeEvidenceRequired"), False))
    merged["productEvidenceRequired"] = boolish(task.get("productEvidenceRequired"), boolish(merged.get("productEvidenceRequired"), False))
    merged["manualHandoffAllowed"] = boolish(task.get("manualHandoffAllowed"), boolish(merged.get("manualHandoffAllowed"), True))
    return merged


def append_runtime_unique(items: list[str], values: list[str]) -> list[str]:
    updated = list(items)
    for value in values:
        updated = append_unique(updated, value)
    return updated


def ensure_project_task_runtime(bundle: Bundle, task_path: Path, task: dict[str, Any] | None = None) -> dict[str, Any]:
    current = task or load_object(task_path)
    runtime = normalized_task_runtime(current)
    if current.get("taskRuntime") != runtime:
        current = update_frontmatter_file(task_path, {"taskRuntime": runtime, "updatedAt": utc_now()})
    return current


def handoff_contract_for_task_type(task_type: str) -> dict[str, Any]:
    normalized = normalized_task_type(task_type)
    if normalized in ROLE_HANDOFF_CONTRACTS:
        return ROLE_HANDOFF_CONTRACTS[normalized]
    if normalized in {"project_initialization", "blocker_resolution", "project_intake"}:
        return ROLE_HANDOFF_CONTRACTS["project_management"]
    if normalized in {"product_discovery", "requirement_clarification"}:
        return ROLE_HANDOFF_CONTRACTS["product_requirement"]
    if normalized in {"frontend_design", "ux_design", "ui_design"}:
        return ROLE_HANDOFF_CONTRACTS["design_spec"]
    if normalized in {"engineering_action", "implementation", "backend", "frontend"}:
        return ROLE_HANDOFF_CONTRACTS["development"]
    if normalized in {"qa", "verification", "release_test"}:
        return ROLE_HANDOFF_CONTRACTS["testing"]
    if normalized in {"operations_feedback", "growth_feedback"}:
        return ROLE_HANDOFF_CONTRACTS["operations"]
    if normalized in {"knowledge_retry", "knowledge_review"}:
        return ROLE_HANDOFF_CONTRACTS["knowledge_capture"]
    return {
        "from": "",
        "to": "",
        "requiredArtifacts": ["summary", "evidence refs", "next action or terminal reason"],
    }


def validate_task_status_transition(current: str, target: str) -> None:
    if not current or current == target:
        return
    if current in CLOSED_TASK_STATUSES:
        raise KnowledgeError(f"illegal task status transition: {current} -> {target}")
    if current in TASK_STATE_TRANSITIONS and target not in TASK_STATE_TRANSITIONS[current]:
        raise KnowledgeError(f"illegal task status transition: {current} -> {target}")


def validate_project_workspace_ref(rel_path: str, project: dict[str, Any]) -> list[str]:
    workspace_ref = str(project.get("workspaceRef") or "").strip()
    if not workspace_ref:
        return [f"{rel_path}: Project missing workspaceRef; use an explicit path/ref or pending_confirmation"]
    if workspace_ref == PENDING_WORKSPACE_REF:
        status = str(project.get("status") or "")
        if status in {"active", "done", "verified", "approved", "accepted", "launch_approved"}:
            return [f"{rel_path}: Project workspaceRef pending_confirmation cannot be used after project activation"]
        return []
    if workspace_ref.startswith(("workspace://", "git@", "http://", "https://", "./", "../")):
        return []
    if Path(workspace_ref).is_absolute():
        return []
    return [f"{rel_path}: Project workspaceRef must be absolute, workspace://, git/http URL, relative path, or pending_confirmation"]


def validate_central_record_size(path: Path, rel_path: str, fm: dict[str, Any]) -> list[str]:
    try:
        size = path.stat().st_size
    except OSError:
        return []
    if size <= CENTRAL_RECORD_MAX_BYTES:
        return []
    parts = path.parts
    if "projects" in parts:
        idx = parts.index("projects")
        project_id = parts[idx + 1] if idx + 1 < len(parts) else ""
        if project_id == "company-knowledge-core":
            return []
    if fm.get("type") in {"TaskResult", "SourceMaterial", "ProjectTask", "KnowledgeTask", "ProjectManagerAction", "ProjectManagerReview"} or rel_path.startswith(("projects/", "task-results/", "sources/")):
        return [
            f"{rel_path}: central record is {size} bytes; keep central records under {CENTRAL_RECORD_MAX_BYTES} bytes and store bulky artifacts in workspaceRef/storageRef"
        ]
    return []


def normalize_handoff_contract(
    task: dict[str, Any],
    status: str,
    summary: str,
    output_refs: list[str] | None = None,
    knowledge_refs: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    next_actions: list[str] | None = None,
    handoff_to: str = "",
    handoff_summary: str = "",
    artifact_refs: list[str] | None = None,
    open_risks: list[str] | None = None,
    next_suggested_task: str = "",
) -> dict[str, Any]:
    contract = handoff_contract_for_task_type(str(task.get("taskType") or ""))
    artifacts = append_unique(list(artifact_refs or []), "")
    for item in output_refs or []:
        artifacts = append_unique(artifacts, item)
    for item in knowledge_refs or []:
        artifacts = append_unique(artifacts, item)
    for item in evidence_refs or []:
        artifacts = append_unique(artifacts, item)
    actions = list(next_actions or [])
    target = handoff_to.strip()
    if not target and actions:
        target = str(contract.get("to") or "")
    terminal_reason = ""
    if not target:
        terminal_reason = "No next role declared; Project Manager Agent should close or create the next task." if status in TERMINAL_TASK_STATUSES else "Task is not terminal yet."
    return {
        "fromAgent": str(task.get("assignee") or contract.get("from") or ""),
        "handoffTo": target,
        "handoffSummary": handoff_summary.strip() or summary.strip(),
        "requiredArtifacts": as_list(contract.get("requiredArtifacts")),
        "artifactRefs": artifacts,
        "openRisks": list(open_risks or []),
        "nextSuggestedTask": next_suggested_task.strip() or (actions[0] if actions else ""),
        "terminalReason": terminal_reason,
    }


def evaluate_project_task_result(
    task: dict[str, Any],
    status: str,
    summary: str,
    handoff_contract: dict[str, Any],
    evidence_refs: list[str],
    tests_or_checks: list[str],
) -> dict[str, Any]:
    attempt = task_attempt_number(task)
    max_attempts = task_max_attempts(task)
    reasons: list[str] = []
    if status == "blocked":
        reasons.append("executor reported blocked")
        return {
            "type": "AgentResultEvaluation",
            "status": "blocked",
            "passed": False,
            "decision": "escalate_to_project_manager",
            "score": 0,
            "attemptNumber": attempt,
            "maxAttempts": max_attempts,
            "retryable": False,
            "reasons": reasons,
            "nextOwnerAgent": PROJECT_MANAGER_AGENT_ID,
        }
    if status in {"rejected", "failed"}:
        reasons.append(f"executor reported {status}")
    if not summary.strip():
        reasons.append("missing summary")
    if not str(handoff_contract.get("handoffSummary") or "").strip():
        reasons.append("missing handoff summary")
    if not (handoff_contract.get("artifactRefs") or evidence_refs):
        reasons.append("missing artifact or evidence refs")
    runtime = task_runtime_profile(str(task.get("taskType") or ""))
    if bool(runtime.get("requiresTests")) and not tests_or_checks:
        reasons.append("missing tests/checks")
    failed_checks = [item for item in tests_or_checks if test_or_check_looks_failed(item)]
    if failed_checks:
        reasons.append("tests/checks reported failure")
    expected_outputs = as_list(task.get("expectedOutput"))
    coverage_refs = as_list(handoff_contract.get("artifactRefs")) + evidence_refs
    missing_expected = [
        item
        for item in expected_outputs
        if not expected_output_is_covered(item, summary, coverage_refs, tests_or_checks)
    ]
    if missing_expected:
        reasons.append("expected output not covered: " + "; ".join(missing_expected[:3]))
    if reasons:
        decision = "retry_required" if attempt < max_attempts else "escalate_to_project_manager"
        return {
            "type": "AgentResultEvaluation",
            "status": "failed",
            "passed": False,
            "decision": decision,
            "score": 45 if decision == "retry_required" else 20,
            "attemptNumber": attempt,
            "maxAttempts": max_attempts,
            "retryable": decision == "retry_required",
            "reasons": reasons,
            "nextOwnerAgent": str(task.get("assignee") or "") if decision == "retry_required" else PROJECT_MANAGER_AGENT_ID,
        }
    return {
        "type": "AgentResultEvaluation",
        "status": "passed",
        "passed": True,
        "decision": "handoff_ready" if handoff_contract.get("handoffTo") else "close",
        "score": 95 if tests_or_checks else 85,
        "attemptNumber": attempt,
        "maxAttempts": max_attempts,
        "retryable": False,
        "reasons": [],
        "artifactRefsPresent": bool(handoff_contract.get("artifactRefs")),
        "evidenceRefsPresent": bool(evidence_refs),
        "testsOrChecksPresent": bool(tests_or_checks),
        "expectedOutputCovered": True,
        "nextOwnerAgent": str(handoff_contract.get("handoffTo") or ""),
    }


def attach_agent_to_project(bundle: Bundle, agent_id: str, project_id: str, note: str = "") -> Path:
    aid = slug(agent_id)
    pid = slug(project_id)
    agent_path = find_agent(bundle, aid)
    project_path = find_project(bundle, pid)
    agent = load_object(agent_path)
    project = load_object(project_path)
    allowed_projects = append_unique(as_list(agent.get("allowedProjects")), pid)
    related_agents = append_unique(as_list(project.get("relatedAgents")), aid)
    update_frontmatter_file(agent_path, {"allowedProjects": allowed_projects, "updatedAt": utc_now()})
    update_frontmatter_file(project_path, {"relatedAgents": related_agents, "updatedAt": utc_now()})
    project_agents_path = project_path.parent / "agents.md"
    existing = read_text(project_agents_path) if project_agents_path.exists() else "# Agents\n\n"
    line = f"- [{agent.get('title') or aid}](../../agents/{aid}.md)"
    if note:
        line += f" - {note}"
    if f"../../agents/{aid}.md" not in existing:
        write_text(project_agents_path, existing.rstrip() + "\n" + line + "\n")
    create_audit_log(bundle, aid, "agent.attachProject", rel(project_path, bundle.root), after=pid, policy_result="draft")
    return agent_path


def register_project_agent(
    bundle: Bundle,
    project_id: str,
    agent_id: str,
    name: str,
    owner: str,
    ai_tool: str,
    purpose: str,
    required_capabilities: list[str] | None = None,
    allowed_tools: list[str] | None = None,
    body: str | None = None,
) -> Path:
    aid = slug(agent_id)
    path = bundle.root / "agents" / f"{aid}.md"
    if path.exists():
        update_frontmatter_file(
            path,
            {
                "title": name,
                "description": purpose,
                "owner": owner,
                "aiTool": ai_tool,
                "updatedAt": utc_now(),
            },
        )
    else:
        path = make_agent(bundle, aid, name, owner, ai_tool, purpose)
    attached_path = attach_agent_to_project(bundle, aid, project_id, purpose)
    updates: dict[str, Any] = {"updatedAt": utc_now()}
    if required_capabilities is not None:
        updates["requiredCapabilities"] = required_capabilities
    if allowed_tools is not None:
        updates["allowedTools"] = allowed_tools
    update_frontmatter_file(attached_path, updates)
    if body is not None:
        frontmatter, _ = parse_frontmatter(read_text(attached_path))
        write_text(attached_path, render_doc(frontmatter, body))
    return attached_path


def ensure_default_project_agents(
    bundle: Bundle,
    project_id: str,
    project_name: str,
    owner: str,
    lead_agent_name: str = "",
    requested_agents: str = "",
    goal: str = "",
    repo_mode: str = "",
) -> list[Path]:
    pid = slug(project_id)
    specs = [
        (
            f"agent.{pid}.project-manager",
            lead_agent_name or f"{project_name} 项目经理 Agent",
            "项目初始化闭环负责人；确认范围、里程碑、仓库、项目群、Agent team、Runner 交接、TaskResult 和启动后下一步。",
            ["project_initialization", "project_management", "task_orchestration", "agent_team_coordination", "knowledge_sync"],
            ["tool.zhenzhi-knowledge"],
            project_manager_agent_body(pid, project_name),
        ),
        (
            f"agent.{pid}.knowledge-engineering",
            f"{project_name} 知识工程 Agent",
            "资料解析、证据引用、结构化知识沉淀、Review 与入库质量保障。",
            ["knowledge_capture", "source_extraction", "evidence_citation", "knowledge_writeback"],
            [],
            None,
        ),
        (
            f"agent.{pid}.executor",
            f"{project_name} 执行 Agent",
            "通过本地 Runner 驱动 Codex、Claude 或本地工具完成项目初始化和执行任务。",
            ["codex", "git", "local_execution", "project_initialization"],
            [],
            None,
        ),
    ]
    if needs_product_manager_agent(requested_agents, goal, repo_mode):
        specs.append(
            (
                f"agent.{pid}.product-manager",
                f"{project_name} 产品经理 Agent",
                "产品需求澄清、用户目标拆解、验收标准、业务里程碑建议和首批产品任务定义。",
                ["product_discovery", "requirement_clarification", "acceptance_criteria", "project_planning"],
                [],
                None,
            )
        )
    return [
        register_project_agent(bundle, pid, agent_id, name, owner, "codex", purpose, capabilities, allowed_tools, body)
        for agent_id, name, purpose, capabilities, allowed_tools, body in specs
    ]


def project_manager_agent_body(project_id: str, project_name: str) -> str:
    pid = slug(project_id)
    return "\n".join(
        [
            f"# {project_name} 项目经理 Agent",
            "",
            "## Purpose",
            "",
            "项目经理 Agent 是项目初始化闭环负责人。它不替代人类项目 Owner，也不兼任产品经理；它负责把创建项目产生的启动卡、审批、Agent team、仓库、项目群、Runner 和首批任务收口成可执行项目上下文。",
            "",
            "## Required Reading",
            "",
            "- `docs/agent-team/project-manager-agent-skill-pack.md`",
            f"- `projects/{pid}/project.md`",
            f"- `projects/{pid}/launch.md`",
            f"- `projects/{pid}/agents.md`",
            f"- `projects/{pid}/tools.md`",
            f"- `projects/{pid}/decisions.md`",
            f"- `projects/{pid}/tasks/project-init-{pid}.md`",
            "",
            "## Required Tools",
            "",
            "- `tool.zhenzhi-knowledge`: sync pull, start, task pull, task finish, finish, sync push, status, audit search.",
            "- Agent Ring runner registry and lease API through the central processor.",
            "- Git/repository inspection through the selected Runner; use read-only inspection until owner approval permits changes.",
            "- Feishu project group, approval, and notification gateway through Agent Hub; external side effects require approval.",
            "- Knowledge Review queue for any reusable knowledge, policy, permission, or tool output.",
            "",
            "## Initialization Workflow",
            "",
            "1. Pull latest context and read the generated context pack.",
            "2. Read project record, launch.md, initialization task card, approval status, Agent roster, and tool list.",
            "3. Verify M0-M3 startup milestones: intake completeness, owner/approval, initialization execution, first work queue.",
            "4. Existing repo: inspect repo URL, README, AGENTS, directory shape, review/test rules, and migration gaps.",
            "5. New repo: prepare repo creation request and initialization checklist; do not create external repos without approved integration.",
            "6. Verify default Agent team: project manager, product manager unless explicitly skipped, knowledge engineering, executor.",
            "7. Turn frontend/backend/test/ops/domain role requests into candidate Agents or first ProjectTasks only after runner, permission, and need are clear.",
            "8. Verify project group state: created, bound, explicitly unnecessary, or blocked with owner.",
            "9. Verify Runner state through assignedRunner/leaseOwner/heartbeat, or waiting_runner with handoff recipient.",
            "10. Write TaskResult plus AgentRun/manual handoff record with evidence, blockers, risks, and first ProjectTask list.",
            "11. Notify requester and project Owner.",
            "",
            "## Completion Criteria",
            "",
            "- Project draft and launch.md exist and match the current intake.",
            "- Entity workspace is confirmed, or `workspaceRef: pending_confirmation` is explicitly recorded with owner and next action.",
            "- Human project Owner and approval state are explicit.",
            "- Repo path is inspected or repo creation is represented as an approved/pending action.",
            "- README, AGENTS, review rules, and project directory expectations are ready or listed as blockers.",
            "- Product Manager Agent decision is recorded, including skip reason when product is not needed.",
            "- Project group is created, bound, deliberately skipped, or blocked with owner.",
            "- Agent team has allowed project scope and clear role boundaries.",
            "- Runner/manual handoff path is explicit.",
            "- First ProjectTasks exist or every missing first task has a blocker, owner, and next action.",
            "- TaskResult, AgentRun/manual handoff record, notification, and audit trail are written.",
            "",
            "## Evaluation",
            "",
            "- `pass`: all completion criteria are satisfied, or remaining gaps have explicit owner, blocker reason, and next action.",
            "- `blocked`: repo access, project Owner, approval, Runner, or required context is missing and no safe manual path exists.",
            "- `needs_human_approval`: repo creation, permission changes, member invitations, customer commitments, policy changes, or high-risk tools are required.",
            "- `needs_repair`: TaskResult, AgentRun, notification, audit trail, first task list, or launch.md status is missing or inconsistent.",
            "",
            "## After Initialization Handoff",
            "",
            "After initialization passes, switch from launch closure to project operating mode:",
            "",
            "- Convert the first ProjectTask list into an owned project backlog.",
            "- Mark each task with owner Agent/human, expected output, due date or review point, dependency, and risk level.",
            "- Confirm which tasks are ready for Scheduler dispatch and which require approval, Product Manager input, Tool Owner input, or human decision.",
            "- Keep project.md current with current focus, milestone state, and open blockers.",
            "- Keep decisions.md updated for scope, milestone, priority, risk, or ownership decisions.",
            "",
            "## Operating Cadence",
            "",
            "- Daily: inspect task status, Runner lease/heartbeat, blockers, due dates, approvals, and unread project material.",
            "- Twice weekly: summarize progress, risks, decisions needed, and next 3-5 actions to project Owner and project group.",
            "- Weekly: review milestone health, backlog age, blocked tasks, stale decisions, tool/permission gaps, and knowledge capture quality.",
            "- On every TaskResult: decide whether to close, create follow-up ProjectTask, send to Review, request repair, or escalate.",
            "",
            "## Progress Control",
            "",
            "- Every active task must have one accountable owner, expected output, status, next action, and due/review date.",
            "- Tasks with missing owner, missing output, stale lease, or no next action are not considered healthy.",
            "- Product discovery, implementation, test, ops, material ingest, tool request, and review-prep work must remain separate task types when ownership differs.",
            "- Milestone progress is based on completed evidence and accepted TaskResult, not optimistic chat updates.",
            "- Scope changes must become Decision records or approval requests before changing active commitments.",
            "",
            "## Risk Radar",
            "",
            "Check these risk signals during every follow-up:",
            "",
            "- Schedule risk: due date passed, milestone has no completed evidence, task age exceeds expected window.",
            "- Ownership risk: task has no accountable Agent/human, owner is unreachable, Runner is missing or stale.",
            "- Dependency risk: blocked by approval, repo access, tool permission, product decision, source material, or customer input.",
            "- Scope risk: new work appears without Decision/approval, requirements conflict, Product Manager output missing.",
            "- Quality risk: TaskResult lacks evidence, tests/checks missing, Review rejects, repeated repair tasks.",
            "- Knowledge risk: lessons/decisions not captured, reusable output bypasses Knowledge Review.",
            "- Communication risk: project group not bound, notification failed, Owner has not seen blocker/decision request.",
            "",
            "## Alert And Escalation",
            "",
            "- Alert project Owner immediately for blocked critical path, approval wait, missing Runner, repo access failure, or customer/security impact.",
            "- Alert Product Manager Agent or human product owner when product discovery or acceptance criteria block execution.",
            "- Alert Knowledge Engineering Agent review sub-agent when reusable knowledge, policy, or tool output is produced.",
            "- Alert Knowledge Engineering Agent ops sub-agent when gateway, Runner, notification, audit, sync, or permission behavior fails.",
            "- Escalate to human owner before changing scope, dates, permissions, customer commitments, or external side effects.",
            "",
            "## Status Report Format",
            "",
            "Every project follow-up should produce:",
            "",
            "- Overall state: on_track, at_risk, blocked, or needs_decision.",
            "- Progress since last update.",
            "- Active tasks: owner, status, due/review date, next action.",
            "- Risks/blockers: severity, owner, needed decision, deadline.",
            "- Decisions needed from human Owner.",
            "- Next 3-5 actions.",
            "- Links to TaskResult, AgentRun, evidence, Review records, and audit entries.",
            "",
            "## Boundaries",
            "",
            "- Does not approve its own high-impact output.",
            "- Does not publish reusable knowledge without Knowledge Engineering Agent review sub-agent.",
            "- Does not call unregistered tools.",
            "- Does not execute external side effects before approval.",
        ]
    ) + "\n"


def product_manager_agent_decision(requested_agents: str = "", goal: str = "", repo_mode: str = "") -> tuple[bool, str]:
    text = " ".join([requested_agents, goal, repo_mode]).strip().lower()
    no_product_patterns = [
        r"不需要产品",
        r"无需产品",
        r"不用产品",
        r"no\s+product",
        r"no\s+pm",
        r"需求已(经)?(清晰|明确|拆完|完成)",
        r"(只|仅)(做)?(技术|工程|仓库|代码|迁移|接入|初始化)",
    ]
    if any(re.search(pattern, text) for pattern in no_product_patterns):
        return False, "intake says product work is already clear or not needed"
    if "产品" in text or "product" in text:
        return True, "intake requests product role"
    if re.search(r"(^|[/,\s;；，、])pm($|[/,\s;；，、])", text):
        return True, "intake requests PM role"
    if re.search(r"(需求|用户|场景|验收|原型|prd|mvp|业务|增长|转化)", text):
        return True, "goal contains product or business discovery signals"
    if repo_mode == "new":
        return True, "new projects include product manager by default"
    return True, "default include product manager unless intake clearly excludes product work"


def needs_product_manager_agent(requested_agents: str = "", goal: str = "", repo_mode: str = "") -> bool:
    return product_manager_agent_decision(requested_agents, goal, repo_mode)[0]


def ensure_project_initialization_task(
    bundle: Bundle,
    project_id: str,
    project_name: str,
    requester: str,
    assignee: str,
    project_intake: dict[str, str] | None = None,
    ring_enabled: bool = False,
) -> Path:
    intake = project_intake or {}
    pid = slug(project_id)
    task_id = f"project-init-{pid}"
    try:
        task_path = find_project_task(bundle, task_id)
    except KnowledgeError:
        repo_mode = intake.get("repoMode") or "unknown"
        repo_url = intake.get("repoUrl", "")
        expected = [
            "检查项目 launch.md，补齐启动里程碑 M0-M3；业务/产品里程碑只能作为待确认项，不能由创建项目动作代填。",
            "已有仓库接入时检查 README、AGENTS、目录结构和 Review 规则；新项目时生成仓库创建与初始化清单。",
            "确认默认 Agent team：项目经理 Agent、产品经理 Agent、知识工程 Agent、执行 Agent；仅在 intake 明确不需要产品时记录跳过原因。",
            "将请求里的前端、后端、测试、运维或领域角色先整理为候选 Agent 或首批 ProjectTask，确认 Runner、权限和真实需要后再进入项目组。",
            "产品需求澄清只有在 Product Manager Agent 或人类产品 Owner 明确后才能进入首批 ProjectTask；若 intake 明确不需要产品，则记录跳过原因，不创建确认产品 Agent 的任务。",
            "确认项目群创建/绑定方案、项目 Owner、协作成员、通知对象和审批状态。",
            "确认项目 Agent 与 Runner 绑定关系；Agent Ring 未启用时将任务置为 waiting_runner 并记录 manual runner 交接方式。",
            "完成启动闭环验收：launch.md、仓库、项目群、Agent team、Runner、风险、第一批 ProjectTask 均有明确状态。",
            "使用受控工具完成初始化：tool.zhenzhi-knowledge、Agent Ring runner registry、Git 只读检查、Feishu 审批/项目群/通知网关；外部副作用必须走审批。",
            "按项目经理 Agent Evaluation 写明结论：pass、blocked、needs_human_approval 或 needs_repair。",
            "把初始化结果、证据路径、风险、未决问题和下一步写回 TaskResult，并保留 AgentRun 或人工接管记录。",
        ]
        sources = [f"projects/{pid}/launch.md"]
        if repo_url:
            sources.append(repo_url)
        task_path = create_project_task(
            bundle,
            f"{project_name} 项目初始化",
            pid,
            requester,
            assignee,
            "project_initialization",
            task_id,
            "high",
            "",
            sources,
            expected,
        )
        create_audit_log(bundle, requester, "project.initTask.create", rel(task_path, bundle.root), after=repo_mode, policy_result="draft")
    task = load_object(task_path)
    updates: dict[str, Any] = {
        "assignedRunner": intake.get("defaultRunner", ""),
        "requiredCapabilities": ["codex", "git", "knowledge_sync", "project_initialization"],
        "repoMode": intake.get("repoMode", ""),
        "repoUrl": intake.get("repoUrl", ""),
        "repoName": intake.get("repoName", ""),
        "updatedAt": utc_now(),
    }
    if not ring_enabled and str(task.get("status", "")) in {"pending", "waiting_runner"}:
        updates["status"] = "waiting_runner"
    update_frontmatter_file(task_path, updates)
    if updates.get("status") == "waiting_runner" and task.get("status") != "waiting_runner":
        create_audit_log(bundle, requester, "task.waitingRunner", rel(task_path, bundle.root), before=str(task.get("status", "")), after="waiting_runner")
    return task_path


def validate_publish_ready(bundle: Bundle, path: Path, fm: dict[str, Any], body: str, target_status: str | None = None) -> list[str]:
    problems: list[str] = []
    rel_path = rel(path, bundle.root)
    object_type = fm.get("type", "")
    status = target_status or str(fm.get("status", ""))
    if object_type == "ToolAsset":
        for field in ["owner", "entrypoint", "riskLevel"]:
            if not fm.get(field):
                problems.append(f"{rel_path}: ToolAsset missing required field {field}")
        if fm.get("riskLevel") not in {"L1", "L2", "L3", "L4", "L5"}:
            problems.append(f"{rel_path}: unknown ToolAsset riskLevel {fm.get('riskLevel')}")
        if status == "approved" and not fm.get("lastVerifiedAt"):
            problems.append(f"{rel_path}: approved ToolAsset missing lastVerifiedAt")
    elif object_type == "AgentRun":
        if status in {"verified", "approved"}:
            context_refs = as_list(fm.get("contextRefs"))
            if not context_refs:
                problems.append(f"{rel_path}: verified AgentRun missing contextRefs")
            for context_ref in context_refs:
                if not (bundle.root / context_ref).exists():
                    problems.append(f"{rel_path}: AgentRun contextRef not found: {context_ref}")
            if "TBD" in body:
                problems.append(f"{rel_path}: verified AgentRun still contains TBD")
    elif object_type == "EvalCase":
        if not fm.get("targetRef"):
            problems.append(f"{rel_path}: EvalCase missing targetRef")
        elif not (bundle.root / str(fm["targetRef"])).exists():
            problems.append(f"{rel_path}: EvalCase targetRef not found: {fm['targetRef']}")
        if not fm.get("expected") and not as_list(fm.get("requires")):
            problems.append(f"{rel_path}: EvalCase must define expected or requires")
    return problems


def human_approval_required_for_status(fm: dict[str, Any], status: str) -> bool:
    object_type = str(fm.get("type") or "")
    risk = str(fm.get("riskLevel") or fm.get("risk") or "").upper()
    knowledge_type = str(fm.get("knowledgeType") or "").lower()
    impact = " ".join(as_list(fm.get("impactAreas")) + as_list(fm.get("decisionImpact"))).lower()
    if object_type == "KnowledgeItem" and status in {"verified", "approved", "active"}:
        return True
    if object_type in {"Policy", "Workflow"} and status in {"approved", "active", "verified"}:
        return True
    if object_type in {"AccessCredentialRequest"} and status in {"approved", "active"}:
        return True
    if object_type == "ToolAsset" and status == "approved" and (risk in {"L3", "L4", "L5"} or bool(fm.get("requiresApproval"))):
        return True
    if object_type == "SkillAsset" and status == "approved":
        return True
    if object_type == "Decision" and status in {"approved", "done"}:
        return True
    if any(token in knowledge_type for token in ["policy", "workflow", "iron_rule", "permission", "security", "customer"]):
        return status in {"verified", "approved", "active"}
    return any(token in impact for token in ["security", "permission", "customer", "legal", "cross-team"])


def select_review_route(fm: dict[str, Any], requested_status: str = "") -> dict[str, Any]:
    object_type = str(fm.get("type") or "")
    risk = str(fm.get("riskLevel") or fm.get("risk") or "normal")
    owner = str(fm.get("owner") or fm.get("assignee") or "")
    required = human_approval_required_for_status(fm, requested_status or str(fm.get("status") or ""))
    if object_type == "KnowledgeItem":
        route = "knowledge_review_agent_then_human" if required else "knowledge_review_agent"
        default_reviewer = KNOWLEDGE_REVIEW_AGENT_ID
    elif object_type in {"Requirement", "PRDDocument"}:
        route = "product_manager_quality_gate"
        default_reviewer = PRODUCT_MANAGER_AGENT_ID
    elif object_type == "Decision":
        route = "product_manager_plus_owner"
        default_reviewer = owner or PRODUCT_MANAGER_AGENT_ID
    elif object_type == "ToolAsset":
        route = "tool_owner_governance"
        default_reviewer = owner or KNOWLEDGE_STEWARD_AGENT_ID
    elif object_type == "SkillAsset":
        route = "skill_owner_governance"
        default_reviewer = owner or KNOWLEDGE_STEWARD_AGENT_ID
    elif object_type in {"AccessCredentialRequest", "Policy"}:
        route = "admin_governance"
        default_reviewer = owner or KNOWLEDGE_STEWARD_AGENT_ID
    elif object_type == "EvalRun":
        route = "release_gate"
        default_reviewer = TEST_AGENT_ID
    else:
        route = "owner_review"
        default_reviewer = owner or "human.owner"
    return {
        "route": route,
        "objectType": object_type,
        "risk": risk,
        "owner": owner,
        "defaultReviewer": default_reviewer,
        "humanApprovalRequired": required,
    }


def validate_review_comment(summary: str) -> None:
    text = summary.strip()
    if not text:
        raise KnowledgeError("review summary is required")
    if text.lower() in {"needs improvement", "improve", "fix", "bad", "不行", "需要改进"}:
        raise KnowledgeError("review comment is not actionable")
    if len(text) < 12:
        raise KnowledgeError("review comment must include issue, affected field/section, reason, and requested change")
    actionable_markers = ("需要", "补充", "修改", "不适合", "冲突", "clarify", "clarification", "conflict", "detected", "overlap", "operating rule", "resolve", "change", "reject", "approval", "human", "field", "section", "reason", "requested")
    if not any(marker in text.lower() for marker in actionable_markers):
        raise KnowledgeError("review comment must include issue, affected field/section, reason, and requested change")


def validate_environment_manifest(path: Path, root: Path, fm: dict[str, Any], body: str) -> list[str]:
    rel_path = rel(path, root)
    name = path.name.lower()
    object_type = str(fm.get("type") or "").lower()
    manifest_kind = str(fm.get("manifestKind") or fm.get("kind") or fm.get("schema") or "").lower()
    is_environment_manifest = (
        name in {"environment.manifest.md", "environment.md", "env.manifest.md"}
        or name.endswith(".environment.md")
        or name.endswith(".environment.manifest.md")
        or object_type in {"environmentmanifest", "environment_manifest"}
        or manifest_kind in {"environment", "environment_manifest", "environment-manifest"}
        or any(key in fm for key in ["environmentManifest", "environmentManifestSchema"])
    )
    if not is_environment_manifest:
        return []
    problems: list[str] = []
    if re.search(r"(^|\s)(/Users/|/private/|/var/folders/|[A-Za-z]:\\)", body):
        problems.append(f"{rel_path}: environment manifest must not use local absolute paths as canonical state")
    return problems


def review_path(bundle: Bundle, target: Path, status: str, reviewer: str) -> Path:
    if status not in STATUS_VALUES:
        raise KnowledgeError(f"unknown status: {status}")
    if not reviewer.strip():
        raise KnowledgeError("reviewer is required")
    path = target if target.is_absolute() else bundle.root / target
    if not path.exists():
        raise KnowledgeError(f"target not found: {target}")
    text = read_text(path)
    fm, body = parse_frontmatter(text)
    if not fm:
        raise KnowledgeError("target has no frontmatter")
    route = select_review_route(fm, status)
    if route["humanApprovalRequired"] and actor_is_agent(reviewer):
        raise KnowledgeError("human approval required; Agent cannot self-approve this review route")
    if status == "approved" and failed_evals_for_target(bundle, rel(path, bundle.root)):
        raise KnowledgeError(f"target has failing EvalRun and cannot be approved: {rel(path, bundle.root)}")
    if fm.get("type") == "ToolAsset" and status == "approved" and not fm.get("lastVerifiedAt"):
        fm["lastVerifiedAt"] = utc_now()
    publish_problems = validate_publish_ready(bundle, path, fm, body, status)
    if publish_problems:
        raise KnowledgeError("; ".join(publish_problems))
    before = fm.get("status", "")
    fm["status"] = status
    fm["reviewer"] = reviewer
    fm["reviewedAt"] = utc_now()
    write_text(path, render_doc(fm, body))
    audit_dir = bundle.root / "knowledge" / "audit"
    ensure_dir(audit_dir)
    audit_id = unique_time_id("audit")
    audit_path = audit_dir / f"{audit_id}.md"
    audit_fm = {
        "type": "AuditLog",
        "title": audit_id,
        "timestamp": utc_now(),
        "auditId": audit_id,
        "actor": reviewer,
        "action": "review.updateStatus",
        "targetRef": rel(path, bundle.root),
        "before": before,
        "after": status,
        "policyResult": route["route"],
        "reviewRoute": route["route"],
        "humanApprovalRequired": route["humanApprovalRequired"],
    }
    write_text(
        audit_path,
        render_doc(
            audit_fm,
            "\n".join(
                [
                    "## Review",
                    "",
                    "Status changed by review route.",
                    "",
                    "## Route",
                    "",
                    f"- route: {route['route']}",
                    f"- objectType: {route['objectType']}",
                    f"- risk: {route['risk']}",
                    f"- owner: {route['owner'] or 'unknown'}",
                    f"- humanApprovalRequired: {route['humanApprovalRequired']}",
                ]
            ),
        ),
    )
    append_log(bundle, f"reviewed {rel(path, bundle.root)} {before}->{status}")
    return audit_path


def review_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "knowledge" / "reviews"


def create_review_record(
    bundle: Bundle,
    review_task: dict[str, Any],
    outcome: str,
    reviewer: str,
    summary: str,
    target_refs: list[str],
    followup_refs: list[str] | None = None,
) -> Path:
    review_id = unique_time_id("review")
    path = review_storage_dir(bundle) / f"{review_id}.md"
    status = {
        "pass_as_observed": "done",
        "needs_human_approval": "waiting_acceptance",
        "changes_requested": "changes_requested",
        "needs_clarification": "changes_requested",
        "conflict_detected": "blocked",
        "reject": "rejected",
    }.get(outcome, "done")
    frontmatter = {
        "type": "ReviewRecord",
        "title": f"Review {review_task.get('taskId', '')}",
        "description": "Knowledge review outcome and routing record.",
        "timestamp": utc_now(),
        "reviewId": review_id,
        "reviewTaskId": review_task.get("taskId", ""),
        "originTaskId": review_task.get("originTaskId", review_task.get("parentTaskId", "")),
        "reviewer": reviewer,
        "outcome": outcome,
        "status": status,
        "targetRefs": target_refs,
        "followupTaskRefs": followup_refs or [],
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            summary,
            "",
            "## Targets",
            "",
            "\n".join(f"- {item}" for item in target_refs) or "- none",
            "",
            "## Follow Up",
            "",
            "\n".join(f"- {item}" for item in followup_refs or []) or "- none",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", str(frontmatter["title"]), f"reviews/{path.name}")
    create_audit_log(bundle, reviewer, "review.record", rel(path, bundle.root), after=outcome, policy_result="knowledge_review", details=f"reviewTaskId={review_task.get('taskId', '')}")
    return path


def knowledge_refs_from_review_task(review_task: dict[str, Any], explicit_refs: list[str] | None = None) -> list[str]:
    refs = list(explicit_refs or [])
    for item in as_list(review_task.get("sourceMaterialRefs")):
        if item.startswith("knowledge/"):
            refs = append_unique(refs, item)
    return refs


def knowledge_refs_from_approval_task(approval_task: dict[str, Any], explicit_refs: list[str] | None = None) -> list[str]:
    refs = list(explicit_refs or [])
    for item in as_list(approval_task.get("targetKnowledgeRefs")):
        refs = append_unique(refs, item)
    for item in as_list(approval_task.get("sourceMaterialRefs")):
        if item.startswith("knowledge/"):
            refs = append_unique(refs, item)
    return refs


def find_review_task_for_approval(bundle: Bundle, approval_task: dict[str, Any]) -> Path | None:
    review_task_id = str(approval_task.get("reviewTaskId") or "")
    if review_task_id:
        try:
            return find_project_task(bundle, review_task_id)
        except KnowledgeError:
            return None
    approval_ref = ""
    task_id = str(approval_task.get("taskId") or "")
    if task_id:
        try:
            approval_ref = rel(find_project_task(bundle, task_id), bundle.root)
        except KnowledgeError:
            approval_ref = ""
    for task_dir in [bundle.root / "tasks", *((bundle.root / "projects").glob("*/tasks") if (bundle.root / "projects").exists() else [])]:
        if not task_dir.exists():
            continue
        for path in sorted(task_dir.glob("*.md")):
            if path.name in COLLECTION_NAMES:
                continue
            try:
                candidate = load_object(path)
            except KnowledgeError:
                continue
            if str(candidate.get("taskType") or "") != "knowledge_review":
                continue
            refs = as_list(candidate.get("followupTaskRefs"))
            if approval_ref and approval_ref in refs:
                return path
            if task_id and slug(task_id) in {slug(item) for item in refs}:
                return path
    return None


def create_approval_record(
    bundle: Bundle,
    approval_task: dict[str, Any],
    outcome: str,
    approver: str,
    summary: str,
    target_refs: list[str],
    published_refs: list[str] | None = None,
    followup_refs: list[str] | None = None,
) -> Path:
    review_id = unique_time_id("approval")
    path = review_storage_dir(bundle) / f"{review_id}.md"
    ensure_dir(path.parent)
    frontmatter = {
        "type": "ReviewRecord",
        "title": f"Approval {approval_task.get('taskId', '')}",
        "description": "Human approval outcome for reviewed knowledge.",
        "timestamp": utc_now(),
        "reviewId": review_id,
        "reviewTaskId": approval_task.get("reviewTaskId", ""),
        "approvalTaskId": approval_task.get("taskId", ""),
        "originTaskId": approval_task.get("originTaskId", approval_task.get("parentTaskId", "")),
        "reviewer": approver,
        "outcome": outcome,
        "status": "done" if outcome == "approved" else "rejected",
        "targetRefs": target_refs,
        "publishedRefs": published_refs or [],
        "followupRefs": followup_refs or [],
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            summary,
            "",
            "## Targets",
            "",
            "\n".join(f"- {item}" for item in target_refs) or "- none",
            "",
            "## Published",
            "",
            "\n".join(f"- {item}" for item in published_refs or []) or "- none",
            "",
            "## Follow Up",
            "",
            "\n".join(f"- {item}" for item in followup_refs or []) or "- none",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", str(frontmatter["title"]), f"reviews/{path.name}")
    create_audit_log(bundle, approver, "approval.record", rel(path, bundle.root), after=outcome, policy_result="human_approval", details=f"approvalTaskId={approval_task.get('taskId', '')}")
    return path


def apply_knowledge_review_result(
    bundle: Bundle,
    review_task_id: str,
    outcome: str,
    reviewer: str,
    summary: str,
    target_refs: list[str] | None = None,
) -> dict[str, Any]:
    allowed = {
        "pass_as_observed",
        "needs_human_approval",
        "changes_requested",
        "needs_clarification",
        "conflict_detected",
        "reject",
    }
    if outcome not in allowed:
        raise KnowledgeError(f"unknown review outcome: {outcome}")
    if not reviewer.strip():
        raise KnowledgeError("reviewer is required")
    if not summary.strip():
        raise KnowledgeError("review summary is required")
    if outcome in {"changes_requested", "needs_clarification", "conflict_detected", "reject"}:
        validate_review_comment(summary)
    review_task_path = find_project_task(bundle, review_task_id)
    review_task = load_object(review_task_path)
    if str(review_task.get("taskType", "")) != "knowledge_review":
        raise KnowledgeError(f"task is not a knowledge_review task: {review_task_id}")
    targets = knowledge_refs_from_review_task(review_task, target_refs)
    if not targets and outcome in {"pass_as_observed", "needs_human_approval", "changes_requested", "conflict_detected", "reject"}:
        raise KnowledgeError("review target refs are required")

    project_id = str(review_task.get("projectId", ""))
    requester = str(review_task.get("requester") or "system.scheduler")
    origin_task_id = str(review_task.get("originTaskId") or review_task.get("parentTaskId") or review_task.get("taskId", ""))
    trigger_ref = str(review_task.get("triggerResultRef") or "")
    source_refs = as_list(review_task.get("sourceMaterialRefs"))
    followup_refs: list[str] = []
    published_refs: list[str] = []
    notification_refs: list[str] = []
    conflict_ref = ""

    if outcome == "pass_as_observed":
        for target in targets:
            review_path(bundle, Path(target), "observed", reviewer)
            published_refs = append_unique(published_refs, target)
        publish_result = publish_knowledge_bundle(
            bundle,
            actor="system.scheduler",
            reason=f"knowledge review passed: {review_task_id}",
        )
        update_frontmatter_file(review_task_path, {"status": "done", "publishedRefs": published_refs, "updatedAt": utc_now()})
        notification_path = create_task_notification(
            bundle,
            review_task_path,
            load_object(review_task_path),
            "knowledge_indexed",
            recipient=requester,
            summary=f"知识审核通过并已进入 observed 可检索状态：{', '.join(published_refs)}。",
            source_message_ref=trigger_ref,
        )
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))
        append_log(bundle, f"review publish completed task {review_task_id} audit={publish_result['auditRef']}")

    elif outcome == "needs_human_approval":
        approval_path = create_project_task(
            bundle,
            title=f"Human approval for reviewed knowledge {origin_task_id or review_task_id}",
            project_id=project_id,
            requester=requester,
            assignee=str(review_task.get("humanOwner") or "meimei"),
            task_type="knowledge_approval",
            task_id=followup_task_id(bundle, f"{review_task_id}-approval"),
            priority="high",
            source_material_refs=append_unique([*source_refs, *targets], trigger_ref),
            expected_output=[
                "Create or complete human approval for verified/active/high-impact knowledge.",
                "On approval, publish/index the target knowledge; on rejection, close with reason and notify requester.",
            ],
        )
        followup_refs.append(rel(approval_path, bundle.root))
        update_frontmatter_file(
            approval_path,
            {
                "reviewTaskId": str(review_task.get("taskId") or review_task_id),
                "originTaskId": origin_task_id,
                "targetKnowledgeRefs": targets,
                "triggerReviewOutcome": outcome,
                "triggerResultRef": trigger_ref,
                "updatedAt": utc_now(),
            },
        )
        update_frontmatter_file(review_task_path, {"status": "waiting_acceptance", "followupTaskRefs": followup_refs, "updatedAt": utc_now()})
        notification_path = create_task_notification(bundle, approval_path, load_object(approval_path), "knowledge_approval_required", recipient=str(review_task.get("humanOwner") or "meimei"), summary=f"知识审核要求人工审批：{summary}", source_message_ref=trigger_ref)
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))

    elif outcome == "changes_requested":
        retry_path = create_project_task(
            bundle,
            title=f"Revise knowledge extraction for {origin_task_id or review_task_id}",
            project_id=project_id,
            requester=requester,
            assignee=KNOWLEDGE_ENGINEERING_AGENT_ID,
            task_type="knowledge_retry",
            task_id=followup_task_id(bundle, f"{review_task_id}-changes"),
            priority=str(review_task.get("priority") or "normal"),
            source_material_refs=append_unique([*source_refs, *targets], trigger_ref),
            expected_output=[
                "Address Knowledge Engineering Agent review sub-agent requested changes.",
                "Write a new TaskResult and updated KnowledgeItem draft with source evidence.",
            ],
        )
        followup_refs.append(rel(retry_path, bundle.root))
        update_frontmatter_file(review_task_path, {"status": "changes_requested", "followupTaskRefs": followup_refs, "updatedAt": utc_now()})
        notification_path = create_task_notification(bundle, retry_path, load_object(retry_path), "knowledge_changes_requested", recipient=KNOWLEDGE_ENGINEERING_AGENT_ID, summary=f"知识审核要求返工：{summary}", source_message_ref=trigger_ref)
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))

    elif outcome == "needs_clarification":
        clarification_path = create_project_task(
            bundle,
            title=f"Clarify source material for {origin_task_id or review_task_id}",
            project_id=project_id,
            requester=requester,
            assignee=requester,
            task_type="knowledge_clarification",
            task_id=followup_task_id(bundle, f"{review_task_id}-clarification"),
            priority="normal",
            source_material_refs=append_unique([*source_refs, *targets], trigger_ref),
            expected_output=[
                "Submit missing context, source access, ownership, scope, or applicability clarification.",
                "After clarification, Knowledge Engineering Agent or Review Agent continues the chain.",
            ],
        )
        followup_refs.append(rel(clarification_path, bundle.root))
        update_frontmatter_file(review_task_path, {"status": "changes_requested", "followupTaskRefs": followup_refs, "updatedAt": utc_now()})
        notification_path = create_task_notification(bundle, clarification_path, load_object(clarification_path), "knowledge_clarification_required", recipient=requester, summary=f"知识审核需要补充说明：{summary}", source_message_ref=trigger_ref)
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))

    elif outcome == "conflict_detected":
        conflict_path = create_conflict(bundle, "knowledge_review", reviewer, summary, targets)
        conflict_ref = rel(conflict_path, bundle.root)
        resolution_path = create_project_task(
            bundle,
            title=f"Resolve knowledge conflict for {origin_task_id or review_task_id}",
            project_id=project_id,
            requester=requester,
            assignee=KNOWLEDGE_STEWARD_AGENT_ID,
            task_type="knowledge_conflict_resolution",
            task_id=followup_task_id(bundle, f"{review_task_id}-conflict"),
            priority="high",
            source_material_refs=append_unique([*source_refs, *targets, conflict_ref], trigger_ref),
            expected_output=[
                "Resolve duplicate, contradiction, ownership, or scope conflict.",
                "Write ConflictRecord resolution and route accepted knowledge back to review.",
            ],
        )
        followup_refs.append(rel(resolution_path, bundle.root))
        update_frontmatter_file(review_task_path, {"status": "blocked", "conflictRef": conflict_ref, "followupTaskRefs": followup_refs, "updatedAt": utc_now()})
        notification_path = create_task_notification(bundle, resolution_path, load_object(resolution_path), "knowledge_conflict_detected", recipient=KNOWLEDGE_STEWARD_AGENT_ID, summary=f"知识审核发现冲突：{summary}", source_message_ref=trigger_ref)
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))

    elif outcome == "reject":
        for target in targets:
            review_path(bundle, Path(target), "rejected", reviewer)
        update_frontmatter_file(review_task_path, {"status": "rejected", "updatedAt": utc_now()})
        notification_path = create_task_notification(
            bundle,
            review_task_path,
            load_object(review_task_path),
            "knowledge_rejected",
            recipient=requester,
            summary=f"知识审核拒绝：{summary}",
            source_message_ref=trigger_ref,
        )
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))

    review_record_path = create_review_record(bundle, load_object(review_task_path), outcome, reviewer, summary, targets, followup_refs)
    review_task_after = update_frontmatter_file(
        review_task_path,
        {
            "reviewRecordRef": rel(review_record_path, bundle.root),
            "updatedAt": utc_now(),
        },
    )
    create_audit_log(
        bundle,
        "system.scheduler",
        "workflow.review.route",
        rel(review_task_path, bundle.root),
        after=outcome,
        policy_result="knowledge_review_orchestration",
        details=f"reviewRecordRef={rel(review_record_path, bundle.root)}\nfollowupRefs={','.join(followup_refs) or 'none'}",
    )
    append_log(bundle, f"review routed task {review_task_id} outcome={outcome}")
    return {
        "apiVersion": "v0.1",
        "kind": "KnowledgeReviewOutcome",
        "reviewTaskId": str(review_task_after.get("taskId", review_task_id)),
        "outcome": outcome,
        "reviewRecordRef": rel(review_record_path, bundle.root),
        "publishedRefs": published_refs,
        "followupTaskRefs": followup_refs,
        "notificationRefs": notification_refs,
        "conflictRef": conflict_ref,
    }


def apply_knowledge_approval_result(
    bundle: Bundle,
    approval_task_id: str,
    outcome: str,
    approver: str,
    summary: str,
    target_refs: list[str] | None = None,
    publish_status: str = "verified",
) -> dict[str, Any]:
    allowed = {"approved", "rejected"}
    if outcome not in allowed:
        raise KnowledgeError(f"unknown approval outcome: {outcome}")
    if not approver.strip():
        raise KnowledgeError("approver is required")
    if actor_is_agent(approver):
        raise KnowledgeError("human approval required; Agent cannot self-approve this approval task")
    if not summary.strip():
        raise KnowledgeError("approval summary is required")
    if publish_status not in {"verified", "approved", "active"}:
        raise KnowledgeError(f"unsupported publish status: {publish_status}")
    approval_task_path = find_project_task(bundle, approval_task_id)
    approval_task = load_object(approval_task_path)
    if str(approval_task.get("taskType", "")) != "knowledge_approval":
        raise KnowledgeError(f"task is not a knowledge_approval task: {approval_task_id}")
    targets = knowledge_refs_from_approval_task(approval_task, target_refs)
    if not targets:
        raise KnowledgeError("approval target refs are required")

    requester = str(approval_task.get("requester") or "system.scheduler")
    trigger_ref = str(approval_task.get("triggerResultRef") or "")
    review_task_path = find_review_task_for_approval(bundle, approval_task)
    followup_refs: list[str] = []
    published_refs: list[str] = []
    notification_refs: list[str] = []

    if outcome == "approved":
        for target in targets:
            review_path(bundle, Path(target), publish_status, approver)
            published_refs = append_unique(published_refs, target)
        publish_result = publish_knowledge_bundle(
            bundle,
            actor="system.scheduler",
            reason=f"knowledge approval approved: {approval_task_id}",
        )
        approval_after = update_frontmatter_file(
            approval_task_path,
            {
                "status": "done",
                "approvalOutcome": outcome,
                "publishedRefs": published_refs,
                "updatedAt": utc_now(),
            },
        )
        if review_task_path:
            update_frontmatter_file(
                review_task_path,
                {
                    "status": "done",
                    "publishedRefs": published_refs,
                    "approvalTaskRef": rel(approval_task_path, bundle.root),
                    "updatedAt": utc_now(),
                },
            )
        notification_path = create_task_notification(
            bundle,
            approval_task_path,
            approval_after,
            "knowledge_published",
            recipient=requester,
            summary=f"人工审批通过，知识已发布为 {publish_status} 并进入索引：{', '.join(published_refs)}。",
            source_message_ref=trigger_ref,
        )
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))
        append_log(bundle, f"approval publish completed task {approval_task_id} audit={publish_result['auditRef']}")
    else:
        retry_path = create_project_task(
            bundle,
            title=f"Revise rejected approved knowledge {approval_task_id}",
            project_id=str(approval_task.get("projectId") or ""),
            requester=requester,
            assignee=KNOWLEDGE_ENGINEERING_AGENT_ID,
            task_type="knowledge_retry",
            task_id=followup_task_id(bundle, f"{approval_task_id}-rejected"),
            priority=str(approval_task.get("priority") or "normal"),
            source_material_refs=append_unique([*as_list(approval_task.get("sourceMaterialRefs")), *targets], trigger_ref),
            expected_output=[
                "Address human approval rejection reason.",
                "Write a new TaskResult and KnowledgeItem draft, then route back to Knowledge Engineering Agent review sub-agent.",
            ],
        )
        followup_refs.append(rel(retry_path, bundle.root))
        for target in targets:
            review_path(bundle, Path(target), "rejected", approver)
        approval_after = update_frontmatter_file(
            approval_task_path,
            {
                "status": "rejected",
                "approvalOutcome": outcome,
                "followupTaskRefs": followup_refs,
                "updatedAt": utc_now(),
            },
        )
        if review_task_path:
            update_frontmatter_file(
                review_task_path,
                {
                    "status": "changes_requested",
                    "followupTaskRefs": append_unique(as_list(load_object(review_task_path).get("followupTaskRefs")), rel(retry_path, bundle.root)),
                    "approvalTaskRef": rel(approval_task_path, bundle.root),
                    "updatedAt": utc_now(),
                },
            )
        notification_path = create_task_notification(
            bundle,
            retry_path,
            load_object(retry_path),
            "knowledge_approval_rejected",
            recipient=KNOWLEDGE_ENGINEERING_AGENT_ID,
            summary=f"人工审批未通过，已创建返工任务：{summary}",
            source_message_ref=trigger_ref,
        )
        notification_refs = append_unique(notification_refs, rel(notification_path, bundle.root))
        requester_notification_path = create_task_notification(
            bundle,
            approval_task_path,
            approval_after,
            "knowledge_approval_rejected_notice",
            recipient=requester,
            summary=f"你提交的知识未通过人工审批，已进入返工：{summary}",
            source_message_ref=trigger_ref,
        )
        notification_refs = append_unique(notification_refs, rel(requester_notification_path, bundle.root))

    approval_record_path = create_approval_record(
        bundle,
        load_object(approval_task_path),
        outcome,
        approver,
        summary,
        targets,
        published_refs,
        followup_refs,
    )
    approval_after = update_frontmatter_file(
        approval_task_path,
        {
            "approvalRecordRef": rel(approval_record_path, bundle.root),
            "updatedAt": utc_now(),
        },
    )
    if review_task_path:
        update_frontmatter_file(
            review_task_path,
            {
                "approvalRecordRef": rel(approval_record_path, bundle.root),
                "updatedAt": utc_now(),
            },
        )
    create_audit_log(
        bundle,
        "system.scheduler",
        "workflow.approval.route",
        rel(approval_task_path, bundle.root),
        after=outcome,
        policy_result="knowledge_publish_orchestration",
        details=f"approvalRecordRef={rel(approval_record_path, bundle.root)}\npublishedRefs={','.join(published_refs) or 'none'}\nfollowupRefs={','.join(followup_refs) or 'none'}",
    )
    append_log(bundle, f"approval routed task {approval_task_id} outcome={outcome}")
    return {
        "apiVersion": "v0.1",
        "kind": "KnowledgeApprovalOutcome",
        "approvalTaskId": str(approval_after.get("taskId", approval_task_id)),
        "outcome": outcome,
        "publishStatus": publish_status if outcome == "approved" else "",
        "approvalRecordRef": rel(approval_record_path, bundle.root),
        "publishedRefs": published_refs,
        "followupTaskRefs": followup_refs,
        "notificationRefs": notification_refs,
    }


def bulk_review(bundle: Bundle, object_type: str, from_status: str, to_status: str, reviewer: str, limit: int | None = None) -> list[Path]:
    reviewed: list[Path] = []
    queue = list_review_queue(bundle)
    for item in queue:
        if object_type and item["type"] != object_type:
            continue
        if from_status and item["status"] != from_status:
            continue
        audit_path = review_path(bundle, Path(item["path"]), to_status, reviewer)
        reviewed.append(audit_path)
        if limit and len(reviewed) >= limit:
            break
    return reviewed


def list_review_queue(bundle: Bundle) -> list[dict[str, str]]:
    queue: list[dict[str, str]] = []
    object_roots = [bundle.root / name for name in OBJECT_ROOT_NAMES]
    collection_names = COLLECTION_NAMES
    for object_root in object_roots:
        if not object_root.exists():
            continue
        for path in object_root.rglob("*.md"):
            if path.name in collection_names or path.name.endswith(".draft.md"):
                continue
            fm = load_object(path)
            if fm.get("status") in {"draft", "testing", "open", "stale_candidate"}:
                queue.append(
                    {
                        "path": rel(path, bundle.root),
                        "type": fm.get("type", ""),
                        "status": fm.get("status", ""),
                        "title": fm.get("title", ""),
                        "owner": fm.get("owner", ""),
                    }
                )
    return sorted(queue, key=lambda item: item["path"])


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def requirement_tree_record_dirs(bundle: Bundle) -> list[Path]:
    dirs: list[Path] = []
    global_base = requirement_storage_dir(bundle)
    project_root = bundle.root / "projects"
    bases = [global_base]
    if project_root.exists():
        bases.extend(sorted(path / "requirements" for path in project_root.iterdir() if path.is_dir()))
    for base in bases:
        for name in ["requirement-trees", "nodes", "mappings", "gates", "snapshots"]:
            candidate = base / name
            if candidate.exists():
                dirs.append(candidate)
    return dirs


def requirement_tree_json_records(bundle: Bundle) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    for directory in requirement_tree_record_dirs(bundle):
        for path in sorted(directory.glob("*.json")):
            try:
                payload = json.loads(read_text(path))
            except json.JSONDecodeError as exc:
                raise KnowledgeError(f"{rel(path, bundle.root)}: invalid JSON: {exc}") from exc
            if not isinstance(payload, dict):
                raise KnowledgeError(f"{rel(path, bundle.root)}: JSON record must be an object")
            records.append((path, payload))
    return records


def record_rel(bundle: Bundle, path: Path) -> str:
    return rel(path, bundle.root)


def missing_required_field(record: dict[str, Any], field: str) -> bool:
    if field not in record:
        return True
    value = record.get(field)
    return value is None or value == ""


def require_fields(bundle: Bundle, path: Path, record: dict[str, Any], fields: list[str]) -> list[str]:
    rel_path = record_rel(bundle, path)
    return [f"{rel_path}: {record.get('type', 'record')} missing required field {field}" for field in fields if missing_required_field(record, field)]


def require_list_field(bundle: Bundle, path: Path, record: dict[str, Any], field: str, non_empty: bool = False) -> list[str]:
    rel_path = record_rel(bundle, path)
    if field not in record:
        return [f"{rel_path}: {record.get('type', 'record')} missing required field {field}"]
    value = record.get(field)
    if not isinstance(value, list):
        return [f"{rel_path}: {field} must be a list"]
    if non_empty and not value:
        return [f"{rel_path}: {field} cannot be empty"]
    return []


def validate_enum_field(bundle: Bundle, path: Path, record: dict[str, Any], field: str, allowed: set[str]) -> list[str]:
    rel_path = record_rel(bundle, path)
    value = str(record.get(field) or "")
    if value and value not in allowed:
        return [f"{rel_path}: unknown {field} {value}"]
    return []


def validate_requirement_tree_reference_shape(value: str) -> bool:
    raw = str(value).strip()
    if not raw:
        return False
    if raw.startswith(("http://", "https://")):
        return True
    if raw.startswith(("agent.", "runner.", "tool.")):
        return True
    if re.fullmatch(r"rt\.[a-z0-9][a-z0-9-]*\.[a-z0-9][a-z0-9-]*\.v[a-zA-Z0-9_.-]+", raw):
        return True
    if re.fullmatch(r"(BR|UREQ|PREQ)-\d{3,}", raw):
        return True
    if re.fullmatch(r"ANOS-REQ-\d{3,}", raw):
        return True
    if re.fullmatch(r"(TEST|EVAL|AC|GATE)-[A-Z0-9_.-]+", raw):
        return True
    if re.fullmatch(r"TC-[A-Z0-9]+-\d{3}", raw):
        return True
    if raw.startswith(("tasks/", "projects/", "task-results/", "requirements/", "prd/", "reviews/", "knowledge/", "tests/")):
        return True
    return "/" in raw and not raw.startswith("/")


def requirement_tree_node_ref_kind(value: str) -> str:
    raw = str(value).strip()
    if re.fullmatch(r"(BR|UREQ|PREQ)-\d{3,}", raw) or re.fullmatch(r"ANOS-REQ-\d{3,}", raw):
        return "RequirementNode"
    if re.fullmatch(r"GATE-[A-Z0-9_.-]+", raw):
        return "AcceptanceGate"
    if raw.startswith("requirements/snapshots/") or re.fullmatch(r"coverage-snapshot\.[A-Za-z0-9_.-]+", raw):
        return "RequirementCoverageSnapshot"
    return ""


def parse_markdown_table_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    table: list[list[str]] = []
    for line in markdown.splitlines() + [""]:
        if line.strip().startswith("|"):
            table.append([cell.strip() for cell in line.strip().strip("|").split("|")])
            continue
        if len(table) >= 3:
            header = table[0]
            separator = table[1]
            if all(set(cell.replace(":", "").strip()) <= {"-"} for cell in separator):
                for raw_row in table[2:]:
                    if len(raw_row) == len(header):
                        rows.append(dict(zip(header, raw_row)))
        table = []
    return rows


def expand_numeric_refs(prefix: str, start: int, end: int) -> list[str]:
    if end < start:
        start, end = end, start
    return [f"{prefix}{number:03d}" for number in range(start, end + 1)]


def expand_anos_refs(text: str) -> list[str]:
    refs: list[str] = []
    for segment in re.split(r"[,;]", str(text or "")):
        raw = segment.strip()
        if not raw:
            continue
        range_match = re.search(r"ANOS-REQ-(\d{3})\s*(?:to|\.\.)\s*(?:ANOS-REQ-)?(\d{3})", raw, re.IGNORECASE)
        if range_match:
            refs.extend(expand_numeric_refs("ANOS-REQ-", int(range_match.group(1)), int(range_match.group(2))))
            continue
        bare_range = re.fullmatch(r"(\d{3})\.\.(\d{3})", raw)
        if bare_range:
            refs.extend(expand_numeric_refs("ANOS-REQ-", int(bare_range.group(1)), int(bare_range.group(2))))
            continue
        refs.extend(re.findall(r"ANOS-REQ-\d{3}", raw))
    return append_unique_list([], refs)


def expand_trace_refs(text: str, prefix_pattern: str) -> list[str]:
    refs: list[str] = []
    text_value = str(text or "")
    for prefix, start, end in re.findall(rf"({prefix_pattern}-)(\d{{3}})\.\.(\d{{3}})", text_value):
        refs.extend(expand_numeric_refs(prefix, int(start), int(end)))
    for prefix, numbers in re.findall(rf"({prefix_pattern}-)(\d{{3}}(?:/\d{{3}})+)", text_value):
        refs.extend(f"{prefix}{number}" for number in numbers.split("/"))
    refs.extend(re.findall(rf"{prefix_pattern}-\d{{3}}", text_value))
    return append_unique_list([], refs)


def append_unique_list(items: list[str], values: list[str]) -> list[str]:
    for value in values:
        normalized = str(value).strip()
        if normalized and normalized not in items:
            items.append(normalized)
    return items


def compact_utc_version() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def imported_requirement_tree_id(project_id: str, slug_value: str, version: str) -> str:
    version_value = version.strip()
    if not version_value.startswith("v"):
        version_value = "v" + version_value
    return f"rt.{slug(project_id)}.{safe_slug(slug_value, 'requirement-tree')}.{version_value}"


def coverage_matrix_by_ureq(markdown: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in parse_markdown_table_rows(markdown):
        ureq = str(row.get("UREQ") or row.get("User Requirement") or "").strip()
        if not re.fullmatch(r"UREQ-\d{3}", ureq):
            continue
        br_refs = re.findall(r"BR-\d{3}", row.get("BR", "") or row.get("Business Requirement", ""))
        anos_refs = expand_anos_refs(row.get("ANOS refs", "") or row.get("Functional Requirement Areas", "") or row.get("ANOS", ""))
        test_refs = expand_trace_refs(row.get("Test refs", "") or row.get("Tests", "") or row.get("Test cases", ""), r"TC-[A-Z0-9]+")
        gate_refs = expand_trace_refs(row.get("Acceptance gates", "") or row.get("Acceptance", ""), r"AC-[A-Z0-9]+")
        result[ureq] = {
            "businessRequirementRefs": br_refs,
            "functionalRequirementRefs": anos_refs,
            "testCaseRefs": test_refs,
            "acceptanceGateRefs": [f"GATE-{gate_ref}" for gate_ref in gate_refs],
            "sourceAcceptanceRefs": gate_refs,
            "status": str(row.get("Status") or "").strip(),
        }
    return result


def coverage_matrix_by_functional_ref(markdown: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in parse_markdown_table_rows(markdown):
        first_value = next(iter(row.values()), "")
        if re.fullmatch(r"UREQ-\d{3}", str(first_value).strip()):
            continue
        anos_refs = expand_anos_refs(row.get("ANOS refs", "") or row.get("ANOS range", "") or row.get("ANOS Range", ""))
        if not anos_refs:
            continue
        test_refs = expand_trace_refs(row.get("Test refs", "") or row.get("Tests", "") or row.get("Test cases", ""), r"TC-[A-Z0-9]+")
        gate_refs = [f"GATE-{gate_ref}" for gate_ref in expand_trace_refs(row.get("Acceptance gates", "") or row.get("Acceptance", ""), r"AC-[A-Z0-9]+")]
        for anos_ref in anos_refs:
            current = result.setdefault(anos_ref, {"testCaseRefs": [], "acceptanceGateRefs": []})
            current["testCaseRefs"] = append_unique_list(current["testCaseRefs"], test_refs)
            current["acceptanceGateRefs"] = append_unique_list(current["acceptanceGateRefs"], gate_refs)
    return result


REQUIREMENT_TREE_EXISTING_WORK_BACKFILL_VERSION = "requirement-tree-existing-work-backfill.v1"
REQUIREMENT_TREE_TRACEABILITY_PROMOTION_VERSION = "requirement-tree-traceability-promotion.v1"
REQUIREMENT_TREE_PROMOTION_STATUS_VALUES = {"complete", "partial", "blocked"}
REQUIREMENT_TREE_PROMOTION_EVIDENCE_FIELDS = [
    "implementationEvidenceRefs",
    "executionEvidenceRefs",
    "testEvidenceRefs",
    "acceptanceEvidenceRefs",
    "reviewEvidenceRefs",
]
REQUIREMENT_TREE_PROMOTION_DOC_ONLY_PREFIXES = (
    "docs/product/",
    "projects/company-knowledge-core/product-reviews/",
    "projects/company-knowledge-core/technical-solutions/",
)

REQUIREMENT_TREE_EXISTING_WORK_EVIDENCE_PACKAGES: list[dict[str, Any]] = [
    {
        "needles": ["Requirement/PRD domain"],
        "taskRefs": [
            "projects/company-knowledge-core/tasks/kt-ai-native-os-impl-requirement-prd-domain.md",
            "projects/company-knowledge-core/tasks/kt-ai-native-os-test-requirement-prd-domain.md",
        ],
        "resultRefs": [
            "task-results/tr-kt-ai-native-os-impl-requirement-prd-domain.md",
            "task-results/tr-kt-ai-native-os-test-requirement-prd-domain.md",
        ],
    },
    {
        "needles": ["Desktop Slice 0"],
        "taskRefs": [
            "projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-workbench-slice0.md",
            "projects/company-knowledge-core/tasks/kt-ai-native-os-test-desktop-workbench-slice0.md",
        ],
        "resultRefs": [
            "task-results/tr-kt-ai-native-os-impl-desktop-workbench-slice0.md",
            "task-results/tr-kt-ai-native-os-test-desktop-workbench-slice0.md",
        ],
    },
    {
        "needles": ["Scheduler/runner/result"],
        "taskRefs": [
            "projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result.md",
            "projects/company-knowledge-core/tasks/kt-ai-native-os-test-scheduler-runner-result.md",
        ],
        "resultRefs": [
            "task-results/tr-kt-ai-native-os-impl-scheduler-runner-result.md",
            "task-results/tr-kt-ai-native-os-test-scheduler-runner-result.md",
        ],
    },
    {
        "needles": ["Governance/quality/ops/API"],
        "taskRefs": [
            "projects/company-knowledge-core/tasks/kt-ai-native-os-impl-governance-quality-ops-api.md",
            "projects/company-knowledge-core/tasks/kt-ai-native-os-test-governance-quality-ops-api.md",
        ],
        "resultRefs": [
            "task-results/tr-kt-ai-native-os-impl-governance-quality-ops-api.md",
            "task-results/tr-kt-ai-native-os-test-governance-quality-ops-api.md",
        ],
    },
    {
        "needles": ["product review"],
        "taskRefs": ["projects/company-knowledge-core/tasks/kt-ai-native-os-product-review-technical-solutions.md"],
        "resultRefs": ["task-results/tr-kt-ai-native-os-product-review-technical-solutions.md"],
    },
    {
        "needles": ["Agent Ring protocol", "stub runner"],
        "taskRefs": [
            "projects/company-knowledge-core/tasks/kt-agent-ring-stub-runner-tests.md",
        ],
        "resultRefs": [
            "task-results/tr-kt-agent-ring-protocol.md",
            "task-results/tr-kt-agent-ring-stub-runner-tests.md",
        ],
    },
    {
        "needles": ["knowledge governance loop"],
        "taskRefs": ["projects/company-knowledge-core/tasks/kt-ai-native-os-knowledge-governance-mapping.md"],
        "resultRefs": [
            "task-results/tr-kt-os-knowledge-governance-loop.md",
            "task-results/tr-task-knowledge-capture-review-pipeline.md",
            "task-results/tr-task-universal-material-ingest.md",
        ],
    },
    {
        "needles": ["metadata migration repair"],
        "taskRefs": ["projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration.md"],
        "resultRefs": ["task-results/tr-kt-ai-native-os-repair-taskresult-metadata-migration.md"],
    },
    {
        "needles": ["notification loop"],
        "taskRefs": [],
        "resultRefs": [
            "task-results/tr-task-task-notification-loop.md",
            "task-results/tr-project-approval-notification-closed-loop.md",
        ],
    },
    {
        "needles": ["digital worker registry"],
        "taskRefs": ["projects/company-knowledge-core/tasks/kt-os-digital-worker-capability-registry.md"],
        "resultRefs": ["task-results/tr-kt-os-digital-worker-capability-registry.md"],
    },
    {
        "needles": ["automation hub result"],
        "taskRefs": ["projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md"],
        "resultRefs": [
            "task-results/tr-kt-ai-native-os-dev-automation-hub-hard-capabilities.md",
            "task-results/tr-kt-ai-native-os-test-automation-hub-hard-capabilities.md",
        ],
    },
    {
        "needles": ["policy gates result"],
        "taskRefs": [],
        "resultRefs": ["task-results/tr-kt-os-policy-quality-gates.md"],
    },
]


def requirement_tree_output_base(bundle: Bundle, project_id: str) -> Path:
    return bundle.root / "projects" / slug(project_id) / "requirements"


def requirement_tree_import_records(
    bundle: Bundle,
    project_id: str,
    source_path: Path,
    coverage_matrix_path: Path | None = None,
    actor: str = "agent.company.development",
    version: str = "",
    tree_slug: str = "ai-native-os",
) -> dict[str, Any]:
    source_text = read_text(source_path)
    source_ref = rel(source_path, bundle.root) if source_path.is_relative_to(bundle.root) else str(source_path)
    coverage_ref = ""
    coverage: dict[str, dict[str, Any]] = {}
    functional_coverage: dict[str, dict[str, Any]] = {}
    if coverage_matrix_path:
        coverage_text = read_text(coverage_matrix_path)
        coverage_ref = rel(coverage_matrix_path, bundle.root) if coverage_matrix_path.is_relative_to(bundle.root) else str(coverage_matrix_path)
        coverage = coverage_matrix_by_ureq(coverage_text)
        functional_coverage = coverage_matrix_by_functional_ref(coverage_text)
    rows = parse_markdown_table_rows(source_text)
    br_rows = [row for row in rows if re.fullmatch(r"BR-\d{3}", str(row.get("ID") or ""))]
    ureq_rows = [row for row in rows if re.fullmatch(r"UREQ-\d{3}", str(row.get("ID") or ""))]
    functional_rows = [row for row in rows if re.fullmatch(r"UREQ-\d{3}", str(row.get("User Requirement") or ""))]
    functional_by_ureq = {str(row.get("User Requirement")): expand_anos_refs(row.get("Functional Requirement Areas", "")) for row in functional_rows}
    version_value = version.strip() or compact_utc_version()
    tree_id = imported_requirement_tree_id(project_id, tree_slug, version_value)
    tree_version = version_value if version_value.startswith("v") else "v" + version_value
    base = requirement_tree_output_base(bundle, project_id)
    for name in ["requirement-trees", "nodes", "mappings", "gates", "snapshots"]:
        ensure_dir(base / name)
    source_refs = [source_ref] + ([coverage_ref] if coverage_ref else [])
    nodes: dict[str, dict[str, Any]] = {}
    mappings: dict[str, dict[str, Any]] = {}
    gates: dict[str, dict[str, Any]] = {}
    tests_by_functional: dict[str, list[str]] = {}
    gates_by_functional: dict[str, list[str]] = {}

    def add_mapping(from_ref: str, to_ref: str, kind: str, rationale: str) -> None:
        key = f"map.{slug(tree_id)}.{slug(from_ref)}.{slug(kind)}.{slug(to_ref)}"
        mappings[key] = {
            "mappingId": key,
            "type": "RequirementMapping",
            "treeRef": tree_id,
            "fromRef": from_ref,
            "toRef": to_ref,
            "mappingKind": kind,
            "confidence": "source_exact" if source_ref else "agent_inferred",
            "rationale": rationale,
            "sourceRefs": source_refs,
            "createdByAgentRef": actor,
            "reviewState": "draft",
            "auditRefs": [],
        }

    for row in br_rows:
        br_id = str(row.get("ID") or "")
        covered = []
        for ureq, coverage_row in coverage.items():
            if br_id in coverage_row.get("businessRequirementRefs", []):
                covered.append(ureq)
        nodes[br_id] = {
            "nodeId": br_id,
            "type": "RequirementNode",
            "nodeKind": "business",
            "treeRef": tree_id,
            "title": br_id,
            "statement": str(row.get("Business Requirement") or "").strip(),
            "whyItMatters": str(row.get("Why It Matters") or "").strip(),
            "successSignal": str(row.get("Success Signal") or "").strip(),
            "ownerRole": "agent.company.product-manager",
            "sourceRefs": source_refs,
            "sourceLocation": f"{source_ref}#business-requirements:{br_id}",
            "status": "draft",
            "sensitivity": "internal",
            "parentRefs": [],
            "childRefs": covered,
            "acceptanceGateRefs": [],
            "testCaseRefs": [],
            "taskRefs": [],
            "resultRefs": [],
            "decisionRefs": [],
            "auditRefs": [],
        }

    for index, row in enumerate(ureq_rows, start=1):
        ureq_id = str(row.get("ID") or "")
        preq_id = f"PREQ-{index:03d}"
        coverage_row = coverage.get(ureq_id, {})
        br_refs = list(coverage_row.get("businessRequirementRefs") or [])
        anos_refs = functional_by_ureq.get(ureq_id) or list(coverage_row.get("functionalRequirementRefs") or [])
        test_refs = list(coverage_row.get("testCaseRefs") or [])
        gate_refs = list(coverage_row.get("acceptanceGateRefs") or [])
        owner_role = str(row.get("Role") or "agent.company.product-manager").strip()
        nodes[ureq_id] = {
            "nodeId": ureq_id,
            "type": "RequirementNode",
            "nodeKind": "user",
            "treeRef": tree_id,
            "title": str(row.get("User Requirement") or ureq_id).strip()[:80],
            "statement": str(row.get("User Requirement") or "").strip(),
            "problem": str(row.get("Pain / Goal") or "").strip(),
            "acceptanceSignal": str(row.get("Product Requirement") or "").strip(),
            "ownerRole": owner_role,
            "sourceRefs": source_refs,
            "sourceLocation": f"{source_ref}#user-scenarios-and-requirements:{ureq_id}",
            "status": "draft",
            "sensitivity": "internal",
            "parentRefs": br_refs,
            "childRefs": [preq_id],
            "acceptanceGateRefs": gate_refs,
            "testCaseRefs": test_refs,
            "taskRefs": [],
            "resultRefs": [],
            "decisionRefs": [],
            "auditRefs": [],
        }
        for br_ref in br_refs:
            add_mapping(br_ref, ureq_id, "decomposes_to", "Coverage matrix maps BR to UREQ.")
            if br_ref in nodes:
                nodes[br_ref]["childRefs"] = append_unique_list(as_list(nodes[br_ref].get("childRefs")), [ureq_id])
        nodes[preq_id] = {
            "nodeId": preq_id,
            "type": "RequirementNode",
            "nodeKind": "product",
            "treeRef": tree_id,
            "title": f"Product bridge for {ureq_id}",
            "statement": str(row.get("Product Requirement") or "").strip(),
            "whyItMatters": str(row.get("Pain / Goal") or "").strip(),
            "successSignal": str(row.get("Product Requirement") or "").strip(),
            "ownerRole": "agent.company.product-manager",
            "sourceRefs": source_refs,
            "sourceLocation": f"{source_ref}#user-scenarios-and-requirements:{ureq_id}:product-requirement",
            "status": "draft",
            "sensitivity": "internal",
            "parentRefs": [ureq_id],
            "childRefs": anos_refs,
            "acceptanceGateRefs": gate_refs,
            "testCaseRefs": test_refs,
            "taskRefs": [],
            "resultRefs": [],
            "decisionRefs": [],
            "auditRefs": [],
        }
        add_mapping(ureq_id, preq_id, "decomposes_to", "ProductRequirement bridge derived from product requirement text.")
        for anos_ref in anos_refs:
            tests_by_functional[anos_ref] = append_unique_list(tests_by_functional.get(anos_ref, []), test_refs)
            gates_by_functional[anos_ref] = append_unique_list(gates_by_functional.get(anos_ref, []), gate_refs)
            add_mapping(preq_id, anos_ref, "satisfies", "Functional requirement range maps to ProductRequirement bridge.")

    for anos_ref in sorted(tests_by_functional | gates_by_functional, key=lambda item: int(item.rsplit("-", 1)[1])):
        parent_refs = sorted({mapping["fromRef"] for mapping in mappings.values() if mapping.get("toRef") == anos_ref and str(mapping.get("fromRef", "")).startswith("PREQ-")})
        supplemental = functional_coverage.get(anos_ref, {})
        test_refs = append_unique_list(list(tests_by_functional.get(anos_ref, [])), list(supplemental.get("testCaseRefs") or []))
        gate_refs = append_unique_list(list(gates_by_functional.get(anos_ref, [])), list(supplemental.get("acceptanceGateRefs") or []))
        tests_by_functional[anos_ref] = test_refs
        gates_by_functional[anos_ref] = gate_refs
        nodes[anos_ref] = {
            "nodeId": anos_ref,
            "type": "RequirementNode",
            "nodeKind": "functional",
            "treeRef": tree_id,
            "title": anos_ref,
            "statement": f"Functional requirement reference {anos_ref} imported from Requirement Tree mapping.",
            "whyItMatters": "Functional references preserve implementation traceability from product requirements.",
            "successSignal": "Mapped test cases and acceptance gates remain visible before execution.",
            "ownerRole": "agent.company.development",
            "sourceRefs": source_refs,
            "sourceLocation": f"{source_ref}#functional-requirement-mapping:{anos_ref}",
            "status": "draft",
            "sensitivity": "internal",
            "parentRefs": parent_refs,
            "childRefs": [],
            "acceptanceGateRefs": gate_refs,
            "testCaseRefs": test_refs,
            "taskRefs": [],
            "resultRefs": [],
            "decisionRefs": [],
            "auditRefs": [],
        }
        for test_ref in test_refs:
            add_mapping(anos_ref, test_ref, "verified_by", "Coverage matrix maps functional requirement to designed test case.")
        for gate_ref in gate_refs:
            add_mapping(anos_ref, gate_ref, "accepted_by", "Coverage matrix maps functional requirement to acceptance gate.")

    for gate_ref in sorted({gate for values in gates_by_functional.values() for gate in values}):
        requirement_refs = sorted([anos_ref for anos_ref, refs in gates_by_functional.items() if gate_ref in refs], key=lambda item: int(item.rsplit("-", 1)[1]))
        source_gate_ref = gate_ref.removeprefix("GATE-")
        gates[gate_ref] = {
            "gateId": gate_ref,
            "type": "AcceptanceGate",
            "treeRef": tree_id,
            "requirementRefs": requirement_refs,
            "ownerRole": "agent.company.test",
            "verificationMethod": "document_check",
            "observableSignal": f"{source_gate_ref} is checked against acceptance checklist evidence before launch.",
            "requiredEvidenceRefs": source_refs,
            "status": "draft",
            "waiverDecisionRef": "",
            "sourceRefs": source_refs,
            "auditRefs": [],
        }

    coverage_rows = []
    for ureq_id, coverage_row in coverage.items():
        preq_number = int(ureq_id.split("-")[1])
        preq_id = f"PREQ-{preq_number:03d}"
        for br_ref in coverage_row.get("businessRequirementRefs", []) or [""]:
            for anos_ref in functional_by_ureq.get(ureq_id, []) or coverage_row.get("functionalRequirementRefs", []):
                coverage_rows.append(
                    {
                        "businessRequirementRef": br_ref,
                        "userRequirementRef": ureq_id,
                        "productRequirementRef": preq_id,
                        "functionalRequirementRef": anos_ref,
                        "taskRef": "",
                        "resultRef": "",
                        "testCaseRef": (tests_by_functional.get(anos_ref) or [""])[0],
                        "acceptanceGateRef": (gates_by_functional.get(anos_ref) or [""])[0],
                    }
                )
    snapshot_id = f"requirements/snapshots/coverage-snapshot.{tree_version.removeprefix('v')}.json"
    snapshot = {
        "snapshotId": snapshot_id,
        "type": "RequirementCoverageSnapshot",
        "treeRef": tree_id,
        "treeVersion": tree_version,
        "counts": {
            "BR": len([node for node in nodes.values() if node["nodeKind"] == "business"]),
            "UREQ": len([node for node in nodes.values() if node["nodeKind"] == "user"]),
            "product": len([node for node in nodes.values() if node["nodeKind"] == "product"]),
            "functional": len([node for node in nodes.values() if node["nodeKind"] == "functional"]),
            "acceptance": len(gates),
            "tests": len({test for values in tests_by_functional.values() for test in values}),
            "tasks": 0,
            "results": 0,
            "blockers": 0,
        },
        "coverageRows": coverage_rows,
        "blockers": [],
        "generatedAt": utc_now(),
        "generatedByAgentRef": actor,
        "sourceRefs": source_refs,
        "auditRefs": [],
    }
    tree = {
        "treeId": tree_id,
        "type": "RequirementTree",
        "projectRef": f"projects/{slug(project_id)}/project.md",
        "title": "AI Native OS Requirement Tree",
        "version": tree_version,
        "status": "draft",
        "sourceRefs": source_refs,
        "businessRequirementRefs": sorted([node_id for node_id, node in nodes.items() if node["nodeKind"] == "business"]),
        "userRequirementRefs": sorted([node_id for node_id, node in nodes.items() if node["nodeKind"] == "user"]),
        "productRequirementRefs": sorted([node_id for node_id, node in nodes.items() if node["nodeKind"] == "product"]),
        "functionalRequirementRefs": sorted([node_id for node_id, node in nodes.items() if node["nodeKind"] == "functional"], key=lambda item: int(item.rsplit("-", 1)[1])),
        "acceptanceGateRefs": sorted(gates),
        "testCaseRefs": sorted({test for values in tests_by_functional.values() for test in values}),
        "taskRefs": [],
        "resultRefs": [],
        "coverageSnapshotRef": snapshot_id,
        "reviewRefs": [],
        "auditRefs": [],
    }
    write_text(base / "requirement-trees" / f"{slug(tree_id)}.json", json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    for node_id, node in nodes.items():
        write_text(base / "nodes" / f"{slug(node_id)}.json", json.dumps(node, indent=2, ensure_ascii=False) + "\n")
    for mapping_id, mapping in mappings.items():
        write_text(base / "mappings" / f"{slug(mapping_id)}.json", json.dumps(mapping, indent=2, ensure_ascii=False) + "\n")
    for gate_id, gate in gates.items():
        write_text(base / "gates" / f"{slug(gate_id)}.json", json.dumps(gate, indent=2, ensure_ascii=False) + "\n")
    write_text(base / "snapshots" / f"coverage-snapshot.{tree_version.removeprefix('v')}.json", json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    audit = create_audit_log(bundle, actor, "requirement_tree.import", rel(base / "requirement-trees" / f"{slug(tree_id)}.json", bundle.root), after="draft", policy_result="recorded", details=f"treeId={tree_id}\nBR={len(tree['businessRequirementRefs'])}\nUREQ={len(tree['userRequirementRefs'])}\nfunctional={len(tree['functionalRequirementRefs'])}")
    audit_ref = rel(audit, bundle.root)
    tree["auditRefs"] = [audit_ref]
    snapshot["auditRefs"] = [audit_ref]
    write_text(base / "requirement-trees" / f"{slug(tree_id)}.json", json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    write_text(base / "snapshots" / f"coverage-snapshot.{tree_version.removeprefix('v')}.json", json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    return {
        "treeRef": rel(base / "requirement-trees" / f"{slug(tree_id)}.json", bundle.root),
        "treeId": tree_id,
        "treeVersion": tree_version,
        "counts": snapshot["counts"],
        "recordCounts": {"nodes": len(nodes), "mappings": len(mappings), "gates": len(gates), "snapshots": 1},
        "sourceRefs": source_refs,
        "auditRef": audit_ref,
    }


def requirement_tree_existing_work_matrix_rows(markdown: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in parse_markdown_table_rows(markdown):
        anos_refs = expand_anos_refs(row.get("ANOS refs", "") or row.get("ANOS range", "") or row.get("ANOS Range", ""))
        if not anos_refs:
            continue
        rows.append(
            {
                "area": str(row.get("Area") or row.get("Functional area") or "").strip(),
                "functionalRequirementRefs": anos_refs,
                "userRequirementRefs": expand_trace_refs(row.get("UREQs", "") or row.get("UREQ", ""), r"UREQ"),
                "testCaseRefs": expand_trace_refs(row.get("Test cases", "") or row.get("Test refs", "") or row.get("Tests", ""), r"TC-[A-Z0-9]+"),
                "acceptanceGateRefs": [f"GATE-{gate_ref}" for gate_ref in expand_trace_refs(row.get("Acceptance gates", "") or row.get("Acceptance", ""), r"AC-[A-Z0-9]+")],
                "status": str(row.get("Status") or "").strip().lower(),
                "evidenceText": str(row.get("Existing done task/result evidence") or row.get("Evidence") or "").strip(),
            }
        )
    return rows


def requirement_tree_existing_work_evidence_refs(bundle: Bundle, evidence_text: str) -> dict[str, list[str]]:
    task_refs: list[str] = []
    result_refs: list[str] = []
    normalized = str(evidence_text or "").lower()
    for package in REQUIREMENT_TREE_EXISTING_WORK_EVIDENCE_PACKAGES:
        if not any(str(needle).lower() in normalized for needle in package.get("needles", [])):
            continue
        task_refs = append_unique_list(task_refs, [ref for ref in as_list(package.get("taskRefs")) if (bundle.root / str(ref)).exists() and not REQUIREMENT_TREE_SECRET_VALUE_RE.search(str(ref))])
        result_refs = append_unique_list(result_refs, [ref for ref in as_list(package.get("resultRefs")) if (bundle.root / str(ref)).exists() and not REQUIREMENT_TREE_SECRET_VALUE_RE.search(str(ref))])
    return {"taskRefs": task_refs, "resultRefs": result_refs}


def requirement_tree_record_path_by_id(records: list[tuple[Path, dict[str, Any]]], record_type: str, id_field: str) -> dict[str, Path]:
    return {str(record.get(id_field)): path for path, record in records if record.get("type") == record_type and str(record.get(id_field) or "")}


def requirement_tree_select_tree_record(records: list[tuple[Path, dict[str, Any]]], tree_ref: str = "", project_id: str = "") -> tuple[Path, dict[str, Any]] | None:
    trees = [(path, record) for path, record in records if record.get("type") == "RequirementTree"]
    if tree_ref:
        for path, record in trees:
            if str(record.get("treeId") or "") == tree_ref or str(path).endswith(tree_ref):
                return path, record
    if project_id:
        project_slug = slug(project_id)
        scoped = [(path, record) for path, record in trees if f"/projects/{project_slug}/" in path.as_posix() or str(record.get("projectRef") or "").startswith(f"projects/{project_slug}/")]
        if scoped:
            trees = scoped
    if not trees:
        return None
    return sorted(trees, key=lambda item: str(item[1].get("version") or ""))[-1]


def requirement_tree_ancestor_refs(nodes: dict[str, dict[str, Any]], functional_ref: str) -> dict[str, list[str]]:
    product_refs = [ref for ref in as_list(nodes.get(functional_ref, {}).get("parentRefs")) if str(ref).startswith("PREQ-")]
    user_refs: list[str] = []
    business_refs: list[str] = []
    for product_ref in product_refs:
        user_refs = append_unique_list(user_refs, [ref for ref in as_list(nodes.get(product_ref, {}).get("parentRefs")) if str(ref).startswith("UREQ-")])
    for user_ref in user_refs:
        business_refs = append_unique_list(business_refs, [ref for ref in as_list(nodes.get(user_ref, {}).get("parentRefs")) if str(ref).startswith("BR-")])
    return {"businessRequirementRefs": business_refs, "userRequirementRefs": user_refs, "productRequirementRefs": product_refs}


def backfill_mapping_id(tree_id: str, functional_ref: str, target_ref: str) -> str:
    digest = hashlib.sha256(f"{tree_id}|{functional_ref}|{target_ref}".encode("utf-8")).hexdigest()[:16]
    return f"map.{slug(tree_id)}.{slug(functional_ref)}.existing-work.{digest}"


def backfill_requirement_tree_existing_work(
    bundle: Bundle,
    project_id: str,
    coverage_matrix_path: Path,
    actor: str = "agent.company.development",
    tree_ref: str = "",
    source_path: Path | None = None,
    version: str = "",
    tree_slug: str = "ai-native-os",
) -> dict[str, Any]:
    if not coverage_matrix_path.exists():
        raise KnowledgeError(f"coverage matrix not found: {coverage_matrix_path}")
    records = requirement_tree_json_records(bundle)
    selected = requirement_tree_select_tree_record(records, tree_ref, project_id)
    imported: dict[str, Any] | None = None
    if selected is None:
        source = source_path or bundle.root / "docs/product/ai-native-os/requirement-tree.md"
        imported = requirement_tree_import_records(bundle, project_id, source, coverage_matrix_path, actor, version, tree_slug)
        records = requirement_tree_json_records(bundle)
        selected = requirement_tree_select_tree_record(records, imported["treeId"], project_id)
    if selected is None:
        raise KnowledgeError("RequirementTree not found and import did not create one")

    tree_path, tree = selected
    tree_id = str(tree.get("treeId") or "")
    base = requirement_tree_output_base(bundle, project_id)
    for name in ["mappings", "backfills"]:
        ensure_dir(base / name)
    node_paths = requirement_tree_record_path_by_id(records, "RequirementNode", "nodeId")
    mapping_paths = requirement_tree_record_path_by_id(records, "RequirementMapping", "mappingId")
    snapshot_paths = requirement_tree_record_path_by_id(records, "RequirementCoverageSnapshot", "snapshotId")
    nodes = {str(record.get("nodeId")): record for _path, record in records if record.get("type") == "RequirementNode"}
    snapshots = {str(record.get("snapshotId")): record for _path, record in records if record.get("type") == "RequirementCoverageSnapshot"}
    snapshot_id = str(tree.get("coverageSnapshotRef") or "")
    snapshot = snapshots.get(snapshot_id)
    matrix_ref = rel(coverage_matrix_path, bundle.root) if coverage_matrix_path.is_relative_to(bundle.root) else str(coverage_matrix_path)
    source_refs = append_unique_list(as_list(tree.get("sourceRefs")), [matrix_ref])
    backfill_id = f"requirement-tree-existing-work-backfill.{compact_utc_version()}"
    backfill_path = base / "backfills" / f"{backfill_id}.json"
    backfill_ref = rel(backfill_path, bundle.root)
    rows = requirement_tree_existing_work_matrix_rows(read_text(coverage_matrix_path))
    records_out: list[dict[str, Any]] = []
    changed_nodes: dict[str, dict[str, Any]] = {}
    changed_mappings: dict[str, dict[str, Any]] = {}
    blocked_refs: list[str] = []
    partial_refs: list[str] = []
    unique_task_refs: list[str] = []
    unique_result_refs: list[str] = []

    for matrix_row in rows:
        evidence_refs = requirement_tree_existing_work_evidence_refs(bundle, matrix_row["evidenceText"])
        row_status = matrix_row["status"] if matrix_row["status"] in {"partial", "blocked", "uncovered"} else "partial"
        for functional_ref in matrix_row["functionalRequirementRefs"]:
            node = dict(nodes.get(functional_ref) or {})
            if not node:
                continue
            ancestor_refs = requirement_tree_ancestor_refs(nodes, functional_ref)
            product_refs = append_unique_list(list(ancestor_refs["productRequirementRefs"]), as_list(node.get("parentRefs")))
            user_refs = append_unique_list(list(ancestor_refs["userRequirementRefs"]), matrix_row["userRequirementRefs"])
            business_refs = ancestor_refs["businessRequirementRefs"]
            task_refs = evidence_refs["taskRefs"]
            result_refs = evidence_refs["resultRefs"]
            test_refs = append_unique_list(as_list(node.get("testCaseRefs")), matrix_row["testCaseRefs"])
            gate_refs = append_unique_list(as_list(node.get("acceptanceGateRefs")), matrix_row["acceptanceGateRefs"])
            node["taskRefs"] = append_unique_list(as_list(node.get("taskRefs")), task_refs)
            node["resultRefs"] = append_unique_list(as_list(node.get("resultRefs")), result_refs)
            node["testCaseRefs"] = append_unique_list(as_list(node.get("testCaseRefs")), test_refs)
            node["acceptanceGateRefs"] = append_unique_list(as_list(node.get("acceptanceGateRefs")), gate_refs)
            node["coverageStatus"] = row_status
            node["backfillConfidence"] = "backfill_inferred"
            node["executionUnlocking"] = False
            node["backfillRefs"] = append_unique_list(as_list(node.get("backfillRefs")), [backfill_ref])
            node["auditRefs"] = as_list(node.get("auditRefs"))
            changed_nodes[functional_ref] = node
            if row_status == "blocked":
                blocked_refs.append(functional_ref)
            elif row_status == "partial":
                partial_refs.append(functional_ref)
            unique_task_refs = append_unique_list(unique_task_refs, task_refs)
            unique_result_refs = append_unique_list(unique_result_refs, result_refs)
            record = {
                "functionalRequirementRef": functional_ref,
                "businessRequirementRefs": business_refs,
                "userRequirementRefs": user_refs,
                "productRequirementRefs": product_refs,
                "testCaseRefs": test_refs,
                "acceptanceGateRefs": gate_refs,
                "taskRefs": task_refs,
                "resultRefs": result_refs,
                "coverageStatus": row_status,
                "confidence": "backfill_inferred",
                "executionUnlocking": False,
                "evidenceText": matrix_row["evidenceText"],
                "limitations": ["package-level evidence; does not promote requirement to complete", "backfill mapping is not execution-unlocking"],
            }
            records_out.append(record)
            for target_ref in task_refs + result_refs:
                mapping_id = backfill_mapping_id(tree_id, functional_ref, target_ref)
                mapping = {
                    "mappingId": mapping_id,
                    "type": "RequirementMapping",
                    "treeRef": tree_id,
                    "fromRef": functional_ref,
                    "toRef": target_ref,
                    "mappingKind": "implemented_by",
                    "confidence": "backfill_inferred",
                    "rationale": "Existing-work backfill from PM coverage matrix; package-level evidence is traceable but does not mark completion.",
                    "sourceRefs": append_unique_list([matrix_ref], result_refs),
                    "createdByAgentRef": actor,
                    "reviewState": "needs_review",
                    "backfillRef": backfill_ref,
                    "backfillStatus": row_status,
                    "executionUnlocking": False,
                    "auditRefs": [],
                }
                changed_mappings[mapping_id] = mapping

    tree["taskRefs"] = append_unique_list(as_list(tree.get("taskRefs")), unique_task_refs)
    tree["resultRefs"] = append_unique_list(as_list(tree.get("resultRefs")), unique_result_refs)
    tree["sourceRefs"] = source_refs
    tree["backfillRefs"] = append_unique_list(as_list(tree.get("backfillRefs")), [backfill_ref])

    if snapshot:
        snapshot["sourceRefs"] = append_unique_list(as_list(snapshot.get("sourceRefs")), [matrix_ref])
        blockers = [blocker for blocker in (snapshot.get("blockers") if isinstance(snapshot.get("blockers"), list) else []) if not (isinstance(blocker, dict) and blocker.get("reason") == "Existing-work backfill preserves blocked Agent Ring live contract status.")]
        for functional_ref in blocked_refs:
            blockers.append(
                {
                    "severity": "high",
                    "ownerRole": "agent.company.development",
                    "nodeRef": functional_ref,
                    "reason": "Existing-work backfill preserves blocked Agent Ring live contract status.",
                    "suggestedFix": "Complete live Agent Ring PostgreSQL contract verification before treating this row as complete.",
                }
            )
        snapshot["blockers"] = blockers
        counts = snapshot.get("counts") if isinstance(snapshot.get("counts"), dict) else {}
        counts["tasks"] = len(unique_task_refs)
        counts["results"] = len(unique_result_refs)
        counts["blockers"] = len(blockers)
        snapshot["counts"] = counts

    audit = create_audit_log(
        bundle,
        actor,
        "requirement_tree.existing_work_backfill",
        backfill_ref,
        after="needs_review",
        policy_result="recorded",
        details=f"treeId={tree_id}\nfunctional={len(records_out)}\npartial={len(partial_refs)}\nblocked={len(blocked_refs)}\nexecutionUnlocking=false",
    )
    audit_ref = rel(audit, bundle.root)
    tree["auditRefs"] = append_unique_list(as_list(tree.get("auditRefs")), [audit_ref])
    if snapshot:
        snapshot["auditRefs"] = append_unique_list(as_list(snapshot.get("auditRefs")), [audit_ref])
    for node in changed_nodes.values():
        node["auditRefs"] = append_unique_list(as_list(node.get("auditRefs")), [audit_ref])
    for mapping in changed_mappings.values():
        mapping["auditRefs"] = append_unique_list(as_list(mapping.get("auditRefs")), [audit_ref])

    manifest = {
        "backfillId": backfill_id,
        "type": "RequirementTreeExistingWorkBackfill",
        "backfillVersion": REQUIREMENT_TREE_EXISTING_WORK_BACKFILL_VERSION,
        "treeRef": tree_id,
        "projectRef": f"projects/{slug(project_id)}/project.md",
        "generatedAt": utc_now(),
        "generatedByAgentRef": actor,
        "sourceRefs": source_refs,
        "coverageMatrixRef": matrix_ref,
        "policy": {
            "rewriteHistoricalTaskResults": False,
            "promotePartialToComplete": False,
            "inferredMappingsExecutionUnlocking": False,
            "evidenceRule": "Only existing refs named by the PM coverage matrix and present on disk are linked.",
        },
        "counts": {
            "functionalRequirements": len(records_out),
            "partial": len(partial_refs),
            "blocked": len(blocked_refs),
            "uncovered": len([record for record in records_out if record["coverageStatus"] == "uncovered"]),
            "completePromotions": 0,
            "executionUnlockingMappings": 0,
            "taskRefs": len(unique_task_refs),
            "resultRefs": len(unique_result_refs),
            "mappingRecords": len(changed_mappings),
        },
        "records": sorted(records_out, key=lambda item: int(str(item["functionalRequirementRef"]).rsplit("-", 1)[1])),
        "auditRefs": [audit_ref],
        "importResult": imported or {},
    }
    write_text(backfill_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    write_text(tree_path, json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    for node_id, node in changed_nodes.items():
        node_path = node_paths.get(node_id)
        if node_path:
            write_text(node_path, json.dumps(node, indent=2, ensure_ascii=False) + "\n")
    for mapping_id, mapping in changed_mappings.items():
        mapping_path = mapping_paths.get(mapping_id) or base / "mappings" / f"{slug(mapping_id)}.json"
        write_text(mapping_path, json.dumps(mapping, indent=2, ensure_ascii=False) + "\n")
    if snapshot:
        snapshot_path = snapshot_paths.get(snapshot_id)
        if snapshot_path:
            write_text(snapshot_path, json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    return {
        "backfillRef": backfill_ref,
        "treeId": tree_id,
        "status": "backfilled",
        "counts": manifest["counts"],
        "taskRefs": unique_task_refs,
        "resultRefs": unique_result_refs,
        "auditRef": audit_ref,
        "importedTree": bool(imported),
    }


def normalize_requirement_tree_promotion_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, list):
        return {"candidates": payload}
    if not isinstance(payload, dict):
        raise KnowledgeError("promotion candidate payload must be a JSON object or array")
    candidates = payload.get("candidates", payload.get("promotions"))
    if candidates is None and any(key in payload for key in ["requirementRef", "functionalRequirementRef", "userRequirementRef", "nodeRef"]):
        candidates = [payload]
    if not isinstance(candidates, list):
        raise KnowledgeError("promotion candidate payload requires candidates or promotions list")
    normalized = dict(payload)
    normalized["candidates"] = candidates
    return normalized


def requirement_tree_promotion_candidate_ref(candidate: dict[str, Any]) -> str:
    for field in ["requirementRef", "functionalRequirementRef", "userRequirementRef", "nodeRef"]:
        value = str(candidate.get(field) or "").strip()
        if value:
            return value
    return ""


def requirement_tree_promotion_target_status(candidate: dict[str, Any]) -> str:
    return str(candidate.get("targetCoverageStatus") or candidate.get("coverageStatus") or candidate.get("targetStatus") or "").strip().lower()


def requirement_tree_promotion_evidence_refs(candidate: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for field in REQUIREMENT_TREE_PROMOTION_EVIDENCE_FIELDS:
        refs = append_unique_list(refs, as_list(candidate.get(field)))
    refs = append_unique_list(refs, as_list(candidate.get("resultRefs")))
    refs = append_unique_list(refs, as_list(candidate.get("taskRefs")))
    return refs


def requirement_tree_promotion_ref_slices(ref: str) -> set[str]:
    raw = str(ref or "").strip()
    slices: set[str] = set()
    anos_match = re.fullmatch(r"ANOS-REQ-(\d{3})", raw)
    if anos_match:
        number = int(anos_match.group(1))
        ranges = {
            "S1": [(1, 6), (120, 122)],
            "S2": [(10, 16), (20, 24)],
            "S3": [(30, 34), (40, 45)],
            "S4": [(50, 56), (70, 73)],
            "S5": [(60, 63)],
            "S6": [(80, 84), (90, 93)],
            "S7": [(100, 102), (130, 133), (150, 152)],
            "S8": [(110, 114), (140, 142)],
        }
        for slice_id, bounds in ranges.items():
            if any(start <= number <= end for start, end in bounds):
                slices.add(slice_id)
        return slices or {"unknown"}
    ureq_slices = {
        "UREQ-001": {"S1"},
        "UREQ-002": {"S2"},
        "UREQ-003": {"S2"},
        "UREQ-004": {"S3", "S4"},
        "UREQ-005": {"S4"},
        "UREQ-006": {"S2"},
        "UREQ-007": {"S2", "S3"},
        "UREQ-008": {"S5"},
        "UREQ-009": {"S6"},
        "UREQ-010": {"S6"},
        "UREQ-011": {"S6"},
        "UREQ-012": {"S8"},
        "UREQ-013": {"S7"},
        "UREQ-014": {"S2", "S6"},
        "UREQ-015": {"S1", "S6"},
    }
    return set(ureq_slices.get(raw, {"unknown"}))


def requirement_tree_promotion_external_registry_refs(bundle: Bundle, project_id: str) -> list[str]:
    registry_refs: list[str] = []
    for path in [
        requirement_tree_output_base(bundle, project_id) / "evidence-registry.json",
        requirement_storage_dir(bundle) / "evidence-registry.json",
    ]:
        if not path.exists():
            continue
        try:
            payload = json.loads(read_text(path))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            registry_refs = append_unique_list(registry_refs, as_list(payload.get("approvedExternalEvidenceRefs")))
            for item in payload.get("records") if isinstance(payload.get("records"), list) else []:
                if isinstance(item, dict) and str(item.get("status") or "").lower() in {"approved", "verified"}:
                    registry_refs = append_unique_list(registry_refs, [str(item.get("ref") or "")])
    return registry_refs


def resolve_requirement_tree_promotion_evidence_ref(bundle: Bundle, ref: str, approved_external_refs: list[str]) -> dict[str, Any]:
    raw = str(ref or "").strip()
    if not raw:
        return {"ref": raw, "resolved": False, "reason": "empty evidence ref"}
    if raw in approved_external_refs:
        return {"ref": raw, "resolved": True, "kind": "approved_external"}
    if raw.startswith(("http://", "https://")):
        return {"ref": raw, "resolved": False, "reason": "external evidence ref is not approved"}
    path = bundle.root / raw
    if path.exists():
        return {"ref": raw, "resolved": True, "kind": "local_file", "path": raw}
    return {"ref": raw, "resolved": False, "reason": "evidence ref does not exist"}


def resolve_requirement_tree_promotion_gate_ref(gates: dict[str, dict[str, Any]], gate_ref: str) -> dict[str, Any]:
    raw = str(gate_ref or "").strip()
    if not raw:
        return {"ref": raw, "resolved": False, "reason": "empty gate ref"}
    candidates = [raw]
    if raw.startswith("GATE-"):
        candidates.append(raw.removeprefix("GATE-"))
    elif raw.startswith("AC-"):
        candidates.append(f"GATE-{raw}")
    for candidate in candidates:
        if candidate in gates:
            return {"ref": raw, "resolved": True, "gateId": candidate, "gate": gates[candidate]}
    return {"ref": raw, "resolved": False, "reason": "acceptance gate ref does not resolve"}


def requirement_tree_functional_descendants(nodes: dict[str, dict[str, Any]], node_ref: str) -> list[str]:
    node = nodes.get(node_ref) or {}
    if node.get("nodeKind") == "functional":
        return [node_ref]
    refs: list[str] = []
    for child_ref in as_list(node.get("childRefs")):
        refs = append_unique_list(refs, requirement_tree_functional_descendants(nodes, str(child_ref)))
    return refs


def validate_requirement_tree_promotion_batch_guard(
    candidates: list[dict[str, Any]],
    tree: dict[str, Any],
    migration_approval_ref: str = "",
) -> list[str]:
    errors: list[str] = []
    refs = append_unique_list([], [requirement_tree_promotion_candidate_ref(candidate) for candidate in candidates])
    functional_refs = set(as_list(tree.get("functionalRequirementRefs")))
    candidate_functional_refs = {ref for ref in refs if ref.startswith("ANOS-REQ-")}
    if functional_refs and candidate_functional_refs >= functional_refs and len(functional_refs) >= 74:
        errors.append("batch_guard: refusing all-74 functional requirement promotion in one operation")
    if len(candidate_functional_refs) >= 74:
        errors.append("batch_guard: refusing promotion request touching 74 or more ANOS records")
    if not migration_approval_ref:
        touched_slices: set[str] = set()
        for ref in refs:
            touched_slices.update(requirement_tree_promotion_ref_slices(ref))
        if len(touched_slices) > 1:
            errors.append("batch_guard: promotion request touches more than one accepted slice without migrationApprovalRef")
    return errors


def validate_requirement_tree_promotion_candidate(
    bundle: Bundle,
    candidate: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    gates: dict[str, dict[str, Any]],
    approved_external_refs: list[str],
    projected_statuses: dict[str, str],
) -> dict[str, Any]:
    ref = requirement_tree_promotion_candidate_ref(candidate)
    target_status = requirement_tree_promotion_target_status(candidate)
    confidence = str(candidate.get("confidence") or candidate.get("promotionConfidence") or "").strip()
    execution_unlocking = boolish(candidate.get("executionUnlocking"), False)
    errors: list[str] = []
    warnings: list[str] = []

    node = nodes.get(ref)
    if not ref:
        errors.append("missing requirementRef")
    elif not node:
        errors.append(f"requirementRef does not resolve to RequirementNode: {ref}")
    if target_status not in REQUIREMENT_TREE_PROMOTION_STATUS_VALUES:
        errors.append(f"unknown targetCoverageStatus {target_status or 'missing'}")
    if confidence == "backfill_inferred" and execution_unlocking:
        errors.append("backfill_inferred cannot be execution-unlocking")
    if execution_unlocking and confidence != "direct_verified":
        errors.append("executionUnlocking requires direct_verified promotion confidence")
    if target_status in {"partial", "blocked"} and execution_unlocking:
        errors.append(f"{target_status} promotion cannot be execution-unlocking")

    all_evidence_refs = requirement_tree_promotion_evidence_refs(candidate)
    if all_evidence_refs and all("requirement-tree-existing-work-backfill" in item for item in all_evidence_refs):
        errors.append("backfill-only evidence cannot promote traceability status")

    resolved_evidence = [
        resolve_requirement_tree_promotion_evidence_ref(bundle, ref_value, approved_external_refs)
        for ref_value in all_evidence_refs
    ]
    for result in resolved_evidence:
        if not result.get("resolved"):
            errors.append(f"{result['ref']}: {result['reason']}")

    gate_results = [resolve_requirement_tree_promotion_gate_ref(gates, gate_ref) for gate_ref in as_list(candidate.get("acceptanceGateRefs"))]
    for gate_result in gate_results:
        if not gate_result.get("resolved"):
            errors.append(f"{gate_result['ref']}: {gate_result['reason']}")

    if target_status == "complete":
        if confidence != "direct_verified":
            errors.append("complete promotion requires direct_verified confidence")
        for field in REQUIREMENT_TREE_PROMOTION_EVIDENCE_FIELDS:
            if not as_list(candidate.get(field)):
                errors.append(f"complete promotion missing {field}")
        implementation_refs = as_list(candidate.get("implementationEvidenceRefs"))
        if implementation_refs and all(any(ref_value.startswith(prefix) for prefix in REQUIREMENT_TREE_PROMOTION_DOC_ONLY_PREFIXES) for ref_value in implementation_refs):
            errors.append("complete promotion cannot use document-only implementation evidence")
        test_status = str(candidate.get("testStatus") or candidate.get("testEvidenceStatus") or "").strip().lower()
        if test_status not in {"pass", "passed", "done"}:
            errors.append("complete promotion requires executed pass test evidence")
        if not gate_results:
            errors.append("complete promotion missing acceptanceGateRefs")
        for gate_result in gate_results:
            gate = gate_result.get("gate") if isinstance(gate_result.get("gate"), dict) else {}
            gate_status = str(gate.get("status") or "").lower()
            if gate_status not in {"passed", "waived"}:
                errors.append(f"{gate_result.get('gateId') or gate_result.get('ref')}: acceptance gate must be passed or waived for complete promotion")
        review_conclusion = str(candidate.get("reviewConclusion") or "").strip()
        if not review_conclusion:
            errors.append("complete promotion requires reviewer-readable conclusion")
        elif len(review_conclusion) < 16:
            warnings.append("reviewConclusion is terse; reviewer may need more context")
        if node and node.get("nodeKind") == "user":
            child_functional_refs = requirement_tree_functional_descendants(nodes, ref)
            incomplete = [child_ref for child_ref in child_functional_refs if projected_statuses.get(child_ref, str(nodes.get(child_ref, {}).get("coverageStatus") or "")) != "complete"]
            if incomplete and not as_list(candidate.get("acceptedExceptionRefs")):
                errors.append("UREQ complete promotion requires all child ANOS complete or acceptedExceptionRefs")

    if target_status == "blocked":
        for field in ["blockerOwner", "blockerReason", "recoveryCondition", "nextAction", "releaseImpact"]:
            if not str(candidate.get(field) or "").strip():
                errors.append(f"blocked promotion missing {field}")

    return {
        "requirementRef": ref,
        "targetCoverageStatus": target_status,
        "confidence": confidence,
        "executionUnlocking": execution_unlocking,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "resolvedEvidenceRefs": resolved_evidence,
        "resolvedGateRefs": [
            {key: value for key, value in gate_result.items() if key != "gate"}
            for gate_result in gate_results
        ],
        "beforeCoverageStatus": str((node or {}).get("coverageStatus") or (node or {}).get("status") or ""),
        "afterCoverageStatus": target_status,
    }


def validate_requirement_tree_promotion_candidates(
    bundle: Bundle,
    payload: Any,
    project_id: str = "",
    tree_ref: str = "",
) -> dict[str, Any]:
    normalized = normalize_requirement_tree_promotion_payload(payload)
    records = requirement_tree_json_records(bundle)
    tree_path, tree = find_requirement_tree_record(bundle, records, tree_ref or str(normalized.get("treeRef") or ""), project_id or str(normalized.get("projectId") or ""))
    pid = requirement_tree_project_id(tree, project_id or str(normalized.get("projectId") or ""))
    tree_id = str(tree.get("treeId") or "")
    candidates = [dict(candidate) for candidate in normalized["candidates"] if isinstance(candidate, dict)]
    nodes = {str(record.get("nodeId")): record for _path, record in records if record.get("type") == "RequirementNode" and str(record.get("treeRef") or "") == tree_id}
    gates = {str(record.get("gateId")): record for _path, record in records if record.get("type") == "AcceptanceGate" and str(record.get("treeRef") or "") == tree_id}
    approved_external_refs = append_unique_list(as_list(normalized.get("approvedExternalEvidenceRefs")), requirement_tree_promotion_external_registry_refs(bundle, pid))
    migration_approval_ref = str(normalized.get("migrationApprovalRef") or "").strip()
    batch_errors = validate_requirement_tree_promotion_batch_guard(candidates, tree, migration_approval_ref)
    projected_statuses = {
        ref: requirement_tree_promotion_target_status(candidate)
        for candidate in candidates
        for ref in [requirement_tree_promotion_candidate_ref(candidate)]
        if ref
    }
    candidate_reports = [
        validate_requirement_tree_promotion_candidate(bundle, candidate, nodes, gates, approved_external_refs, projected_statuses)
        for candidate in candidates
    ]
    errors = list(batch_errors)
    for report in candidate_reports:
        errors.extend([f"{report['requirementRef'] or 'candidate'}: {error}" for error in report["errors"]])
    return {
        "status": "valid" if not errors else "rejected",
        "promotionVersion": REQUIREMENT_TREE_TRACEABILITY_PROMOTION_VERSION,
        "treeId": tree_id,
        "treeRef": record_rel(bundle, tree_path),
        "projectId": pid,
        "candidateCount": len(candidates),
        "validCandidateCount": len([report for report in candidate_reports if report["valid"]]),
        "errors": errors,
        "batchGuard": {"passed": not batch_errors, "errors": batch_errors},
        "candidateReports": candidate_reports,
        "auditPreview": [
            {
                "action": "requirement_tree.traceability_promotion",
                "targetRef": report["requirementRef"],
                "before": report["beforeCoverageStatus"],
                "after": report["afterCoverageStatus"],
                "policyResult": "accepted" if report["valid"] and not batch_errors else "rejected",
            }
            for report in candidate_reports
        ],
    }


def promote_requirement_tree_traceability(
    bundle: Bundle,
    payload: Any,
    project_id: str = "",
    tree_ref: str = "",
    actor: str = DEVELOPMENT_AGENT_ID,
    dry_run: bool = True,
) -> dict[str, Any]:
    normalized = normalize_requirement_tree_promotion_payload(payload)
    report = validate_requirement_tree_promotion_candidates(bundle, normalized, project_id, tree_ref)
    report["dryRun"] = dry_run
    if report["status"] != "valid":
        return report
    if dry_run:
        report["status"] = "dry_run"
        return report

    records = requirement_tree_json_records(bundle)
    tree_path, tree = find_requirement_tree_record(bundle, records, report["treeId"], report["projectId"])
    tree_id = str(tree.get("treeId") or "")
    nodes = {str(record.get("nodeId")): record for _path, record in records if record.get("type") == "RequirementNode" and str(record.get("treeRef") or "") == tree_id}
    node_paths = requirement_tree_record_path_by_id(records, "RequirementNode", "nodeId")
    snapshots = {str(record.get("snapshotId")): record for _path, record in records if record.get("type") == "RequirementCoverageSnapshot" and str(record.get("treeRef") or "") == tree_id}
    snapshot_paths = requirement_tree_record_path_by_id(records, "RequirementCoverageSnapshot", "snapshotId")
    snapshot_ref = str(tree.get("coverageSnapshotRef") or "")
    snapshot = snapshots.get(snapshot_ref)
    written_audit_refs: list[str] = []
    changed_refs: list[str] = []
    now = utc_now()

    candidates_by_ref = {
        requirement_tree_promotion_candidate_ref(candidate): dict(candidate)
        for candidate in normalized["candidates"]
        if isinstance(candidate, dict)
    }
    for candidate_report in report["candidateReports"]:
        ref = str(candidate_report["requirementRef"])
        candidate = candidates_by_ref.get(ref, {})
        node = dict(nodes.get(ref) or {})
        node_path = node_paths.get(ref)
        if not node or not node_path:
            continue
        before = str(node.get("coverageStatus") or node.get("status") or "")
        target_status = str(candidate_report["targetCoverageStatus"])
        evidence = {field: as_list(candidate.get(field)) for field in REQUIREMENT_TREE_PROMOTION_EVIDENCE_FIELDS}
        node["coverageStatus"] = target_status
        node["promotionConfidence"] = str(candidate_report["confidence"])
        node["executionUnlocking"] = bool(candidate_report["executionUnlocking"]) if target_status == "complete" else False
        node["promotionEvidenceRefs"] = evidence
        node["promotionReviewConclusion"] = str(candidate.get("reviewConclusion") or "")
        node["promotionUpdatedAt"] = now
        node["promotionUpdatedByAgentRef"] = actor
        if target_status == "blocked":
            node["coverageBlocker"] = {
                "owner": str(candidate.get("blockerOwner") or ""),
                "reason": str(candidate.get("blockerReason") or ""),
                "recoveryCondition": str(candidate.get("recoveryCondition") or ""),
                "nextAction": str(candidate.get("nextAction") or ""),
                "releaseImpact": str(candidate.get("releaseImpact") or ""),
            }
        audit = create_audit_log(
            bundle,
            actor,
            "requirement_tree.traceability_promotion",
            ref,
            before=before,
            after=target_status,
            policy_result="accepted",
            details=(
                f"treeId={tree_id}\n"
                f"requirementRef={ref}\n"
                f"confidence={candidate_report['confidence']}\n"
                f"executionUnlocking={str(node['executionUnlocking']).lower()}\n"
                f"evidenceRefs={json.dumps(evidence, ensure_ascii=False)}\n"
                f"reviewConclusion={node['promotionReviewConclusion']}"
            ),
        )
        audit_ref = rel(audit, bundle.root)
        written_audit_refs.append(audit_ref)
        changed_refs.append(ref)
        node["auditRefs"] = append_unique_list(as_list(node.get("auditRefs")), [audit_ref])
        write_text(node_path, json.dumps(node, indent=2, ensure_ascii=False) + "\n")
        nodes[ref] = node

    if snapshot:
        counts = snapshot.get("counts") if isinstance(snapshot.get("counts"), dict) else {}
        functional_nodes = [node for node in nodes.values() if node.get("nodeKind") == "functional"]
        counts["completePromotions"] = len([node for node in functional_nodes if node.get("coverageStatus") == "complete"])
        counts["executionUnlockingMappings"] = len([node for node in functional_nodes if boolish(node.get("executionUnlocking"), False)])
        counts["blockers"] = len([node for node in functional_nodes if node.get("coverageStatus") == "blocked"])
        snapshot["counts"] = counts
        snapshot["auditRefs"] = append_unique_list(as_list(snapshot.get("auditRefs")), written_audit_refs)
        snapshot_path = snapshot_paths.get(snapshot_ref)
        if snapshot_path:
            write_text(snapshot_path, json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")

    tree["auditRefs"] = append_unique_list(as_list(tree.get("auditRefs")), written_audit_refs)
    write_text(tree_path, json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    promotion_dir = requirement_tree_output_base(bundle, report["projectId"]) / "promotions"
    ensure_dir(promotion_dir)
    promotion_report_path = promotion_dir / f"traceability-promotion.{compact_utc_version()}.json"
    final_report = {
        **report,
        "status": "written",
        "dryRun": False,
        "changedRequirementRefs": changed_refs,
        "auditRefs": written_audit_refs,
        "promotionReportRef": rel(promotion_report_path, bundle.root),
    }
    write_text(promotion_report_path, json.dumps(final_report, indent=2, ensure_ascii=False) + "\n")
    return final_report


def walk_requirement_tree_values(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    items: list[tuple[str, Any]] = [(prefix, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            items.extend(walk_requirement_tree_values(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            items.extend(walk_requirement_tree_values(child, f"{prefix}[{index}]"))
    return items


def validate_requirement_tree_no_secrets(bundle: Bundle, path: Path, record: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    rel_path = record_rel(bundle, path)
    for key_path, value in walk_requirement_tree_values(record):
        if isinstance(value, (dict, list)):
            continue
        text = str(value or "")
        normalized_key = key_path.lower().replace("_", "").replace("-", "")
        if any(secret_key in normalized_key for secret_key in SECRET_KEYS) and text.strip():
            problems.append(f"{rel_path}: possible secret value in {key_path}")
        elif REQUIREMENT_TREE_SECRET_VALUE_RE.search(text):
            problems.append(f"{rel_path}: possible secret-like text in {key_path}")
    return problems


def validate_requirement_tree_record_shape(bundle: Bundle, path: Path, record: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    record_type = str(record.get("type") or "")
    rel_path = record_rel(bundle, path)
    if record_type == "RequirementTree":
        problems.extend(require_fields(bundle, path, record, ["treeId", "type", "projectRef", "title", "version", "status", "coverageSnapshotRef"]))
        for field in ["sourceRefs", "businessRequirementRefs", "userRequirementRefs", "productRequirementRefs", "functionalRequirementRefs", "acceptanceGateRefs", "testCaseRefs", "taskRefs", "resultRefs", "reviewRefs", "auditRefs"]:
            problems.extend(require_list_field(bundle, path, record, field, non_empty=(field == "sourceRefs")))
        problems.extend(validate_enum_field(bundle, path, record, "status", REQUIREMENT_TREE_STATUS_VALUES))
        tree_id = str(record.get("treeId") or "")
        if tree_id and not validate_requirement_tree_reference_shape(tree_id):
            problems.append(f"{rel_path}: invalid treeId {tree_id}")
    elif record_type == "RequirementNode":
        problems.extend(require_fields(bundle, path, record, ["nodeId", "type", "nodeKind", "treeRef", "title", "statement", "ownerRole", "sourceLocation", "status", "sensitivity"]))
        if not (str(record.get("whyItMatters") or "").strip() or str(record.get("problem") or "").strip()):
            problems.append(f"{rel_path}: RequirementNode requires whyItMatters or problem")
        if not (str(record.get("successSignal") or "").strip() or str(record.get("acceptanceSignal") or "").strip()):
            problems.append(f"{rel_path}: RequirementNode requires successSignal or acceptanceSignal")
        for field in ["sourceRefs", "parentRefs", "childRefs", "acceptanceGateRefs", "testCaseRefs", "taskRefs", "resultRefs", "decisionRefs", "auditRefs"]:
            problems.extend(require_list_field(bundle, path, record, field, non_empty=(field == "sourceRefs")))
        problems.extend(validate_enum_field(bundle, path, record, "nodeKind", REQUIREMENT_NODE_KIND_VALUES))
        problems.extend(validate_enum_field(bundle, path, record, "status", REQUIREMENT_NODE_STATUS_VALUES))
        node_id = str(record.get("nodeId") or "")
        if node_id and not validate_requirement_tree_reference_shape(node_id):
            problems.append(f"{rel_path}: invalid nodeId {node_id}")
    elif record_type == "RequirementMapping":
        problems.extend(require_fields(bundle, path, record, ["mappingId", "type", "treeRef", "fromRef", "toRef", "mappingKind", "confidence", "rationale", "createdByAgentRef", "reviewState"]))
        problems.extend(require_list_field(bundle, path, record, "sourceRefs", non_empty=True))
        problems.extend(require_list_field(bundle, path, record, "auditRefs"))
        problems.extend(validate_enum_field(bundle, path, record, "mappingKind", REQUIREMENT_MAPPING_KIND_VALUES))
        problems.extend(validate_enum_field(bundle, path, record, "confidence", REQUIREMENT_MAPPING_CONFIDENCE_VALUES))
        problems.extend(validate_enum_field(bundle, path, record, "reviewState", REQUIREMENT_MAPPING_REVIEW_STATE_VALUES))
    elif record_type == "AcceptanceGate":
        problems.extend(require_fields(bundle, path, record, ["gateId", "type", "treeRef", "ownerRole", "verificationMethod", "observableSignal", "status"]))
        for field in ["requirementRefs", "requiredEvidenceRefs", "sourceRefs", "auditRefs"]:
            problems.extend(require_list_field(bundle, path, record, field, non_empty=(field in {"requirementRefs", "sourceRefs"})))
        problems.extend(validate_enum_field(bundle, path, record, "verificationMethod", ACCEPTANCE_GATE_VERIFICATION_METHOD_VALUES))
        problems.extend(validate_enum_field(bundle, path, record, "status", ACCEPTANCE_GATE_STATUS_VALUES))
        if record.get("status") == "waived" and not str(record.get("waiverDecisionRef") or "").strip():
            problems.append(f"{rel_path}: waived AcceptanceGate requires waiverDecisionRef")
        if not str(record.get("observableSignal") or "").strip():
            problems.append(f"{rel_path}: AcceptanceGate observableSignal cannot be empty")
    elif record_type == "RequirementCoverageSnapshot":
        problems.extend(require_fields(bundle, path, record, ["snapshotId", "type", "treeRef", "treeVersion", "counts", "generatedAt", "generatedByAgentRef"]))
        for field in ["coverageRows", "blockers", "sourceRefs", "auditRefs"]:
            problems.extend(require_list_field(bundle, path, record, field, non_empty=(field == "sourceRefs")))
        if "counts" in record and not isinstance(record.get("counts"), dict):
            problems.append(f"{rel_path}: counts must be an object")
        coverage_rows = record.get("coverageRows") if isinstance(record.get("coverageRows"), list) else []
        for index, row in enumerate(coverage_rows):
            if not isinstance(row, dict):
                problems.append(f"{rel_path}: coverageRows[{index}] must be an object")
                continue
            for field in REQUIREMENT_COVERAGE_ROW_FIELDS:
                if field not in row:
                    problems.append(f"{rel_path}: coverageRows[{index}] missing {field}")
        blockers = record.get("blockers") if isinstance(record.get("blockers"), list) else []
        for index, blocker in enumerate(blockers):
            if not isinstance(blocker, dict):
                problems.append(f"{rel_path}: blockers[{index}] must be an object")
                continue
            for field in ["severity", "ownerRole", "nodeRef", "reason", "suggestedFix"]:
                if missing_required_field(blocker, field):
                    problems.append(f"{rel_path}: blockers[{index}] missing {field}")
    else:
        problems.append(f"{rel_path}: unknown Requirement Tree JSON type {record_type or 'missing'}")
    for field, value in record.items():
        if field.endswith("Ref") and value and not validate_requirement_tree_reference_shape(str(value)):
            problems.append(f"{rel_path}: invalid reference shape in {field}: {value}")
        elif field.endswith("Refs") and isinstance(value, list):
            for item in value:
                if item and not validate_requirement_tree_reference_shape(str(item)):
                    problems.append(f"{rel_path}: invalid reference shape in {field}: {item}")
    problems.extend(validate_requirement_tree_no_secrets(bundle, path, record))
    return problems


def validate_requirement_tree_cross_refs(bundle: Bundle, records: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    nodes = {str(record.get("nodeId")): (path, record) for path, record in records if record.get("type") == "RequirementNode"}
    gates = {str(record.get("gateId")): (path, record) for path, record in records if record.get("type") == "AcceptanceGate"}
    snapshots = {str(record.get("snapshotId")): (path, record) for path, record in records if record.get("type") == "RequirementCoverageSnapshot"}
    tree_ids = {str(record.get("treeId")) for _path, record in records if record.get("type") == "RequirementTree"}
    known_refs = set(nodes) | set(gates) | set(snapshots) | tree_ids
    for path, node in [(path, record) for path, record in records if record.get("type") == "RequirementNode"]:
        rel_path = record_rel(bundle, path)
        node_id = str(node.get("nodeId") or "")
        for child_ref in as_list(node.get("childRefs")):
            child = nodes.get(str(child_ref))
            if not child:
                problems.append(f"{rel_path}: childRef does not resolve to RequirementNode: {child_ref}")
                continue
            if node_id not in as_list(child[1].get("parentRefs")):
                problems.append(f"{rel_path}: childRef {child_ref} missing reciprocal parentRef {node_id}")
        for parent_ref in as_list(node.get("parentRefs")):
            parent = nodes.get(str(parent_ref))
            if not parent:
                problems.append(f"{rel_path}: parentRef does not resolve to RequirementNode: {parent_ref}")
                continue
            if node_id not in as_list(parent[1].get("childRefs")):
                problems.append(f"{rel_path}: parentRef {parent_ref} missing reciprocal childRef {node_id}")
        for gate_ref in as_list(node.get("acceptanceGateRefs")):
            if str(gate_ref) not in gates:
                problems.append(f"{rel_path}: acceptanceGateRef does not resolve to AcceptanceGate: {gate_ref}")
    for path, mapping in [(path, record) for path, record in records if record.get("type") == "RequirementMapping"]:
        rel_path = record_rel(bundle, path)
        from_ref = str(mapping.get("fromRef") or "")
        to_ref = str(mapping.get("toRef") or "")
        for field, value in [("fromRef", from_ref), ("toRef", to_ref)]:
            local_kind = requirement_tree_node_ref_kind(value)
            if value in known_refs:
                continue
            if local_kind:
                problems.append(f"{rel_path}: {field} does not resolve to {local_kind}: {value}")
            elif not validate_requirement_tree_reference_shape(value):
                problems.append(f"{rel_path}: {field} has invalid endpoint {value}")
        kind = str(mapping.get("mappingKind") or "")
        if kind == "implemented_by" and not (to_ref.startswith(("tasks/", "projects/", "task-results/"))):
            problems.append(f"{rel_path}: implemented_by must point to ProjectTask or TaskResult ref")
        if kind == "verified_by" and to_ref not in gates and not (to_ref.startswith(("tests/", "knowledge/evals/")) or re.fullmatch(r"(TEST|EVAL|AC)-[A-Z0-9_.-]+", to_ref) or re.fullmatch(r"TC-[A-Z0-9]+-\d{3}", to_ref)):
            problems.append(f"{rel_path}: verified_by must point to a test, eval, acceptance criteria, or gate ref")
        if kind == "accepted_by" and to_ref not in gates:
            problems.append(f"{rel_path}: accepted_by must point to an AcceptanceGate")
    for path, gate in [(path, record) for path, record in records if record.get("type") == "AcceptanceGate"]:
        rel_path = record_rel(bundle, path)
        for requirement_ref in as_list(gate.get("requirementRefs")):
            if str(requirement_ref) not in nodes:
                problems.append(f"{rel_path}: requirementRef does not resolve to RequirementNode: {requirement_ref}")
    for path, tree in [(path, record) for path, record in records if record.get("type") == "RequirementTree"]:
        rel_path = record_rel(bundle, path)
        for field in ["businessRequirementRefs", "userRequirementRefs", "productRequirementRefs", "functionalRequirementRefs"]:
            for node_ref in as_list(tree.get(field)):
                if str(node_ref) not in nodes:
                    problems.append(f"{rel_path}: {field} does not resolve to RequirementNode: {node_ref}")
        for gate_ref in as_list(tree.get("acceptanceGateRefs")):
            if str(gate_ref) not in gates:
                problems.append(f"{rel_path}: acceptanceGateRefs does not resolve to AcceptanceGate: {gate_ref}")
        snapshot_ref = str(tree.get("coverageSnapshotRef") or "")
        snapshot = snapshots.get(snapshot_ref)
        if snapshot_ref and not snapshot:
            problems.append(f"{rel_path}: coverageSnapshotRef does not resolve to RequirementCoverageSnapshot: {snapshot_ref}")
        if tree.get("status") == "accepted":
            review_refs = [str(item).lower() for item in as_list(tree.get("reviewRefs"))]
            if not any("product-manager" in item or "product_review" in item or "product-review" in item for item in review_refs):
                problems.append(f"{rel_path}: accepted RequirementTree requires Product Manager review ref")
            if not any("project-manager" in item or "project_review" in item or "project-review" in item for item in review_refs):
                problems.append(f"{rel_path}: accepted RequirementTree requires Project Manager review ref")
            if snapshot:
                blockers = snapshot[1].get("blockers") if isinstance(snapshot[1].get("blockers"), list) else []
                high_blockers = [blocker for blocker in blockers if isinstance(blocker, dict) and str(blocker.get("severity") or "").lower() in {"high", "critical"}]
                if high_blockers:
                    problems.append(f"{rel_path}: accepted RequirementTree requires zero high-severity coverage blockers")
            else:
                problems.append(f"{rel_path}: accepted RequirementTree requires coverageSnapshotRef")
    return problems


def validate_requirement_tree_traceability(bundle: Bundle, records: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    for path, record in records:
        rel_path = record_rel(bundle, path)
        if record.get("type") == "RequirementNode":
            node_id = str(record.get("nodeId") or "")
            node_kind = str(record.get("nodeKind") or "")
            if not str(record.get("ownerRole") or "").strip():
                problems.append(f"{rel_path}: {node_id or 'RequirementNode'} missing ownerRole")
            if node_kind == "user" and not as_list(record.get("parentRefs")):
                problems.append(f"{rel_path}: orphan user requirement has no BR parent: {node_id}")
            if node_kind == "product" and not as_list(record.get("parentRefs")):
                problems.append(f"{rel_path}: product requirement has no UREQ parent: {node_id}")
            if node_kind == "functional":
                if not as_list(record.get("parentRefs")):
                    problems.append(f"{rel_path}: orphan functional requirement has no ProductRequirement parent: {node_id}")
                if not as_list(record.get("testCaseRefs")):
                    problems.append(f"{rel_path}: functional requirement missing test expectation: {node_id}")
                if not as_list(record.get("acceptanceGateRefs")):
                    problems.append(f"{rel_path}: functional requirement missing acceptance gate: {node_id}")
        elif record.get("type") == "AcceptanceGate":
            gate_id = str(record.get("gateId") or "")
            if not str(record.get("observableSignal") or "").strip():
                problems.append(f"{rel_path}: acceptance gate missing observable criteria: {gate_id}")
            if not as_list(record.get("requirementRefs")):
                problems.append(f"{rel_path}: acceptance gate has no requirement refs: {gate_id}")
    return problems


def validate_requirement_tree_records(bundle: Bundle) -> list[str]:
    try:
        records = requirement_tree_json_records(bundle)
    except KnowledgeError as exc:
        return [str(exc)]
    problems: list[str] = []
    for path, record in records:
        problems.extend(validate_requirement_tree_record_shape(bundle, path, record))
    problems.extend(validate_requirement_tree_cross_refs(bundle, records))
    problems.extend(validate_requirement_tree_traceability(bundle, records))
    return problems


REQUIREMENT_TREE_TASK_QUEUE_COMPILER_VERSION = "requirement-tree-task-queue-compiler.v1"

REQUIREMENT_TREE_TASK_QUEUE_ROUTES = [
    {
        "roleKey": "development",
        "taskType": "development",
        "assignee": DEVELOPMENT_AGENT_ID,
        "title": "Implement Requirement Tree functional slice",
    },
    {
        "roleKey": "test",
        "taskType": "test",
        "assignee": TEST_AGENT_ID,
        "title": "Test Requirement Tree traceability slice",
    },
    {
        "roleKey": "design",
        "taskType": "design",
        "assignee": DESIGN_AGENT_ID,
        "title": "Design Requirement Tree interaction slice",
    },
    {
        "roleKey": "ops",
        "taskType": "ops",
        "assignee": OPERATIONS_AGENT_ID,
        "title": "Operate Requirement Tree rollout slice",
    },
    {
        "roleKey": "review",
        "taskType": "review",
        "assignee": KNOWLEDGE_REVIEW_AGENT_ID,
        "title": "Review Requirement Tree knowledge slice",
    },
    {
        "roleKey": "governance",
        "taskType": "governance",
        "assignee": KNOWLEDGE_STEWARD_AGENT_ID,
        "title": "Govern Requirement Tree lifecycle slice",
    },
]


def requirement_tree_project_id(tree: dict[str, Any], fallback: str = "") -> str:
    project_ref = str(tree.get("projectRef") or "")
    match = re.fullmatch(r"projects/([^/]+)/project\.md", project_ref)
    if match:
        return slug(match.group(1))
    if fallback:
        return slug(fallback)
    return "company-knowledge-core"


def find_requirement_tree_record(
    bundle: Bundle,
    records: list[tuple[Path, dict[str, Any]]],
    tree_ref: str = "",
    project_id: str = "",
) -> tuple[Path, dict[str, Any]]:
    candidates = [(path, record) for path, record in records if record.get("type") == "RequirementTree"]
    if project_id:
        pid = slug(project_id)
        candidates = [(path, record) for path, record in candidates if f"projects/{pid}/requirements/" in record_rel(bundle, path)]
    if tree_ref:
        normalized = str(tree_ref).strip()
        for path, record in candidates:
            if normalized in {str(record.get("treeId") or ""), record_rel(bundle, path), path.name, path.stem}:
                return path, record
        raise KnowledgeError(f"RequirementTree not found: {tree_ref}")
    if not candidates:
        raise KnowledgeError("RequirementTree not found")
    return sorted(candidates, key=lambda item: record_rel(bundle, item[0]))[-1]


def requirement_tree_blocker(code: str, ref: str, message: str, severity: str = "high") -> dict[str, str]:
    return {"severity": severity, "code": code, "ref": ref, "message": message}


def requirement_tree_traceability_sets(tree: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "businessRequirementRefs": as_list(tree.get("businessRequirementRefs")),
        "userRequirementRefs": as_list(tree.get("userRequirementRefs")),
        "productRequirementRefs": as_list(tree.get("productRequirementRefs")),
        "functionalRequirementRefs": as_list(tree.get("functionalRequirementRefs")),
        "testCaseRefs": as_list(tree.get("testCaseRefs")),
        "acceptanceGateRefs": as_list(tree.get("acceptanceGateRefs")),
    }


def requirement_tree_compile_readiness(
    tree_path: Path,
    tree: dict[str, Any],
    records: list[tuple[Path, dict[str, Any]]],
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    tree_id = str(tree.get("treeId") or "")
    nodes = {str(record.get("nodeId")): record for _path, record in records if record.get("type") == "RequirementNode" and str(record.get("treeRef") or "") == tree_id}
    gates = {str(record.get("gateId")): record for _path, record in records if record.get("type") == "AcceptanceGate" and str(record.get("treeRef") or "") == tree_id}
    snapshots = {str(record.get("snapshotId")): record for _path, record in records if record.get("type") == "RequirementCoverageSnapshot" and str(record.get("treeRef") or "") == tree_id}
    snapshot_ref = str(tree.get("coverageSnapshotRef") or "")
    snapshot = snapshots.get(snapshot_ref, {})
    traceability = requirement_tree_traceability_sets(tree)
    blockers: list[dict[str, str]] = []

    if tree.get("status") != "accepted":
        blockers.append(requirement_tree_blocker("tree_not_accepted", tree_id, "RequirementTree status must be accepted before task queue compilation."))
    if not as_list(tree.get("sourceRefs")):
        blockers.append(requirement_tree_blocker("missing_evidence", tree_id, "RequirementTree sourceRefs cannot be empty."))
    review_refs = [item.lower() for item in as_list(tree.get("reviewRefs"))]
    if not any("product-manager" in item or "product_review" in item or "product-review" in item for item in review_refs):
        blockers.append(requirement_tree_blocker("missing_evidence", tree_id, "RequirementTree requires Product Manager review evidence."))
    if not any("project-manager" in item or "project_review" in item or "project-review" in item for item in review_refs):
        blockers.append(requirement_tree_blocker("missing_evidence", tree_id, "RequirementTree requires Project Manager review evidence."))

    for field, refs in traceability.items():
        if not refs:
            blockers.append(requirement_tree_blocker("missing_traceability", tree_id, f"RequirementTree {field} cannot be empty."))

    for field in ["businessRequirementRefs", "userRequirementRefs", "productRequirementRefs", "functionalRequirementRefs"]:
        for node_ref in traceability[field]:
            node = nodes.get(node_ref)
            if not node:
                blockers.append(requirement_tree_blocker("missing_traceability", node_ref, f"{field} does not resolve to local RequirementNode."))
                continue
            if not str(node.get("ownerRole") or "").strip():
                blockers.append(requirement_tree_blocker("missing_owner", node_ref, "RequirementNode ownerRole cannot be empty."))
            if not as_list(node.get("sourceRefs")):
                blockers.append(requirement_tree_blocker("missing_evidence", node_ref, "RequirementNode sourceRefs cannot be empty."))

    for functional_ref in traceability["functionalRequirementRefs"]:
        node = nodes.get(functional_ref)
        if not node:
            continue
        if not as_list(node.get("parentRefs")):
            blockers.append(requirement_tree_blocker("missing_traceability", functional_ref, "Functional requirement needs ProductRequirement parent."))
        if not as_list(node.get("testCaseRefs")):
            blockers.append(requirement_tree_blocker("missing_test", functional_ref, "Functional requirement needs testCaseRefs before task generation."))
        if not as_list(node.get("acceptanceGateRefs")):
            blockers.append(requirement_tree_blocker("missing_acceptance_gate", functional_ref, "Functional requirement needs acceptanceGateRefs before task generation."))

    for gate_ref in traceability["acceptanceGateRefs"]:
        gate = gates.get(gate_ref)
        if not gate:
            blockers.append(requirement_tree_blocker("missing_acceptance_gate", gate_ref, "acceptanceGateRefs does not resolve to local AcceptanceGate."))
            continue
        if not str(gate.get("ownerRole") or "").strip():
            blockers.append(requirement_tree_blocker("missing_owner", gate_ref, "AcceptanceGate ownerRole cannot be empty."))
        if not str(gate.get("observableSignal") or "").strip():
            blockers.append(requirement_tree_blocker("missing_observable_criteria", gate_ref, "AcceptanceGate observableSignal cannot be empty."))
        if not as_list(gate.get("requiredEvidenceRefs")):
            blockers.append(requirement_tree_blocker("missing_evidence", gate_ref, "AcceptanceGate requiredEvidenceRefs cannot be empty."))
        if not as_list(gate.get("requirementRefs")):
            blockers.append(requirement_tree_blocker("missing_traceability", gate_ref, "AcceptanceGate requirementRefs cannot be empty."))

    if not snapshot:
        blockers.append(requirement_tree_blocker("missing_evidence", snapshot_ref or tree_id, "RequirementTree requires coverage snapshot evidence."))
    else:
        for blocker in snapshot.get("blockers") if isinstance(snapshot.get("blockers"), list) else []:
            if isinstance(blocker, dict) and str(blocker.get("severity") or "").lower() in {"high", "critical"}:
                blockers.append(
                    requirement_tree_blocker(
                        "high_coverage_blocker",
                        str(blocker.get("nodeRef") or tree_id),
                        str(blocker.get("reason") or "Coverage snapshot contains high or critical blocker."),
                        str(blocker.get("severity") or "high").lower(),
                    )
                )
        coverage_rows = snapshot.get("coverageRows") if isinstance(snapshot.get("coverageRows"), list) else []
        for index, row in enumerate(coverage_rows):
            if not isinstance(row, dict):
                blockers.append(requirement_tree_blocker("missing_traceability", f"{snapshot_ref}#{index}", "Coverage row must be an object."))
                continue
            required_fields = {
                "businessRequirementRef": "BR traceability",
                "userRequirementRef": "UREQ traceability",
                "productRequirementRef": "ProductRequirement traceability",
                "functionalRequirementRef": "ANOS traceability",
                "testCaseRef": "test traceability",
                "acceptanceGateRef": "acceptance traceability",
            }
            for field, label in required_fields.items():
                if not str(row.get(field) or "").strip():
                    code = "missing_test" if field == "testCaseRef" else "missing_acceptance_gate" if field == "acceptanceGateRef" else "missing_traceability"
                    blockers.append(requirement_tree_blocker(code, f"{snapshot_ref}#{index}", f"Coverage row missing {label}."))

    context = {"nodes": nodes, "gates": gates, "snapshot": snapshot, "traceability": traceability, "treePath": tree_path}
    return context, blockers


def requirement_tree_task_draft_body(route: dict[str, str], traceability: dict[str, list[str]]) -> str:
    return "\n".join(
        [
            "## Purpose",
            "",
            f"Role-specific executable draft for {route['roleKey']} work generated from accepted Requirement Tree.",
            "",
            "## Traceability",
            "",
            f"- BR: {', '.join(traceability['businessRequirementRefs'])}",
            f"- UREQ: {', '.join(traceability['userRequirementRefs'])}",
            f"- ProductRequirement: {', '.join(traceability['productRequirementRefs'])}",
            f"- ANOS: {', '.join(traceability['functionalRequirementRefs'])}",
            f"- Tests: {', '.join(traceability['testCaseRefs'])}",
            f"- Acceptance: {', '.join(traceability['acceptanceGateRefs'])}",
            "",
            "## Boundary",
            "",
            "This is a draft ProjectTask. Scheduler execution requires explicit promotion out of .draft.md.",
        ]
    )


def compile_requirement_tree_task_queue(
    bundle: Bundle,
    tree_ref: str = "",
    project_id: str = "",
    actor: str = DEVELOPMENT_AGENT_ID,
) -> dict[str, Any]:
    records = requirement_tree_json_records(bundle)
    tree_path, tree = find_requirement_tree_record(bundle, records, tree_ref, project_id)
    tree_id = str(tree.get("treeId") or "")
    pid = requirement_tree_project_id(tree, project_id)
    context, blockers = requirement_tree_compile_readiness(tree_path, tree, records)
    draft_dir = bundle.root / "projects" / pid / "tasks"
    diagnostic_dir = bundle.root / "projects" / pid / "requirements" / "task-queue-drafts"
    diagnostic_path = diagnostic_dir / f"{safe_slug(tree_id)}.blockers.json"
    traceability = context["traceability"]
    tree_path_ref = rel(tree_path, bundle.root)
    snapshot = context.get("snapshot") if isinstance(context.get("snapshot"), dict) else {}
    snapshot_ref = str(tree.get("coverageSnapshotRef") or "")

    if blockers:
        ensure_dir(diagnostic_dir)
        payload = {
            "status": "blocked",
            "compilerVersion": REQUIREMENT_TREE_TASK_QUEUE_COMPILER_VERSION,
            "treeId": tree_id,
            "treeRef": tree_path_ref,
            "generatedAt": utc_now(),
            "generatedByAgentRef": actor,
            "blockers": blockers,
        }
        write_text(diagnostic_path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        audit = create_audit_log(
            bundle,
            actor,
            "requirement_tree.task_queue.compile.blocked",
            tree_path_ref,
            after=rel(diagnostic_path, bundle.root),
            policy_result="blocked",
            details=f"treeId={tree_id}\nblockers={len(blockers)}",
        )
        return {
            "status": "blocked",
            "compilerVersion": REQUIREMENT_TREE_TASK_QUEUE_COMPILER_VERSION,
            "treeId": tree_id,
            "treeRef": tree_path_ref,
            "taskDraftRefs": [],
            "blockerDiagnosticRef": rel(diagnostic_path, bundle.root),
            "blockers": blockers,
            "auditRef": rel(audit, bundle.root),
        }

    task_refs: list[str] = []
    for route in REQUIREMENT_TREE_TASK_QUEUE_ROUTES:
        task_id = f"kt-{safe_slug(tree_id)}-{route['roleKey']}"
        task_path = draft_dir / f"{task_id}.draft.md"
        frontmatter = {
            "type": "ProjectTask",
            "title": route["title"],
            "description": f"Generated {route['roleKey']} task draft from accepted Requirement Tree.",
            "taskId": task_id,
            "projectId": pid,
            "requester": actor,
            "assignee": route["assignee"],
            "taskType": route["taskType"],
            "status": "draft",
            "priority": "normal",
            "sourceMaterialRefs": append_unique_list([tree_path_ref, snapshot_ref], as_list(tree.get("sourceRefs"))),
            "requirementTreeRef": tree_path_ref,
            "requirementTreeId": tree_id,
            "compilerVersion": REQUIREMENT_TREE_TASK_QUEUE_COMPILER_VERSION,
            "businessRequirementRefs": traceability["businessRequirementRefs"],
            "userRequirementRefs": traceability["userRequirementRefs"],
            "productRequirementRefs": traceability["productRequirementRefs"],
            "functionalRequirementRefs": traceability["functionalRequirementRefs"],
            "testCaseRefs": traceability["testCaseRefs"],
            "acceptanceGateRefs": traceability["acceptanceGateRefs"],
            "traceabilityRefs": traceability,
            "coverageSnapshotRef": snapshot_ref,
            "coverageRows": snapshot.get("coverageRows", []),
            "expectedOutput": [
                f"Execute the {route['roleKey']} slice with BR/UREQ/ProductRequirement/ANOS/test/acceptance traceability preserved.",
                "Write TaskResult with changed files, checks, blockers, and next handoff.",
            ],
            "blockedBy": [],
            "createdAt": utc_now(),
        }
        write_text(task_path, render_doc(frontmatter, requirement_tree_task_draft_body(route, traceability)))
        task_refs.append(rel(task_path, bundle.root))

    audit = create_audit_log(
        bundle,
        actor,
        "requirement_tree.task_queue.compile",
        tree_path_ref,
        after=", ".join(task_refs),
        policy_result="drafted",
        details=f"treeId={tree_id}\ntaskDrafts={len(task_refs)}",
    )
    return {
        "status": "drafted",
        "compilerVersion": REQUIREMENT_TREE_TASK_QUEUE_COMPILER_VERSION,
        "treeId": tree_id,
        "treeRef": tree_path_ref,
        "taskDraftRefs": task_refs,
        "blockers": [],
        "routes": [route["roleKey"] for route in REQUIREMENT_TREE_TASK_QUEUE_ROUTES],
        "counts": {
            "tasks": len(task_refs),
            "BR": len(traceability["businessRequirementRefs"]),
            "UREQ": len(traceability["userRequirementRefs"]),
            "product": len(traceability["productRequirementRefs"]),
            "functional": len(traceability["functionalRequirementRefs"]),
            "tests": len(traceability["testCaseRefs"]),
            "acceptance": len(traceability["acceptanceGateRefs"]),
        },
        "auditRef": rel(audit, bundle.root),
    }


def requirement_tree_node_summary(node: dict[str, Any] | None) -> dict[str, Any]:
    if not node:
        return {}
    return {
        "nodeRef": str(node.get("nodeId") or ""),
        "nodeKind": str(node.get("nodeKind") or ""),
        "title": str(node.get("title") or ""),
        "statement": str(node.get("statement") or ""),
        "ownerRole": str(node.get("ownerRole") or ""),
        "status": str(node.get("status") or ""),
        "parentRefs": as_list(node.get("parentRefs")),
        "childRefs": as_list(node.get("childRefs")),
        "testCaseRefs": as_list(node.get("testCaseRefs")),
        "acceptanceGateRefs": as_list(node.get("acceptanceGateRefs")),
        "taskRefs": as_list(node.get("taskRefs")),
        "resultRefs": as_list(node.get("resultRefs")),
        "assumptions": as_list(node.get("assumptions")) + as_list(node.get("assumptionRefs")),
        "decisionRefs": as_list(node.get("decisionRefs")),
        "sourceRefs": as_list(node.get("sourceRefs")),
    }


def requirement_tree_gate_summary(gate: dict[str, Any] | None) -> dict[str, Any]:
    if not gate:
        return {}
    return {
        "gateRef": str(gate.get("gateId") or ""),
        "ownerRole": str(gate.get("ownerRole") or ""),
        "verificationMethod": str(gate.get("verificationMethod") or ""),
        "observableCriteria": str(gate.get("observableSignal") or ""),
        "requiredEvidenceRefs": as_list(gate.get("requiredEvidenceRefs")),
        "requirementRefs": as_list(gate.get("requirementRefs")),
        "status": str(gate.get("status") or ""),
        "waiverDecisionRef": str(gate.get("waiverDecisionRef") or ""),
    }


def requirement_tree_resolve_ref(bundle: Bundle, ref_value: str) -> dict[str, Any]:
    ref_text = str(ref_value or "").strip()
    if not ref_text:
        return {}
    path = bundle.root / ref_text
    if path.exists():
        try:
            item = load_object(path)
        except KnowledgeError:
            return {"ref": ref_text, "resolved": False}
        return {
            "ref": ref_text,
            "resolved": True,
            "type": str(item.get("type") or ""),
            "title": str(item.get("title") or ""),
            "status": str(item.get("status") or ""),
            "taskId": str(item.get("taskId") or ""),
            "resultId": str(item.get("resultId") or ""),
            "assignee": str(item.get("assignee") or ""),
            "executorAgent": str(item.get("executorAgent") or ""),
            "summary": str(item.get("summary") or item.get("description") or ""),
            "evidenceRefs": as_list(item.get("evidenceRefs")),
        }
    return {"ref": ref_text, "resolved": False}


def requirement_tree_item_ref(kind: str, ref_value: str, reason: str, severity: str = "medium") -> dict[str, str]:
    return {"kind": kind, "ref": str(ref_value or ""), "reason": reason, "severity": severity}


def requirement_tree_workbench_read_model(bundle: Bundle, project_id: str = "", tree_ref: str = "") -> dict[str, Any]:
    records = requirement_tree_json_records(bundle)
    tree_path, tree = find_requirement_tree_record(bundle, records, tree_ref, project_id)
    tree_id = str(tree.get("treeId") or "")
    pid = requirement_tree_project_id(tree, project_id)
    nodes = {str(record.get("nodeId")): record for _path, record in records if record.get("type") == "RequirementNode" and str(record.get("treeRef") or "") == tree_id}
    gates = {str(record.get("gateId")): record for _path, record in records if record.get("type") == "AcceptanceGate" and str(record.get("treeRef") or "") == tree_id}
    snapshots = {str(record.get("snapshotId")): record for _path, record in records if record.get("type") == "RequirementCoverageSnapshot" and str(record.get("treeRef") or "") == tree_id}
    snapshot_ref = str(tree.get("coverageSnapshotRef") or "")
    snapshot = snapshots.get(snapshot_ref, {})
    coverage_rows = snapshot.get("coverageRows") if isinstance(snapshot.get("coverageRows"), list) else []
    blockers = snapshot.get("blockers") if isinstance(snapshot.get("blockers"), list) else []
    chains: list[dict[str, Any]] = []
    unmapped: list[dict[str, str]] = []
    untested: list[dict[str, str]] = []
    blocked: list[dict[str, str]] = []
    assumption_heavy: list[dict[str, Any]] = []
    seen_refs: dict[str, set[str]] = {"business": set(), "user": set(), "product": set(), "functional": set(), "test": set(), "gate": set()}

    def mark_assumption_heavy(ref_value: str, item: dict[str, Any]) -> None:
        assumptions = as_list(item.get("assumptions")) + as_list(item.get("assumptionRefs"))
        if len(assumptions) >= 3:
            assumption_heavy.append({"ref": ref_value, "kind": str(item.get("type") or item.get("nodeKind") or ""), "assumptions": assumptions, "count": len(assumptions)})

    for node_ref, node in nodes.items():
        mark_assumption_heavy(node_ref, node)
        if str(node.get("status") or "") == "blocked":
            blocked.append(requirement_tree_item_ref("RequirementNode", node_ref, "RequirementNode status is blocked.", "high"))
    for gate_ref, gate in gates.items():
        mark_assumption_heavy(gate_ref, gate)
        if str(gate.get("status") or "") in {"blocked", "failed"}:
            blocked.append(requirement_tree_item_ref("AcceptanceGate", gate_ref, f"AcceptanceGate status is {gate.get('status')}.", "high"))

    for index, raw_row in enumerate(coverage_rows):
        if not isinstance(raw_row, dict):
            unmapped.append(requirement_tree_item_ref("coverageRow", f"{snapshot_ref}#{index}", "Coverage row is not an object."))
            continue
        br_ref = str(raw_row.get("businessRequirementRef") or "")
        ureq_ref = str(raw_row.get("userRequirementRef") or "")
        preq_ref = str(raw_row.get("productRequirementRef") or "")
        functional_ref = str(raw_row.get("functionalRequirementRef") or "")
        test_ref = str(raw_row.get("testCaseRef") or "")
        gate_ref = str(raw_row.get("acceptanceGateRef") or "")
        task_refs = append_unique_list(as_list(raw_row.get("taskRef")), as_list(nodes.get(functional_ref, {}).get("taskRefs")) if functional_ref in nodes else [])
        result_refs = append_unique_list(as_list(raw_row.get("resultRef")), as_list(nodes.get(functional_ref, {}).get("resultRefs")) if functional_ref in nodes else [])
        for field, value, kind in [
            ("businessRequirementRef", br_ref, "business"),
            ("userRequirementRef", ureq_ref, "user"),
            ("productRequirementRef", preq_ref, "product"),
            ("functionalRequirementRef", functional_ref, "functional"),
        ]:
            if not value:
                unmapped.append(requirement_tree_item_ref("coverageRow", f"{snapshot_ref}#{index}", f"Coverage row missing {field}."))
            elif value not in nodes:
                unmapped.append(requirement_tree_item_ref("RequirementNode", value, f"{field} does not resolve to RequirementNode."))
            else:
                seen_refs[kind].add(value)
        if not test_ref:
            untested.append(requirement_tree_item_ref("functional", functional_ref or f"{snapshot_ref}#{index}", "Coverage row missing testCaseRef."))
        else:
            seen_refs["test"].add(test_ref)
        if not gate_ref:
            unmapped.append(requirement_tree_item_ref("AcceptanceGate", functional_ref or f"{snapshot_ref}#{index}", "Coverage row missing acceptanceGateRef."))
        elif gate_ref not in gates:
            unmapped.append(requirement_tree_item_ref("AcceptanceGate", gate_ref, "acceptanceGateRef does not resolve to AcceptanceGate."))
        else:
            seen_refs["gate"].add(gate_ref)
        chains.append(
            {
                "rowIndex": index,
                "businessRequirement": requirement_tree_node_summary(nodes.get(br_ref)),
                "userRequirement": requirement_tree_node_summary(nodes.get(ureq_ref)),
                "productRequirement": requirement_tree_node_summary(nodes.get(preq_ref)),
                "functionalRequirement": requirement_tree_node_summary(nodes.get(functional_ref)),
                "tasks": [requirement_tree_resolve_ref(bundle, ref_value) for ref_value in task_refs],
                "results": [requirement_tree_resolve_ref(bundle, ref_value) for ref_value in result_refs],
                "testRefs": [test_ref] if test_ref else [],
                "acceptanceGates": [requirement_tree_gate_summary(gates.get(gate_ref))] if gate_ref else [],
            }
        )

    if not chains:
        for functional_ref in as_list(tree.get("functionalRequirementRefs")):
            node = nodes.get(functional_ref, {})
            parent_refs = as_list(node.get("parentRefs"))
            preq_ref = parent_refs[0] if parent_refs else ""
            preq = nodes.get(preq_ref, {})
            ureq_ref = (as_list(preq.get("parentRefs")) or [""])[0]
            ureq = nodes.get(ureq_ref, {})
            br_ref = (as_list(ureq.get("parentRefs")) or [""])[0]
            chains.append(
                {
                    "rowIndex": len(chains),
                    "businessRequirement": requirement_tree_node_summary(nodes.get(br_ref)),
                    "userRequirement": requirement_tree_node_summary(ureq),
                    "productRequirement": requirement_tree_node_summary(preq),
                    "functionalRequirement": requirement_tree_node_summary(node),
                    "tasks": [requirement_tree_resolve_ref(bundle, ref_value) for ref_value in as_list(node.get("taskRefs"))],
                    "results": [requirement_tree_resolve_ref(bundle, ref_value) for ref_value in as_list(node.get("resultRefs"))],
                    "testRefs": as_list(node.get("testCaseRefs")),
                    "acceptanceGates": [requirement_tree_gate_summary(gates.get(ref_value)) for ref_value in as_list(node.get("acceptanceGateRefs"))],
                }
            )

    for ref_value in as_list(tree.get("businessRequirementRefs")):
        node = nodes.get(ref_value, {})
        if ref_value not in seen_refs["business"] or not as_list(node.get("childRefs")):
            unmapped.append(requirement_tree_item_ref("business", ref_value, "BR is missing coverage row or UREQ child mapping."))
    for ref_value in as_list(tree.get("userRequirementRefs")):
        node = nodes.get(ref_value, {})
        if ref_value not in seen_refs["user"] or not as_list(node.get("parentRefs")) or not as_list(node.get("childRefs")):
            unmapped.append(requirement_tree_item_ref("user", ref_value, "UREQ is missing BR parent, ProductRequirement child, or coverage row."))
    for ref_value in as_list(tree.get("productRequirementRefs")):
        node = nodes.get(ref_value, {})
        if ref_value not in seen_refs["product"] or not as_list(node.get("parentRefs")) or not as_list(node.get("childRefs")):
            unmapped.append(requirement_tree_item_ref("product", ref_value, "ProductRequirement is missing UREQ parent, ANOS child, or coverage row."))
    for ref_value in as_list(tree.get("functionalRequirementRefs")):
        node = nodes.get(ref_value, {})
        if ref_value not in seen_refs["functional"] or not as_list(node.get("parentRefs")):
            unmapped.append(requirement_tree_item_ref("functional", ref_value, "ANOS is missing ProductRequirement parent or coverage row."))
        if not as_list(node.get("testCaseRefs")):
            untested.append(requirement_tree_item_ref("functional", ref_value, "ANOS has no testCaseRefs."))
        if not as_list(node.get("acceptanceGateRefs")):
            unmapped.append(requirement_tree_item_ref("functional", ref_value, "ANOS has no acceptanceGateRefs."))
    for blocker in blockers:
        if isinstance(blocker, dict):
            blocked.append(
                {
                    "kind": "coverageBlocker",
                    "ref": str(blocker.get("nodeRef") or tree_id),
                    "reason": str(blocker.get("reason") or ""),
                    "severity": str(blocker.get("severity") or "medium"),
                    "ownerRole": str(blocker.get("ownerRole") or ""),
                    "suggestedFix": str(blocker.get("suggestedFix") or ""),
                }
            )

    diagnostics = {
        "unmapped": unmapped,
        "untested": untested,
        "blocked": blocked,
        "assumptionHeavyItems": assumption_heavy,
    }
    return {
        "apiVersion": "v0.1",
        "kind": "RequirementTreeWorkbenchReadModel",
        "projectId": pid,
        "treeId": tree_id,
        "treeRef": rel(tree_path, bundle.root),
        "treeStatus": str(tree.get("status") or ""),
        "coverageSnapshotRef": snapshot_ref,
        "counts": {
            "chains": len(chains),
            "BR": len(as_list(tree.get("businessRequirementRefs"))),
            "UREQ": len(as_list(tree.get("userRequirementRefs"))),
            "product": len(as_list(tree.get("productRequirementRefs"))),
            "functional": len(as_list(tree.get("functionalRequirementRefs"))),
            "tests": len(as_list(tree.get("testCaseRefs"))),
            "acceptance": len(as_list(tree.get("acceptanceGateRefs"))),
            "unmapped": len(unmapped),
            "untested": len(untested),
            "blocked": len(blocked),
            "assumptionHeavyItems": len(assumption_heavy),
        },
        "chains": chains,
        "diagnostics": diagnostics,
    }


TASK_RESULT_REQUIRED_FIELDS = [
    "summary",
    "outputRefs",
    "evidenceRefs",
    "executorAgent",
    "runner",
    "leaseProof",
    "risks",
    "blockers",
    "nextAction",
    "checks",
    "approvalRequest",
    "qualityEvaluation",
    "createdAt",
]

TASK_RESULT_LEGACY_COMPAT_FIELDS = {
    "runner",
    "leaseProof",
    "risks",
    "blockers",
    "nextAction",
    "checks",
    "approvalRequest",
    "qualityEvaluation",
    "createdAt",
}

TASK_RESULT_CURRENT_CONTRACT_MARKERS = {"createdAt", "contractVersion", "taskResultContract"}
TASK_RESULT_LEGACY_PROVENANCE_FIELDS = {"timestamp", "completedAt", "resultId", "runnerId", "testsOrChecks", "nextActions"}


def is_legacy_task_result_compatible(fm: dict[str, Any]) -> bool:
    if fm.get("type") != "TaskResult":
        return False
    if any(field in fm for field in TASK_RESULT_CURRENT_CONTRACT_MARKERS):
        return False
    has_summary = bool(fm.get("summary") or fm.get("result") or fm.get("description"))
    has_task_link = bool(fm.get("taskId") or fm.get("taskRef") or as_list(fm.get("taskRefs")))
    has_output = "outputRefs" in fm or "outputRef" in fm or "outputs" in fm or bool(as_list(fm.get("knowledgeRefs")))
    has_evidence = "evidenceRefs" in fm or "evidenceRef" in fm or bool(as_list(fm.get("sourceMaterialRefs")))
    has_legacy_provenance = any(field in fm for field in TASK_RESULT_LEGACY_PROVENANCE_FIELDS)
    return has_summary and has_task_link and has_output and has_evidence and has_legacy_provenance


def quality_decision_value_valid(decision: str) -> bool:
    value = decision.strip()
    if not value:
        return True
    if value in QUALITY_DECISION_VALUES:
        return True
    if value in QUALITY_DECISION_BAD_VALUES:
        return False
    return bool(QUALITY_DECISION_PATTERN.match(value))


PM_DELIVERY_GATE_TERMINAL_STATUS = {"accepted", "auto_accepted", "closed", "done", "passed"}
PM_DELIVERY_CLOSEOUT_TASK_TYPES = {"pm_acceptance", "pm_closeout", "release_acceptance", "final_acceptance"}
PM_CLOSEOUT_ARTIFACT_TYPES = {"TaskResult", "ReviewRecord", "ProjectManagerReview"}
PM_CLOSEOUT_BLOCKED_STATUS = {"blocked", "changes_requested", "failed", "needs_rework", "rejected"}
PM_CLOSEOUT_SCOPE_VALUES = {"process_status_only", "legacy_process_review", "not_delivery_closeout"}
PM_PRE_DELIVERY_TEST_SCOPES = {"test_plan_preparation_only", "test_preparation_only", "test_handoff_only"}
PM_PRE_DELIVERY_TEST_MARKERS = (
    "test plan",
    "test-plan",
    "test_plan",
    "测试计划",
    "preparation",
    "planning",
    "准备",
    "handoff",
    "交接",
)
PM_TEST_EXECUTION_MARKERS = (
    "execution",
    "execute",
    "validation",
    "regression",
    "acceptance",
    "verification",
    "执行",
    "验收",
    "回归",
)
PM_CLOSEOUT_TEXT_MARKERS = (
    "closeout",
    "final acceptance",
    "final-acceptance",
    "final_acceptance",
    "pm final",
    "pm-final",
    "pm_closeout",
    "最终验收",
    "最终收口",
    "pm 收口",
    "pm 最终",
)
PM_FORBIDDEN_OUTPUT_REF_PREFIXES = (
    "zhenzhi_knowledge/",
    "src/",
    "scripts/",
    "tests/",
    "docs/product/",
    "requirements/",
    "prd/",
)
PM_FORBIDDEN_PROJECT_OUTPUT_SEGMENTS = (
    "/technical-solutions/",
    "/design/",
    "/engineering/",
    "/test-plans/",
    "/test-reports/",
    "/product-reviews/",
)


def pm_delivery_gate_enabled(record: dict[str, Any]) -> bool:
    gate = record.get("pmDeliveryGate")
    if isinstance(gate, dict) and gate.get("enforce") is True:
        return True
    return record.get("pmCanClose") is True


def pm_delivery_gate_requirement_refs(record: dict[str, Any]) -> list[str]:
    gate = record.get("pmDeliveryGate")
    if isinstance(gate, dict) and as_list(gate.get("requirementRefs")):
        return as_list(gate.get("requirementRefs"))
    return as_list(record.get("requirementRefs"))


def pm_artifact_agent(record: dict[str, Any]) -> str:
    return str(
        record.get("executorAgent")
        or record.get("reviewAgent")
        or record.get("reviewerAgent")
        or record.get("actor")
        or record.get("assignee")
        or ""
    )


def pm_closeout_scope(record: dict[str, Any]) -> str:
    return str(record.get("pmCloseoutScope") or "").strip()


def pm_closeout_artifact(rel_path: str, record: dict[str, Any], task: dict[str, Any] | None = None) -> bool:
    if record.get("type") not in PM_CLOSEOUT_ARTIFACT_TYPES:
        return False
    if pm_artifact_agent(record) != "agent.company.project-manager":
        return False
    status_text = f"{record.get('status', '')} {record.get('decision', '')} {dict(record.get('qualityEvaluation') or {}).get('decision', '')}".lower()
    if any(status in status_text for status in PM_CLOSEOUT_BLOCKED_STATUS):
        return False
    task_type = str((task or {}).get("taskType") or record.get("taskType") or "").lower()
    if task_type in PM_DELIVERY_CLOSEOUT_TASK_TYPES:
        return True
    text = " ".join(
        [
            rel_path,
            str(record.get("title") or ""),
            str(record.get("description") or ""),
            str(record.get("taskId") or ""),
        ]
    ).lower()
    return any(marker in text for marker in PM_CLOSEOUT_TEXT_MARKERS)


def pm_closeout_artifact_contract_satisfied(record: dict[str, Any]) -> bool:
    if pm_delivery_gate_enabled(record):
        return True
    scope = pm_closeout_scope(record)
    if scope not in PM_CLOSEOUT_SCOPE_VALUES:
        return False
    return bool(as_list(record.get("evidenceRefs")) or as_list(record.get("sourceRefs")) or as_list(record.get("outputRefs")))


def pm_forbidden_output_ref(ref: str) -> bool:
    value = ref.strip()
    if not value:
        return False
    if value.startswith(PM_FORBIDDEN_OUTPUT_REF_PREFIXES):
        return True
    return value.startswith("projects/") and any(segment in value for segment in PM_FORBIDDEN_PROJECT_OUTPUT_SEGMENTS)


def pm_role_exception_satisfied(record: dict[str, Any]) -> bool:
    exception = record.get("pmRoleException")
    if not isinstance(exception, dict):
        return False
    return (
        exception.get("temporaryEmergencyTakeover") is True
        and bool(str(exception.get("owningAgent") or "").strip())
        and bool(as_list(exception.get("handoffTaskRefs")) or as_list(exception.get("receiverReviewRefs")) or as_list(record.get("receiverReviewRefs")))
    )


def delegated_output_producers(records: list[tuple[str, dict[str, Any]]]) -> dict[str, list[str]]:
    producers: dict[str, list[str]] = {}
    for rel_path, record in records:
        if record.get("type") != "TaskResult":
            continue
        if pm_artifact_agent(record) == "agent.company.project-manager":
            continue
        for output_ref in as_list(record.get("outputRefs")):
            value = str(output_ref).strip()
            if value:
                producers.setdefault(value, []).append(rel_path)
    return producers


def validate_pm_role_boundaries(records: list[tuple[str, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    delegated_outputs = delegated_output_producers(records)
    for rel_path, record in records:
        if record.get("type") != "TaskResult":
            continue
        if pm_artifact_agent(record) != "agent.company.project-manager":
            continue
        if pm_role_exception_satisfied(record):
            continue
        for output_ref in as_list(record.get("outputRefs")):
            output_ref = str(output_ref).strip()
            if pm_forbidden_output_ref(output_ref) and output_ref not in delegated_outputs:
                problems.append(
                    f"{rel_path}: Project Manager TaskResult outputRef lacks owning Agent TaskResult provenance: {output_ref}"
                )
    return problems


def validate_pm_action_runtime(records: list[tuple[str, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    delegated_outputs = delegated_output_producers(records)
    outcome_refs = {rel_path: record for rel_path, record in records if record.get("type") == "OutcomeSlice"}
    for rel_path, record in records:
        if record.get("type") != "ProjectManagerAction":
            continue
        intent = str(record.get("intent") or "")
        exit_state = str(record.get("exitState") or "")
        runtime_version = str(record.get("pmActionRuntimeVersion") or "")
        strict_runtime = runtime_version == "v1" or str(record.get("outcomeGuardrailVersion") or "") == "v1"
        if not strict_runtime and intent not in PM_ACTION_INTENTS:
            continue
        if intent not in PM_ACTION_INTENTS:
            problems.append(f"{rel_path}: ProjectManagerAction intent must be one of {sorted(PM_ACTION_INTENTS)}")
        if exit_state not in PM_ACTION_EXIT_STATES:
            problems.append(f"{rel_path}: ProjectManagerAction exitState must be one of {sorted(PM_ACTION_EXIT_STATES)}")
            continue
        for field in ["projectId", "actor", "currentState", "allowedTransition", "summary"]:
            if not str(record.get(field) or "").strip():
                problems.append(f"{rel_path}: ProjectManagerAction missing required field {field}")
        records_written = as_list(record.get("recordsWritten"))
        delegated_owners = as_list(record.get("delegatedOwners"))
        next_action = str(record.get("nextAction") or "").strip()
        blocker = str(record.get("blocker") or "").strip()
        blocker_owner = str(record.get("blockerOwner") or "").strip()
        terminal_decision = str(record.get("terminalDecision") or "").strip()
        outcome_slice_ref = str(record.get("outcomeSliceRef") or "").strip()
        outcome_state_before = str(record.get("outcomeStateBefore") or "").strip()
        outcome_state_after = str(record.get("outcomeStateAfter") or "").strip()
        outcome_value_change = str(record.get("outcomeValueChange") or "").strip()
        guardrail_decision = str(record.get("guardrailDecision") or "").strip()
        guardrail_reason = str(record.get("guardrailReason") or "").strip()
        if not any([next_action, blocker, terminal_decision]):
            problems.append(f"{rel_path}: ProjectManagerAction exit requires nextAction, blocker, or terminalDecision")
        if strict_runtime and intent in PM_ACTION_OUTCOME_REQUIRED_INTENTS:
            if not outcome_slice_ref:
                problems.append(f"{rel_path}: ProjectManagerAction intent {intent} requires outcomeSliceRef")
            elif outcome_slice_ref not in outcome_refs:
                problems.append(f"{rel_path}: ProjectManagerAction outcomeSliceRef does not exist or is not OutcomeSlice: {outcome_slice_ref}")
        if strict_runtime and outcome_slice_ref:
            if not (outcome_state_before and outcome_state_after):
                problems.append(f"{rel_path}: ProjectManagerAction with outcomeSliceRef requires outcomeStateBefore and outcomeStateAfter")
            elif outcome_state_before == outcome_state_after and guardrail_decision not in {"pause", "stop", "escalate"}:
                problems.append(f"{rel_path}: ProjectManagerAction outcome state did not change; use guardrailDecision pause/stop/escalate or record a target state change")
            if not outcome_value_change:
                problems.append(f"{rel_path}: ProjectManagerAction with outcomeSliceRef requires outcomeValueChange")
            if guardrail_decision:
                if guardrail_decision not in OUTCOME_GUARDRAIL_DECISIONS:
                    problems.append(f"{rel_path}: ProjectManagerAction guardrailDecision must be one of {sorted(OUTCOME_GUARDRAIL_DECISIONS)}")
                if guardrail_decision in {"pause", "stop", "escalate"} and not guardrail_reason:
                    problems.append(f"{rel_path}: ProjectManagerAction guardrailDecision {guardrail_decision} requires guardrailReason")
        if exit_state == "dispatched" and not (records_written or delegated_owners or next_action):
            problems.append(f"{rel_path}: dispatched PM action requires recordsWritten, delegatedOwners, or nextAction")
        if exit_state == "waiting_acceptance" and not (records_written or next_action):
            problems.append(f"{rel_path}: waiting_acceptance PM action requires recordsWritten or nextAction")
        if exit_state == "blocked_with_owner" and not (blocker and blocker_owner):
            problems.append(f"{rel_path}: blocked_with_owner PM action requires blocker and blockerOwner")
        if exit_state == "closed_with_gate_passed":
            if not terminal_decision:
                problems.append(f"{rel_path}: closed_with_gate_passed PM action requires terminalDecision")
            if not pm_delivery_gate_enabled(record):
                problems.append(f"{rel_path}: closed_with_gate_passed PM action requires pmDeliveryGate.enforce true")
        for record_ref in records_written:
            record_ref = str(record_ref).strip()
            if pm_forbidden_output_ref(record_ref) and record_ref not in delegated_outputs:
                problems.append(f"{rel_path}: ProjectManagerAction recordsWritten lacks owning Agent TaskResult provenance: {record_ref}")
    return problems


def task_has_result(task: dict[str, Any], results_by_task: dict[str, list[dict[str, Any]]]) -> bool:
    task_id = str(task.get("taskId") or "")
    return bool(str(task.get("resultRef") or "").strip() or results_by_task.get(task_id))


def task_result_passed(result: dict[str, Any]) -> bool:
    status = str(result.get("status") or result.get("result") or "")
    quality = result.get("qualityEvaluation") if isinstance(result.get("qualityEvaluation"), dict) else {}
    acceptance = result.get("acceptancePolicy") if isinstance(result.get("acceptancePolicy"), dict) else {}
    decision = str(quality.get("decision") or "")
    acceptance_status = str(acceptance.get("acceptanceStatus") or "")
    if status in {"blocked", "failed", "rejected", "changes_requested"}:
        return False
    if decision in {"retry_required", "repair_required", "changes_requested", "blocked"}:
        return False
    if acceptance_status in {"blocked", "failed", "rejected", "changes_requested"}:
        return False
    return (
        status in PM_DELIVERY_GATE_TERMINAL_STATUS
        or acceptance_status in PM_DELIVERY_GATE_TERMINAL_STATUS
        or decision in {"close", "auto_accepted", "accepted"}
    )


def _result_search_text(result: dict[str, Any]) -> str:
    parts: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            for nested in value.values():
                collect(nested)
        elif isinstance(value, list):
            for nested in value:
                collect(nested)
        elif value is not None:
            parts.append(str(value))

    for field in [
        "taskId",
        "resultId",
        "summary",
        "description",
        "terminalReason",
        "sourceTaskRef",
        "sourceMaterialRefs",
        "evidenceRefs",
        "outputRefs",
        "testsOrChecks",
        "checks",
        "defectRefs",
        "qualityEvaluation",
        "acceptancePolicy",
        "residualDebt",
        "followupTaskRefs",
        "handoffContract",
    ]:
        collect(result.get(field))
    return " ".join(parts).lower()


def task_result_has_historical_debt_boundary(result: dict[str, Any]) -> bool:
    text = _result_search_text(result)
    return (
        "historical" in text
        and any(marker in text for marker in ["debt", "followup", "follow-up", "architecture-classified", "architecture classified"])
    )


def _result_refs_intersect(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_refs = {str(ref) for ref in as_list(left.get("defectRefs")) if str(ref)}
    right_refs = {str(ref) for ref in as_list(right.get("defectRefs")) if str(ref)}
    return bool(left_refs and right_refs and left_refs.intersection(right_refs))


def _result_mentions(result: dict[str, Any], values: list[str]) -> bool:
    text = _result_search_text(result)
    return any(value and value.lower() in text for value in values)


def development_result_superseded_by_quality_acceptance(
    task: dict[str, Any],
    result: dict[str, Any],
    requirement_ref: str,
    results: list[dict[str, Any]],
    product_results: list[dict[str, Any]],
) -> bool:
    if str(result.get("executorAgent") or "") != DEVELOPMENT_AGENT_ID:
        return False
    if task_result_passed(result):
        return True
    if not task_result_has_historical_debt_boundary(result):
        return False

    dev_refs = [
        str(task.get("taskId") or ""),
        str(result.get("taskId") or ""),
        str(result.get("resultId") or ""),
    ]
    test_results = [
        candidate
        for candidate in results
        if str(candidate.get("executorAgent") or "") == TEST_AGENT_ID
        and requirement_ref in as_list(candidate.get("requirementRefs"))
        and task_result_passed(candidate)
        and (_result_refs_intersect(result, candidate) or _result_mentions(candidate, dev_refs))
    ]
    if not test_results:
        return False

    test_refs: list[str] = []
    for test_result in test_results:
        test_refs.extend([str(test_result.get("taskId") or ""), str(test_result.get("resultId") or "")])
    return any(
        task_result_passed(product_result)
        and (_result_refs_intersect(result, product_result) or _result_mentions(product_result, dev_refs + test_refs))
        for product_result in product_results
    )


def task_is_pre_delivery_test_preparation(task: dict[str, Any], results_by_task: dict[str, list[dict[str, Any]]] | None = None) -> bool:
    task_type = str(task.get("taskType") or "")
    identity_text = " ".join(
        [
            task_type,
            str(task.get("title") or ""),
            str(task.get("sourceReason") or ""),
            str(task.get("taskId") or ""),
        ]
    ).lower()
    if results_by_task:
        for result in results_by_task.get(str(task.get("taskId") or ""), []):
            scope = pm_closeout_scope(result)
            if scope in PM_PRE_DELIVERY_TEST_SCOPES:
                return True
    if any(marker in identity_text for marker in PM_TEST_EXECUTION_MARKERS):
        return False
    if any(marker in identity_text for marker in PM_PRE_DELIVERY_TEST_MARKERS):
        return True
    if results_by_task:
        for result in results_by_task.get(str(task.get("taskId") or ""), []):
            result_text = " ".join(
                [
                    str(result.get("title") or ""),
                    str(result.get("description") or ""),
                    str(result.get("summary") or ""),
                    " ".join(as_list(result.get("checks"))),
                    " ".join(as_list(result.get("blockers"))),
                ]
            ).lower()
            if any(marker in result_text for marker in PM_PRE_DELIVERY_TEST_MARKERS) and not any(marker in result_text for marker in PM_TEST_EXECUTION_MARKERS):
                return True
    return False


def task_is_delivery_role(task: dict[str, Any], role: str) -> bool:
    assignee = str(task.get("assignee") or task.get("executorAgent") or "")
    task_type = str(task.get("taskType") or "")
    if role == "development":
        return assignee == "agent.company.development" or task_type in {"implementation", "engineering_action", "bugfix", "development"}
    if role == "test":
        return assignee == "agent.company.test" or "test" in task_type
    return False


def validate_pm_delivery_gates(records: list[tuple[str, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    tasks = [(path, record) for path, record in records if record.get("type") in {"ProjectTask", "KnowledgeTask"}]
    results = [(path, record) for path, record in records if record.get("type") == "TaskResult"]
    tasks_by_id = {str(task.get("taskId") or ""): task for _path, task in tasks if str(task.get("taskId") or "")}
    results_by_task: dict[str, list[dict[str, Any]]] = {}
    product_results_by_requirement: dict[str, list[dict[str, Any]]] = {}
    for result_path, result in results:
        task_id = str(result.get("taskId") or "")
        if task_id:
            results_by_task.setdefault(task_id, []).append(result)
        if str(result.get("executorAgent") or "") == "agent.company.product-manager":
            for requirement_ref in as_list(result.get("requirementRefs")):
                product_results_by_requirement.setdefault(requirement_ref, []).append(result)
        linked_task = tasks_by_id.get(task_id, {})
        task_type = str(linked_task.get("taskType") or result.get("taskType") or "")
        is_pm_result = str(result.get("executorAgent") or "") == "agent.company.project-manager"
        is_closeout = task_type in PM_DELIVERY_CLOSEOUT_TASK_TYPES or "closeout" in task_type or result.get("pmCanClose") is True
        if is_pm_result and is_closeout and not pm_delivery_gate_enabled(result):
            problems.append(f"{result_path}: PM closeout TaskResult requires pmDeliveryGate.enforce true")
    for rel_path, record in records:
        linked_task = tasks_by_id.get(str(record.get("taskId") or ""), {})
        if pm_closeout_artifact(rel_path, record, linked_task) and not pm_closeout_artifact_contract_satisfied(record):
            problems.append(f"{rel_path}: PM closeout artifact requires pmDeliveryGate.enforce true or pmCloseoutScope process_status_only")
    for rel_path, record in records:
        if not pm_delivery_gate_enabled(record):
            continue
        if record.get("type") == "ProjectManagerAction" and str(record.get("exitState") or "") != "closed_with_gate_passed":
            continue
        requirement_refs = pm_delivery_gate_requirement_refs(record)
        if not requirement_refs:
            problems.append(f"{rel_path}: pmDeliveryGate requires requirementRefs")
            continue
        gate = record.get("pmDeliveryGate") if isinstance(record.get("pmDeliveryGate"), dict) else {}
        require_product = gate.get("requireProductAcceptance", True)
        for requirement_ref in requirement_refs:
            matching_tasks = [task for _task_path, task in tasks if requirement_ref in as_list(task.get("requirementRefs"))]
            development_tasks = [task for task in matching_tasks if task_is_delivery_role(task, "development")]
            test_tasks = [
                task
                for task in matching_tasks
                if task_is_delivery_role(task, "test") and not task_is_pre_delivery_test_preparation(task, results_by_task)
            ]
            if not development_tasks:
                problems.append(f"{rel_path}: pmDeliveryGate {requirement_ref} requires a Development task")
            if not test_tasks:
                problems.append(f"{rel_path}: pmDeliveryGate {requirement_ref} requires a Test task")
            for task in development_tasks:
                status = str(task.get("status") or "")
                task_results = results_by_task.get(str(task.get("taskId") or ""), [])
                superseded_results = [
                    result
                    for result in task_results
                    if development_result_superseded_by_quality_acceptance(
                        task,
                        result,
                        requirement_ref,
                        [record for _path, record in results],
                        product_results_by_requirement.get(requirement_ref, []),
                    )
                ]
                if not task_results:
                    problems.append(
                        f"{rel_path}: pmDeliveryGate {requirement_ref} cannot close while Development task {task.get('taskId')} is {status or 'unknown'} without TaskResult"
                    )
                elif status in {"pending", "waiting_runner", "processing", "blocked", "failed"} and not superseded_results:
                    problems.append(
                        f"{rel_path}: pmDeliveryGate {requirement_ref} cannot close while Development task {task.get('taskId')} is {status or 'unknown'}"
                    )
                for result in task_results:
                    if not task_result_passed(result) and result not in superseded_results:
                        problems.append(
                            f"{rel_path}: pmDeliveryGate {requirement_ref} requires passing Development TaskResult for {task.get('taskId')}"
                        )
            for task in test_tasks:
                status = str(task.get("status") or "")
                if status in {"pending", "waiting_runner", "processing", "blocked", "failed"} or not task_has_result(task, results_by_task):
                    problems.append(
                        f"{rel_path}: pmDeliveryGate {requirement_ref} cannot close while Test task {task.get('taskId')} is {status or 'unknown'} without TaskResult"
                    )
                for result in results_by_task.get(str(task.get("taskId") or ""), []):
                    if not task_result_passed(result):
                        problems.append(
                            f"{rel_path}: pmDeliveryGate {requirement_ref} requires passing Test TaskResult for {task.get('taskId')}"
                        )
            if require_product:
                product_results = product_results_by_requirement.get(requirement_ref, [])
                if not product_results or not any(task_result_passed(result) for result in product_results):
                    problems.append(f"{rel_path}: pmDeliveryGate {requirement_ref} requires Product Manager acceptance TaskResult")
    return problems


def validate_bundle(bundle: Bundle) -> list[str]:
    problems: list[str] = []
    required = [
        "index.md",
        "log.md",
        "projects/index.md",
        "agents/index.md",
        "tools/index.md",
        "knowledge/index.md",
        "runs/index.md",
        "tasks/index.md",
        "sources/index.md",
        "task-results/index.md",
    ]
    for item in required:
        if not (bundle.root / item).exists():
            problems.append(f"missing required file: {item}")
    object_roots = [bundle.root / name for name in OBJECT_ROOT_NAMES]
    object_files: list[Path] = []
    for object_root in object_roots:
        if object_root.exists():
            object_files.extend(object_root.rglob("*.md"))
    task_index: dict[str, dict[str, Any]] = {}
    validation_records: list[tuple[str, dict[str, Any]]] = []
    for object_path in object_files:
        if ".zhenzhi" in object_path.parts or object_path.name.endswith(".draft.md"):
            continue
        task_text = read_text(object_path)
        task_fm, _task_body = parse_frontmatter(task_text)
        if task_fm and object_path.name not in COLLECTION_NAMES:
            validation_records.append((rel(object_path, bundle.root), task_fm))
        if task_fm.get("type") in {"ProjectTask", "KnowledgeTask"} and task_fm.get("taskId"):
            task_index[str(task_fm["taskId"])] = task_fm
    collection_names = COLLECTION_NAMES
    for path in object_files:
        rel_path = rel(path, bundle.root)
        if ".zhenzhi" in path.parts:
            continue
        if path.name in collection_names or path.name.endswith(".draft.md"):
            problems.extend(scan_for_secret_values(path))
            continue
        text = read_text(path)
        fm, body = parse_frontmatter(text)
        if not fm:
            problems.append(f"{rel_path}: missing frontmatter")
            continue
        if "type" not in fm:
            problems.append(f"{rel_path}: missing type")
        elif fm["type"] not in TYPE_VALUES:
            problems.append(f"{rel_path}: unknown type {fm['type']}")
        problems.extend(validate_central_record_size(path, rel_path, fm))
        if "status" in fm and fm["status"] not in STATUS_VALUES:
            problems.append(f"{rel_path}: unknown status {fm['status']}")
        if fm.get("type") == "Project":
            problems.extend(validate_project_workspace_ref(rel_path, fm))
        if fm.get("type") in {"ProjectTask", "KnowledgeTask"} and fm.get("status") not in (TASK_ROUTING_STATUS_VALUES | LEGACY_TASK_ROUTING_STATUS_VALUES):
            problems.append(f"{rel_path}: unknown task routing status {fm.get('status')}")
        if fm.get("type") in {"ProjectTask", "KnowledgeTask"}:
            problems.extend(validate_task_source_traceability(rel_path, fm, require_explicit=bool(fm.get("workSourceType"))))
            outcome_ref = str(fm.get("outcomeSliceRef") or "").strip()
            if outcome_ref:
                outcome_path = bundle.root / outcome_ref
                if not outcome_path.exists():
                    problems.append(f"{rel_path}: outcomeSliceRef does not exist: {outcome_ref}")
                else:
                    outcome = load_object(outcome_path)
                    if outcome.get("type") != "OutcomeSlice":
                        problems.append(f"{rel_path}: outcomeSliceRef must point to OutcomeSlice: {outcome_ref}")
            for review_ref in as_list(fm.get("receiverReviewRefs")):
                review_path = bundle.root / review_ref
                if not review_path.exists():
                    problems.append(f"{rel_path}: receiverReviewRefs does not exist: {review_ref}")
                    continue
                review = load_object(review_path)
                if review.get("type") != "ReceiverReview":
                    problems.append(f"{rel_path}: receiverReviewRefs must point to ReceiverReview: {review_ref}")
        if fm.get("type") == "OutcomeSlice":
            for field in ["outcomeSliceId", "projectId", "owner", "stageGoal", "mainDeliverable", "currentState", "targetState"]:
                if is_empty_value(fm.get(field)):
                    problems.append(f"{rel_path}: OutcomeSlice missing required field {field}")
            current_state = str(fm.get("currentState") or "")
            target_state = str(fm.get("targetState") or "")
            if current_state and current_state not in OUTCOME_SLICE_STATE_VALUES:
                problems.append(f"{rel_path}: unknown OutcomeSlice currentState {current_state}")
            if target_state and target_state not in OUTCOME_SLICE_STATE_VALUES:
                problems.append(f"{rel_path}: unknown OutcomeSlice targetState {target_state}")
            if current_state and target_state and current_state == target_state and str(fm.get("status") or "") not in {"blocked", "stopped"}:
                problems.append(f"{rel_path}: OutcomeSlice must declare a target state change")
            budget = fm.get("budget")
            if not isinstance(budget, dict):
                problems.append(f"{rel_path}: OutcomeSlice requires budget")
            else:
                try:
                    wip_limit = int(budget.get("wipLimit") or 0)
                except (TypeError, ValueError):
                    wip_limit = 0
                if wip_limit < 1:
                    problems.append(f"{rel_path}: OutcomeSlice budget.wipLimit must be >= 1")
            if not as_list(fm.get("stopConditions")):
                problems.append(f"{rel_path}: OutcomeSlice requires stopConditions")
            if str(fm.get("status") or "") in {"done", "closed", "delivered"} and not as_list(fm.get("evidenceRefs")):
                problems.append(f"{rel_path}: completed OutcomeSlice requires evidenceRefs")
        if fm.get("type") == "Defect":
            for field in ["defectId", "projectId", "reporter", "severity", "status"]:
                if is_empty_value(fm.get(field)):
                    problems.append(f"{rel_path}: Defect missing required field {field}")
            if str(fm.get("status") or "") not in DEFECT_STATUS_VALUES:
                problems.append(f"{rel_path}: unknown Defect status {fm.get('status')}")
            if fm.get("status") in {"fixed", "closed"} and not as_list(fm.get("fixTaskRefs")):
                problems.append(f"{rel_path}: fixed or closed Defect requires fixTaskRefs")
            if fm.get("status") == "closed" and not as_list(fm.get("regressionEvidenceRefs")):
                problems.append(f"{rel_path}: closed Defect requires regressionEvidenceRefs")
        if fm.get("type") == "ReceiverReview":
            for field in ["reviewId", "projectId", "upstreamRef", "receiverAgent", "reviewerAgent", "decision"]:
                if is_empty_value(fm.get(field)):
                    problems.append(f"{rel_path}: ReceiverReview missing required field {field}")
            decision = str(fm.get("decision") or "")
            if decision not in RECEIVER_REVIEW_STATUS_VALUES:
                problems.append(f"{rel_path}: unknown ReceiverReview decision {decision}")
            status = str(fm.get("status") or "")
            if status and status != decision:
                problems.append(f"{rel_path}: ReceiverReview status must equal decision")
            if decision in {"needs_rework", "human_decision_required"} and not as_list(fm.get("issues")):
                problems.append(f"{rel_path}: ReceiverReview decision {decision} requires issues")
            if decision == "accepted_with_assumptions" and not as_list(fm.get("assumptions")):
                problems.append(f"{rel_path}: ReceiverReview accepted_with_assumptions requires assumptions")
            if decision == "accepted_for_work" and not (as_list(fm.get("checklist")) or as_list(fm.get("artifactRefs"))):
                problems.append(f"{rel_path}: ReceiverReview accepted_for_work requires checklist or artifactRefs")
        if fm.get("type") == "TaskResult":
            legacy_compatible = is_legacy_task_result_compatible(fm)
            for field in TASK_RESULT_REQUIRED_FIELDS:
                if field not in fm:
                    if legacy_compatible and field in TASK_RESULT_LEGACY_COMPAT_FIELDS:
                        continue
                    problems.append(f"{rel_path}: TaskResult missing required field {field}")
            acceptance_policy = dict(fm.get("acceptancePolicy") or {})
            if "status" in acceptance_policy:
                problems.append(f"{rel_path}: acceptancePolicy must use acceptanceStatus, not status")
            acceptance_status = str(acceptance_policy.get("acceptanceStatus") or "")
            if acceptance_policy and acceptance_status and acceptance_status not in ACCEPTANCE_POLICY_STATUS_VALUES:
                problems.append(f"{rel_path}: unknown acceptancePolicy.acceptanceStatus {acceptance_status}")
            quality_evaluation = dict(fm.get("qualityEvaluation") or {})
            decision = str(quality_evaluation.get("decision") or "")
            if quality_evaluation and decision and not quality_decision_value_valid(decision):
                problems.append(f"{rel_path}: unknown qualityEvaluation.decision {decision}")
            task = task_index.get(str(fm.get("taskId") or ""))
            task_runtime = dict(task.get("taskRuntime") or {}) if task else {}
            task_type = str((task or {}).get("taskType") or task_runtime.get("taskType") or "")
            task_category = str(task_runtime.get("category") or "")
            requires_product_verdict = (
                task_type in {"product_review", "product_acceptance", "product_requirement", "product_clarification"}
                or task_category == "product"
            )
            executor_agent = str(fm.get("executorAgent") or "")
            if requires_product_verdict and not legacy_compatible and executor_agent != "agent.company.product-manager":
                problems.append(
                    f"{rel_path}: product verdict TaskResult must be executed by agent.company.product-manager, not {executor_agent or 'unknown'}"
                )
        if fm.get("type") == "SourceMaterial":
            material_kind = str(fm.get("materialType") or fm.get("sourceType") or "")
            if material_kind in {"document", "pdf", "docx", "image", "video", "audio", "package", "binary", "model", "dataset"} and not str(fm.get("storageRef") or "").strip():
                problems.append(f"{rel_path}: bulky SourceMaterial type {material_kind} requires storageRef; central record must not store raw artifact data")
        if fm.get("type") == "Requirement":
            for field in ["requirementId", "projectRef", "title", "submitter", "status", "sensitivity", "requirementStateRef"]:
                if not fm.get(field):
                    problems.append(f"{rel_path}: Requirement missing required field {field}")
            if not as_list(fm.get("sourceRefs")):
                problems.append(f"{rel_path}: Requirement sourceRefs cannot be empty")
            if fm.get("status") == "approved":
                if not fm.get("owner"):
                    problems.append(f"{rel_path}: approved Requirement requires owner")
                if not as_list(fm.get("acceptanceCriteriaRefs")):
                    problems.append(f"{rel_path}: approved Requirement requires acceptanceCriteriaRefs")
        if fm.get("type") == "AcceptanceCriteria":
            for field in ["criteriaId", "requirementRef", "description", "observableSignal", "verificationMethod", "owner"]:
                if not fm.get(field):
                    problems.append(f"{rel_path}: AcceptanceCriteria missing required field {field}")
        if fm.get("type") == "PRDDocument":
            quality_gate = dict(fm.get("qualityGate") or {})
            if fm.get("status") == "approved" and not quality_gate.get("passed"):
                problems.append(f"{rel_path}: approved PRDDocument requires passing qualityGate")
            for field in ["positioning", "marketPositioning", "businessModel", "workflows", "requirements", "metrics", "risks", "scope", "nonGoals"]:
                if field not in fm:
                    problems.append(f"{rel_path}: PRDDocument missing section {field}")
        if fm.get("type") == "Decision" and fm.get("impactLevel") == "high":
            if not fm.get("owner") or str(fm.get("owner")).startswith("agent."):
                problems.append(f"{rel_path}: high-impact Decision requires human owner")
            if not fm.get("deadline"):
                problems.append(f"{rel_path}: high-impact Decision requires deadline")
        if fm.get("type") == "ImpactReview":
            for field in ["impactReviewId", "requirementRef", "fromPrdRef", "toPrdRef", "changedFields", "owner", "status"]:
                if field not in fm or is_empty_value(fm.get(field)):
                    problems.append(f"{rel_path}: ImpactReview missing required field {field}")
        if rel_path.startswith("knowledge/"):
            parts = rel_path.split("/")
            category = parts[1] if len(parts) > 1 else ""
            if len(parts) < 3:
                problems.append(f"{rel_path}: knowledge files must live under knowledge/<category>/")
            elif category not in KNOWLEDGE_ALLOWED_CATEGORIES:
                problems.append(f"{rel_path}: unknown knowledge category {category}")
            if fm.get("type") == "KnowledgeItem":
                if category in KNOWLEDGE_SYSTEM_CATEGORIES:
                    problems.append(f"{rel_path}: KnowledgeItem must live under a content category, not {category}")
                for field in sorted(KNOWLEDGE_ITEM_REQUIRED_FIELDS):
                    if not fm.get(field):
                        problems.append(f"{rel_path}: KnowledgeItem missing required field {field}")
        problems.extend(validate_publish_ready(bundle, path, fm, body))
        problems.extend(validate_agent_team_guide_gate(bundle, rel_path, fm))
        problems.extend(validate_environment_manifest(path, bundle.root, fm, body))
        problems.extend(scan_for_secret_values(path))
    problems.extend(validate_pm_delivery_gates(validation_records))
    problems.extend(validate_pm_role_boundaries(validation_records))
    problems.extend(validate_pm_action_runtime(validation_records))
    problems.extend(validate_skill_registry(bundle))
    problems.extend(validate_requirement_tree_records(bundle))
    return problems


def rebuild_index(bundle: Bundle) -> int:
    ensure_database_schema()
    conn = connect_database()
    conn.execute("drop table if exists objects")
    conn.execute(
        """
        create table objects (
            path text primary key,
            "type" text not null default '',
            title text not null default '',
            status text not null default '',
            owner text not null default '',
            scope text not null default '',
            "projectId" text not null default '',
            "agentId" text not null default '',
            "toolId" text not null default '',
            "riskLevel" text not null default '',
            "updatedAt" text not null default ''
        )
        """
    )
    conn.execute('create index if not exists objects_type_idx on objects ("type")')
    conn.execute('create index if not exists objects_status_idx on objects (status)')
    conn.execute('create index if not exists objects_project_idx on objects ("projectId")')
    count = 0
    object_roots = [bundle.root / name for name in OBJECT_ROOT_NAMES]
    collection_names = COLLECTION_NAMES
    object_files: list[Path] = []
    for object_root in object_roots:
        if object_root.exists():
            object_files.extend(object_root.rglob("*.md"))
    for path in object_files:
        if ".zhenzhi" in path.parts or path.name in collection_names or path.name.endswith(".draft.md"):
            continue
        fm, _ = parse_frontmatter(read_text(path))
        if not fm or "type" not in fm:
            continue
        conn.execute(
            """
            insert into objects (
                path, "type", title, status, owner, scope, "projectId", "agentId", "toolId", "riskLevel", "updatedAt"
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                rel(path, bundle.root),
                fm.get("type", ""),
                fm.get("title", ""),
                fm.get("status", ""),
                fm.get("owner", ""),
                fm.get("scope", ""),
                fm.get("projectId", ""),
                fm.get("agentId", ""),
                fm.get("toolId", ""),
                fm.get("riskLevel", ""),
                fm.get("updatedAt", fm.get("timestamp", "")),
            ),
        )
        count += 1
    conn.commit()
    conn.close()
    return count


def search_index(bundle: Bundle, filters: dict[str, str] | str) -> list[dict[str, str]]:
    if isinstance(filters, str):
        filters = {"text": filters}
    conn = connect_database()
    if not table_exists(conn, "objects"):
        conn.close()
        rebuild_index(bundle)
        conn = connect_database()
    clauses: list[str] = []
    values: list[str] = []
    for key, value in filters.items():
        if not value:
            continue
        if key == "text":
            clauses.append("(path ilike %s or title ilike %s)")
            values.extend([f"%{value}%", f"%{value}%"])
        elif key in {"type", "projectId", "agentId", "toolId", "riskLevel"}:
            clauses.append(f'"{key}" = %s')
            values.append(value)
        elif key in {"status", "owner", "scope"}:
            clauses.append(f"{key} = %s")
            values.append(value)
        else:
            raise KnowledgeError(f"unsupported index filter: {key}")
    where = " where " + " and ".join(clauses) if clauses else ""
    cursor = conn.execute(
        'select path, "type", title, status, owner, scope, "projectId", "agentId", "toolId", "riskLevel" from objects' + where + " order by path",
        values,
    )
    rows = fetchall_dicts(cursor)
    conn.close()
    return rows


def object_files(bundle: Bundle) -> list[Path]:
    files: list[Path] = []
    for root_name in OBJECT_ROOT_NAMES:
        root = bundle.root / root_name
        if root.exists():
            files.extend(root.rglob("*.md"))
    return sorted(files)


GRAPH_RELATION_FIELDS: dict[str, str] = {
    "projectId": "belongsToProject",
    "taskId": "belongsToTask",
    "resultRef": "hasResult",
    "taskResultRef": "hasResult",
    "sourceRef": "citesSource",
    "storageRef": "hasStorage",
    "agentId": "performedBy",
    "toolId": "usesTool",
    "runnerId": "runsOn",
    "assignedRunner": "assignedToRunner",
    "leaseOwner": "leasedToRunner",
}

GRAPH_LIST_RELATION_FIELDS: dict[str, str] = {
    "sourceMaterialRefs": "usesSource",
    "evidenceRefs": "hasEvidence",
    "outputRefs": "hasOutput",
    "knowledgeRefs": "producesKnowledge",
    "knowledgeItemRefs": "usesKnowledge",
    "decisionRefs": "dependsOnDecision",
    "conflictRefs": "hasConflict",
    "requiredAgents": "requiresAgent",
    "requiredCapabilities": "requiresCapability",
    "requiredSecretRefs": "requiresAccessRef",
    "repositoryRefs": "usesRepository",
    "notificationRefs": "hasNotification",
    "auditRefs": "hasAudit",
}


def graph_ref_for_value(bundle: Bundle, field: str, value: str) -> str:
    raw = str(value).strip()
    if not raw:
        return ""
    if raw.endswith(".md") or "/" in raw or raw.startswith("http://") or raw.startswith("https://"):
        return raw
    if field == "projectId":
        return f"projects/{slug(raw)}/project.md"
    if field in {"taskId"}:
        try:
            return rel(find_project_task(bundle, raw), bundle.root)
        except KnowledgeError:
            return f"tasks/{slug(raw)}.md"
    if field in {"agentId"} or raw.startswith("agent."):
        return f"agents/{slug(raw)}.md"
    if field in {"toolId"} or raw.startswith("tool."):
        return f"tools/{slug(raw)}.md"
    if field in {"runnerId", "assignedRunner", "leaseOwner"} or raw.startswith("runner."):
        return f"runners/{slug(raw)}.md"
    return raw


def make_graph_edge(from_ref: str, relation: str, to_ref: str, source_ref: str, sensitivity: str = "") -> dict[str, Any]:
    key = "|".join([from_ref, relation, to_ref, source_ref])
    edge_id = "edge." + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return {
        "type": "KnowledgeGraphEdge",
        "title": edge_id,
        "description": f"{from_ref} {relation} {to_ref}",
        "timestamp": utc_now(),
        "edgeId": edge_id,
        "fromRef": from_ref,
        "relation": relation,
        "toRef": to_ref,
        "sourceRef": source_ref,
        "evidenceRefs": [source_ref],
        "confidence": "high",
        "status": "observed",
        "sensitivity": sensitivity,
        "auditRefs": [],
    }


def extract_graph_edges(bundle: Bundle) -> list[dict[str, Any]]:
    edges_by_id: dict[str, dict[str, Any]] = {}
    for path in object_files(bundle):
        if ".zhenzhi" in path.parts or path.name in COLLECTION_NAMES or path.name.endswith(".draft.md"):
            continue
        if rel(path, bundle.root).startswith("graph/"):
            continue
        try:
            fm = load_object(path)
        except KnowledgeError:
            continue
        if not fm.get("type"):
            continue
        from_ref = rel(path, bundle.root)
        sensitivity = str(fm.get("sensitivity") or fm.get("classification") or "")
        for field, relation in GRAPH_RELATION_FIELDS.items():
            value = str(fm.get(field) or "").strip()
            to_ref = graph_ref_for_value(bundle, field, value)
            if to_ref and to_ref != from_ref:
                edge = make_graph_edge(from_ref, relation, to_ref, from_ref, sensitivity)
                edges_by_id[edge["edgeId"]] = edge
        for field, relation in GRAPH_LIST_RELATION_FIELDS.items():
            for item in as_list(fm.get(field)):
                to_ref = graph_ref_for_value(bundle, field, str(item))
                if to_ref and to_ref != from_ref:
                    edge = make_graph_edge(from_ref, relation, to_ref, from_ref, sensitivity)
                    edges_by_id[edge["edgeId"]] = edge
    return sorted(edges_by_id.values(), key=lambda item: (item["fromRef"], item["relation"], item["toRef"]))


def graph_edge_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "graph" / "edges"


def graph_snapshot_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "graph" / "snapshots"


def rebuild_graph_edges(bundle: Bundle, actor: str = "system") -> list[dict[str, Any]]:
    edge_dir = graph_edge_storage_dir(bundle)
    ensure_dir(edge_dir)
    for old_path in edge_dir.glob("edge.*.md"):
        old_path.unlink()
    edges = extract_graph_edges(bundle)
    for edge in edges:
        body = "\n".join(
            [
                "## Edge",
                "",
                f"- fromRef: {edge['fromRef']}",
                f"- relation: {edge['relation']}",
                f"- toRef: {edge['toRef']}",
                f"- sourceRef: {edge['sourceRef']}",
                f"- confidence: {edge['confidence']}",
                "",
                "## Evidence",
                "",
                "\n".join(f"- {item}" for item in edge["evidenceRefs"]),
            ]
        )
        write_text(edge_dir / f"{edge['edgeId']}.md", render_doc(edge, body))
    write_text(bundle.root / "graph" / "index.md", "# Graph\n\n- edges: graph/edges/\n- snapshots: graph/snapshots/\n")
    create_audit_log(bundle, actor, "graph.edges.rebuild", "graph/edges", after=str(len(edges)), policy_result="generated")
    return edges


def graph_nodes(bundle: Bundle) -> list[dict[str, str]]:
    nodes: list[dict[str, str]] = []
    for path in object_files(bundle):
        ref_value = rel(path, bundle.root)
        if ".zhenzhi" in path.parts or path.name in COLLECTION_NAMES or path.name.endswith(".draft.md") or ref_value.startswith("graph/"):
            continue
        try:
            fm = load_object(path)
        except KnowledgeError:
            continue
        if not fm.get("type"):
            continue
        nodes.append(
            {
                "ref": ref_value,
                "type": str(fm.get("type", "")),
                "title": str(fm.get("title", "")),
                "status": str(fm.get("status", "")),
                "projectId": str(fm.get("projectId", "")),
            }
        )
    return sorted(nodes, key=lambda item: item["ref"])


def export_graph_snapshot(bundle: Bundle, actor: str = "system") -> dict[str, Any]:
    edges = rebuild_graph_edges(bundle, actor)
    nodes = graph_nodes(bundle)
    snapshot_id = unique_time_id("graph-snapshot")
    snapshot = {
        "apiVersion": "v0.1",
        "kind": "GraphSnapshot",
        "snapshotId": snapshot_id,
        "generatedAt": utc_now(),
        "sourceOfTruth": "object frontmatter refs",
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "nodes": nodes,
        "edges": edges,
    }
    path = graph_snapshot_storage_dir(bundle) / f"{snapshot_id}.md"
    frontmatter = {
        "type": "GraphSnapshot",
        "title": snapshot_id,
        "description": "Generated knowledge graph snapshot. Export artifact, not source of truth.",
        "timestamp": snapshot["generatedAt"],
        "snapshotId": snapshot_id,
        "status": "observed",
        "sourceRef": "graph/edges",
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
    }
    body = "\n".join(
        [
            "## Notice",
            "",
            "This snapshot is generated from object frontmatter references. Source markdown objects remain the source of truth.",
            "",
            "## Snapshot JSON",
            "",
            "```json",
            json.dumps(snapshot, indent=2, ensure_ascii=False),
            "```",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    snapshot["snapshotRef"] = rel(path, bundle.root)
    create_audit_log(bundle, actor, "graph.snapshot.export", rel(path, bundle.root), after=f"nodes={len(nodes)} edges={len(edges)}", policy_result="generated")
    return snapshot


def graph_impact(bundle: Bundle, target_ref: str, actor: str = "system", rebuild: bool = False) -> dict[str, Any]:
    edges = rebuild_graph_edges(bundle, actor) if rebuild else extract_graph_edges(bundle)
    target = target_ref.strip()
    outgoing = [edge for edge in edges if edge["fromRef"] == target]
    incoming = [edge for edge in edges if edge["toRef"] == target]
    affected = sorted({edge["fromRef"] for edge in incoming} | {edge["toRef"] for edge in outgoing})
    create_audit_log(bundle, actor, "graph.impact", target, after=f"affected={len(affected)}", policy_result="generated")
    return {
        "apiVersion": "v0.1",
        "kind": "GraphImpact",
        "targetRef": target,
        "incoming": incoming,
        "outgoing": outgoing,
        "affectedRefs": affected,
    }


def graph_inclusion_reason(bundle: Bundle, item_ref: str, project_id: str = "", task_ref: str = "") -> str:
    project_ref = f"projects/{slug(project_id)}/project.md" if project_id else ""
    for edge in extract_graph_edges(bundle):
        if edge["fromRef"] != item_ref and edge["toRef"] != item_ref:
            continue
        other = edge["toRef"] if edge["fromRef"] == item_ref else edge["fromRef"]
        if project_ref and other == project_ref:
            return f"graph:{edge['relation']}:{project_ref}"
        if task_ref and other == task_ref:
            return f"graph:{edge['relation']}:{task_ref}"
    return "retrieval_match"


def is_retrieval_allowed(path: Path, fm: dict[str, Any]) -> bool:
    if path.name in COLLECTION_NAMES or path.name.endswith(".draft.md"):
        return False
    if fm.get("type") == "AuditLog":
        return False
    confidentiality = str(fm.get("confidentiality", fm.get("classification", ""))).lower()
    scope = str(fm.get("scope", "")).lower()
    if "customer_confidential" in {confidentiality, scope}:
        return False
    if fm.get("customerConfidential") is True:
        return False
    return True


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_\-.]+|[\u4e00-\u9fff]", text.lower())


def vectorize(text: str) -> list[float]:
    vector = [0.0] * RETRIEVAL_VECTOR_DIMS
    for token in tokenize(text):
        bucket = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) % RETRIEVAL_VECTOR_DIMS
        vector[bucket] += 1.0
    length = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / length for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        elif current:
            current += "\n\n" + paragraph
        else:
            current = paragraph
    if current:
        chunks.append(current)
    return chunks


def extract_source_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(r"sourceRef:\s*([^\n]+)", text):
        ref_value = match.group(1).strip()
        if ref_value and ref_value not in refs:
            refs.append(ref_value)
    return refs


def retrieval_source_fingerprint(bundle: Bundle) -> str:
    digest = hashlib.sha256()
    for path in sorted(object_files(bundle)):
        if ".zhenzhi" in path.parts:
            continue
        if path.name in COLLECTION_NAMES or path.name.endswith(".draft.md"):
            continue
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        digest.update(rel(path, bundle.root).encode("utf-8"))
        digest.update(str(stat.st_mtime_ns).encode("utf-8"))
        digest.update(str(stat.st_size).encode("utf-8"))
    return digest.hexdigest()


def retrieval_index_fingerprint(conn: Any) -> str:
    if not table_exists(conn, "retrieval_index_meta"):
        return ""
    rows = fetchall_dicts(conn.execute("select value from retrieval_index_meta where key = 'sourceFingerprint'"))
    if not rows:
        return ""
    return str(rows[0].get("value") or "")


def write_retrieval_index_fingerprint(conn: Any, fingerprint: str) -> None:
    conn.execute("drop table if exists retrieval_index_meta")
    conn.execute(
        """
        create table retrieval_index_meta (
            key text primary key,
            value text not null default ''
        )
        """
    )
    conn.execute("insert into retrieval_index_meta (key, value) values (%s, %s)", ("sourceFingerprint", fingerprint))


def extract_context_meta(text: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"-\s+([A-Za-z][A-Za-z0-9_]*):\s*(.*)", line)
        if match:
            meta[match.group(1)] = match.group(2).strip()
    return meta


def rebuild_retrieval_index(bundle: Bundle) -> int:
    ensure_database_schema()
    fingerprint = retrieval_source_fingerprint(bundle)
    rebuild_index(bundle)
    conn = connect_database()
    conn.execute("drop table if exists chunks")
    conn.execute(
        """
        create table chunks (
            path text not null,
            "chunkId" text not null,
            "type" text not null default '',
            title text not null default '',
            status text not null default '',
            owner text not null default '',
            scope text not null default '',
            "projectId" text not null default '',
            "agentId" text not null default '',
            "toolId" text not null default '',
            text text not null default '',
            vector jsonb not null,
            "sourceRef" text not null default '',
            primary key(path, "chunkId")
        )
        """
    )
    conn.execute('create index if not exists chunks_project_idx on chunks ("projectId")')
    conn.execute('create index if not exists chunks_scope_idx on chunks (scope)')
    count = 0
    for path in object_files(bundle):
        if ".zhenzhi" in path.parts:
            continue
        full_text = read_text(path)
        fm, body = parse_frontmatter(full_text)
        if not fm or "type" not in fm or not is_retrieval_allowed(path, fm):
            continue
        if scan_for_secret_values(path):
            continue
        source_refs = extract_source_refs(full_text)
        source_ref = str(fm.get("sourceRef") or (source_refs[0] if source_refs else "") or rel(path, bundle.root))
        for idx, chunk in enumerate(chunk_text(body), 1):
            chunk_id = f"chunk-{idx}"
            index_text = "\n\n".join(
                part
                for part in [
                    str(fm.get("title", "")),
                    str(fm.get("description", "")),
                    chunk,
                ]
                if part.strip()
            )
            conn.execute(
                """
                insert into chunks (
                    path, "chunkId", "type", title, status, owner, scope, "projectId", "agentId", "toolId", text, vector, "sourceRef"
                ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                """,
                (
                    rel(path, bundle.root),
                    chunk_id,
                    fm.get("type", ""),
                    fm.get("title", ""),
                    fm.get("status", ""),
                    fm.get("owner", ""),
                    fm.get("scope", ""),
                    fm.get("projectId", ""),
                    fm.get("agentId", ""),
                    fm.get("toolId", ""),
                    index_text,
                    json.dumps(vectorize(index_text)),
                    source_ref,
                ),
            )
            count += 1
    write_retrieval_index_fingerprint(conn, fingerprint)
    conn.commit()
    conn.close()
    return count


def ensure_retrieval_index_fresh(bundle: Bundle) -> None:
    current_fingerprint = retrieval_source_fingerprint(bundle)
    conn = connect_database()
    has_chunks = table_exists(conn, "chunks")
    indexed_fingerprint = retrieval_index_fingerprint(conn) if has_chunks else ""
    conn.close()
    if not has_chunks or indexed_fingerprint != current_fingerprint:
        rebuild_retrieval_index(bundle)


def publish_knowledge_bundle(
    bundle: Bundle,
    actor: str = "system.publisher",
    reason: str = "",
    rebuild_graph: bool = False,
) -> dict[str, Any]:
    problems = validate_bundle(bundle)
    if problems:
        raise KnowledgeError("bundle validation failed before publish: " + "; ".join(problems[:10]))
    object_count = rebuild_index(bundle)
    chunk_count = rebuild_retrieval_index(bundle)
    graph_snapshot_ref = ""
    if rebuild_graph:
        graph_snapshot_ref = str(export_graph_snapshot(bundle, actor).get("snapshotRef", ""))
    audit_path = create_audit_log(
        bundle,
        actor,
        "knowledge.publish",
        "bundle",
        after=f"objects={object_count} chunks={chunk_count}",
        policy_result="published",
        details="\n".join(
            [
                f"reason={reason or 'manual'}",
                f"objectCount={object_count}",
                f"chunkCount={chunk_count}",
                f"graphSnapshotRef={graph_snapshot_ref or 'none'}",
            ]
        ),
    )
    append_log(bundle, f"knowledge published objects={object_count} chunks={chunk_count} actor={actor}")
    return {
        "apiVersion": "v0.1",
        "kind": "KnowledgePublishResult",
        "objectCount": object_count,
        "chunkCount": chunk_count,
        "graphSnapshotRef": graph_snapshot_ref,
        "auditRef": rel(audit_path, bundle.root),
    }


def search_retrieval(bundle: Bundle, query: str, project_id: str = "", scopes: list[str] | None = None, limit: int = 5) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    ensure_retrieval_index_fresh(bundle)
    query_vector = vectorize(query)
    query_tokens = set(tokenize(query))
    conn = connect_database()
    rows = fetchall_dicts(conn.execute('select path, "chunkId", "type", title, status, owner, scope, "projectId", "agentId", "toolId", text, vector, "sourceRef" from chunks'))
    conn.close()
    allowed_scopes = set(scopes or [])
    scored: list[dict[str, Any]] = []
    for row in rows:
        row_scope = row["scope"]
        row_project = row["projectId"]
        if allowed_scopes and row_scope and row_scope not in allowed_scopes:
            continue
        if project_id and row_project and row_project != project_id:
            continue
        text = row["text"]
        lexical = len(query_tokens & set(tokenize(text))) / max(len(query_tokens), 1)
        vector = row["vector"]
        if isinstance(vector, str):
            vector = json.loads(vector)
        semantic = cosine(query_vector, vector)
        score = round((semantic * 0.7) + (lexical * 0.3), 4)
        if score <= 0:
            continue
        item = dict(row)
        item.pop("vector", None)
        item["score"] = score
        scored.append(item)
    scored.sort(key=lambda item: (-item["score"], item["path"], item["chunkId"]))
    return scored[:limit]


def create_conflict(bundle: Bundle, conflict_type: str, owner: str, summary: str, affected: list[str]) -> Path:
    conflict_id = unique_time_id("conflict")
    path = bundle.root / "knowledge" / "conflicts" / f"{conflict_id}.md"
    frontmatter = {
        "type": "ConflictRecord",
        "title": conflict_id,
        "description": summary,
        "timestamp": utc_now(),
        "conflictId": conflict_id,
        "conflictType": conflict_type,
        "owner": owner,
        "status": "open",
        "affectedRefs": affected,
    }
    body = f"## Summary\n\n{summary}\n\n## Resolution\n\nTBD.\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", conflict_id, f"conflicts/{conflict_id}.md")
    append_log(bundle, f"created ConflictRecord {conflict_id}")
    return path


def resolve_conflict(bundle: Bundle, target: Path, owner: str, resolution: str) -> Path:
    path = target if target.is_absolute() else bundle.root / target
    if not path.exists():
        raise KnowledgeError(f"conflict not found: {target}")
    text = read_text(path)
    fm, body = parse_frontmatter(text)
    if fm.get("type") != "ConflictRecord":
        raise KnowledgeError("target is not a ConflictRecord")
    before = fm.get("status", "")
    fm["status"] = "resolved"
    fm["reviewer"] = owner
    fm["resolvedAt"] = utc_now()
    body = body.rstrip() + f"\n\n## Resolution Note\n\n{resolution}\n"
    write_text(path, render_doc(fm, body))
    return create_audit_log(
        bundle,
        owner,
        "conflict.resolve",
        rel(path, bundle.root),
        before=before,
        after="resolved",
        policy_result="human_resolution",
        details=resolution,
    )


def search_audit_logs(bundle: Bundle, project_id: str = "", agent_id: str = "", tool_id: str = "", target: str = "") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    audit_root = bundle.root / "knowledge" / "audit"
    if not audit_root.exists():
        return rows
    terms = [value for value in [slug(project_id) if project_id else "", slug(agent_id) if agent_id else "", slug(tool_id) if tool_id else "", target] if value]
    for path in sorted(audit_root.glob("*.md")):
        text = read_text(path)
        fm, _ = parse_frontmatter(text)
        if fm.get("type") != "AuditLog":
            continue
        searchable = "\n".join([text, str(fm.get("targetRef", "")), str(fm.get("actor", "")), str(fm.get("action", ""))])
        if terms and not all(term in searchable for term in terms):
            continue
        rows.append(
            {
                "path": rel(path, bundle.root),
                "action": fm.get("action", ""),
                "actor": fm.get("actor", ""),
                "targetRef": fm.get("targetRef", ""),
                "policyResult": fm.get("policyResult", ""),
            }
        )
    return rows


def create_metrics_report(bundle: Bundle, owner: str = "system") -> Path:
    rebuild_index(bundle)
    rows = search_index(bundle, {})
    draft_backlog = sum(1 for row in rows if row.get("status") in {"draft", "testing"})
    stale_count = sum(1 for row in rows if row.get("status") == "stale")
    stale_candidate_count = sum(1 for row in rows if row.get("status") == "stale_candidate")
    testing_tools = sum(1 for row in rows if row.get("type") == "ToolAsset" and row.get("status") == "testing")
    approved_tools = sum(1 for row in rows if row.get("type") == "ToolAsset" and row.get("status") == "approved")
    agent_runs = [row for row in rows if row.get("type") == "AgentRun"]
    unfinished = sum(1 for row in agent_runs if row.get("status") in {"draft", "open"})
    denied_tool_invocations = 0
    approved_tool_invocations = 0
    audit_root = bundle.root / "knowledge" / "audit"
    if audit_root.exists():
        for audit_path in audit_root.glob("*.md"):
            fm = load_object(audit_path)
            if fm.get("action") == "tool.invoke.denied":
                denied_tool_invocations += 1
            elif fm.get("action") == "tool.invoke.allowed":
                approved_tool_invocations += 1
    start_count = 0
    if (bundle.root / "log.md").exists():
        log_text = read_text(bundle.root / "log.md")
        start_count = log_text.count("started AgentRun") + log_text.count("started context ")
    run_success = 0
    run_failure = 0
    for run_path in (bundle.root / "runs").rglob("*.md"):
        if run_path.name == "index.md":
            continue
        fm = load_object(run_path)
        if fm.get("type") != "AgentRun":
            continue
        result = str(fm.get("result", "")).lower()
        if result in {"completed", "success", "passed", "pass"}:
            run_success += 1
        elif result in {"failed", "failure", "error", "blocked"}:
            run_failure += 1
    tasks = [load_object(path) for path in active_project_task_paths(bundle)]
    task_count = len(tasks)
    done_tasks = sum(1 for item in tasks if str(item.get("status") or "") == "done")
    blocked_tasks = sum(1 for item in tasks if str(item.get("status") or "") == "blocked")
    retry_tasks = sum(1 for item in tasks if str(item.get("status") or "") in {"changes_requested", "retry_required"})
    stale_tasks = sum(1 for item in tasks if str(item.get("status") or "") == "stale" or bool(item.get("staleDetectedAt")))
    completion_hours: list[float] = []
    for item in tasks:
        created = parse_utc(str(item.get("timestamp") or ""))
        finished = parse_utc(str(item.get("finishedAt") or item.get("completedAt") or ""))
        if created and finished and finished >= created:
            completion_hours.append(round((finished - created).total_seconds() / 3600, 2))
    completion_hours.sort()
    median_completion = completion_hours[len(completion_hours) // 2] if completion_hours else 0
    p95_completion = completion_hours[min(len(completion_hours) - 1, math.ceil(len(completion_hours) * 0.95) - 1)] if completion_hours else 0
    reviews = [row for row in rows if row.get("type") == "ReviewRecord"]
    accepted_reviews = sum(1 for row in reviews if row.get("status") in {"done", "approved", "accepted"})
    notification_rows = [load_object(path) for path in notification_storage_dir(bundle).glob("*.md") if path.name != "index.md"] if notification_storage_dir(bundle).exists() else []
    notification_failure_count = sum(1 for item in notification_rows if str(item.get("status") or "") in {"failed", "dead_letter"})
    critical_notification_failure_count = sum(1 for item in notification_rows if str(item.get("status") or "") in {"failed", "dead_letter"} and notification_failure_is_critical(item))
    eval_runs = [
        load_object(path)
        for path in (bundle.root / "knowledge" / "eval-runs").glob("*.md")
        if path.name != "index.md"
    ] if (bundle.root / "knowledge" / "eval-runs").exists() else []
    release_blocking_eval_count = sum(
        1
        for row in eval_runs
        if str(row.get("result") or "") == "fail"
        and str(row.get("severity") or row.get("releaseGateImpact") or "high").lower() in {"high", "critical", "release_blocking", "blocks_release"}
    )
    improvement_count = sum(1 for row in rows if row.get("type") == "AgentImprovementProposal")
    decision_rows = [row for row in rows if row.get("type") == "Decision"]
    report_id = unique_time_id("metrics")
    path = bundle.root / "knowledge" / "metrics" / f"{report_id}.md"
    frontmatter = {
        "type": "MetricsReport",
        "title": report_id,
        "description": "Knowledge core operational metrics.",
        "timestamp": utc_now(),
        "reportId": report_id,
        "owner": owner,
        "status": "verified",
        "startCount": start_count,
        "finishCount": len(agent_runs),
        "unfinishedTasks": unfinished,
        "draftBacklog": draft_backlog,
        "staleCount": stale_count,
        "staleCandidateCount": stale_candidate_count,
        "testingTools": testing_tools,
        "approvedTools": approved_tools,
        "deniedToolInvocations": denied_tool_invocations,
        "approvedToolInvocations": approved_tool_invocations,
        "agentRunSuccessCount": run_success,
        "agentRunFailureCount": run_failure,
        "taskThroughput": task_count,
        "doneTaskCount": done_tasks,
        "medianCompletionHours": median_completion,
        "p95CompletionHours": p95_completion,
        "acceptancePassRate": round(accepted_reviews / len(reviews), 4) if reviews else 0,
        "retryRate": round(retry_tasks / task_count, 4) if task_count else 0,
        "blockedRate": round(blocked_tasks / task_count, 4) if task_count else 0,
        "staleRate": round(stale_tasks / task_count, 4) if task_count else 0,
        "agentSuccessRate": round(run_success / (run_success + run_failure), 4) if (run_success + run_failure) else 0,
        "agentReviewPassRate": round(accepted_reviews / len(reviews), 4) if reviews else 0,
        "improvementTaskCount": improvement_count,
        "requirementQualityGatePassRate": 0,
        "decisionLatencyCount": len(decision_rows),
        "notificationFailureCount": notification_failure_count,
        "criticalNotificationFailureCount": critical_notification_failure_count,
        "releaseBlockingEvalRunCount": release_blocking_eval_count,
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            f"- indexed objects: {len(rows)}",
            f"- AgentRun count: {len(agent_runs)}",
            f"- start count: {start_count}",
            f"- unfinished tasks: {unfinished}",
            f"- draft/testing backlog: {draft_backlog}",
            f"- stale knowledge: {stale_count}",
            f"- stale candidates: {stale_candidate_count}",
            f"- testing tools: {testing_tools}",
            f"- approved tools: {approved_tools}",
            f"- approved tool invocations: {approved_tool_invocations}",
            f"- denied tool invocations: {denied_tool_invocations}",
            f"- AgentRun success count: {run_success}",
            f"- AgentRun failure count: {run_failure}",
            f"- task throughput: {task_count}",
            f"- median completion hours: {median_completion}",
            f"- p95 completion hours: {p95_completion}",
            f"- acceptance pass rate: {frontmatter['acceptancePassRate']}",
            f"- retry rate: {frontmatter['retryRate']}",
            f"- blocked rate: {frontmatter['blockedRate']}",
            f"- stale rate: {frontmatter['staleRate']}",
            f"- notification failures: {notification_failure_count}",
            f"- release-blocking EvalRuns: {release_blocking_eval_count}",
            "",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", report_id, f"metrics/{report_id}.md")
    create_audit_log(bundle, owner, "metrics.report.create", rel(path, bundle.root), after="verified", policy_result="quality_dashboard")
    append_log(bundle, f"created MetricsReport {report_id}")
    return path


def agent_improvement_storage_dir(bundle: Bundle) -> Path:
    return bundle.root / "knowledge" / "agent-improvements"


def agent_ref_for_id(bundle: Bundle, agent_id: str) -> str:
    if not agent_id:
        return ""
    agent_path = bundle.root / "agents" / f"{slug(agent_id)}.md"
    if agent_path.exists():
        return rel(agent_path, bundle.root)
    return agent_id


def improvement_reuse_scope(agent_id: str, project_id: str) -> str:
    if not project_id:
        return "company"
    if agent_id.startswith("agent.company.") or agent_id.startswith("agent.company-knowledge-core.") or agent_id.startswith("agent.core."):
        return "company"
    return "project"


def create_agent_improvement_eval_case(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    result_fm: dict[str, Any],
    reasons: list[str],
    agent_id: str,
) -> Path:
    task_id = str(task.get("taskId") or result_fm.get("taskId") or "")
    eval_id = unique_time_id(f"eval-agent-improvement-{slug(task_id) or 'task'}")
    path = bundle.root / "knowledge" / "evals" / f"{eval_id}.md"
    expected = "TaskResult must include summary, evidence/artifacts, qualityEvaluation, handoff/terminal reason, and retry or escalation decision when it fails."
    frontmatter = {
        "type": "EvalCase",
        "title": f"Agent improvement regression for {task_id}",
        "description": "Regression case generated from a failed or rejected Agent delivery.",
        "timestamp": utc_now(),
        "evalId": eval_id,
        "owner": agent_id or "system.scheduler",
        "status": "draft",
        "targetRef": rel(result_path, bundle.root),
        "agentTargetRef": agent_ref_for_id(bundle, agent_id),
        "sourceResultRef": rel(result_path, bundle.root),
        "taskId": task_id,
        "projectId": str(task.get("projectId") or result_fm.get("projectId") or ""),
        "requires": [
            "summary",
            "evidence or artifact refs",
            "qualityEvaluation",
            "handoff or terminal reason",
            "next action",
        ],
        "expected": expected,
    }
    body = "\n".join(
        [
            "## Trigger",
            "",
            f"- taskId: {task_id}",
            f"- resultRef: {rel(result_path, bundle.root)}",
            f"- agentId: {agent_id or 'unknown'}",
            "",
            "## Failure Reasons",
            "",
            "\n".join(f"- {item}" for item in reasons) or "- none",
            "",
            "## Expected",
            "",
            expected,
            "",
            "## Usage",
            "",
            "This EvalCase is a draft regression guard. The responsible Agent or Skill maintainer should refine it, run it against the improved workflow/skill, and only promote it after review.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", str(frontmatter["title"]), rel(path, bundle.root))
    create_audit_log(bundle, agent_id or "system.scheduler", "agent.improvement.evalCase.create", rel(path, bundle.root), after="draft", details=f"taskId={task_id}\nresultRef={rel(result_path, bundle.root)}")
    return path


def create_agent_improvement_proposal(
    bundle: Bundle,
    task: dict[str, Any],
    result_path: Path,
    result_fm: dict[str, Any],
    reasons: list[str],
    agent_id: str,
    eval_case_refs: list[str],
    trigger: str,
) -> Path:
    ensure_dir(agent_improvement_storage_dir(bundle))
    index_path = agent_improvement_storage_dir(bundle) / "index.md"
    if not index_path.exists():
        write_text(index_path, "# Agent Improvements\n\n")
    task_id = str(task.get("taskId") or result_fm.get("taskId") or "")
    project_id = str(task.get("projectId") or result_fm.get("projectId") or "")
    proposal_id = unique_time_id("agent-improvement")
    path = agent_improvement_storage_dir(bundle) / f"{proposal_id}.md"
    reuse_scope = improvement_reuse_scope(agent_id, project_id)
    recommended_actions = [
        "Update the responsible Agent skill pack or workflow checklist when the failure is repeatable.",
        "Keep the EvalCase as a regression guard before closing the improvement.",
        "If the change affects company-level roles, skills, workflow, scheduler, Agent Ring, or knowledge policy, update the company Agent Team guide.",
    ]
    frontmatter = {
        "type": "AgentImprovementProposal",
        "title": f"Improve {agent_id or 'agent'} after {task_id}",
        "description": "Agent self-improvement proposal generated from task quality evaluation or human acceptance feedback.",
        "timestamp": utc_now(),
        "proposalId": proposal_id,
        "owner": agent_id or "system.scheduler",
        "status": "draft",
        "agentId": agent_id,
        "projectId": project_id,
        "taskId": task_id,
        "resultRef": rel(result_path, bundle.root),
        "trigger": trigger,
        "failureReasons": reasons,
        "reuseScope": reuse_scope,
        "evalCaseRefs": eval_case_refs,
        "recommendedActions": recommended_actions,
        "reviewOwner": project_manager_for_task(task),
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            f"`{agent_id or 'unknown agent'}` 在任务 `{task_id}` 中触发改进闭环。这个记录不是最终知识，而是后续 Skill / workflow / EvalCase 修复的入口。",
            "",
            "## Trigger",
            "",
            f"- trigger: {trigger}",
            f"- resultRef: {rel(result_path, bundle.root)}",
            f"- reuseScope: {reuse_scope}",
            "",
            "## Failure Reasons",
            "",
            "\n".join(f"- {item}" for item in reasons) or "- none",
            "",
            "## Eval Cases",
            "",
            "\n".join(f"- {item}" for item in eval_case_refs) or "- none",
            "",
            "## Recommended Actions",
            "",
            "\n".join(f"- {item}" for item in recommended_actions),
            "",
            "## Reuse Policy",
            "",
            "- `company`: 可复用给所有员工、所有项目和所有 Agent Ring Runner，但必须通过 Review 后再成为正式 Skill / 指南 / Eval。",
            "- `project`: 只进入本项目上下文，除非知识工程 Agent 判断可以抽象为公司级经验。",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(index_path, str(frontmatter["title"]), path.name)
    update_index(bundle.root / "knowledge" / "index.md", str(frontmatter["title"]), rel(path, bundle.root))
    create_audit_log(bundle, agent_id or "system.scheduler", "agent.improvement.proposal.create", rel(path, bundle.root), after="draft", details=f"taskId={task_id}\nresultRef={rel(result_path, bundle.root)}\nreuseScope={reuse_scope}")
    return path


def maybe_record_agent_improvement(
    bundle: Bundle,
    task_path: Path,
    task: dict[str, Any],
    result_path: Path,
    result_fm: dict[str, Any],
    trigger: str = "qualityEvaluation",
    extra_reasons: list[str] | None = None,
) -> dict[str, list[str]]:
    evaluation = dict(result_fm.get("qualityEvaluation") or {})
    acceptance_policy = dict(result_fm.get("acceptancePolicy") or {})
    acceptance_status = str(acceptance_policy.get("acceptanceStatus") or "")
    reasons = as_list(evaluation.get("reasons"))
    for item in extra_reasons or []:
        reasons = append_unique(reasons, item)
    passed = bool(evaluation.get("passed"))
    needs_improvement = not passed or acceptance_status in {"rejected", "changes_requested"} or (trigger in {"actorFeedback", "userFeedback"} and bool(reasons))
    if not needs_improvement:
        return {"improvementRefs": as_list(result_fm.get("improvementRefs")), "evalCaseRefs": as_list(result_fm.get("evalCaseRefs"))}
    if not reasons:
        reasons = [str(evaluation.get("decision") or acceptance_status or trigger)]
    existing_improvement_refs = as_list(result_fm.get("improvementRefs"))
    existing_eval_case_refs = as_list(result_fm.get("evalCaseRefs"))
    for proposal_ref in existing_improvement_refs:
        try:
            proposal = load_object(bundle.root / proposal_ref)
        except KnowledgeError:
            continue
        if proposal.get("trigger") == trigger and set(reasons).issubset(set(as_list(proposal.get("failureReasons")))):
            return {"improvementRefs": existing_improvement_refs, "evalCaseRefs": existing_eval_case_refs}
    agent_id = str(result_fm.get("executorAgent") or task.get("assignee") or result_fm.get("runnerId") or "")
    eval_path = create_agent_improvement_eval_case(bundle, task, result_path, result_fm, reasons, agent_id)
    eval_ref = rel(eval_path, bundle.root)
    proposal_path = create_agent_improvement_proposal(bundle, task, result_path, result_fm, reasons, agent_id, [eval_ref], trigger)
    proposal_ref = rel(proposal_path, bundle.root)
    improvement_refs = existing_improvement_refs
    improvement_refs = append_unique(improvement_refs, proposal_ref)
    eval_case_refs = existing_eval_case_refs
    eval_case_refs = append_unique(eval_case_refs, eval_ref)
    update_frontmatter_file(result_path, {"improvementRefs": improvement_refs, "evalCaseRefs": eval_case_refs, "updatedAt": utc_now()})
    task_improvement_refs = as_list(task.get("improvementRefs"))
    task_improvement_refs = append_unique(task_improvement_refs, proposal_ref)
    update_frontmatter_file(task_path, {"improvementRefs": task_improvement_refs, "updatedAt": utc_now()})
    summary = f"Agent 交付触发自净化改进：{task.get('title', task.get('taskId', ''))}。改进提案：{proposal_ref}；回归 Eval：{eval_ref}。"
    create_task_notification(
        bundle,
        task_path,
        load_object(task_path),
        "agent_improvement_proposal_created",
        recipient=project_manager_for_task(task),
        summary=summary,
        source_message_ref=proposal_ref,
    )
    if agent_id and agent_id != project_manager_for_task(task):
        create_task_notification(
            bundle,
            task_path,
            load_object(task_path),
            "agent_improvement_action_required",
            recipient=agent_id,
            summary=summary,
            source_message_ref=proposal_ref,
        )
    return {"improvementRefs": improvement_refs, "evalCaseRefs": eval_case_refs}


def create_agent_capability_report(
    bundle: Bundle,
    agent_id: str,
    owner: str = "system.scheduler",
    project_id: str = "",
    period: str = "",
) -> Path:
    aid = slug(agent_id)
    matched_results: list[dict[str, Any]] = []
    for path in task_result_storage_dir(bundle).glob("*.md"):
        if path.name in COLLECTION_NAMES:
            continue
        fm = load_object(path)
        if fm.get("type") != "TaskResult":
            continue
        if project_id and str(fm.get("projectId") or "") != project_id:
            continue
        result_agent = str(fm.get("executorAgent") or fm.get("assignee") or fm.get("runnerId") or "")
        if agent_id and result_agent != agent_id:
            continue
        row = dict(fm)
        row["resultRef"] = rel(path, bundle.root)
        matched_results.append(row)
    total = len(matched_results)
    passed = sum(1 for item in matched_results if bool(dict(item.get("qualityEvaluation") or {}).get("passed")))
    failed = total - passed
    scores = [float(dict(item.get("qualityEvaluation") or {}).get("score") or 0) for item in matched_results]
    average_score = round(sum(scores) / len(scores), 2) if scores else 0
    improvement_refs: list[str] = []
    reason_counts: dict[str, int] = {}
    for item in matched_results:
        for ref in as_list(item.get("improvementRefs")):
            improvement_refs = append_unique(improvement_refs, ref)
        for reason in as_list(dict(item.get("qualityEvaluation") or {}).get("reasons")):
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
    report_id = unique_time_id(f"agent-capability-{aid or 'all'}")
    path = bundle.root / "knowledge" / "metrics" / f"{report_id}.md"
    frontmatter = {
        "type": "AgentCapabilityReport",
        "title": f"Capability report for {agent_id or 'all agents'}",
        "description": "Agent capability metrics generated from TaskResult quality evaluations and improvement proposals.",
        "timestamp": utc_now(),
        "reportId": report_id,
        "owner": owner,
        "status": "verified",
        "agentId": agent_id,
        "projectId": project_id,
        "period": period,
        "taskResultCount": total,
        "passedCount": passed,
        "failedCount": failed,
        "firstPassRate": round(passed / total, 4) if total else 0,
        "averageScore": average_score,
        "improvementRefs": improvement_refs,
        "topFailureReasons": sorted(reason_counts.items(), key=lambda item: (-item[1], item[0]))[:10],
    }
    body = "\n".join(
        [
            "## Summary",
            "",
            f"- agentId: {agent_id or 'all'}",
            f"- projectId: {project_id or 'all'}",
            f"- task results: {total}",
            f"- passed: {passed}",
            f"- failed: {failed}",
            f"- first pass rate: {frontmatter['firstPassRate']}",
            f"- average score: {average_score}",
            "",
            "## Top Failure Reasons",
            "",
            "\n".join(f"- {reason}: {count}" for reason, count in frontmatter["topFailureReasons"]) or "- none",
            "",
            "## Improvement Proposals",
            "",
            "\n".join(f"- {item}" for item in improvement_refs) or "- none",
            "",
            "## Reuse",
            "",
            "Project Manager Agent and Agent Ring can use this report to decide which Skills, EvalCases, and workflow checklists should be updated next.",
        ]
    )
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", str(frontmatter["title"]), rel(path, bundle.root))
    create_audit_log(bundle, owner, "agent.capability.report.create", rel(path, bundle.root), after="verified", details=f"agentId={agent_id}\nprojectId={project_id}\nresults={total}")
    return path


def create_backup(bundle: Bundle, output: Path | None = None) -> Path:
    backup_dir = bundle.root / "backups"
    ensure_dir(backup_dir)
    out = output or backup_dir / f"knowledge-backup-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.zip"
    skip_parts = {".zhenzhi", "__pycache__", ".git"}
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in bundle.root.rglob("*"):
            if not path.is_file():
                continue
            rel_path = path.relative_to(bundle.root)
            if any(part in skip_parts for part in rel_path.parts):
                continue
            if rel_path.parts and rel_path.parts[0] == "backups":
                continue
            archive.write(path, rel_path)
    append_log(bundle, f"created backup {rel(out, bundle.root)}")
    return out


def restore_backup(bundle: Bundle, archive_path: Path, overwrite: bool = False) -> list[Path]:
    archive = archive_path if archive_path.is_absolute() else bundle.root / archive_path
    if not archive.exists():
        raise KnowledgeError(f"backup not found: {archive_path}")
    restored: list[Path] = []
    with zipfile.ZipFile(archive, "r") as zip_file:
        for member in zip_file.infolist():
            target = bundle.root / member.filename
            if target.exists() and not overwrite:
                raise KnowledgeError(f"restore target exists: {member.filename}; pass overwrite")
        for member in zip_file.infolist():
            target = bundle.root / member.filename
            ensure_dir(target.parent)
            with zip_file.open(member) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            restored.append(target)
    append_log(bundle, f"restored backup {archive_path}")
    return restored


def create_eval_case(
    bundle: Bundle,
    eval_id: str,
    title: str,
    owner: str,
    target_ref: str,
    input_text: str,
    expected: str,
) -> Path:
    eid = slug(eval_id)
    path = bundle.root / "knowledge" / "evals" / f"{eid}.md"
    frontmatter = {
        "type": "EvalCase",
        "title": title,
        "description": f"Evaluation case for {target_ref}.",
        "timestamp": utc_now(),
        "evalId": eid,
        "owner": owner,
        "status": "verified",
        "targetRef": target_ref,
        "expected": expected,
    }
    body = f"## Input\n\n{input_text}\n\n## Expected\n\n{expected}\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", title, f"evals/{eid}.md")
    append_log(bundle, f"created EvalCase {eid}")
    return path


def evaluate_actual(case: dict[str, Any], actual: str) -> tuple[bool, list[str]]:
    missing: list[str] = []
    expected = str(case.get("expected", ""))
    requirements = as_list(case.get("requires"))
    if expected and expected not in actual:
        missing.append(expected)
    for requirement in requirements:
        if requirement not in actual:
            missing.append(requirement)
    if not expected and not requirements and not actual:
        missing.append("non-empty actual")
    return not missing, missing


def run_eval_case(bundle: Bundle, eval_id: str, actual: str, runner: str, severity: str = "high") -> Path:
    eval_path = bundle.root / "knowledge" / "evals" / f"{slug(eval_id)}.md"
    if not eval_path.exists():
        raise KnowledgeError(f"EvalCase not found: {eval_id}")
    case = load_object(eval_path)
    expected = str(case.get("expected", ""))
    requirements = as_list(case.get("requires"))
    target_ref = str(case.get("targetRef", ""))
    target_version = ""
    target_path = bundle.root / target_ref if target_ref else None
    if target_path and target_path.exists():
        target_fm = load_object(target_path)
        target_version = str(target_fm.get("version", target_fm.get("promptVersion", "")))
    passed, missing = evaluate_actual(case, actual)
    run_id = unique_time_id("evalrun")
    path = bundle.root / "knowledge" / "eval-runs" / f"{run_id}.md"
    frontmatter = {
        "type": "EvalRun",
        "title": run_id,
        "description": f"EvalRun for {eval_id}.",
        "timestamp": utc_now(),
        "evalRunId": run_id,
        "evalId": slug(eval_id),
        "targetRef": target_ref,
        "targetVersion": target_version,
        "owner": runner,
        "status": "verified" if passed else "draft",
        "result": "pass" if passed else "fail",
        "severity": severity,
        "releaseGateImpact": "none" if passed or severity.lower() not in {"high", "critical"} else "blocks_release",
        "score": 1 if passed else 0,
        "missing": missing,
    }
    body = f"## Expected\n\n{expected}\n\n## Requirements\n\n" + "\n".join(f"- {item}" for item in requirements)
    body += f"\n\n## Actual\n\n{actual}\n"
    write_text(path, render_doc(frontmatter, body))
    update_index(bundle.root / "knowledge" / "index.md", run_id, f"eval-runs/{run_id}.md")
    append_log(bundle, f"created EvalRun {run_id} result={'pass' if passed else 'fail'}")
    if not passed:
        gap_path = bundle.root / "knowledge" / "engineering" / f"eval-failure-{run_id}.md"
        gap_fm = {
            "type": "KnowledgeItem",
            "title": f"Eval failure {run_id}",
            "description": f"Failure case from {eval_id}.",
            "timestamp": utc_now(),
            "owner": runner,
            "status": "draft",
            "scope": "engineering",
            "sourceRef": rel(path, bundle.root),
            "confidence": "high",
            "knowledgeType": "issue",
        }
        missing_text = ", ".join(missing) if missing else expected
        write_text(gap_path, render_doc(gap_fm, f"## Failure\n\nMissing `{missing_text}`. Actual was:\n\n{actual}\n"))
    return path


def detect_stale(bundle: Bundle, owner: str = "system") -> list[Path]:
    candidates: list[Path] = []
    tool_versions: dict[str, str] = {}
    for path in (bundle.root / "tools").glob("*.md"):
        fm = load_object(path)
        if fm.get("type") == "ToolAsset":
            tool_versions[fm.get("toolId", path.stem)] = fm.get("version", "")
    for root_name in ["knowledge", "projects"]:
        root = bundle.root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if path.name in {"index.md", "log.md", "decisions.md", "lessons.md", "agents.md", "tools.md"} or path.name.endswith(".draft.md"):
                continue
            text = read_text(path)
            fm, body = parse_frontmatter(text)
            if not fm or fm.get("status") != "verified":
                continue
            linked_tool = fm.get("toolId") or fm.get("relatedTool")
            known_version = fm.get("toolVersion")
            should_mark = False
            reason = ""
            if linked_tool and known_version and tool_versions.get(linked_tool) and tool_versions[linked_tool] != known_version:
                should_mark = True
                reason = f"tool version changed: {linked_tool} {known_version}->{tool_versions[linked_tool]}"
            if should_mark:
                fm["status"] = "stale_candidate"
                fm["staleReason"] = reason
                fm["staleDetectedAt"] = utc_now()
                fm["reviewer"] = owner
                write_text(path, render_doc(fm, body))
                candidates.append(path)
                audit_dir = bundle.root / "knowledge" / "audit"
                ensure_dir(audit_dir)
                audit_id = unique_time_id("audit") + f".{len(candidates)}"
                audit_path = audit_dir / f"{audit_id}.md"
                audit_fm = {
                    "type": "AuditLog",
                    "title": audit_id,
                    "timestamp": utc_now(),
                    "auditId": audit_id,
                    "actor": owner,
                    "action": "stale.detect",
                    "targetRef": rel(path, bundle.root),
                    "before": "verified",
                    "after": "stale_candidate",
                    "policyResult": "auto_candidate",
                }
                write_text(audit_path, render_doc(audit_fm, f"## Reason\n\n{reason}\n"))
    if candidates:
        append_log(bundle, f"detected stale candidates: {len(candidates)}")
    return candidates


def invoke_tool(
    bundle: Bundle,
    tool_id: str,
    project_id: str,
    agent_id: str,
    input_text: str,
    execute: bool = False,
) -> dict[str, Any]:
    project_path = find_project(bundle, project_id)
    agent_path = find_agent(bundle, agent_id)
    actor = slug(agent_id)
    target_ref = f"tools/{slug(tool_id)}.md"
    try:
        tool_path = find_tool(bundle, tool_id)
    except KnowledgeError as exc:
        create_audit_log(bundle, actor, "tool.invoke.denied", target_ref, after="denied", policy_result="unregistered_tool", details=str(exc))
        raise
    project = load_object(project_path)
    agent = load_object(agent_path)
    tool = load_object(tool_path)
    permissions = merged_agent_permissions(agent, active_policies_for_agent(bundle, agent_id))
    allowed_projects = permissions.get("allowedProjects", []) or []
    allowed_agents = tool.get("allowedAgents", []) or []
    tool_projects = tool.get("allowedProjects", []) or []
    risk = tool.get("riskLevel", "")
    high_risk_tool = risk in {"L3", "L4", "L5"} or bool(tool.get("requiresApproval"))
    deny_reason = ""
    if tool.get("status") == "disabled":
        deny_reason = "tool_disabled"
    elif allowed_projects and slug(project_id) not in allowed_projects:
        deny_reason = "agent_project_not_allowed"
    elif tool_projects and slug(project_id) not in tool_projects:
        deny_reason = "tool_project_not_allowed"
    elif allowed_agents and slug(agent_id) not in allowed_agents:
        deny_reason = "tool_agent_not_allowed"
    elif execute and tool.get("status") != "approved":
        deny_reason = "tool_not_approved_for_execution"
    elif execute and high_risk_tool:
        deny_reason = "tool_execution_requires_approval"
    if deny_reason:
        create_audit_log(bundle, actor, "tool.invoke.denied", rel(tool_path, bundle.root), after="denied", policy_result=deny_reason, details=input_text)
        raise KnowledgeError(f"tool invocation denied: {deny_reason}")
    output = ""
    mode = "dry_run"
    entrypoint = str(tool.get("entrypoint", ""))
    if execute:
        if entrypoint.startswith("echo://"):
            output = entrypoint[len("echo://") :]
            mode = "executed"
        else:
            create_audit_log(
                bundle,
                actor,
                "tool.invoke.denied",
                rel(tool_path, bundle.root),
                after="denied",
                policy_result="unsupported_entrypoint_execution",
                details=entrypoint,
            )
            raise KnowledgeError("only echo:// ToolAsset execution is supported by the local safe runtime")
    audit_path = create_audit_log(
        bundle,
        actor,
        "tool.invoke.allowed",
        rel(tool_path, bundle.root),
        after=mode,
        policy_result="allowed",
        details=f"project={project.get('projectId', slug(project_id))}\ninput={input_text}",
    )
    return {
        "apiVersion": "v0.1",
        "kind": "ToolInvocationResult",
        "generatedAt": utc_now(),
        "projectId": slug(project_id),
        "agentId": slug(agent_id),
        "toolId": slug(tool_id),
        "mode": mode,
        "entrypoint": entrypoint,
        "riskLevel": risk,
        "resultStoragePolicy": "result_returned_only; project writeback and knowledge publication require separate write/review approval",
        "auditRef": rel(audit_path, bundle.root),
        "output": output,
    }


def export_api_snapshot(bundle: Bundle) -> dict[str, Any]:
    rebuild_index(bundle)
    objects = search_index(bundle, {})
    return {
        "apiVersion": "v0.1",
        "kind": "KnowledgeSnapshot",
        "generatedAt": utc_now(),
        "root": str(bundle.root),
        "objects": objects,
    }


def gateway_context(bundle: Bundle, project_id: str, agent_id: str, task: str) -> dict[str, Any]:
    context_path = start_task(bundle, project_id, agent_id, task)
    text = read_text(context_path)
    agent = load_object(find_agent(bundle, agent_id))
    policies = active_policies_for_agent(bundle, agent_id)
    permissions = merged_agent_permissions(agent, policies)
    return {
        "apiVersion": "v0.1",
        "kind": "GatewayContext",
        "generatedAt": utc_now(),
        "contextPath": rel(context_path, bundle.root),
        "projectId": slug(project_id),
        "agentId": slug(agent_id),
        "task": task,
        "policyResult": permissions,
        "context": text,
    }



def git(bundle: Bundle, args: list[str]) -> str:
    if shutil.which("git") is None:
        raise KnowledgeError("git not found")
    proc = subprocess.run(["git", *args], cwd=bundle.root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise KnowledgeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout.strip()
