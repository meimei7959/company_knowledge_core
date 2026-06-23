---
type: ProjectTask
title: AI Native Agent V1 Technical Solution - Local Router And Session Registry
description: Development Agent technical solution for single-machine Agent session registration, heartbeat, message routing, and failure detection.
timestamp: "2026-06-22T00:00:00+08:00"
taskId: kt-ai-native-agent-v1-tech-local-router-session-registry
taskType: technical_solution
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
currentStage: technical_solution
technicalSolutionRequired: true
requiredCapabilities:
  - development
  - scheduler_design
requiredAgents:
  - agent.company.development
preferredRunner: runner.meimei-mac-local-dev-rt
assignedRunner: runner.meimei-mac-local-dev-rt
executorAgent: agent.company.development
leaseOwner: runner.meimei-mac-local-dev-rt
leaseExpiresAt: "2026-06-22T03:13:38Z"
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx
  - /Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md
  - docs/scheduler/task-dispatch-model.md
  - scripts/distributed_runner_proof_harness.py
expectedOutput:
  - technical solution document
  - Local Router API/CLI proposal
  - Session Registry data model
  - failure and stale-session handling rules
resultRef: task-results/tr-kt-ai-native-agent-v1-tech-local-router-session-registry.md
notificationRefs:
  - notifications/notification.20260622T030302539274Z.md
  - notifications/notification.20260622T030338352321Z.md
  - notifications/notification.20260622T030338356398Z.md
  - notifications/notification.20260622T030338357429Z.md
  - notifications/notification.20260622T030338358273Z.md
  - notifications/notification.20260622T030359204371Z.md
auditRefs:
  - knowledge/audit/audit.20260622T000000-ai-native-agent-v1-upgrade-plan.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"technical_solution","requiredCapabilities":["technical_solution","development","scheduler_design"],"requiredTools":[],"sourceRefs":["/Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx","/Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md","docs/scheduler/task-dispatch-model.md","scripts/distributed_runner_proof_harness.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-22T03:03:59Z"
leaseTokenHash: d048bbb82757b4999b887e3ba1e0a9c70143ac8666e1d3e389c3110a5e1f4902
leaseProofHash: d048bbb82757b4999b887e3ba1e0a9c70143ac8666e1d3e389c3110a5e1f4902
leaseHeartbeatAt: "2026-06-22T03:03:38Z"
heartbeatAt: "2026-06-22T03:03:38Z"
taskVersion: 3
retryRequestedAt: "2026-06-22T03:03:02Z"
retryRequestedBy: agent.company.project-manager
retryReason: product-scope-accepted-release-development-technical-solution
retryHistory:
  - {"fromStatus":"blocked","reason":"product-scope-accepted-release-development-technical-solution","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T03:03:02Z"}
failureReasons:
  - product-scope-accepted-release-development-technical-solution
attemptNumber: 2
nextAction: Runner should claim the retry lease and write back fresh evidence.
leaseIssuedAt: "2026-06-22T03:03:38Z"
leaseVersion: 3
leaseAttempt: 1
completedAt: "2026-06-22T03:03:38Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-local-router-session-registry-handoff.md
---

## Request

Produce the technical solution for Local Router and Session Registry.

## Expected Output

- Session register/heartbeat/list/unregister flow.
- AgentMessage send/receive/status/result routing flow.
- Local-only routing guarantees for V1.
- Stale session, blocked approval, token exhaustion, and retry handling.
- Tests that prove at least Group/Product/Development/Test sessions can register and exchange messages.

## Handling Notes

Blocked until Product Manager Agent completes V1 requirement structuring and scope review. Do not use Codex subagents as proof of V1 routing. V1 evidence must come from formal session registration and message routing.
