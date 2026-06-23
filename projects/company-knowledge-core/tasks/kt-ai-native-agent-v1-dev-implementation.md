---
type: ProjectTask
title: AI Native Agent V1 Development Implementation
description: Development Agent implementation of the Product-approved V1 single-machine closed-loop runtime.
timestamp: "2026-06-22T00:00:00+08:00"
taskId: kt-ai-native-agent-v1-dev-implementation
taskType: implementation
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
currentStage: implementation
technicalSolutionRequired: false
requiredCapabilities:
  - development
  - scheduler
  - agent_worker
  - workbench
requiredAgents:
  - agent.company.development
preferredRunner: runner.meimei-mac-local-dev-rt
assignedRunner: runner.meimei-mac-local-dev-rt
executorAgent: agent.company.development
leaseOwner: runner.meimei-mac-local-dev-rt
leaseExpiresAt: "2026-06-22T03:30:25Z"
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/ai-native-agent-v1-single-machine-upgrade-plan.md
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-review-technical-solutions.md
expectedOutput:
  - implemented V1 runtime path
  - tests
  - TaskResult with evidence refs
resultRef: task-results/tr-kt-ai-native-agent-v1-dev-implementation.md
notificationRefs:
  - notifications/notification.20260622T030500937030Z.md
  - notifications/notification.20260622T031955971648Z.md
  - notifications/notification.20260622T032018966301Z.md
  - notifications/notification.20260622T032025187121Z.md
  - notifications/notification.20260622T032025191344Z.md
  - notifications/notification.20260622T032025192275Z.md
  - notifications/notification.20260622T032025193150Z.md
  - notifications/notification.20260622T032032301863Z.md
auditRefs:
  - knowledge/audit/audit.20260622T000000-ai-native-agent-v1-upgrade-plan.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"engineering","stage":"implementation","requiredCapabilities":["implementation","development","scheduler","agent_worker","workbench"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/ai-native-agent-v1-single-machine-upgrade-plan.md","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-review-technical-solutions.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
updatedAt: "2026-06-22T03:20:32Z"
leaseTokenHash: bc63137f7a5b4f14481fbc9a0861ce80f81a6581b0ece7049a86d6d35a0336ae
leaseProofHash: bc63137f7a5b4f14481fbc9a0861ce80f81a6581b0ece7049a86d6d35a0336ae
leaseHeartbeatAt: "2026-06-22T03:20:25Z"
heartbeatAt: "2026-06-22T03:20:25Z"
taskVersion: 4
retryRequestedAt: "2026-06-22T03:20:18Z"
retryRequestedBy: agent.company.project-manager
retryReason: dev-runner-implementation-capability-added
retryHistory:
  - {"fromStatus":"blocked","reason":"product-reviewed-technical-solutions-release-implementation","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T03:05:00Z"}
  - {"fromStatus":"blocked","reason":"dev-runner-implementation-capability-added","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T03:20:18Z"}
failureReasons:
  - product-reviewed-technical-solutions-release-implementation
  - dev-runner-implementation-capability-added
attemptNumber: 3
nextAction: Runner should claim the retry lease and write back fresh evidence.
leaseIssuedAt: "2026-06-22T03:20:25Z"
leaseVersion: 4
leaseAttempt: 1
completedAt: "2026-06-22T03:20:25Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-dev-implementation-handoff.md
---

## Request

Implement the V1 runtime only after Product Manager Agent accepts the technical solution package.

## Expected Output

- Agent Profile Service and Skill Registry.
- Session Registry and Local Router.
- TaskPackage and AgentMessage model/API/CLI.
- Agent Runtime worker.
- Group Agent Orchestrator dispatch/result loop.
- Minimal Worktree Manager.
- Console/read model upgrade.
- Tests for the V1 loop.

## Blocking Condition

Blocked until `kt-ai-native-agent-v1-product-review-technical-solutions` passes.
