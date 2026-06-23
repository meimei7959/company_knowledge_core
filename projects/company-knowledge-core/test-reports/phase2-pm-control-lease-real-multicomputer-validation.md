---
type: EvalRun
title: Phase 2 PM 主控租约真实多电脑防冲突补验
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-real-multicomputer-validation
testerAgent: agent.company.test
status: done
decision: changes_requested
createdAt: "2026-06-23T06:45:43Z"
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-real-multicomputer-validation.md
  - projects/company-knowledge-core/product-reviews/phase2-pm-control-lease-product-final-acceptance.md
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md
  - task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md
  - projects/company-knowledge-core/ops/phase2-pm-control-lease-api-readiness.md
evidenceRefs:
  - /private/tmp/pm_control_lease_real_multicomputer_20260623T064422Z.json
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
---

# Phase 2 PM 主控租约真实多电脑防冲突补验

## 结论

本次补验未通过，需要研发返工。

测试 Agent 使用一台电脑上的两个等价独立 host 进行验证：两个不同 `runnerId`、两个不同 `deviceId`、两个不同 worktree、两个独立 PM client identity，共用同一个真实 `KnowledgeHTTPServer` 和 PostgreSQL readiness 中枢。这个方式等价覆盖了“多台电脑同时接入同一项目中枢”的调度租约冲突路径；限制是物理机器仍是同一台 Mac，不能替代后续真实双机部署冒烟。

核心失败点：两个不同 PM Agent 同时请求同一项目主控租约时，两个请求都成功了。通过标准要求“同一项目同一时间只能一个主控 PM 持有调度租约”，因此这是共享中枢并发一致性缺陷。

## 已读取材料

- 产品最终验收：`projects/company-knowledge-core/product-reviews/phase2-pm-control-lease-product-final-acceptance.md`
- 非沙箱 HTTP/API 补验通过报告：`projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md`
- 研发返工结果：`task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md`
- 运维 readiness 报告：`projects/company-knowledge-core/ops/phase2-pm-control-lease-api-readiness.md`

## 验证方式

- 临时共享中枢：`/private/tmp` 下自动创建的验证 bundle。
- Host A：`runner.host-a`、`device.host-a`、独立 worktree。
- Host B：`runner.host-b`、`device.host-b`、独立 worktree。
- PM 会话：主控候选、协同 PM、备用 PM、第二备用 PM。
- API 路径：真实 `KnowledgeHTTPServer`。
- 数据库路径：本机 PostgreSQL readiness 环境。

## 通过项

- 真实 HTTP Server 与 PostgreSQL readiness `/health` 初始通过。
- 两个等价 host/runner/device 成功登记到同一项目中枢。
- 主控 PM 带有效租约可以写调度任务。
- 无租约写调度被拒绝并写审计。
- 协同 PM 写调度被拒绝并写审计。
- 备用 PM 接管前写调度被拒绝并写审计。
- 跨项目复用租约被拒绝并写审计。
- 健康主控未确认接管被拒绝。
- 主控心跳过期后备用 PM 可接管。
- 接管后旧代际/旧主控不能继续写。
- PM 租约 read model 展示主控、协同、备用、两个设备、租约健康、接管历史、拒绝审计。
- 工作台 read model 展示 PM 防冲突信息。
- 验证后 `/health` 仍通过。
- PM 租约落盘不触发 secret scan。

## 失败项

- 并发主控获取：两个独立 PM 同时请求 `/v0/pm-control-lease/acquire`，期望只有一个成功，实际两个都成功。

## 返工判断

需要研发 Agent 修复。推测根因是主控租约获取路径缺少共享中枢级原子互斥或条件写入保护：`current_pm_control_lease` 检查和租约文件写入之间存在竞态窗口。研发应在中枢写入层做原子 acquire，保证同一项目同一时间只有一个 active/expiring 主控租约能创建成功。

已创建返工任务：`projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-concurrent-acquire-rework.md`。

## 后续动作

研发修复后，测试 Agent 必须复跑本报告同一真实 HTTP/API 多 host 验收。复验通过前，产品/PM 不得声明 PM 主控租约防冲突达到发布级闭环。
