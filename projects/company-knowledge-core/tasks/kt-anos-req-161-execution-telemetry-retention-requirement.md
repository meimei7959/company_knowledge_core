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
status: done
priority: high
dueAt: []
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
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.product-requirement.md
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
resultRef:
  - task-results/tr-kt-anos-req-161-product-requirement-acceptance.md
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260623T113018926248Z.md
  - knowledge/audit/audit.20260623T113530Z-anos-req-161-pm-orchestration.md
  - knowledge/audit/audit.20260623T113824529424Z.md
  - knowledge/audit/audit.20260623T114315Z-anos-req-161-product-requirement-acceptance.md
pmActionRefs:
  - projects/company-knowledge-core/pm-actions/pm-action.20260623T113824528952Z.md
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-architecture.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-development.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-test.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-product-acceptance.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-pm-closeout.md
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_requirement","category":"product","stage":"product_requirement","requiredCapabilities":["product_requirement","requirement_traceability","acceptance_criteria_definition"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/execution-telemetry-retention-prd.md","docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","docs/product/ai-native-os/phase-2-central-runner-observability-prd.md","docs/product/ai-native-os/task-execution-productization-prd.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"product_requirement","acceptancePath":"pm_review","reviewPath":"product_prd_gate","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-23T12:27:52Z"
nextAction: ANOS-REQ-161 V0 product requirement accepted and downstream delivery closed by PM closeout; future work is limited to recorded scope deferrals if prioritized.
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.product-manager","requiredArtifacts":["ReceiverReview","accepted requirement package","retention class table","protected reference rules","architecture handoff"],"artifactRefs":["docs/product/ai-native-os/execution-telemetry-retention-prd.md","docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md"],"blockedUntil":"Product Manager Agent ReceiverReview decision is accepted_for_work or accepted_with_assumptions."}
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

## PM Orchestration

Project Manager Agent created the downstream closed-loop chain on 2026-06-23. Architecture, development, test, product acceptance, and PM closeout tasks must not bypass this product requirement task.
