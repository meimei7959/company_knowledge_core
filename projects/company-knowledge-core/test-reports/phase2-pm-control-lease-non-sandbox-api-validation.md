---
type: EvalRun
title: Phase 2 PM 主控租约非沙箱 HTTP/API 补验
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-non-sandbox-api-validation
testerAgent: agent.company.test
status: done
decision: accepted
createdAt: "2026-06-23T05:57:57Z"
updatedAt: "2026-06-23T06:40:00Z"
sourceRefs:
  - projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-non-sandbox-api-validation.md
  - task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md
  - projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md
  - projects/company-knowledge-core/ops/phase2-pm-control-lease-api-readiness.md
  - task-results/tr-kt-v2-pm-control-lease-api-readiness-ops.md
evidenceRefs:
  - /private/tmp/pm_control_lease_revalidation.json
  - zhenzhi_knowledge/server.py
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/cli.py
  - tests/test_cli.py
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-shell.js
  - projects/company-knowledge-core/desktop-workbench-slice0/workbench-live-read-model.js
---

# Phase 2 PM 主控租约非沙箱 HTTP/API 补验

## 结论

本次研发返工后复验结论为 accepted。

测试 Agent 使用 `.zhenzhi/local/pm-control-lease-api-readiness.env` 启动真实 `KnowledgeHTTPServer`，连接本机 PostgreSQL readiness 环境，并在临时验证 bundle 中执行 PM 主控租约 HTTP/API 全链路。复验 38 项检查全部通过，未发现新的研发返工项。

原失败点已修复：真实创建 PM 主控租约后，落盘文件不再包含会触发 secret scan 的旧持久化字段；`/health` 在创建、心跳、任务写入、接管、释放之后均保持 HTTP 200 且 `ok=true`。

## 已读取材料

- 补验任务：`projects/company-knowledge-core/tasks/kt-v2-pm-control-lease-non-sandbox-api-validation.md`
- 研发返工结果：`task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md`
- 上次失败报告：`projects/company-knowledge-core/test-reports/phase2-pm-control-lease-non-sandbox-api-validation.md`
- 运维 readiness：`projects/company-knowledge-core/ops/phase2-pm-control-lease-api-readiness.md`
- 运维 TaskResult：`task-results/tr-kt-v2-pm-control-lease-api-readiness-ops.md`

## 已执行验证

- readiness env 已加载，未输出任何真实认证值或数据库连接串。
- 真实 `KnowledgeHTTPServer` 已在 `127.0.0.1:18765` 启动。
- 本机 PostgreSQL readiness 路径已参与 `/health` 检查。
- 初始 `/health` 通过。
- PM 主控租约 acquire 通过。
- 真实创建 PM 租约后 `/health` 仍通过。
- 租约落盘字段为安全命名，secret scan 干净。
- 兼容旧客户端字段的 heartbeat 通过。
- 使用有效 PM 主控租约创建任务成功。
- 无租约写入被拒绝并写审计。
- 协同 PM 写入被拒绝并写审计。
- 备用 PM 写入被拒绝并写审计。
- 项目不匹配写入被拒绝并写审计。
- 主控健康时未确认接管被拒绝。
- 确认接管通过。
- 旧代际写入被拒绝并写审计。
- 过期租约写入被拒绝并写审计。
- release 路由通过。
- 所有拒绝场景均未写入目标任务文件。
- PM status read model 展示主控、协同、备用、租约健康、接管记录和拒绝摘要。
- Workbench execution read model 包含 PM control 数据，角色覆盖 primary、collaborator、standby。
- Workbench shell 包含中文展示文案：主控 PM、协同 PM、备用 PM、租约、接管。

## 证据摘要

- 验证项目根：临时 validation bundle，未污染正式项目数据。
- API 地址：`http://127.0.0.1:18765`。
- 检查项：38 项。
- 失败项：0 项。
- 拒绝审计：已观察到 `pm_control_lease.denied`。
- 租约文件：7 个测试租约文件，均位于临时 bundle。
- 状态 read model 角色：collaborator、primary、standby。
- Workbench read model 角色：collaborator、primary、standby。

## 返工判断

不需要研发返工。

上次发现的 PM 主控租约落盘 secret scan 问题已由研发返工修复，并通过真实 HTTP/API 路径复验。

## 后续动作

测试 Agent 将补验结论交回项目经理 Agent，由项目经理组织产品/PM 发布级最终验收。
