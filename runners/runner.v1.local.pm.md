---
type: AgentRunner
title: runner.v1.local.pm
description: External Agent Ring runner registration.
timestamp: "2026-06-22T03:19:27Z"
runnerId: runner.v1.local.pm
machineId: runner.v1.local.pm
owner: ""
ringVersion: v1-local-runtime
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.project-manager
agentIds:
  - agent.company.project-manager
capabilities:
  - acceptance
  - local_router
  - orchestrator
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
lastHeartbeatAt: "2026-06-22T04:37:02Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory:
  - {"taskId":"kt-ai-native-agent-v1-pm-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-pm-product-final-acceptance.md","event":"claimed","at":"2026-06-22T03:22:39Z"}
  - {"taskId":"kt-ai-native-agent-v1-pm-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-pm-product-final-acceptance.md","event":"finished:submitted","at":"2026-06-22T03:22:39Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-22T03:22:39Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
