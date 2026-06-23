---
type: ProjectTask
title: ANOS-REQ-161 执行遥测保留与后台清理技术方案
description: Architecture Agent designs the minimal V0 telemetry retention, compaction, cleanup, audit summary, and learning-signal promotion solution after product requirement acceptance.
timestamp: "2026-06-23T11:35:30Z"
updatedAt: "2026-06-23T11:48:19Z"
taskId: kt-anos-req-161-telemetry-retention-architecture
taskType: technical_solution
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"technical_solution","category":"project","stage":"architecture_handoff","requiredCapabilities":["technical_solution","architecture_review","requirement_traceability","schema_boundary_review","workflow_design"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/execution-telemetry-retention-prd.md","docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","projects/company-knowledge-core/tasks/kt-anos-req-161-execution-telemetry-retention-requirement.md","docs/product/ai-native-os/phase-2-central-runner-observability-prd.md","docs/product/ai-native-os/task-execution-productization-prd.md","docs/schemas/core-objects.md"],"repositoryRefs":[],"dataScopes":["ProjectTask","AgentRunner","TaskResult","AgentRun","ReviewRecord","NotificationRecord","AuditLog","MetricsReport","SourceMaterial","AgentImprovementProposal","EvalCase"],"qualityGate":"architecture_solution","acceptancePath":"product_review","reviewPath":"product_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.architecture
status: done
priority: high
workSourceType: feature
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
requirementObjectRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
receiverReviewRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.architecture.md
sourceMaterialRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-execution-telemetry-retention-requirement.md
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.product-requirement.md
  - projects/company-knowledge-core/product-reviews/anos-req-161-telemetry-retention-product-requirement-acceptance.md
  - task-results/tr-kt-anos-req-161-product-requirement-acceptance.md
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
  - docs/schemas/core-objects.md
prerequisiteTaskRefs:
  - projects/company-knowledge-core/tasks/kt-anos-req-161-execution-telemetry-retention-requirement.md
expectedOutput:
  - Architecture Agent ReceiverReview before work; decision must be accepted_for_work or accepted_with_assumptions.
  - Technical solution for telemetry ingestion classification, Current State upsert, task closeout compaction, TelemetryRetentionWorker or equivalent background job, dry-run/apply, protected refs, batch AuditLog summary, and learning-signal promotion.
  - Explicit object/storage mapping that preserves Scheduler, Runner, TaskResult, AuditLog, and core object semantics.
  - V0 implementation slices, rollback plan, risks, and test handoff.
resultRef: task-results/tr-kt-anos-req-161-telemetry-retention-architecture.md
nextAction: Architecture solution accepted for V0 and consumed by Development; no further architecture action required for ANOS-REQ-161 V0.
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260623T113530Z-anos-req-161-pm-orchestration.md
  - knowledge/audit/audit.20260623T114315Z-anos-req-161-product-requirement-acceptance.md
  - knowledge/audit/audit.20260623T114650909797Z.md
  - knowledge/audit/audit.20260623T114819Z-anos-req-161-architecture.md
pmActionRefs:
  - projects/company-knowledge-core/pm-actions/pm-action.20260623T114650909089Z.md
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
assignedRunner: ""
executorAgent: agent.company.architecture
leaseOwner: ""
leaseTokenHash: ""
leaseProofHash: ""
leaseIssuedAt: ""
leaseExpiresAt: ""
leaseHeartbeatAt: ""
leaseVersion: 1
leaseAttempt: 0
heartbeatAt: ""
taskVersion: 2
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.architecture","requiredArtifacts":["ReceiverReview","technical solution","risk and rollback plan","implementation handoff"],"artifactRefs":["docs/product/ai-native-os/execution-telemetry-retention-prd.md","docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","projects/company-knowledge-core/product-reviews/anos-req-161-telemetry-retention-product-requirement-acceptance.md","task-results/tr-kt-anos-req-161-product-requirement-acceptance.md"],"blockedUntil":"Architecture Agent records ReceiverReview decision accepted_for_work or accepted_with_assumptions."}
---

## Hard Boundary

Do not introduce an external logging platform as V0 prerequisite. Do not rewrite Scheduler, Runner, TaskResult, AuditLog, lease, finish, or result writeback semantics. Do not make raw telemetry a long-term truth source.
