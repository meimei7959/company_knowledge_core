---
type: ProjectTask
taskId: kt-v2-pm-control-lease-real-multicomputer-validation
projectId: company-knowledge-core
status: done
assignee: agent.company.test
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T05:52:56Z
dependsOn:
  - kt-v2-pm-control-lease-product-final-acceptance
  - kt-v2-pm-control-lease-non-sandbox-api-validation
collaborators:
  - agent.company.operations
resultRef: task-results/tr-kt-v2-pm-control-lease-real-multicomputer-validation.md
auditRefs:
  - knowledge/audit/audit.20260623T064543Z-pm-control-lease-real-multicomputer-validation-failed.md
completedAt: "2026-06-23T06:45:43Z"
updatedAt: "2026-06-23T06:45:43Z"
nextTaskRef: projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-concurrent-acquire-rework.md
---

# 补验任务：真实多电脑共享中枢 PM 主控防冲突验收

## 背景

产品经理 Agent 明确：本地模拟和单机证据不能替代真实多电脑共享中枢证据。上线发布前必须证明同一项目下多台电脑、多个项目经理 Agent 同时存在时，只有一个主控 PM 能持有调度租约并执行写操作。

## 验收范围

- 两台不同电脑或两个等价独立 host 注册到同一个项目中枢。
- 同一项目注册一个主控 PM、至少一个协同 PM、至少一个备用 PM。
- 同时尝试获取主控租约时，只能一个 PM 成功，其余 PM 进入协同或备用状态。
- 协同 PM 和备用 PM 写调度任务必须被拒绝并审计。
- 主控 PM 心跳健康时，备用 PM 接管必须被拒绝或进入待确认状态。
- 主控 PM 心跳过期后，备用 PM 可按规则接管并生成接管记录。
- 旧租约代际不能继续写入，必须被拒绝并审计。
- 工作台展示真实设备数量、主控 PM、协同 PM、备用 PM、租约健康、接管历史和拒绝审计。

## 通过标准

- 输出真实多电脑或等价独立 host 验收报告。
- 输出 TaskResult，引用两端设备注册、心跳、租约竞争、拒绝审计、接管记录和工作台截图或 DOM 证据。
- 如发现共享中枢并发一致性问题，创建研发返工任务并交 `agent.company.development`。
- 如缺真实第二台电脑或部署权限，记录为人类/管理员动作阻塞，不得声明上线完成。

## 产出

- `projects/company-knowledge-core/test-reports/phase2-pm-control-lease-real-multicomputer-validation.md`
- `task-results/tr-kt-v2-pm-control-lease-real-multicomputer-validation.md`

## 执行结果

测试 Agent 已完成补验。结论为未通过，已创建研发返工任务：

- `projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-concurrent-acquire-rework.md`
