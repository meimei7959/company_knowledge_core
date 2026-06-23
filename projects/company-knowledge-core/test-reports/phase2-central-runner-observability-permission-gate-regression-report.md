---
type: EvalRun
title: Phase 2 Central Runner Observability Permission Gate Regression Report
taskId: kt-v2-central-runner-observability-test-regression
executorAgent: agent.company.test
status: done
date: 2026-06-23
---

# Phase 2 中枢 Runner 观测登记入口权限门禁回归报告

## 结论

本地回归通过。研发返工修复了上次阻断项：四个工作台写入口在缺少 `permissions` 或权限不足时拒绝写入，返回 permission denied，并写入 `workbench.permission.denied` 审计；未创建登记对象。有权限时登记语义正常；旧 Agent Ring `/v0/runners/register` 兼容；执行监管 read model 仍只读。

保留残余风险：本次仍是本地临时 bundle 与静态工作台回归，未连接真实远程 Gateway、真实审批回调或双机 Runner 环境。

## 已读取材料

- `task-results/tr-kt-v2-central-runner-observability-permission-gate-rework.md`
- `knowledge/audit/audit.20260623T024027Z-central-runner-observability-permission-gate-rework.md`
- `projects/company-knowledge-core/test-reports/phase2-central-runner-observability-test-report.md`

## 回归范围

- 四个 API 工作台写入口缺权限拒绝与审计。
- 四个 CLI 工作台写命令缺权限拒绝与审计。
- 权限不足场景拒绝与审计。
- 正向授权登记语义。
- 旧 Agent Ring `/v0/runners/register`。
- 工作台执行监管只读。
- 研发声明测试、全量 CLI 回归、桌面工作台静态回归、py_compile。

## 重点复验结果

### 缺权限必须拒绝

独立黑盒 API 复验：

```txt
api_missing [('project', 400, 'Error', True), ('invite', 400, 'Error', True), ('tool', 400, 'Error', True), ('toolRequest', 400, 'Error', True)]
api_wrong [('project', 400, 'Error', True), ('invite', 400, 'Error', True), ('tool', 400, 'Error', True), ('toolRequest', 400, 'Error', True)]
```

独立黑盒 CLI 复验：

```txt
cli_missing [('create-project', 2, True, False), ('invite-runner', 2, True, False), ('register-tool', 2, True, False), ('request-tool', 2, True, False)]
```

结论：通过。API 缺失/错误权限均 400；CLI 缺权限均非 0；stderr/body 包含 permission denied。

### 拒绝必须审计且不创建对象

独立黑盒复验：

```txt
denied_audit_count 12
denied_audit_shape_ok True
sample [('user.meimei', 'projects/api-denied/project.md', 'not_created', 'denied', 'permission_denied'), ('system.workbench', 'runner-invitations/api-denied.api-denied-runner.md', 'not_created', 'denied', 'permission_denied')]
denied_objects {'apiDeniedProjectExists': False, 'cliDeniedProjectExists': False, 'deniedInvitationFiles': [], 'deniedToolFiles': [], 'deniedToolRequestFiles': []}
```

结论：通过。拒绝审计包含 actor、targetRef、before=`not_created`、after=`denied`、policyResult=`permission_denied`。拒绝场景未创建 project、runner invitation、tool、tool registration request 对象。

### 有权限时按登记语义创建

独立黑盒 API 正向复验：

```txt
api_positive [(200, 'WorkbenchProject', 'auto_approved'), (200, 'RunnerInvitation', 'auto_approved'), (200, 'ToolAsset', 'auto_approved'), (200, 'ToolRegistrationRequest', 'pending_review')]
```

独立黑盒 CLI 正向复验：

```txt
cli_positive [('create-project', 0, 'WorkbenchProject', 'auto_approved'), ('invite-runner', 0, 'RunnerInvitation', 'auto_approved'), ('register-tool', 0, 'ToolAsset', 'auto_approved'), ('request-tool', 0, 'ToolRegistrationRequest', 'pending_review')]
```

结论：通过。低风险登记 auto approved，高风险工具申请 pending review，符合登记/审批语义。

### 旧 Agent Ring register 兼容

独立黑盒复验：

```txt
old_ring_register 200 RunnerRegistrationResult auto_approved ['api-ok']
```

结论：通过。旧 `/v0/runners/register` 使用配对码注册成功，未要求 workbench 权限参数。

### 执行监管仍只读

独立黑盒复验：

```txt
read_model 200 True {'dispatchTask': False, 'repairTask': False, 'overwriteTaskResult': False, 'editAgentRun': False, 'forceCompleteTask': False, 'claimAsWorkbench': False}
```

结论：通过。未开放派单、修复、覆盖结果、编辑 AgentRun、强制完成或工作台领取任务入口。

## 自动化回归

| Check | Result |
| --- | --- |
| `boost python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_cli.CliTests.test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions tests.test_desktop_workbench_slice0.DesktopWorkbenchSlice0Tests` | passed, 16 tests OK |
| `boost python3 -m unittest tests.test_cli` | passed, 181 tests OK |
| `boost python3 -m unittest tests.test_desktop_workbench_slice0` | passed, 13 tests OK |
| `boost python3 scripts/validate_desktop_workbench_slice0.py` | passed |
| `PYTHONPYCACHEPREFIX=/private/tmp/company_knowledge_core_pycache boost python3 -m py_compile ...` | passed |

## 交接命令差异

研发 TaskResult 中写的目标测试名为 `test_phase2_workbench_permission_gate_rejects_api_and_cli_without_permissions`，实际测试名是 `test_phase2_workbench_permission_gate_rejects_api_and_cli_missing_permissions`。错误 selector 会产生 `AttributeError`；正确 selector 已通过。此为交接记录瑕疵，不影响代码回归结论。

## 最终判断

通过本地回归，可交给项目经理/产品验收继续判断。最终上线前仍建议补跑真实远程 Gateway、真实审批回调、真实双机 Runner 注册/心跳/只读监管链路。
