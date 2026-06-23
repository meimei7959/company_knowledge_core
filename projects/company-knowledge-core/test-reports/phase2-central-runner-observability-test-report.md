---
type: EvalRun
title: Phase 2 Central Runner Observability Test Report
taskId: kt-v2-central-runner-observability-test
executorAgent: agent.company.test
status: changes_requested
date: 2026-06-23
---

# Phase 2 方案二中枢 Runner 观测与登记入口测试报告

## 结论

未通过，需研发返工。

本地 core/API/CLI/桌面静态工作台大部分正向链路通过：登记入口可创建对象，幂等键强制存在，重复请求返回同一对象，执行监管 read model 保持只读，桌面入口与中文展示校验通过，旧 Agent Ring 本地注册、心跳、领取、完成链路未在现有回归中发现回归。

阻断问题：工作台 API 与 CLI 写入口没有强制业务权限语义。调用方不传 `permissions` 时，创建项目、邀请电脑、登记低风险工具、提交高风险工具申请仍返回 200 并写入对象，且没有 `workbench.permission.denied` 审计。这违反 PRD 与研发 TaskResult 的验收口径：登记类写操作必须带权限语义、审批状态和 AuditLog；无权限必须拒绝并审计。

## 已读取材料

- `task-results/tr-kt-v2-central-runner-observability-development.md`
- `docs/product/ai-native-os/phase-2-central-runner-observability-prd.md`
- `projects/company-knowledge-core/technical-solutions/phase2-central-runner-observability-technical-solution.md`
- `projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md`

## 验收范围

- API/CLI/core 测试。
- 工作台登记入口。
- 执行监管只读边界。
- 中文可读展示。
- 模型、token、tool、Agent、电脑、项目、需求字段。
- 幂等。
- 权限、审批、审计。
- 旧 Agent Ring 兼容。

## 发现

### High: API 写入口缺少权限仍成功

受影响入口：

- `POST /v0/workbench/projects`
- `POST /v0/workbench/runner-invitations`
- `POST /v0/workbench/tools`
- `POST /v0/workbench/tool-registration-requests`

复验结果：

| 用例 | 实际结果 |
| --- | --- |
| 创建项目不传 `permissions` | 200, `WorkbenchProject` |
| 邀请电脑不传 `permissions` | 200, `RunnerInvitation` |
| 登记低风险工具不传 `permissions` | 200, `ToolAsset` |
| 提交高风险工具申请不传 `permissions` | 200, `ToolRegistrationRequest` |

审计结果只出现正常写入动作：`workbench.project.create`、`runner.invitation.create`、`tool.register`、`tool.registration_request.create`。没有 `workbench.permission.denied`。

期望：缺少权限声明或权限不足时，API 应拒绝写入，返回清晰错误，写入 `workbench.permission.denied` AuditLog，不创建登记对象。

### High: CLI 写命令缺少权限仍成功

复验命令形态：`zhenzhi-knowledge --root <tmp> workbench invite-runner --project cli-phase2 --runner-label Denied --actor user.meimei --idempotency-key cli-denied`

实际结果：命令返回 0，创建 `RunnerInvitation`，`approvalStatus=auto_approved`，无权限拒绝审计。

CLI 参数里 `--permission` 是可选参数；缺省未触发拒绝。工作台写命令应与 API 一致强制权限语义，至少对 create-project、invite-runner、register-tool、request-tool 强制传入并校验对应权限。

### Medium: 真实部署验收仍未完成

研发 TaskResult 已声明真实双机、远程 API Gateway 权限/审计/并发幂等、真实 Tool Owner 审批回调、桌面真实后端联调未覆盖。本次测试也只完成本地临时 bundle 与静态工作台验证，未连接 `http://124.221.138.151/knowledge-api` 或两台真实电脑。

此项不阻断本地代码返工，但阻断最终产品验收。

## 通过项

- `python3 -m unittest tests.test_cli`: 180 tests OK。
- 正确目标命令：`python3 -m unittest tests.test_cli.CliTests.test_phase2_workbench_registration_core_is_idempotent_audited_and_readonly tests.test_cli.CliTests.test_phase2_workbench_api_routes tests.test_desktop_workbench_slice0.DesktopWorkbenchSlice0Tests`: 15 tests OK。
- `python3 -m unittest tests.test_desktop_workbench_slice0`: 13 tests OK。
- `python3 scripts/validate_desktop_workbench_slice0.py`: passed。
- `python3 -m py_compile zhenzhi_knowledge/core.py zhenzhi_knowledge/server.py zhenzhi_knowledge/cli.py scripts/validate_desktop_workbench_slice0.py tests/test_cli.py tests/test_desktop_workbench_slice0.py`: passed。
- API 缺少 `idempotencyKey`：四个工作台写入口均 400，符合幂等键强制要求。
- API bad bearer token：只读 read model 返回 401，基础 API token 鉴权有效。
- 执行监管 read model：`readOnly=true`，`dispatchTask`、`repairTask`、`overwriteTaskResult`、`editAgentRun`、`forceCompleteTask`、`claimAsWorkbench` 均为 false。
- 工作台静态校验：五类登记入口可见，包括创建项目、邀请电脑、提交电脑注册申请、登记低风险工具、提交工具申请。
- 中文展示：静态校验覆盖状态中文、内部字段翻译、可见 DOM 不暴露原始路径/用户不友好字段；渲染层显示“所属需求”。
- 模型/token/tool/Agent/电脑/项目/需求：read model 与渲染层存在对应字段或标签；live read model 含 requirement 数据，shell 渲染“所属需求”。

## 未通过复验脚本摘要

API 权限缺口复验：

```txt
createdProject 200 WorkbenchProject auto_approved
('project-missing-permission', 200, 'WorkbenchProject', None)
('invite-missing-permission', 200, 'RunnerInvitation', None)
('tool-missing-permission', 200, 'ToolAsset', None)
('toolreq-missing-permission', 200, 'ToolRegistrationRequest', None)
auditSubset ['runner.invitation.create', 'tool.register', 'tool.registration_request.create', 'workbench.project.create']
```

CLI 权限缺口复验：

```txt
CMD_FAIL workbench invite-runner ... expected return 1, actual return 0
stdout kind=RunnerInvitation approvalStatus=auto_approved
auditActionsSubset ['runner.invitation.create', 'runner.pairing.consume', 'runner.register', 'tool.register', 'tool.registration_request.create', 'workbench.project.create']
```

## 返工要求

已创建研发返工任务：

- `projects/company-knowledge-core/tasks/kt-v2-central-runner-observability-permission-gate-rework.md`

返工完成前，不建议进入产品/人类最终验收。
