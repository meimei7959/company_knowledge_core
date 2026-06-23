---
type: ProjectTask
title: AI Native OS development - automation hub hard capabilities
description: "Implement the four missing automation hub capabilities found in PM retrospective: execution context transfer, exception recovery, supervision workbench, and environment readiness."
timestamp: "2026-06-21T08:25:00Z"
taskId: kt-ai-native-os-dev-automation-hub-hard-capabilities
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","scheduler","agent_worker","task_result_writeback","approval_relay","environment_readiness","workbench"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md","knowledge/audit/audit.20260621T081300Z-ai-native-os-pm-74-requirement-execution-closeout.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"development_then_test","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":true,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - development
  - scheduler
  - agent_worker
  - task_result_writeback
  - approval_relay
  - environment_readiness
  - workbench
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: done
priority: critical
currentStage: implementation
requirementRefs:
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-054
  - ANOS-REQ-055
  - ANOS-REQ-056
  - ANOS-REQ-070
  - ANOS-REQ-071
  - ANOS-REQ-072
  - ANOS-REQ-073
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/ai-native-os-agent-execution-governance.md
  - knowledge/audit/audit.20260621T081300Z-ai-native-os-pm-74-requirement-execution-closeout.md
expectedOutput:
  - Execution context transfer: scheduler claim output gives the executing Agent a usable context reference and writeback command without storing clear lease tokens in reusable knowledge.
  - Exception recovery: stale lease, token/context pause, subagent heartbeat timeout, and approval relay states are visible and recoverable.
  - Supervision workbench: read model exposes selected task, runners, execution context readiness, approval blockers, environment readiness, lease health, retry/repair path, and PM decision log.
  - Environment readiness: required secrets, repositories, tools, database variables, runner capabilities, and project scopes are checked before claim and represented as actionable blockers.
  - Regression tests prove the four capabilities and prevent heartbeat capability overwrite.
  - TaskResult records changed files, checks, risks, blockers, next action, and approval request if any.
assignedRunner: runner.meimei-mac-local-dev-hub
leaseOwner: runner.meimei-mac-local-dev-hub
leaseTokenHash: bbdd2385ca88db8dd4dd8ff56147e47697b8bd2e2a8e722bafa62f168ab7044b
leaseProofHash: bbdd2385ca88db8dd4dd8ff56147e47697b8bd2e2a8e722bafa62f168ab7044b
leaseIssuedAt: "2026-06-21T08:24:12Z"
leaseExpiresAt: "2026-06-21T09:24:12Z"
leaseHeartbeatAt: "2026-06-21T08:24:12Z"
heartbeatAt: "2026-06-21T08:24:12Z"
leaseVersion: 3
leaseAttempt: 2
taskVersion: 3
updatedAt: "2026-06-21T08:48:47Z"
notificationRefs:
  - notifications/notification.20260621T082354888401Z.md
  - notifications/notification.20260621T082412269512Z.md
  - notifications/notification.20260621T083715591495Z.md
  - notifications/notification.20260621T083715593822Z.md
  - notifications/notification.20260621T083715594561Z.md
  - notifications/notification.20260621T084737536201Z.md
resultRef: task-results/tr-kt-ai-native-os-dev-automation-hub-hard-capabilities.md
completedAt: "2026-06-21T08:37:15Z"
improvementRefs:
  - knowledge/agent-improvements/agent-improvement.20260621T083715592852Z.md
followupTaskRefs: []
---

# PM Problem Statement

This task fixes the four hard gaps identified by the Project Manager Agent retrospective:

1. Execution context transfer.
2. Exception recovery.
3. Visual supervision data.
4. Environment readiness.

# Engineering Boundaries

- Do not implement this in the PM thread.
- Do not weaken lease security; clear lease tokens may appear only in runtime execution context returned to the runner or stored under `.zhenzhi/`, not reusable knowledge files.
- Do not let runner heartbeat overwrite existing capabilities unless an explicit replacement mode exists.
- Do not hide external blockers. If PostgreSQL or another environment dependency is missing, expose a readiness blocker and next action.
- Do not mark full Desktop runtime done; this task covers automation hub data/control flow only.

# Required Tests

- Scheduler claim returns execution context data usable by a worker.
- Task context payload includes writeback command with runner and lease token when called by the owning runner.
- Workbench read model exposes execution context, approval relay, recovery status, and environment readiness.
- Runner heartbeat merges capabilities instead of deleting previous capabilities.
- Missing environment variables or secret refs block claim with actionable reason.
- Full `python3 -m unittest discover -s tests` passes.
- Full `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` passes.
