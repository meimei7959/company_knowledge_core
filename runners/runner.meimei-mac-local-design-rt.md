---
type: AgentRunner
title: Meimei Mac Local Design RT
description: External Agent Ring runner registration.
timestamp: "2026-06-21T12:23:07Z"
runnerId: runner.meimei-mac-local-design-rt
machineId: runner.meimei-mac-local-design-rt
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.design
agentIds:
  - agent.company.design
capabilities:
  - cross_platform
  - design
  - desktop
  - requirement_traceability
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
lastHeartbeatAt: "2026-06-22T04:37:02Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory:
  - {"taskId":"kt-ai-native-os-gap-design-desktop-client","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-gap-design-desktop-client.md","event":"finished:done","at":"2026-06-21T12:28:27Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-21T12:28:27Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
