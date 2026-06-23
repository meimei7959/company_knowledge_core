---
type: TaskResult
title: Result for kt-v2-central-runner-observability-permission-gate-rework
description: Development rework result for Phase 2 workbench permission gate failure.
timestamp: "2026-06-23T02:40:27Z"
resultId: TR-kt-v2-central-runner-observability-permission-gate-rework
taskId: kt-v2-central-runner-observability-permission-gate-rework
projectId: company-knowledge-core
assignee: agent.company.development
taskRuntime: {"version":"task-runtime.v1","taskType":"engineering_action","category":"engineering","stage":"rework","qualityGate":"engineering","acceptancePath":"test_agent_review","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
runnerId: ""
executorAgent: agent.company.development
status: done
summary: 已修复工作台写入口权限门禁：API/CLI 创建项目、邀请电脑、登记低风险工具、提交高风险工具申请在缺少 permissions 或权限不足时拒绝写入，返回 permission denied，并写入 workbench.permission.denied AuditLog；拒绝审计包含 actor、targetRef、before/after、policyResult 和缺失权限详情。保持幂等、审批状态、只读监管、旧 Agent Ring 注册/心跳/领取/完成兼容。
outputRefs:
  - zhenzhi_knowledge/core.py
  - tests/test_cli.py
  - task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md
  - knowledge/audit/audit.20260623T024027Z-central-runner-observability-permission-gate-rework.md
knowledgeRefs: []
sourceMaterialRefs:
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md
  - projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md
  - task-results/tr-kt-v2-central-runner-observability-test.md
evidenceRefs:
  - tests/test_cli.py
  - knowledge/audit/audit.20260623T024027Z-central-runner-observability-permission-gate-rework.md
testsOrChecks:
  - boost python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_cli.CliTests.test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions (3 tests OK with localhost API route verification)
  - boost python3 -m unittest tests.test_cli (181 tests OK; skipped=11 in sandbox run)
  - boost python3 -m unittest tests.test_desktop_workbench_slice0 (13 tests OK)
  - boost python3 scripts/validate_desktop_workbench_slice0.py (passed)
  - PYTHONPYCACHEPREFIX=/private/tmp/company_knowledge_core_pycache python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py scripts/validate_desktop_workbench_slice0.py tests/test_cli.py tests/test_desktop_workbench_slice0.py (passed)
nextActions:
  - Test Agent rerun missing-permission API/CLI acceptance checks.
  - Test Agent rerun full local regression and confirm no direct execution-control mutation endpoint was introduced.
operatingRuleRefs: {"companyConstitution":"docs/agent-team/company-agent-constitution.md","taskRuntimeContract":"docs/agent-team/agent-task-runtime-contract.md","humanAcceptancePolicy":"docs/agent-team/human-acceptance-policy.md","commonRules":"docs/agent-team/common-agent-operating-rules.md","roleOperatingSpec":"docs/agent-team/role-operating-specs.json","roleRules":"agents/agent.company.development.md","projectRules":"projects/company-knowledge-core/project.md","testReport":"projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md","reworkTask":"projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md","testTaskResult":"task-results/tr-kt-v2-central-runner-observability-test.md"}
handoffContract: {"fromAgent":"agent.company.development","handoffTo":"agent.company.test","handoffSummary":"权限门禁返工已完成。请测试 Agent 复验 API/CLI 四类工作台写入口：缺 permissions、权限不足均拒绝；不创建对象；必须生成 workbench.permission.denied AuditLog；正向授权、幂等、审批状态、只读监管、旧 Agent Ring 兼容不回归。","requiredArtifacts":["permission gate re-test","API missing-permission report","CLI missing-permission report","audit denial evidence","full regression result"],"artifactRefs":["zhenzhi_knowledge/core.py","tests/test_cli.py","task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md"],"openRisks":["真实双机部署环境尚未验收。","真实 Tool Owner 审批回调尚未接入。","远程 API Gateway 权限、审计、并发幂等尚未 smoke。"],"nextSuggestedTask":"kt-v2-central-runner-observability-permission-gate-test","terminalReason":""}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"rulesRef":"docs/agent-team/common-agent-operating-rules.md","checkedRules":["source_docs_loaded","role_boundary_respected","root_cause_fixed","audit_log_created","tests_run","handoff_contract"],"reasons":[],"ruleIssueRequired":false}
qualityEvaluation: {"type":"AgentResultEvaluation","status":"passed_local_tests","passed":true,"decision":"handoff_ready","score":94,"attemptNumber":2,"maxAttempts":3,"retryable":false,"reasons":["Permission gate root cause fixed in shared core helper and covered by API/CLI missing-permission regression tests."],"nextOwnerAgent":"agent.company.test"}
acceptancePolicy: {"version":"acceptance.v1","acceptanceStatus":"waiting_acceptance","humanAcceptanceRequired":true,"acceptanceRequiredByDefault":true,"projectManager":"agent.company.project-manager","humanReviewer":"meimei","decidedBy":"","decisionReason":"Rework complete; requires Test Agent acceptance of permission-denied behavior and audit evidence.","acceptedBy":"","acceptedAt":"","rejectedBy":"","rejectedAt":"","requiresNextTaskCreation":true}
improvementRefs: []
evalCaseRefs: []
followupTaskRefs:
  - kt-v2-central-runner-observability-permission-gate-test
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs:
  - knowledge/audit/audit.20260623T024027Z-central-runner-observability-permission-gate-rework.md
completedAt: "2026-06-23T02:40:27Z"
---

## Summary

返工已完成。根因是 `_permission_decision` 在 `permissions is None` 时默认把 required permissions 视为已授予，导致 API/CLI 不传权限也能创建工作台登记对象。现已改为工作台写入口必须显式传入所需权限；缺少或不足时先审计再拒绝，且拒绝发生在幂等命中和对象创建之前。

## Changed Files

- `zhenzhi_knowledge/core.py`：修正 `_permission_decision` 默认授权漏洞；拒绝审计写入 `before=not_created`、`after=denied`、`policyResult=permission_denied` 和缺失权限详情；四个工作台写入口先做权限门禁再处理幂等和创建。
- `tests/test_cli.py`：新增 `test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions`，覆盖 API/CLI 创建项目、邀请电脑、登记低风险工具、提交高风险工具申请的缺权限拒绝、无对象创建、拒绝审计。
- `task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md`：本返工 TaskResult。
- `knowledge/audit/audit.20260623T024027Z-central-runner-observability-permission-gate-rework.md`：返工提交审计。

## Behavior After Fix

- `POST /v0/workbench/projects` 缺 `permissions=["project.create"]`：400，`permission denied`，无 Project 创建，生成 `workbench.permission.denied`。
- `POST /v0/workbench/runner-invitations` 缺 `permissions=["runner.invitation.create"]`：400，无 RunnerInvitation 创建，生成拒绝审计。
- `POST /v0/workbench/tools` 缺 `permissions=["tool.register.low_risk"]`：400，无 ToolAsset 创建，生成拒绝审计。
- `POST /v0/workbench/tool-registration-requests` 缺 `permissions=["tool.registration_request.create"]`：400，无 ToolRegistrationRequest 创建，生成拒绝审计。
- 对应 CLI `workbench create-project`、`invite-runner`、`register-tool`、`request-tool` 缺 `--permission`：非 0 退出，stderr 包含 `permission denied`，不创建对象，生成拒绝审计。

## Test Results

- `boost python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_cli.CliTests.test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions`：3 tests OK。第一次 sandbox socket 限制导致 API 测试 skip，随后以本机 socket 权限重跑通过。
- `boost python3 -m unittest tests.test_cli`：181 tests OK，skipped=11。
- `boost python3 -m unittest tests.test_desktop_workbench_slice0`：13 tests OK。
- `boost python3 scripts/validate_desktop_workbench_slice0.py`：passed。
- `PYTHONPYCACHEPREFIX=/private/tmp/company_knowledge_core_pycache python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py scripts/validate_desktop_workbench_slice0.py tests/test_cli.py tests/test_desktop_workbench_slice0.py`：passed。原始 `py_compile` 试图写 `~/Library/Caches/com.apple.python`，被沙箱拒绝；改用 `/private/tmp` pycache 后通过。

## Remaining Gaps

- 未做真实双机部署验证：runner 邀请、注册、审批、心跳、只读监管仍需测试 Agent 或部署验收补跑。
- 未接真实 API Gateway 权限系统；当前为本地 payload permissions 语义门禁。
- 未接真实 Tool Owner 审批回调。
- 未做并发缺权限/幂等压测。

## Acceptance Focus For Test Agent

- 对四个 API 写入口分别测：无 `permissions`、空数组、错误权限、正确权限。
- 对四个 CLI 写命令分别测：缺 `--permission`、错误 `--permission`、正确 `--permission`。
- 检查拒绝场景不创建对象，只新增 `workbench.permission.denied` AuditLog。
- 检查拒绝审计 frontmatter：`actor`、`targetRef`、`before=not_created`、`after=denied`、`policyResult=permission_denied`。
- 检查授权正向链路：对象创建、幂等重复、审批状态、通知、正常审计仍正确。
- 检查旧 Agent Ring `/v0/runners/register` 兼容、heartbeat、claim、finish 不回归。
