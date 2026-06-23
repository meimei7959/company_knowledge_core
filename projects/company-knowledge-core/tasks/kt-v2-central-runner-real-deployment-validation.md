---
taskId: kt-v2-central-runner-real-deployment-validation
type: ProjectTask
projectId: company-knowledge-core
status: pending
assignee: agent.company.test
requester: agent.company.project-manager
workflow: phase2-central-runner-observability-orchestrator
createdAt: 2026-06-23T02:50:00Z
dependsOn:
  - kt-v2-central-runner-observability-test
---

# 真实部署补验：双机、Gateway、审批回调、并发幂等

## 背景

产品最终验收结论为 `blocked_for_production_launch`。本地登记入口、只读监管、中文可读、权限、审批、幂等和审计语义通过，但缺少生产上线前必须证据。

## 验收范围

1. 真实双机 Runner：两台不同电脑接入同一个部署中枢，具备不同机器指纹、独立心跳和独立租约。
2. 真实 API Gateway 权限：鉴权、权限拒绝、审计落盘和至少一次 smoke。
3. 真实 Tool Owner 审批回调：高风险工具申请经过真实或等价审批回调，状态、通知和审计一致。
4. 并发缺权限/幂等：重复点击、网络重试、并发提交不会创建重复项目、重复电脑邀请或重复工具申请。

## 通过标准

- 工作台显示真实项目数量、电脑数量、任务明细、电脑明细、Agent、工具、Codex/Claude、模型和 token。
- 缺权限写入口拒绝且写 `workbench.permission.denied`。
- 有权限登记入口正常进入申请/审批/登记状态。
- 执行监管区域不提供派单、修复、转交、篡改结果或验收通过入口。
- 输出测试报告、证据引用和 TaskResult。

## 失败回路

- API/Gateway/权限实现缺陷 -> 交研发 Agent 返工。
- 产品流程或可读性不满足 -> 交产品经理 Agent 或设计 Agent 复核。
- 需要真实同事电脑或部署权限 -> 项目经理 Agent 记录阻塞并请求人类/管理员动作。
