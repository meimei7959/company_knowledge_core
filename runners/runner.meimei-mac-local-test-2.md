---
type: AgentRunner
title: Meimei Mac Local Test 2
description: External Agent Ring runner registration.
timestamp: "2026-06-21T07:18:55Z"
runnerId: runner.meimei-mac-local-test-2
machineId: runner.meimei-mac-local-test-2
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
  - testing
  - quality_gate
  - requirement_traceability
  - scheduler
  - agent_worker
  - task_result_validation
  - governance
  - api
  - desktop
  - cross_platform
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
lastHeartbeatAt: "2026-06-21T07:18:55Z"
currentLeases: []
staleLeases: []
failedLeases: []
taskHistory: []
lastFailure: ""
manualHandoff: false
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
