---
type: ProjectTask
title: AI Native Agent V1 Closed-Loop Acceptance Test
description: Test Agent verification of the PRD-defined V1 single-machine Agent collaboration loop.
timestamp: "2026-06-22T00:00:00+08:00"
taskId: kt-ai-native-agent-v1-test-closed-loop-acceptance
taskType: test
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
currentStage: testing
technicalSolutionRequired: false
requiredCapabilities:
  - testing
  - quality_gate
  - requirement_traceability
requiredAgents:
  - agent.company.test
preferredRunner: runner.meimei-mac-local-test-1
assignedRunner: runner.meimei-mac-local-test-1
executorAgent: agent.company.test
leaseOwner: runner.meimei-mac-local-test-1
leaseExpiresAt: "2026-06-22T03:31:27Z"
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/ai-native-agent-v1-single-machine-upgrade-plan.md
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-dev-implementation.md
expectedOutput:
  - acceptance test report
  - failure repair tasks if any test fails
  - evidence refs
resultRef: task-results/tr-kt-ai-native-agent-v1-test-closed-loop-acceptance.md
notificationRefs:
  - notifications/notification.20260622T032055304053Z.md
  - notifications/notification.20260622T032127214408Z.md
  - notifications/notification.20260622T032127218138Z.md
  - notifications/notification.20260622T032127219073Z.md
  - notifications/notification.20260622T032127219884Z.md
  - notifications/notification.20260622T032135275362Z.md
auditRefs:
  - knowledge/audit/audit.20260622T000000-ai-native-agent-v1-upgrade-plan.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"project","stage":"testing","requiredCapabilities":["test","testing","quality_gate","requirement_traceability"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/ai-native-agent-v1-single-machine-upgrade-plan.md","projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-dev-implementation.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-22T03:21:35Z"
leaseTokenHash: cd209ab24d271c6eb21de05efaa762be92d0dd358037717af484464b4360c0e7
leaseProofHash: cd209ab24d271c6eb21de05efaa762be92d0dd358037717af484464b4360c0e7
leaseHeartbeatAt: "2026-06-22T03:21:27Z"
heartbeatAt: "2026-06-22T03:21:27Z"
taskVersion: 3
retryRequestedAt: "2026-06-22T03:20:55Z"
retryRequestedBy: agent.company.project-manager
retryReason: development-implementation-accepted-release-test-agent-closed-loop
retryHistory:
  - {"fromStatus":"blocked","reason":"development-implementation-accepted-release-test-agent-closed-loop","actor":"agent.company.project-manager","previousRunnerId":"","at":"2026-06-22T03:20:55Z"}
failureReasons:
  - development-implementation-accepted-release-test-agent-closed-loop
attemptNumber: 2
nextAction: Runner should claim the retry lease and write back fresh evidence.
leaseIssuedAt: "2026-06-22T03:21:27Z"
leaseVersion: 3
leaseAttempt: 1
completedAt: "2026-06-22T03:21:27Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-test-closed-loop-acceptance-handoff.md
---

## Request

Verify the PRD-defined V1 single-machine closed-loop scenario as Test Agent.

## Expected Output

- Evidence that Group/Product/Development/Test sessions register to Local Router.
- Evidence that Group Agent dispatches Task Package and receives result.
- Evidence that Development Agent uses isolated worktree.
- Evidence that Test Agent returns pass/fail report.
- Evidence that failed tests create Development repair tasks.
- Evidence that high-risk actions require human confirmation.
- Final PASS/BLOCK verdict.

## Blocking Condition

Blocked until Development Agent submits implementation TaskResult.
