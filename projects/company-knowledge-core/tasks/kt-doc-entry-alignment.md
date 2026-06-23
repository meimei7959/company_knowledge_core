---
type: ProjectTask
title: Documentation entry alignment
description: Align project entry documents so a new Agent or teammate can understand the current project quickly.
timestamp: "2026-06-19T00:00:00Z"
taskId: TASK-DOC-ENTRY-ALIGNMENT
taskType: project_initialization
projectId: company-knowledge-core
requester: meimei
assignee: agent.company-knowledge-core.knowledge-engineering
requiredCapabilities:
  - documentation
  - knowledge_sync
requiredAgents:
  - agent.company-knowledge-core.knowledge-engineering
preferredRunner:
  - runner.meimei-mac-codex
assignedRunner: []
executorAgent: []
leaseOwner: []
leaseExpiresAt: []
status: done
priority: high
dueAt: []
sourceMaterialRefs:
  - README.md
  - AGENTS.md
  - docs/protocols/agent-workbench-integration-brief.md
expectedOutput:
  - aligned README and AGENTS current phase
  - docs index links for strategy, architecture, protocols, scheduler, guides
  - project index points to active task list
resultRef: task-results/tr-task-doc-entry-alignment.md
notificationRefs: []
auditRefs: []
completedAt: "2026-06-18T16:09:57Z"
taskRuntime: {"runtimeVersion":"task-runtime.v1","version":"task-runtime.v1","taskType":"project_initialization","category":"project","stage":"","requiredCapabilities":["project_initialization","documentation","knowledge_sync"],"requiredTools":[],"sourceRefs":["README.md","AGENTS.md","docs/protocols/agent-workbench-integration-brief.md"],"repositoryRefs":[],"dataScopes":[],"qualityGate":"project_management","acceptancePath":"pm_review","reviewPath":"pm_review","riskLevel":"low","permissionPolicy":"runner_scope_required","closurePolicy":"task_result_with_evidence","approvalRelayRequired":false,"testEvidenceRequired":false,"knowledgeEvidenceRequired":false,"productEvidenceRequired":false,"manualHandoffAllowed":true,"requiresSourceMaterial":false,"requiresKnowledgeDraft":false,"requiresTests":false}
updatedAt: "2026-06-21T07:18:05Z"
---

## Request

Make the project readable from the top-level entry points.

## Definition of Done

- README states that this project is the central processor: scheduler plus knowledge engineering.
- AGENTS instructions match current phase and do not describe the project as only a knowledge repository.
- `docs/architecture/index.md`, `docs/protocols/index.md`, and `docs/scheduler/index.md` expose the important docs.
- `projects/company-knowledge-core/index.md` links project, tasks, agents, tools, decisions, lessons, and launch/current-plan docs.
- No entry point tells Agent Workbench developers that the workbench product scope is limited to task pulling.

## Test Plan

- Search docs for outdated wording such as "only knowledge base" or "Agent Workbench only connector".
- Check all relative links in changed markdown files.
- Run validation if frontmatter or project objects change.

## Self-Verification Checklist

- [x] README current phase aligned.
- [x] AGENTS current phase aligned.
- [x] Docs indexes aligned.
- [x] Project index aligned.
- [x] Link check performed.
