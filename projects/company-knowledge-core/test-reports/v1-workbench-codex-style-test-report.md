---
type: Workflow
title: V1 工作台 Codex 风格中文测试验收报告
timestamp: "2026-06-22T06:21:02Z"
taskId: kt-v1-workbench-codex-style-test
executorAgent: agent.company.test
result: passed
decision: accepted
regressionRound: 3
handoffTo: agent.company.product-manager
---

# V1 工作台 Codex 风格中文测试验收报告

## 结论

第 3 轮回归结论：`passed / accepted`。

Product final acceptance 发现的详情区 raw status DOM 缺陷已关闭。`workbench-shell.js` 的通用详情 `<dd>` 已统一走 `displayValue()`，`offline`、`done`、`retried`、`escalated`、`accepted`、`required` 等 status-like 原值不再以 `<dd>offline</dd>`、`<dd>done</dd>` 或同类裸值出现在渲染 DOM。

V1 单机闭环工作台验收矩阵第 3 轮复跑通过：真实 read model、中文可读、Codex 风格、设备路由、Agent 状态、任务流转、Runner/lease/heartbeat、审批权限、异常恢复、安全只读 fallback、证据完整性均保持通过。

是否允许产品最终验收：允许。交给 `agent.company.product-manager` 做最终产品验收。

## 覆盖矩阵

| 来源要求 | 验收点 | 实现/证据位置 | 第 3 轮测试方式 | 结果 |
|---|---|---|---|---|
| PRD V1 单机闭环 | 多 Agent 会话、Local Router、组 Agent 调度闭环可见。 | `workbench-live-read-model.js`；首页、运行监控、项目、Agent、Runner、验收页。 | validator；unittest；DOM renderer。 | pass |
| PRD 本机通信 | 设备、会话、消息保留 `device.local`、`routeType`、`targetDeviceId`。 | `devices`、`agentSessions`、`agentMessages`。 | read model 校验；DOM 渲染校验。 | pass |
| PRD 任务闭环 | 任务分派、执行、上报、汇总、确认、沉淀可追溯。 | `taskFlow`、`taskResults`、`acceptanceEvidence`。 | validator；结果中心 DOM 校验。 | pass |
| Agent 角色边界 | Agent 页显示岗位职责，不由主线程代签岗位结论。 | `agent-team-manager`、role label mapping、TaskResult 提示。 | unittest；DOM 文本校验。 | pass |
| Runner 执行事实 | Runner/lease/heartbeat/scope audit/stale/failed 可见。 | `runnerLeases`、`runnerHistory`、`agent-ring-console`。 | validator；DOM 渲染校验。 | pass |
| 审批权限 | 审批、权限动作、审计引用独立于验收展示。 | `approvals`、`permissionGatedActions`、`review-center`。 | validator；DOM 渲染校验。 | pass |
| 异常恢复 | stale lease、failed runner、offline heartbeat、cancelled/rejected/blocked、安全只读 fallback 有恢复入口。 | `recovery`、`problemRunnerLeases`、`problemTasks`、`settingsSecurity`。 | validator；DOM 渲染校验。 | pass |
| 安全只读 fallback | read model 缺失/过期时不把缓存当当前事实。 | `staleStatePolicy`、`initializeWorkbench` fallback。 | 静态检查；validator。 | pass |
| 证据完整性 | 缺 `outputRefs`、`evidenceRefs`、`testsOrChecks`、`operatingRuleRefs`、`commonRulesEvaluation` 显式提示。 | `evidenceWarnings()`、`result-center`。 | unittest；DOM 渲染校验。 | pass |
| 中文可读/Codex 风格 | 状态、下一步、证据优先；内部 ID 次级展示。 | `statusText`、surface sections、card rendering。 | 状态字典扫描；DOM 渲染校验。 | pass |
| Product final acceptance DEFECT | 详情区不得显示 raw status `<dd>offline</dd>`、`<dd>done</dd>` 或同类裸值。 | `displayValue()`、`metaTemplate()`、`validate_shell_rendered_status_details()`、单测。 | 31 个 status-like 原值逐 surface DOM 扫描。 | pass |

## 命令结果

第 3 轮必跑命令结果：

- `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js`: pass, `EXIT=0`
- `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core`: pass, `desktop workbench slice0 artifacts: passed`
- `python3 -m unittest tests.test_desktop_workbench_slice0`: pass, `Ran 9 tests`, `OK`
- `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate`: pass, `valid`

第 3 轮专项 DOM 扫描：

```txt
readModels=2
surfaces=11
statusValues=31
rawDetailHits=0
offline: raw_dd=0, label='离线', label_dd=4
done: raw_dd=0, label='已关闭', label_dd=1
retried: raw_dd=0, label='重试已登记'
escalated: raw_dd=0, label='已升级处理'
accepted: raw_dd=0, label='已接受', label_dd=1
required: raw_dd=0, label='需服务端授权', label_dd=2
safe_fallback / waiting_runner / changes_requested / failed / blocked / cancelled / rejected: raw_dd=0
```

`git diff --check` 在报告更新后执行，见本报告后续 TaskResult 证据。

## 缺陷列表

### DEFECT-001：Runner 页历史状态英文直出

Status：closed in 第 2 轮回归。

首轮可见问题：Runner 历史 `retried`、`escalated` 英文直出，违反中文 Codex 风格和状态语义一致性。

关闭证据：

- `statusText.retried` = “重试已登记”。
- `statusText.escalated` = “已升级处理”。
- validator 从 base/live read model 收集状态并要求中文映射。
- 第 2 轮和第 3 轮必跑命令均通过。

### DEFECT-002：详情区 raw status DOM 直出

Status：closed in 第 3 轮回归。

产品最终验收发现：`home`、`agent-ring-console`、`quality-dashboard`、`recovery-center` 曾出现 `<dd>offline</dd>`，`result-center` 曾出现 `<dd>done</dd>`。

关闭证据：

- `metaTemplate()` 的 `<dd>` 现在使用 `displayValue(item.label, item.value)`。
- `displayValue()` 对所有已知 `statusText` 枚举值输出中文语义。
- `validate_shell_rendered_status_details()` 通过 Node VM 渲染 shell surfaces 并阻止 raw status detail DOM 复发。
- `tests.test_desktop_workbench_slice0` 新增详情 DOM 防回归单测，覆盖 `done/offline/accepted/required/retried/escalated`。
- 第 3 轮专项 DOM 扫描对 31 个 status-like 原值、11 个 surface 检查，`rawDetailHits=0`。

## Operating Rule Evaluation

| Rule | Result | Evidence |
|---|---:|---|
| 读取任务、岗位、公共规则、context pack | pass | 已读取任务单、产品终验、研发自测、研发 TaskResult、workbench shell/js/css/html、validator、单测、公共规则、Test Agent 规则和 context pack。 |
| 不修改研发代码 | pass | 本轮只更新测试报告；未修改 `desktop-workbench-slice0`、validator、单测或研发实现文件。 |
| 独立测试结论 | pass | 必跑命令、validator、unittest、CLI validate、专项 DOM 扫描均由 Test Agent 第 3 轮复跑。 |
| 缺陷处理 | pass | 本轮无新增缺陷；DEFECT-001 和 DEFECT-002 均关闭。 |
| TaskResult 证据完整 | pass | 测试报告、命令结果、DOM 扫描和 finish 生成 TaskResult 将作为验收证据。 |

## 验收路由

当前测试任务可标记通过。请交给 `agent.company.product-manager` 做产品最终验收。
