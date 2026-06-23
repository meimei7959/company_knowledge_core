---
type: ReviewRecord
title: V1 工作台用户可读文案产品复验
description: 产品经理 Agent 第 2 轮复验 V1 工作台中文文案、项目选择器、主 Agent 术语和路由链路表达。
timestamp: "2026-06-22T11:19:13Z"
projectId: company-knowledge-core
taskId: kt-v1-workbench-user-copy-polish-product-review
executorAgent: agent.company.product-manager
decision: accepted
status: submitted
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-v1-workbench-user-copy-polish-product-review.md
  - task-results/tr-kt-v1-workbench-user-copy-polish.md
  - task-results/tr-kt-v1-workbench-user-copy-polish-test.md
  - projects/company-knowledge-core/test-reports/v1-workbench-user-copy-polish-test-report.md
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.html
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.css
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
  - projects/company-knowledge-core/desktop-workbench-slice0/shared-frontend-foundation.ts
evidenceRefs:
  - scripts/validate_desktop_workbench_slice0.py
  - tests/test_desktop_workbench_slice0.py
  - "python3 scripts/validate_desktop_workbench_slice0.py: passed"
  - "python3 -m unittest tests/test_desktop_workbench_slice0.py: 10 tests OK"
---

## 结论

decision: accepted

第 2 轮产品复验通过。Development Agent 第 3 轮返修已经把用户截图中看不懂的问题收敛到可接受状态：顶部先说明当前项目，项目选择器显示中文项目名“真知公司知识核心”，工作台定位说明为“本机单机闭环工作台”，状态说明为只读，数据来源说明为中央状态记录。

普通用户进入页面后，可以理解这不是编辑后台，也不是裸内部数据页，而是本机运行链路的中央状态只读视图。当前 V1 只接入一个项目，但入口形态已经是统一项目选择器，为未来多项目切换预留。

## 产品复验项

| 复验项 | 结论 | 说明 |
| --- | --- | --- |
| 普通用户能否理解当前项目 | 通过 | 顶部项目区域显示“项目选择”和当前中文项目名“真知公司知识核心”，不再只暴露 `company-knowledge-core`。 |
| 普通用户能否理解工作台定位 | 通过 | 顶部说明明确这是“本机单机闭环工作台”，并说明当前只展示状态。 |
| 普通用户能否理解只读状态 | 通过 | 可见文案说明“只读状态”“中央状态只读视图”“真实运行状态只读视图”，不会误导用户以为此页可直接改状态。 |
| 普通用户能否理解数据来源 | 通过 | 可见文案包含“数据来自中央状态记录”，read model 的 `sourceOfTruth` 仍是 `central-api-read-model`，用户文案和底层来源一致。 |
| 项目选择器是否满足 V1 | 通过 | `workbench-shell.html` 存在 `project-select`；渲染层以中文当前项目名填充选项；当前仅一个项目，但已经形成统一入口，可扩展多项目切换。 |
| “主 Agent”术语 | 通过 | 渲染可见文案和测试断言使用“主 Agent”；“组Agent”不再作为用户可见术语。 |
| 路由链路说明 | 通过 | 首页显示“路由已建好：项目 -> 主 Agent -> 岗位 Agent -> 本机设备 -> 执行器 Runner -> 任务结果记录 -> 审批/权限 -> 异常恢复。” |
| 内部字段中文化/隐藏 | 通过 | 第 3 轮测试报告确认 `runtimeMetrics`、`deviceId`、`session.v1`、英文能力值等不作为 DOM 可见文案直出。 |

## 项目选择器判断

项目选择器合格，满足 V1：

1. 统一入口：页面顶部固定使用 `select#project-select`，不是把项目名散落在各模块。
2. 当前项目中文名：默认选项显示“真知公司知识核心”。
3. 未来多项目预留：当前只接一个项目，选择器结构已经允许后续追加项目选项和切换行为。

非阻断遗留项：多项目真实切换尚未实现，属于 V1 之后能力，不影响本次“项目名称应有统一项目选择下拉框”的产品验收。

## 路由链路判断

可以向用户说明“路由已建好”。本轮复验确认页面可解释的链路覆盖：

项目 -> 主 Agent -> 岗位 Agent -> 本机设备 -> 执行器 Runner -> 任务结果记录 -> 审批/权限 -> 异常恢复。

这个表述适用于 V1 本机单机闭环范围：链路已按中央状态记录只读展示，用户能看到路由状态、执行器租约、任务结果、审批/权限和异常恢复，不代表已经完成跨设备、多项目调度能力。

## 证据

- `task-results/tr-kt-v1-workbench-user-copy-polish.md`：第 3 轮返修说明项目选择器、用户视角顶部说明、内部字段隐藏/中文化、路由链路均已完成。
- `task-results/tr-kt-v1-workbench-user-copy-polish-test.md`：Test Agent 最终回归通过，无缺陷，交产品复验。
- `projects/company-knowledge-core/test-reports/v1-workbench-user-copy-polish-test-report.md`：确认项目选择器、当前中文项目名、顶部说明、主 Agent 术语、路由链路、质量门均通过。
- `scripts/validate_desktop_workbench_slice0.py`：本轮复跑 `desktop workbench slice0 artifacts: passed`。
- `tests/test_desktop_workbench_slice0.py`：本轮复跑 10 tests OK。

## 遗留项

无阻断遗留项。

后续建议只作为排期项跟进：接入真实多项目列表和选择后的 read model 切换；这不影响本次用户文案 polish 和 V1 项目选择器验收。

## 下一步

本产品复验接受。任务可 finish，并 handoff 给 `agent.company.project-manager` 做项目收口。
