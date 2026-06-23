---
type: ProjectTask
title: 阶段二：同事接入与多设备路由研发实现
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-22T11:54:29Z"
taskId: kt-v2-colleague-runner-development
taskType: engineering_action
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"","requiredCapabilities":["engineering_action"],"requiredTools":[],"sourceRefs":["产品复核架构方案通过后进入研发实现"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"engineering","acceptancePath":"pm_review","reviewPath":"engineering_test","riskLevel":"medium","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.development
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/product-reviews/phase2-multi-device-runner-collaboration-ia-ui-addendum-product-review.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-ia-ui-impact-revision.md
  - projects/company-knowledge-core/technical-solutions/phase2-multi-device-runner-collaboration-technical-solution.md
  - projects/company-knowledge-core/design/phase2-multi-device-runner-workbench-ui-interaction-revision.md
  - projects/company-knowledge-core/product-information-architecture/phase2-colleague-runner-workbench-information-architecture.md
  - docs/product/ai-native-os/phase-2-multi-device-runner-collaboration-prd.md
  - 产品复核架构方案通过后进入研发实现
expectedOutput:
  - 按方案实现工作台入口、同事接入/配对说明、设备/Runner 展示、路由状态与验证守卫
  - 实现必须遵守设计规范：主界面只展示中文业务含义，不把内部 id、raw status、能力 code、文件路径当作用户主信息
resultRef: task-results/tr-kt-v2-colleague-runner-development.md
notificationRefs:
  - notifications/notification.20260622T115429527584Z.md
  - notifications/notification.20260622T131009Z-phase2-colleague-runner-development-handoff.md
auditRefs:
  - knowledge/audit/audit.20260622T131009Z-phase2-colleague-runner-development.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
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
taskVersion: 1
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["implementation summary","changed files","validator result","unittest result","simulated multi-runner evidence","risk notes"],"handoffSummary":"研发切片已实现协作设备 read model、主界面、只读降级、路由状态、恢复项、审计摘要、模拟验收入口和 validator/unittest；请测试 Agent 按阶段二 PM Workflow 验证。","artifactRefs":["task-results/tr-kt-v2-colleague-runner-development.md","runs/company-knowledge-core/run.20260622T131009Z-phase2-colleague-runner-development.md","projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js","projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js","scripts/validate_desktop_workbench_slice0.py","scripts/distributed_runner_proof_harness.py","tests/test_desktop_workbench_slice0.py","tests/test_distributed_runner_proof_harness.py"]}
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
updatedAt: "2026-06-22T13:10:09Z"
completedAt: "2026-06-22T13:10:09Z"
---

## Request

阶段二：同事接入与多设备路由研发实现

## Source Materials

- 产品复核架构方案通过后进入研发实现

## Expected Output

- 按方案实现工作台入口、同事接入/配对说明、设备/Runner 展示、路由状态与验证守卫
- 实现必须遵守设计规范：主界面只展示中文业务含义，不把内部 id、raw status、能力 code、文件路径当作用户主信息
- 若需要保留技术证据，必须放到“技术详情”或“证据”入口里，不能干扰普通用户判断

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.development
- to: agent.company.test
- requiredArtifacts:
  - implementation summary
  - changed files
  - validator result
  - unittest result
  - simulated multi-runner evidence
  - risk notes
- handoffSummary: 研发切片已实现协作设备 read model、主界面、只读降级、路由状态、恢复项、审计摘要、模拟验收入口和 validator/unittest；请测试 Agent 按阶段二 PM Workflow 验证。
- artifactRefs:
  - task-results/tr-kt-v2-colleague-runner-development.md
  - runs/company-knowledge-core/run.20260622T131009Z-phase2-colleague-runner-development.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
  - scripts/validate_desktop_workbench_slice0.py
  - scripts/distributed_runner_proof_harness.py
  - tests/test_desktop_workbench_slice0.py
  - tests/test_distributed_runner_proof_harness.py

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.

## Phase 2 Workflow Gate

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md` before execution.
- Must preserve role boundary: Product, Design, Architecture, Development, Test, and PM conclusions are separate artifacts.
- Main workbench UI must be user-readable Chinese and hide internal fields from primary content.

## Development Hard Inputs

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md`.
- Must implement from PRD, Product IA, UI/interaction design, original technical solution, architecture addendum, and Product re-review together.
- Must not expose internal ids/raw status/capability code/file paths as primary workbench content.
- Must include self-tests and hand off to Test Agent; PM/main thread must not fix test failures directly.
