---
type: TaskResult
title: Result for kt-v2-central-runner-observability-test-regression
description: Regression acceptance result for Phase 2 central runner observability permission gate rework.
timestamp: "2026-06-23T02:45:09Z"
resultId: TR-kt-v2-central-runner-observability-test-regression
taskId: kt-v2-central-runner-observability-test-regression
projectId: company-knowledge-core
assignee: agent.company.test
taskRuntime: {"version":"task-runtime.v1","taskType":"testing_acceptance","category":"testing","stage":"regression","qualityGate":"test_agent_acceptance","acceptancePath":"project_manager_or_product_acceptance","requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":true}
runnerId: ""
executorAgent: agent.company.test
status: done
summary: 权限门禁返工本地回归通过：API/CLI 四类工作台写入口缺 permissions 或权限不足均拒绝且写 workbench.permission.denied 审计；有权限时登记语义正常；旧 /v0/runners/register 兼容；执行监管 read model 仍只读。真实远程 Gateway、审批回调、双机 Runner 环境仍未在本次回归中执行。
outputRefs:
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-permission-gate-regression-report.md
  - task-results/tr-kt-v2-central-runner-observability-test-regression.md
sourceMaterialRefs:
  - task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md
  - knowledge/audit/audit.20260623T024027Z-central-runner-observability-permission-gate-rework.md
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md
evidenceRefs:
  - tests/test_cli.py
  - tests/test_desktop_workbench_slice0.py
  - scripts/validate_desktop_workbench_slice0.py
  - projects/company-knowledge-core/test-reports/phase2-central-runner-observability-permission-gate-regression-report.md
  - knowledge/audit/audit.20260623T024509Z-central-runner-observability-test-regression.md
testsOrChecks:
  - boost python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_cli.CliTests.test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions tests.test_desktop_workbench_slice0.DesktopWorkbenchSlice0Tests (16 tests OK)
  - boost python3 -m unittest tests.test_cli (181 tests OK)
  - boost python3 -m unittest tests.test_desktop_workbench_slice0 (13 tests OK)
  - boost python3 scripts/validate_desktop_workbench_slice0.py (passed)
  - PYTHONPYCACHEPREFIX=/private/tmp/company_knowledge_core_pycache boost python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py scripts/validate_desktop_workbench_slice0.py tests/test_cli.py tests/test_desktop_workbench_slice0.py (passed)
  - Independent blackbox API/CLI permission regression (passed)
operatingRuleRefs: {"companyConstitution":"docs/agent-team/company-agent-constitution.md","taskRuntimeContract":"docs/agent-team/agent-task-runtime-contract.md","humanAcceptancePolicy":"docs/agent-team/human-acceptance-policy.md","commonRules":"docs/agent-team/common-agent-operating-rules.md","roleOperatingSpec":"docs/agent-team/role-operating-specs.json","roleRules":"agents/agent.company.test.md","projectRules":"projects/company-knowledge-core/project.md","reworkTaskResult":"task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md","previousTestReport":"projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md"}
handoffContract: {"fromAgent":"agent.company.test","handoffTo":"agent.company.project-manager","handoffSummary":"权限门禁返工本地回归通过。可进入项目经理/产品验收；真实远程 Gateway、审批回调、双机 Runner 环境仍建议补跑。","requiredArtifacts":["regression report","TaskResult","audit log"],"artifactRefs":["projects/company-knowledge-core/test-reports/phase2-central-runner-observability-permission-gate-regression-report.md","task-results/tr-kt-v2-central-runner-observability-test-regression.md"],"openRisks":["未连接真实远程 knowledge-api Gateway。","未验证真实 Tool Owner 审批回调。","未验证两台真实电脑同时接入同一中枢。"],"nextSuggestedTask":"","terminalReason":"passed_with_remote_gap"}
commonRulesEvaluation: {"version":"common-agent-rules.v1","status":"passed","passed":true,"rulesRef":"docs/agent-team/common-agent-operating-rules.md","checkedRules":["source_docs_loaded","role_boundary_respected","no_code_fix_by_test_agent","tests_run","audit_log_created","task_result_written"],"reasons":[],"ruleIssueRequired":false}
qualityEvaluation: {"type":"AgentResultEvaluation","status":"done","passed":true,"decision":"handoff_ready","score":94,"attemptNumber":2,"maxAttempts":3,"retryable":false,"reasons":["Local API/CLI permission gate regression passed.","Positive registration semantics, old runner registration, and read-only supervision passed.","Remote Gateway, approval callback, and real dual-runner verification remain as documented residual risks."],"nextOwnerAgent":"agent.company.project-manager"}
acceptancePolicy: {"version":"acceptance.v1","acceptanceStatus":"accepted","humanAcceptanceRequired":true,"acceptanceRequiredByDefault":true,"projectManager":"agent.company.project-manager","humanReviewer":"meimei","decidedBy":"agent.company.test","decisionReason":"Rework fixed local permission gate failure; test agent accepts local regression while recording that remote deployment evidence remains outside this regression run.","acceptedBy":"agent.company.test","acceptedAt":"2026-06-23T02:45:09Z","rejectedBy":"","rejectedAt":"","requiresNextTaskCreation":false}
improvementRefs: []
evalCaseRefs: []
followupTaskRefs: []
guideUpdateRequired: false
guideUpdated: false
guideRef: ""
guideFeishuUrl: ""
guideRevision: ""
guideAuditRefs:
  - knowledge/audit/audit.20260623T024509Z-central-runner-observability-test-regression.md
completedAt: "2026-06-23T02:45:09Z"
---

## Summary

权限门禁返工本地回归通过。上次阻断问题已修复：API/CLI 工作台写入口缺权限不再创建对象，且写入 `workbench.permission.denied` 审计。

## Regression Evidence

- API missing permissions: four workbench write routes returned 400 and permission denied.
- API wrong permissions: four workbench write routes returned 400 and permission denied.
- CLI missing permissions: four workbench commands returned non-zero and permission denied.
- Denied audit count: 12; audit shape includes actor, targetRef, before=`not_created`, after=`denied`, policyResult=`permission_denied`.
- Positive API/CLI registrations passed.
- Old `/v0/runners/register` returned `RunnerRegistrationResult` with `auto_approved`.
- Execution read model stayed read-only.

## Notes

R&D handoff listed one stale test selector ending in `without_permissions`; actual test name ends in `missing_permissions`. Correct selector passed.
