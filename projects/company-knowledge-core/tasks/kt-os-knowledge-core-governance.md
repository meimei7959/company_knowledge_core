---
type: ProjectTask
title: AI Native OS Knowledge Core governance hardening
description: Ensure source material, draft knowledge, review, publish, index, query, conflict, and stale handling form a closed governance loop.
timestamp: "2026-06-20T02:40:00Z"
taskId: KT-OS-KNOWLEDGE-CORE-GOVERNANCE
taskType: os_maturity_hardening
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - source_material
  - knowledge_review
  - publishing
  - indexing
  - conflict_detection
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
  - agent.company-knowledge-core.knowledge-query
preferredRunner: []
assignedRunner: runner.meimei-mac-local-codex
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: waiting_runner
priority: critical
dueAt: []
sourceMaterialRefs:
  - docs/workflows/knowledge-ingest-orchestration.md
  - docs/workflows/knowledge-lifecycle.md
expectedOutput:
  - end-to-end knowledge governance flow
  - status-aware query behavior
  - source evidence enforcement
  - conflict and stale handling
resultRef: []
notificationRefs:
  - notifications/notification.20260621T052918742324Z.md
  - notifications/notification.20260621T053349649657Z.md
  - notifications/notification.20260621T053430463108Z.md
  - notifications/notification.20260621T055524581775Z.md
  - notifications/notification.20260621T055554626693Z.md
  - notifications/notification.20260621T055613440936Z.md
  - notifications/notification.20260621T061855438744Z.md
  - notifications/notification.20260621T062940728387Z.md
auditRefs: []
updatedAt: "2026-06-21T07:18:05Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"os_maturity_hardening","category":"project","stage":"","requiredCapabilities":["os_maturity_hardening","source_material","knowledge_review","publishing","indexing","conflict_detection"],"requiredTools":[],"sourceRefs":["docs/workflows/knowledge-ingest-orchestration.md","docs/workflows/knowledge-lifecycle.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
---

## Goal

Make knowledge reusable, sourced, reviewed, status-aware, and safe for Agents and employees.

## Supports Mature OS Capability

Knowledge Core.

## Requirements

- Public and project knowledge intake both create SourceMaterial and processing tasks when extraction is needed.
- Draft knowledge must include source evidence, scope, confidence, and limitations.
- Query results must show status and source, and must not present draft knowledge as verified truth.
- Review outcome must route to publish, index, return-for-rework, conflict handling, or human approval.

## Completion Standard

- No reusable knowledge is indexed as verified without review gate.
- A query with only draft results clearly labels them as pending reference.
- Every KnowledgeItem has source material or explicit provenance.

## Test Method

- End-to-end intake to draft to review to publish to query test.
- Negative test for missing source evidence.
- Query test for verified, draft, and no-result cases.
