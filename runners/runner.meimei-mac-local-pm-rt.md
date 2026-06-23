---
type: AgentRunner
title: Meimei Mac Local PM RT
description: External Agent Ring runner registration.
timestamp: "2026-06-21T09:37:12Z"
runnerId: runner.meimei-mac-local-pm-rt
machineId: runner.meimei-mac-local-pm-rt
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.project-manager
agentIds:
  - agent.company.project-manager
capabilities:
  - project_management
  - requirement_traceability
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
lastHeartbeatAt: "2026-06-21T09:48:03Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory:
  - {"taskId":"kt-ai-native-os-rt-pm-coverage-matrix","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-rt-pm-coverage-matrix.md","event":"claimed","at":"2026-06-21T09:37:32Z"}
  - {"taskId":"kt-ai-native-os-rt-pm-coverage-matrix","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-rt-pm-coverage-matrix.md","event":"finished:done","at":"2026-06-21T09:43:01Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-21T09:43:01Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
