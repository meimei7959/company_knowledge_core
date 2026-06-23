---
type: ProjectTask
title: AI Native OS RT test regression - object model repair
description: Test Agent reruns independent regression after Development Agent repaired object model validation blockers.
timestamp: "2026-06-21T10:15:09Z"
taskId: kt-ai-native-os-rt-test-object-model-slice-regression
taskType: test
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test","category":"engineering","stage":"regression","requiredCapabilities":["testing","requirement_traceability","quality_gate"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-ai-native-os-rt-dev-object-model-slice-repair.md","task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md","tests/test_requirement_tree_object_model.py","zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"test_regression_then_pm_review","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: done
priority: critical
dueAt: ""
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-rt-dev-object-model-slice-repair.md
  - task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md
  - tests/test_requirement_tree_object_model.py
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
expectedOutput:
  - Regression test the two repaired Requirement Tree object model blockers.
  - Verify full object model test suite and repository validation pass.
  - Confirm no forbidden slice expansion was introduced.
  - Return pass/fail to Project Manager Agent for acceptance or Development Agent for another repair.
resultRef: task-results/tr-kt-ai-native-os-rt-test-object-model-slice-regression.md
notificationRefs:
  - notifications/notification.20260621T101509818676Z.md
  - notifications/notification.20260621T101809283779Z.md
  - notifications/notification.20260621T101809284538Z.md
  - notifications/notification.20260621T101809285126Z.md
  - notifications/notification.20260621T101904673427Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.test
leaseOwner: ""
leaseTokenHash: ""
leaseProofHash: ""
leaseIssuedAt: ""
leaseExpiresAt: ""
leaseHeartbeatAt: ""
leaseVersion: 1
leaseAttempt: 0
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"","to":"","requiredArtifacts":["summary","evidence refs","next action or terminal reason"]}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-test-object-model-slice-regression-handoff.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-21T10:19:04Z"
startedAt: "2026-06-21T10:15:49Z"
completedAt: "2026-06-21T10:18:09Z"
---

## Request

AI Native OS RT test regression - object model repair

## Source Materials

- task-results/tr-kt-ai-native-os-rt-dev-object-model-slice-repair.md
- task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md
- tests/test_requirement_tree_object_model.py

## Expected Output

- Regression test the two repaired Requirement Tree object model blockers.
- Verify full object model test suite and repository validation pass.
- Confirm no forbidden slice expansion was introduced.
- Return pass/fail to Project Manager Agent for acceptance or Development Agent for another repair.

## Regression Scope

- Verify ghost local refs such as `PREQ-999` fail unless the referenced local object exists.
- Verify accepted RequirementTree records fail when high or critical blockers remain.
- Verify original positive object model path still passes.
- Verify implementation did not expand into importer, compiler, context pack, workbench, historical backfill, or ProjectTask queue generation.

## Role Boundary

Test Agent must not modify implementation. If regression fails, produce a failed TaskResult and route back to Development Agent.

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: current assignee
- to: terminal or project manager decision
- requiredArtifacts:
  - summary
  - evidence refs
  - next action or terminal reason

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
