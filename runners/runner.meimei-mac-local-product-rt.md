---
type: AgentRunner
title: Meimei Mac Local Product RT
description: External Agent Ring runner registration.
timestamp: "2026-06-21T09:37:12Z"
runnerId: runner.meimei-mac-local-product-rt
machineId: runner.meimei-mac-local-product-rt
owner: ""
ringVersion: local-codex-v1
hostType: local_mac
status: online
mode: online
agents:
  - agent.company.product-manager
agentIds:
  - agent.company.product-manager
capabilities:
  - acceptance_criteria_definition
  - product_acceptance
  - product_management
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
lastHeartbeatAt: "2026-06-22T04:37:02Z"
currentLeases: []
staleLeases: []
failedLeases:
  - {"taskId":"kt-ai-native-agent-v1-product-requirement-structure","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","status":"waiting_runner","reason":"context-builder-docx-binary-source-fixed","at":"2026-06-22T02:59:49Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md","status":"waiting_runner","reason":"upgrade-product-final-acceptance-result-contract","at":"2026-06-22T03:29:28Z"}
taskHistory:
  - {"taskId":"kt-ai-native-os-gap-product-acceptance-criteria","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-os-gap-product-acceptance-criteria.md","event":"finished:done","at":"2026-06-21T12:56:35Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-requirement-structure","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","event":"claimed","at":"2026-06-22T02:56:40Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-requirement-structure","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","event":"retry_requested","status":"waiting_runner","reason":"context-builder-docx-binary-source-fixed","at":"2026-06-22T02:59:49Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-requirement-structure","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","event":"claimed","at":"2026-06-22T02:59:56Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-requirement-structure","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-requirement-structure.md","event":"finished:submitted","at":"2026-06-22T02:59:56Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-review-technical-solutions","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-review-technical-solutions.md","event":"claimed","at":"2026-06-22T03:02:04Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-review-technical-solutions","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-review-technical-solutions.md","event":"finished:submitted","at":"2026-06-22T03:02:04Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-scope-review","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md","event":"claimed","at":"2026-06-22T03:02:40Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-scope-review","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-scope-review.md","event":"finished:submitted","at":"2026-06-22T03:02:40Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-review-technical-solutions-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-review-technical-solutions-retry.md","event":"claimed","at":"2026-06-22T03:04:40Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-review-technical-solutions-retry","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-review-technical-solutions-retry.md","event":"finished:submitted","at":"2026-06-22T03:04:40Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md","event":"claimed","at":"2026-06-22T03:24:01Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md","event":"finished:submitted","at":"2026-06-22T03:24:01Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md","event":"retry_requested","status":"waiting_runner","reason":"upgrade-product-final-acceptance-result-contract","at":"2026-06-22T03:29:28Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md","event":"claimed","at":"2026-06-22T03:29:38Z"}
  - {"taskId":"kt-ai-native-agent-v1-product-final-acceptance","taskRef":"projects/company-knowledge-core/tasks/kt-ai-native-agent-v1-product-final-acceptance.md","event":"finished:submitted","at":"2026-06-22T03:29:38Z"}
lastFailure: upgrade-product-final-acceptance-result-contract
manualHandoff: false
updatedAt: "2026-06-22T03:29:38Z"
---

## Purpose

This runner represents one distributed computer connected through Agent Ring.

## Health Checks

- Agent Ring must report heartbeat before claiming tasks.
- Runner-side tools, models, repositories, and data access remain local to that computer.
- Central processor stores capabilities and audit metadata, not local secrets.

## Notes

Agent Ring owns local execution. This record is the central processor view used for scheduling.
