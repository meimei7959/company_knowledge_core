---
type: ProjectTask
taskId: kt-v2-pm-control-lease-non-sandbox-api-validation
projectId: company-knowledge-core
status: done
assignee: agent.company.test
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T05:52:56Z
dependsOn:
  - kt-v2-pm-control-lease-product-final-acceptance
---

# 补验任务：非沙箱 HTTP/API 主控租约路由验收

## 背景

产品经理 Agent 已接受 PM 主控租约的本地可验证产品范围，但上线发布仍被阻塞。测试报告记录当前沙箱不能绑定本地 socket，因此 HTTP/API 路由需要在非沙箱或部署验收环境补跑。

## 验收范围

- PM 主控租约状态读取 API。
- 主控 PM 获取、心跳、释放、接管 API。
- PM 调度写操作带租约成功。
- 无租约、过期租约、协同 PM、备用 PM、项目不匹配、旧租约代际写入被拒绝。
- 拒绝写入必须生成 `pm_control_lease.denied` 审计。
- 被拒绝的调度写操作不能留下目标任务。
- 工作台 live read model 能读取并展示 API 返回的主控 PM、协同 PM、备用 PM、租约健康和接管记录。

## 通过标准

- 输出非沙箱 HTTP/API 验收报告。
- 输出 TaskResult，引用命令、日志、API 响应摘要和审计文件。
- 如 API 路由或权限语义失败，创建研发返工任务并交 `agent.company.development`。

## 产出

- `projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md`
- `task-results/tr-kt-v2-pm-control-lease-non-sandbox-api-validation.md`
