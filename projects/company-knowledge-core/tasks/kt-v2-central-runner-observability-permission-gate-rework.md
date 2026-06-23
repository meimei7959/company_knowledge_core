---
type: ProjectTask
title: Phase 2 中枢 Runner 观测登记入口权限门禁返工
description: Development rework for Phase 2 central runner observability permission gate acceptance failure.
timestamp: "2026-06-23T02:34:03Z"
taskId: kt-v2-central-runner-observability-permission-gate-rework
taskType: engineering_action
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"rework","requiredCapabilities":["api","cli","testing","governance","audit"],"qualityGate":"engineering","acceptancePath":"test_agent_review","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
projectId: company-knowledge-core
requester: agent.company.test
assignee: agent.company.development
status: waiting_runner
priority: high
dueAt: ""
sourceMaterialRefs:
  - task-results/tr-kt-v2-central-runner-observability-test.md
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md
expectedOutput:
  - API 工作台写入口缺少 permissions 或权限不足时拒绝写入，返回清晰错误，不创建登记对象。
  - CLI 工作台写命令强制权限语义；缺少 --permission 或权限不足时非 0 退出，不创建登记对象。
  - 缺权限写入必须创建 workbench.permission.denied AuditLog，并包含 actor、targetRef、before/after、policyResult 或等价可读原因。
  - 补充 API/CLI 缺权限回归测试，覆盖 create-project、invite-runner、register-tool、request-tool。
  - 保持 idempotency、审批状态、只读监管、旧 Agent Ring register/heartbeat/claim/finish 兼容不回归。
resultRef: ""
notificationRefs: []
auditRefs:
  - knowledge/audit/audit.20260623T023403Z-central-runner-observability-test.md
assignedRunner: ""
leaseOwner: ""
leaseProofHash: ""
leaseExpiresAt: ""
heartbeatAt: ""
taskVersion: 1
handoffContract: {"from":"agent.company.test","to":"agent.company.development","requiredArtifacts":["code fix","targeted tests","full local regression result","updated TaskResult"],"failureSummary":"API/CLI workbench write entry points create objects without permissions and without workbench.permission.denied audit."}
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
updatedAt: "2026-06-23T02:34:03Z"
completedAt: ""
---

## Request

修复 Phase 2 方案二中枢 Runner 观测与登记入口验收失败项：工作台 API/CLI 写入口必须强制业务权限语义。

## Failure Evidence

测试 Agent 复验发现：

- `POST /v0/workbench/projects` 不传 `permissions` 仍返回 200 并创建 `WorkbenchProject`。
- `POST /v0/workbench/runner-invitations` 不传 `permissions` 仍返回 200 并创建 `RunnerInvitation`。
- `POST /v0/workbench/tools` 不传 `permissions` 仍返回 200 并创建 `ToolAsset`。
- `POST /v0/workbench/tool-registration-requests` 不传 `permissions` 仍返回 200 并创建 `ToolRegistrationRequest`。
- CLI `workbench invite-runner` 不传 `--permission` 仍返回 0 并创建邀请。
- 上述缺权限场景没有 `workbench.permission.denied` 审计。

## Acceptance Criteria

1. API 四个工作台写入口缺少 `permissions` 或权限不足时必须拒绝写入。
2. CLI 四个工作台写命令缺少 `--permission` 或权限不足时必须拒绝写入。
3. 拒绝写入必须产生 `workbench.permission.denied` AuditLog。
4. 正向权限、审批状态、幂等、只读监管、旧 Agent Ring 兼容必须不回归。
5. 新增或更新测试覆盖缺权限 API/CLI 场景。

## Suggested Checks

- `python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes`
- 新增 API missing-permission tests。
- 新增 CLI missing-permission tests。
- `python3 -m unittest tests.test_cli`
- `python3 -m unittest tests.test_desktop_workbench_slice0`
- `python3 scripts/validate_desktop_workbench_slice0.py`
