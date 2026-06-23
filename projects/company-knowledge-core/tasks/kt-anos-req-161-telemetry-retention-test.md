---
type: ProjectTask
title: ANOS-REQ-161 执行遥测保留与后台清理测试验证
description: Test Agent validates implementation against the ANOS-REQ-161 acceptance matrix, protected-reference safety, dry-run/apply behavior, batch audit, and learning-signal retention.
timestamp: "2026-06-23T11:35:30Z"
taskId: kt-anos-req-161-telemetry-retention-test
taskType: test_validation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test_validation","category":"project","stage":"test","requiredCapabilities":["test_validation","acceptance_matrix","retention_cleanup_regression","safety_regression"],"requiredTools":[],"sourceRefs":["docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-development.md"],"repositoryRefs":[],"dataScopes":["ProjectTask","TaskResult","AuditLog","MetricsReport","AgentImprovementProposal","EvalCase","SourceMaterial"],"qualityGate":"test_validation","acceptancePath":"product_review","reviewPath":"product_review","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":true,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
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
  - projects/company-knowledge-core/receiver-reviews/receiver-review.anos-req-161.test.md
sourceMaterialRefs:
  - docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-development.md
  - task-results/tr-kt-anos-req-161-telemetry-retention-development.md
  - zhenzhi_knowledge/telemetry_retention.py
  - tests/test_telemetry_retention.py
  - knowledge/audit/audit.20260623T120902Z-anos-req-161-development.md
prerequisiteTaskRefs:
  - projects/company-knowledge-core/tasks/kt-anos-req-161-telemetry-retention-development.md
prerequisiteEvidenceRefs:
  - task-results/tr-kt-anos-req-161-telemetry-retention-development.md
  - zhenzhi_knowledge/telemetry_retention.py
  - tests/test_telemetry_retention.py
  - scripts/quality/development_quality_gate.py
expectedOutput:
  - Test Agent ReceiverReview before work; decision must be accepted_for_work or accepted_with_assumptions.
  - Execute acceptance matrix for ANOS-REQ-161-001 through ANOS-REQ-161-008.
  - Verify dry-run reports delete/compact/rollup/promote/archive/skip counts and reasons before apply.
  - Verify protected refs are never deleted, including TaskResult, AuditLog, human acceptance, verified knowledge, active lease/task progress, unresolved blocker, open incident, AgentImprovementProposal, EvalCase, and required evidence.
  - Verify ordinary heartbeat/progress does not append indefinitely and cleanup does not write per-row AuditLog noise.
  - Verify learning signals survive cleanup and are promoted or linked.
  - Return test report and TaskResult; failed items route back to Development Agent.
resultRef: task-results/tr-kt-anos-req-161-telemetry-retention-test.md
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260623T113530Z-anos-req-161-pm-orchestration.md
  - knowledge/audit/audit.20260623T120902Z-anos-req-161-development.md
  - knowledge/audit/audit.20260623T121155758889Z.md
  - knowledge/audit/audit.20260623T121742Z-anos-req-161-test-validation.md
pmActionRefs:
  - projects/company-knowledge-core/pm-actions/pm-action.20260623T121155758197Z.md
operatingRuleRefs:
  - docs/agent-team/company-agent-constitution.md
  - docs/agent-team/agent-task-runtime-contract.md
  - docs/agent-team/human-acceptance-policy.md
  - docs/agent-team/common-agent-operating-rules.md
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
updatedAt: "2026-06-23T12:27:52Z"
nextAction: Test validation passed and was consumed by Product final acceptance; no Test rework required.
handoffContract: {"from":"agent.company.project-manager","to":"agent.company.test","requiredArtifacts":["ReceiverReview","test report","acceptance matrix result","TaskResult"],"artifactRefs":["docs/product/ai-native-os/execution-telemetry-retention-acceptance-matrix.md","task-results/tr-kt-anos-req-161-telemetry-retention-development.md","zhenzhi_knowledge/telemetry_retention.py","tests/test_telemetry_retention.py"],"blockedUntil":"Test Agent records ReceiverReview decision accepted_for_work or accepted_with_assumptions."}
---

## Test Boundary

Do not product-accept the requirement. Test Agent reports pass/fail evidence and routes failed items.
