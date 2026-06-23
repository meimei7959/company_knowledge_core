---
type: AgentRunner
title: Meimei Mac Local Codex
description: External Agent Ring runner registration.
timestamp: "2026-06-20T09:55:17Z"
runnerId: runner.meimei-mac-local-codex
ringVersion: local-codex-v1
hostType: local_mac
status: busy
mode: online
agents:
  - agent.company.development
  - agent.company.test
  - agent.company.project-manager
capabilities:
  - development
  - schema_migration
  - validation
  - task_result_writeback
availableProjects:
  - company-knowledge-core
repoAccess:
  - /Users/meimei/Documents/company_knowledge_core
dataScopes:
  - local_repo
load: 0.1
lastHeartbeatAt: "2026-06-21T07:21:33Z"
currentLeases:
  - {"taskId":"kt-ai-native-os-test-desktop-workbench-slice0","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-test-desktop-workbench-slice0.md","leaseOwner":"runner.meimei-mac-local-codex","leaseVersion":2,"leaseAttempt":1,"leaseExpiresAt":"2026-06-21T07:28:38Z","status":"processing"}
failedLeases: []
taskHistory:
  - {"taskId":"kt-ai-native-os-test-desktop-workbench-slice0","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-test-desktop-workbench-slice0.md","event":"claimed","at":"2026-06-21T07:18:38Z"}
  - {"taskId":"kt-ai-native-os-impl-desktop-workbench-slice0-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-workbench-slice0-retry.md","event":"claimed","at":"2026-06-21T07:21:34Z"}
  - {"taskId":"kt-ai-native-os-impl-governance-quality-ops-api-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-governance-quality-ops-api-retry.md","event":"claimed","at":"2026-06-21T07:21:34Z"}
  - {"taskId":"kt-ai-native-os-impl-requirement-prd-domain-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-requirement-prd-domain-retry.md","event":"claimed","at":"2026-06-21T07:21:34Z"}
  - {"taskId":"kt-ai-native-os-impl-scheduler-runner-result-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result-retry.md","event":"claimed","at":"2026-06-21T07:21:34Z"}
  - {"taskId":"kt-ai-native-os-repair-taskresult-metadata-migration","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration.md","event":"claimed","at":"2026-06-21T07:21:34Z"}
  - {"taskId":"kt-ai-native-os-impl-desktop-workbench-slice0-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-workbench-slice0-retry.md","event":"stale_repaired","at":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-impl-governance-quality-ops-api-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-governance-quality-ops-api-retry.md","event":"stale_repaired","at":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-impl-requirement-prd-domain-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-requirement-prd-domain-retry.md","event":"stale_repaired","at":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-impl-scheduler-runner-result-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result-retry.md","event":"stale_repaired","at":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-repair-taskresult-metadata-migration","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration.md","event":"stale_repaired","at":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-repair-taskresult-metadata-migration","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration.md","event":"claimed","at":"2026-06-21T08:01:03Z"}
  - {"taskId":"kt-ai-native-os-repair-taskresult-metadata-migration","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration.md","event":"finished:done","at":"2026-06-21T08:11:09Z"}
updatedAt: "2026-06-21T08:11:09Z"
staleLeases:
  - {"taskId":"kt-ai-native-os-impl-desktop-workbench-slice0-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-desktop-workbench-slice0-retry.md","previousRunnerId":"runner.meimei-mac-local-codex","status":"waiting_runner","reason":"lease_expired","priority":"critical","detectedAt":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-impl-governance-quality-ops-api-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-governance-quality-ops-api-retry.md","previousRunnerId":"runner.meimei-mac-local-codex","status":"waiting_runner","reason":"lease_expired","priority":"critical","detectedAt":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-impl-requirement-prd-domain-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-requirement-prd-domain-retry.md","previousRunnerId":"runner.meimei-mac-local-codex","status":"waiting_runner","reason":"lease_expired","priority":"critical","detectedAt":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-impl-scheduler-runner-result-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-impl-scheduler-runner-result-retry.md","previousRunnerId":"runner.meimei-mac-local-codex","status":"waiting_runner","reason":"lease_expired","priority":"critical","detectedAt":"2026-06-21T07:46:20Z"}
  - {"taskId":"kt-ai-native-os-repair-taskresult-metadata-migration","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-repair-taskresult-metadata-migration.md","previousRunnerId":"runner.meimei-mac-local-codex","status":"waiting_runner","reason":"lease_expired","priority":"critical","detectedAt":"2026-06-21T07:46:20Z"}
lastFailure: lease_expired
machineId: runner.meimei-mac-local-codex
owner: ""
agentIds:
  - agent.company.development
  - agent.company.test
  - agent.company.project-manager
tools: []
repositoryScopes:
  - /Users/meimei/Documents/company_knowledge_core
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
