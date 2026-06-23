---
type: ProjectTask
title: ANOS-REQ-161 执行遥测保留与后台清理研发实现
description: Development Agent implements the accepted architecture for minimal telemetry retention, compaction, cleanup dry-run/apply, protected refs, batch audit, and learning signal promotion.
timestamp: "2026-06-23T11:35:30Z"
taskId: kt-anos-req-161-telemetry-retention-development
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"project","stage":"development","requiredCapabilities":["implementation","retention_worker","telemetry_ingestion","data_compaction","development_engineering_quality_gate"],"requiredTools":[],"sourceRefs":["projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture.md","docs/product/ai-native-os/execution-telemetry-retention-prd.md","docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","scripts/quality/development_quality_gate.py"],"repositoryRefs":[],"dataScopes":["ProjectTask","TaskResult","AgentRun","AuditLog","MetricsReport","AgentImprovementProposal","EvalCase"],"qualityGate":"development-engineering-quality-gate","acceptancePath":"test_then_product_review","reviewPath":"test_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: done
priority: high
workSourceType: feature
requirementRefs:
  - ANOS-REQ-161
  - ANOS-REQ-160
requirementObjectRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
acceptanceCriteriaRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
receiverReviewRefs:
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.development.md
sourceMaterialRefs:
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture.md
  - projects/company-knowledge-core/technical-solutions/anos-req-161-telemetry-retention-technical-solution.md
  - task-results/tr-kt-anos-req-161-telemetry-retention-architecture.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture-product-review.md
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.architecture-product-review.md
  - projects/company-knowledge-core/product-reviews/anos-req-161-telemetry-retention-architecture-product-review.md
  - task-results/tr-kt-anos-req-161-architecture-product-review.md
  - docs/product/ai-native-os/execution-telemetry-retention-prd.md
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
  - docs/product/ai-native-os/task-execution-productization-prd.md
prerequisiteTaskRefs:
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture-product-review.md
prerequisiteEvidenceRefs:
  - projects/company-knowledge-core/technical-solutions/anos-req-161-telemetry-retention-technical-solution.md
  - task-results/tr-kt-anos-req-161-telemetry-retention-architecture.md
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.architecture-product-review.md
  - projects/company-knowledge-core/product-reviews/anos-req-161-telemetry-retention-architecture-product-review.md
  - task-results/tr-kt-anos-req-161-architecture-product-review.md
  - scripts/quality/development_quality_gate.py
expectedOutput:
  - Development Agent ReceiverReview before work; decision must be accepted_for_work or accepted_with_assumptions.
  - Implement accepted architecture only after architecture/product review are accepted.
  - Current State status telemetry must upsert/overwrite instead of append unbounded raw noise.
  - Cleanup supports dry-run and apply with protected-reference skip reasons.
  - Cleanup emits one batch AuditLog summary per run, not per-row deletion noise.
  - Learning signals are promoted or linked before any cleanup can discard related raw telemetry.
  - Load development-engineering-quality-gate and run scripts/quality/development_quality_gate.py before handoff.
  - Return TaskResult with changed files, tests/checks, quality gate output, risks, and test handoff.
resultRef: task-results/tr-kt-anos-req-161-telemetry-retention-development.md
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260623T113530Z-anos-req-161-pm-orchestration.md
  - knowledge/audit/audit.20260623T115231Z-anos-req-161-architecture-product-review-task.md
  - knowledge/audit/audit.20260623T115323217167Z.md
  - knowledge/audit/audit.20260623T115555Z-anos-req-161-architecture-product-review.md
  - knowledge/audit/audit.20260623T115909460098Z.md
  - knowledge/audit/audit.20260623T120902Z-anos-req-161-development.md
pmActionRefs:
  - projects/company-knowledge-core/pm-actions/pm-action.20260623T115323216406Z.md
  - projects/company-knowledge-core/pm-actions/pm-action.20260623T115909459639Z.md
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
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
updatedAt: "2026-06-23T12:27:52Z"
nextAction: Development completed with quality gate evidence and passed Test/Product acceptance; no Development rework required for ANOS-REQ-161 V0.
taskVersion: 3
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.development","requiredArtifacts":["ReceiverReview","implementation summary","changed files","test evidence","development quality gate output","TaskResult"],"artifactRefs":["projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture.md","projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture-product-review.md","projects/company-knowledge-core/technical-solutions/anos-req-161-telemetry-retention-technical-solution.md","projects/company-knowledge-core/product-reviews/anos-req-161-telemetry-retention-architecture-product-review.md","task-results/tr-kt-anos-req-161-architecture-product-review.md","scripts/quality/development_quality_gate.py"],"blockedUntil":"PM/Scheduler dispatches this task and Development Agent creates an accepted ReceiverReview; architecture-product review is accepted_with_assumptions."}
---

## Hard Stop

Do not start implementation until the Architecture Agent TaskResult and required product review are accepted. Do not bypass `development-engineering-quality-gate`.
