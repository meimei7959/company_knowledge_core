---
type: ProjectTask
title: AI Native OS test - scheduler, runner, and result flow
description: Validate Scheduler, Runner, Agent Worker, PM Autopilot, TaskResult, approval relay, and stale lease repair implementation.
timestamp: "2026-06-21T07:18:00Z"
taskId: kt-ai-native-os-test-scheduler-runner-result
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"test","requiredCapabilities":["testing","scheduler","agent_worker","task_result_validation"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result.md","task-results/tr-kt-ai-native-os-impl-scheduler-runner-result.md","projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_and_product_review","reviewPath":"test_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - testing
  - scheduler
  - agent_worker
  - task_result_validation
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test
requirementRefs:
  - ANOS-REQ-050
  - ANOS-REQ-051
  - ANOS-REQ-052
  - ANOS-REQ-053
  - ANOS-REQ-054
  - ANOS-REQ-055
  - ANOS-REQ-056
  - ANOS-REQ-060
  - ANOS-REQ-061
  - ANOS-REQ-062
  - ANOS-REQ-063
  - ANOS-REQ-070
  - ANOS-REQ-071
  - ANOS-REQ-072
  - ANOS-REQ-073
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-impl-scheduler-runner-result.md
  - projects/company-knowledge-core/technical-solutions/ai-native-os-scheduler-runner-result.md
expectedOutput:
  - Test Agent validates scheduler dispatch, claim, lease, approval relay, stale repair, worker run, and workbench read model behavior.
  - Test Agent verifies TaskResult metadata and closed-loop state transitions.
  - Any failure must be returned to Development Agent through a repair task.
updatedAt: "2026-06-21T08:12:51Z"
assignedRunner: runner.meimei-mac-local-test-1
leaseOwner: runner.meimei-mac-local-test-1
leaseTokenHash: ed60cd47d810819151929d22e1913d329b332723c1af29b5c6d08ccc8b98e961
leaseProofHash: ed60cd47d810819151929d22e1913d329b332723c1af29b5c6d08ccc8b98e961
leaseIssuedAt: "2026-06-21T07:50:30Z"
leaseExpiresAt: "2026-06-21T08:20:30Z"
leaseHeartbeatAt: "2026-06-21T07:50:30Z"
heartbeatAt: "2026-06-21T07:50:30Z"
leaseVersion: 4
leaseAttempt: 3
taskVersion: 4
notificationRefs:
  - notifications/notification.20260621T071855553707Z.md
  - notifications/notification.20260621T074504826039Z.md
  - notifications/notification.20260621T075030144524Z.md
  - notifications/notification.20260621T075051230279Z.md
  - notifications/notification.20260621T075051231691Z.md
  - notifications/notification.20260621T075051232427Z.md
  - notifications/notification.20260621T081251846269Z.md
resultRef: task-results/tr-kt-ai-native-os-test-scheduler-runner-result.md
completedAt: "2026-06-21T07:50:51Z"
---

# Test Scope

Validate the automatic execution loop and TaskResult writeback path without changing implementation files.

# Required Checks

- Run scheduler/runner/result focused tests.
- Exercise `scheduler autopilot` dry-run and claim behavior.
- Confirm approval requests are surfaced in TaskResult data for PM relay.
- Confirm failed checks produce actionable evidence for Development Agent repair.
