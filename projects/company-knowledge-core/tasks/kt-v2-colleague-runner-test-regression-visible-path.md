---
type: ProjectTask
title: 阶段二回归：主界面路径脱敏与多设备闭环复测
description: ProjectTask assigned to agent.company.test.
timestamp: "2026-06-22T13:32:03Z"
taskId: kt-v2-colleague-runner-test-regression-visible-path
taskType: test_validation
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"test_validation","category":"project","stage":"","requiredCapabilities":["test_validation"],"requiredTools":[],"sourceRefs":["研发完成主界面路径泄露返修，需测试 Agent 回归"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
projectId: company-knowledge-core
requester: agent.company.project-manager
assignee: agent.company.test
status: waiting_acceptance
priority: high
dueAt: ""
sourceMaterialRefs:
  - projects/company-knowledge-core/workflows/phase2-multi-device-collaboration-orchestrator.md
  - projects/company-knowledge-core/test-reports/phase2-colleague-runner-test-report.md
  - task-results/tr-kt-v2-colleague-runner-test.md
  - task-results/tr-kt-v2-colleague-runner-development-fix-visible-path.md
  - 研发完成主界面路径泄露返修，需测试 Agent 回归
expectedOutput:
  - 复测 runtime-monitor 主界面不得出现绝对路径或 workspace/repository 原始值；回归工作台 validator、DOM 可见文本扫描、双 Runner 模拟、全量 validate 和 diff check
resultRef: task-results/tr-kt-v2-colleague-runner-test-regression-visible-path.md
notificationRefs:
  - notifications/notification.20260622T133203010283Z.md
auditRefs:
  - knowledge/audit/audit.20260622T133600Z-phase2-colleague-runner-regression-visible-path.md
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
handoffContract: {"from":"agent.company.test","to":"agent.company.project-manager","requiredArtifacts":["summary","evidence refs","next action or terminal reason"],"handoffSummary":"路径脱敏返修回归通过；所有自动检查和独立 DOM 扫描通过。真实双 host 风险仍需 PM/产品决策。","artifactRefs":["task-results/tr-kt-v2-colleague-runner-test-regression-visible-path.md","projects/company-knowledge-core/test-reports/phase2-colleague-runner-regression-visible-path-report.md","projects/company-knowledge-core/test-reports/artifacts/phase2-colleague-runner-regression-visible-path-evidence.20260622T133500Z.jsonl"]}
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
updatedAt: "2026-06-22T13:36:00Z"
---

## Request

阶段二回归：主界面路径脱敏与多设备闭环复测

## Source Materials

- 研发完成主界面路径泄露返修，需测试 Agent 回归

## Expected Output

- 复测 runtime-monitor 主界面不得出现绝对路径或 workspace/repository 原始值；回归工作台 validator、DOM 可见文本扫描、双 Runner 模拟、全量 validate 和 diff check

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

## Regression Gate

- Must verify the blocker from `tr-kt-v2-colleague-runner-test.md` is closed.
- Must run visible DOM/path leak checks, desktop workbench validator, targeted tests, distributed runner proof, validate, and diff check.
- If regression fails, create a new defect task for agent.company.development.

## Regression Outcome

- status: passed
- resultRef: task-results/tr-kt-v2-colleague-runner-test-regression-visible-path.md
- reportRef: projects/company-knowledge-core/test-reports/phase2-colleague-runner-regression-visible-path-report.md
- evidenceRef: projects/company-knowledge-core/test-reports/artifacts/phase2-colleague-runner-regression-visible-path-evidence.20260622T133500Z.jsonl
- auditRef: knowledge/audit/audit.20260622T133600Z-phase2-colleague-runner-regression-visible-path.md
- runRef: runs/company-knowledge-core/run.20260622T133600Z-phase2-colleague-runner-regression-visible-path.md
- conclusion: 原 runtime-monitor 主界面路径泄漏阻断缺陷已关闭；自动检查和独立 DOM 扫描全部通过。
- remainingRisk: 真实双 host 验收风险仍存在，本地模拟不能自动替代最终真实同事电脑验收。
