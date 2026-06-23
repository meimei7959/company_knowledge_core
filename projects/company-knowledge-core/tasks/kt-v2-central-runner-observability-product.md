---
taskId: kt-v2-central-runner-observability-product
projectId: company-knowledge-core
type: ProjectTask
status: processing
assignee: agent.company.product-manager
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T01:43:59Z
---

# 产品任务：阶段二方案二中枢监管需求补充

## 背景

用户确认当前项目已经部署过并有线上地址，因此阶段二应采用方案二：部署中枢加多设备 Runner，而不是本地文件同步。

## 任务

产品经理 Agent 输出补充 PRD，明确：

- 工作台承担受控登记入口：创建项目、电脑注册/邀请、工具注册或工具注册申请。
- 工作台运行监管区只读：不直接派单、转交、修复、禁用 Runner、篡改结果或批准验收。
- 工作台展示项目数量、电脑数量、项目任务明细、电脑明细。
- 项目任务必须展示所属需求、当前进展、负责 Agent、执行电脑、使用模型、token 消耗、工具、最后更新时间和验收状态。
- 电脑明细必须展示有哪些 Agent 在工作、使用 Codex 还是 Claude、使用工具、当前任务、模型、token、心跳和异常。
- 每台电脑如何注册到中枢。
- 每台电脑如何上报进展到中枢。
- 项目隔离、权限、审批、审计、幂等和真实双机验收标准。

## 产出

- `docs/product/ai-native-os/phase-2-central-runner-observability-prd.md`

## 完成标准

- 用户能从 PRD 中看懂工作台要看什么、不能做什么。
- 研发能根据 PRD 知道需要哪些数据字段。
- 测试能根据 PRD 写出双机验收用例。
