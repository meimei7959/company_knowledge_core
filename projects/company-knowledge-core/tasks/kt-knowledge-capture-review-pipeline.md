---
type: ProjectTask
title: Knowledge capture to review pipeline
description: Complete the flow from Feishu material or meeting note to SourceMaterial, KnowledgeTask, structured draft, Review, and reusable KnowledgeItem.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-KNOWLEDGE-CAPTURE-REVIEW-PIPELINE
taskType: engineering_action
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - knowledge_capture
  - source_material
  - review_gate
  - evidence
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/workflows/knowledge-lifecycle.md
  - zhenzhi_knowledge/feishu.py
expectedOutput:
  - SourceMaterial saved with raw content
  - KnowledgeTask created for parsing and structuring
  - structured KnowledgeItem draft with source evidence
  - Review gate before reusable knowledge
resultRef: task-results/tr-task-knowledge-capture-review-pipeline.md
notificationRefs:
  - notifications/notification.20260619T013445030390Z.md
auditRefs: []
completedAt: "2026-06-19T01:34:45Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action","knowledge_capture","source_material","review_gate","evidence"],"requiredTools":[],"sourceRefs":["docs/workflows/knowledge-lifecycle.md","zhenzhi_knowledge/feishu.py"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
---

## Request

Make knowledge capture evidence-backed and reviewable.

## Definition of Done

- Uploaded or pasted material is stored as SourceMaterial, not directly as verified knowledge.
- KnowledgeTask includes source refs, expected output, assignee, and project context.
- Structured draft includes summary, source evidence, scope, confidence, limits, and original source path.
- Review gate prevents unreviewed summaries from becoming reusable verified knowledge.
- A future Agent can reopen the original source if the summary looks wrong.
- Tests cover material capture, meeting note capture, task creation, evidence refs, and review gate.

## Test Plan

- Unit test project material parsing by project name.
- Unit test SourceMaterial and KnowledgeTask creation.
- Unit test generated draft knowledge contains source evidence.
- Run validation to ensure KnowledgeItem category and status rules pass.

## Self-Verification Checklist

- [x] Raw material preserved.
- [x] Structured draft has evidence.
- [x] Review gate enforced.
- [x] Tests cover Feishu intake and local object writes.
