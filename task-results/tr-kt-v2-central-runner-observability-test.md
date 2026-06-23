---
type: TaskResult
title: Result for kt-v2-central-runner-observability-test
description: Test acceptance result for Phase 2 central runner observability option 2.
timestamp: "2026-06-23T02:34:03Z"
resultId: TR-kt-v2-central-runner-observability-test
taskId: kt-v2-central-runner-observability-test
projectId: company-knowledge-core
assignee: agent.company.test
taskRuntime: {"version":"task-runtime.v1","taskType":"testing_acceptance","category":"testing","qualityGate":"test_agent_acceptance","acceptancePath":"product_manager_after_rework","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
runnerId: ""
executorAgent: agent.company.test
status: changes_requested
summary: 本地 core/API/CLI/桌面静态工作台大部分正向链路通过，但 API/CLI 工作台写入口未强制业务权限语义；不传 permissions 仍可创建登记对象且无 workbench.permission.denied 审计，违反 PRD/技术方案/研发 TaskResult 验收口径。已创建研发返工任务。
outputRefs:
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md
  - task-results/tr-kt-v2-central-runner-observability-test.md
  - projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md
sourceMaterialRefs:
  - task-results/tr-kt-v2-central-runner-observability-development.md
  - docs/product/ai-native-os/phase-2-central-runner-observability-prd.md
  - projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md
  - projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md
evidenceRefs:
  - tests/test_cli.py
  - tests/test_desktop_workbench_slice0.py
  - scripts/validate_desktop_workbench_slice0.py
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md
  - knowledge/audit/audit.20260623T023403Z-central-runner-observability-test.md
testsOrChecks:
  - python3 -m unittest tests.test_cli (180 tests OK)
  - python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_desktop_workbench_slice0.DesktopWorkbenchSlice0Tests (15 tests OK)
  - python3 -m unittest tests.test_desktop_workbench_slice0 (13 tests OK)
  - python3 scripts/validate_desktop_workbench_slice0.py (passed)
  - python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py scripts/validate_desktop_workbench_slice0.py tests/test_cli.py tests/test_desktop_workbench_slice0.py (passed)
  - API missing-idempotency checks (passed: four workbench write routes returned 400)
  - API/CLI missing-permission checks (failed: write routes/commands created objects without permissions)
operatingRuleRefs: {"companyConstitution":"docs/agent-team/company-agent-constitution.md","taskRuntimeContract":"docs/agent-team/agent-task-runtime-contract.md","humanAcceptancePolicy":"docs/agent-team/human-acceptance-policy.md","commonRules":"docs/agent-team/common-agent-operating-rules.md","roleOperatingSpec":"docs/agent-team/role-operating-specs.json","roleRules":"agents/agent.company.test.md","projectRules":"projects/company-knowledge-core/project.md","productPrd":"docs/product/ai-native-os/phase-2-central-runner-observability-prd.md","technicalSolution":"projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md","workbenchDesign":"projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md"}
handoffContract: {"fromAgent":"agent.company.test","handoffTo":"agent.company.development","handoffSummary":"API/CLI 工作台写入口缺少强制权限语义；请研发返工并补测试。","requiredArtifacts":["permission gate fix","API missing-permission tests","CLI missing-permission tests","audit denial tests","updated development TaskResult"],"artifactRefs":["projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md","projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md"],"openRisks":["真实双机部署环境尚未验收。","真实 Tool Owner 审批回调尚未接入。","远程 API Gateway 权限/审计/并发幂等尚未 smoke。"],"nextSuggestedTask":"kt-v2-central-runner-observability-permission-gate-rework","terminalReason":"failed_needs_rework"}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"rulesRef":"docs/agent-team/common-agent-operating-rules.md","checkedRules":["source_docs_loaded","role_boundary_respected","no_code_fix_by_test_agent","tests_run","rework_task_created","audit_log_created"],"reasons":[],"ruleIssueRequired":false}
qualityEvaluation: {"type":"AgentResultEvaluation","status":"changes_requested","passed":false,"decision":"retry_required","score":72,"attemptNumber":1,"maxAttempts":3,"retryable":true,"reasons":["API/CLI workbench write entry points allow object creation without permissions and without permission-denied audit; test agent returned the work to development for rework."],"nextOwnerAgent":"agent.company.development"}
acceptancePolicy: {"version":"acceptance.v1","acceptanceStatus":"changes_requested","humanAcceptanceRequired":true,"acceptanceRequiredByDefault":true,"projectManager":"agent.company.project-manager","humanReviewer":"meimei","decidedBy":"agent.company.test","decisionReason":"Permission semantics are not enforced on workbench write entry points; test agent requested development rework.","acceptedBy":"","acceptedAt":"","rejectedBy":"agent.company.test","rejectedAt":"2026-06-23T02:34:03Z","requiresNextTaskCreation":true}
improvementRefs:
  - projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md
evalCaseRefs: []
followupTaskRefs:
  - kt-v2-central-runner-observability-permission-gate-rework
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs:
  - knowledge/audit/audit.20260623T023403Z-central-runner-observability-test.md
completedAt: "2026-06-23T02:34:03Z"
---

## Summary

本次验收未通过。正向登记链路、幂等键强制、只读监管、静态工作台中文展示和旧 Agent Ring 本地回归基本通过；阻断问题是 API/CLI 写入口缺少权限仍成功创建对象，且没有权限拒绝 AuditLog。

## Findings

- High: `POST /v0/workbench/projects`、`/v0/workbench/runner-invitations`、`/v0/workbench/tools`、`/v0/workbench/tool-registration-requests` 在缺少 `permissions` 时仍返回 200 并创建对象。
- High: CLI `workbench invite-runner` 不传 `--permission` 仍返回 0 并创建 `RunnerInvitation`。
- Medium: 真实双机、远程 Gateway 权限/审计/并发幂等、真实审批回调和桌面后端联调仍未执行。

## Verification

详见 `projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md`。

## Rework

已创建研发返工任务：`projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md`。
