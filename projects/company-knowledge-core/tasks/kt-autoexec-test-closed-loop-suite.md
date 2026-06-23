---
type: ProjectTask
title: Auto execution closed loop test suite
description: Test the minimum automatic execution loop from PM Autopilot through Agent Worker TaskResult writeback and PM acceptance readiness.
timestamp: "2026-06-21T05:53:52Z"
taskId: kt-autoexec-test-closed-loop-suite
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"project","stage":"test_design","requiredCapabilities":["test","test_planning","regression_gate","task_lifecycle_testing"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - test_planning
  - regression_gate
  - task_lifecycle_testing
requiredAgents:
  - agent.company.test
executorAgent: agent.company.test
status: done
priority: critical
currentStage: test_design
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
expectedOutput:
  - Tests for priority scheduling.
  - Tests for PM Autopilot finite-cycle behavior.
  - Tests for Agent Worker technical solution TaskResult writeback.
  - Tests for TaskResult evidence and next-step readiness.
  - Launch blocker report.
acceptanceCriteria:
  - A failing closed-loop behavior fails the test suite.
  - Tests prove the system does not merely create tasks.
  - Tests prove the flow moves beyond processing.
assignedRunner: runner.meimei-mac-local-codex
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T055613435512Z.md
  - notifications/notification.20260621T061317803984Z.md
  - notifications/notification.20260621T061317804704Z.md
  - notifications/notification.20260621T061317805433Z.md
  - notifications/notification.20260621T061422588148Z.md
resultRef: task-results/tr-kt-autoexec-test-closed-loop-suite.md
completedAt: "2026-06-21T06:13:17Z"
---

# Auto Execution Closed Loop Test Suite

## Test Agent Instruction

Prove the loop works. If it only assigns or claims tasks and then stops, fail it.
