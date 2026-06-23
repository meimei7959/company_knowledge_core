---
type: ProjectTask
taskId: kt-v2-pm-control-lease-concurrent-acquire-rework
projectId: company-knowledge-core
status: pending
assignee: agent.company.development
requester: agent.company.test
workflow: phase2-pm-control-lease-orchestrator
createdAt: "2026-06-23T06:45:43Z"
dependsOn:
  - kt-v2-pm-control-lease-real-multicomputer-validation
sourceRefs:
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-real-multicomputer-validation.md
  - task-results/tr-kt-v2-pm-control-lease-real-multicomputer-validation.md
evidenceRefs:
  - /private/tmp/pm_control_lease_real_multicomputer_20260623T064422Z.json
---

# 研发返工任务：PM 主控租约并发获取缺少原子互斥

## 背景

测试 Agent 按真实多电脑共享中枢要求执行补验：两个等价独立 host、两个 runner、两个 device、多个 PM 会话，共用同一个真实 `KnowledgeHTTPServer` 和 PostgreSQL readiness 中枢。

## 缺陷

两个不同 PM Agent 同时调用 `/v0/pm-control-lease/acquire` 获取同一项目主控租约时，实际两个请求都成功。

这违反产品要求：同一项目同一时间只能一个主控 PM 持有调度租约，其他 PM 只能协同或备用。

## 返工要求

- 修复 PM 主控租约 acquire 路径的并发一致性。
- 同一项目同一时刻只能创建一个 active/expiring 主控租约。
- `current_pm_control_lease` 检查与租约写入之间不能存在竞态窗口。
- 中枢拒绝失败方写入，并生成可审计的 `pm_control_lease.denied` 或等价 acquire-denied 审计。
- 不得降低现有校验：无租约、非主控、备用/协同、跨项目、过期、旧代际仍必须拒绝。
- 不得引入真实 secret、数据库连接串、API 凭据到 git 跟踪文件。

## 验收标准

- 研发自测覆盖并发 acquire，证明两个独立 PM 同时抢同一项目主控租约时只有一个成功。
- `python3 -m zhenzhi_knowledge.cli validate` 通过。
- `git diff --check` 通过。
- 修复后交回测试 Agent 复跑 `kt-v2-pm-control-lease-real-multicomputer-validation`。
