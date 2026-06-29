---
type: ProjectTask
title: Task Title
description: Work scheduled to an Agent Ring runner.
timestamp: 2026-06-18T00:00:00Z
taskId: KT-YYYYMMDD-001
taskType: knowledge_capture
projectId: project-id
workSourceType: feature
requirementRefs: []
requirementObjectRefs: []
acceptanceCriteriaRefs: []
defectRefs: []
defectObjectRefs: []
incidentRefs: []
operationRefs: []
knowledgeTaskRefs: []
researchQuestion:
sourceReason:
receiverReviewRefs: []
requester: requester
requiredCapabilities: []
requiredAgents: []
preferredRunner:
assignedRunner:
executorAgent:
leaseOwner:
leaseExpiresAt:
status: pending
priority: normal
dueAt:
sourceMaterialRefs: []
expectedOutput: []
executionContract:
  version: execution-contract.v1
  contractId: EC-KT-YYYYMMDD-001
  taskId: KT-YYYYMMDD-001
  status: active
  generatedAt: 2026-06-18T00:00:00Z
  ruleRef: docs/workflows/execution-contract-lifecycle.md
  hashAlgorithm: sha256
  sourceFactsHash: sha256:<hash of task facts>
resultRef:
notificationRefs: []
auditRefs: []
---

## Request

What the requester asked for.

## Work Source

- workSourceType: feature | bugfix | project_setup | research | knowledge_ingest | maintenance
- feature tasks must link requirementRefs.
- bugfix tasks must link defectRefs; requirementRefs are optional.
- research, knowledge_ingest, and maintenance tasks must include sourceReason, researchQuestion, sourceMaterialRefs, knowledgeTaskRefs, or expectedOutput as applicable.
- downstream Agent must create ReceiverReview before consuming upstream deliverables.

## Source Materials

- SourceMaterial refs, links, snapshots, or storage refs.

## Expected Output

- Structured summary.
- Evidence-backed conclusions.
- KnowledgeItem drafts or project updates if applicable.

## Execution Contract

- Refresh with `zhenzhi-knowledge task contract <task-id>` after source materials, expected output, linked requirements/defects, or runtime constraints change.
- Runner must not close the task when `executionContract.sourceFactsHash` differs from current task facts.

## Handling Notes

Scheduler should assign this task to an Agent Ring runner with matching capability, permission, data access, and load.

Agent Ring should use local Codex, Claude, IDE automation, browser automation, local models, or approved tools when the work needs project context, long-document parsing, or engineering execution.
