---
type: AgentMessage
title: V1 Agent Message - msg.20260622T031927635063Z
description: Local Router message between V1 Agent sessions.
timestamp: "2026-06-22T03:19:27Z"
messageId: msg.20260622T031927635063Z
projectId: company-knowledge-core
fromAgentId: agent.company.project-manager
toAgentId: agent.company.test
fromSessionId: session.v1.group
toSessionId: session.v1.test
messageType: task
priority: critical
payload: {"taskId":"kt-v1-local-router-runtime-acceptance-test","packageId":"pkg.kt-v1-local-router-runtime-acceptance-test.20260622T031927634496Z"}
contextRefs:
  - projects/company-knowledge-core/tasks/kt-v1-local-router-runtime-acceptance-test.md
  - task-results/tr-kt-v1-local-router-runtime-acceptance-dev.md
  - runtime/worktrees/worktree.kt-v1-local-router-runtime-acceptance-dev.agent.company.development.md
routing: {"routeType":"local","targetDeviceId":"device.local"}
status: delivered
---

## Payload

```json
{
  "taskId": "kt-v1-local-router-runtime-acceptance-test",
  "packageId": "pkg.kt-v1-local-router-runtime-acceptance-test.20260622T031927634496Z"
}
```
