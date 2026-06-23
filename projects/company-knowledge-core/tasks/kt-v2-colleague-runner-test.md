---
type: ProjectTask
title: 阶段二：同事接入多设备闭环测试
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T11:54:29Z"
taskId: kt-v2-colleague-runner-test
taskType: test_validation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test_validation","category":"project","stage":"","requiredCapabilities":["test_validation"],"requiredTools":[],"sourceRefs":["研发完成后交测试 Agent 验证"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: changes_requested
priority: high
dueAt: ""
sourceMaterialRefs:
  - 研发完成后交测试 Agent 验证
  - task-results/tr-kt-v2-colleague-runner-development.md
  - runs/company-knowledge-core/run.20260622T131009Z-phase2-colleague-runner-development.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
  - scripts/validate_desktop_workbench_slice0.py
  - scripts/distributed_runner_proof_harness.py
  - tests/test_desktop_workbench_slice0.py
  - tests/test_distributed_runner_proof_harness.py
expectedOutput:
  - 验证双设备/双 Runner 模拟、路由可视化、中文用户视角、权限/异常状态、回归测试与验收证据
  - 必须专项验证用户可读性：普通用户能看懂当前项目、同事接入状态、任务路由去向、卡住原因、下一步操作
  - 必须专项扫描主界面不得出现 runtimeMetrics、sessionId、runnerId、deviceId、capability code、raw status、文件路径等内部字段
resultRef: task-results/tr-kt-v2-colleague-runner-test.md
notificationRefs:
  - notifications/notification.20260622T115429667586Z.md
  - notifications/notification.20260622T131009Z-phase2-colleague-runner-development-handoff.md
auditRefs:
  - knowledge/audit/audit.20260622T131009Z-phase2-colleague-runner-development.md
  - knowledge/audit/audit.20260622T131845Z-phase2-colleague-runner-test.md
operatingRuleRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
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
taskVersion: 2
handoffContract: {"from":"agent.company.development","to":"agent.company.test","requiredArtifacts":["summary","evidence refs","validator result","rendered DOM scan","simulated multi-runner proof result","next action or terminal reason"],"handoffSummary":"Development finished controlled Phase 2 implementation slice. Test must verify colleague access/read model, device and runner display, authorization, route board, readonly degradation, recovery states, audit summaries, and no internal fields in primary UI."}
qualityGateRequired: true
attemptNumber: 1
maxAttempts: 3
followupTaskRefs:
  - projects/company-knowledge-core/tasks/kt-v2-colleague-runner-development-fix-visible-path.md
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs: []
updatedAt: "2026-06-22T13:18:45Z"
---

## Request

阶段二：同事接入多设备闭环测试

## Source Materials

- 研发完成后交测试 Agent 验证
- task-results/tr-kt-v2-colleague-runner-development.md
- runs/company-knowledge-core/run.20260622T131009Z-phase2-colleague-runner-development.md
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
- projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
- scripts/validate_desktop_workbench_slice0.py
- scripts/distributed_runner_proof_harness.py
- tests/test_desktop_workbench_slice0.py
- tests/test_distributed_runner_proof_harness.py

## Expected Output

- 验证双设备/双 Runner 模拟、路由可视化、中文用户视角、权限/异常状态、回归测试与验收证据
- 必须专项验证用户可读性：普通用户能看懂当前项目、同事接入状态、任务路由去向、卡住原因、下一步操作
- 必须专项扫描主界面不得出现 runtimeMetrics、sessionId、runnerId、deviceId、capability code、raw status、文件路径等内部字段

## Handling Notes

The central scheduler should match this task to an Agent Ring runner. The runner claims the task with a lease, processes linked source material through local Codex, Claude, local models, IDE automation, or approved tools, then writes a TaskResult back to the central processor.

## Handoff Contract

- from: agent.company.development
- to: agent.company.test
- requiredArtifacts:
  - summary
  - evidence refs
  - validator result
  - rendered DOM scan
  - simulated multi-runner proof result
  - next action or terminal reason
- handoffSummary: Development finished controlled Phase 2 implementation slice. Test must verify colleague access/read model, device and runner display, authorization, route board, readonly degradation, recovery states, audit summaries, and no internal fields in primary UI.

## Quality Gate

- TaskResult must include summary, evidence/artifacts, quality evaluation, and handoff or terminal reason.
- Failed evaluation creates retry/escalation follow-up instead of silently closing.

## Test Outcome

- status: changes_requested
- resultRef: task-results/tr-kt-v2-colleague-runner-test.md
- reportRef: projects/company-knowledge-core/test-reports/phase2-colleague-runner-test-report.md
- followupTaskRef: projects/company-knowledge-core/tasks/kt-v2-colleague-runner-development-fix-visible-path.md
- reason: 渲染后的 runtime-monitor 可见文本包含本机绝对路径 `/Users/meimei/Documents/company_knowledge_core`，违反主界面不得出现文件路径等内部字段的验收要求。

## Agent Team Guide Gate

- Not required unless execution discovers an Agent role, Skill, workflow, Scheduler, Agent Ring, or knowledge policy change.

## Phase 2 Workflow Gate

- Must follow `projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md` before execution.
- Must preserve role boundary: Product, Design, Architecture, Development, Test, and PM conclusions are separate artifacts.
- Main workbench UI must be user-readable Chinese and hide internal fields from primary content.
