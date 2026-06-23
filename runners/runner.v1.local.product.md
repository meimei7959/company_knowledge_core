---
type: AgentRunner
title: runner.v1.local.product
description: External Agent Ring runner registration.
timestamp: "2026-06-22T03:19:27Z"
runnerId: runner.v1.local.product
machineId: runner.v1.local.product
owner: ""
ringVersion: v1-local-runtime
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.product-manager
agentIds:
  - agent.company.product-manager
capabilities:
  - product_requirement
  - product_review
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
lastHeartbeatAt: "2026-06-22T03:19:27Z"
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
