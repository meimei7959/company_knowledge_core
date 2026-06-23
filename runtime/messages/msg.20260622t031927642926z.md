---
type: AgentMessage
title: V1 Agent Message - msg.20260622T031927642926Z
description: Local Router message between V1 Agent sessions.
timestamp: "2026-06-22T03:19:27Z"
messageId: msg.20260622T031927642926Z
projectId: company-knowledge-core
fromAgentId: agent.company.project-manager
toAgentId: agent.company.project-manager
fromSessionId: session.v1.group
toSessionId: session.v1.group
messageType: confirm_request
priority: high
payload: {"action":"merge_or_publish_v1_acceptance","requiresHuman":true}
contextRefs:
  - task-results/tr-kt-v1-local-router-runtime-acceptance-dev.md
  - task-results/tr-kt-v1-local-router-runtime-acceptance-test.md
routing: {"routeType":"local","targetDeviceId":"device.local"}
status: delivered
---

## Payload

```json
{
  "action": "merge_or_publish_v1_acceptance",
  "requiresHuman": true
}
```
