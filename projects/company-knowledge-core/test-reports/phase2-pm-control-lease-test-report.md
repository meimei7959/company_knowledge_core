---
type: EvalRun
title: Phase 2 PM Control Lease Test Report
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-test
testerAgent: agent.company.test
status: done
decision: accepted
createdAt: "2026-06-23T03:45:00Z"
sourceRefs:
  - task-results/tr-kt-v2-pm-control-lease-development.md
  - docs/product/ai-native-os/phase-2-pm-control-lease-prd.md
  - projects/company-knowledge-core/technical-solutions/phase2-pm-control-lease-technical-solution.md
  - projects/company-knowledge-core/product-reviews/phase2-pm-control-lease-architecture-product-review.md
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-test.md
evidenceRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - zhenzhi_knowledge/cli.py
  - tests/test_cli.py
  - tests/test_desktop_workbench_slice0.py
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
---

# Phase 2 PM Control Lease Test Report

## 结论

验收通过。研发结果满足“同一项目多电脑 PM 主控租约”的本地可验证范围：同一项目单主控、协同/备用无有效租约写入拒绝并审计、主控带租约写成功、项目不匹配/旧 fencing token/过期租约拒绝、接管记录、工作台展示、Runner/登记入口回归均已覆盖。

不创建研发返工任务。当前唯一未完全实跑项是 HTTP API socket 路由用例：沙箱禁止本地 socket bind，提权重跑又被审批额度拦截。代码检查和测试定义显示 API 路由已接入 core guard，但真实 HTTP 路径仍建议在非沙箱或部署验收环境补跑。

## 读取材料

- 已读 `task-results/tr-kt-v2-pm-control-lease-development.md`。
- 已读 `docs/product/ai-native-os/phase-2-pm-control-lease-prd.md`。
- 已读 `projects/company-knowledge-core/technical-solutions/phase2-pm-control-lease-technical-solution.md`。
- 已读 `projects/company-knowledge-core/product-reviews/phase2-pm-control-lease-architecture-product-review.md`。
- 已读 `projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-test.md`。

## 验收矩阵

| 验收项 | 结果 | 证据 |
| --- | --- | --- |
| 同一项目单主控 PM | 通过 | `acquire_pm_control_lease` 在已有 active lease 时拒绝；临时 harness 验证第二个 PM acquire 得到 `pm_control_lease_already_active`。 |
| 协同/备用 PM 无租约写入拒绝并审计 | 通过 | `validate_pm_control_lease_for_write` 和 `deny_pm_control_lease_write` 写 `pm_control_lease.denied`；测试和 harness 验证无目标 task 写入。 |
| 主控带租约写成功 | 通过 | `create_project_task` 写入 `pmControlLeaseId`、`pmControlFencingToken`、`pmControlPrimaryPm`；测试和 harness 通过。 |
| 过期租约拒绝 | 通过 | 临时 harness 构造过期 active lease，写入返回 `pm_control_lease_expired`，目标 task 不存在，审计存在。 |
| 非主控拒绝 | 通过 | `tests.test_cli.CliTests.test_pm_control_lease_core_guard_takeover_and_read_model` 验证 collaborator 写入返回 `pm_control_lease_not_primary`。 |
| 项目不匹配拒绝 | 通过 | 测试和 harness 验证项目 A lease 写项目 B 返回 `pm_control_lease_project_mismatch`，项目 B 不写 task。 |
| 旧 fencing token 拒绝 | 通过 | 接管后旧主控写入被拒绝；harness 验证无目标 task。 |
| 接管记录 | 通过 | `takeover_pm_control_lease` 生成 `PmLeaseTakeoverRecord` 和 `pm_control_lease.taken_over` audit；read model 展示 takeover records。 |
| 工作台展示主控/协同/备用/租约健康/接管记录 | 通过 | `pm_control_lease_read_model`、TS 类型、DOM 测试通过；`test_phase2_pm_control_read_model_and_dom_are_user_readable` 通过。 |
| Runner/登记入口不回归 | 通过 | workbench/Runner regression 窄集通过；全量 unittest 通过。 |
| API route live path | 环境限制 | API route 测试在当前沙箱跳过：`socket bind not allowed in sandbox`；提权重跑被审批额度拦截。 |

## 运行测试

- `boost python3 -m unittest -v tests.test_cli.CliTests.test_pm_control_lease_core_guard_takeover_and_read_model tests.test_cli.CliTests.test_pm_control_lease_api_routes_and_protected_task_create tests.test_cli.CliTests.test_pm_control_lease_cli_commands_and_task_flags tests.test_desktop_workbench_slice0.DesktopWorkbenchSlice0Tests.test_phase2_pm_control_read_model_and_dom_are_user_readable`
  - 结果：通过，4 tests，1 skipped。
  - skip 原因：API route test 需要绑定本地 socket，当前沙箱返回 `Operation not permitted`。
- `boost python3 -m unittest discover -s tests -p 'test*.py'`
  - 结果：通过，222 tests，13 skipped。
- `boost python3 -m unittest -v tests.test_desktop_workbench_slice0 tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_cli.CliTests.test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions tests.test_cli.CliTests.test_scheduler_workbench_read_model_exposes_queue_runner_lease_and_evidence_policy tests.test_cli.CliTests.test_agent_ring_console_lifecycle_cli_and_workbench_evidence`
  - 结果：通过，19 tests，2 skipped。
  - skip 原因：两个 workbench API socket tests 被沙箱禁止本地 bind。
- 临时验收 harness：
  - 结果：`ACCEPTANCE_HARNESS_PASS`。
  - 覆盖：第二主控 acquire 拒绝、备用无租约拒绝、主控租约写成功、项目不匹配拒绝、旧 fencing token 拒绝、过期租约拒绝、拒绝/接管审计存在。

## 代码检查摘要

- `validate_pm_control_lease_for_write` 是 core 权威 guard，覆盖缺字段、租约不存在、项目不匹配、状态/过期、非主控、旧 fencing token、source channel、权限/能力。
- `deny_pm_control_lease_write` 在抛出 `PMControlLeaseError` 前写 `pm_control_lease.denied` audit，带项目、请求 PM、当前主控、动作、原因、来源、target 等详情。
- `create_project_task` 和 `set_project_task_status` 在 PM 上下文存在时先调用 guard，再写业务对象。
- `takeover_pm_control_lease` 标记旧 lease `taken_over`、生成新 lease、写 takeover record 和 audit。
- `pm_control_lease_read_model` 聚合 current lease、participants、takeover records、denial summaries、health explanation。
- `server.py` 和 `cli.py` 已暴露 PM lease acquire/heartbeat/release/takeover/status 与 protected task create/start flags。

## 残余风险

- 当前环境未能实跑真实 HTTP server route，因为 socket bind 被沙箱禁止，提权重跑被审批额度拦截。建议部署验收或本机非沙箱环境补跑 API route tests。
- 真实多电脑共享存储/并发 acquire 仍未由本次本地验收直接证明；研发结果已记录此部署风险。本次验收确认本地 lifecycle、guard、audit、CLI、workbench 和 Runner 回归。

## 返工判断

无研发返工任务。未发现实现失败；API live path 是测试环境限制，不是代码失败。
