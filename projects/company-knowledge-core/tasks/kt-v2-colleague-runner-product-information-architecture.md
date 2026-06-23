---
type: ProjectTask
title: 阶段二：同事接入工作台产品信息架构
description: ProjectTask assigned to agent.company.product-manager.
timestamp: "2026-06-22T12:31:01Z"
taskId: kt-v2-colleague-runner-product-information-architecture
taskType: product_requirements
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"product_requirements","category":"project","stage":"","requiredCapabilities":["product_requirements"],"requiredTools":[],"sourceRefs":["用户明确：信息架构应该由产品经理整理，设计 Agent 只做 UI/交互设计"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.product-manager
status: done
priority: high
dueAt: ""
sourceMaterialRefs:
  - 用户明确：信息架构应该由产品经理整理，设计 Agent 只做 UI/交互设计
expectedOutput:
  - 输出产品信息架构：页面目标、导航模型、用户对象分组、主次信息、用户可见命名、概念边界、禁止暴露字段、交付给设计/架构/研发/测试的 IA 输入
resultRef: task-results/tr-kt-v2-colleague-runner-product-information-architecture.md
notificationRefs:
  - notifications/notification.20260622T123101883094Z.md
auditRefs:
  - knowledge/audit/audit.20260622T123415Z-phase2-colleague-runner-product-information-architecture.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md
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
updatedAt: "2026-06-22T12:34:15Z"
---

## Request

阶段二：同事接入工作台产品信息架构

## Source Materials

- 用户明确：信息架构应该由产品经理整理，设计 Agent 只做 UI/交互设计

## Expected Output

- 输出产品信息架构：页面目标、导航模型、用户对象分组、主次信息、用户可见命名、概念边界、禁止暴露字段、交付给设计/架构/研发/测试的 IA 输入

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
- Result written: task-results/tr-kt-v2-colleague-runner-product-information-architecture.md
- Product IA artifact: projects/company-knowledge-core/product-information-architecture/phase2-colleague-runner-workbench-information-architecture.md
- Audit: knowledge/audit/audit.20260622T123415Z-phase2-colleague-runner-product-information-architecture.md

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.

## Phase 2 Workflow Gate

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator-orchestrator.md` before execution.
- Product Manager Agent owns information architecture: navigation model, object grouping, user-facing terminology, content hierarchy, and forbidden main-UI fields.
- Design Agent consumes this artifact for UI/interaction design.
