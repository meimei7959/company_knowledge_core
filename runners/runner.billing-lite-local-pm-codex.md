---
type: AgentRunner
title: Billing Lite Local PM Codex
description: External Agent Ring runner registration.
timestamp: "2026-06-23T12:33:33Z"
runnerId: runner.billing-lite-local-pm-codex
machineId: runner.billing-lite-local-pm-codex
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: idle
mode: online
agents:
  - agent.company.project-manager
  - agent.company.product-manager
agentIds:
  - agent.company.project-manager
  - agent.company.product-manager
capabilities:
  - acceptance_criteria
  - product_review
  - project_management
  - requirement_traceability
tools: []
availableProjects:
  - billing-lite
repoAccess:
  - /Users/meimei/Documents/company_knowledge_core
repositoryScopes:
  - /Users/meimei/Documents/company_knowledge_core
dataScopes:
  - Project
  - ProjectTask
  - SourceMaterial
  - TaskResult
  - Decision
  - AuditLog
load: 0.1
lastHeartbeatAt: "2026-06-23T12:33:33Z"
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
