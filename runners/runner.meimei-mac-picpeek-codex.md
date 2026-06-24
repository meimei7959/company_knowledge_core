---
type: AgentRunner
title: Meimei Mac PicPeek Codex Runner
description: External Agent Ring runner registration.
timestamp: "2026-06-24T01:44:48Z"
runnerId: runner.meimei-mac-picpeek-codex
machineId: runner.meimei-mac-picpeek-codex
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.project-manager
  - agent.company.product-manager
  - agent.company.development
  - agent.company.test
agentIds:
  - agent.company.project-manager
  - agent.company.product-manager
  - agent.company.development
  - agent.company.test
capabilities:
  - code_reading
  - evidence_planning
  - product_analysis
  - project_management
  - task_result_writeback
tools: []
availableProjects:
  - picpeek
repoAccess:
  - /Users/meimei/Documents/picpeek/01_源码镜像/picpeek
repositoryScopes:
  - /Users/meimei/Documents/picpeek/01_源码镜像/picpeek
dataScopes:
  - local_repo
  - project_workspace
load: 0.05
lastHeartbeatAt: "2026-06-24T01:45:02Z"
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
