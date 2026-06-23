---
type: ProjectTask
title: 阶段二返修：主界面路径泄露脱敏
description: ProjectTask assigned to agent.company.development.
timestamp: "2026-06-22T13:18:45Z"
taskId: kt-v2-colleague-runner-development-fix-visible-path
taskType: implementation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"implementation","category":"project","stage":"","requiredCapabilities":["implementation"],"requiredTools":[],"sourceRefs":["task-results/tr-kt-v2-colleague-runner-test.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"test_validation","reviewPath":"test_validation","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":true,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.test
assignee: agent.company.development
status: done
priority: high
dueAt: ""
sourceMaterialRefs:
  - task-results/tr-kt-v2-colleague-runner-test.md
  - projects/company-knowledge-core/test-reports/phase2-colleague-runner-test-report.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
expectedOutput:
  - 修复主界面运行监控页本机绝对路径可见文本泄露。
  - 主界面不得出现 runtimeMetrics、sessionId、runnerId、deviceId、capability code、raw status、文件路径、repositoryRefs、repositoryScopes、workspace 原始值。
  - 补充 DOM 可见文本测试，覆盖 `/Users/`、项目内路径、workspace/repository path 原始值。
  - 重新运行 validator、targeted unittest、full unittest/validate、git diff --check。
resultRef: task-results/tr-kt-v2-colleague-runner-development-fix-visible-path.md
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260622T131845Z-phase2-colleague-runner-test.md
  - knowledge/audit/audit.20260622T132714Z-phase2-colleague-runner-visible-path-fix.md
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
taskVersion: 1
handoffContract: {"from":"agent.company.test","to":"agent.company.development","requiredArtifacts":["fixed implementation","DOM visible text scan","validator result","targeted unittest result","full unittest/validate result","handoff back to test"],"handoffSummary":"测试发现 runtime-monitor 可见文本泄露 /Users/meimei/Documents/company_knowledge_core。请脱敏 workspace/repository path 渲染，补测试后交回测试 Agent。"}
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
updatedAt: "2026-06-22T13:27:14Z"
---

## Request

修复阶段二主界面路径泄露缺陷。

## Defect

渲染后的 `runtime-monitor` 可见文本包含 `/Users/meimei/Documents/company_knowledge_core`。测试定位到：

- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js:738` 渲染 `device.workspace`。
- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js:861` 存在本机绝对路径 `workspace`。
- `projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js` 多处 `repositoryRefs` / `repositoryScopes` 含本机绝对路径。

## Acceptance

- 主界面所有可见文本不得出现本机绝对路径、项目内文件路径、workspace/repositoryRefs/repositoryScopes 原始值。
- 协作设备页继续保留中文用户可读性、设备/执行器列表、配对授权、任务路由、只读降级、异常恢复、审计摘要。
- 返修后交回 `agent.company.test` 复测 `kt-v2-colleague-runner-test`。
