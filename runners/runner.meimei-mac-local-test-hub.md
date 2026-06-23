---
type: AgentRunner
title: Meimei Mac Local Test Hub
description: External Agent Ring runner registration.
timestamp: "2026-06-21T08:37:59Z"
runnerId: runner.meimei-mac-local-test-hub
machineId: runner.meimei-mac-local-test-hub
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: busy
mode: online
agents:
  - agent.company.test
agentIds:
  - agent.company.test
capabilities:
  - agent_worker
  - approval_relay
  - environment_readiness
  - quality_gate
  - scheduler
  - testing
  - workbench
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
lastHeartbeatAt: "2026-06-21T08:37:59Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory:
  - {"taskId":"kt-ai-native-os-test-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-test-automation-hub-hard-capabilities.md","event":"claimed","at":"2026-06-21T08:37:59Z"}
  - {"taskId":"kt-ai-native-os-test-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-test-automation-hub-hard-capabilities.md","event":"claimed","at":"2026-06-21T08:38:09Z"}
  - {"taskId":"kt-ai-native-os-test-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-test-automation-hub-hard-capabilities.md","event":"finished:done","at":"2026-06-21T08:45:02Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-21T08:45:02Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
