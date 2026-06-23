---
type: ProjectTask
taskId: kt-v2-pm-control-lease-secret-scan-rework
projectId: company-knowledge-core
status: done
assignee: agent.company.development
requester: agent.company.test
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T06:16:58Z
dependsOn:
  - kt-v2-pm-control-lease-non-sandbox-api-validation
resultRef: task-results/tr-kt-v2-pm-control-lease-secret-scan-rework.md
auditRefs:
  - knowledge/audit/audit.20260623T062800Z-pm-control-lease-secret-scan-rework.md
completedAt: "2026-06-23T06:28:00Z"
updatedAt: "2026-06-23T06:28:00Z"
---

# 研发返工任务：PM 主控租约持久化字段触发安全扫描

## 背景

测试 Agent 复跑非沙箱 HTTP/API 验收时，运维 readiness 已完成，真实 `KnowledgeHTTPServer` 和本机 PostgreSQL 可用。

首轮路由已证明：

- `/health` 初始通过。
- PM 主控租约 status/acquire/heartbeat 可走真实 HTTP。
- 带有效主控租约创建任务成功。
- 无租约、协同 PM、备用 PM、项目不匹配、旧租约代际写入均被拒绝并生成审计。
- 被拒绝写入没有留下目标任务。

但 API 写入 PM 主控租约文件后，`/health` 变为 500。

## 缺陷

PM 主控租约持久化文件仍写入以下字段名：

- `fencingToken`
- `idempotencyKey`

健康检查会把这些字段识别为疑似 secret，返回 `possible secret value`，导致 readiness 失败。

这会造成上线环境只要真实创建 PM 主控租约，系统健康检查就变红。

## 返工要求

- 调整 PM 主控租约持久化字段命名，避免触发 secret 扫描。
- 建议持久化使用 `leaseGeneration`、`deduplicationRef` 等非 token/key 命名。
- 保持 HTTP/CLI API 入参兼容：外部旧字段仍可接收，但落盘对象不得使用疑似 secret 字段名。
- 更新 core/server/cli/tests 中相关断言和 read model 映射。
- 增加回归测试：真实创建 PM 主控租约后，安全扫描/validate/health 不应报疑似 secret。
- 修复后交回测试 Agent 复跑 `kt-v2-pm-control-lease-non-sandbox-api-validation`。

## 禁止事项

- 不得降低或绕过 secret 扫描规则。
- 不得把真实 `pmLeaseToken`、数据库连接串、API token 写入 git 跟踪文件。

## 验收标准

- `python3 -m zhenzhi_knowledge.cli validate` 通过。
- PM 主控租约非沙箱 HTTP/API 补验通过。
- 工作台 live/read model 能展示主控 PM、协同 PM、备用 PM、租约健康和接管记录。
