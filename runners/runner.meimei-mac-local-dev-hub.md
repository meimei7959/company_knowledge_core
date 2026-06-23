---
type: AgentRunner
title: Meimei Mac Local Dev Hub
description: External Agent Ring runner registration.
timestamp: "2026-06-21T08:23:54Z"
runnerId: runner.meimei-mac-local-dev-hub
machineId: runner.meimei-mac-local-dev-hub
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: busy
mode: online
agents:
  - agent.company.development
agentIds:
  - agent.company.development
capabilities:
  - development
  - scheduler
  - agent_worker
  - task_result_writeback
  - approval_relay
  - environment_readiness
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
lastHeartbeatAt: "2026-06-21T08:23:54Z"
currentLeases: []
staleLeases: []
failedLeases:
  - {"taskId":"kt-ai-native-os-dev-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md","status":"blocked","at":"2026-06-21T08:37:15Z"}
taskHistory:
  - {"taskId":"kt-ai-native-os-dev-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md","event":"claimed","at":"2026-06-21T08:23:54Z"}
  - {"taskId":"kt-ai-native-os-dev-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md","event":"claimed","at":"2026-06-21T08:24:12Z"}
  - {"taskId":"kt-ai-native-os-dev-automation-hub-hard-capabilities","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-dev-automation-hub-hard-capabilities.md","event":"finished:blocked","at":"2026-06-21T08:37:15Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-21T08:37:15Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
