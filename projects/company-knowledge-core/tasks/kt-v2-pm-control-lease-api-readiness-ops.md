---
type: ProjectTask
taskId: kt-v2-pm-control-lease-api-readiness-ops
projectId: company-knowledge-core
status: done
assignee: agent.company.operations
requester: agent.company.project-manager
workflow: phase2-pm-control-lease-orchestrator
createdAt: 2026-06-23T06:00:00Z
dependsOn:
  - kt-v2-pm-control-lease-non-sandbox-api-validation
completedAt: 2026-06-23T06:08:24Z
resultRefs:
  - task-results/tr-kt-v2-pm-control-lease-api-readiness-ops.md
---

# 运维任务：PM 主控租约非沙箱 API readiness

## 背景

测试 Agent 执行 `kt-v2-pm-control-lease-non-sandbox-api-validation` 时被环境 readiness 阻塞。真实 HTTP Server 初始化要求 `DATABASE_URL` 指向 PostgreSQL；当前机器或当前会话缺少 PostgreSQL/API 启动配置。

## 目标

补齐可复跑非沙箱 HTTP/API 验收的本机或部署环境 readiness。

## 范围

- 确认本仓库 API Server 启动方式和必需环境变量。
- 准备 PostgreSQL，可用方式包括本机 PostgreSQL、Docker Compose PostgreSQL、已部署 PostgreSQL 或等价测试实例。
- 设置 `DATABASE_URL` 指向 PostgreSQL。
- 设置 API token 相关环境变量，供测试脚本调用。
- 启动或证明可启动 API Server，使 readiness 通过 `ensure_database_schema()` 和 `ensure_operational_schema()`。
- 不把真实密钥、token、密码写入知识文件、审计文件或任务文件。
- 产出运维结果，说明测试 Agent 复跑时应使用的非敏感命令、端口、环境文件位置和剩余阻塞。

## 通过标准

- API Server 能在非沙箱环境启动。
- PostgreSQL schema 初始化通过。
- 测试 Agent 可以复跑 `kt-v2-pm-control-lease-non-sandbox-api-validation`。
- 若受限于本机缺 Docker/PostgreSQL/部署权限/秘钥，必须明确记录缺失项和人类/管理员动作。

## 产出

- `projects/company-knowledge-core/ops/phase2-pm-control-lease-api-readiness.md`
- `task-results/tr-kt-v2-pm-control-lease-api-readiness-ops.md`
