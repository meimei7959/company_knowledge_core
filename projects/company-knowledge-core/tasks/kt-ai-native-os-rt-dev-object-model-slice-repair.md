---
type: ProjectTask
title: AI Native OS RT development repair - object model slice
description: Development Agent repairs the object model slice defects found by Test Agent without expanding the slice scope.
timestamp: "2026-06-21T10:11:12Z"
taskId: kt-ai-native-os-rt-dev-object-model-slice-repair
taskType: development
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"development","category":"engineering","stage":"repair","requiredCapabilities":["development","requirement_traceability","schema_migration"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md","tests/test_requirement_tree_object_model.py","zhenzhi_knowledge/core.py","zhenzhi_knowledge/cli.py","task-results/tr-kt-ai-native-os-rt-dev-object-model-slice.md"],"repositoryRefs":["/Users/meimei/Documents/company_knowledge_core"],"dataScopes":["local_repo"],"qualityGate":"engineering","acceptancePath":"test_then_pm_review","reviewPath":"development_repair_then_test_regression","riskLevel":"high","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: done
priority: critical
dueAt: ""
sourceMaterialRefs:
  - task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md
  - tests/test_requirement_tree_object_model.py
  - task-results/tr-kt-ai-native-os-rt-dev-object-model-slice.md
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
expectedOutput:
  - Fix unresolved local ref validation for RequirementMapping.
  - Fix accepted RequirementTree high/critical blocker severity validation.
  - Keep importer/compiler/context pack/workbench/backfill out of scope.
  - Rerun object model tests and repository validate, then hand off to Test Agent for regression.
resultRef: task-results/tr-kt-ai-native-os-rt-dev-object-model-slice-repair.md
notificationRefs:
  - notifications/notification.20260621T101112049596Z.md
  - notifications/notification.20260621T101433309111Z.md
  - notifications/notification.20260621T101433309998Z.md
  - notifications/notification.20260621T101433310832Z.md
  - notifications/notification.20260621T101904553294Z.md
auditRefs: []
assignedRunner: ""
executorAgent: agent.company.development
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
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["technical plan","change summary","self-test result","risk notes"]}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-os-rt-dev-object-model-slice-repair-handoff.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-21T10:19:04Z"
startedAt: "2026-06-21T10:11:55Z"
completedAt: "2026-06-21T10:14:33Z"
---

## Request

AI Native OS RT development repair - object model slice

## Source Materials

- task-results/tr-kt-ai-native-os-rt-test-object-model-slice.md
- tests/test_requirement_tree_object_model.py

## Expected Output

- Fix unresolved local ref validation for RequirementMapping.
- Fix accepted RequirementTree high/critical blocker severity validation.
- Keep importer/compiler/context pack/workbench/backfill out of scope.
- Rerun object model tests and repository validate, then hand off to Test Agent for regression.

## Test Agent Blockers

- `RequirementMapping` currently accepts ghost local refs such as `PREQ-999` when the ref shape is valid but no local requirement node, gate, or snapshot exists.
- Accepted `RequirementTree` currently misses high/critical blockers because blocker dictionaries are converted to strings before severity inspection.

## Scope Boundary

- Repair only object model validation behavior and matching tests.
- Do not implement importer, compiler, context pack, workbench, historical backfill, or ProjectTask queue generation.
- Do not change Product Manager Agent review verdict.
- Do not weaken Test Agent assertions to make tests pass.

## Regression Gate

- `python3 -m unittest tests.test_requirement_tree_object_model` must pass.
- `python3 -m unittest discover -s tests` must pass or any unrelated failure must be explicitly proven unrelated.
- `python3 -m zhenzhi_knowledge requirement tree validate` must pass.
- `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` must pass.

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.development
- to: agent.company.test
- requiredArtifacts:
  - technical plan
  - change summary
  - self-test result
  - risk notes

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.
