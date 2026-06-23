---
type: TaskResult
title: Result for KT-AGENT-RING-PROTOCOL
description: Result of task KT-AGENT-RING-PROTOCOL.
timestamp: "2026-06-18T11:15:40Z"
resultId: TR-KT-AGENT-RING-PROTOCOL
taskId: KT-AGENT-RING-PROTOCOL
projectId: company-knowledge-core
assignee: agent-ring-team
runnerId: []
executorAgent: ""
status: done
summary: 已完成中央处理器侧 Agent Ring 协议集成：runner register/upsert、heartbeat、task list/status、claim、task heartbeat、context pull、finish writeback；claim 会校验 runner status、capabilities、availableProjects、stale task version、active lease、secretRef readiness；pull/finish 会拒绝 expired lease、invalid token 和非 lease owner 写回；协议文档已与实现 payload 对齐。
outputRefs:
  - zhenzhi_knowledge/core.py
  - zhenzhi_knowledge/server.py
  - tests/test_cli.py
  - docs/protocols/agent-ring-communication-protocol.md
knowledgeRefs: []
sourceMaterialRefs:
  - docs/protocols/agent-ring-communication-protocol.md
  - docs/architecture/central-processor-and-agent-ring.md
evidenceRefs:
  - tests.test_cli.CliTests.test_agent_ring_http_task_lifecycle
testsOrChecks: []
nextActions:
  - 后续如需更强幂等，可增加 Agent Ring idempotency-key 字段；当前 TaskResult 已按 taskId 固定路径覆盖写回。
completedAt: "2026-06-18T11:15:40Z"
---

## Summary

已完成中央处理器侧 Agent Ring 协议集成：runner register/upsert、heartbeat、task list/status、claim、task heartbeat、context pull、finish writeback；claim 会校验 runner status、capabilities、availableProjects、stale task version、active lease、secretRef readiness；pull/finish 会拒绝 expired lease、invalid token 和非 lease owner 写回；协议文档已与实现 payload 对齐。

## Evidence

- tests.test_cli.CliTests.test_agent_ring_http_task_lifecycle

## Outputs

- zhenzhi_knowledge/core.py
- zhenzhi_knowledge/server.py
- tests/test_cli.py
- docs/protocols/agent-ring-communication-protocol.md

## Next Actions

- 后续如需更强幂等，可增加 Agent Ring idempotency-key 字段；当前 TaskResult 已按 taskId 固定路径覆盖写回。

## Tests Or Checks

- none
