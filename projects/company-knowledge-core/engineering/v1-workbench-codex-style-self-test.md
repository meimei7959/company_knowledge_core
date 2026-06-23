---
type: Workflow
title: V1 工作台 Codex 风格研发自测结果
projectId: company-knowledge-core
taskId: kt-v1-workbench-codex-style-dev
agentId: agent.company.development
status: submitted
createdAt: "2026-06-22"
sourceRefs:
  - projects/company-knowledge-core/engineering/v1-workbench-codex-style-implementation-plan.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
  - scripts/validate_desktop_workbench_slice0.py
  - tests/test_desktop_workbench_slice0.py
---

# V1 工作台 Codex 风格研发自测结果

## 结论

研发自测通过。Product final acceptance defect fixed：详情区、卡片、列表中 status-like raw value 不再以 `<dd>offline</dd>`、`<dd>done</dd>` 形式直出。此结论仅代表研发 Agent 的技术自测，不替代测试 Agent、产品 Agent 或 PM 最终验收。

## 命令结果

| 命令 | 结果 |
| --- | --- |
| `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js` | pass |
| `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core` | pass：`desktop workbench slice0 artifacts: passed` |
| `python3 -m unittest tests.test_desktop_workbench_slice0` | pass：8 tests |
| `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` | pass：`valid` |
| `git diff --check -- <touched files>` | pass |

## 覆盖点

- 接真实 `workbench-live-read-model.js`，`runtimeReadModelKind=real-v1-runtime-read-model`，`fixture=false`。
- 中文 Codex 风格 shell 覆盖总览、运行监控、项目、Agent、Runner、验收、审批/权限、异常恢复。
- `submitted` 显示为“已提交，待评审”，不写成已验收。
- 权限/审批独立显示 `serverGate`、`permission`、`idempotencyKey`、`auditRef`。
- TaskResult 证据缺失显式提示 `outputRefs`、`evidenceRefs`、`testsOrChecks`、`operatingRuleRefs`、`commonRulesEvaluation`。
- V1 只有 `device.local`，但消息、设备、会话仍展示 `routeType`、`targetDeviceId`、`deviceId`。
- 异常恢复覆盖 stale lease、failed runner、offline heartbeat、cancelled/rejected/blocked、通知异常和 safe fallback。

## 已处理的验证问题

首轮 `zhenzhi_knowledge validate` 发现相关文档使用当前 schema 未登记类型：`DesignArtifact`、`ProductReview`、`EngineeringPlan`。已将本任务相关设计文件和实现方案文件调整为已支持类型，正文和决策内容未变。

## 第 2 轮返修自测

DEFECT-001 fixed：Runner 历史状态不再把 `retried`、`escalated` 作为英文状态直出。

- `workbench-shell.js` 补齐 live/base read model 已出现状态的中文映射：`retried` 显示为“重试已登记”，`escalated` 显示为“已升级处理”，并补齐 `waiting_runner`、`changes_requested`、`processing` 等同类状态。
- `workbench-shell.css` 补齐新增状态的视觉分组，避免新增状态只落到默认样式。
- `scripts/validate_desktop_workbench_slice0.py` 增加 read model 状态到 `statusText` 中文映射的覆盖检查，缺失映射或英文 fallback 会失败。
- `tests/test_desktop_workbench_slice0.py` 增加 `retried`、`escalated` 中文语义断言和全量状态映射 validator 断言。

第 2 轮命令结果：

| 命令 | 结果 |
| --- | --- |
| `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js` | pass |
| `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core` | pass：`desktop workbench slice0 artifacts: passed` |
| `python3 -m unittest tests.test_desktop_workbench_slice0` | pass：8 tests |
| `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` | pass |
| `git diff --check -- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css scripts/validate_desktop_workbench_slice0.py tests/test_desktop_workbench_slice0.py` | pass |

研发结论：DEFECT-001 技术修复和防回归检查已完成，交给 `agent.company.test` 回归；研发 Agent 不替测试或产品下最终结论。

## 第 3 轮返修自测

Product final acceptance defect fixed：产品最终验收发现的详情区 raw status DOM 输出已系统性修复。

- `workbench-shell.js` 新增统一详情值格式化：`metaTemplate` 的 `<dd>` 不再直接输出 `item.value`，而是对所有已知状态枚举走 `statusText` 中文语义映射；覆盖 `heartbeat=offline`、`taskStatus=done`、`acceptanceStatus=accepted`、`serverGate=required` 等 status-like 值。
- `workbench-shell.js` 同步将可见状态上下文文案改为中文，例如“过期租约、失败 Runner、离线心跳”和“已关闭、已驳回、已取消、阻塞”。
- `scripts/validate_desktop_workbench_slice0.py` 新增 Node VM DOM 渲染检查，逐 surface 扫描并阻止 `<dd>offline</dd>`、`<dd>done</dd>`、`<dd>retried</dd>`、`<dd>escalated</dd>` 等 raw status detail DOM 复发。
- `tests/test_desktop_workbench_slice0.py` 新增详情 DOM 防回归单测，并覆盖 `done/offline/accepted/required/retried/escalated` 中文映射。

第 3 轮命令结果：

| 命令 | 结果 |
| --- | --- |
| `node --check projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js` | pass |
| `python3 scripts/validate_desktop_workbench_slice0.py /Users/meimei/Documents/company_knowledge_core` | pass：`desktop workbench slice0 artifacts: passed` |
| `python3 -m unittest tests.test_desktop_workbench_slice0` | pass：9 tests |
| `python3 -m zhenzhi_knowledge --root /Users/meimei/Documents/company_knowledge_core validate` | pass：`valid` |
| `git diff --check -- projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js scripts/validate_desktop_workbench_slice0.py tests/test_desktop_workbench_slice0.py projects/company-knowledge-core/engineering/v1-workbench-codex-style-self-test.md task-results/tr-kt-v1-workbench-codex-style-dev.md` | pass |

研发结论：Product final acceptance defect fixed，详情 DOM raw status 防回归检查已进入 validator 和单测；交给 `agent.company.test` 回归，研发 Agent 不替测试或产品下最终结论。
