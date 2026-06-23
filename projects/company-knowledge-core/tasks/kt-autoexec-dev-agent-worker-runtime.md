---
type: ProjectTask
title: Auto execution Agent Worker runtime
description: Implement a local Agent Worker command that claims matching tasks and writes TaskResult output for executable stages.
timestamp: "2026-06-21T05:53:52Z"
taskId: kt-autoexec-dev-agent-worker-runtime
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"implementation","requiredCapabilities":["development","agent_worker","task_result_writeback","local_runner_execution"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md","projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
requiredCapabilities:
  - agent_worker
  - task_result_writeback
  - local_runner_execution
requiredAgents:
  - agent.company.development
executorAgent: agent.company.development
status: done
priority: critical
currentStage: implementation
sourceMaterialRefs:
  - projects/company-knowledge-core/coordination/auto-execution-system-delivery-plan.md
  - projects/company-knowledge-core/coordination/ai-native-os-development-stage-control.md
expectedOutput:
  - Worker function and CLI for project, agent, runner, limit, and lease settings.
  - Worker claim and execution path for technical_solution tasks.
  - TaskResult writeback with executorAgent, runner, requirementRefs, evidenceRefs, nextActions, and openRisks.
  - TaskResult with implementation evidence and tests/checks run.
acceptanceCriteria:
  - Development worker can claim a technical solution task and move it beyond processing by writing TaskResult.
  - Worker does not claim tasks for the wrong Agent.
  - Worker does not claim completion of implementation when it only produced a technical solution.
assignedRunner: runner.meimei-mac-local-codex
updatedAt: "2026-06-21T07:18:05Z"
notificationRefs:
  - notifications/notification.20260621T055554618022Z.md
  - notifications/notification.20260621T055613430499Z.md
  - notifications/notification.20260621T061307730265Z.md
  - notifications/notification.20260621T061307731014Z.md
  - notifications/notification.20260621T061307731834Z.md
  - notifications/notification.20260621T061422548373Z.md
resultRef: task-results/tr-kt-autoexec-dev-agent-worker-runtime.md
completedAt: "2026-06-21T06:13:07Z"
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-autoexec-dev-agent-worker-runtime-handoff.md
---

# Auto Execution Agent Worker Runtime

## PM Instruction

Implement the missing execution bridge after claim.

## Done Means

`claim` becomes the start of executable Agent work, not a terminal state.
