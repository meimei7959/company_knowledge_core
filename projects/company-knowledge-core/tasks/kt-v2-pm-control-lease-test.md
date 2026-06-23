---
type: ProjectTask
taskId: kt-v2-pm-control-lease-test
projectId: company-knowledge-core
status: pending
assignee: agent.company.test
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T02:57:45Z
dependsOn:
  - kt-v2-pm-control-lease-development
---

# 测试任务：PM 主控租约验收

## 测试范围

- 同一项目只能一个主控 PM 持有调度租约。
- 协同 PM/备用 PM 无租约写操作被拒绝并审计。
- 主控 PM 带租约写操作成功。
- 过期租约写操作失败。
- 接管流程生成新租约和接管记录。
- 工作台展示主控 PM、协同 PM、备用 PM、租约健康和接管记录。
- 已有工作台登记入口、Runner 注册、权限门禁不回归。

## 产出

- `projects/company-knowledge-core/test-reports/phase2-pm-control-lease-test-report.md`
- `task-results/tr-kt-v2-pm-control-lease-test.md`
