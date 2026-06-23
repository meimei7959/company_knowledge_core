---
type: ProjectTask
title: Auto execution workbench data API
description: Expose the data needed for a workbench to show Agent activity, PM decisions, blockers, stale work, and requirement coverage.
timestamp: "2026-06-21T05:53:52Z"
taskId: kt-autoexec-dev-workbench-data-api
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","api_gateway","project_console","scheduler_visibility"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - api_gateway
  - project_console
  - scheduler_visibility
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: done
priority: high
currentStage: implementation
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
expectedOutput:
  - Workbench-readable status object or API for Agent activity and task lifecycle.
  - Coverage and evidence gaps for requirements.
  - PM Autopilot decision history.
  - TaskResult with implementation evidence and tests/checks run.
acceptanceCriteria:
  - Workbench can distinguish waiting, claimed, running, stale, blocked, result_submitted, and accepted work.
  - Workbench can show which Agent is doing what now.
  - Workbench can show missing evidence and PM next action.
assignedRunner: runner.meimei-mac-local-codex
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T055613433675Z.md
  - notifications/notification.20260621T061307802197Z.md
  - notifications/notification.20260621T061307802970Z.md
  - notifications/notification.20260621T061307803605Z.md
  - notifications/notification.20260621T061422562511Z.md
resultRef: task-results/tr-kt-autoexec-dev-workbench-data-api.md
completedAt: "2026-06-21T06:13:07Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-autoexec-dev-workbench-data-api-handoff.md
---

# Auto Execution Workbench Data API

## PM Instruction

Expose visibility after the execution engine works. Do not treat UI visibility as a substitute for execution.
