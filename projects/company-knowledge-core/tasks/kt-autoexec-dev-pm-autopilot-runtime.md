---
type: ProjectTask
title: Auto execution PM Autopilot runtime
description: Implement finite Project Manager Autopilot cycles so scheduling is not only manual scheduler tick.
timestamp: "2026-06-21T05:53:52Z"
taskId: kt-autoexec-dev-pm-autopilot-runtime
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","scheduler","project_management_automation","task_lifecycle"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md","docs/scheduler/task-dispatch-model.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - scheduler
  - project_management_automation
  - task_lifecycle
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: done
priority: critical
currentStage: implementation
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
  - docs/scheduler/task-dispatch-model.md
expectedOutput:
  - PM Autopilot function and CLI with finite cycles.
  - Priority and stage-aware scheduling order.
  - Decision summary with claimed, waiting, blocked, and skipped work.
  - TaskResult with implementation evidence and tests/checks run.
acceptanceCriteria:
  - High-priority development technical solution tasks are selected before medium design tasks.
  - Autopilot does not run forever by default.
  - Autopilot output is usable by workbench and PM status.
assignedRunner: runner.meimei-mac-local-codex
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T055554619187Z.md
  - notifications/notification.20260621T055613431707Z.md
  - notifications/notification.20260621T061251990517Z.md
  - notifications/notification.20260621T061251991292Z.md
  - notifications/notification.20260621T061251992131Z.md
  - notifications/notification.20260621T061408297339Z.md
resultRef: task-results/tr-kt-autoexec-dev-pm-autopilot-runtime.md
completedAt: "2026-06-21T06:12:51Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-autoexec-dev-pm-autopilot-runtime-handoff.md
---

# Auto Execution PM Autopilot Runtime

## PM Instruction

Implement the runtime layer that lets Project Manager Agent continuously advance work in bounded cycles.

## Done Means

Manual `scheduler tick` is no longer the only way to move the project forward.
