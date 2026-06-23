---
taskId: kt-v2-central-runner-observability-design
projectId: company-knowledge-core
type: ProjectTask
status: processing
assignee: agent.company.design
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T01:43:59Z
---

# 设计任务：中枢登记与监管工作台

## 任务

设计 Agent 基于产品经理的信息架构输出 UI/UX 设计。设计重点是用户看得懂，而不是展示内部对象。

必须覆盖：

- 创建项目入口。
- 电脑注册或邀请入口。
- 工具注册或工具注册申请入口。
- 统一项目选择。
- 总览：项目数、电脑数、运行中任务、异常电脑、待验收任务。
- 项目页：每个项目任务明细、所属需求、进展、Agent、电脑、模型、token、工具、验收状态。
- 电脑页：每台电脑在线状态、Agent、工具、Codex/Claude、当前任务、模型、token、心跳、异常。
- 边界：登记入口允许创建/申请/邀请；运行监管区域不出现派单、转交、修复、禁用、验收通过等执行操作按钮。
- 中文主文案，不用英文内部 id 作为主信息。
- 空状态、异常状态、离线状态和数据过期状态。

## 产出

- `projects/company-knowledge-core/design/phase2-central-runner-observability-workbench-design.md`

## 完成标准

- 普通用户能创建项目、发起电脑接入、提交工具注册，并判断现在有几台电脑、几个项目、每个任务卡在哪里、哪台电脑异常。
- 页面风格保持 Codex 风格，克制、清晰、信息密度合理。
- 设计不得承担产品信息架构职责。
