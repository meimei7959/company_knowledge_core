---
type: ReviewRecord
title: Phase 2 PM Control Lease API Readiness
status: submitted
projectId: company-knowledge-core
taskId: kt-v2-pm-control-lease-api-readiness-ops
ownerAgent: agent.company.operations
createdAt: 2026-06-23T06:08:24Z
---

# Phase 2 PM 主控租约 API Readiness

## 结论

运维 Agent 已补齐本机 PostgreSQL/API readiness，测试 Agent 可以复跑 `kt-v2-pm-control-lease-non-sandbox-api-validation`。

本结论只证明环境 readiness 已准备好，不替代测试 Agent 的非沙箱 HTTP/API 验收结论。

## 已准备环境

- 本机临时环境文件：`.zhenzhi/local/pm-control-lease-api-readiness.env`
- 环境文件状态：未跟踪、位于 `.zhenzhi/`，受 `.gitignore` 保护。
- 环境文件权限：`600`。
- PostgreSQL 容器：`zhenzhi-pm-lease-readiness-postgres`
- PostgreSQL 监听：`127.0.0.1:55433`
- API 验证地址：`http://127.0.0.1:18765`

真实密码、API token、数据库连接串未写入本报告、任务文件、审计文件或 git 跟踪文件。

## 验证结果

- Docker 可用。
- Docker Compose 可用。
- 专用 PostgreSQL 容器已启动。
- `ensure_database_schema()` 通过。
- `ensure_operational_schema("ops-readiness")` 通过。
- `KnowledgeHTTPServer` 动态端口启动通过。
- `/health` 返回 `200` 且 `ok=true`。
- `/v0/pm-control-lease/status?projectId=company-knowledge-core` 返回 `200`，响应类型为 `PMControlLeaseReadModel`。
- CLI API 固定端口 `127.0.0.1:18765` 短跑通过，`/health` 返回 `ok=true`。

## 测试 Agent 复跑方式

测试 Agent 复跑时应在本机仓库根目录执行：

```bash
cd /Users/meimei/Documents/company_knowledge_core
set -a
. .zhenzhi/local/pm-control-lease-api-readiness.env
set +a
python3 -m zhenzhi_knowledge.cli --root /Users/meimei/Documents/company_knowledge_core api serve --host "$READINESS_API_HOST" --port "$READINESS_API_PORT"
```

另一个终端或测试脚本使用同一份 `.zhenzhi/local/pm-control-lease-api-readiness.env` 读取 `ZHENZHI_KNOWLEDGE_API_TOKEN` 后访问：

```txt
http://127.0.0.1:18765
```

测试 Agent 应复跑 PM 主控租约非沙箱 HTTP/API 路由验收，并自行产出测试结论。

## 运维注意事项

- `deploy/lighthouse/.env` 存在且未被 git 跟踪，但该部署环境连接的是部署容器内地址，不适合作为宿主机 Python 进程的 API 补验连接串。
- 现有 `zhenzhi-knowledge-postgres` 部署容器未被修改。
- 本次为避免影响现有部署，使用了专用 readiness PostgreSQL 容器。
- API 常驻进程未保留；测试 Agent 复跑时按上方命令启动。

## 剩余事项

- 测试 Agent 需要复跑非沙箱 HTTP/API 路由验收。
- 产品/PM 发布级结论仍需等待测试 Agent 复跑结果。
