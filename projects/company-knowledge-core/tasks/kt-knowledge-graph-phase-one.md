---
type: ProjectTask
title: Knowledge graph phase one
description: Materialize first-stage relationship edges from existing central processor objects and provide graph export and impact inspection.
timestamp: "2026-06-19T02:10:00Z"
taskId: TASK-KNOWLEDGE-GRAPH-PHASE-ONE
taskType: architecture_implementation
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.executor
requiredCapabilities:
  - graph_model
  - index
  - impact_analysis
  - audit
requiredAgents:
  - agent.company-knowledge-core.executor
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: medium
dueAt: []
sourceMaterialRefs:
  - docs/architecture/knowledge-graph-management.md
  - docs/schemas/core-objects.md
  - docs/strategy/zhenzhi-ai-native-knowledge-system.md
expectedOutput:
  - KnowledgeGraphEdge object support
  - GraphSnapshot export support
  - edge extraction during index rebuild
  - graph impact command
  - audit records for graph export and edge writes
resultRef: task-results/tr-task-knowledge-graph-phase-one.md
notificationRefs:
  - notifications/notification.20260619T025629847666Z.md
auditRefs: []
completedAt: "2026-06-19T02:56:29Z"
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"architecture_implementation","category":"project","stage":"","requiredCapabilities":["architecture_implementation","graph_model","index","impact_analysis","audit"],"requiredTools":[],"sourceRefs":["docs/architecture/knowledge-graph-management.md","docs/schemas/core-objects.md","docs/strategy/zhenzhi-ai-native-knowledge-system.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make knowledge relationships inspectable.

When a project, task, source material, knowledge item, tool, decision, policy, runner, or audit record changes, the central processor should know what depends on it and what may be affected.

## Scope

First-stage graph relationships should be extracted from parseable object fields, not inferred from vague prose.

Objects in scope:

- Project.
- ProjectTask / KnowledgeTask.
- AgentRunner.
- TaskResult.
- SourceMaterial.
- KnowledgeItem.
- AgentRun.
- ToolAsset.
- Decision.
- Policy.
- ConflictRecord.
- EvalRun.
- ReviewRecord when present.
- AuditLog.

## Definition of Done

- `KnowledgeGraphEdge` object shape is implemented or documented in executable schema support.
- `GraphSnapshot` export exists and is clearly marked as export artifact, not source of truth.
- Index rebuild or equivalent graph command extracts basic edges from frontmatter refs.
- Edges include fromRef, relation, toRef, sourceRef/evidenceRefs, confidence, status, sensitivity, and auditRefs where applicable.
- `zhenzhi-knowledge graph export` produces a graph snapshot without secret values.
- `zhenzhi-knowledge graph impact <ref>` shows directly affected projects, tasks, knowledge, tools, policies, sources, or runners.
- Context pack generation can explain at least one inclusion reason using graph relationships.
- Edge writes, deletes, and exports create AuditLog records.

## Test Plan

- Unit test graph edge extraction from Project, SourceMaterial, KnowledgeItem, TaskResult, ToolAsset, and Policy fixtures.
- Unit test graph export omits secret values and local-only sensitive fields.
- Unit test graph impact returns expected dependent objects for a changed SourceMaterial or ToolAsset.
- Unit test context pack includes a relationship reason for included knowledge.
- Run `python3 -m unittest tests.test_cli`.
- Run `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`.

## Self-Verification Checklist

- [ ] Edge object supported.
- [ ] Snapshot export supported.
- [ ] Edge extraction covered by tests.
- [ ] Impact command covered by tests.
- [ ] Secret filtering verified.
- [ ] Context inclusion reason verified.
- [ ] AuditLog written for graph operations.
