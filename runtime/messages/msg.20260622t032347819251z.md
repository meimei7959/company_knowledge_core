---
type: AgentMessage
title: V1 Agent Message - msg.20260622T032347819251Z
description: Local Router message between V1 Agent sessions.
timestamp: "2026-06-22T03:23:47Z"
messageId: msg.20260622T032347819251Z
projectId: company-knowledge-core
fromAgentId: agent.company.project-manager
toAgentId: agent.company.product-manager
fromSessionId: session.v1.group
toSessionId: session.v1.product
messageType: task
priority: high
payload: {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","packageId":"pkg.kt-ai-native-agent-v1-product-final-acceptance.20260622T032347818463Z"}
contextRefs:
  - projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md
  - runtime/acceptance-runs/v1.acceptance.20260622t031927643283z.md
  - task-results/tr-kt-ai-native-agent-v1-test-closed-loop-acceptance.md
  - task-results/tr-kt-ai-native-agent-v1-pm-product-final-acceptance.md
routing: {"routeType":"local","targetDeviceId":"device.local"}
status: delivered
---

## Payload

```json
{
  "taskId": "kt-ai-native-agent-v1-product-final-acceptance",
  "packageId": "pkg.kt-ai-native-agent-v1-product-final-acceptance.20260622T032347818463Z"
}
```
