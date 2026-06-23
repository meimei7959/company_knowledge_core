---
type: AgentRunner
title: Meimei Mac Local Dev RT
description: External Agent Ring runner registration.
timestamp: "2026-06-21T09:37:12Z"
runnerId: runner.meimei-mac-local-dev-rt
machineId: runner.meimei-mac-local-dev-rt
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.development
agentIds:
  - agent.company.development
capabilities:
  - agent_worker
  - api
  - cross_platform
  - database
  - desktop
  - development
  - implementation
  - integration
  - migration
  - requirement_traceability
  - scheduler
  - scheduler_design
  - technical_solution
  - workbench
  - workflow_engineering
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
  - {"taskId":"kt-ai-native-os-gap-tech-feishu-api-postgres-live","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-gap-tech-feishu-api-postgres-live.md","event":"finished:submitted","at":"2026-06-21T12:30:00Z"}
  - {"taskId":"kt-ai-native-os-gap-tech-traceability-promotion","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-gap-tech-traceability-promotion.md","event":"finished:done","at":"2026-06-21T12:30:11Z"}
  - {"taskId":"kt-ai-native-os-gap-tech-agent-ring-console-live-execution","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-gap-tech-agent-ring-console-live-execution.md","event":"finished:submitted","at":"2026-06-21T12:30:37Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-profile-skill-registry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-profile-skill-registry.md","event":"claimed","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-profile-skill-registry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-profile-skill-registry.md","event":"finished:submitted","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-local-router-session-registry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-local-router-session-registry.md","event":"claimed","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-local-router-session-registry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-local-router-session-registry.md","event":"finished:submitted","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-agent-runtime-orchestrator","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-agent-runtime-orchestrator.md","event":"claimed","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-agent-runtime-orchestrator","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-agent-runtime-orchestrator.md","event":"finished:submitted","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-worktree-console-harness","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-worktree-console-harness.md","event":"claimed","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-tech-worktree-console-harness","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-tech-worktree-console-harness.md","event":"finished:submitted","at":"2026-06-22T03:03:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-dev-implementation","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-dev-implementation.md","event":"claimed","at":"2026-06-22T03:20:25Z"}
  - {"taskId":"kt-ai-native-agent-v1-dev-implementation","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-dev-implementation.md","event":"finished:submitted","at":"2026-06-22T03:20:25Z"}
lastFailure: ""
manualHandoff: false
updatedAt: "2026-06-22T03:20:25Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
