---
type: ProjectTask
title: AI Native Agent V1 Technical Solution - Worktree Console And Acceptance Harness
description: Development Agent technical solution for minimal Worktree Manager, V1 status console, and acceptance harness integration.
timestamp: "2026-06-22T00:00:00+08:00"
taskId: kt-ai-native-agent-v1-tech-worktree-console-harness
taskType: technical_solution
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
currentStage: technical_solution
technicalSolutionRequired: true
requiredCapabilities:
  - development
  - workbench
  - agent_worker
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
  - projects/company-knowledge-core/desktop-workbench-slice0/
  - tests/test_desktop_workbench_slice0.py
expectedOutput:
  - technical solution document
  - Worktree Manager minimal V1 API
  - Console/read-model upgrade plan
  - acceptance harness design
resultRef: task-results/tr-kt-ai-native-agent-v1-tech-worktree-console-harness.md
notificationRefs:
  - notifications/notification.20260622T030313256414Z.md
  - notifications/notification.20260622T030338369759Z.md
  - notifications/notification.20260622T030338373154Z.md
  - notifications/notification.20260622T030338374108Z.md
  - notifications/notification.20260622T030338374935Z.md
  - notifications/notification.20260622T030414285091Z.md
auditRefs:
  - knowledge/audit/audit.20260622T000000-ai-native-agent-v1-upgrade-plan.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"technical_solution","requiredCapabilities":["technical_solution","development","workbench","agent_worker"],"requiredTools":[],"sourceRefs":["/Users/meimei/Downloads/AI_Native_Agent协同系统_PRD_V1.0.docx","/Users/meimei/Downloads/AI_Native_Agent协同系统_技术方案_V1.0.docx","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md","projects/company-knowledge-core/desktop-workbench-slice0/","tests/test_desktop_workbench_slice0.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-22T03:04:14Z"
leaseTokenHash: a2413ac48c7399d5b0fd5b141f044bb9ed45b0e1c3def6ef208b674d4fdb98cf
leaseProofHash: a2413ac48c7399d5b0fd5b141f044bb9ed45b0e1c3def6ef208b674d4fdb98cf
leaseHeartbeatAt: "2026-06-22T03:03:38Z"
heartbeatAt: "2026-06-22T03:03:38Z"
taskVersion: 3
retryRequestedAt: "2026-06-22T03:03:13Z"
retryRequestedBy: agent.company.project-manager
retryReason: product-scope-accepted-release-development-technical-solution
retryHistory:
  - {"fromStatus":"blocked","reason":"product-scope-accepted-release-development-technical-solution","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T03:03:13Z"}
failureReasons:
  - product-scope-accepted-release-development-technical-solution
attemptNumber: 2
nextAction: Runner should claim the retry lease and write back fresh evidence.
leaseIssuedAt: "2026-06-22T03:03:38Z"
leaseVersion: 3
leaseAttempt: 1
completedAt: "2026-06-22T03:03:38Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-worktree-console-harness-handoff.md
---

## Request

Produce the technical solution for the V1 worktree, console, and acceptance harness slice.

## Expected Output

- Worktree allocation/binding/status/release model.
- Console read model for sessions, messages, task graph, worktrees, approvals, stale leases, and blocked prompts.
- Acceptance harness that proves the PRD V1 scenario end to end.
- Test plan for failed-test-to-development-repair routing.

## Handling Notes

Blocked until Product Manager Agent completes V1 requirement structuring and scope review. The console is supervision and intervention surface, not the execution engine.
