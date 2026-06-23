---
type: AgentRunner
title: Meimei Mac Local Test 1
description: External Agent Ring runner registration.
timestamp: "2026-06-21T07:18:55Z"
runnerId: runner.meimei-mac-local-test-1
machineId: runner.meimei-mac-local-test-1
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.test
agentIds:
  - agent.company.test
capabilities:
  - integration
  - migration
  - quality_gate
  - requirement_traceability
  - test
  - testing
tools: []
availableProjects:
  - company-knowledge-core
repoAccess:
  - /Users/meimei/Documents/company_knowledge_core
repositoryScopes:
  - /Users/meimei/Documents/company_knowledge_core
dataScopes:
  - local_repo
load: 0.05
lastHeartbeatAt: "2026-06-22T04:37:02Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory:
  - {"taskId":"kt-ai-native-agent-v1-test-closed-loop-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-test-closed-loop-acceptance.md","event":"claimed","at":"2026-06-22T03:21:27Z"}
  - {"taskId":"kt-ai-native-agent-v1-test-closed-loop-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-test-closed-loop-acceptance.md","event":"finished:submitted","at":"2026-06-22T03:21:27Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-22T03:21:27Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
