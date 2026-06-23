---
type: AgentRunner
title: runner.v1.local.dev
description: External Agent Ring runner registration.
timestamp: "2026-06-22T03:19:27Z"
runnerId: runner.v1.local.dev
machineId: runner.v1.local.dev
owner: ""
ringVersion: v1-local-runtime
hostType: local_mac
status: busy
mode: online
agents:
  - agent.company.development
agentIds:
  - agent.company.development
capabilities:
  - agent_runtime
  - development
  - implementation
  - worktree
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
lastHeartbeatAt: "2026-06-22T03:19:27Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory:
  - {"taskId":"kt-v1-local-router-runtime-acceptance-dev","taskRef":"projects/company-knowledge-core/tasks/kt-v1-local-router-runtime-acceptance-dev.md","event":"claimed","at":"2026-06-22T03:19:27Z"}
  - {"taskId":"kt-v1-local-router-runtime-acceptance-dev","taskRef":"projects/company-knowledge-core/tasks/kt-v1-local-router-runtime-acceptance-dev.md","event":"finished:submitted","at":"2026-06-22T03:19:27Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-22T03:19:27Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
