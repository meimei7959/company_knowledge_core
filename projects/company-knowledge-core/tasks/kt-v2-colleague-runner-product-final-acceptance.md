---
type: ProjectTask
title: 阶段二：同事接入多设备协作产品验收
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T13:39:46Z"
taskId: kt-v2-colleague-runner-product-final-acceptance
taskType: product_acceptance
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_acceptance","category":"project","stage":"","requiredCapabilities":["product_acceptance"],"requiredTools":[],"sourceRefs":["测试回归通过，但真实双 host 风险仍需产品验收判断"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: blocked
priority: high
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/test-reports/phase2-colleague-runner-regression-visible-path-report.md
  - task-results/tr-kt-v2-colleague-runner-test-regression-visible-path.md
  - task-results/tr-kt-v2-colleague-runner-development-fix-visible-path.md
  - task-results/tr-kt-v2-colleague-runner-test.md
  - task-results/tr-kt-v2-colleague-runner-development.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-ia-ui-impact-revision.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-ui-interaction-revision.md
  - projects/company-knowledge-core/product-information-architecture/phase2-colleague-runner-workbench-information-architecture.md
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
  - 测试回归通过，但真实双 host 风险仍需产品验收判断
expectedOutput:
  - 产品经理基于 PRD、产品 IA、UI/交互设计、技术方案、研发结果、测试报告和回归结果，判断阶段二产品目标是否通过；明确本机模拟和真实同事电脑验收边界
resultRef: task-results/tr-kt-v2-colleague-runner-product-final-acceptance.md
notificationRefs:
  - notifications/notification.20260622T133946459317Z.md
auditRefs: []
resultAuditRefs:
  - knowledge/audit/audit.20260622T134409Z-phase2-colleague-runner-product-final-acceptance.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
assignedRunner: ""
executorAgent: agent.company.product-manager
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
handoffContract: {"from":"","to":"","requiredArtifacts":["summary","evidence refs","next action or terminal reason"]}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T13:44:09Z"
---

## Request

阶段二：同事接入多设备协作产品验收

## Source Materials

- 测试回归通过，但真实双 host 风险仍需产品验收判断

## Expected Output

- 产品经理基于 PRD、产品 IA、UI/交互设计、技术方案、研发结果、测试报告和回归结果，判断阶段二产品目标是否通过；明确本机模拟和真实同事电脑验收边界

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: current assignee
- to: terminal or project manager decision
- requiredArtifacts:
  - summary
  - evidence refs
  - next action or terminal reason

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.

## Product Acceptance Gate

- Product Manager Agent must decide whether Phase 2 product acceptance passes, fails, or passes only as local-simulation readiness.
- Must explicitly state whether real colleague computer / real dual host is final acceptance blocker.
- PM cannot close beyond the Product decision.
