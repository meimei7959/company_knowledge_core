---
type: ProjectTask
title: ANOS-REQ-161 Execution Telemetry Retention Requirement
description: Product Manager Agent refines execution telemetry retention, compaction, cleanup, audit summary, and learning signal promotion requirements before Architecture Agent technical solution.
timestamp: "2026-06-23T10:05:00+08:00"
taskId: kt-anos-req-161-execution-telemetry-retention-requirement
taskType: product_requirement
projectId: company-knowledge-core
requester: agent.company.architecture
assignee: agent.company.product-manager
currentStage: product_requirement
technicalSolutionRequired: false
relatedRequirements:
  - ANOS-REQ-161
  - ANOS-REQ-160
requiredCapabilities:
  - product_requirement
  - requirement_traceability
  - acceptance_criteria_definition
requiredAgents:
  - agent.company.product-manager
preferredRunner: []
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: pending
priority: high
dueAt: []
sourceMaterialRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
expectedOutput:
  - Accepted ANOS-REQ-161 product requirement package
  - Retention class table
  - Cleanup dry-run/apply acceptance criteria
  - Protected reference rules
  - Handoff input for Architecture Agent technical solution
resultRef: []
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260623T113018926248Z.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_requirement","category":"product","stage":"product_requirement","requiredCapabilities":["product_requirement","requirement_traceability","acceptance_criteria_definition"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/execution-telemetry-retention-prd.md","docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","docs/product/ai-native-os/phase-2-central-runner-observability-prd.md","docs/product/ai-native-os/task-execution-productization-prd.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"product_requirement","acceptancePath":"pm_review","reviewPath":"product_prd_gate","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-23T10:05:00+08:00"
nextAction: Product Manager Agent should refine ANOS-REQ-161 before Architecture Agent writes a technical solution.
---

## Request

Act as Product Manager Agent. Turn ANOS-REQ-161 into an accepted product requirement for execution telemetry retention and cleanup.

## Boundary

Do not implement cleanup. Do not change Runner/Scheduler/TaskResult behavior from this task. Preserve TaskResult, AuditLog, MetricsReport, AgentImprovementProposal, EvalCase, Review, and knowledge governance contracts.

## Required Output

- Retention classes and default TTL.
- Current State / Task Timeline / TaskResult / Audit / Metrics / Learning Signal split.
- Task closeout compaction rules.
- Background cleanup dry-run/apply behavior.
- Protected reference rules.
- Acceptance matrix ready for Architecture Agent.
